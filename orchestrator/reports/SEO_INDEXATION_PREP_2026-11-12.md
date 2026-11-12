# SEO launch staging — 2026-11-12

GSC ownership: user-confirmed in Google Search Console. HTML verification meta present on homepage.
Canonical site: https://dmitriydizdar2020-cyber.github.io/servicestack-guide/

At this stage all six HTML pages still carry noindex,nofollow until independent QAD acceptance and per-page OPS release.
A baseline sitemap.xml is deliberately EMPTY because zero pages have QA PASS. Submitting an empty sitemap to Google is NOT the next step.
scripts/build_sitemap.py fails CI if noindex is removed before an independent QAD PASS recorded in canonical orchestrator/state/tasks.json.
After a page is cleared and noindex is lifted, run python3 scripts/build_sitemap.py to add its canonical URL.
The project-local robots.txt is for transparency only: crawlers seek robots.txt from the github.io site root, not the project subdirectory.

Browser-smoke CI covers six pages at widths 390/768/1280/1440, images, overflow, JS errors, and interactive tools. CI success is not human visual or factual QA.
The old ART-0001 source defect was repaired in current main with directly relevant official Hostinger builder support docs, but QAD must verify and re-accept before release.
No external paid services enabled. No affiliate tracking added without account/payout confirmation and contextual editorial disclosures.

When at least one page passes independent QAD and is released with noindex removed, ensure that the live sitemap has its URL. Then owner: GSC > Sitemaps > sitemap.xml > Submit; GSC > URL Inspection > paste canonical > Test Live URL > Request Indexing.
