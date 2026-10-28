#!/usr/bin/env python3
"""Close out a check-in: verify the record, then build the final line and the watermark.

  python3 scripts/checkin_close.py RUN.json FINDINGS_DIR [--ledger FILE] --level quiet|daily|chatty
         [--slack-dm ID] [--outbox-dir DIR] [--now ISO]

Prints one JSON object:

  verified        true only if scripts/checkin_verify.py passes, ledger included
  errors          what failed
  status_allowed  "complete" if verified, otherwise "partial"
  final_line      the one line for the operator, built from the record, the open findings
                  and the ledger, never from the model's recollection
  state_checkin   {watermark, slack_last_ts} to write, present only when verified
  ledger          {calls, errors, head, first, last, by_tool} for the run record

The model writes the run record and decides what the findings say; this decides whether
the run may call itself complete, whether the watermark may move, and what the phone is
told. It exits 0 when verified, 1 when not, and the final line is still produced so a
partial run can be reported honestly.

--ledger defaults to $URSULA_LEDGER, then /var/tmp/ursula-ledger/ledger.jsonl. A missing or
empty ledger fails verification: a check-in nobody observed is not a verified one.

A finding is imminent when it is open or carried and its `due_at` (ISO, with offset) is
in the past or within 36 hours of --now. Findings without `due_at` are never imminent;
the check that raises a finding sets it.
"""
import datetime
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import checkin_verify as V  # noqa: E402


def parse(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def main(argv):
    args = argv[1:]
    opts = {"--level": "quiet"}
    for flag in ("--ledger", "--level", "--slack-dm", "--outbox-dir", "--now"):
        if flag in args:
            i = args.index(flag)
            opts[flag] = args[i + 1]
            del args[i:i + 2]
    opts.setdefault("--ledger", os.environ.get("URSULA_LEDGER") or "/var/tmp/ursula-ledger/ledger.jsonl")
    if len(args) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    run, findings = V.load(args[0]), V.open_findings(args[1])
    now = parse(opts["--now"]) if "--now" in opts else datetime.datetime.now(datetime.timezone.utc)

    if not Path(opts["--ledger"]).is_file():
        Path(opts["--ledger"]).parent.mkdir(parents=True, exist_ok=True)
        Path(opts["--ledger"]).touch()
    errs = V.verify(run, findings, opts["--ledger"], opts.get("--slack-dm"))
    facts, _ = V.ledger_facts(opts["--ledger"])
    verified = not errs

    horizon = now + datetime.timedelta(hours=36)
    imminent = []
    for f in findings:
        if f.get("due_at"):
            try:
                if parse(f["due_at"]) <= horizon:
                    imminent.append(f)
            except ValueError:
                errs.append(f"finding {f['key']} has an unreadable due_at {f['due_at']!r}")
                verified = False
    imminent.sort(key=lambda f: f["due_at"])

    stale = (run.get("coverage") or {}).get("outbox_stale") or 0
    needs_ok = 0
    if "--outbox-dir" in opts:
        for p in Path(opts["--outbox-dir"]).rglob("*.json"):
            o = V.load(p)
            if o.get("status") == "proposed" and not (o.get("expires_at") and parse(o["expires_at"]) < now):
                needs_ok += 1

    parts = []
    if not verified:
        gaps = [e.split(":", 1)[-1].strip()[:70] for e in errs[:3]]
        parts.append("partial, " + "; ".join(gaps) + (f" (+{len(errs) - 3} more)" if len(errs) > 3 else "") + ", will retry")
    parts += [f"{f['title'][:60]} (due {f['due_at'][:16].replace('T', ' ')})" for f in imminent[:3]]
    if len(imminent) > 3:
        parts.append(f"{len(imminent) - 3} more due soon")
    if needs_ok:
        parts.append(f"{needs_ok} outbox item{'s' if needs_ok != 1 else ''} need your OK")
    if stale:
        parts.append(f"{stale} outbox item{'s' if stale != 1 else ''} expired unsent")
    line = "Ursula: " + "; ".join(parts) if parts else "Nothing needs you."
    if opts["--level"] == "chatty":
        c = run.get("coverage") or {}
        line += (f" [read {len(facts['docs_opened'])} docs, {facts['gmail_opened']} mails opened of "
                 f"{c.get('gmail_listed')} listed, DM {'read' if facts['slack_dm_reads'] else 'not read'}; "
                 f"{len(findings)} open findings, {run.get('findings_new', 0)} new]")

    out = {
        "verified": verified, "errors": errs,
        "status_allowed": "complete" if verified else "partial",
        "final_line": line,
        "state_checkin": ({"watermark": run["window_end"], "slack_last_ts": run.get("slack_last_ts")}
                          if verified and run.get("status") == "complete" else None),
        "ledger": {k: facts[k] for k in ("calls", "errors", "head", "first", "last", "by_tool")},
    }
    print(json.dumps(out, indent=2))
    return 0 if verified else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
