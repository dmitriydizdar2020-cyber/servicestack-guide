# AffiliateOS internal role skills v1.0

A **skill** is a concise, versioned instruction package for an existing department. Nine role-specific packages are present under `skills/<ROLE-ID>/SKILL.md`. These files are **internal repository documentation, not native ChatGPT plugins or independently executing agents**.

## How skills flow into real work
- ORC-01 determines the assigned role from canonical `orchestrator/state/tasks.json`.
- The existing role prompt `orchestrator/prompts/<ROLE-ID>.md` remains active until an independent QA review explicitly promotes the skill package in `skills/manifest.json` from `candidate` to `approved`.
- The relevant role reads **only its own approved skill** alongside the one task and its necessary sources. Do not read all nine every cycle.
- The role's output is a concrete artifact plus a short handoff. ORC routes it; QAD independently checks releases; CEO decides escalations.
- The `skill_audit.py` static check verifies that all roles have well-formed skill packs. This is not a five-case prompt evaluation or an independent quality approval.

## Adding a new role safely
1. Confirm a real repeated gap, not speculative prestige.
2. Generate a DRAFT: `python3 orchestrator/skills/new_role.py --role PRD-01 --name 'Product Manager' --purpose 'Define product tests from user needs'`.
3. Define scopes, dependencies, permissions, cost limits, acceptance criteria and a 5-case evaluation.
4. CEO reviews the business need; independent QAD reviews evaluation and rights; only then add a new role registry entry, operational prompt and candidate/approved skill manifest entry as appropriate.
5. CI validates all declared roles. A generated file does NOT create a live agent, model call, automation or tool privilege.

## Read-only health check
`python3 orchestrator/skills/skill_audit.py`

No external package or paid service is needed for the present scheme.