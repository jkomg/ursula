# Config schema

**This assumes claude.ai.** Config and state live in the operator's artifact database,
which Claude Code cannot reach. Running the skill from Claude Code would need a
file-based config and would have no board; that path is not built.

Config lives in the operator's artifact database, collection `config`. The YAML in
this directory is a reference and an export format — it is not the input path.
Setup is a conversation.

## Documents

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

## State

Operational, not configuration. Same database, `state` collection.

| Document | Holds |
|---|---|
| `state/watermark` | Timestamp of last successful mine. Only updated on success. |
| `state/ingested` | Source document id to created issue keys. Prevents re-ingestion. |
| `state/tagging` | Proposals and whether the operator accepted them. |

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
| `closed_at`, `closed_by`, `close_note` | Set when closed. `closed_by` is `session` or `board` |

**The operator can close findings from the board.** `Resolved` and `Not a finding` set
`status`, `closed_by: "board"` and a `close_note`; a dismissal requires a reason. The
next session reads these before Pass 3: a dismissed finding is not raised again unless
its evidence has changed, and its `close_note` is the operator saying why the check
fired wrongly — log it in `test/golden-week.md` if it is a check defect. The board never
touches Jira for a finding; any ticket change is the session's, in the next Pass 5.

### `runs/<date>-<session>`

One document per session, id like `2026-09-28-plan`, `2026-10-01-retro`, `-adhoc` for
anything between. The board shows the latest 52.

| Field | Notes |
|---|---|
| `date` | ISO date. The board orders on it |
| `session` | `plan` · `retro` · `adhoc` |
| `mode` | `dry-run` · `sandbox` · `live` |
| `status` | `complete` · `partial` · `failed`. Only `complete` advances the watermark |
| `summary` | One or two sentences |
| `watermark_before`, `watermark_after` | Timestamps |
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

The board also keeps unsent comment drafts at `ursula/drafts`. Claude does not read or
write it.

## Rules

Shared rows are readable by anyone who can open the artifact. **Never store
credentials, tokens or vault item names.** Cloud ids and project keys are fine.

`config/run.prohibitions` holds the hard limits — no email, no Slack writes. Calendar
writes are permitted under the approval tiers in SKILL.md; `config/run.calendar` can
lower that further per operator (for example, tier 1 only) but never raise it.

Last-writer-wins, no transactions. Fine at twice a week; do not build anything that
assumes atomicity.

Config is per-operator. Two operators watching the same boards have two separate
configs and two separate databases. Jira is the only shared state.
