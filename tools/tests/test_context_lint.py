"""Negative fixtures exercise the real context linter in isolated scratch repos."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
class ContextLint(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ['scripts', 'accounts', 'sections/slideshows', 'research', '.pi/extensions']:
            (self.root/name).mkdir(parents=True, exist_ok=True)
        for name in ['lint','link-skills']:
            shutil.copy2(ROOT/'scripts'/name,self.root/'scripts'/name)
        (self.root/'sections/slideshows/rules.md').write_text('### H-known\nKnown rule.\n')
        subprocess.run(['git','init','-q',str(self.root)],check=True)
    def run_lint(self):
        return subprocess.run([str(self.root/'scripts/lint')],capture_output=True,text=True)
    def test_clean_fixture_passes(self):
        result=self.run_lint(); self.assertEqual(result.returncode,0,result.stdout)
    def test_broken_research_markdown_link_fails(self):
        (self.root/'research/report.md').write_text('[evidence](missing.md)\n')
        result=self.run_lint(); self.assertNotEqual(result.returncode,0)
        self.assertIn('Markdown link does not exist',result.stdout)
    def test_unknown_house_rule_fails(self):
        (self.root/'sections/slideshows/README.md').write_text('Use `H-missing`.\n')
        result=self.run_lint(); self.assertNotEqual(result.returncode,0)
        self.assertIn('undefined house rule',result.stdout)
    def test_missing_runtime_import_fails(self):
        (self.root/'.pi/extensions/example.ts').write_text('import x from "./missing.mjs";\n')
        result=self.run_lint(); self.assertNotEqual(result.returncode,0)
        self.assertIn('runtime import does not exist',result.stdout)
    def test_preserved_history_is_not_active_context(self):
        (self.root/'history').mkdir()
        (self.root/'history/prior.md').write_text('[old](missing.md)\n`core/removed.md`\n')
        result=self.run_lint(); self.assertEqual(result.returncode,0,result.stdout)

if __name__=='__main__':unittest.main()
