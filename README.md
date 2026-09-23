# Ursula

A weekly operating harness for a service-delivery manager.

Ursula mines meeting notes, calendar and mail for commitments, reconciles them
against Jira, hunts for contradictions across projects, and produces a one-pager for
the operator's own manager. Two sessions a week: plan and retro.

**The analysis pass is the point.** Mining and ticket-writing are plumbing. The
value is catching that a dependency is scheduled after the thing that consumes it,
that an access grant does not do what someone thinks it does, or that a fix applied
to three tickets left two templates broken. A run that produces tidy tickets and no
findings has done the easy half.

## Layout

```
INSTALL.md                    short install guide — share this with the tarball
SKILL.md                      the skill itself
reference/
  analysis-checks.md          the nine checks, with worked examples
  mining.md                   queries, naming patterns, untitled meetings
  jira-conventions.md         transition ids, label trap, response envelopes
  artifact-board.md           board structure and capabilities
docs/
  setup.md                    the conversational install — start here
  cadence.md                  the weekly rhythm
  troubleshooting.md          when connectors and queries misbehave
config/
  schema.md                   what config and state hold
  example.yaml                illustrative reference
```

## Start

**Handing this to someone? `INSTALL.md` is the page to send with the tarball.**

Read `docs/setup.md` for the full version. Setup is an interview, not a file edit — the operator answers
questions and Claude writes the config. Nobody needs to touch YAML.

## Three tiers of state

| Tier | Holds | Why |
|---|---|---|
| Git | Skill and docs | Versioned, reviewable, propagates to the next operator |
| Artifact database | Config, watermark, run log, tagging history | Per-operator, changes twice a week, no business in version control |
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
