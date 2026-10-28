#!/usr/bin/env python3
"""Verify receipt membership; never claim semantic entailment or connector coverage."""
import argparse
import hashlib
import json
from pathlib import Path

LIMIT = 8 * 1024 * 1024


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON field')
        result[key] = value
    return result


def read_artifact(path):
    with Path(path).open('rb') as stream:
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError('Artifact exceeds 8 MiB')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object), digest(raw)


def fields(record, names):
    if not isinstance(record, dict) or any(
        not isinstance(record.get(name), str) or not record[name].strip() for name in names
    ):
        raise ValueError('Missing or invalid required string')


def verify(inputs, proposals):
    fields(inputs, ('run_id',))
    fields(proposals, ('run_id',))
    if inputs['run_id'] != proposals['run_id']:
        raise ValueError('Run IDs differ')
    sources, items = inputs.get('sources'), proposals.get('items')
    if not isinstance(sources, list) or not isinstance(items, list) or not items:
        raise ValueError('Source list and nonempty item list required')
    coverage = inputs.get('coverage')
    if not isinstance(coverage, dict) or not coverage or any(
        not isinstance(k, str) or not k.strip() or v not in ('complete', 'partial', 'unavailable')
        for k, v in coverage.items()
    ):
        raise ValueError('Explicit coverage required')
    by_id = {}
    for source in sources:
        fields(source, ('source_type', 'source_id', 'text', 'sha256'))
        key = (source['source_type'], source['source_id'])
        if key in by_id or key[0] not in coverage:
            raise ValueError('Duplicate source or missing source coverage')
        if digest(source['text'].encode('utf-8')) != source['sha256']:
            raise ValueError('Source hash mismatch')
        by_id[key] = source
    seen, receipts = set(), 0
    for index, item in enumerate(items):
        fields(item, ('id', 'title'))
        if item['id'] in seen:
            raise ValueError('Duplicate item ID')
        seen.add(item['id'])
        refs = item.get('source_receipts')
        if not isinstance(refs, list) or not refs:
            raise ValueError(f'Item {index}: nonempty receipts required')
        for ref in refs:
            fields(ref, ('source_type', 'source_id', 'sha256', 'exact_quote'))
            source = by_id.get((ref['source_type'], ref['source_id']))
            if source is None or ref['sha256'] != source['sha256']:
                raise ValueError(f'Item {index}: unknown source or receipt hash mismatch')
            if ref['exact_quote'] not in source['text']:
                raise ValueError(f'Item {index}: quote absent from source')
            receipts += 1
    return {'sources': len(sources), 'items': len(items), 'receipts': receipts,
            'declared_coverage_complete': all(v == 'complete' for v in coverage.values()),
            'semantic_review': 'pending'}


def verify_files(inputs_path, proposals_path):
    inputs, inputs_hash = read_artifact(inputs_path)
    proposals, proposals_hash = read_artifact(proposals_path)
    return {**verify(inputs, proposals), 'inputs_sha256': inputs_hash,
            'proposals_sha256': proposals_hash}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('inputs', type=Path)
    p.add_argument('proposals', type=Path)
    args = p.parse_args()
    try:
        print(json.dumps(verify_files(args.inputs, args.proposals)))
    except (ValueError, OSError, UnicodeError, RecursionError):
        p.exit(1, 'Receipt verification failed. Check artifact shapes, run IDs, coverage, hashes and quotes. No source text logged.\n')


if __name__ == '__main__':
    main()
