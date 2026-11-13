# AffiliateOS — Hourly Conveyor v1 (13 November 2026)

**Scope**: only `dmitriydizdar2020-cyber/servicestack-guide`; external spend $0. Two independently scheduled, finite ChatGPT jobs orchestrate **nine role contracts**, not nine always-on robots. Scheduler timing may vary. No CI job has authority to approve content or publish automatically.

## Continuous queue without imaginary agents

In Europe/Bucharest:
- **:00 each hour — production/OPS**: first release items already *independently* QA PASS, then repair QA reworks, then produce new source-grounded articles subject to queue pressure and the **five new drafts/day target**.
- **:30 each hour — independent QAD**: review oldest/highest-priority `awaiting_qa` pages, up to 3 per bounded run; separate decision on each; never write production changes, self-QA or release. Returning REWORK is a *successful prevention* of bad publication, not a reason to waive controls.
- Next `:00` production checks for PASS and can release; **nominal** review-to-release delay ≤30 minutes plus task scheduling/CI/deploy latency **when a run actually executes and has capacity**. Not an SLA.
- Issue triage at both lanes, no third paid or background agent. GitHub Actions is deterministic checks, not an LLM.

Run `python3 orchestrator/pipeline/hourly_pipeline.py --check --out hourly-plan.json` for an evidence-grounded plan and basic state/indexation integrity check. CI publishes it as a **read-only artifact**, never edits `tasks.json`.

## State handoffs and priorities

| Status | Actual owner | Next role | Durable evidence |
|---|---|---|---|
| `ready` | EDT-01 | EDT-01 | unique question, brief, dependencies, real source intent |
| `claimed` | EDT-01 or OPS-01 | same owner | unique real run ID + optimistic GitHub branch-head lease |
| `awaiting_qa` | QAD-01 | QAD-01 | complete HTML, original relevant images, dated citations, source SHA, test results; retains noindex |
| `rework` | EDT-01 | EDT-01 | QAD reason, exact reproducer and acceptance criteria |
| `qa_passed` | OPS-01 | OPS-01 | **separate real QAD run** with PASS review file; retain noindex until atomic release |
| `published` | OPS-01/ANA-01 handoff | ANA-01 | public HTTP evidence, success CI/Pages, indexable canonical + sitemap, deployment SHA; actual Google indexing still UNKNOWN |
| `blocked` | responsible role/CEO-01 | triage | exact blocker, age, incident ID, one next recovery step |

**Article handoff contract:** `task_id | article path | producer run + source Git SHA/blob hash | primary URLs + checked dates | visuals provenance | affiliate disclosure and actual approved link eligibility | 390/1280 screenshots if really inspected | static/browser results or NOT TESTED | independent QA pending | budget=0`.

**QA verdict contract:** `article ID | unique QAD run | exact reviewed content SHA | PASS/REWORK/REJECT | source and claims | original media/alt/rights | real mobile/table/form checks or NOT TESTED | affiliate/legal claims | QA evidence file | return owner`. A changed article after PASS requires fresh independent QA. No bypass via stale review approval.

**OPS release contract:** immutable reviewed source unchanged; full site technical checks green; remove noindex only for PASS; update homepage/contextual links and sitemap **in same optimistic compare-and-swap commit** as release state; verify Pages success, public 200, actual meta robots, canonical and sitemap. If deployment is still pending, status must not claim fully verified publication; record a pending verification blocker. Treat `published` in code as a state marker, not proof Google indexed it.

## Queue backpressure and error recovery

- A single production run should take **up to 4 approved releases**, then **up to 2 reworks**, then **up to 2 new drafts**. Stop new draft generation once **5 new complete drafts** are actually handed off in the local day; unused hourly slots fix reworks, optimize articles, review CI and update real analytics.
- If **6 or more articles await QA**, pause new drafts; give QA capacity a chance to catch up. Do not let commercial or agent-rating work starve content review.
- QAD takes up to 3 per real run, sorted priority then recorded handoff time; backlog/unknown timestamps reported honestly. Do not batch PASS without separate article evidence.
- A `claimed` lock older than **90 minutes** creates an alert; never auto-steal. If a run stopped mid-artifact, inspect real source commit/run and retry the same task only after ownership resolution; avoid double articles/commits.
- If QA wait or PASS→release wait exceeds **2 hours** (where time can be established), emit an aging warning. Recovery owner is specified, not speculative timers or external notifications.
- A GitHub write must compare the last-known head SHA; if head changed, re-fetch and reconcile, don't force-push or overwrite another lane's work. Keep authorship/QA independence even on branch conflicts.
- After failure, record `INC` root cause, keep safe unrelated tasks moving. Retry transient errors up to 2 times; do not retry invalid QA or editorial failures automatically.
- Keep 10–15 distinct prepared briefs, but do not generate articles just to meet a count. The original images must have real provenance and relevance; original tools only where genuinely useful.

## Verification and economics

- `scripts/check_site.py`, `scripts/check_editorial_evidence.py`, `scripts/build_sitemap.py --check` and **dynamic all-article** Chromium smoke at 390/768/1280/1440; screenshots require explicit visual review by independent QAD where available. A passing CI test **cannot** substitute for source/reader QA.
- Hourly coordinator report is read-only; actual schedules are hosted in ChatGPT Automations. If a schedule fails, hourly planner alone does NOT run production or QA.
- Record new complete drafts, independent decisions, actual public releases, Google indexed pages (only actual GSC evidence), source citations and paid cash as **separate measured states**.
- Never guarantee 5 published per day, ranking, revenue or exact 30-minute transitions.

## Owner alert threshold

Escalate: P0 trust/security/false disclosures immediately within the next real authorized run; 2 missed QA slots or 2 hours beyond a time-stamped pending handoff; any repeated broken CI, lost writes or conflicting source SHAs. Nonurgent issues go in the daily ledger, not hourly user spam.
