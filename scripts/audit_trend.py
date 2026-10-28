#!/usr/bin/env python3
"""Weekly audit and trend of check-ins and findings, from the board's own records.

  python3 scripts/audit_trend.py RUNS_DIR FINDINGS_DIR [--per-day 3]

RUNS_DIR and FINDINGS_DIR are ArtifactData exports (out_dir). Prints Markdown: one row per
ISO week, then the weekdays that had fewer check-ins than scheduled. Nothing is written
back; a check-in stores the output as `audit/<week>` if the operator wants it on the board.

What each column is for:

  runs / complete / partial   how often a check-in finished its job; a rising partial
                              rate means a source is failing or runs are cutting corners
  no coverage                 complete runs without a `coverage` block: unverifiable
  unverified                  check-in runs with no `verified.ok`; only runs closed with
                              scripts/checkin_close.py carry it
  opened / resolved / lapsed  findings first seen, closed by someone, and expired unhandled
  open at end, oldest (d)     the open set and the age of its oldest member; findings that
                              are never closed are noise that hides the ones that matter
  silent-green                complete runs that listed a check clean while an open finding
                              of that check existed (the failure of 27 Oct)
"""
import datetime
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def docs(folder):
    for p in sorted(Path(folder).rglob("*.json")):
        d = json.loads(p.read_text())
        d = d.get("data", d)
        d.setdefault("key", p.stem)
        d.setdefault("_id", p.stem)
        yield d


def week(day):
    y, w, _ = datetime.date.fromisoformat(day).isocalendar()
    return f"{y}-w{w:02d}"


def main(argv):
    args = argv[1:]
    per_day = 3
    if "--per-day" in args:
        i = args.index("--per-day")
        per_day = int(args[i + 1])
        del args[i:i + 2]
    if len(args) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    every = [r for r in docs(args[0]) if r.get("session") == "checkin"]
    runs = [r for r in every if r.get("date")]
    if len(every) != len(runs):
        print(f"WARNING: {len(every) - len(runs)} check-in records have no date and are not counted\n")
    finds = list(docs(args[1]))
    today = datetime.date.today().isoformat()
    open_checks = {f.get("check") for f in finds if f.get("status") in ("open", "carried")}

    rows = defaultdict(lambda: defaultdict(int))
    per_date = defaultdict(int)
    for r in runs:
        w = rows[week(r["date"])]
        per_date[r["date"]] += 1
        w["runs"] += 1
        st = r.get("status") or "unrecorded"
        w[st] += 1
        if st == "complete" and not r.get("coverage"):
            w["no coverage"] += 1
        if not (r.get("verified") or {}).get("ok"):
            w["unverified"] += 1
        for c in r.get("checks_clean") or []:
            slug = re.split(r"[\s(:]", str(c).strip(), 1)[0]
            if st == "complete" and any(slug.startswith(x) for x in open_checks if x):
                w["silent-green"] += 1
    oldest = {}
    for f in finds:
        if f.get("first_seen"):
            w = rows[week(f["first_seen"])]
            w["opened"] += 1
        if f.get("status") == "resolved":
            w2 = rows[week(f.get("closed_at", f.get("last_seen", f["first_seen"]))[:10])]
            w2["resolved"] += 1
        if f.get("status") == "lapsed":
            rows[week(f.get("closed_at", f.get("last_seen", f["first_seen"]))[:10])]["lapsed"] += 1
        if f.get("status") in ("open", "carried") and f.get("first_seen"):
            age = (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(f["first_seen"])).days
            rows[week(today)]["open at end"] += 1
            oldest[week(today)] = max(oldest.get(week(today), 0), age)

    cols = ["runs", "complete", "partial", "failed", "no coverage", "unverified", "silent-green",
            "opened", "resolved", "lapsed", "open at end"]
    print("| week | " + " | ".join(cols) + " | partial rate | oldest open (d) |")
    print("|---|" + "---|" * (len(cols) + 2))
    for wk in sorted(rows):
        r = rows[wk]
        rate = f"{100 * r['partial'] / r['runs']:.0f}%" if r["runs"] else "-"
        print(f"| {wk} | " + " | ".join(str(r[c]) for c in cols) + f" | {rate} | {oldest.get(wk, '')} |")

    if per_date:
        first = datetime.date.fromisoformat(min(per_date))
        d = first
        short = []
        while d <= datetime.date.today():
            if d.weekday() < 5 and per_date.get(d.isoformat(), 0) < per_day and d != datetime.date.today():
                short.append(f"{d.isoformat()} ({per_date.get(d.isoformat(), 0)}/{per_day})")
            d += datetime.timedelta(days=1)
        print(f"\nWeekdays with fewer than {per_day} check-ins: " + (", ".join(short) if short else "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
