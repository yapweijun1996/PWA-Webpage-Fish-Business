# Sanyo Aquarium — modern catalogue website (rebuild)

A static, responsive B2B catalogue and enquiry website rebuilt from the content of
<https://www.sanyoaqm.com.sg/index.html>. Plain HTML, CSS and JavaScript — no framework, no runtime dependencies, no
external requests. The site is generated from structured data so it can be edited and rebuilt.

**Status: review preview.** Completed: source audit, design, build, automated and browser QA (Chromium).
Not done / not configured: email delivery backend, public hosting, company confirmation of the flagged content
(see [What is not done](#what-is-not-done)).

---

## 1. Quick start (view the finished site)

Prerequisite: any web browser and either Python 3 or any other static file server. Nothing needs installing.

```bash
# from the folder that contains this README
python tools/serve.py 8080          # serves ./site on http://127.0.0.1:8080/  (no-cache headers)
# alternative, same result:
python -m http.server 8080 --directory site
```

Open <http://127.0.0.1:8080/>. (The pages also work when opened straight from disk, but use a server for realistic testing.)

On Windows use `py` instead of `python` if `python` is not on your PATH.

## 2. Rebuild / verify

Prerequisites for rebuilding: Python 3.9+ and `pip install pillow beautifulsoup4 lxml requests`
(`requests` is only needed to re-crawl the original site).

```bash
python tools/build_site.py      # regenerates ./site from data/, src/ and source-audit/originals/ (WebP conversion included)
python tools/qa_static.py       # static QA: links, assets, headings, titles, labels, JSON-LD, tel/mailto  -> docs/qa/static-checks.json
python tools/verify_content.py  # compares the built site with the audited source record      -> docs/qa/content-fidelity.json
python tools/build_docs.py      # regenerates the inventories, review log and source-mapping documents in docs/
```

Optional — repeat the audit against the live original site (network access; this **overwrites** `source-audit/`):

```bash
python tools/crawl_source.py    # GET-only crawl of every same-domain page; saves raw HTML + originals + SHA-256
python tools/extract_source.py  # rebuilds data/source-record.json from the raw HTML (no network)
python tools/build_site.py && python tools/build_docs.py
```

## 3. What is in this package

| Path | Purpose |
|---|---|
| `site/` | **Ready-to-serve website** (18 HTML pages, CSS, JS, WebP images, logo). Upload this folder to a static host. |
| `src/css`, `src/js` | Hand-written stylesheet and scripts (copied into `site/assets/` by the build). |
| `data/source-record.json` | Verbatim text blocks and every gallery image with its source URL, classified (company information, contact details, product categories, named products, gallery images, care information, supply forms, shipment information, historical claims). |
| `data/editorial.json` | Display labels, search aliases, **proposed (unverified) taxonomy corrections**, publication decisions, site config (`site_url`, `noindex`). |
| `data/review-log.json` | The content-review log (also rendered to `docs/CONTENT-REVIEW-LOG.md` and the site's *Content notes* page). |
| `data/url-map.json`, `data/image-manifest.json` | Old URL → new page map; original ↔ delivered image checksums. |
| `source-audit/` | **Untouched audit evidence**: `raw-html/` (19 pages), `originals/` (every downloaded image and the CSS, original files with watermarks), `page-inventory.json`, `asset-inventory.json`. |
| `tools/` | Crawler, extractor, site generator (`sitegen/`), QA scripts, tiny server. |
| `docs/` | Page and asset inventories (with capture dates), source mapping, content-review log, QA report, `screenshots/`, optional-backend notes. |

## 4. Static deployment

1. Copy the contents of `site/` to any static host (Netlify, GitHub Pages, Cloudflare Pages, S3 + CDN, Apache, Nginx). No server code is required.
2. Serve over HTTPS (the “Copy text” button uses the browser clipboard API, which needs a secure context).
3. Use `404.html` as the host's not-found page. Ensure `.webp` is served as `image/webp` (all current hosts do this).
4. **Before a public launch** edit `data/editorial.json`:
   * `"site_url": "https://your-domain.example"` — turns on canonical tags and `sitemap.xml` (nothing is generated while it is empty, so no URL is invented);
   * `"noindex": false` — the preview ships with `noindex` and `Disallow: /` so it cannot be indexed by accident;
   then run `python tools/build_site.py` again. With `noindex` off, Lighthouse SEO is 100 (verified on the home page); with it on it is 66 for that single reason.
5. Optional redirects from the old URLs are listed in `docs/SOURCE-MAPPING.md` (Apache and Netlify snippets). They are documentation only.

This package does not modify the original website, DNS or hosting.

## 5. Editing guide

| To change… | Edit | Then |
|---|---|---|
| Page wording (home, company, contact, notices) | `tools/sitegen/pages.py` | `python tools/build_site.py` |
| Header, footer, navigation | `tools/sitegen/layout.py` | build |
| Album labels, search aliases, proposed spellings, withheld text, site config | `data/editorial.json` | build |
| Review-log entries (and the public *Content notes* page) | `data/review-log.json` | build + `build_docs.py` |
| Colours, spacing, layout | `src/css/styles.css` (design tokens at the top) | build |
| Search, lightbox, enquiry behaviour | `src/js/*.js` | build |
| Add or replace a gallery photo | put the original in `source-audit/originals/images/<folder>/`, add it to the source record (or re-run the extractor against a corrected source) | build + verify |
| Contact details | `data/source-record.json` → `contact` (they come from the original page; update them there once the company confirms new values) | build + verify |

Always run `python tools/verify_content.py` after content edits: it fails if a published value drifts from the audited source,
if a withheld/flagged text leaks into a public page, or if a photo/album association changes.

## 6. How the enquiry workflow behaves (honest by design)

* Add any photo or listed category to the **enquiry list** (stored in this browser's `localStorage` only). Duplicates are never added twice; a toast says so.
* Each line has a quantity (whole number 1–99,999), variety/size notes and — for plants — the supply forms listed on the original site.
* Contact and destination details are kept in `sessionStorage` (this tab only; cleared when the tab closes) so they survive navigation but are **not persisted by default**.
* The review step offers **Open email draft** (a `mailto:` to `sales@sanyoaqm.com.sg`), **Copy text**, **Download .txt / .csv** and **Print**.
* **Nothing is transmitted.** The site never says an enquiry was “sent”, never shows a server reference and makes no claim that the sales team was notified. Long lists are truncated in the email link and the full text is copied to the clipboard (and offered as a download).
* There is no backend, payment, live inventory, ERP integration, login or CMS, and no fake versions of them. See `docs/OPTIONAL-BACKEND.md` for what a real submission service would need.

## 7. Content fidelity, in one paragraph

Company details, categories, named products, care values and image-to-album associations come from the original pages and are machine-checked against them (`tools/verify_content.py`). Old claims (years in business, long-standing customers, OFI/SAFEA membership, AVA scheme, 600 tanks, 24-hour support) appear only in a clearly qualified section of the Company page. The platy breeding paragraph (which says “74 Degree Celsius”) is withheld and quoted only, flagged, on the *Content notes* page. Source spellings (“Cichild”, “XIPHOPHORUS HELERI”, “PUNTIUS DENISONI”, “BOTIA KUBOTIA”) are kept; proposed corrections are labelled as unverified. The *New Fishes* page is shown as an undated source page, not as current stock. Unlabelled photos keep their source album and file name — no species names are invented. Full detail: `docs/CONTENT-REVIEW-LOG.md`.

## 8. Images

* The checked-in default is `"image_mode": "ai-illustration"` in `data/editorial.json`: the 102 catalogue photos and seven building/facility photos display separate AI illustration variants. Set it to `"original"` to show the source photographs or `"both"` to show originals with toggles for their illustrations. This applies to gallery cards, search results, homepage and category thumbnails, lightboxes, and company/contact photos; then run `python tools/build_site.py`.
* All original gallery and company photographs remain intact in `source-audit/originals/`; delivered original WebPs remain separate and unchanged. Original watermarks are preserved, and image frames use `object-fit: contain` without cropping. Logos and association marks remain original files.
* The 102 catalogue illustrations are stored as WebP files under `generated/imagen/<album>/<fileid>.webp`. The seven building/facility illustrations are stored under `generated/imagen/company/<fileid>.webp`. The build copies them to `site/assets/img/generated/`. `tools/ai_images/manifest.json` records the catalogue sources and attempts; `tools/ai_images/company-manifest.json` records all seven company/facility variants, prompts, hashes, dimensions, times, and reported tool metadata. The catalogue run accepted all 102 photo records and recorded 59 rejected retry attempts; the seven company/facility variants are accepted.
* Cards show the short **AI illustration** badge. Alt text identifies generated illustrations; enquiry lines identify AI variants, and the footer explains that illustrations are not photos of actual stock or company premises. The building artwork is generic and does not depict Sanyo Aquarium's premises. Catalogue titles and source scientific names are not generated or changed.
* Codex CLI Imagen was unavailable (`codex help imagegen` returned `error: unrecognized subcommand 'imagegen'`). As you requested, the built-in `image_gen.imagegen` tool generated the variants. It did not report a model name or version; neither is claimed. See [AI image tool status](docs/AI-IMAGE-BLOCKED.md) and review-log entry R30.
* The generated-variant package is `Sanyo-Aquarium-Modern-Website-AI.zip`; the earlier `Sanyo-Aquarium-Modern-Website.zip` is kept separately.

## 9. What is not done

* **Email/form delivery** is not configured (no authorised backend or email service was supplied). Enquiries leave the browser only when the visitor sends the email draft themselves.
* **Public hosting** is not set up and no live URL exists.
* **Company confirmation** of the flagged claims and spellings is outstanding (21 of the 30 review-log entries are marked *open*).
* **Browser coverage**: tested in Chromium (Chrome DevTools) only; Firefox and Safari were not run. The `mailto:` hand-off to a real mail client was not exercised (automation cannot launch one).
* Photos have short, neutral alt text (album + file number), not visual descriptions.
* Photographs and logos belong to the company; this package grants no licence. Confirm usage rights before publishing.
