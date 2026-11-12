#!/usr/bin/env python3
"""Merge Claude Design export zips into the published site in docs/.

Usage:
    python3 tools/update_site.py path/to/Export1.zip [path/to/Export2.zip ...]

What it does:
  1. Extracts each export into docs/, replacing files with the same name.
     (Claude Design names assets by content hash, so updated images get new
     names and never overwrite a different image.)
  2. Drops the export's README.md (it describes the export, not this site).
  3. Rebuilds docs/index.html from docs/Home.dc.html, so the bare domain
     always opens the latest homepage.
  4. Makes sure every page has a viewport tag. Claude Design exports come
     without one, and without it phones report a ~980px window, so each page
     would show its desktop layout instead of its phone artboard.
  5. Checks every link, image and component reference and reports anything
     missing, so a broken page is caught before it is pushed.

It never deletes files. Old, unused assets can be listed with --unused.
"""

import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "docs")

# Files that belong to this site, not to any export. Never overwritten.
PROTECTED = {"CNAME", ".nojekyll", "Library.dc.html", "index.html"}

# Added to the <head> of every full page so phones report their real width
# and each page's width switch shows the phone artboard.
VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1">'

# Tags from the retired phone layer (mobile.css / mobile.js, replaced by the
# phone artboards in Claude Design). Stripped if an old page still has them.
RETIRED_TAGS = (
    '<link rel="stylesheet" href="./mobile.css">\n',
    '<script src="./mobile.js" defer></script>\n',
)


def merge(zip_path):
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zip_path) as z:
            for member in z.namelist():
                target = os.path.realpath(os.path.join(tmp, member))
                if not target.startswith(os.path.realpath(tmp) + os.sep):
                    sys.exit(f"Refusing unsafe path in {zip_path}: {member}")
            z.extractall(tmp)
        copied = 0
        for dirpath, _, files in os.walk(tmp):
            for name in files:
                src = os.path.join(dirpath, name)
                rel = os.path.relpath(src, tmp)
                if rel == "README.md" or rel in PROTECTED:
                    continue
                dst = os.path.join(SITE, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1
        print(f"  {os.path.basename(zip_path)}: {copied} files")


def rebuild_index():
    home = os.path.join(SITE, "Home.dc.html")
    if os.path.exists(home):
        shutil.copy2(home, os.path.join(SITE, "index.html"))


def ensure_viewport():
    """Give every full page a viewport tag, and drop any retired phone-layer tags.

    Only full pages are touched (they contain the scaling "pf-stage"); the
    *-Phone, Slot-*, Annot* and other component files are loaded into those
    pages and must stay as exported.
    """
    changed = []
    for name in sorted(os.listdir(SITE)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(SITE, name)
        text = open(path, encoding="utf-8").read()
        if 'class="pf-stage"' not in text or "<head>" not in text:
            continue
        new = text
        for tag in RETIRED_TAGS:
            new = new.replace(tag, "")
        if 'name="viewport"' not in new:
            new = new.replace("<head>", "<head>\n" + VIEWPORT, 1)
        if new != text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            changed.append(name)
    if changed:
        print(f"Viewport tag checked on: {', '.join(changed)}")


def referenced_files():
    """Map each referenced local file to the pages that reference it."""
    refs = {}
    for name in os.listdir(SITE):
        if not name.endswith(".html"):
            continue
        text = open(os.path.join(SITE, name), encoding="utf-8", errors="ignore").read()
        found = re.findall(r'(?:href|src)="([^"#?]+)', text)
        found += re.findall(r'url\(\s*[\'"]?([^\'")#?]+)', text)  # fonts and CSS images
        found += [n + ".dc.html" for n in re.findall(r'<dc-import name="([^"]+)"', text)]
        for url in found:
            if url.startswith(("http:", "https:", "mailto:", "tel:", "data:", "{{")):
                continue
            refs.setdefault(os.path.normpath(url.removeprefix("./")), set()).add(name)
    return refs


def check():
    missing = {f: pages for f, pages in referenced_files().items()
               if not os.path.exists(os.path.join(SITE, f))}
    if not missing:
        print("All links, images and components resolve.")
        return True
    print("Missing files:")
    for f, pages in sorted(missing.items()):
        print(f"  {f}  (used by {', '.join(sorted(pages))})")
    return False


def list_unused():
    used = set(referenced_files())
    assets = sorted(os.path.join("assets", a) for a in os.listdir(os.path.join(SITE, "assets")))
    unused = [a for a in assets if a not in used]
    print(f"{len(unused)} asset(s) no page references:")
    for a in unused:
        print("  docs/" + a)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("zips", nargs="*", help="Claude Design export .zip files")
    parser.add_argument("--unused", action="store_true", help="list assets no page uses")
    args = parser.parse_args()

    if args.zips:
        print("Merging exports into docs/:")
        for z in args.zips:
            merge(z)
        rebuild_index()
    ensure_viewport()
    if args.unused:
        list_unused()
    sys.exit(0 if check() else 1)


if __name__ == "__main__":
    main()
