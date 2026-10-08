# Hire scan

A scan of one person's board, written to a tab of its own on the operator's board. Asked
for by name — "scan Vandit's board", "prep me for my one-to-one with Jonathan" — usually
on Monday or Tuesday morning before the week's one-to-ones.

It is the Thursday blocked sweep (`docs/cadence.md`, "The team call") filtered to one
person and kept. The sweep answers "what is stuck across everyone"; the scan answers
"what does this person need from me this week", and leaves the answer on the board
where the operator can open it in the one-to-one instead of scrolling back through a
chat.

## Who can be scanned

Anyone in `config/people` with a `board` — a watched project key. If the named person
has no board in config, or their name does not resolve against the people map, stop
and ask. Never guess which project is theirs: two hires with similar names and
neighbouring keys is the normal case, and a scan of the wrong board is worse than
none because it looks right.

## What it reads

1. **Their board's open set** — `project = <board> AND statusCategory != Done`, paged
   to exhaustion (`reference/jira-conventions.md`, result caps). Then the items
   resolved since the last scan (`resolved >= <last scanned_at>`), for *moved*.
2. **The previous scan** — `hires/<slug>`, if one exists, for what moved and which
   findings are carried.
3. **Their notes and messages since the last scan** — the one-to-one notes documents
   (calendar attachments first, `reference/mining.md`), Slack DMs with them, and
   mentions of the operator on their board with no reply. This is where "waiting on
   you" comes from, and it rarely shows in ticket status.
4. **The next one-to-one on the calendar** — so the agenda is for a real meeting.

## What it checks

The core checks that make sense for one board — `self-blocking`, `stale-parent`,
`deadline-inversion`, `orphaned-commitment` — and every enabled pack's checks scoped
to this board. With `service-delivery` on, `template-propagation` still searches the
excluded template projects: a broken card on this hire's board is usually broken for
the next hire too.

Findings are written like any other (`config/schema.md`), with `subject` set to the
hire's slug, so they show both on the hire's tab and on the Findings tab.

## What it writes

The watched-board rule holds: **nothing is written to their board.** Everything
the scan produces goes to the operator's agreed private state store, in every mode
(`docs/sandbox.md`) — a scan in dry-run still produces the hire's tab, marked with
its mode. Findings that need a card on the shared manager board are proposed in the
chat, in the same batch-and-confirm way as a planning session, and created only
outside `dry-run`.

| Document | What |
|---|---|
| `hires/<slug>` | The latest scan. The board renders exactly these fields; shape in `config/schema.md` |
| `hires/<slug>/scans/<date>` | A copy of the same body, so a later scan can say what moved and the operator can look back |
| `findings/<key>` | One per finding, `subject: <slug>` |
| `runs/<date>-hire-<slug>` | A run-log entry, `session: hire-scan` |

**Keep it about the work.** Anyone the operator shares their board with can read these
documents. A scan says what is blocked, on whom, and what the operator owes; it does
not assess the person. "Three items overdue, two waiting on access" is a scan. "Seems
disengaged" is not, and does not go in the database or the chat summary.

## What the tab shows

The scan's judgement as of `scanned_at`, and under it the board read live from Jira
when the tab is opened in Claude. ChatGPT/Codex's portable board shows the dated scan
and exported Jira items, without live reads (`reference/runtime.md`). The live list marks items the scan named, so the operator can
see at a glance what changed since the scan ran. A scan older than a week is flagged
on the tab; ask for a fresh one rather than walking into a one-to-one with it.

## Ending the scan

Say in chat, briefly: the summary line, what is waiting on the operator, the agenda,
and anything that could not be done — a capped query, a notes document that could not
be opened, a name that did not resolve. Then give the board link. The tab is the
record; the chat is the headline.
