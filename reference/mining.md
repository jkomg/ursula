# Mining

Finding commitments the operator made or was given, from everything that happened
since the last watermark.

## Order

Drive first, Gmail second, Calendar third. Drive holds the content; Gmail is the
index; Calendar supplies the context that makes untitled notes interpretable.

## Google Drive — the primary source

Meeting notes are Google Docs owned by the operator, named:

```
<meeting title> - YYYY/MM/DD HH:MM TZ - Notes by Gemini
```

Search:

```
title contains 'Notes by Gemini' and modifiedTime > '<watermark>'
```

`title`, not `name` — the field is rejected otherwise. Read each with
`read_file_content` using the file id.

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

Transcription mangles names, and meeting notes are transcribed. Expect surnames
turned into common words, first names merged, product names phoneticised. Check
extracted names against the config people map and against Jira before creating a
ticket about someone who does not exist.

## Watermark

Update only after a successful run. A partial run that updates the watermark loses
everything it did not reach, silently, forever.
