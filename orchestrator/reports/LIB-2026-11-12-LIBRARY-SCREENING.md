# LIB-2026-11-12 — Reusable libraries and CI dependency review

Review date: November 12, 2026. Reviewer function: AES-00 / OPS-01; evidence source: public upstream documentation. This is a candidate evaluation, not a purchase, install, or assertion of tested performance on our workflow.

| Library or platform | Evidence | Decision | Why |
|---|---|---|---|
| Python stdlib: json, pathlib, unittest, hashlib | https://docs.python.org/3.12/library/ and https://docs.python.org/3.12/library/unittest.html | ADOPTED / already used | Zero external dependency, adequate for present simple task-state machine and regression suite |
| Python stdlib: sqlite3 | https://docs.python.org/3.12/library/sqlite3.html | WATCH | Consider only if actual concurrent-writer failure proves need for transactional shared state; current GitHub version-control compare-and-swap is sufficient |
| Ruff Python linter | https://pypi.org/project/ruff/ | EVALUATE ONLY | Official PyPI lists MIT and fast Python linting; potential future improvement, but no measured marginal benefit yet and no new dependency installed |
| GitHub Actions checkout/setup-python/upload-artifact | https://docs.github.com/en/actions/reference/security/secure-use | HARDENED | Changed existing action references from mutable v4/v5 tags to exact GitHub-resolved full SHA in CI; retain minimal GITHUB_TOKEN contents:read |

## Enforced evaluation protocol
No third-party library installation, new service account, paid API, unreviewed network installation or transitive dependencies without actual technical need, vetted license/security/provenance/version, deterministic test and rollback; owner-approved spend controls remain. Compare to stdlib baseline; record observed output not marketing benchmarks. Follow up only if a concrete recurring defect justifies further adoption.
