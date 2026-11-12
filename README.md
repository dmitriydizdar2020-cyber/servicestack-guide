# ServiceStack Journal — AffiliateOS pilot

Independent English-language buyer guides, original decision tools and transparent software comparisons for local service businesses. This is the first owner-controlled pilot, separate from BucharestUA.

**Status as of 12 November 2026:** Four articles and homepage/about are recorded as QA-approved and indexable in the repository. The fifth article (SITE123 vs Systeme.io) is publicly accessible but **noindex, pending separate editorial QA**. This does not establish that Google has indexed these URLs or that traffic/revenue exists.

- Public pilot: https://dmitriydizdar2020-cyber.github.io/servicestack-guide/
- [Editorial standards](about.html), [daily production standard](orchestrator/DAILY_PUBLISHING_STANDARD.md), and [canonical state](orchestrator/state/tasks.json).
- Source QA: `python3 scripts/check_site.py`
- Indexable-only sitemap validation: `python3 scripts/build_sitemap.py --check`
- Actual browser testing (Playwright in Actions): `python3 scripts/browser_smoke.py`

## Release safeguards

1. Produce a useful, original, source-verified buyer article; label images and commercial relationships.
2. Send to **independent QAD-01**. Never self-approve. Keep `noindex` until a real independent PASS.
3. OPS releases only approved pages, verifies deploy and updates canonical sitemap entries.
4. Measure actual GSC clicks/impressions, verified merchant conversions and **paid** affiliate cash separately from plans.
5. No external spending without explicit owner approval; current cap **$0**.

Two finite scheduled ChatGPT tasks handle production and independent QA; GitHub Actions runs deterministic checks and is **not** an AI content worker or independent editorial reviewer.

Search rankings, merchant eligibility, and paid commissions remain unverified until backed by external evidence.
