# AffiliateOS Agent Orchestrator v1.0

This is **real deterministic coordination code** for the owner's commercial GitHub repository, not a fake autonomous multi-LLM fleet. It assigns tasks, enforces independent QA evidence and $0 spend, supports corrective feedback and bounded retries, records handoffs, offers prioritization and runs automated checkups via GitHub Actions.

## Components
- `BOOTSTRAP.md`: single shared startup and values; no old 40-file mandatory context loading.
- `PROTOCOL.md`: state transitions and security/quality gates.
- `state/agent_registry.json`: nine narrow role contracts, including new `ORC-01`.
- `prompts/*.md`: concise task-specific prompts.
- `state/tasks.json`: canonical **operational** task ledger; do not confuse with older Library planning queue.
- `state/events.jsonl`: evidence-backed audit events for actual transitions.
- `orchestrate.py`: no external dependencies; `checkup`, `next`, `claim`, `handoff`, `review`, `release`.
- `tests/`: regression tests for QA autonomy, routing, budget, idempotency, failure behavior.
- `.github/workflows/orchestrator-checkup.yml`: read-only scheduled and push CI that runs the tests and emits a checkup artifact. It does **not** call paid model APIs, change role states or publish autonomously.

## Quick usage from repository root
```sh
python3 -m unittest discover -s orchestrator/tests -v
python3 orchestrator/orchestrate.py checkup --out orchestrator-checkup.json
python3 orchestrator/orchestrate.py next --role QAD-01
python3 orchestrator/orchestrate.py next --role SID-00
```
For real role updates, use CLI help for `claim`, `handoff`, `review`, `release` and preserve file changes in owner GitHub with expected current branch head; do not run demo transitions against production state.

## Honest operational status
Current agents = prompt roles simulated sequentially in existing **production** ChatGPT task (08:00 Europe/Bucharest), plus actual separate **QA** task (14:00). Agent Orchestrator verifies and routes work through persistent state; its GitHub workflow automatically audits the system at scheduled UTC times. Without a separately authorized, connected LLM runtime it cannot wake every role to converse 24/7. Independent QAD content approval and first real revenue remain **unverified** until observed.

## Release gate
Do not remove staging `noindex` until independently reviewed. Site static CI and orchestrator CI must pass. A QA result must cite actually inspected material and distinct run; a live user journey may remain `NOT TESTED` if browser unavailable. `published` means actually indexable and verified; mere GitHub Pages deployment is not enough.

## Future evolution
After proving reliability, the next authorized version can integrate a durable job queue and connected model runtime. Before any new cost or third-party account, require explicit owner approval and keep $0 before the first actually paid affiliate payout. No new runtime has been installed as part of this module.