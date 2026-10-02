#!/usr/bin/env python3
"""Static QA of the built site (no browser): links, assets, ids, headings, titles, labels, JSON-LD.

Run after tools/build_site.py:   python tools/qa_static.py
Writes docs/qa/static-checks.json. Exit code 1 if anything fails.
"""
import glob
import json
import os
import re
import sys
from urllib.parse import urldefrag

from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
results = []


def check(name, ok, detail=""):
    results.append({"check": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))


pages = sorted(glob.glob(os.path.join(SITE, "*.html")))
docs = {os.path.basename(p): BeautifulSoup(open(p, encoding="utf-8").read(), "lxml") for p in pages}
ids = {n: {e["id"] for e in d.find_all(id=True)} for n, d in docs.items()}

# links / assets ------------------------------------------------------------------------------------------
broken, frag_bad = [], []
for n, d in docs.items():
    for tag, attr in (("a", "href"), ("img", "src"), ("link", "href"), ("script", "src")):
        for e in d.find_all(tag, **{attr: True}):
            v = e[attr]
            if v.startswith(("http://", "https://", "mailto:", "tel:", "data:", "javascript:")):
                continue
            path, frag = urldefrag(v)
            target = n if not path else path
            if not os.path.exists(os.path.join(SITE, target.replace("/", os.sep))):
                broken.append((n, v))
            elif frag and target.endswith(".html") and frag not in ids.get(target, set()):
                if n == "enquiry.html" and frag in ("items", "details", "review"):
                    continue  # hash-routed wizard steps handled by enquiry.js (documented)
                frag_bad.append((n, v))
check(f"all local href/src targets exist ({len(docs)} pages)", not broken, str(broken[:5]))
check("all #fragment links point to an existing id", not frag_bad, str(frag_bad[:5]))

# JS references to assets ----------------------------------------------------------------------------------
js_bad = []
data_js = open(os.path.join(SITE, "assets", "js", "catalogue-data.js"), encoding="utf-8").read()
for m in re.findall(r'"img":"(assets/[^"]+)"', data_js):
    if not os.path.exists(os.path.join(SITE, m)):
        js_bad.append(m)
check("every image path inside catalogue-data.js exists", not js_bad, str(js_bad[:3]))
css = open(os.path.join(SITE, "assets", "css", "styles.css"), encoding="utf-8").read()
check("CSS has no external url() dependencies", not re.search(r"url\(\s*['\"]?https?:", css))

# per-page structure --------------------------------------------------------------------------------------
struct = []
for n, d in docs.items():
    t = d.title.get_text(strip=True) if d.title else ""
    md = d.find("meta", attrs={"name": "description"})
    h1 = d.find_all("h1")
    heads = [int(h.name[1]) for h in d.find_all(re.compile(r"^h[1-6]$"))]
    skips = [(a, b) for a, b in zip(heads, heads[1:]) if b > a + 1]
    dup_ids = [i for i in ids[n] if len(d.find_all(id=i)) > 1]
    imgs_noalt = [i.get("src") for i in d.find_all("img") if i.get("alt") is None]
    vp = d.find("meta", attrs={"name": "viewport"})
    problems = []
    if not t or len(t) > 70:
        problems.append(f"title len {len(t)}")
    if not md or not (20 <= len(md.get("content", "")) <= 320):
        problems.append("meta description missing/odd length")
    if len(h1) != 1:
        problems.append(f"{len(h1)} h1")
    if skips:
        problems.append(f"heading skips {skips[:2]}")
    if dup_ids:
        problems.append(f"dup ids {dup_ids[:2]}")
    if imgs_noalt:
        problems.append(f"img without alt {imgs_noalt[:2]}")
    if d.html.get("lang") != "en":
        problems.append("lang")
    if not vp:
        problems.append("viewport")
    if not d.find("main", id="main"):
        problems.append("no main#main")
    if not d.find("a", class_="skip-link"):
        problems.append("no skip link")
    struct.append((n, problems))
check("every page: <title>, description, one <h1>, no heading-level skips, unique ids, alt on all images, lang, viewport, main, skip link",
      not any(p for _, p in struct), str([(n, p) for n, p in struct if p][:6]))
titles = [d.title.get_text(strip=True) for d in docs.values()]
check("page titles are unique", len(set(titles)) == len(titles), str([t for t in titles if titles.count(t) > 1]))

# forms -------------------------------------------------------------------------------------------------
unlabeled = []
for n, d in docs.items():
    for e in d.find_all(["input", "select", "textarea"]):
        if e.get("type") in ("hidden", "submit", "reset"):
            continue
        eid = e.get("id")
        if not (eid and d.find("label", attrs={"for": eid})) and not e.get("aria-label"):
            unlabeled.append((n, eid or e.get("name")))
check("every form control has a <label for> or aria-label (static markup)", not unlabeled, str(unlabeled[:5]))

# structured data ---------------------------------------------------------------------------------------
ld_bad, ld_n = [], 0
for n, d in docs.items():
    for s in d.find_all("script", type="application/ld+json"):
        ld_n += 1
        try:
            j = json.loads(s.string)
            assert j["@type"] == "Organization" and "url" not in j and "aggregateRating" not in j and "review" not in j
        except Exception as ex:  # noqa: BLE001
            ld_bad.append((n, str(ex)))
check(f"JSON-LD ({ld_n} blocks) parses, is Organization only, with no invented url/ratings", not ld_bad and ld_n >= 1, str(ld_bad))
ed = json.load(open(os.path.join(ROOT, "data", "editorial.json"), encoding="utf-8"))
if not ed["site"].get("site_url"):
    check("no canonical/og:url tags are emitted while site_url is unset (no invented deployed URL)",
          not any(d.find("link", rel="canonical") or d.find("meta", property="og:url") for d in docs.values()))
    check("robots.txt exists; sitemap.xml is not generated without site_url",
          os.path.exists(os.path.join(SITE, "robots.txt")) and not os.path.exists(os.path.join(SITE, "sitemap.xml")))

# tel / mailto ------------------------------------------------------------------------------------------
tel_bad = []
for n, d in docs.items():
    for a in d.find_all("a", href=re.compile(r"^tel:")):
        if a["href"] != "tel:+6564813111":
            tel_bad.append((n, a["href"]))
    for a in d.find_all("a", href=re.compile(r"^mailto:")):
        if a["href"] not in ("mailto:sales@sanyoaqm.com.sg", "mailto:info@sanyoaqm.com.sg"):
            tel_bad.append((n, a["href"]))
check("all tel:/mailto: links use only the published number/addresses", not tel_bad, str(tel_bad[:4]))

# size / hygiene --------------------------------------------------------------------------------------------
files = [f for f in glob.glob(os.path.join(SITE, "**", "*.*"), recursive=True) if os.path.isfile(f)]
total = sum(os.path.getsize(f) for f in files)
big = [(os.path.relpath(f, SITE), os.path.getsize(f)) for f in files if os.path.getsize(f) > 150_000]
check(f"site is lightweight (total {total / 1e6:.2f} MB; no single file > 150 KB)", total < 3_000_000 and not big, str(big))
stray = [f for f in files if re.search(r"(\.map|\.log|\.tmp|\.DS_Store|Thumbs\.db)$", f)]
check("no debug/temp files in site/", not stray, str(stray))

os.makedirs(os.path.join(ROOT, "docs", "qa"), exist_ok=True)
with open(os.path.join(ROOT, "docs", "qa", "static-checks.json"), "w", encoding="utf-8") as f:
    json.dump({"checks": results, "passed": sum(r["pass"] for r in results), "total": len(results)}, f, indent=1, ensure_ascii=False)
fails = [r for r in results if not r["pass"]]
print(f"\n{len(results) - len(fails)}/{len(results)} checks passed")
sys.exit(1 if fails else 0)
