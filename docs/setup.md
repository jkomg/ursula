# Setup

Ursula is configured by conversation, not by editing files. Clone the repo, install
the skill, then talk to Claude. Claude asks the questions below, writes the answers
into your artifact database, and publishes your board.

Expect fifteen minutes.

## 1. Install

```bash
git clone <repo-url> ~/ursula
```

Claude Code: point it at the folder, or copy `SKILL.md` and its `reference/`
directory into your skills location.

Claude.ai: attach the skill through the Skills menu.

## 2. Turn on connectors

All four are required. If any is missing you will get a partial run that looks like
a complete one.

| Connector | Used for |
|---|---|
| Atlassian | Reading and writing Jira |
| Google Drive | Meeting-notes documents, shared material |
| Gmail | Notes index, direct commitments |
| Google Calendar | Cadence window, collisions, changed expectations |

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

### Board

An existing artifact URL to adopt, or permission to publish a new one.

## 3b. Completion contract

The interview is a conversation, not a script — but it is **done** only when every item
below is true. Claude must not report setup as complete otherwise.

### Required state

Nine documents, every field populated or explicitly recorded as unknown with a reason:

`config/jira` · `config/labels` · `config/cadence` · `config/numbers` ·
`config/people` · `config/policies` · `config/run` · `state/watermark` ·
`state/ingested`

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
- **Findings** — at least two or three from the nine checks, with evidence and a
  recommendation each. **Zero findings means the analysis pass did not run.** That is
  the single clearest sign of a lazy run, because the checks are the point.
- **Tag proposals** — ranked, with a recommendation on each, and the operator rejecting
  a good number of them.
- **What it could not do** — stated explicitly. Every run ends with this, even when the
  answer is nothing.

A run that produces tidy tickets, no coverage list and no findings has done the easy
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
