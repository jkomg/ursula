# Bounded runs and recovery

Use this in both hosts for mining and any write batch.

## Freeze the window

At the start of mining record `window_start` (the old watermark) and `window_end`
(the current time, in UTC). Read that bounded window and paginate to exhaustion.
Sources arriving while the run is in progress belong to the next run. On complete
success the new watermark is **window_end**, not the time the last write finished.
Otherwise material arriving during a long write batch would be skipped forever.
Record source ids and observed revisions so changed evidence can be distinguished
from a repeated read. Calendar attachments remain the primary notes index; Drive
title searches are a backstop (`reference/mining.md`).

## Reviewable changesets

Give each proposed action a stable id within the run and record target, action,
current value, proposed value, source references and approval status. Keep existing
calendar tier gates. A direct instruction already authorizing the exact changes
counts as approval; changed scope or changed evidence needs a new decision.

In dry-run show the changeset in the response or a proposed export and stop. No
Jira or Calendar writes, and no staging comment, including for findings discovered
between sessions. The run log, findings and hire scans are still saved to the
operator's private store, marked `mode: dry-run`; the ingested map and watermark
are not touched, because nothing was created (`docs/sandbox.md`).

## Resume a partial batch

For sandbox/live, save a `changesets/<run-id>` record before the first approved
write. Include window bounds, mode, actions and per-action outcomes. Only approved
actions execute. Record the returned Jira key or calendar id immediately after each
success. An action state is `proposed`, `approved`, `applied`, `failed`, `unknown`
or `rejected`. Do not retain tokens or raw connector response bodies.

Before updating a ticket re-read the relevant fields. If they differ from the
approved current value, surface the conflict rather than overwriting another
operator's changes. Merge labels against the fresh list.

If a request times out, mark it `unknown`: failure to receive a response is not proof
that no write happened. Re-read the issue/event, or reconcile a create by source and
scope, before retrying. An inconclusive create is an operator decision, not an
automatic second create. Retry only the unapplied actions, preserving previous
receipts. Sandbox receipts are never evidence that an action was applied in live.

A batch with failed or unknown actions is partial, and keeps the old watermark.
Sandbox progress stays in the sandbox changeset; it never advances the live
watermark or live ingested map. Sandbox calendar changes are proposals only.
Only after all approved actions and required output/state saves succeed, record
the run complete and advance to window_end as the **last** state write. If that
final write fails, resume using the receipts instead of replaying external writes.
