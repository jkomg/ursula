#!/usr/bin/env python3
"""Render Ursula's exported record bodies as a portable, read-only HTML board."""

import argparse
from datetime import datetime
import html
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlsplit


def text(value):
    return html.escape(str(value)) if value is not None else "Not recorded"


def link(label, url):
    # Exports are untrusted. No script/data links, userinfo or ambiguous URLs.
    try:
        parsed = urlsplit(url) if isinstance(url, str) else None
        safe = (parsed and parsed.scheme == "https" and parsed.hostname
                and not parsed.username and not parsed.password
                and not any(c.isspace() or ord(c) < 32 for c in url)
                and "\\" not in url)
    except ValueError:
        safe = False
    if safe:
        return f'<a href="{text(url)}" rel="noreferrer">{text(label)}</a>'
    return text(label)


def listing(values, empty="None recorded"):
    if values is None:
        return '<p class="gap">Not recorded</p>'
    if not isinstance(values, list):
        raise ValueError("list field must be an array")
    if not values:
        return f"<p>{text(empty)}</p>"
    return "<ul>" + "".join(f"<li>{text(v)}</li>" for v in values) + "</ul>"


def records(data, key):
    collection = data.get(key, {})
    if not isinstance(collection, dict) or any(not isinstance(v, dict) for v in collection.values()):
        raise ValueError(f"{key} must be an object keyed by document id, containing record bodies")
    return collection


def render(data):
    if not isinstance(data, dict):
        raise ValueError("export must be a JSON object")
    generated = data.get("generated_at")
    if not isinstance(generated, str) or not generated.strip():
        raise ValueError("generated_at is required: use the actual observation timestamp")
    stamp = datetime.fromisoformat(generated.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("generated_at must include a timezone")
    parts = ["<h1>Ursula</h1>", f"<p>Snapshot observed {text(generated)}. Refresh by running another review.</p>",
             "<p>This file has no live connector access or write controls.</p>", "<h2>Run log and coverage</h2>"]
    runs = records(data, "runs")
    for key, run in sorted(runs.items(), key=lambda item: str(item[1].get("date", "")), reverse=True)[:52]:
        sources = run.get("sources", {})
        if not isinstance(sources, dict):
            raise ValueError(f"runs/{key}.sources must be an object")
        counts = (run.get("skipped"), run.get("findings_new"), run.get("findings_carried"))
        complete_fields = (
            all(type(value) is int and value >= 0 for value in counts)
            and isinstance(run.get("could_not"), list)
            and isinstance(run.get("checks_clean"), list)
            and isinstance(sources.get("unmatched_meetings"), list)
        )
        status = text(run.get("status")) if complete_fields else "Incomplete record"
        parts += [f"<article><h3>{text(key)} · {status} · {text(run.get('mode'))}</h3>",
                  f"<p>{text(run.get('summary'))}</p>",
                  f"<p>Created: {text(run.get('created'))} · Already tracked: {text(run.get('skipped'))} · Edited: {text(run.get('edited'))}</p>",
                  f"<p>Sources found / expected: {text(sources.get('found'))} / {text(sources.get('expected'))}</p>",
                  f"<p>New / carried findings: {text(run.get('findings_new'))} / {text(run.get('findings_carried'))}</p>",
                  "<h4>Meetings without notes</h4>", listing(sources.get("unmatched_meetings")),
                  "<h4>What could not be done</h4>", listing(run.get("could_not")),
                  "<h4>Checks that ran clean</h4>", listing(run.get("checks_clean")), "</article>"]
    if not runs:
        parts.append('<p class="gap">No run log supplied; coverage and reconciliation are not recorded.</p>')
    parts.append("<h2>Findings</h2>")
    findings = records(data, "findings")
    def rank(item):
        value = item[1].get("rank")
        return value if isinstance(value, (int, float)) else float("inf")
    for key, finding in sorted(findings.items(), key=rank):
        parts += [f"<article><h3>{text(finding.get('title', key))}</h3>",
                  f"<p>{text(finding.get('check'))} · {text(finding.get('status'))}</p>", "<dl>"]
        for field in ("evidence", "consequence", "recommendation", "close_note"):
            if field == "close_note" and field not in finding:
                continue
            parts.append(f"<dt>{text(field.replace('_', ' ').title())}</dt><dd>{text(finding.get(field))}</dd>")
        parts.append("</dl>")
        refs = finding.get("refs", [])
        if not isinstance(refs, list) or any(not isinstance(ref, dict) for ref in refs):
            raise ValueError(f"findings/{key}.refs must be an array of objects")
        parts.append("<p>" + " · ".join(link(ref.get("label", "Source"), ref.get("url")) for ref in refs) + "</p></article>")
    if not findings:
        parts.append("<p>No findings supplied. See the run log for which checks actually ran.</p>")
    parts.append("<h2>Work observed in Jira</h2>")
    issues = data.get("issues", [])
    if not isinstance(issues, list) or any(not isinstance(issue, dict) for issue in issues):
        raise ValueError("issues must be an array of normalised issue objects")
    if issues:
        parts.append("<table><thead><tr><th>Issue</th><th>Work</th><th>Status</th><th>Due</th></tr></thead><tbody>")
        for issue in issues:
            parts.append(f"<tr><td>{link(issue.get('key'), issue.get('url'))}</td><td>{text(issue.get('title'))}</td><td>{text(issue.get('status'))}</td><td>{text(issue.get('due'))}</td></tr>")
        parts.append("</tbody></table>")
    else:
        parts.append("<p>No Jira snapshot supplied.</p>")
    for key, hire in sorted(records(data, "hires").items()):
        parts += [f"<h2>{text(hire.get('name', key))} · {text(hire.get('board'))}</h2>",
                  f"<p>Scanned {text(hire.get('scanned_at'))}</p><p>{text(hire.get('summary'))}</p>"]
        for field, title in (("needs_me", "What they need from me"), ("blocked", "Blocked"),
                             ("needs_review", "Needs review"), ("overdue", "Overdue"), ("moved", "What moved")):
            parts.append(f"<h3>{title}</h3>")
            rows = hire.get(field)
            if rows is None:
                parts.append(listing(None))
                continue
            if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                raise ValueError(f"hires/{key}.{field} must be an array of objects")
            if not rows:
                parts.append("<p>None recorded</p>")
                continue
            parts.append("<ul>")
            for row in rows:
                detail = next((row[field] for field in ("why", "change", "on_whom", "due") if row.get(field) is not None), None)
                parts.append(f"<li>{link(row.get('key'), row.get('url'))} {text(row.get('title'))} — {text(detail)}</li>")
            parts.append("</ul>")
        parts += ["<h3>One-to-one agenda</h3>", listing(hire.get("agenda")),
                  "<h3>What could not be done</h3>", listing(hire.get("could_not"))]
    return """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Ursula — snapshot</title><style>
body{font:16px/1.55 system-ui,sans-serif;max-width:960px;margin:auto;padding:24px;color:#20211f;background:#f6f4ef}
article{border:1px solid #ddd8cd;background:#fffdf9;padding:16px;margin:16px 0;border-radius:8px}
h1,h2,h3,h4{line-height:1.2}h2{margin-top:36px;color:#a8521f}h4{margin-bottom:8px}
p,li,dd,td{overflow-wrap:anywhere;white-space:pre-wrap}dt{font-weight:600}dd{margin:0 0 12px}
table{border-collapse:collapse;width:100%}td,th{padding:8px;text-align:left;border-bottom:1px solid #ddd8cd}
a{color:#a8521f}.gap{color:#b23c17} @media(max-width:600px){body{padding:16px}table{font-size:13px}}
</style><body>""" + "\n".join(parts) + "</body></html>"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    temp = None
    try:
        if args.export.resolve() == args.out.resolve():
            raise ValueError("output must not replace the input export")
        board = render(json.loads(args.export.read_text(encoding="utf-8")))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        # Private work data; replace only after the whole export renders successfully.
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.out.parent,
                                         prefix=".ursula-", delete=False) as handle:
            temp = handle.name
            handle.write(board)
        os.replace(temp, args.out)
        print(args.out.resolve())
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f"Cannot render snapshot: {exc}\n")
    finally:
        if temp and os.path.exists(temp):
            os.unlink(temp)


if __name__ == "__main__":
    main()
