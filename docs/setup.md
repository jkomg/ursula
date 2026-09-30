# Setup

For ChatGPT/Codex, first read `docs/chatgpt.md` and `reference/runtime.md`.
They replace the Claude installation, persistence and board publication steps below;
the interview and real connector checks remain shared.

Ursula is configured by conversation, not by editing files. Clone the repo, install
the skill, then talk to Claude. Claude asks the questions below, writes the answers
into your artifact database, and publishes your board.

Expect fifteen minutes.

## 1. Install

Add the skill through the Skills menu in claude.ai and run the Monday and Thursday
sessions there: that is where you and your connectors are. Check-ins between sessions
run as a cloud routine with the same connectors, and read and write the same board
database (`docs/routine.md`). The repo is where the skill is edited.

## 2. Turn on connectors

All four are required. If any is missing you will get a partial run that looks like
a complete one.

| Connector | Used for |
|---|---|
| Atlassian | Reading and writing Jira; reading Confluence for the `content-cleanup` pack |
| Custom Google Drive | The Mirantis-built gateway: Gmail, Calendar, Docs, Sheets |
| Google Drive | Google's own. Finding and reading meeting-notes documents |
| Slack | Read-only. Commitments that never reach a meeting |

There is no separate Gmail or Calendar connector; both come through the gateway. An
earlier version of this table listed them separately, which sent an operator looking
for connectors that do not exist.

On a Team or Enterprise plan an owner must enable a connector for the organisation
before you can authenticate it. If you see a **request** button where a toggle
should be, that is the org gate and you need an owner, not a retry.

## 3. The interview

Claude asks these. Have the answers ready.

### Jira

- **Cloud id.** From any Jira API URL, or ask Claude to look it up.
- **Owned projects** — keys for projects where you hold your own work. Full read
  and write.
- **Watched projects** — keys you monitor but do not own, typically your reports'
  boards. Read only.
- **Shared manager board** — one key, where findings about watched boards land.
  Must be a board every relevant manager can see.
- **Excluded projects** — templates and probes. Never scanned for work, still
  searched for template propagation.
- **Transition ids** — the numbers for To Do, In Progress, Blocked and Done. Claude
  can read these off an existing ticket if you do not know them.

### Labels

- **Priority label** — the tag marking work that matters this cadence. Default
  `ursula`.
- **Week tag format** — default `w<ISO week>`, e.g. `w39`.
- **Review label** — what your reports use to flag broken or unclear items.
  Default `needs-review`.

The board query is assignee-scoped, so these labels do not collide between
operators. Two people can use the same tag and never see each other's work.

### Cadence

- **Planning session** — day and time. Default Monday.
- **Retro session** — day and time. Default Thursday, sitting before the one-pager
  deadline rather than on it.
- **One-pager recipient** and when they need it.
- **Required sections.** Ask them; do not assume. The default shape is what moved,
  what is blocked and on whom, decisions needed with recommendations, risks at
  thirty days, and agreed numbers.
- **Agreed numbers** — the specific figures your manager asks for every week. These
  drive standing queries, and getting them wrong is expensive.

### People

Names, roles and email addresses for anyone who appears in your meetings, blocks
your work, or owns something you depend on. Used to resolve owners, build standing
Drive queries for material they share, and correct transcription errors — meeting
notes mangle names constantly.

### Policies

Your written operating rules, the ones a proposal might quietly contradict. Ticket
references where they exist. This drives the policy-conflict check, and it is the
part most people skip and later wish they hadn't.

### Packs

Which domain packs match the operator's work (`reference/analysis-checks.md`). Ask what
the work is, then propose packs; do not enable one by default.

- **`service-delivery`** — onboarding people onto boards cloned from templates,
  arranging their access. No extra questions.
- **`content-cleanup`** — a Confluence cleanup backlog. Ask every field in
  `reference/packs/content-cleanup.md` → Config: the spaces, the staleness threshold,
  exempt labels, what "owned" means, bulk-edit accounts, the backlog project, and how
  findings batch into tickets. None of these has a default. The backlog project must
  also be declared as owned.

An operator can enable none, one or both. With none, say so in the config read-back:
the run is the core checks only.

### Board

An existing artifact URL to adopt, or permission to publish a new one.

### Heads-up

How much the operator wants to hear between sessions: `quiet` (only what needs them),
`daily` (a morning and an end-of-day note) or `chatty` (everything, with reasons). Ask
in those words, not as config. Record it in `config/voice` with their own email address
and the channel id of their Slack DM with themselves. Tell them they can change it any
time from the board. Then offer to turn on check-ins (`docs/routine.md`); say plainly
that each check-in uses some of their Claude allowance.

## 3b. Completion contract

The interview is a conversation, not a script — but it is **done** only when every item
below is true. Claude must not report setup as complete otherwise.

### Required state

Eleven documents, every field populated or explicitly recorded as unknown with a reason:

`config/jira` · `config/labels` · `config/cadence` · `config/numbers` ·
`config/people` · `config/policies` · `config/packs` · `config/run` · `config/voice` ·
`state/watermark` · `state/ingested`

`config/checkins` is written only when check-ins are turned on; its absence means they
are off, which is a valid setup.

A field left out silently is a failure. A field recorded as `null` with a note saying
why is acceptable and gets reported.

### Verification — by execution, never by assertion

Claude must **run each of these and report the actual result**. "Configured correctly"
is not an acceptable answer; the output of the check is.

| # | Check | Passes when |
|---|---|---|
| 1 | Query every declared project key | Each resolves to a real project. A typo'd key returns nothing and must be caught here, not in week three |
| 2 | Read transition ids off a real ticket in an owned project | Ids are observed, not assumed from another operator's config |
| 3 | Run the board JQL | Returns a count. Zero is a finding to report, not a failure — it usually means nothing is labelled yet |
| 4 | Run one Drive notes query over the last 14 days | Returns documents, paginated to exhaustion |
| 5 | Run one Gmail query and one Slack DM query | Both return without an auth error |
| 6 | Read the cadence window from the calendar | The planning and retro sessions exist, or Claude offers to create them under tier 1 |
| 7 | Run the coverage check once | Names any meetings in the last week with no notes source |
| 8 | Publish the board | Returns a URL the operator can open |
| 9 | Read the whole config back to the operator | They confirm it aloud |

With `content-cleanup` enabled, also:

| # | Check | Passes when |
|---|---|---|
| C1 | Resolve every space key with `getConfluenceSpaces` | Each returns a space; its numeric id is stored in `space_ids` |
| C2 | List one space's pages to exhaustion | Reports the page count and the number of calls it took. A count of exactly 25, 100 or 250 on one call means the cursor was not followed |
| C3 | Read one page and show the operator the raw fields returned | Records which of owner, creator, last modifier, parent and labels the connector actually carries — the pack depends on this and the file marks it *observe at setup* |
| C4 | Run the staleness CQL once with `stale_days` | Returns a count per space. Show the operator the ten oldest so they can judge the threshold |
| C5 | Pull the backlog project's open set and match it to pages by id | Reports how many tickets carry a page link and how many name a page by title only |

Write what C3 observed back into `reference/packs/content-cleanup.md` on the next edit
of the repo, and log it in `test/golden-week.md`. Until then, the owner and orphan
checks run on a guessed shape, and the report must say so.

### Refusal

If any check fails, Claude writes `config/run.status = "incomplete"` with the list of
what failed, tells the operator plainly, and **does not proceed to a first planning
session.** A setup reported as complete with a broken project key produces a month of
quietly wrong runs.

### What a good first run looks like

The first planning session is the real acceptance test. Rough shape, from measured runs:

- **Sources found** — several documents, and a coverage list naming the meetings it
  could not reach. A run reporting full coverage is almost certainly wrong.
- **Skip rate** — roughly half of extracted candidates should already have tickets. A
  run creating everything it finds is not reconciling.
- **Findings** — at least two or three from the core checks and enabled packs, with evidence and a
  recommendation each. **Zero findings is a red flag**, and the run is treated as
  having skipped the analysis unless it shows, per check, that the check ran and
  what evidence it ran against. Never manufacture a finding to reach a count; a
  clean check with its evidence shown is the honest answer.
- **Tag proposals** — ranked, with a recommendation on each, and the operator rejecting
  a good number of them.
- **What it could not do** — stated explicitly. Every run ends with this, even when the
  answer is nothing.

A run that produces tidy tickets, no coverage list and no recorded analysis has done the easy
half and should be called out as such rather than accepted.

## 4. First run

Claude sets an initial watermark — usually two weeks back — publishes the board, and
runs a first planning session.

The first run is noisy. It sees two weeks of accumulated notes at once and proposes
more than a normal week would. Expect to reject a lot of tag proposals; that is the
mechanism learning what you care about.

## 5. Check it took

Ask Claude to read back your config. Confirm:

- Every project key is right, and in the right category
- The board shows work, and sorts the way you expect
- Undated items are at the bottom where they belong — that is correct behaviour,
  not a bug

## Multiple operators

Two managers can run Ursula against overlapping boards. Each has their own skill
install, their own artifact and their own database; nothing is shared between the
two instances directly.

What is shared is Jira, which is already the system of record. Coordination happens
there or not at all.

The rules that keep two instances from colliding:

- Neither writes to an individual's own board
- Findings about watched boards go to the shared manager board with an assignee
- Before creating a finding card, check for an existing one with the same key
  (`<person>-<check>-<week>`)

Agree the shared manager board before the second operator's first run. Two managers
filing into different places is worse than either filing alone.
