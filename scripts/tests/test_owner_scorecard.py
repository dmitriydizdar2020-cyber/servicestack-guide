from pathlib import Path
import tempfile
import unittest
from scripts.owner_scorecard import load_gsc, load_merchant_events, score_tasks, render

class ScorecardTests(unittest.TestCase):
    def test_absent_external_data_stays_unknown(self):
        body = render('2026-11-12', score_tasks({'tasks': []}, '2026-11-12'), None, None)
        self.assertIn('**UNKNOWN**', body)
        self.assertNotIn('0 clicks', body)

    def test_published_must_have_separate_qa(self):
        bad = {'tasks': [{'id':'ART-X','artifact_path':'articles/test.html','status':'published',
                          'qa':{'decision':'PASS','reviewer_role':'EDT-01'}}]}
        with self.assertRaises(ValueError):
            score_tasks(bad, '2026-11-12')

    def test_gsc_pages_export(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'Pages.csv'
            path.write_text('Top pages,Clicks,Impressions,CTR,Position\n/a,2,40,5%,10\n/b,3,60,5%,12\n',encoding='utf-8')
            metrics = load_gsc(path)
            self.assertEqual((metrics['clicks'],metrics['impressions'],metrics['ctr_pct']), (5,100,5.0))

    def test_merchant_event_evidence_required(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'merchant.csv'
            path.write_text('event_id,date,merchant,kind,amount,currency,evidence\na,2026-11-12,Merchant,commission_paid,12.50,USD,\n',encoding='utf-8')
            with self.assertRaises(ValueError):
                load_merchant_events(path)
            path.write_text('event_id,date,merchant,kind,amount,currency,evidence\na,2026-11-12,Merchant,commission_paid,12.50,USD,report-123\n',encoding='utf-8')
            self.assertEqual(load_merchant_events(path)['reported_paid_by_currency']['USD'], '12.50')

if __name__ == '__main__':
    unittest.main()
