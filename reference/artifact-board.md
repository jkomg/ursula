# The artifact board

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
- **Findings** — the `findings` collection, open ones ordered by `rank`, closed ones
  folded underneath. Each shows evidence, consequence, recommendation and links. The
  operator can mark one resolved or not a finding (with a reason); that writes back to
  the database for the next session, never to Jira.
- **Log** — the `runs` collection, newest first. One entry per session. This is the tab
  that answers "what happened three weeks ago," and it is the reason the state lives in
  the database rather than in Claude's memory. An entry missing the coverage list, skip
  count or could-not list is marked *not recorded*.

Field shapes for both collections are in `config/schema.md`; change them there first,
then the page. Findings and Log read the database only — they work when Jira is
unreachable, which is also when they are most useful.

Not built yet: a **Watched boards** tab (blocked and review-flagged items from reports'
boards). The Thursday sweep produces it in chat for now.

## Publishing this version

`artifact/index.html` is the baseline. It needs the capabilities the live board already
has — `mcp` (Atlassian: `getAccessibleAtlassianResources`, `searchJiraIssuesUsingJql`,
`getTransitionsForJiraIssue`, `transitionJiraIssue`, `addCommentToJiraIssue`; Custom
Google Drive: `google_calendar_events_list`), `db` and `user` — and no new ones. So
republish it to the existing URL **with `capabilities` omitted**. Passing a set would
replace the stored one and risk dropping a connector grant.

## Updating

Read the current page, change what moved, publish back to the same URL. Passing the
existing artifact URL updates in place rather than creating a second one.

Two artifacts with the same name is a real failure mode — it happened once already.
If a listing shows duplicates, keep the most recently updated and delete the rest
before anyone bookmarks the wrong one.

## What does not go on the page

Secrets of any kind. Shared rows are readable by anyone who can open the artifact.
Cloud ids and project keys are fine; tokens, keys and vault item names are not.
