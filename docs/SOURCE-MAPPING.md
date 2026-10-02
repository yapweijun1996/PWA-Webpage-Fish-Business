# Source mapping

## Old URL → new page

| Original URL | New page | Note |
|---|---|---|
| https://www.sanyoaqm.com.sg/index.html | `index.html` | Home; the four legacy banner tiles are not migrated (see review log R22). |
| https://www.sanyoaqm.com.sg/aboutus.html | `company.html` | Company profile; historical claims moved into a qualified section. |
| https://www.sanyoaqm.com.sg/freshwaterfishes.html | `freshwater-fishes.html` | Category overview; the 24 listed categories are kept in source order. |
| https://www.sanyoaqm.com.sg/freshwaterfishes_platy.html | `freshwater-platy.html` | Original page 1 of the Platy gallery. |
| https://www.sanyoaqm.com.sg/freshwaterfishes_platy_2.html | `freshwater-platy.html` | Original page 2 of the Platy gallery (combined). |
| https://www.sanyoaqm.com.sg/freshwaterfishes_molly.html | `freshwater-molly.html` |  |
| https://www.sanyoaqm.com.sg/freshwaterfishes_guppy.html | `freshwater-guppy.html` |  |
| https://www.sanyoaqm.com.sg/freshwaterfishes_swordtail.html | `freshwater-swordtail.html` |  |
| https://www.sanyoaqm.com.sg/freshwaterfishes_cichild.html | `freshwater-cichild.html` | Source spelling 'Cichild' retained. |
| https://www.sanyoaqm.com.sg/marinefish.html | `marine-fishes.html` | Marine category list (22 entries). |
| https://www.sanyoaqm.com.sg/marinefish_more_pictures_1.html | `marine-fishes.html#gallery` | Marine photo gallery, original page 1 (combined). |
| https://www.sanyoaqm.com.sg/marinefish_more_pictures_2.html | `marine-fishes.html#gallery` | Marine photo gallery, original page 2 (combined). |
| https://www.sanyoaqm.com.sg/aquaticplants.html | `aquatic-plants.html` | Aquatic plants gallery, original page 1 of 3 (combined). |
| https://www.sanyoaqm.com.sg/aquaticplants_2.html | `aquatic-plants.html` | Original page 2 of 3 (combined). |
| https://www.sanyoaqm.com.sg/aquaticplants_3.html | `aquatic-plants.html` | Original page 3 of 3 (combined). |
| https://www.sanyoaqm.com.sg/aquaticplants_on_driftwood.html | `plants-on-driftwood.html` | Distinct source gallery retained. |
| https://www.sanyoaqm.com.sg/newfishes.html | `new-fishes.html` | Renamed 'New Fishes (source page)'; undated, not a stock statement. |
| https://www.sanyoaqm.com.sg/driftwood.html | `driftwood.html` |  |
| https://www.sanyoaqm.com.sg/contact.html | `contact.html` | Contact details; the source form (sendMail.php) is replaced by the enquiry workflow at enquiry.html. |

New pages with no original equivalent:

* `catalogue.html` — New: search and filters across every photo and category.
* `enquiry.html` — New: enquiry list, details, review and email-draft/export (no server submission).
* `content-notes.html` — New: review hand-over notes.
* `404.html` — New: not-found page for static hosts.

## New page → structured source records

Every factual statement and gallery image is stored with its source URL in `data/source-record.json` (classes: company_information, contact_details, product_category, named_product, gallery_image, care_information, supply_form, shipment_information, historical_claim). Display wording lives in `tools/sitegen/pages.py`; display labels, aliases and proposed corrections live in `data/editorial.json`.

| New page | Source block ids | Notes |
|---|---|---|
| `index.html` | `home.*` | Hero/section copy is new, source-supported wording; the quality bullets summarise about.quality_process.*; no numbers are used. |
| `company.html` | `about.*` | about.intro (split into three sentences), about.customers, about.qualities.intro, about.quality_process.1-6, about.services.1-3, about.assurance.1-4; about_orgs; images company_photo, about_us1-5, aboutus_member. |
| `freshwater-fishes.html` | `freshwater.*` | freshwater.intro, freshwater.category.1-24 (+ links to the five albums). |
| `freshwater-platy.html` | `freshwater-platy.*` | p1/p2 heading, care; description withheld (R07); 21 photos. |
| `freshwater-molly.html` | `freshwater-molly.*` | heading, care, description; 9 photos. |
| `freshwater-guppy.html` | `freshwater-guppy.*` | heading, care, description; 12 photos. |
| `freshwater-swordtail.html` | `freshwater-swordtail.*` | heading, care, description; 4 photos. |
| `freshwater-cichild.html` | `freshwater-cichild.*` | heading only (CICHILD); 9 photos. |
| `marine-fishes.html` | `marine.*` | marine.intro (reworded, R18), marine.category.1-22; 15 photos from the two gallery pages. |
| `aquatic-plants.html` | `plants.intro` | supply forms from plants.intro; 24 photos from three gallery pages. |
| `plants-on-driftwood.html` | `plants.intro` | 3 photos (distinct source gallery). |
| `new-fishes.html` | `newfishes.*` | two entries: name, pH, temperature, description (verbatim except the label typo 'Desciption'). |
| `driftwood.html` | `driftwood.intro` | shipment information quoted verbatim; 3 photos. |
| `contact.html` | `contact.*` | contact.address_block values; photo sanyo.jpg; form replaced by enquiry workflow (R17). |

## Redirect snippets (optional, for a future deployment)

Apache `.htaccess`:

```apache
Redirect 301 /aboutus.html /company.html
Redirect 301 /freshwaterfishes.html /freshwater-fishes.html
Redirect 301 /freshwaterfishes_platy.html /freshwater-platy.html
Redirect 301 /freshwaterfishes_platy_2.html /freshwater-platy.html
Redirect 301 /freshwaterfishes_molly.html /freshwater-molly.html
Redirect 301 /freshwaterfishes_guppy.html /freshwater-guppy.html
Redirect 301 /freshwaterfishes_swordtail.html /freshwater-swordtail.html
Redirect 301 /freshwaterfishes_cichild.html /freshwater-cichild.html
Redirect 301 /marinefish.html /marine-fishes.html
Redirect 301 /marinefish_more_pictures_1.html /marine-fishes.html
Redirect 301 /marinefish_more_pictures_2.html /marine-fishes.html
Redirect 301 /aquaticplants.html /aquatic-plants.html
Redirect 301 /aquaticplants_2.html /aquatic-plants.html
Redirect 301 /aquaticplants_3.html /aquatic-plants.html
Redirect 301 /aquaticplants_on_driftwood.html /plants-on-driftwood.html
Redirect 301 /newfishes.html /new-fishes.html
```

Netlify `_redirects`:

```
/aboutus.html  /company.html  301
/freshwaterfishes.html  /freshwater-fishes.html  301
/freshwaterfishes_platy.html  /freshwater-platy.html  301
/freshwaterfishes_platy_2.html  /freshwater-platy.html  301
/freshwaterfishes_molly.html  /freshwater-molly.html  301
/freshwaterfishes_guppy.html  /freshwater-guppy.html  301
/freshwaterfishes_swordtail.html  /freshwater-swordtail.html  301
/freshwaterfishes_cichild.html  /freshwater-cichild.html  301
/marinefish.html  /marine-fishes.html  301
/marinefish_more_pictures_1.html  /marine-fishes.html  301
/marinefish_more_pictures_2.html  /marine-fishes.html  301
/aquaticplants.html  /aquatic-plants.html  301
/aquaticplants_2.html  /aquatic-plants.html  301
/aquaticplants_3.html  /aquatic-plants.html  301
/aquaticplants_on_driftwood.html  /plants-on-driftwood.html  301
/newfishes.html  /new-fishes.html  301
```

These are documentation only; nothing here touches the original company website, DNS or hosting.
