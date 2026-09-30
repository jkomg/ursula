# Turning on check-ins

Check-ins are what make Ursula work between the Monday and Thursday sessions
(`reference/always-on.md`). They run as a **routine**: a scheduled Claude session in
Anthropic's cloud that uses your own connectors. Routines work on Pro, Max, Team and
Enterprise plans, count against your normal Claude usage, and can run at most once an
hour.

Do this after setup is complete and the board exists. Claude can do most of it for you
from Claude Code (`/schedule`), or you can click through it at claude.ai/code/routines.

## What you choose

| Choice | Default | Why |
|---|---|---|
| When | 8am, noon and 4pm on weekdays, your time | Morning catches overnight mail, noon catches the morning's meetings, 4pm leaves time to act. Each run uses some of your Claude allowance |
| Model | Sonnet | A check-in is reading and sorting. The Monday and Thursday sessions are where the heavier thinking happens |
| Repository | Your copy of the Ursula repo | The routine reads the skill from it |
| Connectors | Atlassian, Custom Google Drive, Google Drive, Slack | The same four as setup. Remove any you did not set up |

## What you do once

1. Open claude.ai/code/routines and choose **New routine**, or ask Claude in Claude Code
   to create it. Paste the prompt below, with your board's link where it says BOARD.
2. Set the schedule and pick the connectors from the table.
3. Choose **Run now** once. Within a few minutes the board's Log tab shows a
   `checkin` entry. If it says a connector failed, fix that connector in claude.ai and
   run it again.
4. On the board, open the Outbox tab and set how chatty Ursula should be.

To pause check-ins, turn the routine off at claude.ai/code/routines. To delete it, do it
there too.

## The prompt

```text
You are Ursula's check-in. Read SKILL.md, then reference/always-on.md, and run one
check-in exactly as always-on.md describes. BOARD = <your board's claude.ai link>. The
board's database is the state store; use the ArtifactData tool for it. Read the clock
with `date -u` before writing any time. Never send email or Slack messages to anyone
but me; anything for someone else goes to the outbox for my approval. Finish with the
run entry and one line saying what you did.
```

## LiteLLM (later)

Ursula can hand bulk reading to a cheaper model through the company's LiteLLM gateway,
through `bin/litellm`. It only does so when the key can be kept away from Claude: a
cloud environment **API credential**, which the proxy attaches outside the session.
That option appears when you edit your own cloud environment on Pro and Max plans; on
Team and Enterprise plans it is not available yet. Until it is, check-ins run without
LiteLLM. Never paste the key into a chat, a prompt or the environment-variables box.
