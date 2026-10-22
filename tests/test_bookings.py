"""Regression check for the synthetic room-booking research fixture."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from summary import summarize

class BookingTests(unittest.TestCase):
    def test_booking_statistics(self):
        result = summarize('data/bookings.csv', 'duration_minutes')
        self.assertEqual(result['n'], 5)
        self.assertEqual(result['mean'], 72)
        self.assertEqual(result['median'], 60)
        self.assertEqual(result['minimum'], 30)
        self.assertEqual(result['maximum'], 120)
        self.assertAlmostEqual(result['sample_sd'], 34.20526275297414)

    def test_input_hash_matches_actual_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'result.json'
            subprocess.run([sys.executable, 'summary.py', 'data/bookings.csv',
                '--column', 'duration_minutes', '--output', str(output)], check=True)
            payload = json.loads(output.read_text())
            self.assertEqual(payload['input_sha256'],
                hashlib.sha256(Path('data/bookings.csv').read_bytes()).hexdigest())
