# Content-review log

30 entries; **21 need company review** (status `open`). Quotes are verbatim from the original pages and are machine-checked by `tools/verify_content.py`. Source discrepancies are never silently rewritten: they are kept, qualified or withheld as described under *Treatment*. Source: data/review-log.json.

## R01 — Company age claim

* **Severity:** high  ·  **Status:** open
* **Source pages:** aboutus.html
* **Original text / anchor:** “With a history of over 37 years”
* **Issue:** Undated statement. Every source page was last modified on 10 July 2012 and the footer reads “Copyright © 2006”, so the number cannot be assumed to be current.
* **Treatment:** Shown only in the clearly qualified “Historical statements” section of the Company page, attributed to the original website. Not used in the hero or other marketing copy. No current years-in-business figure is calculated or implied.

## R02 — Long-standing customers and destination list (includes Cairo)

* **Severity:** high  ·  **Status:** open
* **Source pages:** aboutus.html
* **Original text / anchor:** “buying from us for over 35 years”
* **Issue:** Undated relationship claim. The same paragraph lists “Cairo” among countries; Cairo is a city, not a country.
* **Treatment:** Quoted as written inside the qualified section. “Cairo” is reproduced exactly and is not relabelled as a country; a footnote states that the list needs company review. Not presented as a current customer list and not used as a shipping-destination promise.

## R03 — OFI / SAFEA membership

* **Severity:** high  ·  **Status:** open
* **Source pages:** aboutus.html, index.html
* **Original text / anchor:** “We are also a member of the”
* **Issue:** Membership statement and logos are from the legacy site; current membership has not been verified with either organisation.
* **Treatment:** Statement and logos appear only in the qualified section of the Company page, labelled “not verified as current”. Logos are not used in the header or footer.

## R04 — AVA / Accredited Ornamental Fish Exported Scheme

* **Severity:** high  ·  **Status:** open
* **Source pages:** aboutus.html
* **Original text / anchor:** “Accredited Ornamental Fish Exported Scheme”
* **Issue:** Scheme name appears as written (“Exported”). Agency names and schemes may have changed since the page was written; no certificate or number is given.
* **Treatment:** Quoted inside the qualified section only; not shown as a current certification or accreditation badge. Company to confirm the current scheme, issuing body and certificate details before any certification claim is made.

## R05 — Quarantine duration and holding-tank count

* **Severity:** medium  ·  **Status:** open
* **Source pages:** aboutus.html
* **Original text / anchor:** “There are over 600 holding tanks in our quarantine house”
* **Issue:** Operational figures (2 weeks, over 600 tanks) are undated and may be out of date.
* **Treatment:** Shown as a company statement from the original website inside the qualified quality section; the home page repeats only the general process, attributed, without numbers.

## R06 — 24-hour customer support

* **Severity:** medium  ·  **Status:** open
* **Source pages:** aboutus.html
* **Original text / anchor:** “24-hrs customer support”
* **Issue:** Support promise from the legacy site; no operating hours or response times are published anywhere.
* **Treatment:** Listed only as a historical company statement. The rebuild adds no response-time promise, operating hours or sales-notification claim.

## R07 — Platy breeding temperature (unit error)

* **Severity:** high  ·  **Status:** open
* **Source pages:** freshwaterfishes_platy.html, freshwaterfishes_platy_2.html
* **Original text / anchor:** “do best at about 74 Degree Celsius”
* **Issue:** The text gives a breeding range of “65 to 90” and an optimum of “74 Degree Celsius”. 74 °C would kill the fish, so the unit is apparently wrong (the numbers look like Fahrenheit), but the correct unit is not confirmed. Page 2 repeats the paragraph with a different misspelling (“Celcious”).
* **Treatment:** The breeding paragraph is withheld from the catalogue pages; only the first descriptive sentence is shown. The verbatim original is kept in data/source-record.json and quoted, flagged, on the Content notes page. Nothing is silently corrected and no replacement figure is published.

## R08 — Swordtail scientific name spelling

* **Severity:** medium  ·  **Status:** open
* **Source pages:** freshwaterfishes_swordtail.html
* **Original text / anchor:** “XIPHOPHORUS HELERI”
* **Issue:** Source spelling “heleri”; the usual spelling is Xiphophorus hellerii.
* **Treatment:** Source spelling is displayed (readable casing, letters unchanged) and searchable. The proposed spelling is shown separately as “proposed, not confirmed” and is a hidden search alias.

## R09 — “Cichild” spelling

* **Severity:** low  ·  **Status:** open
* **Source pages:** freshwaterfishes.html, freshwaterfishes_cichild.html
* **Original text / anchor:** “CICHILD”
* **Issue:** Category is spelled “Cichild” on the source (usual spelling: Cichlid).
* **Treatment:** Label “Cichild” retained; “Cichlid” shown as a proposed correction and searchable. The Cichild album carries no scientific name or care text on the source, and none is added.

## R10 — PUNTIUS DENISONI spelling / taxonomy

* **Severity:** medium  ·  **Status:** open
* **Source pages:** newfishes.html
* **Original text / anchor:** “PUNTIUS DENISONI”
* **Issue:** Source spelling “denisoni”; the usual spelling is “denisonii” and the genus may have been revised since.
* **Treatment:** Source spelling shown; proposed spelling listed as unverified and searchable. No taxonomy update is asserted.

## R11 — BOTIA KUBOTIA spelling

* **Severity:** low  ·  **Status:** open
* **Source pages:** newfishes.html
* **Original text / anchor:** “BOTIA KUBOTIA”
* **Issue:** Source spelling “kubotia”; the usual spelling is “kubotai”.
* **Treatment:** Source spelling shown; proposed spelling listed as unverified and searchable.

## R12 — “New Fishes” page has no date

* **Severity:** high  ·  **Status:** open
* **Source pages:** newfishes.html
* **Original text / anchor:** “Name: PUNTIUS DENISONI”
* **Issue:** The page establishes no arrival date, so its two entries cannot be advertised as new this week or in stock. The page also contains HTML-comment text “Puntius Denisoni or Red Torpedo Barb” (not published by the source) and a label typo (“Desciption”).
* **Treatment:** Page renamed “New Fishes (source page)” with an explicit notice: no date, no availability statement. The commented-out common name is recorded here only and is not used. The label typo “Desciption” is rendered “Description”; all other text is verbatim.

## R13 — Unlabelled gallery photos

* **Severity:** high  ·  **Status:** handled
* **Source pages:** marinefish.html, freshwaterfishes_cichild.html, marinefish_more_pictures_1.html, marinefish_more_pictures_2.html, aquaticplants.html, aquaticplants_2.html, aquaticplants_3.html, aquaticplants_on_driftwood.html, driftwood.html
* **Original text / anchor:** “Show Pictures”
* **Issue:** Most gallery photos carry no individual name, category or species. Marine and plant galleries list categories separately and never say which photo belongs to which category.
* **Treatment:** Each photo is identified only by its source album and original file identifier (for example “Marine fishes · photo 05”, source file 05.jpg). No species or category is inferred from the picture.

## R14 — Possible mismatch inside the Molly album (visual observation)

* **Severity:** medium  ·  **Status:** open
* **Source pages:** freshwaterfishes_molly.html
* **Original text / anchor:** “POECILIA LATIPINNA”
* **Issue:** Photo molly/126.jpg looks, to a layperson, like a different kind of fish from the other Molly photos. This is a visual impression only and is not confirmed.
* **Treatment:** Photo retained in the Molly album exactly as on the source. Company to confirm album placement.

## R15 — Commented-out legacy content on source pages

* **Severity:** low  ·  **Status:** handled
* **Source pages:** freshwaterfishes_swordtail.html, freshwaterfishes_cichild.html
* **Original text / anchor:** “XIPHOPHORUS HELERI”
* **Issue:** The Swordtail page's markup contains commented-out references to five Molly photos (molly/136, 141, 142, 110, 130); the Cichild page's markup contains a commented-out copy of the Molly description. These are not visible on the live pages.
* **Treatment:** Ignored for the catalogue (they are already in the Molly album on the source); recorded in source-audit/page-inventory.json and data/source-record.json (commented_out_*).

## R16 — Contact details check

* **Severity:** medium  ·  **Status:** handled
* **Source pages:** contact.html
* **Original text / anchor:** “3 Chencharu Link”
* **Issue:** Live values captured on 2026-10-02 are identical to the prior audit: Sanyo Aquarium (Pte) Ltd, 3 Chencharu Link, Singapore 768144; Tel +65 6481 3111; Fax +65 6481 6333 and +65 6481 6688; sales@sanyoaqm.com.sg and info@sanyoaqm.com.sg. The second number sits under the “Fax” label without its own label.
* **Treatment:** Live values used unchanged. Both numbers shown as fax numbers, as the layout implies. Telephone and email are real tel:/mailto: links; fax numbers are not linked. Company should confirm that the second number is a fax line.

## R17 — Original contact form posts to sendMail.php

* **Severity:** medium  ·  **Status:** handled
* **Source pages:** contact.html
* **Original text / anchor:** “Or send us an email”
* **Issue:** The original form submits to sendMail.php on the original server. No authorised backend or email service is configured for the rebuild.
* **Treatment:** The original form is not reproduced and nothing is posted to the original server. The rebuild offers an email draft (mailto) and downloadable/copyable enquiry text, and says plainly that the visitor must send the draft.

## R18 — Marine page: scope and typo

* **Severity:** medium  ·  **Status:** open
* **Source pages:** marinefish.html
* **Original text / anchor:** “Sanyo Aquarium provides an extensive assortment of health marine fishes.”
* **Issue:** Typo (“health”). The company profile mentions marine “invertebrates”, but the marine page lists no invertebrate category and shows no invertebrate-labelled photo.
* **Treatment:** The typo is not copied into display text, which says “a wide assortment of marine fishes” (the word “healthy” is deliberately not asserted). Invertebrates are mentioned only where the source mentions them (Company page, Freshwater list: Shrimps, Snails). No invertebrate photos are labelled.

## R19 — Freshwater category list oddities

* **Severity:** low  ·  **Status:** handled
* **Source pages:** freshwaterfishes.html
* **Original text / anchor:** “Snails”
* **Issue:** The list contains both “Snails” and “Snail”, plus “other”, and lists “Angel” without an album.
* **Treatment:** All 24 entries kept exactly as listed (no merging, no corrections); each can be added to an enquiry as a category-level request.

## R20 — Source freshness

* **Severity:** high  ·  **Status:** handled
* **Source pages:** index.html
* **Original text / anchor:** “Copyright © 2006 sanyoaqm.com.sg”
* **Issue:** All 19 pages report Last-Modified 10 July 2012; the footer says 2006. Prices, stock, dates and availability are not published anywhere.
* **Treatment:** The whole source is treated as historical reference. The rebuild publishes no prices, stock, SKUs, minimum orders, arrival dates, shipping-destination promises, certifications or testimonials.

## R21 — Low image resolution

* **Severity:** medium  ·  **Status:** open
* **Source pages:** (all gallery pages)
* **Original text / anchor:** “Sanyo Aquarium carries a wide variety”
* **Issue:** All gallery images are small thumbnails (about 165×110 px; marine 154 px wide; plants 87×130 for four portraits). Enlargement cannot add detail.
* **Treatment:** Images are shown with object-fit: contain and are never cropped; the enlarge view caps scaling and says so. Company should supply higher-resolution originals for a production catalogue.

## R22 — Legacy decorative assets not migrated

* **Severity:** low  ·  **Status:** handled
* **Source pages:** index.html, (all pages)
* **Original text / anchor:** “Powered By”
* **Issue:** Banner graphics with baked-in titles, spacer GIFs, arch/top/bottom bars, the four home-page tiles and dot.gif (404 on the server) are layout fragments, not product photographs.
* **Treatment:** Classified as decorative/legacy in docs/ASSET-INVENTORY.csv and not used. The “Powered By e-contech” credit belongs to the legacy site build and is not carried over.

## R23 — Unreferenced homepage meta keywords

* **Severity:** low  ·  **Status:** open
* **Source pages:** index.html
* **Original text / anchor:** “glass fish,loach,eel,catfish,fighting fish,rasbora,pacu,stingray,frog,rainbow fish,invertebrate,arowana”
* **Issue:** The home page keyword list names animals (for example rasbora, pacu, stingray, frog, arowana) that appear nowhere in the visible catalogue.
* **Treatment:** Treated as legacy SEO keywords, not as product coverage. Not added to the catalogue or search.

## R24 — Superlative and marketing claims

* **Severity:** medium  ·  **Status:** open
* **Source pages:** aboutus.html
* **Original text / anchor:** “Sanyo Aquarium is one of Singapore's leading exporter”
* **Issue:** “Leading exporter”, “top quality”, “competitive pricing and freight costs”, “availability of new and high-demand species” are self-descriptions with no evidence on the page.
* **Treatment:** Not used in hero copy. Reproduced only as attributed company statements on the Company page.

## R25 — Sourcing statement

* **Severity:** medium  ·  **Status:** open
* **Source pages:** aboutus.html
* **Original text / anchor:** “Export of imported fishes from Indonesia, Malaysia, Thailand etc.”
* **Issue:** Sourcing countries are undated and open-ended (“etc.”).
* **Treatment:** Reproduced as written under company statements; not extended or turned into a supplier list.

## R26 — Care information (pH / temperature)

* **Severity:** low  ·  **Status:** open
* **Source pages:** freshwaterfishes_guppy.html, freshwaterfishes_molly.html, freshwaterfishes_swordtail.html, newfishes.html
* **Original text / anchor:** “pH: 7.3; Temperature: 27 Degree Celsius;”
* **Issue:** Care values are carried over without independent verification.
* **Treatment:** Shown with a label “as published on the original website”; “Degree Celsius” is displayed as °C (same meaning). No additional husbandry advice is written.

## R27 — Watermarks retained

* **Severity:** low  ·  **Status:** handled
* **Source pages:** (all gallery pages)
* **Original text / anchor:** “www.sanyoaqm.com.sg”
* **Issue:** Gallery and facility photos carry a “sanyoaqm” / website watermark.
* **Treatment:** Originals are used as they are; watermarks are not removed or cropped. Files were only re-encoded to WebP (quality 90) for delivery; unmodified originals ship in source-audit/originals/.

## R28 — Plant supply forms wording

* **Severity:** low  ·  **Status:** open
* **Source pages:** aquaticplants.html
* **Original text / anchor:** “sold in loose plants, lead bunch and potted plants and plants on driftwood”
* **Issue:** “lead bunch” is ambiguous (possibly a lead-weighted bunch) and no quantities or sizes are given.
* **Treatment:** The four supply forms are offered, with the source wording, as a selector on plant enquiry lines. No sizes, packs or prices are added.

## R29 — Driftwood shipment information

* **Severity:** low  ·  **Status:** open
* **Source pages:** driftwood.html
* **Original text / anchor:** “Driftwoods are packed in 20 footer container and sent by sea”
* **Issue:** Shipment method statement only; no destinations, lead times, container terms or minimum quantities are given.
* **Treatment:** Reproduced as written (“20 footer container” kept) under Shipment information, without extra promises.

## R30 — AI-generated illustration variants

* **Severity:** low  ·  **Status:** handled
* **Source pages:** (catalogue image cards, home and category thumbnails, lightboxes, company/contact images and enquiry lines)
* **Original text / anchor:** “AI illustration”
* **Issue:** Illustrative variants could be mistaken for factual photographs of the company's stock if their status or provenance is unclear.
* **Treatment:** All 102 catalogue photos have separate accepted AI illustration variants. After the user asked for the building and holding-tank images to be regenerated as well, seven building/facility photos also received separate AI illustration variants. The catalogue run records 161 generation attempts: 102 accepted photo records and 59 rejected retries; the seven company/facility variants are accepted. Codex CLI Imagen was unavailable, so the user-requested built-in image_gen.imagegen tool generated the variants; it reported no model name or version. AI files are stored separately from original source images and delivered original WebPs. Short visible AI illustration badges, AI-specific alt text and concise enquiry labels identify the variants; a site-wide note says they are visual aids, not photos of actual stock or company premises. Generic exterior artwork does not depict Sanyo Aquarium's premises. The AI variants are the display default; switching to original or both mode preserves access to factual photographs. Company and association logos remain original.

