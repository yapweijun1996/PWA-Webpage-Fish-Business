"""Page builders. Prose lives here; facts come from data/*.json (see tools/sitegen/data.py)."""
import re

from .layout import esc, page, tel_href, json_ld, SOURCE_URL

AI_LABEL = "AI illustration"


# ------------------------------------------------------------------ components
def breadcrumb(trail):
    out = []
    for i, (label, href) in enumerate(trail):
        if href and i < len(trail) - 1:
            out.append(f'<li><a href="{href}">{esc(label)}</a></li>')
        else:
            out.append(f'<li aria-current="page">{esc(label)}</li>')
    return '<nav class="breadcrumb" aria-label="Breadcrumb"><ol>' + "".join(out) + "</ol></nav>"


def page_header(trail, title, lead=None, sci=None):
    sci_html = f'<p class="sci-line"><i>{esc(sci)}</i></p>' if sci else ""
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    return f"""<section class="page-header">
  <div class="container">
    {breadcrumb(trail)}
    <h1>{esc(title)}</h1>
    {sci_html}{lead_html}
  </div>
</section>"""


def pill(text, kind="hist"):
    return f'<span class="pill pill-{kind}">{esc(text)}</span>'


def notice(html_inner, kind="info", title=None):
    t = f"<strong>{esc(title)}</strong> " if title else ""
    return f'<div class="notice notice-{kind}" role="note"><p>{t}{html_inner}</p></div>'


def ext_link(url, text):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{text}<span class="visually-hidden"> (opens in a new tab)</span> &#8599;</a>'


def company_figure(model, photo, original_caption, figure_class="photo-frame", style="", loading="lazy", frame_class="company-image-frame"):
    ai_available = bool(photo.get("ai_asset"))
    use_ai = ai_available and model["image_mode"] == "ai-illustration"
    variant = "ai-illustration" if use_ai else "original"
    image_src = photo["ai_asset"] if use_ai else photo["original_asset"]
    image_alt = photo["ai_alt"] if use_ai else photo["alt"]
    ai_caption = photo.get("ai_caption", AI_LABEL)
    active_caption = ai_caption if use_ai else original_caption
    style_attr = f' style="{esc(style)}"' if style else ""
    badge = f'<span class="ai-label company-ai-label" data-ai-label{"" if use_ai else " hidden"}>{AI_LABEL}</span>' if ai_available else ""
    image_attrs = ""
    if ai_available:
        image_attrs = (
            f' data-original-src="{esc(photo["original_asset"])}" data-original-alt="{esc(photo["alt"])}"'
            f' data-ai-src="{esc(photo["ai_asset"])}" data-ai-alt="{esc(photo["ai_alt"])}"'
        )
    toggle = ""
    if ai_available and model["image_mode"] == "both":
        toggle_text = "Show original photo" if use_ai else "Show AI illustration"
        toggle = f'<button type="button" class="btn btn-small btn-ghost-dark company-variant-toggle" data-company-variant aria-pressed="{"true" if use_ai else "false"}">{toggle_text}</button>'
    return f'''<figure class="{esc(figure_class)}"{style_attr} data-company-image data-variant="{variant}">
  <div class="{esc(frame_class)}"><img src="{esc(image_src)}"{image_attrs} width="{photo.get("original_width", 1)}" height="{photo.get("original_height", 1)}" loading="{loading}" decoding="async" alt="{esc(image_alt)}">{badge}</div>
  <figcaption data-company-caption data-original-caption="{esc(original_caption)}" data-ai-caption="{esc(ai_caption)}">{esc(active_caption)}</figcaption>
  {toggle}
</figure>'''


def photo_card(model, it, show_page=False):
    a = model["albums"][it["album"]]
    sci = ""
    if it.get("named"):
        sci = f'<p class="card-sci"><i>{esc(it["named"]["name_display"])}</i></p>'
    elif a["sci_display"]:
        sci = f'<p class="card-sci"><i>{esc(a["sci_display"])}</i></p>'
    page_note = ""
    if len(a["source_pages"]) > 1:
        page_note = f" &middot; original page {it['page_no']}"
    title = esc(it["title"])
    ai_available = bool(it.get("ai_asset"))
    use_ai = ai_available and model["image_mode"] == "ai-illustration"
    image_src = it["ai_asset"] if use_ai else it["asset"]
    image_alt = it["ai_alt"] if use_ai else it["alt"]
    variant = "ai-illustration" if use_ai else "original"
    ai_note = f'<p class="ai-label" data-ai-label{"" if use_ai else " hidden"}>{AI_LABEL}</p>' if ai_available else ""
    toggle = ""
    if ai_available and model["image_mode"] == "both":
        toggle_text = "Show original photo" if use_ai else "Show AI illustration"
        toggle = f'<button type="button" class="btn btn-small btn-ghost-dark ai-variant-toggle" data-card-variant aria-pressed="{"true" if use_ai else "false"}">{toggle_text}</button>'
    return f"""<li class="card" data-item="{esc(it['id'])}" data-album="{esc(it['album'])}" data-section="{esc(it['section'])}">
  <button type="button" class="card-media" data-open="{esc(it['id'])}" data-variant="{variant}" aria-label="Enlarge: {title}">
    <img src="{esc(image_src)}" data-original-src="{esc(it['asset'])}" data-original-alt="{esc(it['alt'])}" data-ai-src="{esc(it.get('ai_asset', ''))}" data-ai-alt="{esc(it.get('ai_alt', ''))}" width="{it['width']}" height="{it['height']}" loading="lazy" decoding="async" alt="{esc(image_alt)}">
  </button>
  <div class="card-body">
    <h3 class="card-title">{title}</h3>
    {sci}
    <p class="card-src">Source file {esc(it['file_id'])}{page_note}</p>
    {ai_note}
    {toggle}
    <button type="button" class="btn btn-small btn-add" data-add="{esc(it['id'])}">Add to enquiry</button>
  </div>
</li>"""


def gallery(model, items, label):
    cards = "\n".join(photo_card(model, it) for it in items)
    return f'<ul class="gallery" data-gallery aria-label="{esc(label)}">\n{cards}\n</ul>'


def category_chips(cats, label):
    out = []
    for c in cats:
        out.append(
            f'<li class="chip-item"><span class="chip-label">{esc(c["label"])}</span>'
            f'<button type="button" class="btn btn-small btn-add" data-add="{esc(c["id"])}" '
            f'aria-label="Add {esc(c["label"])} category to enquiry">Add</button></li>')
    return f'<ul class="chip-list" aria-label="{esc(label)}">' + "".join(out) + "</ul>"


def lightbox():
    return f"""<dialog id="lightbox" class="lightbox" aria-labelledby="lb-title">
  <div class="lb-inner">
    <div class="lb-head">
      <h2 id="lb-title" class="lb-title">Photo</h2>
      <button type="button" class="btn btn-ghost-dark btn-icon" data-lb-close aria-label="Close enlarged photo">&times; <span>Close</span></button>
    </div>
    <div class="lb-stage" id="lb-stage">
      <button type="button" class="lb-nav lb-prev" data-lb-prev aria-label="Previous photo">&#8249;</button>
      <figure class="lb-figure"><img id="lb-img" alt="" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="></figure>
      <button type="button" class="lb-nav lb-next" data-lb-next aria-label="Next photo">&#8250;</button>
    </div>
    <div class="lb-meta">
      <p class="lb-sci" id="lb-sci"></p>
      <p class="lb-care" id="lb-care"></p>
      <p class="lb-src" id="lb-src"></p>
      <p class="lb-res" id="lb-res"></p>
      <p class="lb-count" id="lb-count" aria-live="polite"></p>
      <p class="ai-label" id="lb-ai-label" hidden>{AI_LABEL}</p>
    </div>
    <div class="lb-actions">
      <button type="button" class="btn btn-ghost-dark" data-lb-zoom aria-pressed="false">Actual size (1&times;)</button>
      <button type="button" class="btn btn-ghost-dark" data-lb-variant hidden>Show AI illustration</button>
      <button type="button" class="btn btn-accent" data-lb-add>Add to enquiry</button>
      <a class="btn btn-ghost-dark" href="enquiry.html">View enquiry list</a>
    </div>
  </div>
</dialog>"""


def album_nav(model, current_id, sec_id):
    sec = model["sections_by_id"][sec_id]
    tabs = [(sec["label"] + " overview", sec["page"], None)]
    if sec_id == "freshwater":
        for aid in sec["albums"]:
            a = model["albums"][aid]
            tabs.append((a["label"], a["page"], aid))
    elif sec_id in ("plants", "plants-driftwood"):
        tabs = [("Aquatic plants", "aquatic-plants.html", "aquatic-plants"),
                ("Plants on driftwood", "plants-on-driftwood.html", "plants-on-driftwood")]
    else:
        return ""
    out = []
    for label, href, aid in tabs:
        cur = ' aria-current="page"' if aid == current_id else ""
        out.append(f'<li><a href="{href}"{cur}>{esc(label)}</a></li>')
    return f'<nav class="subnav" aria-label="Gallery sections"><ul>{"".join(out)}</ul></nav>'


def care_panel(a, extra_html=""):
    rows = []
    if a["care"]:
        rows.append(f'<div><dt>pH</dt><dd>{esc(a["care"]["ph"])}</dd></div>')
        rows.append(f'<div><dt>Temperature</dt><dd>{esc(a["care"]["temperature_display"])}</dd></div>')
    dl = f'<dl class="facts">{"".join(rows)}</dl>' if rows else ""
    if not (rows or a["description"] or extra_html):
        return ""
    desc = f'<p>{esc(a["description"])}</p>' if a["description"] else ""
    return f"""<aside class="panel care-panel" aria-label="Care information as published on the original website">
  <h2 class="panel-title">Published care information</h2>
  {dl}{desc}{extra_html}
  <p class="muted small">Carried over from the original website; not independently verified.</p>
</aside>"""


def source_links(a, pages_note=True):
    links = []
    for p in a["source_pages"]:
        links.append(ext_link(p["url"], f'Original page {p["page_no"]}' if len(a["source_pages"]) > 1 else "Original page"))
    txt = " &middot; ".join(links)
    combined = ""
    if len(a["source_pages"]) > 1:
        combined = f" This gallery combines {len(a['source_pages'])} original pages."
    return f'<p class="source-line">Source: {txt}.{combined}</p>'


# ------------------------------------------------------------------ pages
def build_pages(ctx, model):
    P = {}
    albums = model["albums"]
    items_by_album = {}
    for it in model["items"]:
        items_by_album.setdefault(it["album"], []).append(it)
    blocks = model["blocks"]
    total_photos = len(model["items"])

    def cover(sec_id):
        return model["items_by_id"][model["sections_by_id"][sec_id]["cover"]]

    def image_variant(it):
        use_ai = bool(it.get("ai_asset")) and model["image_mode"] == "ai-illustration"
        return (
            it["ai_asset"] if use_ai else it["asset"],
            it["ai_alt"] if use_ai else it["alt"],
            use_ai,
        )

    def thumbnail_media(it):
        image_src, image_alt, use_ai = image_variant(it)
        variant = "ai-illustration" if use_ai else "original"
        ai_label = (
            f'<span class="ai-label ai-label-thumbnail" data-ai-label{"" if use_ai else " hidden"}>{AI_LABEL}</span>'
            if it.get("ai_asset") else ""
        )
        return f'''<span class="cat-media" data-thumbnail data-item="{esc(it['id'])}" data-variant="{variant}">
      <img src="{esc(image_src)}" data-original-src="{esc(it['asset'])}" data-original-alt="{esc(it['alt'])}" data-ai-src="{esc(it.get('ai_asset', ''))}" data-ai-alt="{esc(it.get('ai_alt', ''))}" width="{it['width']}" height="{it['height']}" loading="lazy" decoding="async" alt="{esc(image_alt)}">
      {ai_label}
    </span>'''

    def thumbnail_toggle(it, hero=False):
        if model["image_mode"] != "both" or not it.get("ai_asset"):
            return ""
        style = "btn-ghost" if hero else "btn-ghost-dark"
        return f'<button type="button" class="btn btn-small {style} thumbnail-variant-toggle" data-thumb-variant aria-pressed="false">Show AI illustration</button>'

    # =================================================================== HOME
    home_ld = json_ld({
        "@context": "https://schema.org", "@type": "Organization", "name": ctx.company_name,
        "address": {"@type": "PostalAddress", "streetAddress": ctx.addr1, "postalCode": "768144", "addressCountry": "SG"},
        "telephone": ctx.tel, "email": ctx.email_sales, "faxNumber": ctx.fax[0],
    })
    company_images = model["ed"]["company_images"]
    mosaic = [
        (company_images["exterior_contact"], 280, 188, "The Sanyo Aquarium premises (original company photograph)"),
        (model["items_by_id"]["freshwater-guppy-157"], None, None, None, "Freshwater"),
        (model["items_by_id"]["marine-fishes-05"], None, None, None, "Marine"),
        (model["items_by_id"]["aquatic-plants-11"], None, None, None, "Aquatic plants"),
    ]
    figs = []
    for m in mosaic:
        if isinstance(m[0], dict) and "file" in m[0]:
            photo, w, h, caption = m
            figs.append(company_figure(model, photo, caption, figure_class="mosaic-item", frame_class="mosaic-frame", loading="eager"))
            continue
        if isinstance(m[0], str):
            src, w, h, alt, cap = m
            item_attrs = ""
            image_attrs = ""
            ai_label = ""
            toggle = ""
        else:
            it = m[0]
            src, alt, use_ai = image_variant(it)
            w, h, cap = it["width"], it["height"], m[4]
            variant = "ai-illustration" if use_ai else "original"
            item_attrs = f' data-item="{esc(it["id"])}" data-thumbnail data-variant="{variant}"'
            image_attrs = f' data-original-src="{esc(it["asset"])}" data-original-alt="{esc(it["alt"])}" data-ai-src="{esc(it.get("ai_asset", ""))}" data-ai-alt="{esc(it.get("ai_alt", ""))}"'
            ai_label = (
                f'<p class="ai-label" data-ai-label{"" if use_ai else " hidden"}>{AI_LABEL}</p>'
                if it.get("ai_asset") else ""
            )
            toggle = thumbnail_toggle(it, hero=True)
        figs.append(f'<figure class="mosaic-item"{item_attrs}><div class="mosaic-frame"><img src="{esc(src)}"{image_attrs} width="{w}" height="{h}" alt="{esc(alt)}" decoding="async"></div><figcaption>{esc(cap)}</figcaption>{ai_label}{toggle}</figure>')
    hero_svg = """<svg class="hero-waves" viewBox="0 0 1440 220" preserveAspectRatio="none" aria-hidden="true" focusable="false">
  <path d="M0 150 C 180 110 320 190 520 150 S 900 90 1100 140 S 1340 170 1440 120 L1440 220 L0 220 Z" fill="rgba(255,255,255,.05)"/>
  <path d="M0 185 C 220 150 380 215 620 180 S 1000 140 1200 178 S 1380 200 1440 170 L1440 220 L0 220 Z" fill="rgba(250,247,240,.09)"/>
  <g fill="none" stroke="rgba(120,200,170,.22)" stroke-width="6" stroke-linecap="round">
    <path d="M70 220 C 50 170 95 140 70 90 S 60 40 78 10"/>
    <path d="M118 220 C 138 175 100 150 124 110 S 140 70 126 40"/>
    <path d="M1320 220 C 1300 175 1342 148 1318 104 S 1312 56 1330 24"/>
    <path d="M1372 220 C 1392 180 1356 160 1378 126 S 1394 90 1380 64"/>
  </g>
  <g fill="rgba(255,255,255,.10)"><circle cx="210" cy="60" r="7"/><circle cx="238" cy="104" r="4"/><circle cx="1180" cy="52" r="6"/><circle cx="1215" cy="92" r="3.5"/><circle cx="660" cy="40" r="4"/></g>
</svg>"""

    discover = []
    sec_blurb = {
        "freshwater": "Photo galleries for platy, guppy, molly, swordtail and cichild, plus the full list of freshwater categories the company lists.",
        "marine": "A wide assortment of marine fishes: a photo gallery alongside the company’s category list.",
        "plants": "Aquatic plants supplied as loose plants, lead bunch, potted plants and plants on driftwood.",
        "plants-driftwood": "A separate gallery of aquatic plants on driftwood, kept distinct as on the original site.",
        "new": "Two entries from the original site’s New Fishes page, with their published care notes. The page is undated, so these are not shown as current stock.",
        "driftwood": "Driftwood in different shapes and sizes. Source shipment note: packed in 20 footer container and sent by sea.",
    }
    for s in model["sections"]:
        cv = model["items_by_id"][s["cover"]]
        n = sum(len(albums[a]["item_ids"]) for a in s["albums"])
        discover.append(f"""<li class="cat-card" data-item="{esc(cv['id'])}">
  <a class="cat-card-link" href="{s['page']}">
    {thumbnail_media(cv)}
    <span class="cat-text"><span class="cat-title">{esc(s['label'])}</span>
    <span class="cat-desc">{esc(sec_blurb[s['id']])}</span>
    <span class="cat-meta">{n} photo{'s' if n != 1 else ''} &middot; View gallery &rarr;</span></span>
  </a>
  {thumbnail_toggle(cv)}
</li>""")

    body = f"""<section class="hero">
  <div class="hero-bg" aria-hidden="true">{hero_svg}</div>
  <div class="container hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">Singapore exporter &middot; Trade catalogue</p>
      <h1>{esc(ctx.site['tagline'])}</h1>
      <p class="lead">Ornamental freshwater fish, marine fish, aquatic plants and driftwood for importers and wholesale buyers. Browse the photo catalogue, then prepare an enquiry for the sales team.</p>
      <div class="hero-actions">
        <a class="btn btn-accent btn-lg" href="catalogue.html">Browse products</a>
        <a class="btn btn-ghost btn-lg" href="enquiry.html">Prepare an enquiry</a>
      </div>
      <p class="hero-fine">AI illustrations are visual aids, not photographs of actual premises or stock. Prices and availability are not published &mdash; ask through an enquiry.</p>
    </div>
    <div class="hero-mosaic">{''.join(figs)}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="section-title">Find products</h2>
    <p class="section-lead">Every gallery from the company&rsquo;s original website, organised by category. Photos keep their source album and file identifier.</p>
    <ul class="cat-grid">{''.join(discover)}</ul>
    <p class="after-grid"><a class="btn btn-primary" href="catalogue.html">Search the full catalogue</a></p>
  </div>
</section>

<section class="section section-tint">
  <div class="container two-col">
    <div>
      <h2 class="section-title">About Sanyo Aquarium</h2>
      <p>Sanyo Aquarium (Pte) Ltd exports ornamental freshwater fish, marine fish and invertebrates, aquatic plants and potted plants from Singapore, according to the company profile on its original website.</p>
      <h3 class="subhead">Quality and quarantine, as the company describes it {pill('Historical statement')}</h3>
      <ul class="check-list">
        <li>Visual checks on all fishes from its suppliers, and rejection of fishes that do not meet quality standards.</li>
        <li>Imported fishes held in quarantine, fed and treated during that period.</li>
        <li>In-house conditioning on the shipment day before packing, with automated packing and sealing.</li>
      </ul>
      <p class="muted small">Summarised from the original profile (last modified 10 July 2012); not re-verified. Figures, memberships and support promises are on the <a href="company.html">company page</a> with the same qualification.</p>
      <p><a class="btn btn-primary" href="company.html">Read the company profile</a></p>
    </div>
    {company_figure(model, company_images["facility"][3], "Holding tanks (original company photograph)", style=f"max-width:{2*169+22}px")}
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="section-title">How an enquiry works</h2>
    <ol class="steps-cards">
      <li><span class="step-n">1</span><h3>Add items</h3><p>Use <strong>Add to enquiry</strong> on any photo or category. Your list is saved on this device.</p></li>
      <li><span class="step-n">2</span><h3>Add quantities and notes</h3><p>Set the quantity and note the variety or size you need, then add your company and destination details.</p></li>
      <li><span class="step-n">3</span><h3>Send it yourself</h3><p>Open a ready-written email draft or download the text. <strong>This website does not send anything</strong> &mdash; you press Send in your email app.</p></li>
    </ol>
    <p><a class="btn btn-accent btn-lg" href="enquiry.html">Prepare an enquiry</a></p>
  </div>
</section>

<section class="section section-dark">
  <div class="container contact-strip">
    <div>
      <h2 class="section-title">Contact</h2>
      <address>
        {esc(ctx.company_name)}<br>{esc(ctx.addr1)}, {esc(ctx.addr2)}
      </address>
    </div>
    <ul class="contact-links">
      <li><a class="btn btn-ghost btn-lg" href="{esc(tel_href(ctx.tel))}">Call {esc(ctx.tel)}</a></li>
      <li><a class="btn btn-ghost btn-lg" href="mailto:{esc(ctx.email_sales)}">Email {esc(ctx.email_sales)}</a></li>
    </ul>
  </div>
</section>"""
    P["index.html"] = page(ctx, "index.html", "Sanyo Aquarium — Aquatic life, from Singapore",
                           "Singapore exporter of ornamental freshwater fish, marine fish, aquatic plants and driftwood. Browse the photo catalogue and prepare an enquiry for the sales team.",
                           "home", body, extra_head=home_ld, with_data=False)

    # =================================================================== COMPANY
    sents = re.split(r"(?<=\.)\s+", blocks["about.intro"]["text"])
    assert len(sents) == 3, sents
    s_intro, s_history, s_member = sents
    cust = blocks["about.customers"]["text"]
    cust_sents = re.split(r"(?<=\.)\s+", cust)
    qualities_intro = blocks["about.qualities.intro"]["text"]
    q_items = "".join(f"<li>{esc(blocks[f'about.quality_process.{n}']['text'])}</li>" for n in range(1, 7))
    svc_items = "".join(f"<li>{esc(blocks[f'about.services.{n}']['text'])}</li>" for n in (1, 2))
    ass_items = "".join(f"<li>{esc(blocks[f'about.assurance.{n}']['text'])}</li>" for n in range(1, 5))
    ci = model["ed"]["company_images"]
    fac = "".join(
        company_figure(model, f, f'{f["caption"]} (original company photograph)', figure_class="photo-frame small")
        for f in ci["facility"])
    org_links = " &middot; ".join(ext_link(o["href"], esc(o["text"])) for o in model["src"]["about_orgs"])
    body = page_header([("Home", "index.html"), ("Company", None)], "Company profile",
                       f"{esc(ctx.company_name)} is a Singapore exporter of ornamental freshwater fish, marine fish and invertebrates, aquatic plants and potted plants.")
    body += f"""
<section class="section">
  <div class="container prose-wide">
    {notice('This profile is rewritten from the company&rsquo;s original website, whose pages were last modified on 10 July 2012. Statements marked ' + pill('Historical statement') + ' are quoted from that site, have <strong>not</strong> been re-verified and are not presented as current facts. The company is asked to confirm or update them. See the <a href="content-notes.html">content notes</a>.', 'warn', 'About these statements.')}
    <div class="two-col two-col-narrow">
      <div>
        <h2 class="section-title">What the company exports</h2>
        <p>Main products and services as listed on the original profile:</p>
        <ul class="check-list">{svc_items}</ul>
        <p>The catalogue also covers aquatic plants, plants on driftwood and driftwood &mdash; see the <a href="catalogue.html">full catalogue</a>.</p>
        <p class="hist-line">{pill('Historical statement')} &ldquo;{esc(blocks['about.services.3']['text'])}&rdquo; &mdash; no operating hours or response times are published, and none are promised here.</p>
      </div>
      {company_figure(model, ci["exterior"], "Original company photograph", style=f"max-width:{2*178+22}px", loading="eager")}
    </div>
  </div>
</section>

<section class="section section-tint">
  <div class="container prose-wide">
    <h2 class="section-title">Quality and quarantine {pill('Historical statement')}</h2>
    <blockquote class="quote">&ldquo;{esc(qualities_intro)}&rdquo;<footer>Original company profile</footer></blockquote>
    <p>The original profile lists these quality-control processes:</p>
    <ul class="check-list">{q_items}</ul>
    <p class="muted small">Quarantine duration and tank numbers are the company&rsquo;s own figures from the original website and have not been confirmed for today.</p>
    <h3 class="subhead">Packing and facility photographs</h3>
    <div class="photo-row">{fac}</div>
    <p class="muted small">Original photographs remain as separate files with their watermarks. The illustrations are generic visual aids, not photographs of this facility.</p>
  </div>
</section>

<section class="section">
  <div class="container prose-wide">
    <h2 class="section-title">Company assurances</h2>
    <p>The company&rsquo;s own statements of what it offers, as written on the original profile:</p>
    <ul class="check-list">{ass_items}</ul>
    <p class="muted small">Self-descriptions with no supporting evidence on the original page; not independently verified. Prices, new-species availability and freight costs are not published on this site.</p>
  </div>
</section>

<section class="section section-tint" id="historical">
  <div class="container prose-wide">
    <h2 class="section-title">Historical statements from the original website</h2>
    <p>The original profile says the following. These are kept visible for transparency but are <strong>not</strong> verified as current and are not used as marketing claims.</p>
    <div class="hist-grid">
      <article class="hist-card">
        <h3>Years in business {pill('Historical statement')}</h3>
        <blockquote class="quote">&ldquo;{esc(s_history)}&rdquo;</blockquote>
        <p class="muted small">The source page does not say when this was written (the site&rsquo;s files date from 2012), so no current number of years is calculated.</p>
      </article>
      <article class="hist-card">
        <h3>Long-standing customers {pill('Historical statement')}</h3>
        <blockquote class="quote">&ldquo;{esc(cust)}&rdquo;</blockquote>
        <p class="muted small">Reproduced exactly as written. &ldquo;Cairo&rdquo; appears in the source&rsquo;s list of countries; it is a city, so the list needs company review. This is not a statement of where Sanyo ships today.</p>
      </article>
      <article class="hist-card">
        <h3>Memberships and accreditation {pill('Not verified as current')}</h3>
        <blockquote class="quote">&ldquo;{esc(s_member)}&rdquo;</blockquote>
        <img class="member-strip" src="assets/img/company/aboutus_member.webp" width="403" height="50" loading="lazy" decoding="async" alt="{esc(ci['member_strip']['alt'])}">
        <p class="small">Links as on the original page: {org_links}</p>
        <p class="muted small">Membership status and the accreditation scheme have not been checked with the organisations. No certificate is shown or implied.</p>
      </article>
    </div>
  </div>
</section>

<section class="section section-dark">
  <div class="container contact-strip">
    <div><h2 class="section-title">Ready to ask about products?</h2><p>Build an enquiry list or contact the sales team directly.</p></div>
    <ul class="contact-links">
      <li><a class="btn btn-accent btn-lg" href="enquiry.html">Prepare an enquiry</a></li>
      <li><a class="btn btn-ghost btn-lg" href="contact.html">Contact details</a></li>
    </ul>
  </div>
</section>"""
    P["company.html"] = page(ctx, "company.html", "Company profile — Sanyo Aquarium",
                             "Company profile of Sanyo Aquarium (Pte) Ltd, a Singapore exporter of ornamental fish, plants and driftwood, with the original website's quality and facility information clearly qualified.",
                             "company", body, with_data=False)

    # =================================================================== CATALOGUE
    chips = ['<button type="button" class="chip" data-section-chip="" aria-pressed="true">All</button>']
    for s in model["sections"]:
        chips.append(f'<button type="button" class="chip" data-section-chip="{esc(s["id"])}" aria-pressed="false">{esc(s["label"].replace(" (source page)", ""))}</button>')
    noscript_links = "".join(f'<li><a href="{s["page"]}">{esc(s["label"])}</a></li>' for s in model["sections"])
    body = page_header([("Home", "index.html"), ("Catalogue", None)], "Product catalogue",
                       f"Search all {total_photos} photographs and every listed category from the original website. Add anything to your enquiry list.")
    body += f"""
<section class="section catalogue-tools-wrap">
  <div class="container">
    <form class="catalogue-tools" id="cat-form" role="search" aria-label="Catalogue search" novalidate>
      <div class="field field-grow">
        <label for="q">Search names, scientific names or file numbers</label>
        <input id="q" name="q" type="search" autocomplete="off" inputmode="search" enterkeyhint="search" placeholder="e.g. platy, maculatus, guppy, 005">
      </div>
      <div class="field">
        <label for="album">Gallery</label>
        <select id="album" name="album"><option value="">All galleries</option></select>
      </div>
      <div class="field field-chips">
        <span class="field-label" id="chips-label">Category</span>
        <div class="chips" role="group" aria-labelledby="chips-label">{''.join(chips)}</div>
      </div>
      <div class="field field-actions"><button type="reset" class="btn btn-ghost-dark" id="cat-clear">Clear filters</button></div>
    </form>
    <p id="result-count" class="result-count" role="status" aria-live="polite"></p>
    <div id="results" class="results"></div>
    <noscript><div class="notice notice-info"><p>Search and filters need JavaScript. You can still browse each gallery:</p><ul>{noscript_links}</ul></div></noscript>
  </div>
</section>
{lightbox()}"""
    P["catalogue.html"] = page(ctx, "catalogue.html", "Product catalogue — Sanyo Aquarium",
                               "Search and filter the Sanyo Aquarium photo catalogue: freshwater and marine fishes, aquatic plants, plants on driftwood and driftwood.",
                               "catalogue", body, scripts=("enquiry-store.js", "ui.js", "catalogue.js"))

    # =================================================================== FRESHWATER OVERVIEW
    fw_cats = [c for c in model["categories"] if c["section"] == "freshwater"]
    fw_without = [c for c in fw_cats if not c["has_photos"]]
    fam_cards = []
    for aid in model["sections_by_id"]["freshwater"]["albums"]:
        a = albums[aid]
        first = items_by_album[aid][0]
        sci = f'<span class="cat-sci"><i>{esc(a["sci_display"])}</i></span>' if a["sci_display"] else ""
        fam_cards.append(f"""<li class="cat-card" data-item="{esc(first['id'])}">
  <a class="cat-card-link" href="{a['page']}">
    {thumbnail_media(first)}
    <span class="cat-text"><span class="cat-title">{esc(a['label'])}</span>{sci}
    <span class="cat-meta">{len(a['item_ids'])} photos &middot; View gallery &rarr;</span></span>
  </a>
  {thumbnail_toggle(first)}
</li>""")
    body = page_header([("Home", "index.html"), ("Freshwater fishes", None)], "Freshwater fishes",
                       "A wide range of ornamental freshwater fish, with particular emphasis on platy, swordtail, mollies, barb, guppy, tetra and angel.")
    body += f"""
<section class="section">
  <div class="container">
    <h2 class="section-title">Photo galleries</h2>
    <ul class="cat-grid">{''.join(fam_cards)}</ul>
    <p class="source-line">Source: {ext_link(model['src']['pages']['freshwaterfishes.html']['url'], 'Original page')}.</p>
  </div>
</section>
<section class="section section-tint">
  <div class="container">
    <h2 class="section-title">Also listed by the company</h2>
    <p class="section-lead">These freshwater categories are named on the original site but have no photo gallery there. Use <strong>Add</strong> to include a category in an enquiry. The list is reproduced exactly as published (including the duplicate &ldquo;Snail&rdquo;/&ldquo;Snails&rdquo; and &ldquo;other&rdquo;).</p>
    {category_chips(fw_without, 'Freshwater categories without photographs')}
  </div>
</section>"""
    P["freshwater-fishes.html"] = page(ctx, "freshwater-fishes.html", "Freshwater fishes — Sanyo Aquarium",
                                       "Freshwater ornamental fish from Sanyo Aquarium: platy, guppy, molly, swordtail and cichild photo galleries plus the full category list.",
                                       "freshwater", body)

    # =================================================================== ALBUM PAGES
    def album_body(aid, trail, lead, extra_panel="", pre_gallery="", post_gallery=""):
        a = albums[aid]
        its = items_by_album[aid]
        sec_id = a["section"]
        sci = a["sci_display"]
        header = page_header(trail, a["title"], lead, sci)
        prop = ""
        if a.get("proposed"):
            p = a["proposed"]
            txt = p.get("sci") or p.get("label")
            prop = f'<p class="proposal"><strong>Proposed correction (not confirmed by the company):</strong> {esc(txt)}. {esc(p["note"])}</p>'
        whole = next((c for c in model["categories"] if c["album"] == aid and c["has_photos"] is True and c["section"] == sec_id), None)
        whole_btn = ""
        if whole is None:
            whole = next((c for c in model["categories"] if c["album"] == aid), None)
        if whole:
            whole_btn = f'<button type="button" class="btn btn-primary btn-add" data-add="{esc(whole["id"])}">Add &ldquo;{esc(a["label"])}&rdquo; (any) to enquiry</button>'
        nav = album_nav(model, aid, sec_id)
        return f"""{header}
<section class="section album-section">
  <div class="container">
    {nav}
    {prop}
    <div class="album-top">
      {care_panel(a, extra_panel)}
      <div class="album-actions">{whole_btn}<p class="muted small">Or add individual photos below. {len(its)} photos in this gallery.</p>{source_links(a)}</div>
    </div>
    {pre_gallery}
    {'' if 'id="gallery"' in pre_gallery else '<h2 class="visually-hidden" id="gallery">Photo gallery</h2>'}
    {gallery(model, its, a['title'] + ' photo gallery')}
    {post_gallery}
  </div>
</section>
{lightbox()}"""

    for aid in model["sections_by_id"]["freshwater"]["albums"]:
        a = albums[aid]
        trail = [("Home", "index.html"), ("Freshwater fishes", "freshwater-fishes.html"), (a["label"], None)]
        extra = ""
        pre = ""
        lead = None
        if aid == "freshwater-platy":
            extra = '<p class="withheld"><strong>Breeding guidance withheld.</strong> The original text includes a breeding temperature that cannot be correct as written. It is not shown until the company confirms it &mdash; see <a href="content-notes.html#R07">content note R07</a>.</p>'
        if aid == "freshwater-cichild":
            pre = notice("The original site gives this gallery no scientific name, care information or individual photo labels, so none are shown. Photos are identified by their original file names.", "info")
        if aid == "freshwater-molly":
            pre = notice("Photos are shown in the Molly gallery exactly as on the original site. One photo may be misfiled &mdash; flagged for company review (<a href=\"content-notes.html#R14\">R14</a>).", "info")
        body = album_body(aid, trail, lead, extra, pre)
        titles = {
            "freshwater-platy": "Platy photo gallery — Sanyo Aquarium",
            "freshwater-guppy": "Guppy photo gallery — Sanyo Aquarium",
            "freshwater-molly": "Molly photo gallery — Sanyo Aquarium",
            "freshwater-swordtail": "Swordtail photo gallery — Sanyo Aquarium",
            "freshwater-cichild": "Cichild photo gallery — Sanyo Aquarium",
        }
        P[a["page"]] = page(ctx, a["page"], titles[aid],
                            f"{a['label']} photo gallery from Sanyo Aquarium: {len(a['item_ids'])} original photographs with published source care information and an add-to-enquiry option.",
                            "freshwater", body)

    # =================================================================== MARINE
    marine_cats = [c for c in model["categories"] if c["section"] == "marine" and not c["has_photos"]]
    pre = f"""<h2 class="section-title">Categories listed by the company</h2>
    <p class="section-lead">The original marine page names these categories and separately shows a photo gallery. It does not say which photo belongs to which category, so none is assigned here.</p>
    {category_chips(marine_cats, 'Marine categories')}
    {notice('The company profile also mentions marine invertebrates, but the original marine page lists no invertebrate category and labels no invertebrate photo.', 'info')}
    <h2 class="section-title" id="gallery">Photo gallery</h2>"""
    body = album_body("marine-fishes", [("Home", "index.html"), ("Marine fishes", None)],
                      "A wide assortment of marine fishes, with a photo gallery and the company&rsquo;s category list.", "", pre)
    P["marine-fishes.html"] = page(ctx, "marine-fishes.html", "Marine fishes — Sanyo Aquarium",
                                   "Marine fishes from Sanyo Aquarium: the company's category list and a gallery of 15 original photographs, each identified by source file.",
                                   "marine", body)

    # =================================================================== PLANTS
    supply = "".join(f"<li>{esc(x)}</li>" for x in model["ed"]["plant_supply_forms"])
    extra = f'<div class="supply"><h3 class="panel-subtitle">Supply forms (as listed on the original site)</h3><ul class="check-list compact">{supply}</ul></div>'
    body = album_body("aquatic-plants", [("Home", "index.html"), ("Aquatic plants", None)],
                      "A wide variety of aquatic plants, sold as loose plants, lead bunch, potted plants and plants on driftwood.", extra,
                      notice("Photos are identified only by album and original file number; the original site gives no plant names.", "info"))
    P["aquatic-plants.html"] = page(ctx, "aquatic-plants.html", "Aquatic plants — Sanyo Aquarium",
                                    "Aquatic plants from Sanyo Aquarium: 24 original photographs from three source gallery pages, with the supply forms listed by the company.",
                                    "plants", body)
    body = album_body("plants-on-driftwood", [("Home", "index.html"), ("Aquatic plants", "aquatic-plants.html"), ("Plants on driftwood", None)],
                      "A separate gallery of aquatic plants on driftwood, kept distinct as on the original site.", extra,
                      notice("Photos are identified only by album and original file number; the original site gives no plant names.", "info"))
    P["plants-on-driftwood.html"] = page(ctx, "plants-on-driftwood.html", "Plants on driftwood — Sanyo Aquarium",
                                         "Aquatic plants on driftwood from Sanyo Aquarium: the distinct source gallery of three original photographs.",
                                         "plants", body)

    # =================================================================== DRIFTWOOD
    dw = blocks["driftwood.intro"]["text"]
    ship = f"""<aside class="panel" aria-label="Shipment information"><h2 class="panel-title">Shipment information</h2>
    <p>As published on the original site: &ldquo;{esc(dw)}&rdquo;</p>
    <p class="muted small">No destinations, lead times, minimum quantities or prices are published; ask in an enquiry.</p></aside>"""
    body = album_body("driftwood", [("Home", "index.html"), ("Driftwood", None)],
                      "Driftwood in different shapes and sizes.", "", ship)
    P["driftwood.html"] = page(ctx, "driftwood.html", "Driftwood — Sanyo Aquarium",
                               "Driftwood from Sanyo Aquarium in different shapes and sizes, with the shipment information published on the original site.",
                               "driftwood", body)

    # =================================================================== NEW FISHES
    entries = []
    for it in items_by_album["new-fishes"]:
        n = it["named"]
        desc = "".join(f"<p>{esc(l)}</p>" for l in n["description_lines"])
        ai_available = bool(it.get("ai_asset"))
        use_ai = ai_available and model["image_mode"] == "ai-illustration"
        image_src = it["ai_asset"] if use_ai else it["asset"]
        image_alt = it["ai_alt"] if use_ai else it["alt"]
        variant = "ai-illustration" if use_ai else "original"
        ai_note = f'<p class="ai-label" data-ai-label{"" if use_ai else " hidden"}>{AI_LABEL}</p>' if ai_available else ""
        toggle = ""
        if ai_available and model["image_mode"] == "both":
            toggle_text = "Show original photo" if use_ai else "Show AI illustration"
            toggle = f'<button type="button" class="btn btn-small btn-ghost-dark ai-variant-toggle" data-card-variant aria-pressed="{"true" if use_ai else "false"}">{toggle_text}</button>'
        prop = ""
        if n["proposed"]:
            p = n["proposed"]
            prop = f'<p class="proposal"><strong>Proposed correction (not confirmed by the company):</strong> <i>{esc(p["sci"])}</i>. {esc(p["note"])}</p>'
        entries.append(f"""<article class="entry" data-item="{esc(it['id'])}" data-album="new-fishes" data-section="new">
  <button type="button" class="card-media entry-media" data-open="{esc(it['id'])}" data-variant="{variant}" aria-label="Enlarge: {esc(it['title'])}">
    <img src="{esc(image_src)}" data-original-src="{esc(it['asset'])}" data-original-alt="{esc(it['alt'])}" data-ai-src="{esc(it.get('ai_asset', ''))}" data-ai-alt="{esc(it.get('ai_alt', ''))}" width="{it['width']}" height="{it['height']}" loading="lazy" decoding="async" alt="{esc(image_alt)}">
  </button>
  <div class="entry-body">
    <h2 class="entry-title"><i>{esc(n['name_display'])}</i></h2>
    <p class="muted small">Name as written on the original site: {esc(n['name_source'])}</p>
    {prop}
    <dl class="facts"><div><dt>pH</dt><dd>{esc(n['ph'])}</dd></div><div><dt>Temperature</dt><dd>{esc(n['temperature_display'])}</dd></div></dl>
    <h3 class="subhead">Description (original text)</h3>
    {desc}
    <p class="card-src">Source file {esc(it['file_id'])}</p>
    {ai_note}
    {toggle}
    <button type="button" class="btn btn-primary btn-add" data-add="{esc(it['id'])}">Add to enquiry</button>
  </div>
</article>""")
    body = page_header([("Home", "index.html"), ("New Fishes", None)], "New Fishes (source page)",
                       "Two named entries from the original site&rsquo;s &ldquo;New Fishes&rdquo; page.")
    body += f"""
<section class="section">
  <div class="container prose-wide">
    {notice('The original page carries <strong>no date and no availability statement</strong>. These entries are not presented as recent arrivals or as current stock. Care information is carried over from the original page and has not been verified.', 'warn', 'Not a statement of current stock.')}
    <div data-gallery class="entries">{''.join(entries)}</div>
    {source_links(albums['new-fishes'])}
  </div>
</section>
{lightbox()}"""
    P["new-fishes.html"] = page(ctx, "new-fishes.html", "New Fishes (source page) — Sanyo Aquarium",
                                "Two named entries from the original Sanyo Aquarium New Fishes page, with published care information. The page is undated and does not indicate current stock.",
                                "new", body)

    # =================================================================== CONTACT
    body = page_header([("Home", "index.html"), ("Contact", None)], "Contact",
                       "Reach the sales team by email or telephone, or prepare an itemised enquiry first.")
    body += f"""
<section class="section">
  <div class="container two-col contact-cols">
    <div>
      <div class="panel contact-card">
        <h2 class="panel-title">{esc(ctx.company_name)}</h2>
        <address class="contact-address">
          {esc(ctx.addr1)}<br>{esc(ctx.addr2)}
        </address>
        <dl class="contact-dl">
          <div><dt>Telephone</dt><dd><a href="{esc(tel_href(ctx.tel))}">{esc(ctx.tel)}</a></dd></div>
          <div><dt>Fax</dt><dd>{esc(ctx.fax[0])} / {esc(ctx.fax[1])}</dd></div>
          <div><dt>Sales email</dt><dd><a href="mailto:{esc(ctx.email_sales)}">{esc(ctx.email_sales)}</a></dd></div>
          <div><dt>General email</dt><dd><a href="mailto:{esc(ctx.email_info)}">{esc(ctx.email_info)}</a></dd></div>
        </dl>
        <p class="muted small">Details checked against the original website on {esc(ctx.site['audit_date'])}. No opening hours or response times are published.</p>
      </div>
      <div class="panel">
        <h2 class="panel-title">Make an enquiry</h2>
        <ol class="plain-steps">
          <li>Add the fish, plants or driftwood you are interested in from the <a href="catalogue.html">catalogue</a>.</li>
          <li>Set quantities, add notes on variety or size, and give your destination country or city and any import requirements.</li>
          <li>Open the email draft (or download the text) and send it from your own email program.</li>
        </ol>
        <p><a class="btn btn-accent btn-lg" href="enquiry.html">Prepare an enquiry</a></p>
        <p class="muted small">This site cannot send email or forms. Nothing is transmitted until you send the draft yourself. The original website&rsquo;s contact form is not reproduced.</p>
      </div>
    </div>
    {company_figure(model, ci["exterior_contact"], "The Sanyo Aquarium premises (original company photograph)", style=f"max-width:{2*280+22}px", loading="eager")}
  </div>
</section>"""
    P["contact.html"] = page(ctx, "contact.html", "Contact — Sanyo Aquarium",
                             "Contact Sanyo Aquarium (Pte) Ltd, 3 Chencharu Link, Singapore 768144: telephone, fax and email, plus the enquiry workflow.",
                             "contact", body, extra_head=home_ld, with_data=False)

    # =================================================================== ENQUIRY
    suppl_opts = "".join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in model["ed"]["plant_supply_forms"])
    body = page_header([("Home", "index.html"), ("Enquiry", None)], "Prepare an enquiry",
                       "Build a list, add your details, then open an email draft or download the text. <strong>This website does not send anything for you.</strong>")
    body += f"""
<section class="section" id="enquiry-app">
  <div class="container">
    <noscript><div class="notice notice-warn"><p>The enquiry list needs JavaScript. You can still email <a href="mailto:{esc(ctx.email_sales)}">{esc(ctx.email_sales)}</a> directly.</p></div></noscript>
    <ol class="stepper" id="stepper" aria-label="Enquiry steps">
      <li data-step-ind="items"><a href="#items"><span class="step-n">1</span> Items</a></li>
      <li data-step-ind="details"><a href="#details"><span class="step-n">2</span> Your details</a></li>
      <li data-step-ind="review"><a href="#review"><span class="step-n">3</span> Review &amp; send</a></li>
    </ol>
    <div id="error-summary" class="error-summary" role="alert" tabindex="-1" hidden></div>

    <section id="step-items" class="step" data-step="items" aria-labelledby="h-items" hidden>
      <h2 id="h-items" tabindex="-1">1. Your enquiry list</h2>
      <div id="items-empty" class="empty-state" hidden>
        <h3>Your enquiry list is empty</h3>
        <p>Add photos or categories from the catalogue, or add an item that is not listed below.</p>
        <p><a class="btn btn-primary" href="catalogue.html">Browse the catalogue</a></p>
      </div>
      <ul id="items-list" class="enquiry-items"></ul>
      <form id="custom-form" class="panel custom-form" novalidate>
        <h3 class="panel-title">Add an item that is not listed</h3>
        <div class="form-row">
          <div class="field field-grow"><label for="custom-name">Species or product</label><input id="custom-name" name="name" type="text" maxlength="120" autocomplete="off" placeholder="e.g. a category or variety you need"></div>
          <div class="field field-qty"><label for="custom-qty">Quantity</label><input id="custom-qty" name="qty" type="number" inputmode="numeric" min="1" max="99999" step="1" value="1"></div>
        </div>
        <div class="field"><label for="custom-note">Variety / size notes <span class="muted">(optional)</span></label><input id="custom-note" name="note" type="text" maxlength="300" autocomplete="off"></div>
        <p class="field-error" id="custom-error" hidden></p>
        <button class="btn btn-primary" type="submit">Add to list</button>
      </form>
      <div class="step-actions">
        <a class="btn btn-ghost-dark" href="catalogue.html">Add more from the catalogue</a>
        <button type="button" class="btn btn-accent" id="to-details">Continue to your details</button>
        <button type="button" class="btn btn-link" id="clear-list">Clear list</button>
      </div>
      <p class="muted small">Your item list is saved in this browser on this device only (local storage) so it survives page changes. It is never uploaded.</p>
    </section>

    <section id="step-details" class="step" data-step="details" aria-labelledby="h-details" hidden>
      <h2 id="h-details" tabindex="-1">2. Your details</h2>
      <form id="details-form" novalidate autocomplete="on">
        <div class="form-grid">
          <div class="field"><label for="f-name">Your name <span class="req">*</span></label><input id="f-name" name="name" type="text" autocomplete="name" required aria-describedby="e-name"><p class="field-error" id="e-name" hidden></p></div>
          <div class="field"><label for="f-designation">Designation <span class="muted">(optional)</span></label><input id="f-designation" name="designation" type="text" autocomplete="organization-title"></div>
          <div class="field"><label for="f-company">Company name <span class="req">*</span></label><input id="f-company" name="company" type="text" autocomplete="organization" required aria-describedby="e-company"><p class="field-error" id="e-company" hidden></p></div>
          <div class="field"><label for="f-email">Email address <span class="req">*</span></label><input id="f-email" name="email" type="email" autocomplete="email" inputmode="email" required aria-describedby="e-email"><p class="field-error" id="e-email" hidden></p></div>
          <div class="field"><label for="f-phone">Phone <span class="muted">(optional)</span></label><input id="f-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" aria-describedby="e-phone"><p class="field-error" id="e-phone" hidden></p></div>
          <div class="field"><label for="f-destination">Destination country or city <span class="req">*</span></label><input id="f-destination" name="destination" type="text" autocomplete="country-name" required aria-describedby="e-destination"><p class="field-error" id="e-destination" hidden></p></div>
        </div>
        <div class="field"><label for="f-address">Company address <span class="muted">(optional)</span></label><textarea id="f-address" name="address" rows="2" autocomplete="street-address"></textarea></div>
        <div class="field"><label for="f-requirements">Destination requirements <span class="muted">(optional)</span></label><textarea id="f-requirements" name="requirements" rows="3" aria-describedby="h-requirements"></textarea><p class="hint" id="h-requirements">For example import permits, delivery point or special requirements. This site does not state shipping destinations or lead times.</p></div>
        <div class="field"><label for="f-message">Message <span class="muted">(optional)</span></label><textarea id="f-message" name="message" rows="3"></textarea></div>
        <p class="muted small">Your details are kept only for this browser tab (session storage) so you can move between pages; they are cleared when you close the tab or choose &ldquo;Clear my details&rdquo;. They are not stored long-term and are never uploaded.</p>
        <div class="step-actions">
          <button type="button" class="btn btn-ghost-dark" id="back-items">Back to items</button>
          <button type="submit" class="btn btn-accent">Review enquiry</button>
          <button type="button" class="btn btn-link" id="clear-details">Clear my details</button>
        </div>
      </form>
    </section>

    <section id="step-review" class="step" data-step="review" aria-labelledby="h-review" hidden>
      <h2 id="h-review" tabindex="-1">3. Review &amp; send</h2>
      <div class="notice notice-warn" role="note"><p><strong>Nothing has been sent.</strong> This website has no email service. Use the email draft or download the text, then send it yourself.</p></div>
      <div class="review-grid">
        <div class="panel"><h3 class="panel-title">Items <button type="button" class="btn btn-link" id="edit-items">Edit items</button></h3><ol id="review-items" class="review-items"></ol></div>
        <div class="panel"><h3 class="panel-title">Your details <button type="button" class="btn btn-link" id="edit-details">Edit details</button></h3><dl id="review-details" class="review-details"></dl></div>
      </div>
      <div class="panel send-panel">
        <h3 class="panel-title">Send or save</h3>
        <div class="send-actions">
          <a class="btn btn-accent btn-lg" id="send-mailto" href="mailto:{esc(ctx.email_sales)}">Open email draft</a>
          <button type="button" class="btn btn-primary" id="copy-text">Copy text</button>
          <button type="button" class="btn btn-primary" id="dl-txt">Download .txt</button>
          <button type="button" class="btn btn-primary" id="dl-csv">Download .csv</button>
          <button type="button" class="btn btn-ghost-dark" id="print-enq">Print</button>
        </div>
        <p class="muted small" id="mailto-hint"></p>
        <div id="completion" class="completion" role="status" aria-live="polite" tabindex="-1" hidden></div>
      </div>
      <div class="step-actions">
        <button type="button" class="btn btn-ghost-dark" id="back-details">Back to details</button>
        <button type="button" class="btn btn-link" id="start-new">Start a new enquiry (clears list and details)</button>
      </div>
    </section>
  </div>
  <template id="plant-supply-options">{suppl_opts}</template>
</section>"""
    P["enquiry.html"] = page(ctx, "enquiry.html", "Prepare an enquiry — Sanyo Aquarium",
                             "Build an enquiry list from the Sanyo Aquarium catalogue, add quantities and destination details, then open an email draft or download the text. Nothing is sent automatically.",
                             "enquiry", body, scripts=("enquiry-store.js", "ui.js", "enquiry.js"))

    # =================================================================== CONTENT NOTES
    return P, {"home_ld": home_ld}
