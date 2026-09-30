# Cadence

Two sessions a week. The gap between them matters more than either.

## Monday — plan

Roughly an hour, most of it the operator reading and deciding rather than Claude
working.

| | |
|---|---|
| Pass 0 | Operator's fifteen minutes with handwritten notes. Claude asks, then waits. |
| Pass 1 | Mine Drive, Gmail, Calendar since the watermark. |
| Pass 2 | Reconcile against Jira. Half the candidates usually already exist. |
| Pass 3 | Run the core checks and every enabled pack. |
| Pass 4 | Tagging sweep — Claude proposes, operator disposes. |
| Pass 5 | Write back to Jira, update the board, update the database. |

Pass 0 is the one that gets dropped, and it is the one input nothing else can reach.
Ask first, stop, and wait for a reply.

## Thursday — retro and one-pager

Scheduled before the one-pager is due, never on the same edge. If the note is due
Thursday night, the retro is Thursday early afternoon.

1. What moved since Monday
2. Blocked and `needs-review` sweep across watched boards
3. Assemble the one-pager from staged comments
4. Re-run the analysis pass — a week of new information usually breaks something
   agreed on Monday
5. Update board and run log

## Between sessions

The continuous practice is staging. A finding on Tuesday becomes a comment on the
one-pager's ticket on Tuesday, under the section it belongs to. Thursday is then
assembly, not recall.

This is the difference between a retro that takes twenty minutes and one that takes
two hours and still misses things.

## The team call

If a recurring call with the manager and the reports sits near the retro, run the
blocked sweep **the night before** rather than the morning of. Nobody should first
hear about a blocker in that call if it has been sitting since Monday.

The same sweep, filtered to one person, is the prep for their one-to-one — a **hire
scan**. Ask for it Monday or Tuesday morning, before the week's one-to-ones: "scan
Vandit's board". It lands as that person's tab on the board, and the tab reads their
board live when opened, so it stays useful through the week. See
`reference/hire-scan.md`.

## Adjusting

Cadence lives in config. Two rules survive any rearrangement:

- The retro sits before the one-pager deadline, with room to act on what it finds
- Planning sits early enough in the week that the week can still be changed
