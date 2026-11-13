import sys
import pathlib
import tempfile
import unittest
from datetime import datetime, timezone
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from pipeline.hourly_pipeline import build_plan,audit_state

def task(id,status,owner,priority="P1",path=None,qa=None,extra=None):
    d={"id":id,"status":status,"owner":owner,"priority":priority,
       "artifact_path":path,"depends_on":[],"qa":qa or {}}
    d.update(extra or {})
    return d

class HourlyPipelineTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,11,13,10,tzinfo=timezone.utc)
    def test_passed_release_is_first_and_qa_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            (root/"articles").mkdir()
            (root/"articles/a.html").write_text('<meta name="robots" content="noindex,nofollow">')
            (root/"articles/b.html").write_text('<meta name="robots" content="noindex,nofollow">')
            state={"tasks":[
                task("ART-P","qa_passed","OPS-01","P0","articles/a.html",
                     {"decision":"PASS","reviewer_role":"QAD-01","evidence":"qad.md","reviewer_run_id":"qad-1"},
                     {"producer_run_id":"edt-1"}),
                task("ART-Q","awaiting_qa","QAD-01","P0","articles/b.html"),
                task("ART-D","ready","EDT-01"),
            ]}
            p=build_plan(state,root,self.now)
            self.assertTrue(p["safe"],p["alerts"])
            self.assertEqual(p["production"]["step_1_release_passed"],["ART-P"])
            self.assertEqual(p["independent_qa"]["review_next"],["ART-Q"])
            self.assertEqual(p["production"]["step_3_new_editorial"],["ART-D"])
    def test_qa_backpressure_pauses_new_drafts_but_not_rework(self):
        state={"tasks":[task("Q-"+str(i),"awaiting_qa","QAD-01") for i in range(7)]+
               [task("D","ready","EDT-01"),task("R","rework","EDT-01")]}
        p=build_plan(state,pathlib.Path("/tmp"),self.now)
        self.assertTrue(p["production"]["new_editorial_paused_for_backpressure"])
        self.assertEqual(p["production"]["step_3_new_editorial"],[])
        self.assertEqual(p["production"]["step_2_fix_qa_rework"],["R"])
    def test_stale_qa_pass_cannot_be_indexed_early(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);(root/"articles").mkdir()
            (root/"articles/a.html").write_text('<meta name="robots" content="index,follow">')
            t=task("A","qa_passed","OPS-01",path="articles/a.html",
                qa={"decision":"PASS","reviewer_role":"QAD-01","evidence":"review","reviewer_run_id":"qa"},
                extra={"producer_run_id":"ed"})
            issues=audit_state({"tasks":[t]},root,self.now)
            self.assertIn("EARLY_INDEXATION",[x["code"] for x in issues])
    def test_self_approval_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);(root/"articles").mkdir()
            (root/"articles/a.html").write_text('<meta name="robots" content="noindex">')
            t=task("A","qa_passed","OPS-01",path="articles/a.html",
                qa={"decision":"PASS","reviewer_role":"QAD-01","evidence":"review","reviewer_run_id":"same"},
                extra={"producer_run_id":"same"})
            issues=audit_state({"tasks":[t]},root,self.now)
            self.assertIn("UNVERIFIED_PASS",[x["code"] for x in issues])
    def test_fifo_priority(self):
        state={"tasks":[task("Z","awaiting_qa","QAD-01","P1"),task("A","awaiting_qa","QAD-01","P0")]}
        p=build_plan(state,pathlib.Path("/tmp"),self.now)
        self.assertEqual(p["independent_qa"]["review_next"][0],"A")

if __name__=="__main__":unittest.main()
