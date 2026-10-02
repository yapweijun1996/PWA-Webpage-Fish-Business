"""Shared HTML shell: <head>, header, navigation, footer."""
import html
import json

NAV = [
    ("index.html", "Home", "home"),
    ("catalogue.html", "Catalogue", "catalogue"),
    ("freshwater-fishes.html", "Freshwater", "freshwater"),
    ("marine-fishes.html", "Marine", "marine"),
    ("aquatic-plants.html", "Plants", "plants"),
    ("driftwood.html", "Driftwood", "driftwood"),
    ("new-fishes.html", "New Fishes", "new"),
    ("company.html", "Company", "company"),
    ("contact.html", "Contact", "contact"),
]

SOURCE_URL = "https://www.sanyoaqm.com.sg/index.html"


def esc(s):
    return html.escape(str(s), quote=True)


def tel_href(tel):
    return "tel:" + "".join(ch for ch in tel if ch.isdigit() or ch == "+")


class Ctx:
    """Build-wide context (site config + contact details taken from the source record)."""

    def __init__(self, model):
        self.model = model
        self.site = model["ed"]["site"]
        c = model["contact"]
        self.contact = c
        # The contact block prints the name in capitals; the display name is the source header form.
        self.company_name = model["ed"]["site"]["name"]
        self.email_sales = c["emails"][0]
        self.email_info = c["emails"][1]
        self.tel = c["tel"]
        self.fax = c["fax"]
        self.addr1, self.addr2 = c["address_lines"]


def head(ctx, filename, title, description, extra_head=""):
    site = ctx.site
    robots = '<meta name="robots" content="noindex, nofollow">\n' if site.get("noindex") else ""
    canonical = ""
    if site.get("site_url"):
        base = site["site_url"].rstrip("/") + "/"
        canonical = f'<link rel="canonical" href="{esc(base + filename)}">\n'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
{robots}{canonical}<meta name="theme-color" content="#0d3b36">
<link rel="icon" type="image/png" href="assets/img/brand/favicon.png">
<link rel="stylesheet" href="assets/css/styles.css">
<script>document.documentElement.classList.add('js');</script>
{extra_head}</head>
"""


def header(ctx, active):
    items = []
    for href, label, key in NAV:
        cur = ' aria-current="page"' if key == active else ""
        items.append(f'<li><a href="{href}"{cur}>{esc(label)}</a></li>')
    return f"""<body class="page-{esc(active)}">
<a class="skip-link" href="#main">Skip to main content</a>
<header class="site-header">
  <div class="topbar">
    <div class="container topbar-inner">
      <span>Ornamental fish, plants and driftwood exporter &middot; Singapore</span>
      <span class="topbar-links">
        <a href="{esc(tel_href(ctx.tel))}">{esc(ctx.tel)}</a>
        <a href="mailto:{esc(ctx.email_sales)}">{esc(ctx.email_sales)}</a>
      </span>
    </div>
  </div>
  <div class="container header-main">
    <a class="brand" href="index.html">
      <img src="assets/img/brand/logo.gif" width="191" height="82" alt="">
      <span class="brand-text"><strong>Sanyo Aquarium</strong><small>(Pte) Ltd &middot; Singapore</small></span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
      <span class="nav-toggle-label">Menu</span>
    </button>
    <nav id="site-nav" class="site-nav" aria-label="Main">
      <ul>
        {''.join(items)}
      </ul>
    </nav>
    <a class="btn btn-accent header-enquiry" href="enquiry.html">Enquiry list <span class="count" data-enquiry-count aria-label="items in enquiry list">0</span></a>
  </div>
</header>
"""


def footer(ctx):
    c = ctx
    return f"""<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <p class="footer-brand">{esc(c.company_name)}</p>
      <address>
        {esc(c.addr1)}<br>{esc(c.addr2)}<br>
        Tel: <a href="{esc(tel_href(c.tel))}">{esc(c.tel)}</a><br>
        Fax: {esc(c.fax[0])} / {esc(c.fax[1])}<br>
        <a href="mailto:{esc(c.email_sales)}">{esc(c.email_sales)}</a><br>
        <a href="mailto:{esc(c.email_info)}">{esc(c.email_info)}</a>
      </address>
    </div>
    <div>
      <p class="footer-title">Browse</p>
      <ul class="footer-links">
        <li><a href="catalogue.html">Catalogue &amp; search</a></li>
        <li><a href="freshwater-fishes.html">Freshwater fishes</a></li>
        <li><a href="marine-fishes.html">Marine fishes</a></li>
        <li><a href="aquatic-plants.html">Aquatic plants</a></li>
        <li><a href="plants-on-driftwood.html">Plants on driftwood</a></li>
        <li><a href="driftwood.html">Driftwood</a></li>
        <li><a href="new-fishes.html">New Fishes (source page)</a></li>
      </ul>
    </div>
    <div>
      <p class="footer-title">Company &amp; enquiries</p>
      <ul class="footer-links">
        <li><a href="company.html">Company profile</a></li>
        <li><a href="contact.html">Contact</a></li>
        <li><a href="enquiry.html">Prepare an enquiry</a></li>
        <li><a href="content-notes.html">Content notes</a></li>
        <li><a href="{SOURCE_URL}" rel="noopener" target="_blank">Original website <span class="visually-hidden">(opens in a new tab)</span>&#8599;</a></li>
      </ul>
    </div>
  </div>
  <div class="container footer-note">
    <p>Original catalogue and company photographs remain preserved in the audit sources with their watermarks intact.
    AI illustrations are visual aids, not photographs of actual stock or company premises.
    Company statements marked &ldquo;historical&rdquo; come from that website (last modified 10 July 2012) and await company confirmation.
    No prices, stock levels or availability are published here.</p>
  </div>
</footer>
<a class="enquiry-fab" href="enquiry.html">Enquiry list <span class="count" data-enquiry-count aria-label="items in enquiry list">0</span></a>
<div class="toast-region" id="toast-region" role="status" aria-live="polite" aria-atomic="true"></div>
"""


def page(ctx, filename, title, description, active, body, scripts=("enquiry-store.js", "ui.js"), extra_head="",
         with_data=True):
    scr = []
    if with_data:
        scr.append("catalogue-data.js")
    scr += list(scripts)
    tags = "\n".join(f'<script src="assets/js/{s}" defer></script>' for s in scr)
    return (head(ctx, filename, title, description, extra_head) + header(ctx, active) +
            f'<main id="main" tabindex="-1">\n{body}\n</main>\n' + footer(ctx) + tags + "\n</body>\n</html>\n")


def json_ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"
