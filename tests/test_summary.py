"""Known-answer, validation, and command-line checks."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from summary import summarize

SCRIPT = Path(__file__).resolve().parents[1] / 'summary.py'


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'input.csv'

    def write(self, text):
        self.path.write_text(text, encoding='utf-8')

    def test_known_answer(self):
        self.write('value\n1\n2\n3\n4\n5\n')
        result = summarize(self.path, 'value')
        self.assertEqual({k: result[k] for k in
            ('n', 'mean', 'median', 'minimum', 'maximum')},
            dict(n=5, mean=3, median=3, minimum=1, maximum=5))
        self.assertTrue(math.isclose(result['sample_sd'], math.sqrt(2.5)))

    def test_negative_and_constant(self):
        self.write('value\n-2\n-2\n')
        self.assertEqual(summarize(self.path, 'value')['sample_sd'], 0)

    def test_reject_invalid_inputs(self):
        cases = ['wrong\n1\n2\n', 'value\n', 'value\n1\n',
                 'value\n1\n \n', 'value\n1\ntext\n',
                 'value\n1\nnan\n', 'value\n1\ninf\n',
                 'value,value\n1,2\n3,4\n', 'value\n1,2\n3\n']
        for text in cases:
            with self.subTest(text=text):
                self.write(text)
                with self.assertRaises(ValueError):
                    summarize(self.path, 'value')

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            summarize(self.path, 'value')

    def test_cli_success(self):
        self.write('value\n1\n2\n3\n4\n5\n')
        output = self.path.with_suffix('.json')
        run = subprocess.run([sys.executable, str(SCRIPT), str(self.path),
            '--column', 'value', '--output', str(output)], capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(output.read_text())
        self.assertEqual(result['statistics']['mean'], 3)
        self.assertEqual(len(result['input_sha256']), 64)

    def test_cli_failure(self):
        self.write('value\n1\ninvalid\n')
        output = self.path.with_suffix('.json')
        run = subprocess.run([sys.executable, str(SCRIPT), str(self.path),
            '--column', 'value', '--output', str(output)], capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertFalse(output.exists())

    def test_input_cannot_be_overwritten(self):
        original = 'value\n1\n2\n'
        self.write(original)
        run = subprocess.run([sys.executable, str(SCRIPT), str(self.path),
            '--column', 'value', '--output', str(self.path)], capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(self.path.read_text(), original)


if __name__ == '__main__':
    unittest.main()
