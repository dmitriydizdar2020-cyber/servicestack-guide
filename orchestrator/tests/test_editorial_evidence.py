import unittest
from scripts.check_editorial_evidence import risky_sources

class EditorialEvidenceTests(unittest.TestCase):
    def test_blocks_affiliate_landing_page_as_feature_evidence(self):
        html='<ol class="sources"><li><a href="https://www.hostinger.com/affiliates">Source</a></li></ol>'
        self.assertEqual(len(risky_sources(html)),1)
    def test_does_not_block_official_product_help(self):
        html='<ol class="sources"><li><a href="https://www.hostinger.com/support/6463265-help/">Product documentation</a></li></ol>'
        self.assertEqual(risky_sources(html),[])
    def test_respects_non_source_affiliate_cta(self):
        html='<a href="https://www.site123.com/?aff=123" rel="sponsored">Try</a>'
        self.assertEqual(risky_sources(html),[])
    def test_blocks_tracking_links_as_sources(self):
        html='<ol class="sources"><li><a href="https://example.com/features?aff=1">Source</a></li></ol>'
        self.assertEqual(len(risky_sources(html)),1)

if __name__ == "__main__":
    unittest.main()
