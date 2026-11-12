#!/usr/bin/env python3
"""Real Chromium smoke tests of responsive layout and interactive tools.
Browser tests do not replace independent factual/visual editorial QA.
"""
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import sys
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['index.html', 'about.html',
 'articles/website-builder-landscaping-business.html',
 'articles/landscaping-quote-request-form.html',
 'articles/landscaping-crm-guide.html',
 'articles/landscaping-estimate-follow-up-templates.html',
 'articles/site123-vs-systeme-io-service-business.html']
VIEWPORTS = (390, 768, 1280, 1440)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

@contextmanager
def server():
    httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield f'http://127.0.0.1:{httpd.server_port}/'
    finally:
        httpd.shutdown()
        httpd.server_close()

def check_tool(page, path):
    if path.endswith('website-builder-landscaping-business.html'):
        old = page.locator('#total').inner_text()
        page.locator('#setup').fill('350')
        new = page.locator('#total').inner_text()
        assert new != old and '1,088' in new, f'Budget calculation: {old} -> {new}'
    elif path.endswith('landscaping-quote-request-form.html'):
        page.locator('#generate').click()
        assert 'LANDSCAPING QUOTE REQUEST FORM' in page.locator('#spec').input_value()
    elif path.endswith('landscaping-crm-guide.html'):
        old = page.locator('#crm-total').inner_text()
        page.locator('#crm-seat-price').fill('30')
        assert page.locator('#crm-total').inner_text() != old, 'CRM budget did not update'
        page.locator('#make-pipeline').click()
        assert 'LANDSCAPING CRM' in page.locator('#pipeline-result').inner_text()
    elif path.endswith('landscaping-estimate-follow-up-templates.html'):
        page.locator('#msg-name').fill('Taylor')
        page.locator('#msg-company').fill('Example Landscape Co')
        page.locator('#make-msg').click()
        output = page.locator('#msg-out').inner_text()
        assert 'Taylor' in output and 'Example Landscape Co' in output

    elif path.endswith('site123-vs-systeme-io-service-business.html'):
        photos = page.locator('.article-body .comparison-figure img')
        assert photos.count() >= 3, 'Guide needs useful in-article visuals, not just a hero'
        assert page.locator('.comparison-hero img').count() == 1, 'Hero photograph missing'
        paid_links = page.locator('a[rel~="sponsored"]')
        assert paid_links.count() == 2, 'Expected exactly two disclosed affiliate CTAs'
        labels = [label.strip().lower() for label in paid_links.all_inner_texts()]
        assert all('affiliate link' not in label and 'referral' not in label for label in labels), f'Unnatural CTA labels: {labels}'
        assert 'commission' in page.locator('.editorial-disclosure').inner_text().lower(), 'Paid relationship not disclosed'
        assert page.locator('meta[name="robots"]').get_attribute('content') == 'noindex,nofollow', 'QA staging page must remain noindex'

def main():
    screenshots = ROOT / 'qa_screenshots'
    screenshots.mkdir(exist_ok=True)
    failures = []
    with server() as base, sync_playwright() as p:
        executable = shutil.which('google-chrome') or shutil.which('chromium')
        browser = p.chromium.launch(headless=True, **({'executable_path': executable} if executable else {}))
        try:
            for width in VIEWPORTS:
                context = browser.new_context(viewport={'width': width, 'height': 960}, device_scale_factor=1)
                for path in PAGES:
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda exc: errors.append(str(exc)))
                    try:
                        response = page.goto(base + path, wait_until='load', timeout=15000)
                        assert response and response.status == 200
                        page.evaluate('async () => { await document.fonts.ready; await Promise.all(Array.from(document.images, async img => { img.loading = "eager"; try { await img.decode(); } catch (e) {} })); }')
                        page.wait_for_timeout(75)
                        scroll = page.evaluate('Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)')
                        assert scroll <= width + 2, f'horizontal overflow {scroll}px at {width}px'
                        assert page.locator('h1').count() == 1, 'H1 count not one'
                        broken = page.eval_on_selector_all('img', '(xs) => xs.filter(x => !x.complete || !x.naturalWidth).map(x => x.getAttribute("src"))')
                        assert not broken, f'broken images: {broken}'
                        check_tool(page, path)
                        assert not errors, f'uncaught JS errors: {errors}'
                        if width in (390, 1280):
                            page.screenshot(path=str(screenshots / f'{Path(path).stem}-{width}.png'), full_page=True)
                        print(f'PASS {width}px {path}: HTTP, layout, images, JS and tools')
                    except Exception as exc:
                        failures.append(f'{width}px {path}: {exc}')
                        print('FAIL '+failures[-1], file=sys.stderr)
                    finally:
                        page.close()
                context.close()
        finally:
            browser.close()
    if failures:
        print(f'Browser smoke FAILED: {len(failures)} cases', file=sys.stderr)
        return 1
    print(f'Browser smoke PASSED: {len(PAGES)} pages × {len(VIEWPORTS)} viewports')
    print('NOT A FACTUAL, COMMERCIAL, OR HUMAN VISUAL EDITORIAL APPROVAL.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
