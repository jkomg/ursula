# Golden week — 2026 w39

A week processed by hand before the skill existed. The sources are real, the
outcomes are known, and the skill should reproduce them.

## How to run it

1. `config/run.mode` = `dry-run`
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

**Findings** — partial credit. Six of nine is a pass for a first run. Findings 2, 3
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
