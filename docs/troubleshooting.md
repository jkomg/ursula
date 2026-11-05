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

## A notes document "exceeds the tool limit"

Long Gemini documents (an hour's meeting with its transcript tab) run past 90,000
characters and `read_file_content` fails. Export as plain text with
`gws_drive_files_export` or read the tabs with `gws_docs_documents_get`; see
`reference/mining.md`, "Long documents". Seen in five check-ins, 28 Oct to 2 Nov.

## Check-ins stay partial and the watermark does not move

Read the last runs' `could_not`. If the gap is unopened Gmail, the exclusion list
(`config/checkins.gmail_exclude`) is missing a noisy sender. If it is one document,
it should be in `carried_sources`, which lets the watermark move; a run that holds the
whole window for one item is following the old rule. A source carried three times
becomes an `unreadable-source-<id>` finding.

## Gmail list returns 502, or the same messages for every window

`google_gmail_messages_list` on the Mirantis gateway answers 502 intermittently. Switch
to `gws_gmail_users_messages_list` for the rest of the run, and check that the dates
returned fall inside the window: on 16 Oct an `after:` filter was ignored and every
window returned the same 24 messages.

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
