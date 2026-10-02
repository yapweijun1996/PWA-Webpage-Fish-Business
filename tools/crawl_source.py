#!/usr/bin/env python3
"""Audit crawler for https://www.sanyoaqm.com.sg/ (read-only, GET requests only).

Outputs into source-audit/:
  raw-html/<page>.html         exact bytes of every reachable HTML page
  originals/<url path>         exact bytes of every downloadable asset (images, css)
  page-inventory.json          one record per page URL (status, hash, links, images)
  asset-inventory.json         one record per asset URL (status, size, dimensions, sha256)
Run:  python tools/crawl_source.py
"""
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "source-audit")
RAW = os.path.join(OUT, "raw-html")
ORIG = os.path.join(OUT, "originals")
BASE = "https://www.sanyoaqm.com.sg/"
HOST = urlparse(BASE).netloc
SEEDS = [BASE + "index.html"]
# Extra same-domain probes recorded as "probed" (not discovered through links).
PROBES = ["robots.txt", "sitemap.xml", "favicon.ico", "css/sanyo.css"]
IMG_EXT = (".jpg", ".jpeg", ".gif", ".png", ".webp", ".bmp", ".svg", ".ico")

session = requests.Session()
session.headers["User-Agent"] = "SanyoSiteAudit/1.0 (content migration audit; contact: site owner's agent)"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def norm(url):
    url, _ = urldefrag(url)
    p = urlparse(url)
    if p.netloc.lower() in (HOST, "sanyoaqm.com.sg"):
        p = p._replace(scheme="https", netloc=HOST)
    return p.geturl()


def same_domain(url):
    return urlparse(url).netloc.lower() == HOST


def local_path_for(url, root):
    path = urlparse(url).path.lstrip("/") or "index.html"
    path = os.path.normpath(os.path.join(root, *path.split("/")))
    return path


def fetch(url):
    for attempt in range(3):
        try:
            r = session.get(url, timeout=30, allow_redirects=True)
            return r
        except requests.RequestException as e:  # noqa: PERF203
            err = e
            time.sleep(1 + attempt)
    return err


def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(ORIG, exist_ok=True)
    pages, assets = {}, {}
    queue = list(SEEDS)
    seen = set()
    while queue:
        url = norm(queue.pop(0))
        if url in seen:
            continue
        seen.add(url)
        r = fetch(url)
        rec = {"url": url, "captured_at": now()}
        if isinstance(r, Exception):
            rec.update(status="ERROR", error=str(r))
            pages[url] = rec
            continue
        rec.update(
            status=r.status_code,
            final_url=r.url,
            content_type=r.headers.get("Content-Type"),
            last_modified=r.headers.get("Last-Modified"),
            bytes=len(r.content),
            sha256=sha256(r.content),
        )
        if r.status_code != 200 or "html" not in (r.headers.get("Content-Type") or ""):
            pages[url] = rec
            continue
        fname = os.path.basename(urlparse(url).path) or "index.html"
        with open(os.path.join(RAW, fname), "wb") as f:
            f.write(r.content)
        rec["raw_file"] = f"raw-html/{fname}"
        text = r.content.decode("cp1252", errors="replace")
        soup = BeautifulSoup(text, "lxml")
        rec["title"] = soup.title.get_text(strip=True) if soup.title else None
        md = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
        rec["meta_description"] = md.get("content") if md else None
        links, imgs, other = [], [], []
        for a in soup.find_all(["a", "area"], href=True):
            tgt = norm(urljoin(url, a["href"].strip()))
            if tgt.startswith(("mailto:", "tel:", "javascript:")):
                continue
            links.append({"href": a["href"].strip(), "resolved": tgt, "text": a.get_text(" ", strip=True)[:120]})
            if same_domain(tgt):
                if tgt.lower().endswith(IMG_EXT):
                    imgs.append({"src": a["href"].strip(), "resolved": tgt, "via": "a[href]"})
                elif tgt not in seen:
                    queue.append(tgt)
        for tag in soup.find_all(True):
            for attr in ("src", "background"):
                if tag.has_attr(attr) and tag.name != "script":
                    val = tag[attr].strip()
                    if not val:
                        continue
                    tgt = norm(urljoin(url, val))
                    imgs.append({"src": val, "resolved": tgt, "via": f"{tag.name}[{attr}]",
                                 "width_attr": tag.get("width"), "height_attr": tag.get("height"),
                                 "alt": tag.get("alt")})
            if tag.name == "link" and tag.get("href"):
                other.append(norm(urljoin(url, tag["href"])))
            if tag.name == "script" and tag.get("src"):
                other.append(norm(urljoin(url, tag["src"])))
        # Image-like references that appear only inside HTML comments (legacy leftovers).
        live = {i["src"] for i in imgs}
        commented = []
        for m in re.findall(r"""(?:src|background)\s*=\s*["']?([^"'\s>]+\.(?:jpg|jpeg|gif|png))""", text, re.I):
            if m not in live and m not in commented:
                commented.append(m)
        rec["commented_out_images"] = commented
        rec["links"] = links
        rec["images"] = imgs
        rec["other_resources"] = other
        rec["text_length"] = len(soup.get_text(" ", strip=True))
        pages[url] = rec
        for i in imgs:
            if same_domain(i["resolved"]):
                a = assets.setdefault(i["resolved"], {"url": i["resolved"], "referenced_by": set()})
                a["referenced_by"].add(url)
                a.pop("commented_out_only", None)
                a["live_reference"] = True
        for c in commented:
            t = norm(urljoin(url, c))
            if same_domain(t):
                a = assets.setdefault(t, {"url": t, "referenced_by": set()})
                a["referenced_by"].add(url)
                a["commented_out_only"] = True
        for o in other:
            if same_domain(o):
                assets.setdefault(o, {"url": o, "referenced_by": set()})["referenced_by"].add(url)
        time.sleep(0.3)

    # Probes
    for p in PROBES:
        u = BASE + p
        if u in assets or u in pages:
            continue
        assets.setdefault(u, {"url": u, "referenced_by": set(), "probed": True})

    # CSS url() discovery
    for u in list(assets):
        if u.lower().endswith(".css"):
            r = fetch(u)
            if not isinstance(r, Exception) and r.status_code == 200:
                for m in re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", r.text):
                    t = norm(urljoin(u, m))
                    if same_domain(t):
                        assets.setdefault(t, {"url": t, "referenced_by": set()})["referenced_by"].add(u)

    # Download assets
    for u, rec in sorted(assets.items()):
        r = fetch(u)
        rec["captured_at"] = now()
        rec["referenced_by"] = sorted(rec["referenced_by"])
        if isinstance(r, Exception):
            rec.update(status="ERROR", error=str(r))
            continue
        rec.update(status=r.status_code, content_type=r.headers.get("Content-Type"),
                   last_modified=r.headers.get("Last-Modified"))
        if r.status_code != 200:
            continue
        dest = local_path_for(u, ORIG)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(r.content)
        rec.update(local_path=os.path.relpath(dest, OUT).replace(os.sep, "/"), bytes=len(r.content),
                   sha256=sha256(r.content))
        if u.lower().endswith(IMG_EXT) and (r.headers.get("Content-Type") or "").startswith("image"):
            try:
                with Image.open(dest) as im:
                    rec.update(width=im.width, height=im.height, format=im.format,
                               frames=getattr(im, "n_frames", 1))
            except Exception as e:  # noqa: BLE001
                rec["image_error"] = str(e)
        time.sleep(0.15)

    with open(os.path.join(OUT, "page-inventory.json"), "w", encoding="utf-8") as f:
        json.dump(sorted(pages.values(), key=lambda x: x["url"]), f, indent=1, ensure_ascii=False)
    with open(os.path.join(OUT, "asset-inventory.json"), "w", encoding="utf-8") as f:
        json.dump(sorted(assets.values(), key=lambda x: x["url"]), f, indent=1, ensure_ascii=False)

    ok = [p for p in pages.values() if p.get("status") == 200]
    bad = [p for p in pages.values() if p.get("status") != 200]
    aok = [a for a in assets.values() if a.get("status") == 200]
    abad = [a for a in assets.values() if a.get("status") != 200]
    print(f"pages: {len(ok)} ok, {len(bad)} not ok")
    for p in bad:
        print("  PAGE NOT OK:", p["url"], p.get("status"))
    print(f"assets: {len(aok)} ok, {len(abad)} not ok")
    for a in abad:
        print("  ASSET NOT OK:", a["url"], a.get("status"), "(probe)" if a.get("probed") else "")


if __name__ == "__main__":
    sys.exit(main())
