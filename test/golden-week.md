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
