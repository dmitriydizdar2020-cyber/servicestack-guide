#!/usr/bin/env python3
"""Generate sitemap from independently QA-cleared, indexable pages only.

On a GitHub Pages project URL, robots.txt under /servicestack-guide/ is
informational; crawler robots.txt is resolved at the host root instead.
"""
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://dmitriydizdar2020-cyber.github.io/servicestack-guide/'

class Metadata(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.robots = []
        self.canonical = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'meta' and (d.get('name') or '').lower() == 'robots':
            self.robots.append((d.get('content') or '').lower())
        if tag == 'link' and 'canonical' in (d.get('rel') or '').lower().split():
            self.canonical.append(d.get('href') or '')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    state = json.loads((ROOT / 'orchestrator/state/tasks.json').read_text(encoding='utf-8'))
    approved = set()
    for task in state['tasks']:
        qa = task.get('qa', {})
        if (task.get('status') in {'qa_passed', 'published'}
                and qa.get('decision') == 'PASS'
                and qa.get('reviewer_role') == 'QAD-01'
                and qa.get('evidence')):
            approved.add(task['artifact_path'])
            if task['id'] == 'SITE-0001':
                approved.add('about.html') # Homepage task explicitly covers both pages.
    urls = []
    for page in [ROOT / 'index.html', ROOT / 'about.html', *sorted((ROOT / 'articles').glob('*.html'))]:
        relative = page.relative_to(ROOT).as_posix()
        meta = Metadata()
        meta.feed(page.read_text(encoding='utf-8'))
        if len(meta.canonical) != 1:
            raise SystemExit(f'{relative}: expected exactly one canonical URL')
        canonical = meta.canonical[0]
        if not canonical.startswith(SITE) or urlsplit(canonical).query or urlsplit(canonical).fragment:
            raise SystemExit(f'{relative}: invalid canonical URL: {canonical}')
        if any('noindex' in x for x in meta.robots):
            continue
        if relative not in approved:
            raise SystemExit(f'{relative}: noindex removed without independent QA PASS')
        urls.append(canonical)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += ''.join(f'  <url><loc>{escape(u)}</loc></url>\n' for u in urls)
    xml += '</urlset>\n'
    dest = ROOT / 'sitemap.xml'
    if args.check:
        if not dest.exists() or dest.read_text(encoding='utf-8') != xml:
            raise SystemExit('sitemap.xml is out of sync with actual QA-approved, indexable pages')
    else:
        dest.write_text(xml, encoding='utf-8')
    print(f'Sitemap {"verified" if args.check else "written"}: {len(urls)} indexable, QA-approved URLs')
    if not urls:
        print('EMPTY MAP: Do not submit to Search Console until QA clears at least one page.')

if __name__ == '__main__':
    main()
