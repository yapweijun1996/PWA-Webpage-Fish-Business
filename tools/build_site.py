#!/usr/bin/env python3
"""Generate the static website into site/ from data/*.json, src/ (CSS/JS) and source-audit/originals/.

Prerequisites: Python 3.9+ and Pillow (pip install pillow).
Run from the project root:   python tools/build_site.py
Output: site/ (ready to serve with any static web server), data/image-manifest.json
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sitegen.data import build, load_json  # noqa: E402
from sitegen.images import build_images  # noqa: E402
from sitegen.layout import Ctx  # noqa: E402
from sitegen.pages import build_pages  # noqa: E402
from sitegen import notes  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
SRC = os.path.join(ROOT, "src")


def write(rel, text):
    path = os.path.join(SITE, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


URL_MAP = [
    # old page, new page, note
    ("index.html", "index.html", "Home; the four legacy banner tiles are not migrated (see review log R22)."),
    ("aboutus.html", "company.html", "Company profile; historical claims moved into a qualified section."),
    ("freshwaterfishes.html", "freshwater-fishes.html", "Category overview; the 24 listed categories are kept in source order."),
    ("freshwaterfishes_platy.html", "freshwater-platy.html", "Original page 1 of the Platy gallery."),
    ("freshwaterfishes_platy_2.html", "freshwater-platy.html", "Original page 2 of the Platy gallery (combined)."),
    ("freshwaterfishes_molly.html", "freshwater-molly.html", ""),
    ("freshwaterfishes_guppy.html", "freshwater-guppy.html", ""),
    ("freshwaterfishes_swordtail.html", "freshwater-swordtail.html", ""),
    ("freshwaterfishes_cichild.html", "freshwater-cichild.html", "Source spelling 'Cichild' retained."),
    ("marinefish.html", "marine-fishes.html", "Marine category list (22 entries)."),
    ("marinefish_more_pictures_1.html", "marine-fishes.html#gallery", "Marine photo gallery, original page 1 (combined)."),
    ("marinefish_more_pictures_2.html", "marine-fishes.html#gallery", "Marine photo gallery, original page 2 (combined)."),
    ("aquaticplants.html", "aquatic-plants.html", "Aquatic plants gallery, original page 1 of 3 (combined)."),
    ("aquaticplants_2.html", "aquatic-plants.html", "Original page 2 of 3 (combined)."),
    ("aquaticplants_3.html", "aquatic-plants.html", "Original page 3 of 3 (combined)."),
    ("aquaticplants_on_driftwood.html", "plants-on-driftwood.html", "Distinct source gallery retained."),
    ("newfishes.html", "new-fishes.html", "Renamed 'New Fishes (source page)'; undated, not a stock statement."),
    ("driftwood.html", "driftwood.html", ""),
    ("contact.html", "contact.html", "Contact details; the source form (sendMail.php) is replaced by the enquiry workflow at enquiry.html."),
]
NEW_ONLY = [
    ("catalogue.html", "New: search and filters across every photo and category."),
    ("enquiry.html", "New: enquiry list, details, review and email-draft/export (no server submission)."),
    ("content-notes.html", "New: review hand-over notes."),
    ("404.html", "New: not-found page for static hosts."),
]


def write_url_map(model):
    entries = [{"old": o, "old_url": "https://www.sanyoaqm.com.sg/" + o, "new": n, "note": note} for o, n, note in URL_MAP]
    with open(os.path.join(ROOT, "data", "url-map.json"), "w", encoding="utf-8") as f:
        json.dump({"map": entries, "new_pages_without_old_equivalent": [{"new": n, "note": t} for n, t in NEW_ONLY]},
                  f, indent=1, ensure_ascii=False)


def main():
    model = build()
    ctx = Ctx(model)
    review = load_json("review-log.json")

    # Keep previously delivered image files in place. Individual source-derived
    # WebPs are left untouched by build_images when they already exist.
    os.makedirs(SITE, exist_ok=True)

    # static assets
    for sub in ("css", "js"):
        dest = os.path.join(SITE, "assets", sub)
        os.makedirs(dest, exist_ok=True)
        for fn in os.listdir(os.path.join(SRC, sub)):
            shutil.copyfile(os.path.join(SRC, sub, fn), os.path.join(dest, fn))

    manifest = build_images(model, SITE)
    with open(os.path.join(ROOT, "data", "image-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)

    pages, _ = build_pages(ctx, model)
    pages["content-notes.html"] = notes.content_notes_page(ctx, model, review)
    pages["404.html"] = notes.not_found_page(ctx)
    for name, html in pages.items():
        write(name, html)
    write_url_map(model)
    write("assets/js/catalogue-data.js", notes.catalogue_data_js(ctx, model))
    write("robots.txt", notes.robots_txt(ctx))
    if ctx.site.get("site_url"):
        write("sitemap.xml", notes.sitemap_xml(ctx, sorted(pages)))

    total_mb = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(SITE) for f in fs) / 1e6
    print(f"built {len(pages)} pages, {len(model['items'])} catalogue photos, {len(manifest)} image records, site size {total_mb:.2f} MB")


if __name__ == "__main__":
    main()
