import copy
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import orchestrate as o

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.data=copy.deepcopy(o.load_state())
    def draft_task(self):
        self.data['tasks'].append({
            'id':'DRAFT-999', 'title':'Fixture', 'priority':'P1','status':'ready',
            'owner':'EDT-01','depends_on':[],'attempts':0,'max_attempts':2,
            'spend_usd':0,'qa':{'decision':None,'evidence':None}
        })
        return self.data['tasks'][-1]
    def test_bootstrap_and_readiness(self):
        self.assertEqual([],o.validate(self.data))
        self.assertEqual('ART-0001',o.next_task(self.data,'QAD-01')['id'])
        self.assertNotEqual('ANA-0001',(o.next_task(self.data,'ANA-01') or {}).get('id'))
        self.assertIsNone(o.next_task(self.data,'OPS-01'))
    def test_role_owner_claim_handoff_qa_pass(self):
        t=self.draft_task()
        o.claim(self.data,t['id'],'EDT-01','prod-001')
        self.assertEqual('claimed',t['status'])
        with self.assertRaises(o.OrchestrationError):o.claim(self.data,t['id'],'OPS-01','prod-002')
        o.handoff(self.data,t['id'],'EDT-01','prod-001','source:official','articles/guide.html','Draft grounded in current docs')
        self.assertEqual('awaiting_qa',t['status'])
        with self.assertRaises(o.OrchestrationError):o.review(self.data,t['id'],'prod-001','PASS','qa:browser')
        o.review(self.data,t['id'],'independent-qa-001','PASS','qa:browser+sources')
        self.assertEqual('qa_passed',t['status'])
        self.assertEqual('OPS-01',t['owner'])
        self.assertEqual([],o.validate(self.data))
    def test_qa_rework_does_not_auto_pass(self):
        t=self.draft_task()
        o.claim(self.data,t['id'],'EDT-01','prod-001')
        o.handoff(self.data,t['id'],'EDT-01','prod-001','claim-source','articles/guide.html','Draft')
        o.review(self.data,t['id'],'qa-002','REWORK','review:1','Source dates incomplete')
        self.assertEqual('rework',t['status'])
        self.assertEqual('EDT-01',t['owner'])
        self.assertEqual('Source dates incomplete',t['fix_request']['reason'])
        o.claim(self.data,t['id'],'EDT-01','prod-003')
        o.handoff(self.data,t['id'],'EDT-01','prod-003','source:fixed','articles/guide.html','Updated dates')
        o.review(self.data,t['id'],'qa-004','REWORK','review:2','Same dates still wrong')
        self.assertEqual('blocked',t['status'])
        self.assertEqual('CEO-01',t['owner'])
    def test_qa_reject_escalates_ceo(self):
        t=self.draft_task()
        o.claim(self.data,t['id'],'EDT-01','prod-001')
        o.handoff(self.data,t['id'],'EDT-01','prod-001','source','articles/guide.html','Produced')
        o.review(self.data,t['id'],'qa-002','REJECT','review','False customer results')
        self.assertEqual('rejected',t['status'])
        self.assertEqual('CEO-01',t['owner'])
    def test_qa_requires_concrete_handoff(self):
        t=self.draft_task()
        with self.assertRaises(o.OrchestrationError):o.review(self.data,t['id'],'qa-001','PASS','made up pass')
        o.claim(self.data,t['id'],'EDT-01','prod-001')
        with self.assertRaises(o.OrchestrationError):o.handoff(self.data,t['id'],'EDT-01','prod-001','','articles/guide.html','Draft')
    def test_no_qa_bypass_for_publish(self):
        t=self.draft_task()
        with self.assertRaises(o.OrchestrationError):o.release(self.data,t['id'],'OPS-01','abc','https://example.org/')
        t.update({'status':'published','owner':'OPS-01'})
        self.assertTrue(any(x['code']=='PUBLISH_WITHOUT_QA' for x in o.validate(self.data)))
    def test_noindex_blocks_indexable_publication(self):
        t=self.draft_task()
        o.claim(self.data,t['id'],'EDT-01','prod-001')
        o.handoff(self.data,t['id'],'EDT-01','prod-001','source','index.html','Draft')
        o.review(self.data,t['id'],'qa-001','PASS','source-check')
        with tempfile.TemporaryDirectory() as d:
            pathlib.Path(d,'index.html').write_text('<meta name="robots" content="noindex,nofollow">')
            with self.assertRaises(o.OrchestrationError):
                o.release(self.data,t['id'],'OPS-01','commit','https://example.org/',pathlib.Path(d))
            pathlib.Path(d,'index.html').write_text('<html><h1>Valid</h1></html>')
            o.release(self.data,t['id'],'OPS-01','commit','https://example.org/',pathlib.Path(d))
        self.assertEqual('published',t['status'])
    def test_invalid_budget_and_unknown_role_and_cycles(self):
        self.data['tasks'][0]['spend_usd']=1
        self.assertTrue(any(x['code']=='SPEND' for x in o.validate(self.data)))
        self.data['tasks'][0]['spend_usd']=0
        t=self.draft_task();t['depends_on']=['ART-0001']
        self.data['tasks'][0]['depends_on']=['DRAFT-999']
        self.assertTrue(any(x['code']=='DEPENDENCY_CYCLE' for x in o.validate(self.data)))
        t['owner']='NOT-A-ROLE'
        self.assertTrue(any(x['code']=='OWNER' for x in o.validate(self.data)))
    def test_unfinished_dependency_cannot_be_claimed(self):
        t=self.draft_task();t['depends_on']=['ART-0001']
        with self.assertRaises(o.OrchestrationError):o.claim(self.data,t['id'],'EDT-01','prod')
    def test_idempotent_claim_same_run(self):
        t=self.draft_task()
        o.claim(self.data,t['id'],'EDT-01','prod-001');first=t['attempts']
        o.claim(self.data,t['id'],'EDT-01','prod-001')
        self.assertEqual(first,t['attempts'])
    def test_checkup_is_honest(self):
        result=o.checkup(self.data)
        self.assertTrue(result['safe'])
        self.assertIn('does not invoke LLMs',result['limitations'][0])
        self.assertEqual(len(self.data['tasks']),result['metrics']['task_count'])
    def test_missing_artifact_detected(self):
        with tempfile.TemporaryDirectory() as d:
            errors=o.validate(self.data,pathlib.Path(d))
            self.assertTrue(any(x['code']=='MISSING_ARTIFACT' for x in errors))



class TestCompletedState(unittest.TestCase):
    """Completed research/report task is closed but not a published website page."""
    def test_completed_is_terminal_and_current_state_valid(self):
        data = o.load_state()
        self.assertIn('completed', o.VALID_STATES)
        self.assertIn('completed', o.CLOSE_STATES)
        self.assertNotIn('completed', o.ACTIVE_STATES)
        self.assertFalse(any(issue['severity']=='CRITICAL' for issue in o.validate(data)), o.validate(data))

if __name__=='__main__':unittest.main()