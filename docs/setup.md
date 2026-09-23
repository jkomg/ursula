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
