# AffiliateOS continuous improvement and library adoption

Adopted 2026-11-12. Owner instructions: proactively fix observable failures, learn from evidence, and investigate reusable software libraries while respecting $0 external spending.

## Incident loop — always produce a verifiable outcome
1. Detect (failed GitHub Action, QA REWORK, broken functionality, conflicting state, user feedback). Do not pretend an issue is absent.
2. Record `INC-ID`: exact failing commit/run/step, scope, severity, observed failure, reproducible test, owner and stop/rollback trigger.
3. ORC assigns one owner for the minimal patch; P0 for broken CI or critical trust/security issue. Protect unrelated operations.
4. Add a regression test demonstrating original defect; implement smallest reliable correction. Keep a baseline and no-spend invariant.
5. Run local or GitHub tests. If test unavailable, state NOT TESTED, never declare resolution. Production code still needs release rules; authored content still needs independent QAD.
6. Confirm green CI at exact fixed SHA; close incident with proof and owner/date.
7. If same class recurs twice or severe, AES-00 assesses role skill/prompt; five comparable cases and independent QAD required before promotion.

## Improvement prioritization
P0 broken CI, false claims, privacy/security; P1 QA/indexation and measurable buyer value; P2 new venture research with sourced signals; P3 optional skills and tooling. No multiplying agents solely to increase apparent productivity. At most one recurring defect triage per production cycle; never block P0/P1 to polish prompts.

## Library supply-chain evaluation (mandatory before introducing dependency)
A technical role can investigate any lawful open-source project, but must document a `LIB-ID` with:
- Real requirement and why built-in tools are insufficient; maintenance and integration effort.
- Official upstream homepage/repo, maintainers, publication or update date, release/version, community/issue health when actually observed.
- License and obligations, all direct/transitive dependencies, runtime/Python version compatibility and hidden services/costs.
- Provenance, dependency pin and lockfile or full SHA of GitHub Action; no untrusted install scripts, no credentials in CI, least privilege.
- Reversible $0 proof of concept, security/privacy test, benchmark vs baseline, rollback and owner/QA decisions.
- No auto-install of random packages, copying proprietary code, paid API activation or secret access. Reject if the current Python stdlib is sufficient.

## First screening (not an installation)
1. Python `json`, `pathlib`, `unittest`, `hashlib` — ALREADY USED, stdlib, zero new dependencies. Suitable for current small orchestration scope; keep as default.
2. Python `sqlite3` — STDLIB CANDIDATE only if observed concurrent update conflicts justify transaction storage; currently GitHub branch-head compare-and-swap is sufficient and centrally auditable.
3. Ruff (MIT) — CONSIDER for faster Python lint only if current defect recurrence justifies added dependency; no package installed and no CI download authorized yet.
4. GitHub Actions `checkout`/`upload-artifact` — ALREADY USED; pin their refs to verified full-length SHAs instead of mutable tags when changes are reviewed.

Record test dates, not imaginary benchmarks. No hosted autonomous model runtime exists in this implementation. Existing 08:00 production and 14:00 independent QA are the LLM run gates; GitHub CI is deterministic.