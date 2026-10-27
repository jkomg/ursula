# Governance: keeping an unattended run honest

A check-in is an agent running with nobody watching. The failure that matters is not a
crash (those are loud) but a run that does less than it says and reports success, because
the same model does the work, writes the evidence and writes the summary. This page says
what holds that in place, what each layer proves and does not, and how to carry it to a
different harness.

## The principle

**Whoever does the work does not grade it, and whoever grades it cannot be edited by the
worker.** Everything below is that idea applied at a different point.

## Layers

| Layer | Where | What it proves | What it does not |
|---|---|---|---|
| Call ledger | `bin/ledger-log` (PostToolUse hook) | Which connector and board calls happened, when (harness clock), with hashes of the responses. Written by the harness, not the model | That the model *understood* what it read. A same-user process can still edit the file |
| Ledger guard | `bin/guard-ledger` (PreToolUse hook) | Plain attempts to edit or read the ledger from Bash, Write or Edit are denied and visible in the transcript | Anything built from pieces of a path. It is a speed bump |
| Verifier | `scripts/checkin_verify.py` | Claims in the run record agree with the open findings and the ledger: documents opened, Gmail listed and opened, the DM read, the notes collection read, a board write for every finding claimed as re-evaluated, an unbroken hash chain | That a source was read *well*. It checks that the calls exist, not that the judgement was good |
| Close-out | `scripts/checkin_close.py` | The status the run may claim, the watermark it may write, and the final line the operator is sent are produced by code from verified evidence | That the model writes what the script printed. The instruction is in `always-on.md`; the audit below catches a run that did not |
| Audit and trend | `scripts/audit_trend.py` | Over weeks: partial rate, runs nobody verified, complete runs that listed a check clean while a finding of it was open, findings opened, resolved, lapsed, the age of the oldest open one, weekdays with fewer check-ins than scheduled | Cause. It tells you a source is failing, not why |

Run the audit weekly (a Monday session is the natural place) and read the *unverified* and
*silent-green* columns first: those are the runs where the harness could not or did not
check the model's account. On 27 Oct, against the real board history (57 check-ins since
30 Sep), it reported none of them verified, between 25 and 53 per cent partial per week,
and 18 complete runs that listed a check clean while a finding of that check was open (matched against the findings open today, so an approximation for older weeks).

## What is still on trust

- The ledger lives on the machine the agent runs on. For a claude.ai cloud routine that is
  an ephemeral container: it proves the run to the close-out script at the end of the run,
  and its summary and head hash go onto the run record, but the ledger itself is gone
  afterwards. Anchoring the head hash outside the agent's reach is the missing piece.
- The model could write a favourable `coverage` block *and* make the matching calls
  cheaply (open a document and ignore it). The ledger raises the cost of dishonesty; it
  does not read the model's mind.
- Judgement is unaudited. Whether a finding is the right finding is for the operator, and
  for the sampling below.

## Moving to another harness (T3 Code, a local model, several vendors)

The pieces are small on purpose. Per harness you need three things, and nothing in the
scripts is specific to Claude:

1. **A hook or wrapper that logs every tool call** in the ledger format (`seq`, `ts`,
   `tool`, `args` summary, `error`, `bytes`, `sha256`, `prev`). In T3 Code the logger should
   run **outside the agent's sandbox**, on the operator's machine, so the same-user
   weakness above goes away: the agent gets tools, not the file.
2. **A different model as the checker.** Use the cheapest independent model that can read:
   a local LLM, read-only, given the run record, the ledger, and a random sample of the
   window (three messages, one document, one ticket) with the instruction to re-read them
   and say whether the record's claims hold. It must not be shown the worker's reasoning.
   A worker and a checker that share a vendor share failure modes; mixing them is the
   point of running several.
3. **Anchoring.** Write the ledger head hash, after every run, somewhere the worker cannot
   rewrite: a file on the operator's machine, an append-only log, or a commit.

Not built: the independent checker, canaries (a labelled test document or event seeded into
each window; a run that does not report it did not read that source), and the anchor. The
first two are the next step after the hooks have run in claude.ai and the real failure
rate is known.

## Sampling by a person

Once a month, take three check-ins at random, read what each says it read, and open two of
the things it names. This is the only check that tests judgement, and it is cheap enough to
keep doing.
