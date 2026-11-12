# AffiliateOS — Measured Workload Scheduling v2.0
Effective: 2026-11-12. Goal: reliable throughput and limited compute/context use, not presumed access to AI provider server utilization.

## First principles
- We have **no internal OpenAI server load telemetry** and no permission to claim which hours are quieter or faster. An owner's local off-peak time is NOT evidence about global model load or available quota.
- Do not delay release-critical, low-cost repairs or independently approved publication just to await an unverified off-peak window. Preserve the existing daily 08:00 production / 14:00 QA separation unless evidence and owner preferences justify change.
- Treat response time/429 errors as *observed signals*, not proof of global traffic patterns. Log only measured run data and do not invent tokens consumed, model cost, provider demand, or latency.

## Job classes
FAST: deterministic source/link checks, small CSS fixes, cached metadata, short status handoff. Run at next authorized task slot immediately.
MEDIUM: one source-verified buyer article, one calculator upgrade, focused SEO fix. Use bounded one-asset pipeline and save intermediate work.
HEAVY: deep niche comparison, 10+ source verification, major redesign, bulk asset generation, multi-site audits. Break into independent resumable slices: research / implement / test / release; do not allocate many competing roles in one context window.

## Adaptive scheduling decision — only after actual evidence
For each scheduled run record: job_class, run_id if available, scheduled_for, started_at, completed_at, duration_seconds if available, retry_count, transient_error_codes, succeeded, published_artifact, QA_rework_count, model/tool if known, source. Store null for unavailable fields.
After >=7 **comparable** runs across >=2 clock windows, examine median runtime, error rate and completed QA-approved output per cycle. Change heavy-work schedule only if a consistent >=20% gain or fewer retries is observed without hurting latency-critical QA/release; note small-sample uncertainty. No changes based on intuition alone.

## Resilience / resources
- 429/rate limit or transient failure: stop immediate retry storms; at most 2 bounded retries using permitted host/tool retry semantics, otherwise log BLOCKED and continue a different ready task. Do not invoke timers from a non-scheduled conversational run.
- Save artifact + durable checkpoint after each completed subtask; use unique task ID/revision to avoid double writes. Do not duplicate research context in multiple agent prompts.
- If live production fails, prioritize defect P0. Do not hold already independently approved work behind unrelated heavy research.
- Current external spend limit remains $0 until first *received* partner payout, then owner approval still needed for reinvestment.

## Runtime reality
Two separate scheduled ChatGPT automation cycles are configured, not a persistent cluster of autonomous parallel processes. Future actual orchestration can be evaluated only when runtime and budget permit.