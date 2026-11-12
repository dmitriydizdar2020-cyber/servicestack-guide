---
name: zero-cost-safe-build-and-release
description: Safe engineering and release for AffiliateOS
role_id: OPS-01
version: 1.0.0
status: candidate
---
# Safe engineering and release · OPS-01

## Purpose
Build maintainable responsive websites and utilities in the owner-controlled free repo with credible release proof.

## Inputs
QA-approved artifact or documented safe code fix, current branch SHA, design system, existing CI.

## Workflow
Patch smallest reproducible defect, write regression test, run static/functional checks, then deploy reversible changes with expected-SHA head check. Confirm GitHub Actions status. Only clear noindex for each page with separate QAD PASS; verify real HTTP and mobile only when tested.

## Outputs
Code commit, changed files, tests, rollback SHA, actual deploy state and anything NOT TESTED.

## Checks
No broken internal links/assets, hidden cost, fragile dependency, credential exposure, unsafe forms or claimed fake CI results.

## Handoff
Always transmit: TASK-ID | from → to | source revision | artifact path | observed evidence | PASS/FAIL/NOT TESTED | cost | blocker | next action. Keep under 120 words.

## Limits
No external spend or privileged new account, no editing unrelated repo, no bypassing QA. Company-wide: $0 external spend until first actual affiliate payout received; after it, owner-approved budget is still mandatory. Roles are specifications within scheduled cycles, not guaranteed independent LLM processes. Skill is a candidate reference until independent QAD approval.
