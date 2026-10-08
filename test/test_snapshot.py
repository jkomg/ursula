"""Checks the portable renderer, not the agent cadence or any connector."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("snapshot", ROOT / "scripts/render_snapshot.py")
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


class SnapshotTests(unittest.TestCase):
    def export(self):
        return {
            "generated_at": "2026-09-30T15:00:00Z",
            "runs": {"2026-09-30-plan": {
                "date": "2026-09-30", "mode": "dry-run", "status": "partial",
                "summary": "Jira read; Slack unavailable", "created": 0,
                "skipped": 4, "edited": 0, "findings_new": 1, "findings_carried": 0,
                "sources": {"found": 2, "expected": 3, "unmatched_meetings": ["Partner sync"]},
                "could_not": ["Slack unavailable"], "checks_clean": ["deadline-inversion"]}},
            "findings": {"review": {"title": "Blocked review", "rank": 1, "status": "open",
                "check": "self-blocking", "evidence": "Waiting for operator",
                "consequence": "Launch delayed", "recommendation": "Review the proposal",
                "refs": [{"label": "Ticket", "url": "https://example.com/issue/OPS-1"}]}},
            "hires": {"sam": {"name": "Sam", "board": "HIRE", "scanned_at": "2026-09-30T14:00:00Z",
                "summary": "Review needed", "needs_me": [{"key": "HIRE-1", "title": "Access", "why": "Approval"}],
                "agenda": ["Decide access scope"], "could_not": []}},
            "issues": [{"key": "OPS-1", "title": "Review proposal", "status": "Blocked", "due": None}]
        }

    def test_required_outcomes_and_hire_agenda_render(self):
        board = snapshot.render(self.export())
        for content in ("Snapshot observed", "partial", "Already tracked: 4", "Partner sync",
                        "Slack unavailable", "Review the proposal", "Decide access scope"):
            self.assertIn(content, board)
        self.assertNotIn("<script", board)

    def test_incomplete_run_does_not_look_complete(self):
        data = self.export()
        run = data["runs"]["2026-09-30-plan"]
        run["status"] = "complete"
        del run["could_not"]
        del run["sources"]["unmatched_meetings"]
        board = snapshot.render(data)
        self.assertIn("Incomplete record", board)
        self.assertIn("Not recorded", board)
        data = self.export()
        data["runs"]["2026-09-30-plan"]["could_not"] = None
        self.assertIn("Incomplete record", snapshot.render(data))

    def test_untrusted_text_and_links(self):
        data = self.export()
        data["findings"]["review"]["title"] = '<script>alert("x")</script>'
        data["findings"]["review"]["refs"] = [
            {"label": "Bad link", "url": 'javascript:alert(1)'},
            {"label": "Unsafe credentials", "url": "https://user:password@example.com"},
            {"label": '<img src=x onerror=alert(1)>', "url": "https://example.com/?a=1&b=2"}]
        board = snapshot.render(data)
        self.assertNotIn("<script", board)
        self.assertNotIn("javascript:", board)
        self.assertNotIn("password@", board)
        self.assertIn("&lt;script&gt;", board)
        self.assertIn("?a=1&amp;b=2", board)

    def test_observation_timestamp_and_collection_shapes_required(self):
        for data in ({}, {"generated_at": "2026-09-30"},
                     {"generated_at": "bad"},
                     {"generated_at": "2026-09-30T15:00:00Z", "runs": []}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                snapshot.render(data)

    def test_cli_preserves_existing_output_on_invalid_export(self):
        with tempfile.TemporaryDirectory() as temp:
            source, dest = Path(temp) / "export.json", Path(temp) / "board.html"
            source.write_text(json.dumps(self.export()))
            command = [sys.executable, str(ROOT / "scripts/render_snapshot.py"), str(source), "--out", str(dest)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            saved = dest.read_bytes()
            source.write_text('{"generated_at": "bad"}')
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(dest.read_bytes(), saved)
            self.assertFalse(list(Path(temp).glob(".ursula-*")))


if __name__ == "__main__":
    unittest.main()
