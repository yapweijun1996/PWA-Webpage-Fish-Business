#!/usr/bin/env python3
"""Compare the built site against the audited source record (content fidelity gate).

Run after tools/build_site.py:   python tools/verify_content.py
Exit code 0 = all checks passed, 1 = at least one failed. Writes docs/qa/content-fidelity.json.
"""
import glob
import hashlib
import json
import os
import re
import sys

from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
AUDIT = os.path.join(ROOT, "source-audit")
DATA = os.path.join(ROOT, "data")

results = []


def check(name, ok, detail=""):
    results.append({"check": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def squash(s):
    """Whitespace-free form: link boundaries add or remove spaces in extracted text, but words must still match exactly."""
    return re.sub(r"\s+", "", s.replace("\xa0", " "))


def raw_text(name):
    raw = open(os.path.join(AUDIT, "raw-html", name), "rb").read().decode("cp1252")
    return norm(BeautifulSoup(raw, "lxml").get_text(" ")), raw


def site_html(name):
    return open(os.path.join(SITE, name), encoding="utf-8").read()


def site_text(name):
    return norm(BeautifulSoup(site_html(name), "lxml").get_text(" "))


src = json.load(open(os.path.join(DATA, "source-record.json"), encoding="utf-8"))
ed = json.load(open(os.path.join(DATA, "editorial.json"), encoding="utf-8"))
review = json.load(open(os.path.join(DATA, "review-log.json"), encoding="utf-8"))
pages_inv = {p["url"]: p for p in json.load(open(os.path.join(AUDIT, "page-inventory.json"), encoding="utf-8"))}
assets_inv = {a["url"]: a for a in json.load(open(os.path.join(AUDIT, "asset-inventory.json"), encoding="utf-8"))}
cat_js = open(os.path.join(SITE, "assets", "js", "catalogue-data.js"), encoding="utf-8").read()
SANYO = json.loads(cat_js[cat_js.index("window.SANYO = ") + len("window.SANYO = "):].rstrip().rstrip(";"))

all_raw = {os.path.basename(f): raw_text(os.path.basename(f)) for f in glob.glob(os.path.join(AUDIT, "raw-html", "*.html"))}

# 1. every extracted source block is verbatim in its raw page ------------------------------------------------
bad = []
for b in src["blocks"]:
    page = os.path.basename(b["source_page"])
    text, raw = all_raw[page]
    needle = norm(b["text"])
    if b["class"] == "gallery_image":
        if b["text"] not in raw:
            bad.append(b["id"])
    elif b["id"] == "contact.address_block":
        if not all(squash(x) in squash(text) for x in b["text"].split(" | ") if x not in ("Email:",)):
            bad.append(b["id"])
    elif b["id"].startswith("home.meta"):
        if b["text"] not in raw:
            bad.append(b["id"])
    elif squash(needle) not in squash(text):
        bad.append(b["id"])
check("source blocks are verbatim in the raw pages", not bad, f"{len(bad)} not found: {bad[:5]}")

# 2. review-log quotes exist in the source ---------------------------------------------------------------
bad = []
for e in review["entries"]:
    if e.get("quote_in"):
        continue  # anchor lives in an image (e.g. watermark), not in HTML text
    q = squash(e["quote"])
    pages = [p for p in e["pages"] if p.endswith(".html")] or list(all_raw)
    found = any(q in squash(all_raw[p][0]) or e["quote"] in all_raw[p][1] for p in pages if p in all_raw)
    if not found:
        bad.append(e["id"])
check("review-log quotes are verbatim in the cited source pages", not bad, str(bad))

# 3. contact details -------------------------------------------------------------------------------------
c = src["contact"]
contact_html = site_text("contact.html")
footer_ok = all(c["tel"] in site_text(p) and c["emails"][0] in site_text(p) for p in ("index.html", "company.html", "catalogue.html"))
exp = ["3 Chencharu Link", "Singapore 768144", "+65 6481 3111", "+65 6481 6333", "+65 6481 6688", "sales@sanyoaqm.com.sg", "info@sanyoaqm.com.sg"]
check("contact page shows every published contact value", all(x in contact_html for x in exp), str([x for x in exp if x not in contact_html]))
check("contact values match source record", (c["name"], c["address_lines"], c["tel"], c["fax"], c["emails"]) ==
      ("SANYO AQUARIUM (PTE) LTD", ["3 Chencharu Link", "Singapore 768144"], "+65 6481 3111", ["+65 6481 6333", "+65 6481 6688"],
       ["sales@sanyoaqm.com.sg", "info@sanyoaqm.com.sg"]))
check("footer repeats tel/email on every page", footer_ok)
ch = site_html("contact.html")
check("tel: and mailto: links are correct", 'href="tel:+6564813111"' in ch and 'href="mailto:sales@sanyoaqm.com.sg"' in ch and 'href="mailto:info@sanyoaqm.com.sg"' in ch)

# 4. catalogue coverage & image association ----------------------------------------------------------------
src_imgs = {im["src"]: (a["id"], im["source_page"]) for a in src["albums"] for im in a["items"]}
for e in src["new_fishes"]:
    src_imgs[e["image"]["src"]] = ("new-fishes", "https://www.sanyoaqm.com.sg/newfishes.html")
check("gallery photo count in source record", len(src_imgs) == 102, str(len(src_imgs)))
check("catalogue data has every source photo once", len(SANYO["items"]) == 102 and len({i["id"] for i in SANYO["items"]}) == 102)
# original files on disk + checksum match inventory
missing, badsum = [], []
for rel in src_imgs:
    url = "https://www.sanyoaqm.com.sg/" + rel
    a = assets_inv.get(url)
    p = os.path.join(AUDIT, "originals", rel.replace("/", os.sep))
    if not a or a.get("status") != 200 or not os.path.exists(p):
        missing.append(rel)
        continue
    if hashlib.sha256(open(p, "rb").read()).hexdigest() != a["sha256"]:
        badsum.append(rel)
check("all 102 original gallery files exist and match recorded SHA-256", not missing and not badsum, f"{missing[:3]} {badsum[:3]}")
# delivered webp exists for each item and has same dimensions
from PIL import Image  # noqa: E402
dim_bad = []
for it in SANYO["items"]:
    p = os.path.join(SITE, it["img"].replace("/", os.sep))
    if not os.path.exists(p):
        dim_bad.append(it["id"])
        continue
    with Image.open(p) as im:
        if im.size != (it["w"], it["h"]):
            dim_bad.append(it["id"])
check("delivered WebP for every photo exists with unchanged pixel dimensions", not dim_bad, str(dim_bad[:3]))
# association: the item's source page really contains that image
assoc_bad = []
manifest = json.load(open(os.path.join(DATA, "image-manifest.json"), encoding="utf-8"))
for a in src["albums"]:
    for im in a["items"]:
        page = os.path.basename(im["source_page"])
        if im["src"] not in all_raw[page][1]:
            assoc_bad.append((a["id"], im["src"]))
check("every photo's album/page association appears in its source page markup", not assoc_bad, str(assoc_bad[:3]))
# each site album page contains exactly the album's items
per_album_bad = []
for aid, album in SANYO["albums"].items():
    page = site_html(album["page"])
    ids = re.findall(r'data-item="([^"]+)"', page)
    exp_ids = [i["id"] for i in SANYO["items"] if i["album"] == aid]
    if ids != exp_ids:
        per_album_bad.append((aid, len(ids), len(exp_ids)))
check("each gallery page lists exactly its album's photos in source order", not per_album_bad, str(per_album_bad))
# all site webp are referenced
used = {i["img"] for i in SANYO["items"]}
on_disk = {os.path.relpath(p, SITE).replace(os.sep, "/") for p in glob.glob(os.path.join(SITE, "assets", "img", "catalogue", "**", "*.webp"), recursive=True)}
check("no orphan or missing catalogue images in site/", used == on_disk, f"orphans={sorted(on_disk - used)[:3]} missing={sorted(used - on_disk)[:3]}")

# AI illustrations remain separate from originals and carry concise disclosure.
AI_LABEL = "AI illustration"
AI_ALT_PREFIX = "AI-generated illustration"
configured_mode = ed.get("site", {}).get("image_mode", "ai-illustration")
check("image_mode is configured and built as ai-illustration", configured_mode == "ai-illustration" and SANYO.get("site", {}).get("imageMode") == "ai-illustration",
      f"editorial={configured_mode}, built={SANYO.get('site', {}).get('imageMode')}")
ai_manifest = json.load(open(os.path.join(ROOT, "tools", "ai_images", "manifest.json"), encoding="utf-8"))
ai_records = {entry["id"]: entry for entry in ai_manifest["images"]}
check("AI image manifest covers the 102 catalogue photos exactly once", set(ai_records) == {item["id"] for item in SANYO["items"]} and len(ai_records) == 102)
ai_bad, ai_file_bad, card_bad = [], [], []
for it in SANYO["items"]:
    entry = ai_records.get(it["id"], {})
    if entry.get("status") != "done":
        if it.get("ai"):
            ai_bad.append((it["id"], "unaccepted variant exposed"))
        continue
    if not it.get("ai") or not it.get("aiAlt", "").startswith(AI_ALT_PREFIX):
        ai_bad.append(it["id"])
    ai_path = os.path.join(SITE, (it.get("ai") or "").replace("/", os.sep))
    if not os.path.isfile(ai_path) or hashlib.sha256(open(ai_path, "rb").read()).hexdigest() != entry.get("output_sha256"):
        ai_file_bad.append(it["id"])
    page = SANYO["albums"][it["album"]]["page"]
    page_soup = BeautifulSoup(site_html(page), "html.parser")
    card = page_soup.find(attrs={"data-item": it["id"]})
    badge = card.select_one("[data-ai-label]") if card else None
    image = card.select_one("img[data-ai-src]") if card else None
    toggle = card.select_one("[data-card-variant]") if card else None
    variant_is_labelled = bool(
        badge and AI_LABEL in badge.get_text(" ", strip=True)
        and image and image.get("data-ai-src") == it.get("ai")
        and image.get("data-ai-alt", "").startswith(AI_ALT_PREFIX)
    )
    active_ai_is_labelled = bool(
        image and image.get("src") == it.get("ai")
        and image.get("alt", "").startswith(AI_ALT_PREFIX)
        and badge and not badge.has_attr("hidden")
    )
    if (not card or not variant_is_labelled
            or (configured_mode == "both" and not toggle)
            or (configured_mode == "ai-illustration" and not active_ai_is_labelled)):
        card_bad.append(it["id"])
check("accepted AI images include the required alt label and separate generated file", not ai_bad and not ai_file_bad,
      f"label/data={ai_bad[:3]}, files={ai_file_bad[:3]}")
check("each accepted AI image has a labelled card variant and the both-mode toggle", not card_bad, str(card_bad[:3]))
expected_company = {os.path.splitext(f["file"])[0] for f in ed["company_images"]["facility"]}
expected_company.update(os.path.splitext(ed["company_images"][key]["file"])[0] for key in ("exterior", "exterior_contact"))
company_original_paths = {f'assets/img/company/{stem}.webp' for stem in expected_company}
rendered_ai_bad, default_originals = [], []
for html_path in glob.glob(os.path.join(SITE, "*.html")):
    soup = BeautifulSoup(open(html_path, encoding="utf-8").read(), "html.parser")
    page_name = os.path.basename(html_path)
    for image in soup.find_all("img"):
        image_src = image.get("src", "")
        if image_src.startswith("assets/img/generated/"):
            container = image.find_parent(attrs={"data-company-image": True}) if "/company/" in image_src else image.find_parent(attrs={"data-item": True})
            badge = container.select_one("[data-ai-label]") if container else None
            if (not image.get("alt", "").startswith(AI_ALT_PREFIX) or not badge
                    or (not badge.has_attr("hidden") and AI_LABEL not in badge.get_text(" ", strip=True))
                    or (image_src in [x.get("ai") for x in SANYO["items"]] and badge.has_attr("hidden"))):
                rendered_ai_bad.append((page_name, image_src))
        elif configured_mode == "ai-illustration" and (image_src.startswith("assets/img/catalogue/") or image_src in company_original_paths):
            default_originals.append((page_name, image_src))
check("every rendered AI image has a concise visible badge and AI alt text", not rendered_ai_bad, str(rendered_ai_bad[:3]))
check("AI image mode uses generated images in catalogue and company photo slots", not default_originals,
      str(default_originals[:3]))
thumbnail_toggle_bad = []
if configured_mode == "both":
    for page_name in ("index.html", "freshwater-fishes.html"):
        soup = BeautifulSoup(site_html(page_name), "html.parser")
        for thumbnail in soup.select("[data-thumbnail]"):
            image = thumbnail.select_one("img[data-ai-src]")
            owner = thumbnail.find_parent("li") or thumbnail.find_parent("figure")
            toggle = owner.select_one("[data-thumb-variant]") if owner else None
            if not image or not image.get("data-ai-src") or not toggle:
                thumbnail_toggle_bad.append((page_name, thumbnail.get("data-item", "unknown")))
check("both image mode exposes variant toggles on homepage and category thumbnails",
      configured_mode != "both" or not thumbnail_toggle_bad, str(thumbnail_toggle_bad[:3]))
company_toggle_bad = []
if configured_mode == "both":
    for page_name in ("index.html", "company.html", "contact.html"):
        soup = BeautifulSoup(site_html(page_name), "html.parser")
        for figure in soup.select("[data-company-image]"):
            image = figure.select_one("img[data-ai-src]")
            toggle = figure.select_one("[data-company-variant]")
            if not image or not image.get("data-ai-src") or not toggle:
                company_toggle_bad.append((page_name, figure.get("data-variant", "unknown")))
check("both image mode exposes toggles on building and facility illustrations",
      configured_mode != "both" or not company_toggle_bad, str(company_toggle_bad[:3]))
all_site_js = "\n".join(open(p, encoding="utf-8").read() for p in glob.glob(os.path.join(SITE, "assets", "js", "*.js")))
lb_pages = [p for p in glob.glob(os.path.join(SITE, "*.html")) if 'id="lightbox"' in open(p, encoding="utf-8").read()]
lb_label_ok = bool(lb_pages) and all(
    (lambda node: node is not None and node.get_text(" ", strip=True) == AI_LABEL)(
        BeautifulSoup(open(p, encoding="utf-8").read(), "html.parser").find(id="lb-ai-label")
    )
    for p in lb_pages
)
check("lightbox includes the concise AI label and both-mode toggle", lb_label_ok and AI_LABEL in all_site_js and "data-lb-variant" in all_site_js)
check("enquiry lines and exported item text identify AI illustrations", AI_LABEL in all_site_js and "not evidence of stock" in all_site_js and "photoVariant" in all_site_js)
company_records = [entry for entry in manifest if entry.get("kind") == "company-photo"]
all_company_stems = set(expected_company)
all_company_stems.add(os.path.splitext(ed["company_images"]["member_strip"]["file"])[0])
company_stems = {os.path.splitext(os.path.basename(entry["original"]))[0] for entry in company_records}
company_bad = []
for entry in company_records:
    delivered = os.path.join(SITE, entry["delivered"].replace("/", os.sep))
    original = os.path.join(ROOT, entry["original"].replace("/", os.sep))
    if (not os.path.isfile(delivered) or hashlib.sha256(open(delivered, "rb").read()).hexdigest() != entry.get("delivered_sha256")
            or not os.path.isfile(original) or hashlib.sha256(open(original, "rb").read()).hexdigest() != entry.get("original_sha256")):
        company_bad.append(entry.get("id"))
check("all original company photographs and adjacent logos remain on original delivery paths with source hashes intact", company_stems >= all_company_stems and not company_bad and all(entry.get("kind") != "company-photo" or entry.get("delivered", "").startswith("assets/img/company/") for entry in manifest),
      f"missing={sorted(all_company_stems - company_stems)}, bad={company_bad[:3]}")
check("company/facility originals stay out of the 102-image catalogue manifest", all(not any(stem in entry["id"] for entry in ai_manifest["images"]) for stem in all_company_stems))
company_ai_manifest = json.load(open(os.path.join(ROOT, "tools", "ai_images", "company-manifest.json"), encoding="utf-8"))
company_ai_records = {entry["id"]: entry for entry in company_ai_manifest["images"]}
expected_company_ai = {"company-" + stem for stem in expected_company}
company_ai_file_bad = []
for entry in company_ai_records.values():
    source = os.path.join(ROOT, entry["original_path"].replace("/", os.sep))
    output = os.path.join(ROOT, entry["output_path"].replace("/", os.sep))
    delivered = os.path.join(SITE, "assets", "img", "generated", "company", os.path.basename(entry["output_path"]))
    if (entry.get("status") != "done" or not os.path.isfile(source) or not os.path.isfile(output) or not os.path.isfile(delivered)
            or hashlib.sha256(open(source, "rb").read()).hexdigest() != entry.get("original_sha256")
            or hashlib.sha256(open(output, "rb").read()).hexdigest() != entry.get("output_sha256")
            or hashlib.sha256(open(delivered, "rb").read()).hexdigest() != entry.get("output_sha256")):
        company_ai_file_bad.append(entry.get("id"))
check("company AI manifest covers seven separate, hashed building/facility variants", set(company_ai_records) == expected_company_ai and not company_ai_file_bad,
      f"missing={sorted(expected_company_ai - set(company_ai_records))}, bad={company_ai_file_bad[:3]}")
company_page_bad = []
for html_path in glob.glob(os.path.join(SITE, "*.html")):
    page_name = os.path.basename(html_path)
    soup = BeautifulSoup(open(html_path, encoding="utf-8").read(), "html.parser")
    for figure in soup.select("[data-company-image]"):
        image = figure.select_one("img[data-ai-src]")
        badge = figure.select_one("[data-ai-label]")
        if (not image or not image.get("data-ai-src", "").startswith("assets/img/generated/company/")
                or not image.get("data-ai-alt", "").startswith(AI_ALT_PREFIX) or not badge
                or (configured_mode == "ai-illustration" and (image.get("src") != image.get("data-ai-src") or badge.has_attr("hidden")))
                or (configured_mode == "both" and not figure.select_one("[data-company-variant]"))):
            company_page_bad.append((page_name, image.get("src", "") if image else "missing"))
check("every displayed company illustration has a visible label, AI alt text and an original-image reference", not company_page_bad,
      str(company_page_bad[:3]))

# 5. categories ------------------------------------------------------------------------------------------
fw_src = [x["text"] for x in src["freshwater_categories"]]
mr_src = [x["text"] for x in src["marine_categories"]]
fw_site = [x["label"] for x in SANYO["categories"] if x["sec"] == "freshwater" and x["id"] not in ("cat-marine-any",) and x["id"].startswith("cat-freshwater-")]
mr_site = [x["label"] for x in SANYO["categories"] if x["sec"] == "marine" and x["id"].startswith("cat-marine-") and x["id"] != "cat-marine-any"]
check("freshwater category list (24) identical to source order/spelling", fw_site == fw_src, f"{fw_site} vs {fw_src}")
check("marine category list (22) identical to source order/spelling", mr_site == mr_src)

# 6. names, care info -------------------------------------------------------------------------------------
name_bad = []
for a in src["albums"]:
    first = a["source_pages"][0]["intro"]
    if not first:
        continue
    album = SANYO["albums"][a["id"]]
    heading = first["heading"]
    if heading == "CICHILD":
        continue
    if album["sci"].lower() != heading.lower():
        name_bad.append((a["id"], album["sci"], heading))
    if first["care"]:
        page_txt = site_text(album["page"])
        ph, temp = first["care"]["ph"], re.sub(r"\s*Degree Celsius", " °C", first["care"]["temperature"])
        if ph not in page_txt or temp not in page_txt:
            name_bad.append((a["id"], "care", ph, temp))
check("source scientific names and pH/temperature appear unchanged on album pages", not name_bad, str(name_bad))
nf_txt = site_text("new-fishes.html")
nf_ok = all(x in nf_txt for x in ["PUNTIUS DENISONI", "BOTIA KUBOTIA", "6.5 - 7.5", "18 - 25 °C", "6.8 - 7.3", "23 - 27 °C"]) and \
    all(norm(l) in nf_txt for e in src["new_fishes"] for l in e["fields"]["_description_lines"])
check("New Fishes entries keep source spelling, care values and full description text", nf_ok)
check("source misspellings preserved in the record (Cichild, HELERI)", "CICHILD" in json.dumps(src) and "XIPHOPHORUS HELERI" in json.dumps(src))

# 7. things that must NOT be published as fact -----------------------------------------------------------
pub = [f for f in os.listdir(SITE) if f.endswith(".html") and f != "content-notes.html"]
forbid = {
    "platy breeding temperature text": r"74 Degree|Celcious|65 to 90",
    "'new this week' / stock claims": r"new this week|in stock|just arrived|arrived (this|last)|limited stock",
    "prices": r"S\$\s?\d|\$\s?\d|USD|SGD\s?\d|per (kg|piece|box)\b",
    "'sent' success wording": r"(?i)(has|have) been sent successfully|message sent|successfully sent|we have received your|reference (number|no)",
    "invented certifications / testimonials": r"(?i)ISO ?9001|testimonial|customer logos|GlobalG|certificate no",
}
for label, pat in forbid.items():
    hits = [f for f in pub if re.search(pat, site_text(f))]
    check(f"no {label} on public pages", not hits, str(hits))
# platy breeding sentence only quoted on content-notes (flagged)
cn = site_text("content-notes.html")
check("platy breeding text is quoted only on the flagged content-notes page", "74 Degree Celsius" in cn and "flagged as likely erroneous" in cn)
# historical claims only inside qualified company-page section (not home/hero/catalogue)
hist_terms = ["37 years", "35 years", "OFI", "SAFEA", "AVA)", "600 holding tanks", "24-hrs"]
leak = {f: [t for t in hist_terms if t in site_text(f)] for f in pub if f not in ("company.html",)}
leak = {k: v for k, v in leak.items() if v}
check("historical claims (years, memberships, AVA, tank count, 24-hr support) appear only on the company page", not leak, str(leak))
co = site_html("company.html")
check("company page qualifies historical statements", co.count("Historical statement") >= 4 and "Not verified as current" in co)
check("Cairo kept verbatim and flagged as city, not country", "Cyprus, Cairo, New Zealand" in site_text("company.html") and "it is a city" in site_text("company.html"))
check("hero does not use the 'leading exporter' or years claims", "leading" not in site_text("index.html").lower() and "years" not in site_text("index.html").lower())
check("New Fishes page states it is undated / not current stock", "no date" in nf_txt and "not presented as recent arrivals" in nf_txt)

# 8. no hotlinking / no secrets --------------------------------------------------------------------------
hot = []
for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True):
    s = open(f, encoding="utf-8").read()
    for m in re.findall(r'<(?:img|script|link|source)[^>]+(?:src|href)="(https?://[^"]+)"', s):
        if not re.search(r'rel="(canonical|noopener)"', m):
            hot.append((os.path.basename(f), m))
hot = [h for h in hot if "stylesheet" in h[1] or h[1].lower().endswith((".jpg", ".gif", ".png", ".webp", ".js", ".css"))]
check("no hotlinked images/scripts/styles from external hosts", not hot, str(hot[:3]))
secret_pat = re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{6,}")
leaks = [os.path.relpath(f, ROOT) for f in glob.glob(os.path.join(SITE, "**", "*.*"), recursive=True)
         if f.endswith((".js", ".html", ".json", ".css")) and secret_pat.search(open(f, encoding="utf-8", errors="ignore").read())]
check("no secrets in delivered files", not leaks, str(leaks))

# 9. url map covers every source page -----------------------------------------------------------------------
urlmap = json.load(open(os.path.join(DATA, "url-map.json"), encoding="utf-8")) if os.path.exists(os.path.join(DATA, "url-map.json")) else None
if urlmap is not None:
    old = {m["old"] for m in urlmap["map"]}
    want = {os.path.basename(u) for u in pages_inv}
    check("URL map covers all 19 source pages and targets exist", old == want and all(os.path.exists(os.path.join(SITE, m["new"].split("#")[0])) for m in urlmap["map"]), str(want - old))

os.makedirs(os.path.join(ROOT, "docs", "qa"), exist_ok=True)
with open(os.path.join(ROOT, "docs", "qa", "content-fidelity.json"), "w", encoding="utf-8") as f:
    json.dump({"checks": results, "passed": sum(r["pass"] for r in results), "total": len(results)}, f, indent=1, ensure_ascii=False)
fails = [r for r in results if not r["pass"]]
print(f"\n{len(results) - len(fails)}/{len(results)} checks passed")
sys.exit(1 if fails else 0)
