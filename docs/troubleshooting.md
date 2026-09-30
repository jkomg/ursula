# Troubleshooting

## Atlassian disappears from the connector menu

The symptom that wastes the most time, because the board keeps working.

The artifact board calls Atlassian from inside the page at runtime. The chat session
calls it as a loaded tool. **These are separate grants.** The board can be reading
Jira live while Claude cannot query it at all, which looks like everything is fine.

If Claude says it has no Jira tools:

1. Check Settings → Connectors, the full page rather than the in-chat menu. A
   disconnected or "reconnect" state is an expired token — a ten-second fix. The
   in-chat menu hides anything unauthenticated, so an expired grant and a revoked
   one look identical from there.
2. A **request** button where a toggle should be means the org-level enablement is
   gone. Only an owner can restore it.
3. If your company runs its own MCP gateway, whoever operates it is usually faster
   than the generic request form.

Claude must say plainly when Atlassian is unavailable and stop, rather than running
a planning session on calendar data alone and presenting it as complete.

## Queries return nothing when work exists

- **Labels are missing, not the work.** The board is label-driven. Verify against an
  unlabelled project query before concluding a board is empty.
- **Assignee mismatch.** Items may be assigned to someone else or unassigned. An
  epic full of unassigned tasks returns nothing for `assignee = currentUser()`.
- **Excluded project.** Check the config category.

## Exactly 100 results

Truncation, not a total. Narrow or paginate.

## Large results written to a file

The file is a JSON array whose first element has a `text` key holding the payload as
a string. Parse twice — see `reference/jira-conventions.md`.

## Drive search rejects the query

Use `title`, not `name`. `title contains 'x'` matches word prefixes rather than
strict substrings, so it is looser than it looks.

## Notes document with no meeting name

Match to the calendar by timestamp, allowing a few minutes of drift. If nothing
matches, ask rather than guess.

## Labels vanished after an edit

`editJiraIssue` replaces the labels array wholesale. Read, append, write the full
set.

## Two managers filing duplicate findings

Check for an existing card with the same finding key before creating. If duplicates
appear anyway, the shared manager board was probably agreed after the second
operator's first run.

## Jira: 403 "The app is not installed on this instance"

The Atlassian login still works (your profile and the site both come back) but every
Jira call is refused. The claude.ai connection to the site has lapsed. It has happened
more than once (2026-09-23/24 and 2026-09-30). Fix: claude.ai → Settings → Connectors →
Atlassian → disconnect, connect again, approve the site. It is not a Claude Code versus
claude.ai difference: both use the same connector. The board and check-ins say this in
plain words when they see it.
