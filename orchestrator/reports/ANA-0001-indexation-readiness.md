# ANA-0001 — Indexation and evidence measurement readiness
Prepared 2026-11-12, ANA-01. **Preparation only; no indexing action or QA approval.** No paid services.

## Release and indexation gate (per URL)
1. Confirm the precise canonical production URL and a distinct independent QAD-01 PASS with dated review evidence and artifact SHA. GitHub static CI success is NOT editorial PASS.
2. Confirm source citations, current vendor facts, disclosures, navigation, interactive functionality, mobile browser review, and actual deployed response. Mark untested items NOT TESTED; hold `noindex` until all gates pass.
3. OPS-01 may then remove `noindex,nofollow` from only the individually passed page; verify published HTML and final HTTP response, canonical tag (self-referential if applicable), links, and absence of accidental blocking. Record release commit, deploy run URL, UTC timestamp, and exact URL. Do not bulk-unblock other pages.
4. Verify ownership of the exact GitHub Pages property in Google Search Console (GSC) through owner-controlled access. Ownership is **UNKNOWN**; no account actions authorized. If available, inspect URL Inspection for the exact deployed URL; request indexing once if appropriate. Requests are not guarantees. Submit a sitemap only when it contains QA-approved indexable URLs; ensure absolute URLs, accurate status and lastmod. Do not manufacture a sitemap listing noindex pages.
5. Record observed GSC indexing status, impressions and clicks with property, date range and export/screenshot; distinguish crawl, discovery, indexed and ranking states. GSC data can lag. A Pages deploy alone does not prove indexing.

## Measurement ledger (record each observation with source, window, timestamp)
| Metric | Current status | Evidence required |
|---|---|---|
| QA-passed indexable URLs | **0 confirmed in canonical task state** | Independent per-URL PASS and deployed page check |
| GSC verified property | UNKNOWN | GSC property ownership proof |
| GSC indexed URLs / impressions / clicks | UNKNOWN | GSC Performance and URL Inspection data |
| Actual site sessions | UNKNOWN | Consented/appropriate first-party analytics export, if deployed |
| Outbound merchant clicks | UNKNOWN | Actual click logs/approved affiliate dashboard; no fake event counts |
| Approved affiliate orders and commissions | UNKNOWN | Partner dashboard report and approval status |
| Affiliate payout received | **Not confirmed** | Payout statement and owner reconciliation |
| External spend | **$0 authorized ceiling** | Owner approval plus real expense ledger; authorization is not proof of incurred $0 |
| Revenue, profit, ROI | UNKNOWN | Paid cash minus verified expenses; do not substitute projections |

## Current repository evidence, checked 2026-11-12
- `index.html` contains `<meta name="robots" content="noindex,nofollow">`; this must stay until separate QAD PASS.
- Canonical `orchestrator/state/tasks.json`: ART-0001, ART-0002 and SITE-0001 await QAD-01. No independent PASS recorded.
- GitHub Actions for commit `54842d0bbeb6733d8a51133b4eac1506ee1dfb87`:
  - [Orchestrator checkup: success](https://github.com/dmitriydizdar2020-cyber/servicestack-guide/actions/runs/43133600160)
  - [Site quality: success](https://github.com/dmitriydizdar2020-cyber/servicestack-guide/actions/runs/43133600153)
  - [Pages build: success](https://github.com/dmitriydizdar2020-cyber/servicestack-guide/actions/runs/43133599071)
- These CI checks do NOT demonstrate responsive manual QA, search indexation, conversions or partner payouts.

## Official guidance to verify when account access exists
- Google Search Central: [Ask Google to recrawl URLs](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl-urls)
- Google Search Central: [Robots meta tag specifications](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)
- Google Search Central: [Sitemaps overview](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)
- Search Console Help: [Performance report](https://support.google.com/webmasters/answer/7576553)

These links are documentation references, not evidence of any live GSC action or connected property.

## Handoff
ANA-0001 | ANA-01 -> CEO-01 / OPS-01 (conditional) | source_commit: see creating commit | status: measurement plan complete, release blocked by QAD | artifact: orchestrator/reports/ANA-0001-indexation-readiness.md | evidence: canonical tasks and GitHub CI above | tests: source file and Actions PASS; GSC/mobile/partner dashboards NOT TESTED | spend: no purchases or paid services | blocker: independent per-page QA and GSC property verification | next: QAD-01 reviews queued P0 pages, OPS-01 executes URL-specific release only after PASS | real_run_id: production-20261112-0820
