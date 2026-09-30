# The artifact board

This is the Claude native live board. For ChatGPT/Codex or a portable copy from
either host, use the snapshot in `reference/runtime.md` and
`scripts/render_snapshot.py`. The snapshot has no live bridge or write buttons.

A standing page, updated in place, week after week. Never a fresh artifact per
cadence — the URL is something the operator bookmarks and returns to.

## Capabilities

Declared at publish:

- `mcp` — the page queries Jira and Calendar live at runtime with the viewer's own
  connectors. Data is current when the page is opened, not when it was written.
- `db` — config, state and the running log.
- `user` — identifies the viewer, and scopes per-viewer private rows.

Capability declaration is a full-set operation. Restate everything on republish, or
omit the field entirely to carry the stored set forward. Passing a partial set
revokes what is left out.

Before writing any code that calls a connector from the page, observe one real
request and response for that tool in session. Never publish a guessed shape.

## Structure

Three tabs. The selected tab is remembered per browser.

- **This week** — tagged items read live from Jira, sorted by due date ascending then
  priority, and the calendar for the week with open time. Undated items sink to the
  bottom; that is correct.
- **One tab per hire** — one for each document in `hires`, between This week and
  Findings, appearing after the first scan of that person (`reference/hire-scan.md`).
  The scan's judgement first — waiting on the operator, blocked, flagged, overdue,
  moved, the one-to-one agenda, that hire's findings — then their board read live
  from Jira, read-only, with the items the scan named marked. The live read uses the
  same `searchJiraIssuesUsingJql` grant as This week, so the tab needs no new
  capability.
- **Outbox** — the `outbox` collection (`reference/outbox.md`): what is waiting for the
  operator's OK first, then everything sent and decided, folded. Approving sends with the
  viewer's own connector and writes the receipt; the text can be edited before sending,
  and the original is kept. Dry-run items get Right / Wrong instead of Approve. The top
  of the tab is the heads-up control — Quiet, Daily, Chatty and the two channels — which
  writes `config/voice`, the one config document the board changes. Under it, **Tell
  Ursula**: the operator writes a note (`notes`), and the next check-in or session
  answers on it. This is the conversation channel; nothing goes through Slack.
- **Findings** — the `findings` collection, open ones ordered by `rank`, closed ones
  folded underneath. Each shows evidence, consequence, recommendation and links. The
  operator can mark one resolved or not a finding (with a reason); that writes back to
  the database for the next session, never to Jira.
- **Log** — the `runs` collection, newest first. One entry per session; check-ins are one
  line each, with anything they could not do. This is the tab
  that answers "what happened three weeks ago," and it is the reason the state lives in
  the database rather than in Claude's memory. An entry missing the coverage list, skip
  count or could-not list is marked *not recorded*.

Field shapes for both collections are in `config/schema.md`; change them there first,
then the page. Findings and Log read the database only — they work when Jira is
unreachable, which is also when they are most useful.

Not built yet: a **Watched boards** tab across every report at once. Hire tabs cover one
person at a time; the Thursday sweep still produces the all-boards view in chat.

## Publishing this version

`artifact/index.html` is the baseline. **This version adds tools**, for the Outbox tab, so
the first republish of it must pass the **complete** set, not omit it:

```json
{"db": {}, "user": {},
 "mcp": {"servers": [
   {"server": "Atlassian", "tools": ["getAccessibleAtlassianResources", "searchJiraIssuesUsingJql",
     "getTransitionsForJiraIssue", "transitionJiraIssue", "addCommentToJiraIssue"]},
   {"server": "Custom Google Drive", "tools": ["google_calendar_events_list", "gws_gmail_send",
     "gws_calendar_events_insert"]},
   {"server": "Slack", "tools": ["slack_send_message"]}]}}
```

Read the live board's stored set first and add anything it has that this list lacks: a
full-set declaration revokes whatever it leaves out. Every later republish omits
`capabilities` again. The viewer is asked once for each newly granted connector, on
first use. The Slack send's answer shape has not been observed from the page; the board
keeps the first 300 characters of it as the receipt until it has been.

## Updating

Read the current page, change what moved, publish back to the same URL. Passing the
existing artifact URL updates in place rather than creating a second one.

Two artifacts with the same name is a real failure mode — it happened once already.
If a listing shows duplicates, keep the most recently updated and delete the rest
before anyone bookmarks the wrong one.

## What does not go on the page

Secrets of any kind. Shared rows are readable by anyone who can open the artifact.
Cloud ids and project keys are fine; tokens, keys and vault item names are not.
