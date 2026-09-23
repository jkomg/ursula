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

- **This week** — tagged items, sorted by due date ascending then priority. Undated
  items sink to the bottom; that is correct.
- **Calendar** — the cadence window, with collisions marked.
- **Watched boards** — blocked and review-flagged items from reports' boards.
- **Findings** — open findings from the analysis pass, newest first, each with its
  evidence and recommendation.
- **Log** — the running tally. One entry per session. This is the tab that answers
  "what happened three weeks ago," and it is the reason the state lives in the
  database rather than in Claude's memory.

## Updating

Read the current page, change what moved, publish back to the same URL. Passing the
existing artifact URL updates in place rather than creating a second one.

Two artifacts with the same name is a real failure mode — it happened once already.
If a listing shows duplicates, keep the most recently updated and delete the rest
before anyone bookmarks the wrong one.

## What does not go on the page

Secrets of any kind. Shared rows are readable by anyone who can open the artifact.
Cloud ids and project keys are fine; tokens, keys and vault item names are not.
