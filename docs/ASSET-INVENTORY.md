# Asset inventory (live audit)

Captured 2026-10-02. Every downloadable asset is stored unchanged under `source-audit/originals/` with its SHA-256, pixel size and capture time in `ASSET-INVENTORY.csv`.

* Downloadable image files: **132** (the prior audit counted 131; the extra file is `images/SanyoPhoto.jpg`, which exists on the server but is referenced only inside an HTML comment on the contact page).
* Also captured: `css/sanyo.css`.
* Missing / inaccessible: `favicon.ico` (404), `images/dot.gif` (404), `images/images/homepic11.jpg` (404), `robots.txt` (404), `sitemap.xml` (404).
* `images/images/homepic11.jpg` and `images/dot.gif` are referenced by the source markup but return 404.

## Classification of the downloaded images

| Class | Files |
|---|---|
| product photograph (gallery) | 102 |
| company / facility photograph | 7 |
| legacy section banner (baked-in title text) | 7 |
| legacy layout fragment / spacer | 5 |
| legacy home banner tile | 4 |
| third-party membership logo (legacy footer) | 3 |
| company logo | 1 |
| company photograph (commented out in source) | 1 |
| third-party membership logos (strip) | 1 |
| legacy decorative header banner (aquascape strip) | 1 |

These counts describe files, not products: gallery photos are not product counts and are not used as marketing statistics.

## Delivered images

Gallery and company photographs are re-encoded to WebP (quality 90) at their original pixel size. Nothing is resized, cropped or de-watermarked. `data/image-manifest.json` links each delivered file to its original, with both SHA-256 values.
