"""Content-notes page, 404 page, catalogue-data.js, robots.txt, sitemap."""
import json
import os
import re

from .layout import esc, page
from .pages import page_header, notice, pill, ext_link

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def audit_counts():
    with open(os.path.join(ROOT, "source-audit", "page-inventory.json"), encoding="utf-8") as f:
        pages = json.load(f)
    with open(os.path.join(ROOT, "source-audit", "asset-inventory.json"), encoding="utf-8") as f:
        assets = json.load(f)
    imgs = [a for a in assets if a.get("status") == 200 and (a.get("content_type") or "").startswith("image")]
    return {
        "pages": len([p for p in pages if p.get("status") == 200]),
        "images": len(imgs),
        "missing": [a["url"] for a in assets if a.get("status") != 200],
    }


def content_notes_page(ctx, model, review):
    counts = audit_counts()
    blocks = model["blocks"]
    breeding = re.split(r"(?<=\.)\s+", blocks["freshwater-platy.p1.description"]["text"])
    breeding_txt = " ".join(breeding[1:])
    breeding_p2 = " ".join(re.split(r"(?<=\.)\s+", blocks["freshwater-platy.p2.description"]["text"])[1:])
    entries = []
    for e in review["entries"]:
        status = "Needs company review" if e["status"] == "open" else "Handled in this rebuild"
        kind = "warn" if e["status"] == "open" else "ok"
        pages = ", ".join(e["pages"])
        extra = ""
        if e["id"] == "R07":
            extra = f"""<blockquote class="quote flagged"><p>&ldquo;{esc(breeding_txt)}&rdquo;</p><p class="small">Page 2 wording: &ldquo;{esc(breeding_p2)}&rdquo;</p>
            <footer><strong>Original text &mdash; flagged as likely erroneous. Do not rely on it.</strong></footer></blockquote>"""
        entries.append(f"""<article class="note" id="{esc(e['id'])}">
  <h3><span class="note-id">{esc(e['id'])}</span> {esc(e['topic'])} {pill(status, kind)}</h3>
  <dl class="note-dl">
    <div><dt>Original text / anchor</dt><dd><q>{esc(e['quote'])}</q> <span class="muted small">({esc(pages)})</span></dd></div>
    <div><dt>Issue</dt><dd>{esc(e['issue'])}</dd></div>
    <div><dt>Treatment in this site</dt><dd>{esc(e['treatment'])}</dd></div>
  </dl>
  {extra}
</article>""")
    n_open = sum(1 for e in review["entries"] if e["status"] == "open")
    body = page_header([("Home", "index.html"), ("Content notes", None)], "Content notes",
                       "How the original website&rsquo;s content was carried over, and what still needs company review.")
    body += f"""
<section class="section">
  <div class="container prose-wide">
    {notice('This page is part of the review hand-over. It lists every place where the rebuild keeps, qualifies or withholds original wording. It can be removed or trimmed once the company has confirmed the items.', 'info', 'For reviewers.')}
    <h2 class="section-title">Source and capture</h2>
    <ul class="check-list">
      <li>Source: {ext_link(ctx.site['source_site'], 'sanyoaqm.com.sg')}, audited on {esc(ctx.site['audit_date'])}.</li>
      <li>{counts['pages']} linked HTML pages and {counts['images']} image files were captured (the original files are kept unchanged in the delivery package).</li>
      <li>Every page reports a last-modified date of 10 July 2012; the footer reads &ldquo;Copyright &copy; 2006&rdquo;. Nothing on the source gives prices, stock, SKUs, minimum orders or arrival dates, and none are added.</li>
      <li>Original spellings are kept exactly (for example &ldquo;Cichild&rdquo;, &ldquo;XIPHOPHORUS HELERI&rdquo;, &ldquo;PUNTIUS DENISONI&rdquo;, &ldquo;BOTIA KUBOTIA&rdquo;). Proposed corrections are always labelled as proposals and are not confirmed.</li>
      <li>Photos with no individual label are identified only by their source album and original file name.</li>
    </ul>
    <h2 class="section-title">Review log ({len(review['entries'])} items, {n_open} awaiting company review)</h2>
    <div class="notes-list">{''.join(entries)}</div>
  </div>
</section>"""
    return page(ctx, "content-notes.html", "Content notes — Sanyo Aquarium",
                "Review notes for the Sanyo Aquarium rebuild: historical statements, source spelling issues, withheld text and other content decisions.",
                "notes", body, with_data=False)


def not_found_page(ctx):
    body = page_header([("Home", "index.html"), ("Page not found", None)], "Page not found",
                       "That page does not exist on this site.")
    body += """<section class="section"><div class="container"><p><a class="btn btn-primary" href="index.html">Go to the home page</a>
    <a class="btn btn-ghost-dark" href="catalogue.html">Search the catalogue</a></p></div></section>"""
    return page(ctx, "404.html", "Page not found — Sanyo Aquarium", "The page you requested does not exist. Return to the home page or search the Sanyo Aquarium catalogue.", "none", body, with_data=False)


def catalogue_data_js(ctx, model):
    """window.SANYO: everything the browser scripts need (labels, search strings, image sizes, source links)."""
    def item_js(it):
        d = {
            "id": it["id"], "t": "photo", "album": it["album"], "sec": it["section"], "title": it["title"],
            "file": it["file_id"], "pg": it["page_no"], "img": it["asset"], "w": it["width"], "h": it["height"],
            "alt": it["alt"], "src": it["source_page"], "orig": it["original_url"], "s": it["search"],
        }
        if it.get("ai_asset"):
            d.update({"ai": it["ai_asset"], "aiAlt": it["ai_alt"], "aiW": it["ai_width"], "aiH": it["ai_height"]})
        if it.get("named"):
            n = it["named"]
            d["named"] = {"ph": n["ph"], "temp": n["temperature_display"], "name": n["name_display"]}
        return d

    albums = {}
    for aid, a in model["albums"].items():
        albums[aid] = {
            "id": aid, "label": a["label"], "title": a["title"], "sec": a["section"], "page": a["page"],
            "sci": a["sci_display"], "proposed": (a["proposed"] or {}).get("sci") or (a["proposed"] or {}).get("label"),
            "care": ({"ph": a["care"]["ph"], "temp": a["care"]["temperature_display"]} if a["care"] else None),
            "n": len(a["item_ids"]), "pages": len(a["source_pages"]),
        }
    cats = [{"id": c["id"], "t": "category", "sec": c["section"], "title": c["title"], "label": c["label"],
             "album": c["album"], "photos": c["has_photos"], "src": c["source_page"], "s": c["search"]}
            for c in model["categories"]]
    sections = [{"id": s["id"], "label": s["label"], "page": s["page"]} for s in model["sections"]]
    data = {
        "site": {"name": ctx.company_name, "emailSales": ctx.email_sales, "emailInfo": ctx.email_info, "tel": ctx.tel,
                 "imageMode": model["image_mode"],
                 "address": [ctx.addr1, ctx.addr2]},
        "sections": sections, "albums": albums, "items": [item_js(i) for i in model["items"]], "categories": cats,
        "supplyForms": model["ed"]["plant_supply_forms"], "plantSections": ["plants", "plants-driftwood"],
    }
    return "/* Generated by tools/build_site.py from data/*.json — do not edit by hand. */\nwindow.SANYO = " + \
        json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"


def robots_txt(ctx):
    lines = ["User-agent: *"]
    if ctx.site.get("noindex"):
        lines.append("Disallow: /")
        lines.append("# Preview build: noindex is ON (data/editorial.json -> site.noindex). Set it to false before public launch.")
    else:
        lines.append("Allow: /")
    if ctx.site.get("site_url"):
        lines.append("Sitemap: " + ctx.site["site_url"].rstrip("/") + "/sitemap.xml")
    return "\n".join(lines) + "\n"


def sitemap_xml(ctx, filenames):
    base = ctx.site["site_url"].rstrip("/") + "/"
    urls = "".join(f"  <url><loc>{base}{n}</loc></url>\n" for n in filenames if n != "404.html")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'
