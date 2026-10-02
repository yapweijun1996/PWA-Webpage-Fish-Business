#!/usr/bin/env python3
"""Build the structured source record from the raw crawl (no network access).

Input : source-audit/raw-html/*.html, source-audit/page-inventory.json, source-audit/asset-inventory.json
Output: data/source-record.json  (verbatim text blocks + gallery items, each with its source URL)

Every text value stored here is taken verbatim from the raw HTML (whitespace normalised only).
Run:  python tools/extract_source.py
"""
import json
import os
import re

from bs4 import BeautifulSoup, Comment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "source-audit")
RAW = os.path.join(AUDIT, "raw-html")
OUT = os.path.join(ROOT, "data")
BASE = "https://www.sanyoaqm.com.sg/"

pages_inv = {p["url"]: p for p in json.load(open(os.path.join(AUDIT, "page-inventory.json"), encoding="utf-8"))}
assets_inv = {a["url"]: a for a in json.load(open(os.path.join(AUDIT, "asset-inventory.json"), encoding="utf-8"))}


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def load(name):
    raw = open(os.path.join(RAW, name), "rb").read().decode("cp1252")
    return raw, BeautifulSoup(raw, "lxml")


def comments_text(raw):
    """Text that exists only inside HTML comments (legacy leftovers, not published)."""
    found = []
    for c in re.findall(r"<!--(.*?)-->", raw, re.S):
        if "Template" in c or "DWLayout" in c:
            continue
        t = norm(re.sub(r"<[^>]+>", " ", c))
        if t:
            found.append(t)
    return found


def img_meta(rel):
    """Asset facts for 'images/...' relative path."""
    url = BASE + rel
    a = assets_inv.get(url, {})
    return {
        "original_url": url,
        "local_original": a.get("local_path"),
        "width": a.get("width"),
        "height": a.get("height"),
        "bytes": a.get("bytes"),
        "sha256": a.get("sha256"),
        "last_modified": a.get("last_modified"),
        "captured_at": a.get("captured_at"),
    }


GALLERY_RE = re.compile(r"^images/(freshwater_fishes|aquatic_plants|marine_fishes|new_fishes|driftwood)/(.+)$")


def gallery_imgs(soup, page_url):
    out = []
    for i, im in enumerate(soup.find_all("img")):
        m = GALLERY_RE.match(im.get("src", ""))
        if m:
            out.append({
                "src": im["src"],
                "dir": m.group(1),
                "file": os.path.basename(m.group(2)),
                "display_width_attr": im.get("width"),
                "display_height_attr": im.get("height"),
                "source_page": page_url,
                **img_meta(im["src"]),
            })
    return out


def care_split(td_text):
    """Split an album intro 'HEADING pH: x; Temperature: y; description' into parts."""
    m = re.search(r"pH:\s*([^;]+);\s*Temperature:\s*([^;]+);", td_text)
    return {"ph": norm(m.group(1)), "temperature": norm(m.group(2)), "raw": norm(m.group(0))} if m else None


def album_intro(soup):
    """The <td colspan=3> block holding heading + care + description on family gallery pages."""
    for td in soup.find_all("td", colspan="3"):
        b = td.find("b")
        if b and td.find("font"):
            heading = norm(b.get_text())
            full = norm(td.get_text(" "))
            rest = norm(full.replace(heading, "", 1))
            care = care_split(rest)
            desc = rest
            if care:
                desc = norm(rest.replace(care["raw"], "", 1))
            return {"heading": heading, "care": care, "description": desc or None, "full_text": full}
    return None


def lists(soup):
    out = []
    for ul in soup.find_all("ul"):
        items = []
        for li in ul.find_all("li"):
            a = li.find("a")
            items.append({"text": norm(li.get_text()), "link": a["href"] if a else None})
        out.append(items)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    record = {
        "source_base": BASE,
        "note": "All 'text' values are verbatim from the original pages (whitespace normalised). "
                "Classes: company_information, contact_details, product_category, named_product, gallery_image, "
                "care_information, supply_form, shipment_information, historical_claim.",
        "pages": {},
        "blocks": [],
        "albums": [],
    }
    blocks = record["blocks"]

    def add(block_id, cls, page, text, **extra):
        blocks.append({"id": block_id, "class": cls, "source_page": BASE + page, "text": text, **extra})

    # ---- page-level metadata for all pages
    for url, p in sorted(pages_inv.items()):
        name = os.path.basename(url)
        raw, soup = load(name)
        record["pages"][name] = {
            "url": url,
            "title": p.get("title"),
            "last_modified": p.get("last_modified"),
            "captured_at": p.get("captured_at"),
            "sha256": p.get("sha256"),
            "bytes": p.get("bytes"),
            "commented_out_text": comments_text(raw),
            "commented_out_images": p.get("commented_out_images", []),
        }

    # ---- index.html
    raw, soup = load("index.html")
    md = soup.find("meta", attrs={"name": "description"})
    add("home.meta_description", "company_information", "index.html", md["content"])
    kw = soup.find("meta", attrs={"name": "keywords"})
    add("home.meta_keywords", "company_information", "index.html", kw["content"])
    record["home_images"] = [
        {"role": "home banner tile", **{k: v for k, v in img_meta(f"images/images/homepic-31-1-2007_0{i}.jpg").items()},
         "file": f"homepic-31-1-2007_0{i}.jpg"} for i in (1, 2, 3, 4)
    ]

    # ---- aboutus.html
    raw, soup = load("aboutus.html")
    ps = soup.find_all("p", class_="content_content")
    add("about.intro", "company_information", "aboutus.html", norm(ps[0].get_text()))
    add("about.customers", "historical_claim", "aboutus.html", norm(ps[1].get_text()))
    add("about.qualities.intro", "company_information", "aboutus.html", norm(ps[2].get_text()))
    uls = soup.find_all("ul", class_="content_content")
    for n, li in enumerate(uls[0].find_all("li"), 1):
        add(f"about.quality_process.{n}", "historical_claim", "aboutus.html", norm(li.get_text()))
    for n, li in enumerate(uls[1].find_all("li"), 1):
        add(f"about.services.{n}", "historical_claim" if n == 3 else "company_information", "aboutus.html", norm(li.get_text()))
    for n, li in enumerate(uls[2].find_all("li"), 1):
        add(f"about.assurance.{n}", "company_information", "aboutus.html", norm(li.get_text()))
    # linked organisations (OFI, SAFEA, AVA)
    orgs = []
    for a in ps[0].find_all("a"):
        orgs.append({"text": norm(a.get_text()), "href": a["href"]})
    record["about_orgs"] = orgs
    record["about_images"] = [
        {"role": r, "file": f, **img_meta(f"images/{f}")}
        for r, f in [("company exterior photo (profile)", "company_photo.jpg"),
                     ("membership logo strip", "aboutus_member.jpg"),
                     ("quality section photo 1", "about_us1_11.jpg"),
                     ("facility photo 2", "about_us2_1.jpg"),
                     ("facility photo 3", "about_us3_1.jpg"),
                     ("facility photo 4", "about_us4_1.jpg"),
                     ("facility photo 5", "about_us5_1.jpg")]
    ]

    # ---- contact.html
    raw, soup = load("contact.html")
    addr = soup.find("td", class_="content_address")
    lines = [norm(x) for x in addr.get_text("\n").split("\n") if norm(x)]
    record["contact_lines"] = lines
    add("contact.intro", "contact_details", "contact.html", "If you have any enquiries, please contact us.")
    add("contact.address_block", "contact_details", "contact.html", " | ".join(lines))
    record["contact"] = {
        "name": lines[0],
        "address_lines": lines[1:3],
        "tel": re.sub(r"^Tel:\s*", "", lines[3]),
        "fax": [re.sub(r"^Fax:\s*", "", lines[4]), lines[5]],
        "emails": [a["href"].replace("mailto:", "") for a in addr.find_all("a")],
    }
    form = soup.find("form")
    record["source_contact_form"] = {
        "action": form["action"], "method": form["method"],
        "fields": [i.get("name") for i in form.find_all(["input", "textarea"]) if i.get("name")],
        "labels": [norm(td.get_text()) for td in form.find_all("td", class_="content_content")],
        "note": "Original form posts to sendMail.php on the original server. The rebuild does NOT post to it.",
    }
    record["contact_images"] = [{"role": "contact page photo (active)", "file": "sanyo.jpg", **img_meta("images/sanyo.jpg")},
                                {"role": "commented-out in source markup", "file": "SanyoPhoto.jpg", **img_meta("images/SanyoPhoto.jpg")}]

    # ---- freshwaterfishes.html (category overview)
    raw, soup = load("freshwaterfishes.html")
    p = soup.find("p", class_="content_content")
    add("freshwater.intro", "product_category", "freshwaterfishes.html", norm(p.get_text().split("[Click")[0]))
    add("freshwater.click_hint", "product_category", "freshwaterfishes.html", norm("[Click" + p.get_text().split("[Click")[1]))
    cats = [i for ul in lists(soup) for i in ul]
    record["freshwater_categories"] = cats
    for n, c in enumerate(cats, 1):
        add(f"freshwater.category.{n}", "product_category", "freshwaterfishes.html", c["text"], link=c["link"])

    # ---- marinefish.html (category overview)
    raw, soup = load("marinefish.html")
    p = soup.find("p", class_="content_content")
    add("marine.intro", "product_category", "marinefish.html", norm(p.get_text()))
    cats = [i for ul in lists(soup) for i in ul]
    record["marine_categories"] = cats
    for n, c in enumerate(cats, 1):
        add(f"marine.category.{n}", "product_category", "marinefish.html", c["text"])

    # ---- plants intro + supply forms
    raw, soup = load("aquaticplants.html")
    sf = [t for t in soup.stripped_strings if t.startswith("Sanyo Aquarium carries a wide variety")][0]
    add("plants.intro", "supply_form", "aquaticplants.html", norm(sf))

    # ---- driftwood shipment info
    raw, soup = load("driftwood.html")
    dt = [norm(td.get_text()) for td in soup.find_all("td", class_="content_content") if "driftwood" in td.get_text().lower()][0]
    add("driftwood.intro", "shipment_information", "driftwood.html", dt)

    # ---- gallery albums (pages grouped)
    ALBUMS = [
        # id, section, label, [pages]
        ("freshwater-platy", "freshwater", "Platy", ["freshwaterfishes_platy.html", "freshwaterfishes_platy_2.html"]),
        ("freshwater-molly", "freshwater", "Molly", ["freshwaterfishes_molly.html"]),
        ("freshwater-guppy", "freshwater", "Guppy", ["freshwaterfishes_guppy.html"]),
        ("freshwater-swordtail", "freshwater", "Swordtail", ["freshwaterfishes_swordtail.html"]),
        ("freshwater-cichild", "freshwater", "Cichild", ["freshwaterfishes_cichild.html"]),
        ("marine-fishes", "marine", "Marine fishes", ["marinefish_more_pictures_1.html", "marinefish_more_pictures_2.html"]),
        ("aquatic-plants", "plants", "Aquatic plants", ["aquaticplants.html", "aquaticplants_2.html", "aquaticplants_3.html"]),
        ("plants-on-driftwood", "plants-driftwood", "Aquatic plants on driftwood", ["aquaticplants_on_driftwood.html"]),
        ("driftwood", "driftwood", "Driftwood", ["driftwood.html"]),
    ]
    for aid, section, label, pnames in ALBUMS:
        album = {"id": aid, "section": section, "source_label": label, "source_pages": [], "items": []}
        for pi, pn in enumerate(pnames, 1):
            raw, soup = load(pn)
            url = BASE + pn
            intro = album_intro(soup)
            imgs = gallery_imgs(soup, url)
            album["source_pages"].append({"url": url, "page_no": pi, "intro": intro, "image_count": len(imgs)})
            for order, im in enumerate(imgs, 1):
                im["page_no"] = pi
                im["order_on_page"] = order
                album["items"].append(im)
            if intro:
                add(f"{aid}.p{pi}.heading", "named_product", pn, intro["heading"])
                if intro["care"]:
                    add(f"{aid}.p{pi}.care", "care_information", pn, intro["care"]["raw"], ph=intro["care"]["ph"],
                        temperature=intro["care"]["temperature"])
                if intro["description"]:
                    add(f"{aid}.p{pi}.description", "care_information", pn, intro["description"])
        record["albums"].append(album)
        for im in album["items"]:
            add(f"{aid}.img.{os.path.splitext(im['file'])[0]}", "gallery_image", os.path.basename(im["source_page"]),
                im["src"], original_url=im["original_url"])

    # ---- newfishes.html (named entries, each with its photo)
    raw, soup = load("newfishes.html")
    entries = []
    for tbl in soup.find_all("table", class_="content_newfishes"):
        row = {}
        for tr in tbl.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) == 2 and tds[0].find("b"):
                key = norm(tds[0].get_text()).rstrip(":")
                val = norm(tds[1].get_text())
                if val:
                    row[key] = val
            elif len(tds) == 1:
                row["_description_lines"] = [norm(x) for x in tds[0].get_text("\n").split("\n") if norm(x)]
        img = tbl.find_previous("img", src=re.compile(r"new_fishes"))
        entries.append({"fields": row, "image": {"src": img["src"], "file": os.path.basename(img["src"]), **img_meta(img["src"])}})
    record["new_fishes"] = entries
    for n, e in enumerate(entries, 1):
        f = e["fields"]
        add(f"newfishes.{n}.name", "named_product", "newfishes.html", f["Name"], image=e["image"]["src"])
        add(f"newfishes.{n}.care", "care_information", "newfishes.html", f"pH: {f['pH']} Temperature: {f['Temperature']}")
        add(f"newfishes.{n}.description", "care_information", "newfishes.html", " ".join(e["fields"]["_description_lines"]))
        add(f"newfishes.{n}.photo", "gallery_image", "newfishes.html", e["image"]["src"], original_url=e["image"]["original_url"])

    with open(os.path.join(OUT, "source-record.json"), "w", encoding="utf-8") as f:
        json.dump(record, f, indent=1, ensure_ascii=False)

    n_items = sum(len(a["items"]) for a in record["albums"]) + len(entries)
    print(f"blocks: {len(blocks)}  albums: {len(record['albums'])}  gallery photos: {n_items}")
    for a in record["albums"]:
        print(f"  {a['id']:22} {len(a['items']):3} photos  pages={len(a['source_pages'])}")
    print("  new fishes entries:", len(entries))


if __name__ == "__main__":
    main()
