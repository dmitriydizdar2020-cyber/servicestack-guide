import unittest
from datetime import date
from orchestrator.performance.agent_scorecard import (
    build_report, dated_alerts, rating_for_role, validate_evaluations
)
DIMS = ["accuracy","reliability","reader_or_business_value","safety_and_integrity","autonomy"]

def row(n, role="EDT-01", value=5, reviewer="QAD-01"):
    return {
        "evaluation_id": f"QA-E-{role}-{n}",
        "date": "2026-11-12",
        "role_id": role,
        "reviewer_role": reviewer,
        "reviewer_real_run_id": f"review-run-{n}",
        "artifact_id": f"ART-{n}",
        "evidence_refs": [f"orchestrator/reviews/evidence-{n}.md"],
        "ratings": dict.fromkeys(DIMS, value),
        "diagnosis": "Case-level evidence required; fixture only",
    }

class AgentScorecardTests(unittest.TestCase):
    def test_no_evaluations_is_not_five_or_zero(self):
        result = build_report({"roles":[{"id":"EDT-01"},{"id":"QAD-01"}]}, [], [], date(2026,11,12))
        self.assertEqual(result["counts"]["eligible_for_numeric_rating"], 0)
        self.assertIsNone(result["roles"][0]["score_out_of_5"])

    def test_genuine_five_cases_get_five_if_no_alerts(self):
        entries=[row(i) for i in range(5)]
        validate_evaluations(entries,{"EDT-01"})
        outcome=rating_for_role("EDT-01",entries,[],date(2026,11,12))
        self.assertEqual(outcome["score_out_of_5"],5.0)
        self.assertTrue(outcome["level"].startswith("5/5"))

    def test_repeat_defects_prevent_excellence(self):
        events=[
            {"event":"QA_REWORK","task_id":"ART-001","at":"2026-11-12"},
            {"event":"MOBILE_TABLE_REWORK","task_id":"ART-002","at":"2026-11-12"},
        ]
        alerts=dated_alerts(events,date(2026,11,12))["EDT-01"]
        outcome=rating_for_role("EDT-01",[row(i) for i in range(5)],alerts,date(2026,11,12))
        self.assertEqual(outcome["level"],"IMPROVEMENT REQUIRED")
        self.assertEqual(len(outcome["interventions"]),2)

    def test_reviewer_cannot_review_themselves(self):
        with self.assertRaises(ValueError):
            validate_evaluations([row(1,role="QAD-01",reviewer="QAD-01")],{"QAD-01"})
        validate_evaluations([row(1,role="QAD-01",reviewer="CEO-01")],{"QAD-01"})

    def test_missing_evidence_and_duplicate_ids_rejected(self):
        r=row(1)
        r["evidence_refs"]=[]
        with self.assertRaises(ValueError):
            validate_evaluations([r],{"EDT-01"})
        with self.assertRaises(ValueError):
            validate_evaluations([row(1),row(1)],{"EDT-01"})

    def test_sparse_records_do_not_create_numerical_score(self):
        outcome=rating_for_role("EDT-01",[row(i) for i in range(2)],[],date(2026,11,12))
        self.assertIsNone(outcome["score_out_of_5"])

    def test_generic_dated_quality_signal_for_any_registered_role(self):
        events=[{"event":"ROLE_QUALITY_DEFECT","at":"2026-11-12","affected_role":"ANA-01",
                 "issue_code":"unverified_metric_claim","severity":"P0",
                 "task_id":"ANA-9","evidence_refs":["orchestrator/reviews/ANA-9.md"]}]
        alerts=dated_alerts(events,date(2026,11,12),{"ANA-01"})["ANA-01"]
        self.assertEqual(alerts[0]["severity"],"P0")
        self.assertIn("critical",rating_for_role("ANA-01",[],alerts,date(2026,11,12))["level"])

    def test_generic_event_rejects_missing_evidence(self):
        with self.assertRaises(ValueError):
            dated_alerts([{"event":"ROLE_QUALITY_DEFECT","at":"2026-11-12",
                           "affected_role":"CEO-01","issue_code":"wrong_priority"}],
                         date(2026,11,12),{"CEO-01"})

    def test_alerts_outside_window_ignored(self):
        issues=[{"event":"VISUAL_QA_CONTRAST_FIX","task_id":"ART-1","at":"2025-01-10"}]
        self.assertEqual(dated_alerts(issues,date(2026,11,12)),{})

if __name__ == "__main__":
    unittest.main()
