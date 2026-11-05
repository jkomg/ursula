import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('checkin_verify', ROOT / 'scripts/checkin_verify.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
NOW = '2026-11-02T13:05:00Z'
FULL = [('gws_gmail_users_messages_list', {}), ('gws_gmail_users_messages_get', {'id': 'm1'}),
        ('gws_docs_documents_get', {'documentId': 'd1'}),
        ('ArtifactData', {'collection': 'notes', 'action': 'list'}),
        ('slack_read_channel', {'channel_id': 'D1'})]


def source(kind='drive', source_id='d2', count=1):
    return dict(kind=kind, id=source_id, title='Unread notes', reason='Read deferred', carry_count=count)


def run(partial=False):
    return dict(status='partial' if partial else 'complete', could_not=[], checks_clean=[], summary='Checked',
                window_start='2026-11-02T12:00:00Z', window_end=NOW, date='2026-11-02',
                watermark_before='2026-11-02T12:00:00Z', watermark_after=NOW,
                coverage=dict(notes_read=True, slack_dm_read=True, drive_docs_opened=1,
                              drive_docs_in_window=1, gmail_read=True, gmail_listed=1, gmail_opened=1,
                              outbox_stale=0, open_set=0, open_set_evaluated=0))


class CheckinVerify(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)

    def ledger(self, calls=FULL, marker=True):
        """Write the hash-chained ledger entries used by test_session_verify.py.

        A real hooked session starts with a session_start marker; marker=False omits it.
        A call's extra dict may override ts and session."""
        lines, prev = [], '0' * 64
        if marker and calls and not any(c[0] == 'session_start' for c in calls):
            calls = [('session_start', {'id': 'startup'})] + list(calls)
        for seq, call in enumerate(calls, 1):
            tool, args, *extra = call
            entry = dict(seq=seq, ts=NOW, session='s', tool=tool, args=args, error=False,
                         bytes=1, sha256='0', prev=prev)
            if extra:
                entry.update(extra[0])
            raw = json.dumps(entry, sort_keys=True).encode()
            prev = hashlib.sha256(raw).hexdigest()
            lines.append(raw)
        path = self.folder / 'ledger.jsonl'
        path.write_bytes(b'\n'.join(lines) + (b'\n' if lines else b''))
        return str(path)

    def close(self, r, calls=FULL):
        path = self.folder / 'run.json'
        path.write_text(json.dumps(r))
        findings = self.folder / 'findings'
        findings.mkdir(exist_ok=True)
        proc = subprocess.run([sys.executable, str(ROOT / 'scripts/checkin_close.py'), str(path),
                               str(findings), '--ledger', self.ledger(calls), '--now', NOW],
                              capture_output=True, text=True)
        self.assertIn(proc.returncode, (0, 1), proc.stderr)
        return json.loads(proc.stdout)

    def partial(self):
        r = run(partial=True)
        r['coverage'].update(drive_docs_in_window=2, gmail_listed=2)
        r['carried_sources'] = [source(), source('gmail', 'm2')]
        return r

    def test_complete_requires_every_listed_gmail_message_opened(self):
        r = run()
        r['coverage'].update(gmail_listed=61, gmail_opened=8)
        self.assertIn('Gmail: 8 opened of 61 listed', m.verify(r, []))
        r['coverage']['gmail_opened'] = 61
        self.assertEqual(m.verify(r, []), [])
        r['coverage'].update(gmail_listed=0, gmail_opened=0)
        self.assertEqual(m.verify(r, []), [])
        del r['coverage']['gmail_opened']
        self.assertTrue(m.verify(r, []))

    def test_ledger_log_oversize_requires_error_and_size_threshold(self):
        for error, size, expected in ((True, 49999, False), (True, 50000, True),
                                      (False, 50000, False)):
            with self.subTest(error=error, size=size):
                path = self.folder / 'hook.jsonl'
                response = ('error ' if error else 'notes ') + 'x' * (size - 6)
                proc = subprocess.run([sys.executable, str(ROOT / 'bin/ledger-log')],
                                      input=json.dumps(dict(tool_name='mcp__gws_docs_documents_get',
                                                            tool_input={'documentId': 'd1'},
                                                            tool_response=response)),
                                      env=dict(os.environ, URSULA_LEDGER=str(path)),
                                      capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                entry = json.loads(path.read_text().splitlines()[-1])
                self.assertEqual(entry.get('oversize', False), expected)
                self.assertEqual(entry['error'], error)

    def test_real_hook_records_gmail_ids_and_they_count_per_session(self):
        # End to end through bin/ledger-log: the ids the distinct count needs are written,
        # whether top-level, nested under params (gws_*), or named messageId.
        path = self.folder / 'hook.jsonl'
        events = [dict(hook_event_name='SessionStart', session_id='x', source='startup'),
                  dict(session_id='x', tool_name='mcp__g__google_gmail_messages_get',
                       tool_input={'userId': 'me', 'id': 'm1'}, tool_response={'id': 'm1'}),
                  dict(session_id='x', tool_name='mcp__g__google_gmail_messages_get',
                       tool_input={'userId': 'me', 'id': 'm1'}, tool_response={'id': 'm1'}),
                  dict(session_id='x', tool_name='mcp__g__gws_gmail_users_threads_get',
                       tool_input={'params': {'userId': 'me', 'id': 't9'}}, tool_response={'id': 't9'}),
                  dict(session_id='x', tool_name='mcp__g__gmail_read',
                       tool_input={'messageId': 'm2'}, tool_response={'id': 'm2'}),
                  dict(session_id='x', tool_name='mcp__g__gws_gmail_read',
                       tool_input={'args': ['--id', 'm3']}, tool_response={'id': 'm3'})]
        for ev in events:
            proc = subprocess.run([sys.executable, str(ROOT / 'bin/ledger-log')], input=json.dumps(ev),
                                  env=dict(os.environ, URSULA_LEDGER=str(path)), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
        facts, errs = m.ledger_facts(str(path), this_session=True)
        self.assertEqual(errs, [])
        self.assertEqual(facts['gmail_ids_opened'], {'m1', 't9', 'm2'})
        self.assertEqual(facts['gmail_opened'], 3)

    def test_oversize_doc_read_counts_but_other_errors_do_not(self):
        calls = [('gws_docs_documents_get', {'documentId': 'large'}, {'error': True, 'oversize': True}),
                 ('gws_drive_files_export', {'fileId': 'export'}, {'error': True, 'oversize': True}),
                 ('gws_docs_documents_get', {'documentId': 'failed'}, {'error': True}),
                 ('gws_drive_files_list', {'fileId': 'listing'}, {'error': True, 'oversize': True}),
                 ('gws_docs_documents_get', {'documentId': 'ok'})]
        facts, errs = m.ledger_facts(self.ledger(calls))
        self.assertEqual(errs, [])
        self.assertEqual(facts['docs_opened'], {'large', 'export', 'ok'})

    def test_gmail_opened_ids_only_successful_gets(self):
        calls = [('gws_gmail_users_messages_get', {'id': 'm1'}),
                 ('gmail_read', {'messageId': 'm2'}),
                 ('gws_gmail_users_messages_get', {'id': 'failed'}, {'error': True, 'oversize': True}),
                 ('gws_gmail_users_messages_list', {'id': 'listed'})]
        facts, errs = m.ledger_facts(self.ledger(calls))
        self.assertEqual(errs, [])
        self.assertEqual(facts['gmail_ids_opened'], {'m1', 'm2'})

    def test_partial_gaps_fully_carried_may_advance_with_or_without_ledger(self):
        r = self.partial()
        self.assertEqual(m.carry_ok(r), [])
        self.assertEqual(m.verify(r, []), [])
        self.assertEqual(m.verify(r, [], self.ledger()), [])
        out = self.close(r)
        self.assertTrue(out['verified'])
        self.assertEqual(out['state_checkin'], dict(watermark=NOW, slack_last_ts=None,
                                                   pending_sources=r['carried_sources']))
        self.assertEqual(out['carried'], 2)
        self.assertEqual(out['status_allowed'], 'partial')
        self.assertTrue(out['final_line'].startswith('Ursula: partial'))

    def test_gap_uncarried_blocks_partial_advancement(self):
        for kind in ('drive', 'gmail'):
            with self.subTest(kind=kind):
                r = self.partial()
                r['carried_sources'] = [s for s in r['carried_sources'] if s['kind'] != kind]
                self.assertTrue(m.carry_ok(r))
                self.assertIn('partial run advanced the watermark', m.verify(r, []))
                self.assertIsNone(self.close(r)['state_checkin'])

    def test_partial_carry_preconditions(self):
        for key, value in (('notes_read', False), ('slack_dm_read', False), ('gmail_listed', None)):
            r = self.partial()
            r['coverage'][key] = value
            self.assertTrue(m.carry_ok(r), key)
            self.assertIn('partial run advanced the watermark', m.verify(r, []))
        r = self.partial()
        r['coverage']['slack_dm_read'] = None
        self.assertEqual(m.carry_ok(r), [])

    def test_carried_items_need_id_and_reason(self):
        for key in ('id', 'reason'):
            r = self.partial()
            r['carried_sources'][0][key] = ''
            self.assertTrue(m.carry_ok(r))
            self.assertIn('partial run advanced the watermark', m.verify(r, []))

    def test_unavailable_sources_cannot_be_carried_past_watermark(self):
        for token in ('403', '502', 'CONNECT_TIMEOUT', 'not available'):
            r = self.partial()
            r['could_not'] = ['source: ' + token]
            self.assertTrue(m.carry_ok(r), token)
            self.assertIsNone(self.close(r)['state_checkin'])

    def test_pending_silently_dropped_or_wrong_increment_fails(self):
        for with_ledger in (False, True):
            for old in (source(), source('gmail', 'm2')):
                r = run(partial=True)
                r['pending_in'] = [old]
                path = self.ledger() if with_ledger else None
                self.assertTrue(any('pending source' in e for e in m.verify(r, [], path)))
                r['carried_sources'] = [copy.deepcopy(old)]
                self.assertTrue(any('pending source' in e for e in m.verify(r, [], path)))
                r['carried_sources'][0]['carry_count'] = 2
                self.assertFalse(any('pending source' in e for e in m.verify(r, [], path)))

    def test_pending_opened_in_ledger_or_opened_ids_is_handled(self):
        for kind, source_id in (('drive', 'd1'), ('gmail', 'm1')):
            r = run()
            r['pending_in'] = [source(kind, source_id)]
            self.assertEqual(m.verify(r, [], self.ledger()), [])
            self.assertTrue(any('pending source' in e for e in m.verify(r, [])))
            r['opened_ids'] = [source_id]
            self.assertEqual(m.verify(r, []), [])
            self.assertTrue(any('pending source' in e for e in m.verify(r, [], self.ledger([]))))

    def test_three_carries_requires_matching_new_finding(self):
        for count in (3, 4):
            r = self.partial()
            r['carried_sources'][0]['carry_count'] = count
            self.assertIn('source d2 carried 3 times: raise it as a finding', m.verify(r, []))
            r['findings_new_keys'] = ['unreadable-source-other']
            self.assertIn('source d2 carried 3 times: raise it as a finding', m.verify(r, []))
            r['findings_new_keys'] = ['unreadable-source-d2']
            self.assertEqual(m.verify(r, []), [])

    def test_partial_can_remain_honest_without_advancing(self):
        r = self.partial()
        r['watermark_after'] = r['watermark_before']
        r['carried_sources'] = []
        self.assertEqual(m.verify(r, []), [])
        out = self.close(r)
        self.assertTrue(out['verified'])
        self.assertIsNone(out['state_checkin'])
        self.assertEqual(out['status_allowed'], 'partial')

    def test_complete_close_includes_empty_pending_sources(self):
        out = self.close(run())
        self.assertTrue(out['verified'])
        self.assertEqual(out['status_allowed'], 'complete')
        self.assertEqual(out['state_checkin']['pending_sources'], [])
        self.assertEqual(out['carried'], 0)

    def test_failed_run_cannot_advance(self):
        r = run()
        r['status'] = 'failed'
        self.assertIn('failed run advanced the watermark', m.verify(r, []))

    def test_partial_needs_nonempty_ledger_and_backed_read_claims(self):
        out = self.close(self.partial(), [])
        self.assertFalse(out['verified'])
        self.assertIsNone(out['state_checkin'])
        for tool in ('gws_docs_documents_get', 'gws_gmail_users_messages_get',
                     'gws_gmail_users_messages_list', 'slack_read_channel', 'ArtifactData'):
            calls = [c for c in FULL if c[0] != tool]
            out = self.close(self.partial(), calls)
            self.assertFalse(out['verified'], tool)
            self.assertIsNone(out['state_checkin'], tool)

    def test_calls_from_an_earlier_session_do_not_verify_a_new_run(self):
        # 4 Nov audit: every call dated 1 October still verified a 2 November run.
        old = [(t, a, {'ts': '2026-10-01T09:00:00Z', 'session': 'old'}) for t, a in FULL]
        calls = [('session_start', {'id': 'old'}, {'ts': '2026-10-01T08:59:00Z', 'session': 'old'})] + old + \
                [('session_start', {'id': 'startup'}, {'session': 'new'})]
        errs = m.verify(run(), [], self.ledger(calls))
        self.assertTrue(any('no calls recorded' in e for e in errs), errs)
        out = self.close(run(), calls)
        self.assertFalse(out['verified'])
        self.assertIsNone(out['state_checkin'])
        self.assertEqual(out['ledger']['calls'], 0)

    def test_concurrent_older_session_calls_do_not_count(self):
        # Same clock, but another session's calls: they are not this run's evidence.
        calls = [('session_start', {'id': 'startup'}, {'session': 'other'}),
                 ('session_start', {'id': 'startup'}, {'session': 'new'})] + \
                [(t, a, {'session': 'other'}) for t, a in FULL]
        self.assertTrue(m.verify(run(), [], self.ledger(calls)))

    def test_ledger_without_session_marker_fails(self):
        errs = m.verify(run(), [], self.ledger(FULL, marker=False))
        self.assertTrue(any('no session_start marker' in e for e in errs), errs)

    def test_repeated_gmail_reads_count_once(self):
        # 4 Nov audit: two reads of m1 passed a claim of two messages opened.
        r = run()
        r['coverage'].update(gmail_listed=2, gmail_opened=2)
        calls = FULL + [('gws_gmail_users_messages_get', {'id': 'm1'})]
        errs = m.verify(r, [], self.ledger(calls))
        self.assertTrue(any('1 Gmail messages opened, run claims 2' in e for e in errs), errs)
        calls = FULL + [('gws_gmail_users_messages_get', {'id': 'm2'})]
        self.assertEqual(m.verify(r, [], self.ledger(calls)), [])

    def test_gmail_read_without_an_id_does_not_count(self):
        calls = [c for c in FULL if c[0] != 'gws_gmail_users_messages_get'] + [('gws_gmail_read', {})]
        facts, _ = m.ledger_facts(self.ledger(calls), this_session=True)
        self.assertEqual(facts['gmail_opened'], 0)
        self.assertTrue(m.verify(run(), [], self.ledger(calls)))

    def test_malformed_new_source_lists_return_errors(self):
        for field in ('carried_sources', 'pending_in'):
            for value in ([None], ['bad'], {'bad': 'shape'}):
                r = self.partial()
                r[field] = value
                self.assertTrue(m.verify(r, []), (field, value))


if __name__ == '__main__':
    unittest.main()
