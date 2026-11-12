#!/usr/bin/env python3
"""Evidence-first scorecard and targeted remediation signals for AffiliateOS roles.

This is deterministic analysis, not an LLM agent, a personality measure, or
independent verification of events in the repository.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ORCH = Path(__file__).resolve().parents[1]
ROLES = ORCH / "state/agent_registry.json"
EVENTS = ORCH / "state/events.jsonl"
REVIEWS = ORCH / "performance/evaluations.jsonl"

DIMENSIONS = {
    "accuracy": 0.30,
    "reliability": 0.20,
    "reader_or_business_value": 0.20,
    "safety_and_integrity": 0.20,
    "autonomy": 0.10,
}
ALLOWED_REVIEWERS = {"QAD-01", "CEO-01"}
MIN_REVIEWS = 5
WINDOW_DAYS = 90
WARN_DAYS = 30

# Only traceable operational signals, not inferred agent mental state.
ISSUE_RULES = {
    "QA_REWORK": ("EDT-01", "source_traceability"),
    "MOBILE_TABLE_REWORK": ("EDT-01", "mobile_readability"),
    "VISUAL_QA_CONTRAST_FIX": ("EDT-01", "contrast_regression"),
    "EDITORIAL_REWORK_SUBMITTED": ("EDT-01", "visual_relevance"),
}
ACTIONS = {
    "source_traceability": "EDT-01 candidate skill: make a claim→official product/help source matrix and flag affiliate landing pages used as feature evidence.",
    "mobile_readability": "EDT-01/OPS-01: inspect real 390px screenshots, responsive comparison cards, labels and horizontal overflow; add case-specific Chromium regression.",
    "contrast_regression": "OPS-01: test the computed CTA text/background contrast at 390px and 1280px before a producer handoff.",
    "visual_relevance": "EDT-01: confirm image relevance, distinct assets, rights/provenance captions and mobile composition before handoff.",
}

def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    items = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{line_no}: invalid JSONL") from exc
        if not isinstance(record, dict):
            raise ValueError(f"{path.name}:{line_no}: expected JSON object")
        items.append(record)
    return items

def validate_evaluations(records: list[dict], roles: set[str]) -> None:
    ids = set()
    for i, r in enumerate(records, 1):
        rid = r.get("role_id")
        reviewer = r.get("reviewer_role")
        eid = r.get("evaluation_id")
        if not isinstance(eid, str) or not eid or eid in ids:
            raise ValueError(f"Evaluation {i}: unique evaluation_id required")
        ids.add(eid)
        if rid not in roles or reviewer not in ALLOWED_REVIEWERS or reviewer == rid:
            raise ValueError(f"Evaluation {eid}: invalid role or self-reviewer")
        if rid == "QAD-01" and reviewer != "CEO-01":
            raise ValueError(f"Evaluation {eid}: QAD work must be assessed by CEO, not itself")
        if not r.get("artifact_id") or not r.get("reviewer_real_run_id"):
            raise ValueError(f"Evaluation {eid}: artifact and real reviewer run ID required")
        refs = r.get("evidence_refs")
        if not isinstance(refs, list) or not refs or any(not isinstance(v, str) or not v.strip() for v in refs):
            raise ValueError(f"Evaluation {eid}: non-empty evidence_refs required")
        date.fromisoformat(r.get("date", ""))
        score = r.get("ratings")
        if not isinstance(score, dict) or set(score) != set(DIMENSIONS):
            raise ValueError(f"Evaluation {eid}: exact five-dimension ratings required")
        if any(type(v) is not int or v not in (1, 2, 3, 4, 5) for v in score.values()):
            raise ValueError(f"Evaluation {eid}: each dimension must be an integer 1..5")
        if not isinstance(r.get("diagnosis", ""), str):
            raise ValueError(f"Evaluation {eid}: diagnosis must be text")
        # These are reviewer-reported scores, not cryptographically verified testimony.

def dated_alerts(events: list[dict], today: date) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = defaultdict(list)
    seen = set()
    for event in events:
        name = event.get("event")
        if name not in ISSUE_RULES:
            continue
        try:
            day = date.fromisoformat(str(event.get("at", ""))[:10])
        except ValueError:
            continue
        if not (today - timedelta(days=WARN_DAYS) <= day <= today):
            continue
        role, kind = ISSUE_RULES[name]
        key = (role, kind, event.get("task_id") or event.get("id"), day.isoformat())
        if key in seen:
            continue
        seen.add(key)
        result[role].append({
            "kind": kind, "event": name,
            "task": event.get("task_id") or event.get("id") or "unattributed",
            "date": day.isoformat(),
            "source": "GitHub event log (not independent impact review)",
        })
    return result

def rating_for_role(role: str, records: list[dict], alerts: list[dict], today: date) -> dict:
    cutoff = today - timedelta(days=WINDOW_DAYS)
    samples = [r for r in records if r["role_id"] == role and cutoff <= date.fromisoformat(r["date"]) <= today]
    unique_artifacts = len({r["artifact_id"] for r in samples})
    unique_runs = len({r["reviewer_real_run_id"] for r in samples})
    sufficient = len(samples) >= MIN_REVIEWS and unique_artifacts >= 3 and unique_runs >= 2
    result = {
        "role_id": role,
        "review_count": len(samples),
        "independent_artifacts": unique_artifacts,
        "review_runs": unique_runs,
        "score_out_of_5": None,
        "level": "UNRATED — insufficient independent evidence",
        "quality_alerts": alerts,
        "interventions": list(dict.fromkeys(ACTIONS[a["kind"]] for a in alerts if a["kind"] in ACTIONS)),
    }
    if sufficient:
        averages = {k: sum(r["ratings"][k] for r in samples) / len(samples) for k in DIMENSIONS}
        composite = round(sum(averages[k] * weight for k, weight in DIMENSIONS.items()) / sum(DIMENSIONS.values()), 2)
        result["score_out_of_5"] = composite
        result["dimension_averages"] = {k: round(v, 2) for k, v in averages.items()}
        # "5/5" recognition requires robust quality, not 5 tasks and blind optimism.
        if composite >= 4.85 and min(averages.values()) >= 4.7 and not alerts:
            level = "5/5 EXCELLENCE (evidence-based recognition)"
        elif composite < 4.0 or len(alerts) >= 2:
            level = "IMPROVEMENT REQUIRED"
        elif composite >= 4.5 and not alerts:
            level = "STRONG"
        else:
            level = "IN REVIEW"
        result["level"] = level
        if composite < 4.0 and not result["interventions"]:
            result["interventions"] = ["AES-00: compare five concrete failure cases, isolate the lowest-scoring dimension, draft one targeted candidate skill; independent QAD + CEO activation required."]
    elif len(alerts) >= 2:
        result["level"] = "UNRATED — remediation priority from observed defects"
    return result

def build_report(registry: dict, evaluations: list[dict], events: list[dict], today: date) -> dict:
    roles = [r["id"] for r in registry["roles"]]
    if len(roles) != len(set(roles)):
        raise ValueError("Duplicate role IDs")
    validate_evaluations(evaluations, set(roles))
    alerts = dated_alerts(events, today)
    ratings = [rating_for_role(role, evaluations, alerts.get(role, []), today) for role in roles]
    return {
        "date": today.isoformat(),
        "scope": "AffiliateOS roles; task-run specifications do not equal standalone always-on workers",
        "rating_method": f"Independent reviewer-reported case scores; five distinct evaluations, at least three artifacts and two reviewer runs within {WINDOW_DAYS} days",
        "not_proven": "Role-specific conclusions are not independent evidence of business income or agent motivation",
        "roles": ratings,
        "counts": {
            "registered_roles": len(roles),
            "eligible_for_numeric_rating": sum(x["score_out_of_5"] is not None for x in ratings),
            "alerted_roles": sum(bool(x["quality_alerts"]) for x in ratings),
            "five_of_five_recognitions": sum(x["level"].startswith("5/5") for x in ratings),
        },
    }

def markdown(report: dict) -> str:
    out = [
        f"# AffiliateOS Agent Performance — {report['date']}",
        "",
        "Ratings are **not motivational emotions** and not evidence that nine independent model processes run.",
        "Missing evaluations mean **NOT RATED**, not 0/5 or 5/5.",
        "",
        "| Role | Rated score | Independent cases | Status |",
        "|---|---:|---:|---|",
    ]
    for role in report["roles"]:
        score = "NOT RATED" if role["score_out_of_5"] is None else f"{role['score_out_of_5']:.2f}/5"
        out.append(f"| {role['role_id']} | {score} | {role['review_count']} | {role['level']} |")
    out += ["", "## Observed defects and corrective actions"]
    seen = False
    for role in report["roles"]:
        if not role["quality_alerts"]:
            continue
        seen = True
        out.append(f"### {role['role_id']}")
        for alert in role["quality_alerts"]:
            out.append(f"- {alert['date']} / {alert['task']} / {alert['event']} — **{alert['kind']}** (recorded event, impact not independently re-tested).")
        for action in role["interventions"]:
            out.append(f"- Proposed remedy: {action}")
    if not seen:
        out.append("No mapped defect signals in the last 30 days. This is not proof of perfect quality.")
    out += [
        "",
        "## Quality promotion guard",
        "- A low score or repeat defect opens a diagnosis and a candidate skill/feature proposal, not a live prompt replacement.",
        "- Test baseline vs candidate on five comparable cases; QAD reviews independently, CEO authorizes promotion, OPS checks CI and rollback.",
        "- Do not reduce output safeguards or reward clickbait, duplicated pages, invented sales or QA bypasses.",
        "- Zero external spend; evidence references, issue recurrence and action outcomes stay auditable.",
        "",
    ]
    return "\n".join(out)

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", default=datetime.now(ZoneInfo("Europe/Bucharest")).date().isoformat())
    ap.add_argument("--registry", type=Path, default=ROLES)
    ap.add_argument("--events", type=Path, default=EVENTS)
    ap.add_argument("--evaluations", type=Path, default=REVIEWS)
    ap.add_argument("--out", type=Path, help="Path to generated Markdown report")
    ap.add_argument("--json", type=Path, dest="json_out", help="Path to generated JSON report")
    args = ap.parse_args(argv)
    try:
        today = date.fromisoformat(args.date)
        registry = json.loads(args.registry.read_text(encoding="utf-8"))
        report = build_report(registry, read_jsonl(args.evaluations), read_jsonl(args.events), today)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(markdown(report), encoding="utf-8")
        else:
            print(markdown(report))
        if args.json_out:
            args.json_out.parent.mkdir(parents=True, exist_ok=True)
            args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Performance audit FAILED: {exc}", file=__import__("sys").stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
