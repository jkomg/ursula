# Config schema

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

## State

Operational, not configuration. Same database, `state` collection.

| Document | Holds |
|---|---|
| `state/watermark` | Timestamp of last successful mine. Only updated on success. |
| `state/ingested` | Source document id to created issue keys. Prevents re-ingestion. |
| `state/runs` | One entry per session: what was mined, created, tagged, found. |
| `state/tagging` | Proposals and whether the operator accepted them. |
| `state/findings` | Open findings by key, so the next run can tell new from carried. |

## Rules

Shared rows are readable by anyone who can open the artifact. **Never store
credentials, tokens or vault item names.** Cloud ids and project keys are fine.

Last-writer-wins, no transactions. Fine at twice a week; do not build anything that
assumes atomicity.

Config is per-operator. Two operators watching the same boards have two separate
configs and two separate databases. Jira is the only shared state.
