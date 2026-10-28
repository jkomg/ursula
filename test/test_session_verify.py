import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('session_verify', ROOT / 'scripts/session_verify.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

SINCE = '2026-11-02T13:00:00+00:00'


def ledger(calls, marker=True):
    """Write a hash-chained ledger like bin/ledger-log does; calls are (ts, tool, args)."""
    if marker and not any(c[1] == 'session_start' for c in calls):
        calls = [('2026-11-02T13:00:00Z', 'session_start', {'id': 'startup'})] + list(calls)
    lines, prev = [], '0' * 64
    for seq, (ts, tool, args) in enumerate(calls, 1):
        raw = json.dumps({'seq': seq, 'ts': ts, 'session': 's', 'tool': tool, 'args': args, 'error': False,
                          'bytes': 1, 'sha256': '0', 'prev': prev}, sort_keys=True).encode()
        prev = hashlib.sha256(raw).hexdigest()
        lines.append(raw)
    d = tempfile.mkdtemp()
    p = Path(d) / 'ledger.jsonl'
    p.write_bytes(b'\n'.join(lines) + b'\n')
    return str(p)


NOW = '2026-11-02T13:05:00Z'
FULL = [(NOW, 'gws_gmail_users_messages_list', {'q': 'x'}), (NOW, 'gws_gmail_users_messages_get', {'id': 'm1'}),
        (NOW, 'gws_calendar_events_list', {}),
        (NOW, 'searchJiraIssuesUsingJql', {'jql': 'x'}), (NOW, 'gws_docs_documents_get', {'documentId': 'd1'}),
        (NOW, 'gws_docs_documents_get', {'documentId': 'd2'}), (NOW, 'slack_read_channel', {'channel_id': 'D1'})]


def run(**cov):
    base = dict(gmail_read=True, calendar_read=True, jira_read=True, drive_docs_opened=2,
                drive_docs_in_window=2, gmail_listed=10, gmail_opened=1, calendar_events=30)
    base.update(cov)
    return {'status': 'complete', 'coverage': base}


RECOUNT = {'gmail_in_window': 10, 'calendar_events': 30, 'drive_docs_in_window': 2}


class SessionVerify(unittest.TestCase):
    def errs(self, r, calls, recount=RECOUNT):
        out = m.verify(r, ledger(calls), SINCE, recount)
        return out if isinstance(out, list) else out[0]

    def test_backed_claims_pass(self):
        self.assertEqual(self.errs(run(), FULL), [])

    def test_claimed_email_read_without_a_gmail_call_fails(self):
        # The failure that started this: "I checked your email" with no email call.
        calls = [c for c in FULL if 'gmail' not in c[1]]
        self.assertTrue(any('Gmail read' in e for e in self.errs(run(), calls)))

    def test_partial_run_cannot_claim_a_read_either(self):
        calls = [c for c in FULL if 'gmail' not in c[1]]
        r = run()
        r['status'] = 'partial'
        self.assertTrue(any('Gmail read' in e for e in self.errs(r, calls)))

    def test_gmail_call_from_an_earlier_session_does_not_count(self):
        calls = [('2026-11-01T09:00:00Z', 'gws_gmail_users_messages_list', {})] + \
                [c for c in FULL if 'gmail' not in c[1]]
        self.assertTrue(any('Gmail read' in e for e in self.errs(run(), calls)))

    def test_more_documents_claimed_than_opened(self):
        self.assertTrue(any('documents opened' in e for e in self.errs(run(drive_docs_opened=5), FULL)))

    def test_recount_catches_invented_and_missed_coverage(self):
        e = self.errs(run(gmail_listed=30), FULL, {'gmail_in_window': 25})
        self.assertTrue(any('claims 30' in x for x in e))
        e = self.errs(run(calendar_events=20), FULL, {'calendar_events': 25})
        self.assertTrue(any('covered 20 of 25' in x for x in e))
        self.assertEqual(self.errs(run(), FULL), [])

    def test_tampered_ledger_fails(self):
        path = ledger(FULL)
        lines = Path(path).read_bytes().splitlines()
        self.assertIn(b'"q"', lines[1])
        lines[1] = lines[1].replace(b'"q"', b'"z"')   # edit the first entry; the second's prev no longer matches
        Path(path).write_bytes(b'\n'.join(lines) + b'\n')
        out = m.verify(run(), path, SINCE, RECOUNT)
        self.assertTrue(any('chain broken' in e for e in out[0]))

    def test_no_coverage_block_fails(self):
        self.assertTrue(m.verify({'status': 'complete'}, ledger(FULL), SINCE))


if __name__ == '__main__':
    unittest.main()


class Tightened(unittest.TestCase):
    """Findings from the 2026-10-28 antagonist review."""

    def errs(self, r, calls, recount=RECOUNT):
        out = m.verify(r, ledger(calls), SINCE, recount)
        return out if isinstance(out, list) else out[0]

    def test_listing_mail_is_not_reading_it(self):
        calls = [c for c in FULL if c[1] != 'gws_gmail_users_messages_get']
        self.assertTrue(any('listing ids is not reading' in e for e in self.errs(run(gmail_opened=0), calls)))

    def test_complete_run_needs_a_recount(self):
        self.assertTrue(any('no independent recount' in e for e in self.errs(run(), FULL, None)))

    def test_recount_missing_a_claimed_count_fails(self):
        e = self.errs(run(), FULL, {'gmail_in_window': 10, 'drive_docs_in_window': 2})
        self.assertTrue(any('missing calendar_events' in x for x in e))

    def test_since_before_the_recorded_session_start_fails(self):
        calls = [('2026-11-02T13:02:00Z', 'session_start', {'id': 'startup'})] + FULL
        self.assertTrue(any('earlier than this session' in e for e in self.errs(run(), calls)))
        out = m.verify(run(), ledger(calls), '2026-11-02T13:02:00+00:00', RECOUNT)
        self.assertEqual(out[0], [])

    def test_complete_run_must_state_counts_as_integers(self):
        self.assertTrue(any('as a count' in e for e in self.errs(run(gmail_listed='lots'), FULL)))

    def test_no_session_marker_fails(self):
        out = m.verify(run(), ledger(FULL, marker=False), SINCE, RECOUNT)
        self.assertTrue(any('no session_start marker' in e for e in out[0]))

    def test_gmail_read_needs_an_open_unless_the_recount_confirms_no_mail(self):
        calls = [c for c in FULL if c[1] != 'gws_gmail_users_messages_get']
        e = self.errs(run(gmail_listed=0, gmail_opened=0), calls)
        self.assertTrue(any('not reading' in x for x in e))
        e = self.errs(run(gmail_listed=0, gmail_opened=0), calls,
                      {'gmail_in_window': 0, 'calendar_events': 30, 'drive_docs_in_window': 2})
        self.assertFalse(any('not reading' in x for x in e))
