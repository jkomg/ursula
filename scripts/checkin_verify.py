#!/usr/bin/env python3
"""Check a check-in's run record against the rules in reference/always-on.md.

  python3 scripts/checkin_verify.py RUN.json FINDINGS_DIR

RUN.json is the run document's data (the fields in config/schema.md, "runs").
FINDINGS_DIR holds the findings as JSON files, one per document, as ArtifactData
writes them with out_dir. Exit 0 if the record is sound, 1 and one line per broken
rule if not. It reads files only: no connector, no network.

It checks that a record is internally honest, not that the sources were read; the
counts in `coverage` are the check-in's own statement. What it catches is a record
that says `complete` while its own numbers, its could_not list or the open findings
say otherwise.
"""
import json
import re
import sys
from pathlib import Path

SKIPPED = re.compile(r"\b(not|never|unable to|could not|couldn't|skipped)\b.*\b(read|opened|triaged|mined|reconciled|listed)\b"
                     r"|\b(read|opened|triaged|mined)\b.*\b(not|skipped)\b", re.I)


def load(path):
    d = json.loads(Path(path).read_text())
    return d.get("data", d) if isinstance(d, dict) else d


def open_findings(folder):
    out = []
    for p in sorted(Path(folder).rglob("*.json")):
        f = load(p)
        if isinstance(f, dict) and f.get("status") in ("open", "carried"):
            f.setdefault("key", p.stem)
            out.append(f)
    return out


def verify(run, findings):
    errs = []
    status = run.get("status")
    if status not in ("complete", "partial", "failed"):
        errs.append(f"status is {status!r}; must be complete, partial or failed")
    if not isinstance(run.get("could_not"), list):
        errs.append("could_not is missing; it is [] when nothing, never omitted")
    for k in ("checks_clean", "summary", "window_start", "window_end", "date"):
        if k not in run:
            errs.append(f"{k} is missing")

    cov = run.get("coverage")
    if status == "complete":
        if not isinstance(cov, dict):
            errs.append("complete run has no coverage block")
            cov = {}
        if cov.get("notes_read") is not True:
            errs.append("coverage.notes_read is not true")
        if cov.get("slack_dm_read") not in (True, None):
            errs.append("coverage.slack_dm_read is false (null means no DM configured)")
        if cov.get("drive_docs_opened") != cov.get("drive_docs_in_window") or cov.get("drive_docs_opened") is None:
            errs.append(f"Drive: {cov.get('drive_docs_opened')} opened of {cov.get('drive_docs_in_window')} in window")
        if cov.get("gmail_read") is not True:
            errs.append("coverage.gmail_read is not true")
        if cov.get("gmail_listed") is None:
            errs.append("coverage.gmail_listed is missing")
        if cov.get("outbox_stale") is None:
            errs.append("coverage.outbox_stale is missing")
        for line in run.get("could_not") or []:
            if SKIPPED.search(str(line)):
                errs.append(f"complete, but could_not says a source was not read: {str(line)[:90]!r}")
        if run.get("watermark_before") and run.get("watermark_after") == run.get("watermark_before"):
            errs.append("complete, but the watermark did not advance")
    else:
        if run.get("watermark_before") and run.get("watermark_after") not in (None, run["watermark_before"]):
            errs.append(f"{status} run advanced the watermark")

    # The open set: every open finding was re-evaluated this run.
    n = len(findings)
    if cov and cov.get("open_set") is not None and cov["open_set"] != n:
        errs.append(f"coverage.open_set is {cov['open_set']} but {n} findings are open or carried on the board")
    if status == "complete":
        if cov.get("open_set_evaluated") != n:
            errs.append(f"{cov.get('open_set_evaluated')} open findings evaluated of {n}")
        stale = [f["key"] for f in findings if f.get("last_seen") != run.get("date")]
        if stale:
            errs.append("open findings not re-seen this run (last_seen is not the run date): " + ", ".join(stale))
        accounted = (run.get("findings_carried") or 0) + (run.get("findings_resolved") or 0)
        if accounted < n:
            errs.append(f"findings_carried + findings_resolved is {accounted}, fewer than the {n} open findings")

    # A check cannot be clean while an open finding of that check exists.
    open_checks = {f.get("check") for f in findings if f.get("check")}
    for clean in run.get("checks_clean") or []:
        slug = re.split(r"[\s(:]", str(clean).strip(), 1)[0]
        for c in open_checks:
            if slug == c or slug.startswith(c):
                errs.append(f"checks_clean lists {slug!r} but an open {c!r} finding exists")
    return errs


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip().split("\n\n")[0], file=sys.stderr)
        return 2
    errs = verify(load(argv[1]), open_findings(argv[2]))
    for e in errs:
        print("FAIL ", e)
    if not errs:
        print("ok    run record is consistent with the open findings")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
