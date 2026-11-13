#!/usr/bin/env python3
"""Structural completeness gate, not a replacement for independent reader/claim QA.

Avoids publishing empty, thin, or inaccessible shells to meet an article quota.
Minimum length alone is NOT an SEO or quality guarantee.
"""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
MIN_EXPLANATORY_WORDS=500
MIN_SECTION_HEADINGS=4
MIN_DOCUMENTED_OUTBOUND_REFERENCES=2
FORBIDDEN_PLACEHOLDERS=("lorem ipsum","[todo]","tbd:","insert affiliate link here")

class ContentParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.body_depth=0
        self.in_script=0
        self.in_style=0
        self.words=[]
        self.h2=0
        self.refs=set()
        self.images=0
        self.captions=0
        self.disclosure=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        cls=(a.get("class") or "").split()
        if tag=="script":self.in_script+=1
        if tag=="style":self.in_style+=1
        if "editorial-disclosure" in cls:self.disclosure=True
        if tag=="div" and "article-body" in cls:
            self.body_depth+=1
            return
        if self.body_depth:
            if tag=="div":self.body_depth+=1
            if tag=="h2":self.h2+=1
            if tag=="a":
                href=a.get("href","")
                parsed=urlsplit(href)
                if parsed.scheme=="https" and parsed.netloc:
                    self.refs.add(parsed.netloc.lower()+parsed.path)
    def handle_endtag(self,tag):
        if self.body_depth and tag=="div":self.body_depth-=1
        if tag=="script" and self.in_script:self.in_script-=1
        if tag=="style" and self.in_style:self.in_style-=1
    def handle_data(self,data):
        if self.body_depth and not self.in_script and not self.in_style:
            self.words.extend(re.findall(r"\b[\w'-]+\b",data))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
    # Count media/captions throughout article, not only the prose container.
    def handle_entityref(self,name):pass

def check_article(raw,path="article.html"):
    parser=ContentParser()
    parser.feed(raw)
    issues=[]
    # image and caption may lie outside .article-body as cover art.
    images=len(re.findall(r"<img\b",raw,re.I))
    captions=len(re.findall(r"<figcaption\b",raw,re.I))
    if len(parser.words)<MIN_EXPLANATORY_WORDS:
        issues.append(f"{path}: body is only {len(parser.words)} words, fewer than {MIN_EXPLANATORY_WORDS} meaningful words")
    if parser.h2<MIN_SECTION_HEADINGS:
        issues.append(f"{path}: only {parser.h2} H2 sections; draft may be incomplete")
    if len(parser.refs)<MIN_DOCUMENTED_OUTBOUND_REFERENCES:
        issues.append(f"{path}: fewer than {MIN_DOCUMENTED_OUTBOUND_REFERENCES} distinct external source references in article body")
    if images<1 or captions<1:
        issues.append(f"{path}: article requires a meaningful image and explanatory caption")
    if not parser.disclosure:
        issues.append(f"{path}: missing visible editorial/commercial disclosure")
    lower=raw.lower()
    for marker in FORBIDDEN_PLACEHOLDERS:
        if marker in lower:
            issues.append(f"{path}: unresolved placeholder {marker}")
    return issues

def main():
    errors=[]
    files=sorted((ROOT/"articles").glob("*.html"))
    if not files:
        errors.append("No articles found")
    for path in files:
        errors.extend(check_article(path.read_text(encoding="utf-8"),path.name))
    if errors:
        for message in errors:print("FAIL",message,file=sys.stderr)
        return 1
    print(f"Structural article gate PASS: {len(files)} article(s), meaningful structure, source references, image/caption and disclosure.")
    print("NOT an independent check of usefulness, fact accuracy, originality, licenses or commercial eligibility.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
