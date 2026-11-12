# AffiliateOS — precise handoff protocol v1.0

## Single source of truth and message bus
- Operations state: `orchestrator/state/tasks.json` in the **commercial** GitHub repo, edited through controlled updates. Library documents may describe plans but never override the current GitHub task state.
- Event trace: `orchestrator/state/events.jsonl` append-only, written only after actual state change. Long narratives and full source text belong in referenced files, **not** task messages.
- An "agent" here is a role contract executed within actual authorized ChatGPT scheduled turns, not a separate server process. ORC is a deterministic state machine and role within production.
- Use GitHub branch update with expected old head, reject stale state and re-read before retry; do NOT force-push. Local reference engine uses atomic file replace; it cannot by itself protect GitHub multi-writer conflicts.

## Authority and transitions
`ready -> claimed -> awaiting_qa -> [qa_passed -> published | rework -> claimed | rejected]`.
`blocked` requires concrete missing dependency or CEO escalation; no fake completion. Only QAD-01 can decide independently evidenced PASS/REWORK/REJECT in a distinct real execution. Only OPS-01 may publish QA-passed output. Noindex is held until approved indexable release. Owner controls outside-account/paid actions even if a role prompt says otherwise.

## Role routing
CEO: strategy, priority, critical escalations and owner memo. ORC: select next task, enforce prerequisites, compact handoffs and idempotency, surface stuck tasks. SID: validate new opportunities with dated primary sources. EDT: buyer-focused article/design/tool output. OPS: code, tests, publication and rollback. QAD: independent factual/UX/security QA. COM: program eligibility, terms and affiliate payouts (no claims without statements). ANA: attribution, indexing and verified financial metrics. AES: change proposals and same-input evaluations, never self-approve rollout.

## QA decision definitions
- PASS: named artifact at source commit, independent evidence paths, verified assertions, **unverified checks marked NOT TESTED**, no unresolved severe blocker.
- REWORK: exactly which defect, how to reproduce, acceptance test, assigned producer, retry count. Two failed attempts -> CEO.
- REJECT: fundamental invalidity/unsafety or no recoverable buyer value, with evidence; only CEO may decide replacement project.

## Failure modes
- Transient external error: max 2 bounded retries with backoff when tool actually supports; then BLOCKED with proof and move to independent ready task.
- Stale or duplicate run: no double work; idempotent claim and branch optimistic locking.
- Missing artifact: mark NOT TESTED or BLOCKED, not PASS.
- Missing source/tracking/analytics: UNKNOWN, never zero or fabricated estimate.
- Heavy tasks: chunk with one complete artifact per run; don't infer hidden server load or move urgent deadlines to unverified off-peak.

## Checkup acceptance
Run all state-machine tests + static content QA + GitHub Actions checks, inspect actual workflow results and make a list of outstanding P0 blockers. Do not declare the whole organization "perfect" based only on green CI: functional user journeys, commercial eligibility, live analytics and independent editorial QA require distinct evidence.

## Terminal non-public task state
`completed` is a CLOSED state for verified research, analytics and internal reports; it is NOT `published` and cannot imply a public page is indexed or approved. Internal reports require actual evidence; public content still uses the independent QA -> `qa_passed` -> `published` release sequence.
