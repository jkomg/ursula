import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AuditTrend(unittest.TestCase):
    """silent-green is judged against the findings open on each run's date (PR #2 review)."""

    def trend(self, runs, finds):
        with tempfile.TemporaryDirectory() as tmp:
            rd, fd = Path(tmp, 'runs'), Path(tmp, 'finds')
            rd.mkdir(), fd.mkdir()
            for i, r in enumerate(runs):
                Path(rd, f'r{i}.json').write_text(json.dumps(dict(session='checkin', status='complete',
                                                                  coverage={'x': 1}, **r)))
            for i, f in enumerate(finds):
                Path(fd, f'f{i}.json').write_text(json.dumps(dict(check='deadline-inversion', **f)))
            out = subprocess.run([sys.executable, str(ROOT / 'scripts/audit_trend.py'), str(rd), str(fd)],
                                 capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertNotIn('DeprecationWarning', out.stderr)
        head = out.stdout.splitlines()[0].split('|')
        col = [c.strip() for c in head].index('silent-green')
        return {line.split('|')[1].strip(): int(line.split('|')[col].strip())
                for line in out.stdout.splitlines()[2:] if line.startswith('| 2026')}

    def test_finding_raised_after_the_run_does_not_mark_it(self):
        rows = self.trend([dict(date='2026-10-01', checks_clean=['deadline-inversion'])],
                          [dict(status='open', first_seen='2026-11-01')])
        self.assertEqual(rows['2026-w40'], 0)

    def test_finding_open_then_resolved_since_still_marks_it(self):
        rows = self.trend([dict(date='2026-10-01', checks_clean=['deadline-inversion'])],
                          [dict(status='resolved', first_seen='2026-09-20', closed_at='2026-10-10T09:00:00Z')])
        self.assertEqual(rows['2026-w40'], 1)

    def test_finding_closed_before_the_run_does_not_mark_it(self):
        rows = self.trend([dict(date='2026-10-01', checks_clean=['deadline-inversion'])],
                          [dict(status='resolved', first_seen='2026-09-20', closed_at='2026-09-30T09:00:00Z')])
        self.assertEqual(rows['2026-w40'], 0)


if __name__ == '__main__':
    unittest.main()
