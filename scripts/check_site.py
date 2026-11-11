#!/usr/bin/env python3
"""Basic zero-dependency checks for ServiceStack Guide pages.
Pass of this script does not constitute independent editorial or browser QA.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(ROOT.rglob("*.html"))
FAILURES = []


class PageParser(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.h1s = 0
        self.images = 0
        self.viewport = False
        self.robots = ""
        self.description = False
        self.links = []
        self.has_affiliate_disclosure = False

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "h1":
            self.h1s += 1
        if tag == "meta":
            name = (data.get("name") or "").lower()
            if name == "viewport" and data.get("content"):
                self.viewport = True
            if name == "description" and data.get("content"):
                self.description = True
            if name == "robots":
                self.robots = data.get("content", "").lower()
        if tag == "img":
            self.images += 1
            if not (data.get("alt") or "").strip():
                FAILURES.append(f"{self.path}: image missing meaningful alt")
        if tag in ("a", "img", "script", "link"):
            attr = {"a": "href", "img": "src", "script": "src", "link": "href"}[tag]
            url = data.get(attr)
            if url:
                self.links.append((tag, url))
        if tag == "a" and data.get("target") == "_blank":
            rel = (data.get("rel") or "").split()
            if "noopener" not in rel:
                FAILURES.append(f"{self.path}: target blank missing rel=noopener")

    def handle_data(self, data):
        if "affiliate" in data.lower() and "commission" in data.lower():
            self.has_affiliate_disclosure = True


def check(path):
    relative = path.relative_to(ROOT)
    parser = PageParser(relative)
    raw = path.read_text(encoding="utf-8")
    parser.feed(raw)
    if parser.h1s != 1:
        FAILURES.append(f"{relative}: expected one h1, got {parser.h1s}")
    if not parser.viewport:
        FAILURES.append(f"{relative}: missing responsive viewport")
    if not parser.description:
        FAILURES.append(f"{relative}: missing meta description")
    for kind, href in parser.links:
        u = urlsplit(href)
        if u.scheme or href.startswith("//") or href.startswith(("mailto:", "tel:", "#", "data:")):
            continue
        resolved = unquote(u.path)
        if not resolved:
            continue
        target = ((ROOT / resolved.lstrip("/")) if resolved.startswith("/") else (path.parent / resolved)).resolve()
        if ROOT not in target.parents and target != ROOT:
            FAILURES.append(f"{relative}: path traversal {href}")
            continue
        if not target.exists():
            FAILURES.append(f"{relative}: missing local asset/link {href}")
    if (ROOT / "PRODUCTION_READY").exists() and "noindex" in parser.robots:
        FAILURES.append(f"{relative}: PRODUCTION_READY set but noindex still present")


if not PAGES:
    FAILURES.append("No HTML pages found")
else:
    for page in PAGES:
        check(page)

if FAILURES:
    print("Static QA FAILED")
    for err in FAILURES:
        print(" -", err)
    sys.exit(1)
print(f"Static QA PASSED: {len(PAGES)} HTML pages, internal assets/paths and basic metadata.")
print("Independent factual, responsive visual and affiliate-link audits remain separately required.")
