# AffiliateOS — Portfolio affiliate strategy and operating contract v1
Date: 2026-11-13 (Europe/Bucharest). Owner directive. **Design specification only; autonomous multi-agent runtime NOT deployed.**

## Mission and scale
Build a diversified, US-first, helpful affiliate publishing portfolio. Target 15–20 new topical sites/month, each with 50–70 original buyer-helpful pages, then reinvest editorial capacity into winners. No revenue or ranking guarantee. Existing ServiceStack articles remain governed by current independent QA; no blanket removal of noindex. Only authorized repository dmitriydizdar2020-cyber/servicestack-guide; never touch BucharestUA. No outside account creation, domain, paid API, ads, or other spending; $0 until verified first affiliate payout and later explicit owner budget.

## Candidate merchant research queue — NOT approved, NOT enrolled
Candidate brands to verify individually with dated official program pages and written terms, not evidence of active affiliation:
1. Amazon Associates — relevant physical product guides, commission/category and US enrollment checks.
2. Impact — network marketplace; individual advertiser terms and approval required.
3. CJ Affiliate — network marketplace; individual advertiser approval required.
4. Awin — network marketplace; country and advertiser requirements.
5. PartnerStack — B2B SaaS offers; each program separately approved.
6. Shopify affiliate — commerce education, eligibility and claims checks.
7. Semrush affiliate — SEO/software buyer guides, current program terms.
8. HubSpot affiliate — CRM/marketing buyer guides, current eligibility.
9. Fiverr affiliate — freelancer/service buying guides, attribution terms.
10. Canva affiliate/creator/referral opportunities — verify whether a qualifying active paid affiliate offer exists; do not assume.
11. NordVPN affiliate — security/travel context, substantiated claims only.
12. Hostinger affiliate — hosting buyer guides, pricing and disclosure.
13. Booking.com affiliate/partner program — travel content, access and terms.
14. GetYourGuide partner program — travel activities, eligibility.
15. Coursera affiliate — education, qualifying courses and terms.

**All 15 are research candidates, not verified currently open programs or usable referral links.** Networks are not individual merchant offers. For each: official terms URL + retrieval date; acceptance status; US buyer geo; owner publisher residency eligibility; commission and cookie; excluded traffic/brand bidding; payout threshold/method; tracking test; withdrawal risk; disclosure; contextual fit. Record UNKNOWN until confirmed. No fake links or invented merchant terms. Owner handles any account/KYC/contract approval.

## Editorial and SEO/GEO protocol
- Niche strategist discovers query clusters from real buyer jobs and verifiable search evidence; no invented volume or competition metrics. Map site -> audience -> 50–70 non-overlapping intents -> article -> merchant match.
- Site portfolios must differ in actual audience, expertise and value, not be cloned domains with near-duplicate articles. Respect Google scaled-content-abuse and doorway policies; do not produce content primarily to manipulate rankings.
- Each article answers the question independently, contains original useful comparison, worked example, checklist or tool, dated primary sources, accurate pros/cons, honest limitations and clear authorship.
- Affiliate offers are optional, not mandatory: insert only when genuinely helpful; natural contextual CTA; conspicuous disclosure and rel="sponsored nofollow"; never fabricate tests, endorsements, savings or scarcity.
- Structured data only when accurate and relevant; accessible images with real rights/attribution or labeled original AI illustrations; no fabricated photographs of products or experiences.
- GEO: concise direct answers, well-structured headings, citations, canonical pages and crawlability; do not promise ChatGPT/Google AI citations.

## Roles — finite sequential execution, not phantom workers
CEO-01: strategy, portfolio allocation, stop/go decisions and incident priority.
SID-00: research niches, official affiliate programs and countercases.
ORC-01: canonical queue, dependencies, idempotency and source commit leases.
RES-01 (proposed, not active): evidence capture and claims provenance.
EDT-01: single accountable writer for each article; unique examples and image briefs.
DES-01 (proposed, not active): template and media rights, responsive design.
QAD-01: separately scheduled independent factual, visual, link and disclosure review; sole editorial PASS authority.
OPS-01: deploy only QAD PASS, verify public URLs/canonical/sitemap/browser checks.
ANA-01: GSC/merchant exports, clicks vs conversions vs approved commissions vs cash received.
ECR-01 (proposed, not active): reproduce and fix recurring pipeline defects, regression tests.
Proposed roles confer no execution rights; approved prompts, authority registry, schedules and actual runtime must be implemented and verified before any claim of activation.

## Production state machine
NICHE_RESEARCH -> MERCHANT_ELIGIBILITY -> SITE_BRIEF -> ARTICLE_BRIEF -> DRAFT_COMMITTED_NOINDEX -> AWAITING_QA -> (REWORK | REJECT | PASS) -> OPS_DEPLOY -> LIVE_INDEXABLE -> GSC_DISCOVERED -> VERIFIED_TRAFFIC -> VERIFIED_CONVERSION -> CASH_RECEIVED.
Every transition requires evidence URL/path, timestamp, actor/run ID, source SHA, explicit NOT TESTED fields. GitHub tasks.json remains canonical for current site; design a backward-compatible portfolio registry before migrating. One writer per artifact, atomic non-force branch-head updates, retries with bounded attempts and escalation; no infinite loops or silent failures.

## Throughput and operations
First-month owner target = 750–1,400 *independently approved* pages, ~25–47/day. Existing 5/day producer + separate daily QA are insufficient proof of throughput. Daily ledgers: planned vs actual drafts, PASS, live, indexable, indexing confirmed, failures, reasons, site/merchant attribution. Weekly winner allocation based on real GSC and merchant evidence; freeze weak or low-value clusters. Max two active exploratory venture tests remains until formally revised. No new schedules authorized.

## Owner-only actions
Account registrations, legal/KYC agreements, partner approval, verified referral URLs, Search Console property access/export and any spending approval. The production team may prepare a precise checklist, but must not claim to complete these actions on owner's behalf.

## Immediate executable backlog (not yet completed)
P0: preserve current QA and release gates; identify any deployment incidents.
P1: implement validated portfolio registry and 15-program research evidence table, keeping all statuses UNKNOWN until checked.
P1: choose 2 evidence-supported site pilots and create distinct 50–70-topic maps; measure actual editorial/QA capacity before scaling.
P1: implement portfolio scorecard with missing GSC/merchant exports shown UNKNOWN.
P2: assess runtime options for real autonomous execution under $0 and current access, without assuming GitHub Actions invokes LLMs.

## Current truth
Plan committed only. Merchant program approval: UNKNOWN. 15–20 sites/month: NOT IMPLEMENTED. Autonomous agent collaboration: NOT IMPLEMENTED. GSC, impressions, conversions, cash: UNKNOWN.
