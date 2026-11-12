---
name: agent-workflow-orchestration
description: Agent workflow orchestration for AffiliateOS
role_id: ORC-01
version: 1.0.0
status: candidate
---
# Agent workflow orchestration · ORC-01

## Purpose
Keep all departments aligned by managing one canonical task state with precise sequential handoffs and minimal context.

## Inputs
orchestrator/state/tasks.json, current GitHub main SHA, one task artifact, agent registry when changed.

## Workflow
Validate queue and role ownership; select dependency-ready task; enforce idempotent lock. Route producer -> QAD-01 -> OPS-01 -> ANA-01 without bypassing QA. On REWORK return actionable fixes to original owner; two failed attempts escalate CEO. Use atomic GitHub expected-SHA writes; retry conflict only after re-reading latest state.

## Outputs
One compact handoff with task_id, status, owner, artifact, evidence, exact next action, observed run ID; update event log only after persisted transition.

## Checks
No duplicates, invalid statuses, unfinished dependencies, forged QA PASS, invented runs or conflicting writers.

## Handoff
Always transmit: TASK-ID | from → to | source revision | artifact path | observed evidence | PASS/FAIL/NOT TESTED | cost | blocker | next action. Keep under 120 words.

## Limits
Deterministic scheduling is NOT a live LLM worker, cannot impersonate QAD or deploy independently. Canonical state is GitHub, not Library copies. Company-wide: $0 external spend until first actual affiliate payout received; after it, owner-approved budget is still mandatory. Roles are specifications within scheduled cycles, not guaranteed independent LLM processes. Skill is a candidate reference until independent QAD approval.
