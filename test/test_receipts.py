"""Synthetic helper tests; these do not exercise live connectors or agent behavior."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_receipts import verify, verify_files, read_artifact
from fetch_inputs import capture


def fixture():
    text = 'Please review the résumé by Friday; this is a suggestion.'
    source = dict(source_type='gmail', source_id='m1', text=text,
                  sha256=hashlib.sha256(text.encode()).hexdigest())
    receipt = {k: source[k] for k in ('source_type', 'source_id', 'sha256')}
    receipt['exact_quote'] = 'review the résumé by Friday'
    return ({'run_id': 'r1', 'coverage': {'gmail': 'complete'}, 'sources': [source]},
            {'run_id': 'r1', 'items': [{'id': 'i1', 'title': 'Review résumé', 'source_receipts': [receipt]}]})


class Receipts(unittest.TestCase):
    def test_valid_unicode(self):
        result = verify(*fixture())
        self.assertEqual(result['receipts'], 1)
        self.assertEqual(result['semantic_review'], 'pending')

    def test_negative_cases(self):
        for case in ('run', 'hash', 'quote', 'id', 'duplicate_source', 'duplicate_item',
                     'empty_receipts', 'whitespace', 'null', 'no_items', 'coverage', 'unused_bad_hash'):
            with self.subTest(case=case):
                inputs, proposals = fixture()
                item = proposals['items'][0]
                ref = item['source_receipts'][0]
                if case == 'run': proposals['run_id'] = 'r2'
                elif case == 'hash': inputs['sources'][0]['text'] += 'altered'
                elif case == 'quote': ref['exact_quote'] = 'unmentioned deadline'
                elif case == 'id': ref['source_id'] = 'missing'
                elif case == 'duplicate_source': inputs['sources'] *= 2
                elif case == 'duplicate_item': proposals['items'] *= 2
                elif case == 'empty_receipts': item['source_receipts'] = []
                elif case == 'whitespace': ref['exact_quote'] = ' '
                elif case == 'null': item['title'] = None
                elif case == 'no_items': proposals['items'] = []
                elif case == 'coverage': inputs['coverage'] = {}
                elif case == 'unused_bad_hash':
                    source = copy.deepcopy(inputs['sources'][0]); source.update(source_id='unused', sha256='bad')
                    inputs['sources'].append(source)
                with self.assertRaises(ValueError): verify(inputs, proposals)

    def test_composite_ids_are_tuples(self):
        inputs, proposals = fixture()
        a = inputs['sources'][0]
        a.update(source_type='a:b', source_id='c')
        b = dict(a, source_type='a', source_id='b:c')
        inputs['sources'].append(b)
        inputs['coverage'] = {'a:b': 'complete', 'a': 'complete'}
        proposals['items'][0]['source_receipts'][0].update(source_type='a', source_id='b:c')
        self.assertEqual(verify(inputs, proposals)['sources'], 2)

    def test_partial_coverage_is_not_completion(self):
        inputs, proposals = fixture()
        inputs['coverage']['calendar'] = 'unavailable'
        self.assertFalse(verify(inputs, proposals)['declared_coverage_complete'])

    def test_file_hashes_and_cli_failure_no_raw_text(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory)/name for name in ('inputs.json', 'proposals.json')]
            for path, value in zip(paths, fixture()): path.write_text(json.dumps(value), encoding='utf-8')
            report = verify_files(*paths)
            self.assertEqual(report['inputs_sha256'], hashlib.sha256(paths[0].read_bytes()).hexdigest())
            paths[1].write_text('{"run_id":"PRIVATE-CONTENT","items":[]}', encoding='utf-8')
            result = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1]/'scripts/verify_receipts.py'), *map(str, paths)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('PRIVATE-CONTENT', result.stdout + result.stderr)

    def test_duplicate_json_fields_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'input.json'; path.write_text('{"items":[],"items":[]}')
            with self.assertRaises(ValueError): read_artifact(path)


class Capture(unittest.TestCase):
    def adapter(self, data):
        return [sys.executable, '-c', 'import sys; sys.stdout.write(sys.argv[1])', json.dumps(data)]

    def test_capture_hash_and_coverage(self):
        data = {'sources': [{'source_type':'gmail', 'source_id':'m1', 'text':'fixture only'}], 'coverage':{'gmail':'partial'}}
        result = capture(self.adapter(data), 'r1')
        self.assertEqual(result['sources'][0]['sha256'], hashlib.sha256(b'fixture only').hexdigest())
        self.assertEqual(result['coverage']['gmail'], 'partial')

    def test_capture_rejects_missing_coverage_duplicates_and_bad_adapter(self):
        for data in ({'sources':[]}, {'sources':[{}, {}], 'coverage':{'gmail':'complete'}}):
            with self.assertRaises(ValueError): capture(self.adapter(data), 'r1')
        with self.assertRaises(ValueError): capture([sys.executable, '-c', 'raise SystemExit(1)'], 'r1')


if __name__ == '__main__':
    unittest.main()
