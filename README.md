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

**Handing this to someone? Run `bin/install.sh --target all` and send the matching
host zip with `INSTALL.md`.** Claude remains the default build target.

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
