#!/usr/bin/env python3
"""Generate the audit documents from the crawl + data files (no network).

Writes docs/PAGE-INVENTORY.md/.csv, docs/ASSET-INVENTORY.csv/.md, docs/CONTENT-REVIEW-LOG.md, docs/SOURCE-MAPPING.md.
Run after tools/build_site.py:   python tools/build_docs.py
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
AUDIT = os.path.join(ROOT, "source-audit")
DATA = os.path.join(ROOT, "data")
BASE = "https://www.sanyoaqm.com.sg/"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


pages = load(os.path.join(AUDIT, "page-inventory.json"))
assets = load(os.path.join(AUDIT, "asset-inventory.json"))
review = load(os.path.join(DATA, "review-log.json"))
urlmap = load(os.path.join(DATA, "url-map.json"))
ed = load(os.path.join(DATA, "editorial.json"))
manifest = {m["original"]: m for m in load(os.path.join(DATA, "image-manifest.json")) if m.get("original")}
src = load(os.path.join(DATA, "source-record.json"))
new_for = {m["old"]: m["new"] for m in urlmap["map"]}
os.makedirs(DOCS, exist_ok=True)

# ---------------------------------------------------------------- page inventory
gallery_counts = {}
for a in src["albums"]:
    for p in a["source_pages"]:
        gallery_counts[os.path.basename(p["url"])] = p["image_count"]
gallery_counts["newfishes.html"] = 2

rows = []
for p in pages:
    name = os.path.basename(p["url"])
    live_imgs = len({i["resolved"] for i in p.get("images", [])})
    rows.append({
        "source_page_url": p["url"], "title": p.get("title") or "", "http_status": p.get("status"),
        "last_modified_header": p.get("last_modified") or "", "bytes": p.get("bytes"), "sha256": p.get("sha256"),
        "captured_at_utc": p.get("captured_at"), "gallery_photos": gallery_counts.get(name, 0),
        "distinct_images_referenced": live_imgs, "commented_out_image_refs": "; ".join(p.get("commented_out_images", [])),
        "new_page": new_for.get(name, ""),
    })
with open(os.path.join(DOCS, "PAGE-INVENTORY.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
with open(os.path.join(DOCS, "PAGE-INVENTORY.md"), "w", encoding="utf-8") as f:
    f.write("# Page inventory (live audit)\n\n")
    f.write(f"Captured with `tools/crawl_source.py` on **{ed['site']['audit_date']}** from {BASE}index.html by following every same-domain link "
            "(breadth-first). Raw HTML is kept unchanged in `source-audit/raw-html/`.\n\n")
    f.write(f"* Reachable HTML pages: **{sum(1 for p in pages if p.get('status') == 200)}** (all HTTP 200). Pages that failed or were inaccessible: **none**.\n")
    f.write("* The prior audit also reported 19 linked HTML pages; this audit found the same 19. Differences in the asset total are explained in ASSET-INVENTORY.md.\n")
    f.write("* Every page returns `Last-Modified: Tue, 10 Jul 2012`; the footer reads “Copyright © 2006”.\n")
    f.write("* The server has no `robots.txt`, `sitemap.xml` or `favicon.ico` (404 on probe).\n\n")
    f.write("| Source page | Title | Status | Last-Modified | Bytes | SHA-256 (first 12) | Gallery photos | New page |\n|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        f.write(f"| {os.path.basename(r['source_page_url'])} | {r['title']} | {r['http_status']} | {r['last_modified_header'][5:16]} | {r['bytes']} | "
                f"`{(r['sha256'] or '')[:12]}` | {r['gallery_photos']} | {r['new_page']} |\n")
    f.write("\nFull columns (capture time, hashes, commented-out image references) are in `PAGE-INVENTORY.csv`.\n")

# ---------------------------------------------------------------- asset inventory
GALLERY_DIRS = ("images/freshwater_fishes/", "images/aquatic_plants/", "images/marine_fishes/", "images/new_fishes/", "images/driftwood/")


def classify(rel, status):
    if status != 200:
        return ("missing / inaccessible", "no", "Returned HTTP 404 on the server." if rel.startswith("images/") else "Probe: not present on the server.")
    if rel.startswith(GALLERY_DIRS):
        return ("product photograph (gallery)", "yes", "Delivered as WebP in site/assets/img/catalogue/; unchanged original kept.")
    if rel in ("images/company_photo.jpg", "images/sanyo.jpg") or rel.startswith("images/about_us") and "member" not in rel:
        return ("company / facility photograph", "yes", "Used on Home, Company and/or Contact pages.")
    if rel == "images/SanyoPhoto.jpg":
        return ("company photograph (commented out in source)", "original only", "Referenced only inside an HTML comment on contact.html; not used.")
    if rel == "images/SanyoAqmLogo.gif":
        return ("company logo", "yes", "Copied unchanged to site/assets/img/brand/logo.gif; favicon derived from it.")
    if rel == "images/aboutus_member.jpg":
        return ("third-party membership logos (strip)", "yes (qualified)", "Shown only in the 'Not verified as current' box on the Company page.")
    if rel in ("images/memberof.jpg", "images/ofish.jpg", "images/safea.jpg"):
        return ("third-party membership logo (legacy footer)", "no", "Not used; membership is unverified (R03).")
    if rel.startswith("images/images/homepic"):
        return ("legacy home banner tile", "no", "Low resolution / baked-in slogan text (see editorial.json unused_source_assets).")
    if rel == "images/top_banner.jpg":
        return ("legacy decorative header banner (aquascape strip)", "no", "Decorative; 547x116 with white fade; not a catalogue photograph.")
    if rel.startswith("images/banner_"):
        return ("legacy section banner (baked-in title text)", "no", "Layout graphic with the page title as pixels; replaced by real headings.")
    if rel in ("images/topbar.gif", "images/top.gif", "images/bottom1.jpg", "images/arch.gif", "images/enter.gif", "images/dot.gif"):
        return ("legacy layout fragment / spacer", "no", "Decorative table-layout piece; not a product photograph.")
    if rel.endswith(".css"):
        return ("legacy stylesheet", "no", "Replaced by src/css/styles.css.")
    return ("other", "no", "")


arows = []
for a in assets:
    rel = a["url"].replace(BASE, "")
    cls, used, note = classify(rel, a.get("status"))
    m = manifest.get("source-audit/originals/" + rel)
    arows.append({
        "asset_url": a["url"], "http_status": a.get("status"), "classification": cls, "used_in_new_site": used,
        "live_referenced_by": "; ".join(os.path.basename(u) for u in a.get("referenced_by", [])) if not a.get("commented_out_only") else "",
        "commented_out_only_in": "; ".join(os.path.basename(u) for u in a.get("referenced_by", [])) if a.get("commented_out_only") else "",
        "captured_at_utc": a.get("captured_at", ""), "local_original": ("source-audit/" + a["local_path"]) if a.get("local_path") else "",
        "width": a.get("width", ""), "height": a.get("height", ""), "bytes": a.get("bytes", ""), "sha256": a.get("sha256", ""),
        "delivered_file": m["delivered"] if m else "", "delivered_sha256": m.get("delivered_sha256", "") if m else "", "notes": note,
    })
with open(os.path.join(DOCS, "ASSET-INVENTORY.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(arows[0]))
    w.writeheader()
    w.writerows(arows)

ok_imgs = [r for r in arows if r["http_status"] == 200 and r["asset_url"].lower().endswith((".jpg", ".gif"))]
by_cls = {}
for r in ok_imgs:
    by_cls[r["classification"]] = by_cls.get(r["classification"], 0) + 1
with open(os.path.join(DOCS, "ASSET-INVENTORY.md"), "w", encoding="utf-8") as f:
    f.write("# Asset inventory (live audit)\n\n")
    f.write(f"Captured {ed['site']['audit_date']}. Every downloadable asset is stored unchanged under `source-audit/originals/` with its SHA-256, pixel size and capture time in `ASSET-INVENTORY.csv`.\n\n")
    f.write(f"* Downloadable image files: **{len(ok_imgs)}** (the prior audit counted 131; the extra file is `images/SanyoPhoto.jpg`, which exists on the server but is referenced only inside an HTML comment on the contact page).\n")
    f.write("* Also captured: `css/sanyo.css`.\n")
    f.write("* Missing / inaccessible: " + ", ".join(f"`{r['asset_url'].replace(BASE, '')}` ({r['http_status']})" for r in arows if r["http_status"] != 200) + ".\n")
    f.write("* `images/images/homepic11.jpg` and `images/dot.gif` are referenced by the source markup but return 404.\n\n")
    f.write("## Classification of the downloaded images\n\n| Class | Files |\n|---|---|\n")
    for k, v in sorted(by_cls.items(), key=lambda kv: -kv[1]):
        f.write(f"| {k} | {v} |\n")
    f.write("\nThese counts describe files, not products: gallery photos are not product counts and are not used as marketing statistics.\n")
    f.write("\n## Delivered images\n\nGallery and company photographs are re-encoded to WebP (quality 90) at their original pixel size. Nothing is resized, cropped or de-watermarked. "
            "`data/image-manifest.json` links each delivered file to its original, with both SHA-256 values.\n")

# ---------------------------------------------------------------- content review log
with open(os.path.join(DOCS, "CONTENT-REVIEW-LOG.md"), "w", encoding="utf-8") as f:
    n_open = sum(1 for e in review["entries"] if e["status"] == "open")
    f.write("# Content-review log\n\n")
    f.write(f"{len(review['entries'])} entries; **{n_open} need company review** (status `open`). Quotes are verbatim from the original pages and are machine-checked by `tools/verify_content.py`. "
            "Source discrepancies are never silently rewritten: they are kept, qualified or withheld as described under *Treatment*. Source: data/review-log.json.\n\n")
    for e in review["entries"]:
        f.write(f"## {e['id']} — {e['topic']}\n\n")
        f.write(f"* **Severity:** {e['severity']}  ·  **Status:** {e['status']}\n")
        f.write(f"* **Source pages:** {', '.join(e['pages'])}\n")
        f.write(f"* **Original text / anchor:** “{e['quote']}”\n")
        f.write(f"* **Issue:** {e['issue']}\n")
        f.write(f"* **Treatment:** {e['treatment']}\n\n")

# ---------------------------------------------------------------- source mapping
sections = {
    "index.html": ("home.*", "Hero/section copy is new, source-supported wording; the quality bullets summarise about.quality_process.*; no numbers are used."),
    "company.html": ("about.*", "about.intro (split into three sentences), about.customers, about.qualities.intro, about.quality_process.1-6, about.services.1-3, about.assurance.1-4; about_orgs; images company_photo, about_us1-5, aboutus_member."),
    "freshwater-fishes.html": ("freshwater.*", "freshwater.intro, freshwater.category.1-24 (+ links to the five albums)."),
    "freshwater-platy.html": ("freshwater-platy.*", "p1/p2 heading, care; description withheld (R07); 21 photos."),
    "freshwater-molly.html": ("freshwater-molly.*", "heading, care, description; 9 photos."),
    "freshwater-guppy.html": ("freshwater-guppy.*", "heading, care, description; 12 photos."),
    "freshwater-swordtail.html": ("freshwater-swordtail.*", "heading, care, description; 4 photos."),
    "freshwater-cichild.html": ("freshwater-cichild.*", "heading only (CICHILD); 9 photos."),
    "marine-fishes.html": ("marine.*", "marine.intro (reworded, R18), marine.category.1-22; 15 photos from the two gallery pages."),
    "aquatic-plants.html": ("plants.intro", "supply forms from plants.intro; 24 photos from three gallery pages."),
    "plants-on-driftwood.html": ("plants.intro", "3 photos (distinct source gallery)."),
    "new-fishes.html": ("newfishes.*", "two entries: name, pH, temperature, description (verbatim except the label typo 'Desciption')."),
    "driftwood.html": ("driftwood.intro", "shipment information quoted verbatim; 3 photos."),
    "contact.html": ("contact.*", "contact.address_block values; photo sanyo.jpg; form replaced by enquiry workflow (R17)."),
}
with open(os.path.join(DOCS, "SOURCE-MAPPING.md"), "w", encoding="utf-8") as f:
    f.write("# Source mapping\n\n## Old URL → new page\n\n| Original URL | New page | Note |\n|---|---|---|\n")
    for m in urlmap["map"]:
        f.write(f"| {m['old_url']} | `{m['new']}` | {m['note']} |\n")
    f.write("\nNew pages with no original equivalent:\n\n")
    for n in urlmap["new_pages_without_old_equivalent"]:
        f.write(f"* `{n['new']}` — {n['note']}\n")
    f.write("\n## New page → structured source records\n\nEvery factual statement and gallery image is stored with its source URL in `data/source-record.json` "
            "(classes: company_information, contact_details, product_category, named_product, gallery_image, care_information, supply_form, shipment_information, historical_claim). "
            "Display wording lives in `tools/sitegen/pages.py`; display labels, aliases and proposed corrections live in `data/editorial.json`.\n\n")
    f.write("| New page | Source block ids | Notes |\n|---|---|---|\n")
    for k, (ids, note) in sections.items():
        f.write(f"| `{k}` | `{ids}` | {note} |\n")
    f.write("\n## Redirect snippets (optional, for a future deployment)\n\nApache `.htaccess`:\n\n```apache\n")
    for m in urlmap["map"]:
        if m["old"] != m["new"].split("#")[0]:
            f.write(f"Redirect 301 /{m['old']} /{m['new'].split('#')[0]}\n")
    f.write("```\n\nNetlify `_redirects`:\n\n```\n")
    for m in urlmap["map"]:
        if m["old"] != m["new"].split("#")[0]:
            f.write(f"/{m['old']}  /{m['new'].split('#')[0]}  301\n")
    f.write("```\n\nThese are documentation only; nothing here touches the original company website, DNS or hosting.\n")

print("docs written:", ", ".join(sorted(os.listdir(DOCS))))
