#!/usr/bin/env python3
"""Check a check-in's run record against the rules in reference/always-on.md.

  python3 scripts/checkin_verify.py RUN.json FINDINGS_DIR [--ledger FILE] [--slack-dm ID]

RUN.json is the run document's data (the fields in config/schema.md, "runs").
FINDINGS_DIR holds the findings as JSON files, one per document, as ArtifactData
writes them with out_dir. Exit 0 if the record is sound, 1 and one line per broken
rule if not. It reads files only: no connector, no network.

Without --ledger it checks that a record is internally honest: the counts in `coverage`
are the check-in's own statement, and it catches a record that says `complete` while its
own numbers, its could_not list or the open findings say otherwise.

With --ledger (the harness-written call log from bin/ledger-log) it also checks the claims
against what was actually called: documents opened, Gmail listed and opened, the Slack DM
read, the notes collection read, and a board write for every open finding it says it
re-evaluated. A run cannot make those true by writing them down. --slack-dm is the DM
channel id from config/checkins.slack_dm. A ledger whose hash chain is broken fails.
"""
import hashlib
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


def ledger_facts(path, since=None):
    """Read the ledger written by bin/ledger-log; return (facts, problems).

    The whole chain is verified, but only calls at or after `since` (ISO UTC) count.
    A desktop ledger persists across sessions; without the cut an earlier session's
    Gmail read would satisfy this one's claim."""
    probs, calls, prev = [], [], "0" * 64
    for n, raw in enumerate(Path(path).read_bytes().splitlines(), 1):
        try:
            e = json.loads(raw)
        except ValueError:
            probs.append(f"ledger line {n} is not JSON")
            break
        if e.get("prev") != prev:
            probs.append(f"ledger chain broken at line {n} (an entry was edited, removed or inserted)")
            break
        prev = hashlib.sha256(raw).hexdigest()
        calls.append(e)
    starts = [str(c.get("ts", "")) for c in calls if c.get("tool") == "session_start"]
    if since:
        cut = since.replace("+00:00", "Z")[:19]
        calls = [c for c in calls if str(c.get("ts", ""))[:19] >= cut]
    ok = [c for c in calls if not c.get("error")]

    def arg(c, *keys):
        for k in keys:
            if c["args"].get(k):
                return str(c["args"][k])
        return None

    def named(c, *needles):
        return any(x in c["tool"] for x in needles)
    docs = {arg(c, "documentId", "fileId", "file_id") for c in ok
            if named(c, "docs_get", "documents_get", "read_file_content", "download_file_content", "files_get",
                     "files_export", "files_download")} - {None}
    facts = {
        "calls": sum(1 for c in calls if c.get("tool") != "session_start"),
        "errors": len(calls) - len(ok), "head": prev,
        "session_start": max(starts) if starts else None,
        "first": calls[0]["ts"] if calls else None, "last": calls[-1]["ts"] if calls else None,
        "docs_opened": docs,
        "gmail_listed": sum(1 for c in ok if "gmail" in c["tool"] and named(c, "messages_list", "threads_list", "triage")),
        "gmail_opened": sum(1 for c in ok if "gmail" in c["tool"] and named(c, "messages_get", "threads_get", "gmail_read")),
        "slack_dm_reads": {arg(c, "channel_id") for c in ok if c["tool"] == "slack_read_channel"} - {None},
        "calendar_listed": sum(1 for c in ok if "calendar" in c["tool"] and named(c, "events_list", "agenda", "instances")),
        "jira_searched": sum(1 for c in ok if named(c, "searchJiraIssuesUsingJql", "JiraIssuesUsingJql")),
        "drive_searched": sum(1 for c in ok if named(c, "files_list", "search_files", "list_recent_files")),
        "notes_read": any(c["tool"] == "ArtifactData" and c["args"].get("collection") == "notes"
                          and c["args"].get("action") in ("get", "list", "query") for c in ok),
        "findings_written": {c["args"].get("doc_id") for c in ok if c["tool"] == "ArtifactData"
                             and c["args"].get("collection") == "findings"
                             and c["args"].get("action") in ("set", "update", "str_replace")} - {None},
        "by_tool": {},
    }
    for c in calls:
        facts["by_tool"][c["tool"]] = facts["by_tool"].get(c["tool"], 0) + 1
    return facts, probs


def verify(run, findings, ledger=None, slack_dm=None):
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

    # The claims against the harness's own record of the calls.
    if ledger is not None:
        facts, probs = ledger_facts(ledger)
        errs += probs
        if status == "complete":
            claimed_docs = cov.get("drive_docs_opened") or 0
            if len(facts["docs_opened"]) < claimed_docs:
                errs.append(f"ledger: {len(facts['docs_opened'])} distinct documents opened, run claims {claimed_docs}")
            if cov.get("gmail_listed") and not facts["gmail_listed"]:
                errs.append("ledger: no Gmail list or triage call, run claims it listed mail")
            if (cov.get("gmail_opened") or 0) > facts["gmail_opened"]:
                errs.append(f"ledger: {facts['gmail_opened']} Gmail messages opened, run claims {cov.get('gmail_opened')}")
            if cov.get("gmail_read") is True and not (facts["gmail_listed"] or facts["gmail_opened"]):
                errs.append("ledger: no Gmail call at all, run claims gmail_read")
            if cov.get("slack_dm_read") is True and (slack_dm and slack_dm not in facts["slack_dm_reads"]
                                                     or not facts["slack_dm_reads"]):
                errs.append("ledger: no read of the operator's Slack DM, run claims slack_dm_read")
            if cov.get("notes_read") is True and not facts["notes_read"]:
                errs.append("ledger: the notes collection was never read, run claims notes_read")
            missing = sorted(f["key"] for f in findings if f["key"] not in facts["findings_written"])
            if missing:
                errs.append("ledger: no board write for open findings claimed as re-evaluated: " + ", ".join(missing))
            if facts["calls"] < 5:
                errs.append(f"ledger: only {facts['calls']} calls recorded; a check-in makes dozens")

    # A check cannot be clean while an open finding of that check exists.
    open_checks = {f.get("check") for f in findings if f.get("check")}
    for clean in run.get("checks_clean") or []:
        slug = re.split(r"[\s(:]", str(clean).strip(), 1)[0]
        for c in open_checks:
            if slug == c or slug.startswith(c):
                errs.append(f"checks_clean lists {slug!r} but an open {c!r} finding exists")
    return errs


def main(argv):
    args = argv[1:]
    opts = {}
    for flag in ("--ledger", "--slack-dm"):
        if flag in args:
            i = args.index(flag)
            opts[flag] = args[i + 1] if i + 1 < len(args) else None
            del args[i:i + 2]
    if len(args) != 2 or None in opts.values():
        print(__doc__.strip().split("\n\n")[0], file=sys.stderr)
        return 2
    errs = verify(load(args[0]), open_findings(args[1]), opts.get("--ledger"), opts.get("--slack-dm"))
    for e in errs:
        print("FAIL ", e)
    if not errs:
        print("ok    run record is consistent with the open findings" + (" and the call ledger" if "--ledger" in opts else ""))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
