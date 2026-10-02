"""Create delivery images (WebP, quality 90) from the untouched originals and write an image manifest.

Originals live in source-audit/originals/ and are never modified. Dimensions are preserved (no resizing, no
cropping, watermarks untouched).
"""
import hashlib
import json
import os
import shutil

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORIG = os.path.join(ROOT, "source-audit", "originals")
QUALITY = 90
AI_LABEL = "AI illustration"
AI_ALT_PREFIX = "AI-generated illustration. "
AI_ALT_COPY = {
    "company_photo": ("Generic facility illustration", "AI-generated illustration of a white industrial building with grass and small trees; not a photo of Sanyo Aquarium's premises."),
    "sanyo": ("Generic facility illustration", "AI-generated illustration of a white industrial building with grass and small trees; not a photo of Sanyo Aquarium's premises."),
    "about_us1_11": ("Illustration of packed cartons", "AI-generated illustration of plain cartons stacked in a warehouse; not a photo of Sanyo Aquarium's facility."),
    "about_us2_1": ("Illustration of a packing area", "AI-generated illustration of plain cartons and clear water-filled bags on a floor; not a photo of Sanyo Aquarium's facility."),
    "about_us3_1": ("Illustration of a packing hall", "AI-generated illustration of an indoor hall with rows of clear bags and cartons; not a photo of Sanyo Aquarium's facility."),
    "about_us4_1": ("Illustration of glass holding tanks", "AI-generated illustration of rectangular glass holding tanks in an indoor room; not a photo of Sanyo Aquarium's facility."),
    "about_us5_1": ("Illustration of tanks and equipment", "AI-generated illustration of glass tanks, hoses and buckets in an indoor room; not a photo of Sanyo Aquarium's facility."),
}
AI_MANIFEST = os.path.join(ROOT, "tools", "ai_images", "manifest.json")
COMPANY_AI_MANIFEST = os.path.join(ROOT, "tools", "ai_images", "company-manifest.json")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def to_webp(src_path, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path):
        with Image.open(dest_path) as existing:
            if existing.format != "WEBP":
                raise ValueError("Refusing to replace existing non-WebP delivery: " + dest_path)
            return existing.width, existing.height
    with Image.open(src_path) as im:
        im = im.convert("RGB")
        im.save(dest_path, "WEBP", quality=QUALITY, method=6)
        return im.width, im.height


def build_images(model, site_dir):
    manifest = []
    ai = json.load(open(AI_MANIFEST, encoding="utf-8"))
    ai_by_id = {entry["id"]: entry for entry in ai["images"]}
    known_item_ids = {item["id"] for item in model["items"]}
    if set(ai_by_id) != known_item_ids:
        raise ValueError("AI image manifest must cover each catalogue photo exactly once")
    # ---- catalogue photos
    for it in model["items"]:
        src = os.path.join(ORIG, it["src_rel"].replace("/", os.sep))
        dest = os.path.join(site_dir, it["asset"].replace("/", os.sep))
        w, h = to_webp(src, dest)
        assert (w, h) == (it["width"], it["height"]), (it["id"], w, h)
        manifest.append({
            "id": it["id"], "kind": "catalogue-photo", "album": it["album"],
            "original": "source-audit/originals/" + it["src_rel"], "original_url": it["original_url"],
            "original_sha256": it["sha256"], "original_bytes": it["bytes"], "width": w, "height": h,
            "delivered": it["asset"], "delivered_bytes": os.path.getsize(dest), "delivered_sha256": sha256_file(dest),
            "format": "WEBP q%d" % QUALITY,
        })
        ai_entry = ai_by_id[it["id"]]
        if ai_entry["status"] == "done":
            expected = "generated/imagen/{}/{}.webp".format(it["album"], os.path.splitext(it["file_id"])[0])
            if ai_entry.get("output_path") != expected:
                raise ValueError("Unexpected AI output path for " + it["id"])
            ai_src = os.path.join(ROOT, expected.replace("/", os.sep))
            if not os.path.isfile(ai_src) or sha256_file(ai_src) != ai_entry.get("output_sha256"):
                raise ValueError("AI image is missing or its SHA-256 differs from the manifest: " + it["id"])
            ai_rel = "assets/img/generated/{}/{}.webp".format(it["album"], os.path.splitext(it["file_id"])[0])
            ai_dest = os.path.join(site_dir, ai_rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(ai_dest), exist_ok=True)
            if not os.path.exists(ai_dest) or sha256_file(ai_dest) != ai_entry["output_sha256"]:
                shutil.copyfile(ai_src, ai_dest)
            with Image.open(ai_src) as variant:
                it["ai_width"], it["ai_height"] = variant.size
            it["ai_asset"] = ai_rel
            it["ai_alt"] = AI_ALT_PREFIX + it["alt"]
            it["ai_sha256"] = ai_entry["output_sha256"]
            manifest.append({
                "id": it["id"], "kind": "catalogue-ai-illustration", "album": it["album"],
                "original": "source-audit/originals/" + it["src_rel"], "original_sha256": it["sha256"],
                "delivered": ai_rel, "delivered_sha256": ai_entry["output_sha256"],
                "width": it["ai_width"], "height": it["ai_height"], "label": AI_LABEL,
                "tool": ai_entry.get("tool_reported"), "model": ai_entry.get("model_reported"),
            })
    # ---- company imagery
    ci = model["ed"]["company_images"]
    company_files = [ci["exterior"]["file"], ci["exterior_contact"]["file"], ci["member_strip"]["file"]] + \
                    [f["file"] for f in ci["facility"]]
    company_photos = [ci["exterior"], ci["exterior_contact"]] + ci["facility"]
    company_by_stem = {os.path.splitext(photo["file"])[0]: photo for photo in company_photos}
    company_ai = json.load(open(COMPANY_AI_MANIFEST, encoding="utf-8"))
    company_ai_by_id = {entry["id"]: entry for entry in company_ai["images"]}
    expected_company_ai = {"company-" + stem for stem in AI_ALT_COPY}
    if set(company_ai_by_id) != expected_company_ai or set(company_by_stem) != set(AI_ALT_COPY):
        raise ValueError("Company AI image manifest must cover each building and facility photo exactly once")
    for fn in company_files:
        src = os.path.join(ORIG, "images", fn)
        stem = os.path.splitext(fn)[0]
        dest_rel = "assets/img/company/" + stem + ".webp"
        dest = os.path.join(site_dir, dest_rel.replace("/", os.sep))
        w, h = to_webp(src, dest)
        if stem in company_by_stem:
            company_by_stem[stem]["original_width"] = w
            company_by_stem[stem]["original_height"] = h
        manifest.append({
            "id": "company-" + stem, "kind": "company-photo",
            "original": "source-audit/originals/images/" + fn, "original_url": "https://www.sanyoaqm.com.sg/images/" + fn,
            "original_sha256": sha256_file(src), "original_bytes": os.path.getsize(src), "width": w, "height": h,
            "delivered": dest_rel, "delivered_bytes": os.path.getsize(dest), "delivered_sha256": sha256_file(dest),
            "format": "WEBP q%d" % QUALITY,
        })
        if stem not in company_by_stem:
            continue
        entry = company_ai_by_id["company-" + stem]
        photo = company_by_stem[stem]
        photo["original_asset"] = dest_rel
        photo["ai_caption"], photo["ai_alt"] = AI_ALT_COPY[stem]
        if entry.get("status") != "done" or entry.get("original_sha256") != sha256_file(src):
            raise ValueError("Company AI image is unaccepted or its original hash differs from the manifest: " + stem)
        expected = "generated/imagen/company/{}.webp".format(stem)
        if entry.get("output_path") != expected:
            raise ValueError("Unexpected company AI output path for " + stem)
        ai_src = os.path.join(ROOT, expected.replace("/", os.sep))
        if not os.path.isfile(ai_src) or sha256_file(ai_src) != entry.get("output_sha256"):
            raise ValueError("Company AI image is missing or its SHA-256 differs from the manifest: " + stem)
        with Image.open(ai_src) as variant:
            ai_w, ai_h = variant.size
            if ai_w < w * 2 or ai_h < h * 2:
                raise ValueError("Company AI image must be at least twice the source dimensions: " + stem)
        ai_rel = "assets/img/generated/company/{}.webp".format(stem)
        ai_dest = os.path.join(site_dir, ai_rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(ai_dest), exist_ok=True)
        shutil.copyfile(ai_src, ai_dest)
        photo["ai_asset"] = ai_rel
        photo["ai_width"], photo["ai_height"] = ai_w, ai_h
        manifest.append({
            "id": "company-" + stem, "kind": "company-ai-illustration",
            "original": "source-audit/originals/images/" + fn,
            "original_sha256": entry["original_sha256"], "delivered": ai_rel,
            "delivered_sha256": entry["output_sha256"], "width": ai_w, "height": ai_h,
            "label": AI_LABEL, "tool": entry.get("tool_reported"), "model": entry.get("model_reported"),
        })
    # ---- logo (original GIF copied unchanged) + favicon derived from it
    brand = os.path.join(site_dir, "assets", "img", "brand")
    os.makedirs(brand, exist_ok=True)
    logo_src = os.path.join(ORIG, "images", ci["logo"]["file"])
    logo_dest = os.path.join(brand, "logo.gif")
    shutil.copyfile(logo_src, logo_dest)
    manifest.append({
        "id": "brand-logo", "kind": "logo", "original": "source-audit/originals/images/" + ci["logo"]["file"],
        "original_url": "https://www.sanyoaqm.com.sg/images/" + ci["logo"]["file"],
        "original_sha256": sha256_file(logo_src), "original_bytes": os.path.getsize(logo_src),
        "delivered": "assets/img/brand/logo.gif", "delivered_bytes": os.path.getsize(logo_dest),
        "delivered_sha256": sha256_file(logo_dest), "format": "GIF (unchanged copy)",
    })
    with Image.open(logo_src) as im:
        im = im.convert("RGB")
        side = max(im.size)
        canvas = Image.new("RGB", (side, side), (255, 255, 255))
        canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
        canvas = canvas.resize((64, 64), Image.LANCZOS)
        canvas.save(os.path.join(brand, "favicon.png"))
    manifest.append({"id": "brand-favicon", "kind": "derived-icon", "original": "source-audit/originals/images/" + ci["logo"]["file"],
                     "delivered": "assets/img/brand/favicon.png", "format": "PNG 64x64 (logo on white, derived)"})
    return manifest
