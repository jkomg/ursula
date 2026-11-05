# Golden week — 2026 w39

A week processed by hand before the skill existed. The sources are real, the
outcomes are known, and the skill should reproduce them.

## How to run it

1. `config/run.mode` = `dry-run`, `config/packs.enabled` = `[service-delivery]`
2. `state/watermark` = `2026-09-21T00:00:00Z`
3. Empty `state/ingested` into a scratch copy — the real map would correctly skip
   everything and prove nothing
4. Run a planning session
5. Diff the changeset against the expected outcomes below

## Sources

| Source | Arrived |
|---|---|
| ACCESS.md — operator onboarding | Slack, 21 Sep |
| Randy call notes | 21 Sep |
| AMER Mgmt and SDM sync | 21 Sep |
| Jonathan Vinson onboarding session | 22 Sep |
| MirCloud Operational Management (Drive, revised 18 Sep) | shared 16 Sep, revised after |
| Vandit 1:1 notes | 22 Sep — **deliberately unprocessed** |

## Expected creates

`TSDMON-130` Claude Max upgrade IT ticket · `TSDMON-131` service account question ·
`TSDMON-132` LMCO review with Shane · `TSDMON-133` team break-glass keys to Randy ·
`TSDMON-134` Global AI repo read access · `TSDMON-135` Jonathan to MirCloud Ops Slack

## Expected edits

`NOM-1` retitled and closed · `NOM-2` Rassul dropped · `NOM-3` moved to 23 Sep ·
`NOM-6`, `NOM-7`, `NOM-8` labelled · `NOM-8` retitled and dated · `CCC-6` labelled
and dated

## Expected skips

Expense process (already TSDMON-124) · Jira audit (113) · training alignment (123) ·
public keys (covered by 117 and NOM-7) · Tuesday standup with Jonathan (the 1:1
already exists on the calendar)

Skips matter as much as creates. A run that recreates these has no reconciliation.

## Expected findings

1. Board not consolidating — only TSDMON carried labels; NCCS returned nothing owned
2. Deadline inversion — NOM-3 due after the note consuming it
3. Capability confusion — Warden access does not close NOM-7
4. Policy conflict — shared service account against NCCS-99
5. Scope drift — "walk the Swamp workflows" is 300-plus, human-first, unowned
6. Template propagation — exam link fix leaves NCNET and NCSYS broken
7. Stale parent — phase epic ten weeks overdue with live children
8. Calendar collisions — three
9. Inherited risk — Bluefield 3 and NICo adopted together, lands around January

## Grading

**Creates and edits** — exact match expected. A miss is a mining or reconciliation
failure.

**Skips** — exact match expected. A false create is the more expensive error; it
erodes trust in the whole run.

**Findings** — partial credit. Six of nine is a pass for a first run. The fixture needs
the `service-delivery` pack: without it, findings 3 and 6 cannot fire and the run fails
by construction. Findings 2, 3
and 6 are the ones that justify the skill; missing any of those three is a fail
regardless of the rest.

**False findings** — worse than missed ones. A check that fires on nothing teaches
the operator to skim.

## Known-hard cases

- One notes document is untitled ("Meeting started 2026/09/21 13:25 EDT") and must
  be matched to the calendar by timestamp
- Transcription mangled several names; the people map should catch them
- One person named in an existing ticket had withdrawn before starting, so the
  ticket needed correcting rather than actioning
- "Book the NCA-AIIO certification exam" exists five times: three live boards and
  two templates

---

# Run log

## 2026-09-23 — first dry-run, partial (single source)

Watermark `2026-09-22T00:00:00Z`. **Predicted one new document. Got five.** The
prediction failure was the most useful output; four of the extras were defects.

| # | Defect | Fix |
|---|---|---|
| 1 | `modifiedTime` resurfaced a 9 Sep meeting whose doc was touched on the 22nd | switch to `createdTime`, cross-check the date in the title |
| 2 | One result was `application/vnd.google-apps.shortcut` — `read_file_content` cannot open it | check `mimeType`, resolve or skip loudly |
| 3 | Skill forbade editing a watched board, but the operator had promised that edit in a 1:1 | rule is no *unsolicited* writes; a direct instruction overrides |
| 4 | `text ~` reconcile returned a capped page of mostly unrelated cards | pull the board's open set once and match in memory |
| 5 | Name mangling far worse than documented — 8 entities in one 30-minute call | resolve every name against the people map; add an alias list |

Checks exercised: self-blocking (fired — three Blocked cards waiting on the operator),
stale parents (fired — four overdue), scope drift (fired — course-lab gap), calendar
(not run). Deadline inversion, capability confusion and template propagation were not
exercised: a single 1:1 does not contain them. **Run the full golden week before
handing the skill to a second operator.**

## 2026-09-23 — second dry-run, after fixes 1–5

Predicted four documents. Got five again, for a new reason. Fix 1 worked — the
9 September false positive was gone. Two further defects surfaced:

| # | Defect | Fix |
|---|---|---|
| 6 | First run returned 5 results **plus a `nextPageToken` that was never followed**. The most substantive document of the week was in the unread remainder. | Always page to exhaustion. |
| 7 | A shortcut and its target document both matched, same title, same meeting. | Dedupe on title + parsed meeting time; prefer the real document, and the owner's copy over a shared copy. |

Defect 6 is the serious one: the first run reported a clean result while silently
missing a source. Any mining pass that does not exhaust pagination is unsafe.

## 2026-09-23 — third dry-run, full golden week

Pagination and dedupe confirmed working: seven results, no continuation token, six
unique after collapsing the shortcut onto its target.

**Then the run failed the fixture.** Expected six creates; the sources for five of them
were not found.

| # | Defect | Fix |
|---|---|---|
| 8 | Two meetings that generated five of the week's six tickets produced **no reachable Gemini notes** — no document, no email. Automated mining found 1 source in 6. | Coverage check: match accepted calendar events against found sources, report the gaps by name, ask the operator. |
| 9 | Gmail is a **subset** of Drive for notes, not a cross-check. Four results, all already in the Drive set; it missed a session the operator attended without a personal invite. | Reorder to calendar → Drive → Gmail. One Gmail query, not a strategy. |

Defect 8 is the finding that matters most across all three runs. Everything before it
was plumbing. This one says the automated pass cannot be the primary source, and that
the operator's own fifteen minutes is load-bearing rather than polite.

## 2026-09-23 — Slack source evaluation

Two days of direct messages surfaced three commitments with no ticket behind any of
them, none of which any notes document contained. Slack is added as a first-class
source, read-only.

| Finding | Fix |
|---|---|
| 13 of 20 DM results were notification DMs from Jira, Google Calendar and Google Drive. `include_bots: false` does not exclude them — they are app *conversations*. | Maintain an app-DM exclusion list in config and filter by counterpart name. |

## 2026-09-23 — completion-contract dry run

Ran the nine setup verification checks against a live config.

**Passed:** all twelve project keys resolve (JQL fails atomically on a bad key, so one
query tests them all) · transition ids confirmed 11/21/31/41 and `isGlobal`, which is
why they are uniform · board JQL returns 33 · Drive, Gmail, Slack and calendar all
respond. Board publish was not executed against a live artifact.

**Two defects, one of them the most significant so far.**

| # | Defect | Fix |
|---|---|---|
| 10 | **Notes documents are calendar-event attachments.** A Drive title search missed four: a one-to-one reported as having no notes when it did, two meetings that produced two documents each, and the week's most important meeting, whose notes were titled `Notes - <meeting>` rather than `<meeting> - Notes by Gemini`. | Calendar attachments are the primary index. Drive search becomes the backstop for unattached documents. |
| 11 | `jira-conventions.md` claimed `getTransitionsForJiraIssue` excludes the current status. It does not — an issue in To Do lists To Do among its transitions. | Correct the note. |

Defect 10 supersedes much of defect 8's framing. Coverage is better than measured —
the sweep was looking in the wrong place first, not failing to reach the documents.
Genuinely unreachable meetings remain: recurring syncs and ad-hoc calls with no
attachment and no document anywhere.

## 2026-09-29 — checks split into core and packs (no run)

Not a run: a structural change, logged so the next run knows what moved.

`analysis-checks.md` now holds seven core checks. Capability confusion and template
propagation moved to `reference/packs/service-delivery.md`. A new
`reference/packs/content-cleanup.md` adds five Confluence checks — `stale-page`,
`orphan-page`, `duplicate-title`, `unowned-page`, `backlog-drift` — for an operator
whose only project is a Confluence cleanup backlog.

Check slugs replace the 1–9 numbering, because the slug is what goes into a finding key.

All five content-cleanup checks are unproven, and the pack marks three connector facts
*observe at setup*: which owner fields a page read returns, whether anything exposes
inbound links, and whether page history is reachable. The first setup with the pack on
must record what it saw here.

## 2026-09-29 — board: findings and log tabs (no run)

The board gained Findings and Log tabs, reading new `findings/<key>` and
`runs/<date>-<session>` collections (`config/schema.md`). Rendering was checked locally
against stub data only; the tabs have not been opened against a real database.

| # | Defect | Fix |
|---|---|---|
| 13 | The board read saved note drafts as `snapshot.data.drafts`. `data` is a function in the db contract, so drafts were written on every keystroke and never read back — a reload lost them. | Call `data()` and check `exists`. Found reading the runtime type definitions, not in a run; confirm drafts survive a reload on first use. |

## 2026-09-29 — hire scan and hire tabs (no run)

New: "scan <person>'s board" writes `hires/<slug>` and the board shows one tab per hire
(`reference/hire-scan.md`). Checked locally against stub data only: tabs appear per
document, a remembered hire tab survives reload, the live Jira read runs once per page
load, and a board key that is not a plain project key is refused before it reaches JQL.

Not yet exercised: a real scan writing the document, and the tab against a real board.
The first real scan should confirm `resolved >= <date>` works as the *moved* query on a
watched project, and that the notes-document search finds one-to-one notes for the
person being scanned.

## 2026-09-30 — ChatGPT/Codex adapter and shared recovery (no live run)

One shared skill now selects a host adapter (`reference/runtime.md`). Claude keeps
its native database/live board; ChatGPT/Codex uses private JSON state or an explicit
export, with a dated snapshot. `docs/chatgpt.md` provides installation and setup.
`bin/install.sh --target all` builds host-labelled bundles; the default remains Claude.

Shared improvements: freeze mining window bounds, retain approved action receipts,
re-read fields before edits, and reconcile unknown create outcomes before retrying
(`reference/run-recovery.md`). Corrected contradictory dry-run guidance: staging
comments and hire records are proposals only. Sandbox calendar changes stay proposals
and sandbox progress cannot advance live ingestion state. Zero findings is valid
with executed checks and complete evidence; never invent findings to satisfy a count.

Actual local validation: five portable-renderer tests passed (required review output,
incomplete records, escaping/unsafe links, invalid inputs, preserving an existing
board after a failed render). Packaging checks passed for both hosts, newly created
output directories with spaces, correct HOST metadata, included helpers, omitted
bytecode caches, duplicate-build refusal and invalid targets. Skill frontmatter,
references and shell syntax passed. These checks exercise real executable code,
not connectors or cadence judgement. A fictional preview is in ignored `dist/preview/`.
Browser visual inspection was unavailable because the browser tool blocks local
file URLs; no visual verification is claimed.

Still unproven: OpenAI skill installation in an operator's host, the configured
connector translations, persistent state round-trips in that host, and recovery
after a real partially applied batch. Acceptance requires a fresh setup and dry-run
on each host. No live Jira, Calendar or database writes were made for this change.

## 2026-09-30 — operator guide for a mixed audience (documentation only)

Rewrote `docs/chatgpt.md` for managers and other non-technical staff, including
Windows and Mac users. Explained dry-run, saved handover files and dated boards
without database terminology. Moved command-line installation and rendering details
to the maintainer section of `docs/release.md`. Packaging reference checks passed;
no application installation or live cadence was tested for this documentation edit.

## 2026-09-30 — dry-run keeps the operator's own record (documentation only)

Review of the adapter batch above found it had made dry-run write nothing at all,
including the run log, findings and hire scans, which contradicted the queued test
plan (dry-run a session, confirm the Findings, Log and hire tabs fill) and would have
left the board empty for the two cadences an operator spends in dry-run. Corrected in
`SKILL.md`, `docs/sandbox.md`, `reference/run-recovery.md` and `reference/hire-scan.md`:
dry-run writes nothing to Jira or Calendar and posts no staging comment, but does
record `runs/`, `findings/` and `hires/` marked `mode: dry-run`, and does not advance
the watermark or ingested map. Zero-findings wording in `docs/setup.md` and `README.md`
restored to a red flag that must be argued away per check, keeping the rule against
manufacturing findings. Also: `bin/install.sh --help` no longer prints a stray script
line, the secret scan reports `file:line` without the value, and `docs/release.md`
records the working test command. No run.


## 2026-09-30 — always-on spike (`spike/FINDINGS.md`)

Proved from a one-off cloud routine: writing the board database, a Slack DM to the
operator, and propose → approve on the board → Gmail send with the receipt kept
(gmail id `1a0f35c7d34a10a0`). Defects found and fixed in this change:

- **Invented timestamps.** The routine wrote a midnight time and one later than the
  store's own write. Fix: every time comes from `date -u` (SKILL.md working rules,
  `reference/always-on.md`).
- **Thread-only reply read.** Both operator replies went into the DM, not the thread,
  and a thread read found none. Fix: check-ins read the whole DM since
  `state/checkin.slack_last_ts`, no prefix or threading required.
- **Slack DM does not notify.** The connector posts as the operator, so their own DM
  raises no alert. Fix: the DM is the record and reply channel; the interrupt is email
  to the operator's own address. Not yet confirmed that email alerts.
- **Superseded the same day:** the interrupt is now the routine's own notification
  ("Notify me when this routine finishes": push and email from Claude). The check-in's
  final line is the notification. Email-to-self and the Slack DM log are optional and
  need the guard settings on the routine's environment; without them every connector
  write is blocked, confirmed on the first check-in (`guard: active`, cloud: true).

## 2026-10-27 — source receipt gate (local helper validation)

Added private input capture through a configured read-only adapter, exact source
hashes, run IDs, quote membership checks, strict required fields and duplicate-ID
rejection. Weekly and always-on instructions require the receipt gate before
external writes and watermark advancement. Added a portable independent auditor
prompt; it is not an automatically registered agent. Mirantis review is restricted
to authorized Mirantis inputs and an active Mirantis provider.

13 local helper tests passed, including changed text, absent sources, mismatched
runs, whitespace quotes, empty receipts, duplicate IDs/JSON fields, partial coverage,
exact file hashes and nonzero CLI failure without raw content. Existing snapshot
renderer tests also passed. `bin/install.sh --target all --check` passed. The local
OpenCode builder was interrupted after exceeding its budget; the lead fixed the
draft and invalid fixture hashes. Independent review remains pending.

No real connector ingestion, board write, cadence run or hosted auditor was tested.
No production watermark advanced. Adapter execution does not prove completeness or
authenticity; quote membership does not prove semantic support. The host workflow
must invoke the gate; arbitrary direct connector or board UI writes are not
technically intercepted. No personal input artifacts were added to the bundle.

## 2026-10-27 organization routing update

Added multi-profile setup, single-organization project binding, conversational
profile/agent requests and private state separation. Added a deterministic manifest
validator; this validates policy intent, not account identity or live routing.
Claude/ChatGPT/Gemini/T3 end-to-end profile transitions and live connector ownership
checks remain unverified. No live state or accounts migrated.

Local validation: 22 helper tests passed, including cross-profile rejection,
Mirantis-only LiteLLM opt-in, distinct provider families, duplicate JSON keys,
malformed/oversize CLI inputs and explicit pending-identity output. Bundle checks
passed. A bounded local qwen3-coder:30b design attempt asked for direction rather
than completing review and was cancelled. IREN Claude Sonnet 5.5 reviewed the
implementation; first-round gaps were addressed with profile IDs distinct from
organization, real-manifest testing in the IREN app and broader negative tests.
No token savings or live identity/switching verification is claimed.

## 2026-10-26 / 27 — check-in coverage defects (live board, from the run log)

Found by the operator asking why a "0 notes, 0 DMs" line meant anything, then reading the
runs collection. Four defects in four check-ins:

- **Skipped sources recorded as complete.** The 16:11 check-in listed two new notes
  documents by title, skipped Gmail, wrote `complete` and advanced the watermark; the
  summary line said nothing needed the operator. The 12:09 check-in listed 25 of about
  200 message ids and triaged none, and did not use Slack at all. Fix: Drive notes,
  Gmail and the Slack DM are required sources; a run that skipped any is `partial`,
  leaves the watermark, and says so in the final line at every level.
- **Open findings dropped.** The 27 Oct 08:27 check-in wrote `findings_carried: 0`,
  `calendar-collision-today` clean and "nothing due today" while four findings were open,
  including an 11:30 collision that morning and a review due close of business. Fix: the
  open set is re-evaluated first on every run, imminent findings are always named in the
  final line, and a check cannot be listed clean while an open finding of it exists.
- **Findings never closed.** Fifteen collision and due-date findings from weeks 40 to 43
  were still `open` on 27 Oct. Fix: a cause that is plainly gone is closed by the
  check-in with a `close_note`.
- **Expired outbox item left unmentioned** (12:09 run, item from 8 Oct). Fix: counted
  and named in the summary and final line.

New: `scripts/checkin_verify.py` checks a run record against the open findings. Run
against the two live records above it fails both, for the reasons listed. Run against a
constructed good record it passes, and fails the same record when `could_not` admits an
unread source. It checks that a record is consistent, not that the sources were read.
No claude.ai run of the new rules yet.

### Same day: harness-written evidence (hooks and scripts, no claude.ai run)

Added `bin/ledger-log` (PostToolUse), `bin/guard-ledger`, `scripts/checkin_close.py`,
`scripts/audit_trend.py` and `docs/governance.md`. Exercised here against synthetic hook
events (our own code, not a connector): the ledger chains and records errors; a run that
claims 5 documents and 9 mails when the ledger shows 2 and 1 is refused, is `partial`, gets
no watermark and a final line that leads with the gap; deleting a ledger line is reported as
a broken chain; the guard denies a command naming the ledger and allows the close script;
with two findings given `due_at` the final line names both. The audit, run over the 57
real check-in records, shows 0 verified runs, 25 to 53 per cent partial weeks and 18
silent-green runs. Not yet proven: that the PostToolUse hook receives `tool_response` and
`session_id` as assumed on the claude.ai cloud environment, that the ledger path is
writable there, and that a real check-in follows the close-out. First thing to read after
the next check-in: its `ledger` block and `verified.ok`; if `calls` is 0 the hook is not
running on that environment and every run will report `partial` (correctly).

## 2026-10-28 — Delegation, primary failover and reviewer fallback

**Symptom.** Mid-setup, the Codex primary hit its workspace spend cap during a
calendar change. T3 handed the thread to Claude with a summary; whether the write had
landed was known only because a receipt had been saved to private state first. A
full cadence also loads every source into one context.

**Change.** `reference/delegation.md`: read-only workers mine per source and write
their own raw-input file for the receipt gate; the primary keeps reconcile, analysis,
approvals and writes, and saves `state/handoff` from the frozen window onwards.
Project policy version 2 adds `primary_order`, `review_order` and a generic `litellm`
source any organization can bind; the setup interview asks for each account and
plan. Version 1 policies still validate.

**Review.** Codex attempted first and failed on the spend cap; the fallback ran on
Mirantis LiteLLM `gpt-6-sol` (returned model confirmed). Five findings, all
accepted: takeover needs a shared state store (claude.ai artifact DB and Codex files
are not); workers must freeze source text, not just quotes; an explicit `--agent`
bypassed the order and the unavailable list (fixed, tested); a GPT gateway cannot
review a Codex primary (now explicit: pending); first checkpoint must precede
mining. 30 helper tests and both-target package checks pass.

**Not proven.** No cadence has run with workers or a mid-run takeover. First test:
a dry-run Monday in T3 with Claude primary and per-source workers; then stop the
primary after Pass 1 and resume in Codex from `state/handoff`.


## 2026-10-28 — Desktop rails actually run; antagonist on routine work

**Symptom.** On a Windows desktop every hook had been failing silently since it was
installed. `.claude/settings.json` called `python3`, which there is the Microsoft Store
stub (exit 49), and Claude Code treats any exit other than 0 or 2 as non-blocking.
`ledger-log` also imported `fcntl`, which does not exist on Windows. `guard-secrets`
watched Bash only, while the host also offers a PowerShell tool. `bin/litellm` had no
Windows key store. `bin/install.sh` could not build on Windows (no `zip` in Git Bash).
Nothing reported any of it.

**Change.**
- `bin/run-hook` finds a real Python, blocks the call if there is none, and turns a
  crashing guard's exit into 2.
- `guard-secrets` covers PowerShell environment and credential-store reads.
- `ledger-log` locks with `msvcrt` on Windows.
- `bin/litellm` reads Windows Credential Manager (`ursula-litellm`).
- `bin/rails-check` feeds each rail a test event and reports what works.
- `bin/install.sh --target desktop` builds a workspace zip with the rails and
  operator-facing AGENTS.md/CLAUDE.md, and falls back to Python's zipfile.

The antagonist now runs on every write batch and on check-in drafts before they are
written (`reference/delegation.md`). If it cannot run, writes proceed on approval and
the receipt gate, recorded as pending; the operator chose this so claude.ai hosts
still work. Objected actions are held.

**Observed.** After the change, in T3 with Claude, the live hook denied a Bash command
naming the key variable. It also denied the maintainer's own commit command, because
this entry's text named the patterns: a false positive on documentation, so edit docs
with the file tools. `rails-check` passes on this machine and from an unzipped desktop
zip. A fake crashing interpreter now blocks (exit 2).

**Review.** Codex was unavailable (spend cap, failed attempt earlier this session), so
the review ran on LiteLLM `gpt-6-sol`. Six findings:
1. Hooks do not run under Codex. Accepted; documented per host.
2. The check-in antagonist ran after writes. Fixed: it now runs on drafts.
3. `ledger-log` swallows errors. Rebutted: `checkin_verify` fails a run whose claims
   exceed the ledger.
4. A crashing guard failed open. Fixed.
5. Pending review contradicted the check-in completion rule. Resolved per the operator.
6. A policy command was incomplete. Fixed.

**Not proven.** No check-in or cadence has run the antagonist. Codex hooks are
absent. The LiteLLM key is not yet stored on this machine. Whether the claude.ai
sandbox could reach the gateway was not tested.

## 2026-10-28 — A stored key that was one control character; moving hosts

**Symptom.** After the operator stored the LiteLLM key with the documented credential
command, `bin/litellm check` got a bare HTTP 400 page from the gateway. The stored
secret was a single non-printable character: in a classic Windows console, Ctrl+V at a
hidden prompt types a control character instead of pasting. Nothing said so.

**Fix.** `bin/litellm store` prompts with hidden input, refuses control and non-ASCII
characters, and writes the credential itself. It refuses to run without a real console:
`isatty()` is true for NUL on Windows, and an agent's shell hung on the prompt until
`GetConsoleMode` was added. On a rejected request, `check` reports the key's length and
character classes, never its value. After re-storing: key accepted, 218 models.

**Moving hosts.** The operator wanted the live claude.ai board after setting up on a
desktop host. The board needs claude.ai's artifact database, so state cannot be shared;
`docs/setup.md` now has a one-way move with re-verification, and `config/run.home`
retires the old store so two primaries cannot diverge. Not yet run in claude.ai.

**Review of the above** (LiteLLM `gpt-6-sol`, run through `bin/litellm chat`, the first use
of the direct route). Two findings, both accepted:
1. A console check cannot prove the operator is typing; an agent's interactive shell
   passes it. `guard-secrets` now denies any agent command that runs the key store. The
   live hook was seen denying it.
2. Stripping NUL and tab before validation stored them instead of refusing. Only
   spaces and line breaks are trimmed now.

## 2026-10-28 — Proving the run: evidence the session did not write

**Why.** The operator caught Claude saying it had checked their email when it had not.
A second model reading that summary would have believed it too. Only evidence written
by something other than the session can catch it.

**Change.**
- The desktop call ledger now records every session, not just check-ins.
- `scripts/session_verify.py` checks a run's coverage claims against the ledger, cut
  at a SessionStart marker the harness writes. Reading Gmail means opening messages.
- An independent recount must cover every count a complete run claims.
- Desktop sessions publish runs and findings to `ursula-board-feed.json` in Drive. The
  claude.ai board reads it, labels the desktop's own verdict as self-reported, and
  can recount Gmail and Calendar for any run window itself, with no model involved.

**Observed.**
- Before the fix, the desktop ledger had never existed. Git Bash rewrote the default
  path to `C:/Program Files/Git/var/tmp`, which a normal user cannot write, and the
  logging hook never blocks, so nothing reported it. `rails-check` now checks the real
  location is writable.
- After the fix, a live Slack call in this T3 session was recorded by the hook, and a
  run claiming a Gmail read was rejected: "run claims Gmail read, but no such call is
  recorded".
- Real responses for the board's four new connector calls were observed before
  publishing: Drive list, Drive read (contents come back already parsed), Gmail list
  (an empty result has no `messages` key) and Calendar list.
- The gateway's Drive upload fails ("outside the current directory"). The feed is
  written with Google's own Drive connector.
- The live ledger guard denied this maintainer's own edits whenever they named the
  ledger, including edits to the guard itself; the code now assembles those names.

**Review.** LiteLLM `gpt-6-sol`, two rounds.
- Round 1 found 8 problems:
  1. The ledger can still be edited by the agent. Accepted as a limit, guard narrowed,
     documented.
  2. The board showed the desktop's verdict as independent. Relabelled self-reported.
  3. The recount was optional. Fixed.
  4. The session chose its own cutoff. Fixed with the SessionStart marker.
  5. Listing Gmail ids counted as reading. Fixed.
  6. Coverage fields went unchecked. Fixed.
  7. The check-in promise did not match the code. Docs narrowed.
  8. Malformed recount pages counted as zero. Fixed.
- Round 2 found 3 more, all fixed: a missing marker now fails; the verifier exemption is
  pinned to the repo's own path; a Gmail read with no opens needs a zero recount.
- A malformed count crashed the verifier until the tests caught it.

**Not proven.**
- Whether T3 fires SessionStart. `rails-check` warns until a marker appears; without
  it every run verifies as failed.
- The board changes have not run in claude.ai and need a full-set capability republish.
- The recount worker has not run in a real session.
- The ledger stops a session that claims a read it never made. It does not stop a
  session set on deceiving: anything running as the operator can rewrite a local file.

## 2026-11-04 — check-ins that never finish reading (live board, from the run log)

Found by the operator noticing that notes and mail were sometimes not read. All 74
check-in records (30 Sep to 3 Nov) were read; every run since 2 Nov 12:14Z was
`partial` and the watermark had not moved for six runs.

| # | Symptom | Fix |
|---|---|---|
| 14 | Long Gemini notes (an hour's meeting with transcript) exceed the tool reply limit; `read_file_content` errors, the run reads the saved overflow file, and the ledger counts no open. Five runs, 28 Oct to 2 Nov. | Read by plain-text export or tab by tab; `bin/ledger-log` marks an errored call with a body of 50,000 bytes or more as `oversize`, and the verifier counts it as opened because the content came back. |
| 15 | Gmail listed about 60 per run and opened 8 to 10 "to save budget"; on 3 Nov 20:11 the close-out script allowed `complete` and the model recorded `partial` by hand. | Exclude automated senders in the query (`config/checkins.gmail_exclude`) and open every result; the verifier refuses `complete` when `gmail_opened < gmail_listed`. |
| 16 | One unreadable source held the whole window: six partial runs on one watermark, each window larger than the last. | `carried_sources`: a partial run that names every gap by id may advance; carried items become `pending_sources`, read first next time, and become a finding after three carries. |
| 17 | `always-on.md` said to list notes "modified in the window", contradicting `mining.md` (`createdTime`); 1 Oct re-listed 29 Sep notes. A document created at meeting start and shared at the end can fall between windows. | `createdTime` with a 24-hour lookback, de-duplicated against `state/checkin.read_sources`, plus attachments on events that ended in the window. |
| 18 | `docs_get` returned only the Notes tab; a 2 Nov run reported "no summary produced" and never opened the transcript. | Read the transcript tab when the Notes tab has no summary. |

Not yet proven in claude.ai: that `gws_drive_files_export` with `text/plain` fits in one
reply for the longest documents; that the PostToolUse body of an oversize read is the
content rather than a short error; that `after:`/`before:` with epoch seconds is honoured
by both Gmail tools. First thing to read after the next check-in: `coverage`,
`carried_sources` and whether `state/checkin.watermark` moved.

Review, 2026-11-04: Mirantis LiteLLM (default reviewer model), one round on the frozen diff.
Two "high" findings rejected after checking the code: the `state_checkin` condition is not
inverted (`not carry_ok(run)` is true only for an empty error list), and partial runs do
get the ledger-backed claim checks (`status in ("complete", "partial")`). One accepted:
`opened_ids` was undocumented; it is now in `config/schema.md`, and only matters without
`--ledger`. Local checks re-run by the lead: all six test files pass (17 new tests),
`bin/install.sh --check` passes.

## 2026-11-04 — repository baseline audit

Audited commit `6d11f5a`; observations recorded at 2026-11-04T22:10:21Z.
This was a repository audit, not a cadence or live acceptance run. No connector
calls, board publication or runtime fixes were performed. Existing untracked
`.DS_Store` was left untouched.

**Executed:** `bin/install.sh --target all --check` passed; Python unittest
discovery passed all 68 tests. The entrypoint is 359 lines. These checks validate
local helpers and packaging constraints, not the cadence or host integration.

**Open findings (not fixed):**

1. **High — check-in evidence is not scoped to the current run.**
   `scripts/checkin_verify.py:220` calls `ledger_facts(ledger)` without a cutoff;
   `scripts/checkin_close.py` also reports facts from the entire ledger. A local
   fixture with every call dated 1 October passed verification for the existing
   2 November complete-run fixture with no errors. Old reads and finding writes
   can therefore back a new run and permit watermark advancement. Bind evidence
   to the harness-recorded session/run before verifying or reporting it.
2. **High — repeated Gmail calls count as different messages read.**
   `scripts/checkin_verify.py:91` counts calls, although distinct IDs are also
   collected. A fixture claiming two listed and two opened messages passed with
   two reads of `m1` and only one distinct message ID. Compare actual distinct
   message coverage, with explicit thread-read semantics, before treating the
   unread gap as closed. The shared ledger fact also feeds session verification.
3. **High — sandbox calendar proposals can reach a real write.**
   `artifact/index.html:1344` blocks dry-run and mode mismatches but permits an
   item and current mode both set to sandbox. Evaluating the actual `whyNot`
   function locally for a calendar-block proposal returned null (unblocked).
   Its send branch at line 1335 inserts on the primary calendar after approval,
   contrary to SKILL.md's sandbox rule that calendar changes remain proposals.
   Enforce sandbox restrictions in both the approval and dispatch paths; also
   check Jira outbox target routing against the sandbox project.

The reproductions used temporary input records and the board's pure gate function;
they did not mock connector responses or establish any live behavior. Independent
model review remains pending; no external reviewer was invoked and no provider
account authorization was inferred from this checkout's location.

**Acceptance still outstanding in the recorded history:** cold installation end
to end, the latest board changes in claude.ai, a real independent recount, and the
4 November long-document/carry-forward changes in a live check-in. Documentation
also needs a status refresh: README still calls the project early, CLAUDE.md's
current-state section describes the September batch, and docs/release.md says
`--target all` builds two bundles although the installer now builds three.

### 5 Nov: the three findings fixed (local checks only, no claude.ai run)

1. **Evidence scoped to the run.** `ledger_facts(..., this_session=True)` counts only
   calls from the session of the latest `session_start` marker, from that marker on.
   `checkin_verify.py` and `checkin_close.py` both use it. A ledger with no marker
   fails. Writing the tests turned up a second defect: two sessions starting in the same
   second resolved to the older one. Ties now go to the later line.
2. **Gmail counted by distinct id.** `gmail_opened` is the number of distinct message or
   thread ids read. Reads with no recorded id (`gws_gmail_read`) count as none.
   `bin/ledger-log` now keeps `messageId` and `threadId`. This also tightens
   `session_verify.py`, which shares the fact.
3. **Sandbox gate.** `whyNot` refuses a sandbox `calendar_block`, and a sandbox
   `jira_comment` outside `config/run.sandbox_project`. `send()` re-runs the gate before
   any write. The audit's note on Jira routing in sandbox is covered by the second rule.

**Executed by the lead:** `python3 -m unittest discover -s test` passed 73 tests (5 new,
one per reproduction plus the tie and the missing-marker cases).
`bin/install.sh --target all --check` passed. The board's real `whyNot` was evaluated
in node for seven cases: sandbox calendar, sandbox Jira inside and outside the project,
sandbox with no project set, live calendar, live Jira, and dry-run. Only the expected
cases came back unblocked. `node --check` passes on the board's inline script.

**Not yet observed:** the republished board in claude.ai, and a live check-in under
the session scoping. One risk: on a host whose SessionStart hook does not fire,
check-ins that verified before will now come back partial. `bin/rails-check` reports
whether the marker is being recorded.

**Review (Mirantis LiteLLM, default model, one round; `.handoffs/20261105-123022-litellm/`).**
It raised five defects. Four were rebutted against the code: the config race (`runMode`
and `sandboxProject` are set in one snapshot callback, and `runMode` stays null until
then), "`str()` undefined" (it is at `artifact/index.html:742`), `since` being
overridden (only the later cutoff is kept, so a caller can narrow the window, not widen
it), and unknown Gmail tools (already excluded by tool name). One gap was accepted:
nothing showed `bin/ledger-log` actually writes the ids. A new test now feeds six real
hook events through `bin/ledger-log` and gets three distinct ids. The suite is 74 tests,
all passing. No second round was needed.
