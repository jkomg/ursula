# Ursula — install

Read this first. `docs/setup.md` has the detail; this is the short version.

## What it is

A weekly operating harness. Twice a week you sit down with Claude: Monday it sweeps
your meeting notes, calendar and Jira and helps you decide what the week is; Thursday
it helps you build the note for your manager.

**What it is actually good at** is noticing contradictions — that a thing is due after
the deadline it feeds, that an access grant doesn't do what someone thinks, that a fix
applied to three tickets left two templates broken. The mining and ticket-writing are
plumbing.

**What it is not good at** is finding everything. Testing showed automated mining
reached the source of one ticket in six; the rest came from meetings that produced no
notes anywhere. It now tells you which meetings it couldn't find notes for and asks.
Your own fifteen minutes with your own notes is the primary input, not a supplement.

Nine defects found and fixed across three test runs so far. Expect more.

## Before you start

Four connectors on:

| Connector | What it's for |
|---|---|
| **Atlassian** | Jira — reading and writing your boards |
| **Custom Google Drive** | The Mirantis-built gateway. This is the workhorse: Gmail, Calendar, Docs, Sheets. |
| **Google Drive** | Google's own. Used for finding and reading meeting-notes documents. |
| **Slack** | Read-only. Catches commitments that never reach a meeting. |

Both Google connectors, not one — they do different jobs and the skill calls both.
There is no separate Gmail or Calendar connector; those come through the Mirantis
gateway.

If Atlassian shows a *request* button rather than a toggle, an org owner has to enable
it — that isn't something you can fix by retrying.

## Install

**Run this in claude.ai, not Claude Code.** Your connectors are already provisioned
there, and the config, state and board all live in a claude.ai artifact that Claude
Code cannot reach. Claude Code is the right place to *edit* this repo; it is not where
the skill runs.

1. Extract the tarball.
2. Add the skill through the Skills menu in claude.ai.
3. Start a chat and say: **"set up Ursula"**.

It reads `docs/setup.md` and interviews you. You don't edit any files, and you never
touch YAML.

## Have these answers ready

Claude will ask. Worth thinking about before you sit down.

**Jira**
- Your own project key — where *your* work lives. If you don't have one yet, make one
  first; the skill needs somewhere to write.
- Projects you watch but don't own: the hire boards.
- The shared manager board where findings about the hires go.
- Projects to ignore entirely (templates).

**Cadence**
- Which day you plan, which day you retro.
- Who your one-pager goes to, when, and what sections they want. Ask them; don't guess.
- The specific numbers they ask for every week.

**People** — names and emails for anyone who shows up in your meetings. Meeting
transcripts mangle names badly, and this is what catches it.

**Policies** — any written operating rules a proposal might quietly contradict. This
is the part people skip and later wish they hadn't.

## Start in dry-run

Setup puts you there and you should stay there for two full weeks.

Dry-run reads everything real and **writes nothing**. It shows you every ticket it
would create, every field it would change, every tag it would suggest. Read those lists
and see whether you'd have approved them.

Switch to `live` when two runs in a row look right.

The first run is noisy — it sees two weeks at once and over-proposes. Rejecting things
is how it learns what you care about, so reject freely.

## After setup — what the weeks look like

Setup happens once. After that there is no installation, no commands, and nothing to
maintain. You open a chat and say what you want.

**Monday, about an hour.** Say *"let's do the Monday plan"*.

It opens by asking you to spend fifteen minutes with your own notes and then waits —
that pause is deliberate, and it is the most valuable input of the week. Then it sweeps
Drive, Slack, Gmail and your calendar, matches everything against Jira, tells you which
meetings it could not find notes for, runs the nine checks, and proposes a set of tags,
dates and tickets. You approve or reject each one. In dry-run it stops there and shows
you the list rather than acting.

**Thursday, about forty minutes.** Say *"let's do the retro"*.

What moved, what is blocked and on whom, and your one-pager assembled from notes it has
been staging on a ticket all week. Then it runs the checks again, because a week of new
information usually breaks something you agreed on Monday.

**In between**, nothing scheduled. Paste it something and say *"anything in here for
me?"* when a meeting throws off commitments. Ask it to prep a one-to-one. Ask what is
blocked. It is a standing thing you can talk to, not a job that runs.

**Your board** is a link you keep. It reads Jira and your calendar live, so it is
current whenever you open it, and it carries week to week rather than being rebuilt.

## Two of us running this

We watch some of the same boards, so a couple of rules keep us out of each other's way:

- Neither of our Claudes writes to a hire's own board. Findings go to the shared
  manager board with an assignee.
- We agree that shared board **before** your first run.
- Our setups are completely separate — separate config, separate data, separate
  artifact. Nothing syncs between them. Jira is the only thing we share, which is
  correct, because Jira is already the record.

## What it can't do

- It never sends email and never posts, drafts or reacts in Slack. Those put words in
  your mouth to other people.
- It **can** work your calendar, but only with your say-so each time. Blocking your own
  focus time is one approval; declining someone's invitation is a separate one, because
  they get notified and you should know that before it happens.
- It doesn't know anything about you at the start. My context doesn't transfer — yours
  builds from your own setup interview and your own weeks.
- It won't find every commitment. It'll tell you where it couldn't look.

## If something looks wrong

`docs/troubleshooting.md`. The most common one by far: Claude says it has no Jira
access while your board still works fine. Those are two different permissions and the
fix is in there.
