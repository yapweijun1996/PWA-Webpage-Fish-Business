"""Merge data/source-record.json + data/editorial.json into the catalogue model used by the site generator."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
IMAGE_MODES = {"original", "ai-illustration", "both"}


def load_json(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def sci_case(s):
    """'XIPHOPHORUS HELERI' -> 'Xiphophorus heleri' (casing only; letters are never changed)."""
    parts = s.split()
    if not parts:
        return s
    return " ".join([parts[0].capitalize()] + [p.lower() for p in parts[1:]])


def temp_display(t):
    return re.sub(r"\s*Degree Celsius\s*$", " °C", t.strip())


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def stem(filename):
    return os.path.splitext(filename)[0]


def build():
    src = load_json("source-record.json")
    ed = load_json("editorial.json")
    image_mode = ed.get("site", {}).get("image_mode", "ai-illustration")
    if image_mode not in IMAGE_MODES:
        raise ValueError("site.image_mode must be one of: original, ai-illustration, both")
    blocks = {b["id"]: b for b in src["blocks"]}
    sections = {s["id"]: s for s in ed["sections"]}

    albums = {}
    items = []
    order = []

    # ---- family / gallery albums
    for a in src["albums"]:
        meta = ed["albums"][a["id"]]
        first = a["source_pages"][0]
        intro = first["intro"] or {}
        care = intro.get("care")
        # description: allow editorial override (withheld text), else verbatim source description of page 1
        desc = meta.get("description_show", intro.get("description"))
        album = {
            "id": a["id"],
            "section": meta["section"],
            "label": meta["label"],
            "title": meta["title"],
            "page": meta["page"],
            "sci_source": meta.get("sci_source"),
            "sci_display": sci_case(meta["sci_source"]) if meta.get("sci_source") else None,
            "proposed": meta.get("proposed"),
            "aliases": meta.get("aliases", []),
            "care": {"ph": care["ph"], "temperature": care["temperature"],
                     "temperature_display": temp_display(care["temperature"])} if care else None,
            "description": desc,
            "description_is_source_verbatim": ("description_show" not in meta) and bool(desc),
            "withheld": meta.get("withheld"),
            "review_ids": meta.get("review_ids", []),
            "source_pages": [{"url": p["url"], "page_no": p["page_no"], "image_count": p["image_count"]}
                             for p in a["source_pages"]],
            "item_ids": [],
        }
        albums[a["id"]] = album
        order.append(a["id"])
        for it in a["items"]:
            fid = stem(it["file"])
            iid = f"{a['id']}-{fid}"
            title = f"{meta['label']} - photo {fid}"
            item = {
                "id": iid, "type": "photo", "album": a["id"], "section": meta["section"],
                "title": title, "file_id": it["file"], "page_no": it["page_no"],
                "source_page": it["source_page"], "original_url": it["original_url"],
                "local_original": it["local_original"], "width": it["width"], "height": it["height"],
                "sha256": it["sha256"], "bytes": it["bytes"], "captured_at": it["captured_at"],
                "src_rel": it["src"],  # e.g. images/freshwater_fishes/platy/005.jpg
                "alt": f"{meta['title']} gallery, photo {fid}",
            }
            items.append(item)
            album["item_ids"].append(iid)

    # ---- new fishes (named entries)
    nf_album = {
        "id": "new-fishes", "section": "new", "label": ed["albums"]["new-fishes"]["label"],
        "title": "New Fishes", "page": "new-fishes.html", "sci_source": None, "sci_display": None,
        "proposed": None, "aliases": [], "care": None, "description": None,
        "description_is_source_verbatim": False, "withheld": None,
        "review_ids": ed["albums"]["new-fishes"]["review_ids"],
        "source_pages": [{"url": src["pages"]["newfishes.html"]["url"], "page_no": 1, "image_count": 2}],
        "item_ids": [],
    }
    albums["new-fishes"] = nf_album
    order.append("new-fishes")
    for e, meta in zip(src["new_fishes"], ed["new_fishes"]):
        f = e["fields"]
        fid = stem(e["image"]["file"])
        item = {
            "id": meta["id"], "type": "photo", "album": "new-fishes", "section": "new",
            "title": sci_case(f["Name"]), "file_id": e["image"]["file"], "page_no": 1,
            "source_page": src["pages"]["newfishes.html"]["url"], "original_url": e["image"]["original_url"],
            "local_original": e["image"]["local_original"], "width": e["image"]["width"], "height": e["image"]["height"],
            "sha256": e["image"]["sha256"], "bytes": e["image"]["bytes"], "captured_at": e["image"]["captured_at"],
            "src_rel": e["image"]["src"],
            "alt": f"New Fishes page entry: {sci_case(f['Name'])} (photo {fid})",
            "named": {
                "name_source": f["Name"], "name_display": sci_case(f["Name"]),
                "ph": f["pH"], "temperature": f["Temperature"], "temperature_display": temp_display(f["Temperature"]),
                "description_lines": e["fields"]["_description_lines"],
                "proposed": meta.get("proposed"), "aliases": meta.get("aliases", []),
            },
        }
        items.append(item)
        nf_album["item_ids"].append(item["id"])

    # ---- delivered image paths (WebP derivatives) -------------------------------------------
    for it in items:
        rel = it["src_rel"].replace("images/", "", 1)  # freshwater_fishes/platy/005.jpg
        it["asset"] = "assets/img/catalogue/" + os.path.splitext(rel)[0] + ".webp"

    # ---- category lists (names exactly as listed on the source)
    categories = []
    fw_album_by_label = {albums[a]["label"].lower(): a for a in albums if albums[a]["section"] == "freshwater"}
    for idx, c in enumerate(src["freshwater_categories"], 1):
        album_id = fw_album_by_label.get(c["text"].lower())
        categories.append({
            "id": f"cat-freshwater-{slug(c['text'])}",
            "type": "category", "section": "freshwater", "label": c["text"], "album": album_id,
            "title": c["text"] if c["text"] != "other" else "Other freshwater",
            "source_page": src["pages"]["freshwaterfishes.html"]["url"], "has_photos": bool(album_id),
            "order": idx,
        })
    for idx, c in enumerate(src["marine_categories"], 1):
        categories.append({
            "id": f"cat-marine-{slug(c['text'])}", "type": "category", "section": "marine", "label": c["text"],
            "album": None, "title": c["text"], "source_page": src["pages"]["marinefish.html"]["url"],
            "has_photos": False, "order": idx,
        })
    # deduplicate ids deterministically (e.g. 'Snails' / 'Snail' are different slugs; guard anyway)
    seen = set()
    for c in categories:
        base, n = c["id"], 2
        while c["id"] in seen:
            c["id"] = f"{base}-{n}"
            n += 1
        seen.add(c["id"])
    # whole-category lines for pages without a listed category (plants, driftwood)
    categories.append({"id": "cat-plants-aquatic-plants", "type": "category", "section": "plants", "label": "Aquatic plants",
                       "album": "aquatic-plants", "title": "Aquatic plants (any)", "source_page": src["pages"]["aquaticplants.html"]["url"],
                       "has_photos": True, "order": 1})
    categories.append({"id": "cat-driftwood-driftwood", "type": "category", "section": "driftwood", "label": "Driftwood",
                       "album": "driftwood", "title": "Driftwood (any)", "source_page": src["pages"]["driftwood.html"]["url"],
                       "has_photos": True, "order": 1})
    categories.append({"id": "cat-marine-any", "type": "category", "section": "marine", "label": "Marine fishes",
                       "album": "marine-fishes", "title": "Marine fishes (any)", "source_page": src["pages"]["marinefish.html"]["url"],
                       "has_photos": True, "order": 0})
    categories.append({"id": "cat-plants-driftwood-any", "type": "category", "section": "plants-driftwood",
                       "label": "Aquatic plants on driftwood", "album": "plants-on-driftwood",
                       "title": "Plants on driftwood (any)", "source_page": src["pages"]["aquaticplants_on_driftwood.html"]["url"],
                       "has_photos": True, "order": 1})

    # ---- search haystacks ---------------------------------------------------------------------
    def hay(*parts):
        txt = " ".join(p for p in parts if p)
        return re.sub(r"\s+", " ", txt.lower().replace("_", " ").replace("·", " ")).strip()

    sec_label = {s["id"]: s["label"] for s in ed["sections"]}
    for it in items:
        a = albums[it["album"]]
        extra = []
        if it.get("named"):
            n = it["named"]
            extra += [n["name_source"], n["name_display"], " ".join(n["aliases"])]
            if n["proposed"]:
                extra.append(n["proposed"]["sci"])
        it["search"] = hay(it["title"], a["label"], a["title"], a["sci_source"], a["sci_display"], " ".join(a["aliases"]),
                           (a["proposed"] or {}).get("sci"), (a["proposed"] or {}).get("label"),
                           sec_label[it["section"]], it["file_id"], stem(it["file_id"]),
                           os.path.basename(it["source_page"]), "photo", *extra)
    for c in categories:
        a = albums.get(c["album"]) if c["album"] else None
        extra = []
        if a:
            extra = [a["sci_source"], a["sci_display"], " ".join(a["aliases"]), (a["proposed"] or {}).get("sci"),
                     (a["proposed"] or {}).get("label")]
        c["search"] = hay(c["label"], c["title"], sec_label[c["section"]], "category listed", *extra)

    return {
        "src": src, "ed": ed, "blocks": blocks, "sections": ed["sections"], "sections_by_id": sections,
        "albums": albums, "album_order": order, "items": items,
        "items_by_id": {i["id"]: i for i in items}, "categories": categories,
        "contact": src["contact"], "image_mode": image_mode,
    }
