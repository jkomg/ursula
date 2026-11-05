#!/usr/bin/env python3
"""Check a session's coverage claims against evidence the model did not write.

  python3 scripts/session_verify.py RUN.json --ledger FILE --since ISO_UTC [--recount FILE] [--json]

For planning, retro, ad-hoc and hire-scan sessions; check-ins use checkin_close.py.

Why: an operator caught a session saying it had checked their email when it had not.
A second model reading that session's summary would have believed it too. This compares
the run's `coverage` claims with two things the session cannot write:

  --ledger   the hash-chained call log from bin/ledger-log, counting only calls at or
             after --since (the session's start, UTC). A claim with no matching call fails,
             whatever the run's status: a partial run must not claim a read either.
  --recount  counts from an independent re-read of the sources for the same window
             (reference/delegation.md, "Proving the run"): gmail_in_window,
             calendar_events, drive_docs_in_window. Claiming more than exist fails; a
             complete run that saw fewer than exist fails.

Exit 0 when every claim is backed, 1 otherwise. --json prints the result for the run
record's `verified` field. Reads files only: no connector, no network.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checkin_verify import ledger_facts  # noqa: E402

CLAIMS = {
    # coverage flag: (ledger fact, what was claimed)
    "calendar_read": (lambda f: f["calendar_listed"], "Calendar read"),
    "jira_read": (lambda f: f["jira_searched"], "Jira searched"),
    "slack_dm_read": (lambda f: f["slack_dm_reads"], "Slack DM read"),
}
FLAGS = ("gmail_read", "calendar_read", "jira_read")
COUNTS = ("gmail_listed", "gmail_opened", "calendar_events", "drive_docs_opened", "drive_docs_in_window")
RECOUNT = (("gmail_listed", "gmail_in_window", "Gmail messages"),
           ("calendar_events", "calendar_events", "calendar events"),
           ("drive_docs_in_window", "drive_docs_in_window", "notes documents"))


def is_count(v):
    return type(v) is int and v >= 0


def n(v):
    """A count for comparison; a malformed value is already reported, so it counts as 0."""
    return v if is_count(v) else 0


def verify(run, ledger, since, recount=None):
    errs, notes = [], []
    status = run.get("status")
    cov = run.get("coverage")
    if not isinstance(cov, dict):
        return ["run has no coverage block; every session that mined states what it read"]
    if status == "complete":
        errs += [f"complete run must state coverage.{k} as true or false" for k in FLAGS
                 if type(cov.get(k)) is not bool]
        errs += [f"complete run says coverage.{k} is false" for k in FLAGS if cov.get(k) is False]
        errs += [f"complete run must state coverage.{k} as a count" for k in COUNTS if not is_count(cov.get(k))]
    else:
        errs += [f"coverage.{k} is not a count" for k in COUNTS if k in cov and not is_count(cov[k])]

    facts, probs = ledger_facts(ledger, since)
    errs += probs
    # The session start comes from the harness (SessionStart hook), not from the caller.
    start = facts.get("session_start")
    if start and str(since).replace("+00:00", "Z")[:19] < start[:19]:
        errs.append(f"--since {since} is earlier than this session's recorded start {start}; "
                    "an earlier session's calls cannot back this run's claims")
    elif not start:
        errs.append("no session_start marker in the ledger, so the cutoff would be the caller's own "
                    "statement; the SessionStart hook is not recording (run bash bin/rails-check)")

    # Gmail: reading means opening messages, not just listing ids.
    if cov.get("gmail_read") is True:
        if not facts["gmail_listed"] and not facts["gmail_opened"]:
            errs.append(f"ledger: run claims Gmail read, but no such call is recorded since {since}")
        elif not facts["gmail_opened"] and not (cov.get("gmail_listed") == 0 and recount
                                                and recount.get("gmail_in_window") == 0):
            errs.append("ledger: run claims Gmail read, but no message was opened; listing ids is not reading")
    if n(cov.get("gmail_opened")) > facts["gmail_opened"]:
        errs.append(f"ledger: run claims {cov['gmail_opened']} Gmail messages opened, ledger shows {facts['gmail_opened']}")
    for flag, (has, label) in CLAIMS.items():
        if cov.get(flag) is True and not has(facts):
            errs.append(f"ledger: run claims {label}, but no such call is recorded since {since}")
    if n(cov.get("calendar_events")) > 0 and not facts["calendar_listed"]:
        errs.append("ledger: run reports calendar events, but no calendar listing is recorded")
    claimed_docs = n(cov.get("drive_docs_opened"))
    if claimed_docs > len(facts["docs_opened"]):
        errs.append(f"ledger: run claims {claimed_docs} documents opened, ledger shows {len(facts['docs_opened'])}")
    if status == "complete" and facts["calls"] < 5:
        errs.append(f"ledger: only {facts['calls']} calls since {since}; a mining session makes dozens")

    if recount is None:
        if status == "complete":
            errs.append("complete run has no independent recount (--recount)")
    else:
        for claim, key, label in RECOUNT:
            seen, actual = cov.get(claim), recount.get(key)
            if seen is None or not is_count(seen):
                continue
            if not is_count(actual):
                errs.append(f"recount is missing {key}, so the claimed {label} were not checked")
                continue
            if seen > actual:
                errs.append(f"recount: run claims {seen} {label} in the window, the source has {actual}")
            elif status == "complete" and seen < actual:
                errs.append(f"recount: complete run covered {seen} of {actual} {label}")
    facts["notes"] = notes
    return errs, facts


def main(argv):
    args, opts, want_json = argv[1:], {}, "--json" in argv
    args = [a for a in args if a != "--json"]
    for flag in ("--ledger", "--since", "--recount"):
        if flag in args:
            i = args.index(flag)
            opts[flag] = args[i + 1] if i + 1 < len(args) else None
            del args[i:i + 2]
    if len(args) != 1 or not opts.get("--ledger") or not opts.get("--since"):
        print(__doc__.strip().split("\n\n")[0], file=sys.stderr)
        return 2
    run = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    recount = json.loads(Path(opts["--recount"]).read_text(encoding="utf-8")) if opts.get("--recount") else None
    if not Path(opts["--ledger"]).exists():
        errs, facts = ["ledger file does not exist: the hooks were not recording this session"], {"calls": 0}
    else:
        out = verify(run, opts["--ledger"], opts["--since"], recount)
        errs, facts = (out, {"calls": 0}) if isinstance(out, list) else out
    if want_json:
        print(json.dumps({"ok": not errs, "errors": errs, "notes": facts.get("notes", []), "ledger_calls": facts.get("calls"),
                          "ledger_head": facts.get("head"), "since": opts["--since"],
                          "recount": recount is not None}))
    else:
        for e in errs:
            print("FAIL ", e)
        if not errs:
            print("ok    every coverage claim is backed by the ledger" + (" and the recount" if recount else ""))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
