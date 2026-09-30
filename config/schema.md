# Config schema

The record shapes are shared by both hosts. Claude stores them in its artifact
database. ChatGPT/Codex uses private JSON files or a supplied export, and a snapshot
board; see `reference/runtime.md`. Neither host inherits the other's state.

Config lives in the agreed store, collection `config`. The YAML in
this directory is a reference and an export format — it is not the input path.
Setup is a conversation.

## Documents

### `config/run`

`mode`: `dry-run` (initial), `sandbox` or `live`; `status`: `incomplete` until the
setup completion contract passes, then `complete`. Record missing setup checks
alongside status. `sandbox_project` is required in sandbox. `prohibitions` records
the hard limits in `SKILL.md`; `calendar` may restrict the allowed approval tiers.
Missing mode is dry-run, never implicit permission to write.

### `config/jira`

| Field | Notes |
|---|---|
| `cloud_id` | Atlassian cloud id |
| `owned` | Project keys, read and write |
| `watched` | Project keys, read only |
| `shared_manager_board` | One key, where findings about watched boards land |
| `excluded` | Templates and probes |
| `transitions` | Status name to transition id |

### `config/labels`

`priority` (default `ursula`), `week_format` (default `w{iso_week}`),
`review` (default `needs-review`).

### `config/cadence`

`plan` and `retro` each take a day and time. `onepager` takes a recipient, a
deadline, and the required section list.

### `config/numbers`

The figures the recipient asks for every week. Each has a label and a source — a JQL
query, or `manual` where no query can produce it.

### `config/people`

Name, role, email, and any Jira account id. Used for owner resolution, standing
Drive queries, and correcting transcription errors.

### `config/policies`

Written operating rules a proposal might contradict. Each has a name, a statement,
and a ticket reference where one exists. Drives the policy-conflict check.

### `config/packs`

| Field | Notes |
|---|---|
| `enabled` | Pack names, e.g. `[service-delivery]`. Empty means core checks only, and the config read-back says so |
| `content-cleanup` | Present only when that pack is enabled: `spaces`, `space_ids`, `stale_days`, `exempt_labels`, `owner_rule`, `bulk_editors`, `backlog_project`, `ticket_batching`. Definitions and the reason each is asked are in `reference/packs/content-cleanup.md` |

A pack in `enabled` with its config missing is an incomplete setup, not a pack that
runs on defaults.

### `config/voice`

How much the operator hears between sessions (`reference/always-on.md`, "Heads-up").
**The board writes this document**, from the control on its Outbox tab; the interview
only sets the starting value. It is the one config document the board may change.

| Field | Notes |
|---|---|
| `level` | `quiet` (default) · `daily` · `chatty` |
| `channels` | `{slack_dm: bool}`. Default `false`. A running log in the operator's own DM; works only when the routine's environment carries the guard settings. The interrupt is the routine's own notification, which needs no config |
| `updated_at`, `updated_by` | Set by the board |

### `config/checkins`

| Field | Notes |
|---|---|
| `enabled` | `true` once the routine exists (`docs/routine.md`) |
| `routine` | The routine's claude.ai link, so the operator can find it to pause it |
| `schedule` | Human-readable, e.g. "weekdays 8am, noon, 4pm ET" |
| `slack_dm` | The channel id of the operator's DM with themselves (a `D…` id) |

## State

Operational, not configuration. Same database, `state` collection.

| Document | Holds |
|---|---|
| `state/watermark` | Timestamp of last successful mine. Only updated on success. |
| `state/ingested` | Source document id to created issue keys. Prevents re-ingestion. |
| `state/tagging` | Proposals and whether the operator accepted them. |
| `state/checkin` | `watermark` (the check-ins' own, never the cadence's) and `slack_last_ts` (newest operator DM message read). Advanced only by a completed check-in. |

### `outbox/<id>`

Every proposed action another person will read, and every calendar change, with its
approval and receipt. Written by sessions and check-ins; approved, sent and receipted by
the board. The full field list and the rules are in `reference/outbox.md`; change them
there first, then the board.

Findings and the run log are **collections, one document each**, not single documents.
The board's Findings and Log tabs read them, and a single growing document would hit
the 256 KiB per-document limit within a year of weekly runs. Earlier versions named
them `state/findings` and `state/runs`; a config that still has those should have them
moved on the next run.

### `findings/<key>`

One document per finding. The document id is the finding key,
`<subject>-<check>-<week>`: the person or space the finding is about, the check slug,
the ISO week it was first raised (`adrienne-self-blocking-w39`, `DOCS-stale-page-w40`).
Ids allow only letters, digits and `_ - . ~ : @ +`, so slug names: lower case, spaces to
hyphens, no accents.

| Field | Notes |
|---|---|
| `key` | Same as the document id |
| `check` | Check slug, e.g. `deadline-inversion` |
| `pack` | `core`, or the pack name |
| `title` | One line, readable cold |
| `status` | `open` · `carried` (open and seen again this run) · `resolved` · `dismissed` |
| `rank` | Order by consequence this run; 1 is the most serious. The board sorts on it |
| `first_seen`, `last_seen` | ISO dates |
| `evidence`, `consequence`, `recommendation` | Plain text. A finding without a recommendation is unfinished |
| `refs` | `[{label, url}]` — tickets, pages, documents. The board links only `https://` urls |
| `subject` | Optional. The hire's slug when the finding is about one person's board; the finding then also shows on that hire's tab |
| `closed_at`, `closed_by`, `close_note` | Set when closed. `closed_by` is `session` or `board` |

**The operator can close findings from the board.** `Resolved` and `Not a finding` set
`status`, `closed_by: "board"` and a `close_note`; a dismissal requires a reason. The
next session reads these before Pass 3: a dismissed finding is not raised again unless
its evidence has changed, and its `close_note` is the operator saying why the check
fired wrongly — log it in `test/golden-week.md` if it is a check defect. The board never
touches Jira for a finding; any ticket change is the session's, in the next Pass 5.

### `runs/<date>-<session>`

One document per session, id like `2026-09-28-plan`, `2026-10-01-retro`, `-adhoc` for
anything between, `2026-09-29-hire-vandit` for a hire scan, `2026-10-01-checkin-1600` for a
check-in. The board shows the latest 52 sessions and folds check-ins under the day they ran.

| Field | Notes |
|---|---|
| `date` | ISO date. The board orders on it |
| `session` | `plan` · `retro` · `adhoc` · `hire-scan` · `checkin` |
| `time` | Check-ins only: local `HH:MM` the check-in ran, read from the clock |
| `mode` | `dry-run` · `sandbox` · `live` |
| `status` | `complete` · `partial` · `failed`. Only `complete` advances the watermark |
| `summary` | One or two sentences |
| `watermark_before`, `watermark_after` | Timestamps; after remains before on a partial/failed run |
| `window_start`, `window_end` | Frozen UTC mining bounds; only a successful run advances to window_end |
| `sources` | `{found, expected, unmatched_meetings: [names]}` — `expected` is the prediction stated before mining |
| `created`, `skipped`, `edited` | Counts from reconcile and write-back |
| `tags_proposed`, `tags_accepted` | Counts from the tagging sweep |
| `findings_new`, `findings_carried` | Counts |
| `checks_clean` | Slugs of checks that ran and found nothing |
| `could_not` | What could not be done, one line each. `[]` when nothing, never omitted |

The four things every run must end with (`SKILL.md`, "What good looks like") map to
`sources.unmatched_meetings`, `skipped`, the `findings` collection and `could_not`. The
board marks a run that left any of them out as *not recorded*, so a tidy-looking entry
with no coverage list reads as incomplete rather than clean.

### `changesets/<run-id>`

An approved write batch and its receipts, for sandbox/live only. See
`reference/run-recovery.md`. Fields: `mode`, `window_start`, `window_end`, `actions`.
Each action holds `id`, `target`, `action`, `before`, `proposed`, `refs`,
`approval` (operator decision and scope), `status`, and optional `receipt`
(issue/event id and observed result), `error` (redacted failure explanation).
Unknown outcomes block automatic retry and completion. Dry-run emits a proposed
changeset without saving it. One operator/session writes a store at a time.

### `hires/<slug>`

The latest scan of one person's board (`reference/hire-scan.md`). One tab on the board
per document. `<slug>` is the person's first name from the people map, lower case,
hyphenated if it would collide (`vandit`, `jonathan-v`). A copy of each scan goes to
`hires/<slug>/scans/<YYYY-MM-DD>`.

| Field | Notes |
|---|---|
| `name` | Display name, from the people map. The board orders tabs by it |
| `board` | Their project key. The board reads it live from Jira and refuses anything that is not a plain key |
| `scanned_at` | ISO timestamp. The tab flags a scan older than seven days |
| `mode` | The run mode at the time |
| `summary` | One or two sentences, about the work |
| `counts` | `{open, blocked, needs_review, overdue, done_since_last}` |
| `needs_me` | `[{key, title, url, why}]` — what the operator owes them. The tab leads with it |
| `blocked` | `[{key, title, url, on_whom, since}]` |
| `needs_review` | `[{key, title, url, why}]` — items they flagged `needs-review` |
| `overdue` | `[{key, title, url, due}]` |
| `moved` | `[{key, title, url, change}]` — since the previous scan |
| `agenda` | Strings, for the next one-to-one |
| `could_not` | Strings. `[]` when nothing, never omitted |

Readable by anyone the board is shared with. Facts about work only; no assessment of
the person.

The board also keeps unsent comment drafts at `ursula/drafts`. Claude does not read or
write it.

## Rules

Shared rows are readable by anyone who can open the artifact. **Never store
credentials, tokens or vault item names.** Cloud ids and project keys are fine.

`config/run.prohibitions` holds the hard limits — Ursula sends no email and no Slack
message to anyone but the operator; everything else goes through the outbox. Calendar
writes are permitted under the approval tiers in SKILL.md; `config/run.calendar` can
lower that further per operator (for example, tier 1 only) but never raise it.

Last-writer-wins, no transactions. Fine at a few check-ins a day and two sessions a
week; do not build anything that assumes atomicity. Pin a write to the version read
(`if_version`) where the tool offers it, so a check-in and the board do not overwrite
each other.

Config is per-operator. Two operators watching the same boards have two separate
configs and two separate databases. Jira is the only shared state.
