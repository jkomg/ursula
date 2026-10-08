# CLAUDE.md

Context for Claude Code working in this repo.

Shared maintenance guidance now lives in `AGENTS.md`. Ursula also supports
ChatGPT/Codex via `reference/runtime.md` and `docs/chatgpt.md`; the live artifact
board remains Claude-specific. `scripts/render_snapshot.py` is executable code
that can be checked locally without simulating connectors. Build both bundles
with `bin/install.sh --target all`; validate with `--check`.

## What this is

Ursula is a **skill**, not an application. There is nothing to compile, serve or run
here. The repo is the definition of a weekly operating procedure that Claude executes
inside claude.ai, plus the reference material it reads while doing it.

If you are looking for an entry point, a build step or a test runner, there isn't one.
That is not a gap.

## Your job here

Maintain and improve the written definition. In practice:

- Edit the markdown in `reference/` and `docs/`
- Keep `SKILL.md` accurate and under about 500 lines, pushing detail into `reference/`
- Log defects and fixes in `test/golden-week.md`
- Build the two real code artefacts when asked: `artifact/index.html` and `bin/install.sh`

## What you cannot do here

**You cannot run or test Ursula from this repo.** It needs four live connectors —
Atlassian, the Mirantis Google gateway, Google Drive, Slack — and a claude.ai artifact
database holding config and state. None of that exists in Claude Code.

So: do not write test harnesses that mock the connectors, do not add a CI workflow that
"validates" the skill, and do not try to execute the cadence. Testing happens in
claude.ai against real data. The loop is edit here → push → re-add the skill in
claude.ai → run a dry-run → bring the findings back.

That loop is slow, so **batch edits**. Do not iterate one line at a time.

## Layout

```
SKILL.md                    the procedure itself — read this first
INSTALL.md                  what a new operator is handed
reference/
  analysis-checks.md        core checks and how packs work; the actual value of the skill
  packs/                    domain packs: service-delivery, content-cleanup
  mining.md                 where commitments are found and how
  jira-conventions.md       API traps, all learned by getting them wrong
  artifact-board.md         the board's structure and capabilities
  hire-scan.md              one person's board, written to its own tab
docs/
  setup.md                  the interview + completion contract
  cadence.md                the weekly rhythm
  sandbox.md                dry-run / sandbox / live, and prohibitions
  troubleshooting.md        connector and query failures
config/
  schema.md                 what config and state hold
  example.yaml              illustrative only — setup is a conversation
test/
  golden-week.md            a hand-processed week + the defect log
artifact/
  index.html                copy of the live board (see below)
bin/
  install.sh                checks the skill, builds the upload zip
```

## Principles that hold across changes

**The analysis pass is the point.** Mining and ticket-writing are plumbing. Every defect
found so far has been in collection, never in judgement. Do not make the checks
generic or optimise them away.

**Nothing is asserted that has not been executed.** The setup contract requires Claude
to run each verification and report the real output. Keep that property in any edit —
"configured correctly" is not an acceptable answer anywhere in these docs.

**Write for someone reading cold.** These documents are read by a Claude instance with
no memory of how they came to be, and by operators who were not in the conversation.
Every rule should carry why it exists, ideally with the failure that produced it.

**Prohibitions are load-bearing.** Never send email, never post or draft in Slack, never
write unsolicited to a watched board. Calendar writes are allowed under the tiered
approval in SKILL.md. Do not loosen these without being asked.

## Two files that are code

**`artifact/index.html`** is a copy of the operator's live board, committed as a
baseline. It runs in claude.ai, declares `db` and `mcp` capabilities, and queries Jira
and Calendar at runtime. If you rewrite it, know that capability declaration is a
full-set operation — publishing a partial set silently revokes the rest and leaves a
page that renders fine and cannot reach Jira.

**`bin/install.sh`** checks the skill and builds the zip uploaded to claude.ai. It
installs nothing locally, on purpose — see `docs/release.md`. Run `bin/install.sh
--check` after a batch of edits; it catches references to files that do not exist.

## Current state

Twelve defects found and fixed across five dry-runs; the log is in
`test/golden-week.md`. Two operators are running it. Checks are split into seven core
checks plus domain packs (`reference/packs/`). Three checks — `deadline-inversion`,
`capability-confusion`, `template-propagation` — have never fired in a test, and all
five `content-cleanup` checks are unproven.

Queued work, in rough priority order:

1. **Test the 2026-09-29 batch in claude.ai.** Written and checked locally against stub
   data only; nothing below has touched real data. One upload covers all of it:
   1. `bin/install.sh`, upload the zip replacing the old Ursula, and in a fresh chat ask
      which version is running. It should name the version the script printed. If the
      upload is rejected, `docs/release.md` → "Assumptions to confirm".
   2. Republish the board from `artifact/index.html` to the existing URL with
      `capabilities` omitted. Confirm This week still reads Jira and the calendar, and
      that a note draft survives a reload (defect 13).
   3. Dry-run a planning session. Confirm it writes `runs/` and `findings/` in the
      `config/schema.md` shapes and that the Findings and Log tabs fill. Dismiss one
      finding from the board and check the next session honours it.
   4. "Scan Vandit's board." Confirm a Vandit tab appears, the live list reads RPTB-style
      keys, and the *moved* query works on a watched project.
   5. Daniel's setup with `content-cleanup`: setup checks C1–C5 in `docs/setup.md`, and
      write the observed Confluence fields back into `reference/packs/content-cleanup.md`.
   Log each result in `test/golden-week.md`, defects numbered from 14.
2. **Loader skill that reads the repo live** — blocked on the Mirantis gateway: its
   `github_oauth_start` sends the Google client id to GitHub, so GitHub sign-in 404s
   (reported from claude.ai, reproducible since 22 Sep). Once fixed, a stub skill can
   read `SKILL.md` and `reference/` from `jkomg/ursula` at a branch or tag, removing the
   re-upload from the edit loop. Until then the zip is the only install path.
3. **Watched boards tab** across every report at once — described in
   `reference/artifact-board.md`, not built. Hire tabs cover one person at a time.

## Conventions

- British-ish plain prose, no marketing tone, no emoji in the docs
- Tables for anything enumerable; short paragraphs otherwise
- Every rule states its consequence
- Defects get logged with the symptom, the fix, and the observation that produced it
- Commit messages describe the decision, not the file list
