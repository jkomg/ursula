# Mining

Finding commitments the operator made or was given, from everything that happened
since the last watermark.

## Order

**Calendar first**, then Drive, then Gmail. The calendar is the only complete record of
what happened; Drive holds most of the content; Gmail adds almost nothing on top of
Drive and is worth one query, not a strategy.

Measured over one week: Drive returned six unique notes documents, Gmail four — all
four already in the Drive set. Gmail only carries notes for meetings the operator was
*individually invited* to and where Gemini ran. A meeting the operator attended without
a personal invite produces no email at all, though the document may still be shared
into their Drive.

## Coverage is the point, and it is worse than it looks

**Automated mining does not reach most of what matters.** In the same measured week,
six tickets came out of the operator's meetings. Drive and Gmail between them found
the source for **one**. The other five came from two meetings that produced no
reachable Gemini notes whatsoever — no document, no email, nothing.

This is not a query bug and no query fixes it. Notes exist only when Gemini ran and
the artefact reached the operator. Recurring internal syncs and ad-hoc calls very often
produce neither.

So every mining pass ends with a **coverage check**:

1. List every calendar event in the window that the operator accepted.
2. Take the attached documents from each; then run the Drive search and fold in
   anything it found that no event carried.
3. Report events with no attachment and no matching document, by name, and ask the
   operator what came out of them.

Do not skip the Drive pass — an ad-hoc call that never had a calendar entry produces a
document and no event. The two passes cover different gaps.

This is the step that turns a sweep finding one-sixth of the week into a sweep the
operator can trust. It also makes Pass 0 — the operator's own fifteen minutes — load
bearing rather than a courtesy: for the meetings with no notes, their memory and their
handwriting are the only record that exists.

Never report a mining pass as complete without the coverage check. A list of six
documents looks thorough and can still be missing the two meetings that generated most
of the week's work.

## Calendar attachments — the primary index

**Notes documents are attached to their calendar events.** Read the event list for the
window with attachments and take the document ids from there. The calendar already
knows which document belongs to which meeting, which removes every hard problem in the
Drive-search approach at once: no timestamp matching for untitled meetings, no
shortcut-versus-target dedupe, and no assumption about how the document is named.

Measured against a real three-day window, a Drive title search missed four documents
that were sitting in plain view as calendar attachments:

* a one-to-one whose notes existed but were reported as missing
* two meetings that produced **two** notes documents each, only one of which the search
  found
* the most important meeting of the week, whose notes were titled `Notes - <meeting>`
  rather than `<meeting> - Notes by Gemini`, so no title pattern could reach it

Take everything from the attachment list: notes, recordings, pre-reads, spreadsheets.
An event with no attachment is a genuine coverage gap and goes on the list to ask about.

## Google Drive — the backstop, not the primary source

Meeting notes are Google Docs owned by the operator, named:

```
<meeting title> - YYYY/MM/DD HH:MM TZ - Notes by Gemini
```

Search:

```
title contains 'Notes by Gemini' and createdTime > '<watermark>'
```

`title`, not `name` — the field is rejected otherwise.

**Use `createdTime`, never `modifiedTime`.** A notes document is written once when the
meeting ends and then touched again whenever anyone opens or tidies it. Filtering on
`modifiedTime` resurfaces old meetings: a call from two weeks ago whose doc was edited
yesterday looks new. Observed: a 9 September meeting reappeared in a 22 September
window.

Belt and braces — the meeting date is in the title, `<name> - YYYY/MM/DD HH:MM TZ -
Notes by Gemini`. Parse it and discard anything older than the watermark regardless of
what the timestamps say. Where the parsed date and `createdTime` disagree by more than a
day, trust the title and note the discrepancy.

**Follow `nextPageToken` every time.** Drive returns a short page and a continuation
token even when `pageSize` is set much higher — a request for 20 came back with 5 and a
token. Treating the first page as the full set silently drops sources. Observed: the
document that mattered most in a run was in the unread remainder, and the run reported
a clean result.

**Not every result is a document.** Some entries come back as
`application/vnd.google-apps.shortcut` — a pointer, not a file, and
`read_file_content` will not open one. Check `mimeType` before reading. Resolve the
shortcut to its target if the target is reachable; otherwise skip it and **say so in the
run report** rather than passing over it silently. A shortcut usually means the real
document lives in someone else's drive, which is itself worth knowing.

**Deduplicate before reading.** A shortcut and its target both match the search and both
carry the same title, so the same meeting appears twice. Group results by title plus the
meeting timestamp parsed from it, and keep one: prefer the real document over the
shortcut, and the owner's copy over a shared copy. Without this the same meeting is
either ingested twice or skipped entirely because the only copy examined was the
unreadable one.

A meeting whose notes are owned by someone else is worth flagging in the run report.
It means the operator attended, not convened — and the action items in it are usually
assigned to other people, which makes them dependencies rather than tasks.

Also sweep for documents shared with the operator since the watermark, which is how
substantive material arrives:

```
owner = '<colleague>@<domain>' and modifiedTime > '<watermark>'
```

Colleagues worth standing queries are listed in the people map in config. A document
revised *after* it was shared is the one that matters — a revision date later than
the share date means the operator may be working from a stale copy.

## Gmail — index and direct commitments

Gemini notification mail:

```
from:gemini-notes@google.com newer_than:<N>d
```

Subject: `Notes: "<meeting title>" <date>`. Roughly ten a week for an active
manager. The body only links out, so use this to confirm Drive missed nothing rather
than as a content source.

`messages_list` returns ids only. `messages_get` with `format: metadata` gives
headers and a snippet cheaply; reserve `full` for messages actually being read.

Then sweep for commitments made directly over mail — threads where the operator
promised something, or was asked for something and has not replied. These never
appear in meeting notes and are a common source of self-blocking findings.

## Slack

Meeting notes capture meetings. Slack captures everything else, and a measurable share
of commitments never reach a meeting at all. Two days of messages surfaced three
commitments with no ticket behind any of them: a document review requested of the
operator, a blocked new hire asking a question that stalled their onboarding, and a
promise the operator made to a colleague about checking access.

**Read-only. Never post, never draft, never react.**

Three targeted searches, not a general sweep:

1. **Direct messages since the watermark** — `is:dm after:<date>`. Where requests and
   promises actually live.
2. **Mentions of the operator with no reply from them** — the strongest self-blocking
   signal available anywhere, and Slack is where it lives.
3. **Named channels from config** — the two or three that carry real work.

**Filter out app DMs or the signal drowns.** Thirteen of twenty results in the measured
run were notification DMs from Jira, Google Calendar and Google Drive. These are app
conversations, not bot messages, so the `include_bots` flag does not exclude them.
Drop any DM whose counterpart is an installed app by name, and keep a list of those
names in config.

Extract the same things as from notes: requests made *of* the operator, promises made
*by* them, and questions left unanswered. A question to the operator that has sat
unanswered while the asker is blocked is a finding, not a task.

## Calendar

- The cadence window ahead, for collisions and for the real shape of the week
- Event **description** changes: a recurring one-to-one whose description has been
  rewritten is a changed expectation, and it will not announce itself
- Attachments on events, which is where pre-reads live
- Timestamps, for matching untitled notes

## Untitled meetings

Some notes documents have no meeting name:

```
Meeting started 2026/09/21 13:25 EDT - Notes by Gemini
```

Match to the calendar by timestamp. Allow a few minutes of drift — notes are stamped
when recording starts, not when the meeting was scheduled. If nothing matches,
present the document with its timestamp and ask, rather than guessing whose meeting
it was.

## Extraction

For each document, pull:

- **Action items** — with an owner. An unassigned action item is a finding, not a
  ticket.
- **Decisions** — especially ones that overrode what the operator proposed. These
  change downstream work and rarely get tickets.
- **Numbers** — counts, dates, sizes. These feed the scope-drift check.
- **Commitments made to the operator** — tracked as dependencies with a name.
- **Anything contradicting a stated policy** — feeds the policy-conflict check.

Every extracted item keeps a reference to its source document and the line it came
from. A ticket that cannot be traced back to the sentence that created it is
unarguable when someone disputes it.

## Names

Transcription mangles names, and meeting notes are transcribed. This is not an edge
case — it is the normal condition, and it is worse than it looks.

Observed in a single 30-minute call: the company's own name, two product names, a
customer, a partner, the operator's manager, and the person the meeting was with —
all mangled. One colleague's first name was replaced with a different name entirely in
the closing exchange, which is the dangerous kind, because it reads as a real person.

So: resolve every extracted name against the config people map before it reaches a
ticket. A name that does not resolve is a question for the operator, never a guess. Do
the same for product and customer names — the people map should carry an aliases list
for those too, seeded from the mangles seen so far.

## Watermark

Update only after a successful run. A partial run that updates the watermark loses
everything it did not reach, silently, forever.
