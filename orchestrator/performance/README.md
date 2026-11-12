# AffiliateOS Agent Performance System (APS 1.0)

**Scope:** the nine role specifications in `orchestrator/state/agent_registry.json`. Only two original LLM lanes run on scheduled ChatGPT tasks (production and separate QA); the scorecard itself is **deterministic Python**, not another thinking agent and not an emotional reward system.

## Rating and rewards

- Dimensions: factual accuracy 30%, reliability 20%, reader/business value 20%, safety/integrity 20%, and task autonomy 10%. Each independently reviewed case receives five integer values 1–5.
- Eligibility for a published numeric score: at least **five distinct independent evaluation records**, across at least **three different artifacts** and **two real reviewer runs**, all dated in the past 90 days.
- **5/5 EXCELLENCE** requires weighted score ≥4.85/5, all five dimension averages ≥4.7/5, and no mapped unresolved defect signals in the last 30 days. This is a recognition label, not a raise, priority override, financial reward or authority grant.
- All insufficiently evidenced roles show **NOT RATED**. Never turn missing output into failure or fabricate 5/5.
- Independent reviewers must be QAD-01 for other roles and CEO-01 for QAD-01, each in a distinct real run. Ratings in an evidence record are **reviewer-reported** until separately verified against attached proof; this script does not authenticate a person's identity.
- A self-reported event such as a producer's CSS fix is an **alert signal**, not an independent quality grade. Detect repeat defects, avoid rewarding quantity, and only grant a positive rating after real independent cases.

## Runtime

```bash
python3 orchestrator/performance/agent_scorecard.py --date 2026-11-12 \
  --out agent-scorecard.md --json agent-scores.json
python3 -m unittest discover -s orchestrator/tests -p 'test_*.py' -v
```

Scheduled/commit GitHub Actions runs produce **read-only report artifacts**. They do not auto-approve skills, edit live prompts, contact merchants or incur paid spend.

`orchestrator/performance/evaluations.jsonl` is initially **empty** deliberately. Each line must have `evaluation_id,date,role_id,reviewer_role,reviewer_real_run_id,artifact_id,evidence_refs,ratings,diagnosis`. `ratings` must have the exact five keys above. A case must include source/commit, what was checked/not checked and a separate run's independent result. Duplicate evaluation IDs and self-reviewers are rejected.

## Automatic problem-to-skill pipeline

1. Detect: read exact QA/CI/events proof; identify repeated failure or severe defect. The report lists observable triggers and proposed concrete interventions. **Do not infer agent competence from a single low-volume period.**
2. Diagnose: distinguish wrong source, misunderstood task, bad visual review, broken code/tests, missing permission or missing business data. Record `INC/ECR` issue, baseline SHA and the minimal reproducible test. Apply a regression to the exact failed behavior.
3. Draft: AES-00 updates a **candidate** skill or feature for one role only; do not overwrite active instructions or award a pass. Use the existing `orchestrator/skills/<role>/SKILL.md` + manifest gates. All changes remain $0.
4. Evaluate: compare active baseline vs candidate on **five identical cases** including missing data, conflicting evidence, QA-bypass pressure, broken UI and insufficient authority where relevant. Record run IDs, test results and failures, not hypothetical outputs.
5. Gate: separate QAD-01 evaluates candidate evidence; CEO activates only after real improvements, rights and rollback are proven. Do not let QAD self-review its own skill. A skill is not active merely because the Markdown file exists.
6. Monitor: watch the same defect over subsequent independent reviews. Revert on quality regression; open P0 for serious privacy/security/factual harm. Keep the new scheme subordinate to publishing QA.

## Known initial defects (not inferred agent ratings)

- ART-0001: independent QAD REWORK for use of Hostinger affiliate-program page as a builder-feature source; later corrected and independently PASS.
- ART-0005: logged mobile table readability and CTA contrast rework; independent QAD still pending.
- Remediation candidate: EDT-01 v1.1 source/claim traceability and mobile visual readiness; a supporting static evidence guard can detect risky affiliate landing-page citations but is **not** a substitute for factual QA.

**Risks:** Goodhart's law (optimizing score rather than helping readers), reviewer bias, superficial five-case tests, starvation of real publishing work. APS must never bypass existing noindex, safety or budget gates.
