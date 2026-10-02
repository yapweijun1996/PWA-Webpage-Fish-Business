#!/usr/bin/env python3
"""Create Sanyo-Aquarium-Modern-Website-AI.zip (project root) and verify its integrity.

Includes the ready-to-serve site, sources, data, audit evidence, tools and docs. Excludes caches, .git, the zip itself and
anything that can be reinstalled or regenerated as junk (__pycache__, *.pyc, OS files). No secrets exist in the tree.
Run:  python tools/package_zip.py
"""
import hashlib
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_NAME = "Sanyo-Aquarium-Modern-Website-AI.zip"
OLD_ZIP_NAME = "Sanyo-Aquarium-Modern-Website.zip"
TOP = "Sanyo-Aquarium-Modern-Website"
INCLUDE = ["README.md", ".gitignore", "site", "src", "data", "generated", "source-audit", "tools", "docs"]
SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".pytest_cache"}
SKIP_FILES = {".DS_Store", "Thumbs.db", ZIP_NAME, OLD_ZIP_NAME}


def iter_files():
    for item in INCLUDE:
        path = os.path.join(ROOT, item)
        if os.path.isfile(path):
            yield path
        elif os.path.isdir(path):
            for dp, dns, fns in os.walk(path):
                dns[:] = sorted(d for d in dns if d not in SKIP_DIRS)
                for fn in sorted(fns):
                    if fn in SKIP_FILES or fn.endswith((".pyc", ".tmp", ".log")):
                        continue
                    yield os.path.join(dp, fn)


def main():
    out = os.path.join(ROOT, ZIP_NAME)
    if os.path.exists(out):
        os.remove(out)
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in iter_files():
            arc = TOP + "/" + os.path.relpath(f, ROOT).replace(os.sep, "/")
            z.write(f, arc)
            n += 1
    with zipfile.ZipFile(out) as z:
        bad = z.testzip()
    h = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"{ZIP_NAME}: {n} files, {os.path.getsize(out) / 1e6:.2f} MB, integrity {'OK' if bad is None else 'FAILED at ' + bad}")
    print("sha256:", h)
    return 0 if bad is None else 1


if __name__ == "__main__":
    sys.exit(main())
