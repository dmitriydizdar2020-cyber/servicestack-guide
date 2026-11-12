#!/usr/bin/env python3
"""Flag affiliate landing pages masquerading as ordinary product documentation.

Text-level safety net; independent source-to-claim review remains mandatory.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import sys

ROOT = Path(__file__).resolve().parents[1]
BAD_PATH_SEGMENTS = {"affiliate", "affiliates", "affiliate-program", "affiliate-programs", "referral-program"}
TRACKING_PARAMS = {"aff", "affiliate", "affiliate_id", "ref", "referral", "sa", "partner_id"}

class SourcesParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.urls = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "ol" and "sources" in (attrs.get("class") or "").split():
            self.depth += 1
        elif tag == "ol" and self.depth:
            self.depth += 1
        if tag == "a" and self.depth:
            href = attrs.get("href", "")
            if href.startswith(("https://", "http://")):
                self.urls.append(href)
    def handle_endtag(self, tag):
        if tag == "ol" and self.depth:
            self.depth -= 1

def risky_sources(html: str) -> list[str]:
    parser = SourcesParser()
    parser.feed(html)
    issues = []
    for url in parser.urls:
        parts = urlsplit(url)
        segments = set(parts.path.strip("/").lower().split("/"))
        params = set(parse_qs(parts.query))
        if segments & BAD_PATH_SEGMENTS or params & TRACKING_PARAMS:
            issues.append(url)
    return issues

def main():
    issues = []
    for page in sorted((ROOT / "articles").glob("*.html")):
        for url in risky_sources(page.read_text(encoding="utf-8")):
            issues.append(f"{page.relative_to(ROOT)}: affiliate/referral landing page in product SOURCE list: {url}")
    if issues:
        print("\n".join(issues), file=sys.stderr)
        print("SOURCE GATE FAILED: official feature claims need product/help sources; commercial terms should be explicitly labeled and reviewed.", file=sys.stderr)
        return 1
    print("Source-link heuristic PASS (NOT independent factual review)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
