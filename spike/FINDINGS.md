# Always-on spike — findings

Branch `spike/always-on`, 2026-09-30. Goal: prove the pieces a Muse-like, always-on
Ursula needs, using only a Claude subscription (no API key) and claude.ai connectors.
Bench page: https://claude.ai/artifact/Dhtt3nhWi5CZLan7Swzw7a (collections `spike`,
`outbox`, `config/self`). Routine: `ursula-spike` (one-off, Sonnet 5.5, Default env).

## Results

| Check | Result | Evidence |
|---|---|---|
| Routine writes the board's database | **pass** | `ArtifactData` works in a cloud routine; `spike/db-write` written 17:23Z |
| Routine sends a Slack DM | **pass** | self-DM ts `1790788995.381139`; posts as the owner, tagged "Sent using Claude" |
| Routine reads a reply in that DM | pending | read works; waiting on an `ursula:` reply |
| Routine proposes, board approves and sends email | **pass** | `outbox/routine-20260930T172330`: proposed by routine, approved on the board, sent through `gws_gmail_send`, receipt gmail id `1a0f35c7d34a10a0` |
| Routine calls LiteLLM without seeing the key | deferred | see below |
| Secret guard hook runs in the cloud | **pass** | `.claude/settings.json` PreToolUse hook denied a command naming the key variable |

## What we learned

1. **Approvals are a queue, not a pause.** Routines run unattended; they cannot wait.
   The routine writes a `proposed` outbox row; the board's Approve button executes the
   action with the viewer's own connector and writes the receipt. Nothing waits for the
   next run. The outbox row is the audit record: proposal, why, approver, time, receipt.
2. **The model does not know the time.** The routine invented timestamps (one at
   midnight, one later than the server's own write). Every time Ursula records must come
   from `date -u`, or be taken from the store's `updatedAt`.
3. **Slack posts as the owner.** A DM from the routine is a message to yourself. It is
   a good record; it is probably not a notification (confirm: did the phone buzz?).
   Candidate nudge channels: a calendar event with a reminder, or a Slack app/bot later.
4. **LiteLLM key handling.** The right mechanism is a cloud environment **API
   credential** (the proxy attaches the header after the request leaves the sandbox; the
   agent never sees the key). It is Pro/Max only, and this account's environment editor
   shows no API credentials section: the account is on an organization plan. Environment
   variables are readable by the agent, and the dialog says not to put secrets there.
   Decision: v1 does not use LiteLLM in the cloud. `bin/litellm` already uses the
   credential when present (no key in the session), else the macOS Keychain locally.
   A "config file with the key" has the same exposure as an environment variable: any
   file the agent can read, it can print. Revisit when API credentials reach the plan.
5. **Default environment is not editable.** Users need their own environment (e.g.
   `Ursula`) to change anything; credentials appear only when editing an existing one.

## Pieces on this branch

- `bin/litellm` — the only code that touches the LiteLLM key; `check | models | chat`.
- `bin/guard-secrets` + `.claude/settings.json` — PreToolUse guard. A guard rail, not a
  security boundary.
- `spike/bench.html` — the bench page: check results and an approve-to-send outbox that
  only mails the owner's own address (`config/self`).
- `spike/guard-probe.json` — synthetic input for testing the guard without naming the
  variable on the command line.
