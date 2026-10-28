#!/usr/bin/env python3
"""Capture a configured read-only connector adapter, not model-authored evidence.

Adapter stdout: {"sources":[{"source_type":...,"source_id":...,"text":...}],
"coverage":{"gmail":"complete", ...}}. No provider credentials are handled here.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from datetime import datetime, timezone


def capture(command, run_id):
    if not command or not run_id.strip():
        raise ValueError('Adapter command and run ID are required')
    # A regular file avoids buffering unbounded connector output in memory.
    with tempfile.TemporaryFile() as output:
        result = subprocess.run(command, stdout=output, stderr=subprocess.DEVNULL, timeout=120)
        if result.returncode:
            raise ValueError('Connector adapter failed; no evidence published')
        output.seek(0)
        raw = output.read(8 * 1024 * 1024 + 1)
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError('Connector output exceeds 8 MiB')
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get('sources'), list):
        raise ValueError('Expected a source list from the connector adapter')
    coverage = data.get('coverage')
    if not isinstance(coverage, dict) or not coverage or any(
        not isinstance(k, str) or v not in ('complete', 'partial', 'unavailable')
        for k, v in coverage.items()
    ):
        raise ValueError('Explicit source coverage is required')
    sources, seen = [], set()
    for source in data['sources']:
        if not isinstance(source, dict) or any(
            not isinstance(source.get(k), str) or not source[k].strip()
            for k in ('source_type', 'source_id', 'text')
        ):
            raise ValueError('Malformed source record')
        key = (source['source_type'], source['source_id'])
        if key in seen or key[0] not in coverage:
            raise ValueError('Duplicate source or missing coverage entry')
        seen.add(key)
        sources.append({**{k: source[k] for k in ('source_type', 'source_id', 'text')},
                        'sha256': hashlib.sha256(source['text'].encode('utf-8')).hexdigest()})
    return {'run_id': run_id, 'captured_at': datetime.now(timezone.utc).isoformat(),
            'coverage': coverage, 'sources': sources,
            'adapter_executed': True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-id', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('adapter', nargs=argparse.REMAINDER)
    args = p.parse_args()
    command = args.adapter[1:] if args.adapter[:1] == ['--'] else args.adapter
    try:
        data = capture(command, args.run_id)
        # Refuse overwrite: each run gets its own frozen artifact outside Git.
        fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(json.dumps({'sources': len(data['sources']), 'coverage': data['coverage']}))
    except (ValueError, OSError, subprocess.SubprocessError):
        p.exit(1, 'Input capture failed; check adapter, coverage and destination. No source text logged.\n')


if __name__ == '__main__':
    main()
