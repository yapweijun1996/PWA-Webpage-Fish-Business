# QA report - AI illustration variants

Date: 2026-10-02. The configured `site.image_mode` is `ai-illustration`. Generated artwork is visibly identified as illustration; original source photographs and delivered original WebP files remain preserved.

## Image generation and provenance

- `codex --version` returned `codex-cli 0.160.0`. `codex help imagegen` failed with `error: unrecognized subcommand 'imagegen'`; Imagen was not available through Codex CLI, and no Imagen generation is claimed.
- The built-in `image_gen.imagegen` tool generated 102 accepted catalogue variants and seven separate company/facility illustrations: 109 final variants total. The tool reported no model name or version, so neither is claimed.
- Catalogue manifest: 102 records, all `done`; 161 generation attempts, 102 accepted outputs and 59 rejected attempts. Four catalogue records had four or five attempts after the subsequent request to keep regenerating; the attempt histories preserve each decision. Company/facility manifest: seven records, all `done`. No final image records are failed.
- Catalogue WebPs are under `generated/imagen/<album>/<fileid>.webp`; company/facility WebPs are under `generated/imagen/company/`. Files are separate from `source-audit/originals/` and delivered original assets. Catalogue output uses 2x source dimensions and WebP quality 90; company/facility output uses 2x dimensions and quality 90. The manifests record prompts, source and output hashes, sizes, timestamps, statuses and reported tool metadata.
- Company building/facility illustrations are generic visual aids, not depictions of Sanyo Aquarium's actual premises. Logos remain original. The compact visible badge says "AI illustration"; image alt text identifies generated artwork, and enquiry items state "not evidence of stock".

## Build and static checks

| Check | Result |
|---|---|
| `python tools/build_site.py` | PASS; 18 pages, 102 catalogue photos, 221 image records; 2.57 MB site output |
| `python tools/qa_static.py` | PASS, 13/13 |
| `python tools/verify_content.py` | PASS, 46/46; checks original preservation, AI labels and alt text, company photo protection, mode behavior and source content |
| `python tools/build_docs.py` | PASS; review log and inventories generated, including R30 |

## Browser checks

Chromium was run against the generated site at 320, 390, 768 and 1440 CSS pixels. Home, Company and Guppy gallery pages were checked at all four widths. They had no horizontal overflow, broken images or interactive buttons/form controls below 44px. No console errors, page errors, failed requests or HTTP errors were observed.

In `both` mode, browser interactions verified original/AI switching for a homepage thumbnail and a company/facility image, AI switching for a gallery card, and original/AI switching in the lightbox. Each AI state showed the concise badge and generated-image alt text. The generic company illustration caption remained accurate; returning to the original restored its source alt text. In the configured `ai-illustration` mode, adding a catalogue photo to the enquiry list preserved the generated image, AI alt text, visible AI label and "not evidence of stock" wording.

Screenshots from this pass are in `docs/screenshots/ai/both-mode-home-320.png`, `both-mode-company-768.png`, `both-mode-lightbox-1440.png` and `ai-variant-enquiry-1440.png`. Additional viewport screenshots are in the same directory.

## Package and extracted-copy checks

The project ZIP is rebuilt by `python tools/package_zip.py`; the older `Sanyo-Aquarium-Modern-Website.zip` is preserved and both ZIPs are ignored by Git. The final `Sanyo-Aquarium-Modern-Website-AI.zip` archive passed integrity verification. It was extracted into a fresh directory; from the extracted copy, `python tools/build_site.py`, `python tools/qa_static.py`, `python tools/verify_content.py` and `python tools/build_docs.py` passed. The extracted site was checked in Chromium at 320 and 1440 CSS pixels for generated thumbnails, AI disclosure, original company imagery, no overflow, no broken images and no browser errors.

## Not tested / limitations

- Imagen was not available in Codex CLI; the built-in image-generation tool did not report a model or version.
- Firefox, Safari, assistive technologies and physical phones/tablets were not tested.
- The live Sanyo Aquarium site was not changed, visited for deployment, or used as a target.
- The artwork does not establish actual stock, availability, species identity beyond the published album context, or the appearance of Sanyo Aquarium's premises.
