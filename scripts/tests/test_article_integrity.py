import unittest
from scripts.article_integrity import check_article

def fixture(words=520,h2=5,refs=2,include_disclosure=True,include_caption=True):
    markup='<!doctype html><main>'
    if include_disclosure:markup+='<p class="editorial-disclosure">Transparent editorial methods and relationships.</p>'
    markup+='<figure><img src="pic.webp" alt="Useful picture">'
    if include_caption:markup+='<figcaption>Original visual.</figcaption>'
    markup+='</figure><div class="article-body">'
    markup+=(' '.join(['useful']*words))
    markup+=''.join(f'<h2>Section {i}</h2>' for i in range(h2))
    markup+=''.join(f'<a href="https://docs{i}.example.org/help">Official reference</a>' for i in range(refs))
    markup+='</div></main>'
    return markup

class TestArticleIntegrity(unittest.TestCase):
    def test_complete_page(self):
        self.assertEqual(check_article(fixture()),[])
    def test_short_placeholder_article(self):
        issues=check_article(fixture(words=2)+"[TODO]")
        self.assertTrue(any('fewer than' in i for i in issues))
        self.assertTrue(any('placeholder' in i for i in issues))
    def test_requires_real_references_and_disclosure(self):
        issues=check_article(fixture(refs=0,include_disclosure=False,include_caption=False))
        self.assertTrue(any('source references' in i for i in issues))
        self.assertTrue(any('disclosure' in i for i in issues))
        self.assertTrue(any('caption' in i for i in issues))

if __name__=="__main__":unittest.main()
