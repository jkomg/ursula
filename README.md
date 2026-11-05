# Ursula

A weekly operating harness for a service-delivery manager, for Claude or ChatGPT/Codex.

Ursula mines meeting notes, calendar and mail for commitments, reconciles them
against Jira, hunts for contradictions across projects, and produces a one-pager for
the operator's own manager. Two sessions a week: plan and retro.

**The analysis pass is the point.** Mining and ticket-writing are plumbing. The
value is catching that a dependency is scheduled after the thing that consumes it,
that an access grant does not do what someone thinks it does, or that a fix applied
to three tickets left two templates broken. A run that produces tidy tickets and no
findings has done the easy half, unless it shows per check what ran clean and why.

## Install

Download from the [latest release](https://github.com/jkomg/ursula/releases/latest).
Each release has three zips, one per route below. Do not use GitHub's green **Code →
Download ZIP** button: that zip is the whole repository, not an installable skill,
and it carries no version, so the skill cannot tell you what it is running.

### 1. claude.ai (the usual route)

1. In claude.ai, turn on four connectors: **Atlassian**, **Custom Google Drive** (the
   Mirantis gateway, which carries Gmail, Calendar and Docs), **Google Drive** (Google's
   own, used to find meeting notes) and **Slack**. Both Google connectors are needed. If
   Atlassian shows a *request* button rather than a toggle, an org owner has to enable it.
2. Download `ursula-<version>.zip`. **Do not unzip it.** If your Mac unzipped it,
   upload the original download.
3. Settings → Capabilities → Skills → upload the zip. If Ursula is already installed,
   replace it. Two copies trigger unpredictably.
4. In a fresh chat, ask **"Which Ursula version is running?"** It should name the
   release version. That is the only proof the upload took.
5. Say **"Set up Ursula"** and answer the interview. It verifies each connector by
   reading from it and creates your own board. You never edit a file.
6. Mind the mode (see below).

More detail: [`INSTALL.md`](INSTALL.md) and [`docs/setup.md`](docs/setup.md).

### 2. On your own machine (T3 or Claude Code)

The only route where the safety rails run: hooks, the call ledger and the LiteLLM
reviewer. Use it in addition to claude.ai, or instead of it.

1. Install Python 3.8 or newer. On Windows, install it from python.org or with
   `winget install Python.Python.3.12` (the built-in `python3` is only a Store
   shortcut), and install Git for Windows for `bash`.
2. Download `ursula-desktop-<version>.zip` and **unzip it** into a work folder, for
   example `Documents/ursula`. To update, unzip the newer one over the same folder:
   your local settings and state are not in the zip, so they are kept.
3. Open the folder in T3 or Claude Code. In T3, use **Claude as the provider**: under
   Codex the hooks do not run, so check-ins always come back partial.
4. Run `bash bin/rails-check`. Every line should say `ok`, apart from LiteLLM until
   step 5. Stop on any `FAIL`.
5. If you have a LiteLLM key, store it yourself with the command in
   [`docs/desktop.md`](docs/desktop.md). Never paste it into a chat.
6. Say **"Set up Ursula"**, or after an update, **"Ursula, check my setup after the
   update"**.

More detail: [`docs/desktop.md`](docs/desktop.md); Windows at Mirantis:
[`docs/windows-mirantis.md`](docs/windows-mirantis.md).

### 3. ChatGPT or Codex

1. Make sure ChatGPT or Codex can reach Jira, Google Drive, Gmail, Calendar and
   Slack. Your organisation may need to approve access.
2. Download `ursula-openai-<version>.zip`. Unzip it only if your installer asks you
   to; some accept the zip directly.
3. Install it the way your ChatGPT desktop app or Codex takes skills. ChatGPT in a
   browser or on a phone needs an organisation plugin that includes Ursula; this zip
   is not that plugin.
4. In a new chat say **"Set up Ursula in dry-run. Explain each step in plain
   language."** If it is not recognised, pick it first: `@` in ChatGPT, `$ursula` in
   Codex.

There is no live board on this route: you get a dated snapshot and private state
files. More detail: [`docs/chatgpt.md`](docs/chatgpt.md).

### Mode, on every route

You start in **dry-run**: Ursula reads everything real and sends nothing. Move to
**live** after two cadences that looked right. In live, pressing **Approve** on the
board really sends the email, Slack message, Jira comment or calendar block. **Sandbox**
sends Jira writes only to a throwaway project and never touches the calendar, so set
that project first ([`docs/sandbox.md`](docs/sandbox.md)).

## Layout

```
INSTALL.md                    short install guide — share this with the zip
bin/install.sh                checks the skill and builds the zip — see docs/release.md
SKILL.md                      the skill itself
reference/
  analysis-checks.md          the core checks, and how packs work
  packs/
    service-delivery.md       onboarding, access grants, templated boards
    content-cleanup.md        Confluence: stale, orphaned, duplicate, unowned pages
  mining.md                   queries, naming patterns, untitled meetings
  jira-conventions.md         transition ids, label trap, response envelopes
  artifact-board.md           board structure and capabilities
  hire-scan.md                one person's board, as its own tab on the board
  outbox.md                   proposals another person will read: approve on the board, receipts kept
  always-on.md                check-ins between sessions, and how much the operator hears
docs/
  setup.md                    the conversational install — start here
  cadence.md                  the weekly rhythm
  routine.md                  turning on scheduled check-ins (a claude.ai cloud routine)
  troubleshooting.md          when connectors and queries misbehave
config/
  schema.md                   what config and state hold
  example.yaml                illustrative reference
```

## Start

**Handing this to someone?** Point them at the latest release and the Install
section above. To cut a release, run `bin/install.sh --target all` on a clean
checkout and attach the three zips from `dist/` to a release tagged
`v<version>` (`docs/release.md`).

ChatGPT/Codex installation and setup: `docs/chatgpt.md`. Both hosts use the same
cadence and checks. Claude has a live artifact board; ChatGPT/Codex has a portable,
dated snapshot and private state files or an explicit export. The Python 3 helper
`scripts/render_snapshot.py` can produce that snapshot for either host.

Between sessions, a scheduled cloud routine runs short **check-ins**
(`reference/always-on.md`): it reads the operator's Slack DM and new notes, stages
findings, and puts anything that should reach another person in the **outbox**, where
the operator approves it on the board and the board sends it and keeps the receipt
(`reference/outbox.md`). How much the operator hears is theirs to set, quiet to chatty.

Write batches now carry per-action receipts for resuming partial runs, and mining
uses a frozen window so notes arriving during write-back are picked up next time
(`reference/run-recovery.md`).

Read `docs/setup.md` for the full version. Setup is an interview, not a file edit — the operator answers
questions and the assistant writes the config. Nobody needs to touch YAML.

## Three tiers of state

| Tier | Holds | Why |
|---|---|---|
| Git | Skill and docs | Versioned, reviewable, propagates to the next operator |
| Private state store | Config, watermark, run log, tagging history | Claude artifact database or ChatGPT/Codex files/export; per-operator, outside version control |
| Jira | Everything two people must agree on | Already the system of record. A second shared store immediately disagrees with the first. |

## Multiple operators

Two managers can run Ursula against overlapping boards, each with their own install,
artifact and database. Nothing is shared between instances directly — coordination
happens in Jira.

Neither instance writes to an individual's own board. Findings about watched boards
become cards on the shared manager board with an assignee.

## Status

Early. Written from one operator's live cadence and not yet run end to end from a
cold install. Expect the setup interview to have gaps.
