import json
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'skills'))
from skill_audit import audit, read_frontmatter
from new_role import create_draft


class SkillPackTests(unittest.TestCase):
    def test_all_roles_have_valid_candidate_or_approved_skill(self):
        self.assertEqual([], audit(HERE))

    def test_frontmatter_requires_wrapping(self):
        with self.assertRaises(ValueError):
            read_frontmatter('no frontmatter')

    def test_draft_generator_creates_file_without_role_activation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            result = create_draft('PRD-01', 'Product', 'Validate user needs', root)
            self.assertTrue(result.is_file())
            self.assertIn('status: draft', result.read_text())
            self.assertFalse((root / 'skills/manifest.json').exists())
            with self.assertRaises(FileExistsError):
                create_draft('PRD-01', 'Product', 'Try to overwrite', root)

    def test_invalid_role_cannot_escape_draft_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                create_draft('../OUTSIDE', 'Bad', 'Bad', pathlib.Path(temp))

    def test_approval_requires_independent_qa_and_evaluation(self):
        with tempfile.TemporaryDirectory() as temp:
            base = pathlib.Path(temp)
            (base / 'state').mkdir()
            (base / 'skills/CEO-01').mkdir(parents=True)
            main = HERE / 'skills/CEO-01/SKILL.md'
            source = main.read_text()
            (base / 'skills/CEO-01/SKILL.md').write_text(source.replace('status: candidate','status: approved'))
            (base / 'state/agent_registry.json').write_text(json.dumps({'roles': [{'id': 'CEO-01'}]}))
            (base / 'skills/manifest.json').write_text(json.dumps({'schema_version':'1.0','skills':[{'role_id':'CEO-01','path':'skills/CEO-01/SKILL.md','status':'approved'}]}))
            self.assertTrue(any('approval missing' in x for x in audit(base)))
            self.assertTrue(any('five-case' in x for x in audit(base)))


if __name__ == '__main__':
    unittest.main()