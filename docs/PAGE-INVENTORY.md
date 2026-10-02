# Page inventory (live audit)

Captured with `tools/crawl_source.py` on **2026-10-02** from https://www.sanyoaqm.com.sg/index.html by following every same-domain link (breadth-first). Raw HTML is kept unchanged in `source-audit/raw-html/`.

* Reachable HTML pages: **19** (all HTTP 200). Pages that failed or were inaccessible: **none**.
* The prior audit also reported 19 linked HTML pages; this audit found the same 19. Differences in the asset total are explained in ASSET-INVENTORY.md.
* Every page returns `Last-Modified: Tue, 10 Jul 2012`; the footer reads “Copyright © 2006”.
* The server has no `robots.txt`, `sitemap.xml` or `favicon.ico` (404 on probe).

| Source page | Title | Status | Last-Modified | Bytes | SHA-256 (first 12) | Gallery photos | New page |
|---|---|---|---|---|---|---|---|
| aboutus.html | Welcome to sanyoaqm.com.sg - Company Profile | 200 | 10 Jul 2012 | 10195 | `44aed675ba51` | 0 | company.html |
| aquaticplants.html | Welcome to sanyoaqm.com.sg | 200 | 10 Jul 2012 | 8236 | `7458887cf267` | 9 | aquatic-plants.html |
| aquaticplants_2.html | Welcome to sanyoaqm.com.sg - Aquatic Plant | 200 | 10 Jul 2012 | 8247 | `622d393ef06b` | 9 | aquatic-plants.html |
| aquaticplants_3.html | Welcome to sanyoaqm.com.sg - Aquatic Plant | 200 | 10 Jul 2012 | 7997 | `23b72fd01b0f` | 6 | aquatic-plants.html |
| aquaticplants_on_driftwood.html | Welcome to sanyoaqm.com.sg - Aquatic Plant | 200 | 10 Jul 2012 | 7222 | `069532f4115b` | 3 | plants-on-driftwood.html |
| contact.html | Welcome to sanyoaqm.com.sg - Contact Us | 200 | 10 Jul 2012 | 9383 | `64f3dab24813` | 0 | contact.html |
| driftwood.html | Welcome to sanyoaqm.com.sg - Driftwood | 200 | 10 Jul 2012 | 6437 | `06e725043ffa` | 3 | driftwood.html |
| freshwaterfishes.html | Welcome to sanyoaqm.com.sg - Freshwater Fish | 200 | 10 Jul 2012 | 7000 | `2957808fe4c5` | 0 | freshwater-fishes.html |
| freshwaterfishes_cichild.html | Welcome to sanyoaqm.com.sg - Freshwater Fish | 200 | 10 Jul 2012 | 9308 | `6e2c0f8dda35` | 9 | freshwater-cichild.html |
| freshwaterfishes_guppy.html | Welcome to sanyoaqm.com.sg - Freshwater Fish | 200 | 10 Jul 2012 | 9336 | `4642bfe12749` | 12 | freshwater-guppy.html |
| freshwaterfishes_molly.html | Welcome to sanyoaqm.com.sg - Freshwater Fish | 200 | 10 Jul 2012 | 9077 | `a09a2be939a7` | 9 | freshwater-molly.html |
| freshwaterfishes_platy.html | Welcome to sanyoaqm.com.sg - Freshwater Fish | 200 | 10 Jul 2012 | 10118 | `e1d01b3e4c76` | 12 | freshwater-platy.html |
| freshwaterfishes_platy_2.html | Welcome to sanyoaqm.com.sg - Freshwater Fish | 200 | 10 Jul 2012 | 9557 | `b100d5c00e44` | 9 | freshwater-platy.html |
| freshwaterfishes_swordtail.html | Welcome to sanyoaqm.com.sg - Freshwater Fish | 200 | 10 Jul 2012 | 9157 | `aa8628e14a52` | 4 | freshwater-swordtail.html |
| index.html | Welcome to sanyoaqm.com.sg | 200 | 10 Jul 2012 | 6613 | `6a96ef5b9ff0` | 0 | index.html |
| marinefish.html | Welcome to sanyoaqm.com.sg - Marine Fish | 200 | 10 Jul 2012 | 6613 | `dd2bc969a300` | 0 | marine-fishes.html |
| marinefish_more_pictures_1.html | Welcome to sanyoaqm.com.sg - Marine Fish | 200 | 10 Jul 2012 | 7254 | `b6ef4cd88212` | 9 | marine-fishes.html#gallery |
| marinefish_more_pictures_2.html | Welcome to sanyoaqm.com.sg - Marine Fish | 200 | 10 Jul 2012 | 6947 | `9e239f583e8f` | 6 | marine-fishes.html#gallery |
| newfishes.html | Welcome to sanyoaqm.com.sg - New Fish | 200 | 10 Jul 2012 | 9038 | `412c1d48ba28` | 2 | new-fishes.html |

Full columns (capture time, hashes, commented-out image references) are in `PAGE-INVENTORY.csv`.
