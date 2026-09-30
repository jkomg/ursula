# The outbox

Every action that reaches another person, or that the operator has not yet agreed to,
goes through the outbox. Ursula **proposes**; the operator **approves on the board**;
the board **does it** with the operator's own connector and keeps the receipt. The
outbox is also the audit trail: what was proposed and why, who approved it, when, what
was actually sent, and what the service answered.

This is how Ursula can send on the operator's behalf without ever sending on its own.
A cloud check-in cannot stop and wait for an answer, so approvals are a queue rather
than a pause: the check-in writes the proposal and moves on, and the approval executes
the moment the operator clicks it. Nothing waits for the next run.

## What goes through it

| Kind | What the board does on approval | Tier |
|---|---|---|
| `email` | Sends through Gmail (`gws_gmail_send`) | 3 — per item, recipients shown |
| `slack` | Posts a Slack message as the operator (`slack_send_message`) | 3 — per item, channel or person shown |
| `jira_comment` | Adds a comment to an issue (`addCommentToJiraIssue`) | 2 when on an owned board; 3 elsewhere |
| `calendar_block` | Creates a focus block on the operator's own calendar, no attendees (`gws_calendar_events_insert`) | 1 — may be batched |

The tiers are the calendar tiers in `SKILL.md`, extended to messages. Anything a person
other than the operator will read is tier 3: one approval per item, with the recipients
stated on the card before the button. There is no batch approval for tier 3.

Everything else Ursula writes — findings, the run log, staging proposals, its own Slack
DM to the operator, an email notice to the operator's own address — does not need the
outbox, because nobody else reads it (`reference/always-on.md`, "Heads-up").

## The record — `outbox/<id>`

One document per proposed action. Id: `<source>-<UTC time as YYYYMMDDTHHMMSS>-<n>`, for
example `checkin-20261001T120312-2`. Times come from the clock (`date -u`), never from
the model's sense of the date.

| Field | Written by | Notes |
|---|---|---|
| `kind` | session | `email` · `slack` · `jira_comment` · `calendar_block` |
| `mode` | session | The run mode when proposed. The board sends nothing for a `dry-run` item |
| `status` | both | `proposed` → `approved` → `sent` · or `rejected` · `failed` · `unknown` (no reply in time: it may have gone) · `reviewed` (a dry-run item the operator marked) |
| `to` | session | Email: comma-separated addresses. Slack: a channel or user id plus `to_label`, a readable name |
| `subject` | session | Email only |
| `body` | session | The exact text to send. Plain text |
| `target` | session | `jira_comment`: the issue key. `calendar_block`: `{start, end, title}` as ISO datetimes with offset |
| `why` | session | One line, readable cold: what prompted it |
| `refs` | session | `[{label, url}]` back to the sentence, ticket or meeting that produced it |
| `proposed_by`, `proposed_at` | session | `checkin`, `plan`, `retro`, `adhoc` |
| `expires_at` | session | Optional. After it, the board shows the item as stale and will not send it |
| `approved_by`, `approved_at` | board | The viewer's opaque id and the time of the click |
| `edited` | board | `true` when the operator changed the text before approving; `original_body` keeps what Ursula proposed |
| `sent_at`, `receipt` | board | The service's answer: Gmail message and thread id, Slack channel and ts, Jira comment id, calendar event id and link |
| `error` | board | Code and one line, when sending failed or the outcome is unknown |
| `rejected_by`, `rejected_at`, `reject_note` | board | A rejection may carry a reason; the next session reads it |
| `verdict`, `reviewed_at` | board | Dry-run only: `right` or `wrong`. A `wrong` is a proposal defect worth logging in `test/golden-week.md` |

## Rules

- **Propose the exact words.** The body is what will be sent, not a summary of it. An
  operator approving a paraphrase has approved nothing.
- **One recipient set per item.** If the same note goes to three people separately,
  that is three items.
- **Never re-propose a rejected item** unless its evidence changed. A `reject_note` is
  the operator telling you why; treat it like a dismissed finding's `close_note`.
- **Never edit a `sent`, `failed` or `rejected` record.** They are the audit. A
  correction is a new item.
- **An unknown outcome is not a failure.** If the board recorded status `unknown` (no
  reply in time), the message may have gone. The next session checks
  Gmail Sent, the Slack channel or the issue before proposing anything similar.
- **Dry-run proposals are real proposals that cannot send.** The board shows them, and
  the operator can mark each one right or wrong; that is how two dry-run cadences teach
  Ursula what the operator would actually send.
- **Outbox rows are shared data.** Anyone the board is shared with can read them. Do not
  put anything in a proposal the operator would not want a board viewer to see.
- **The board refuses to send** an item whose `mode` is `dry-run`, whose `mode` differs
  from the current `config/run.mode`, or whose `expires_at` has passed.

Not built yet: earned autonomy — offering, after several unedited approvals of the same
tier-1 kind, to stop asking. Tier 3 is never offered.
