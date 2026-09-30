# Testing and sandboxing

Two things in Ursula have side effects other people can see: **Jira writes and
Calendar writes.** Mining is read-only, and the run log, findings and hire scans go
to the operator's own private store, which nobody else reads. So isolation is a
question about Jira and Calendar writes, not about the whole pipeline — which is
lucky, because the pipeline is exactly what you want to test against real data.
Modes apply across both hosts.

## Three modes

Set in `config/run`.

### `dry-run` — the default for a new install

Reads everything real. Writes nothing to Jira or Calendar. Emits a changeset: every
ticket it would create with full body, every field it would change with before and
after, every comment it would post (the one-pager staging comment included), every
tag it would propose.

It does record the run log, the findings and any hire scan in the operator's private
store, each marked `mode: dry-run`. Those are how the board's Findings, Log and hire
tabs show what the checks found while the operator is deciding whether to trust the
proposals; a dry-run that left the board empty would be judged on chat scrollback.
It does not advance the watermark or the ingested map, because nothing was created.
See `reference/run-recovery.md`.

This is the honest end-to-end test. It exercises mining, reconciliation, every
enabled check and the routing decisions against your actual boards, and the only thing
missing is the mutation. A sandbox Jira project cannot test routing, because the
routing decision *is* which real project a thing belongs in.

Leave a new operator here for two full cadences.

### `sandbox` — for testing the write path

Reads real boards. Redirects every Jira write to one sandbox project. Calendar
changes remain proposals in sandbox: a Jira sandbox does not isolate calendars.
Operational records retain `mode: sandbox` and never advance the live mining
watermark or live ingested mappings; save sandbox progress in its changeset instead.
Use this to
exercise the mechanics that dry-run cannot prove: label replacement actually
preserving existing labels, transitions landing on the right status, comment
formatting rendering correctly, the duplicate-key check firing.

Create a throwaway project, put its key in `config/run.sandbox_project`, and expect
the tickets to be nonsense. You are testing the plumbing, not the content.

### `live`

Normal operation. Go here when a dry-run changeset has looked right twice running.

## Prohibitions that hold in every mode

The gateway makes write tools available well beyond Jira. The skill must never
touch them:

- **Never send email.** Gmail send, reply and forward are loadable. Read-only.
- **Never post to Slack.** Read-only.
- **Never edit, move, archive, delete or comment on a Confluence page.** Read-only.
  Changes to pages become tickets in the cleanup backlog (`reference/packs/content-cleanup.md`).
- **Calendar writes only under the tiered approval in `SKILL.md`**, and never in
  `dry-run`. Earlier versions of this page said never; that was superseded when the
  tiers were added, because a planning session that finds three collisions and can fix
  none of them is doing half a job.
- **No unsolicited writes to a watched board.** Findings go to the shared manager board.
  A direct instruction from the operator — an update they promised someone — overrides
  this (`test/golden-week.md`, defect 3).

These are in `config/run.prohibitions` so they survive a config export.

## The golden-week fixture

The best regression test available is a week that has already been processed by
hand. See `test/golden-week.md`.

The principle generalises: after any week you have worked through carefully, record
the sources and the outcomes. A skill that reproduces a known-good week is a skill
you can trust on an unknown one.

## Before handing it to another operator

1. Two dry-run cadences that produce changesets you would have approved
2. One sandbox run proving the write mechanics
3. One live run with the operator reading every proposal before applying
4. The golden-week fixture passing

Then they install in `dry-run` and repeat for themselves. Nobody's first experience
of this should be it writing to their Jira.
