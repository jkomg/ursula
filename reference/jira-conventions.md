# Jira conventions and traps

Read before any write. Most of these were learned by getting them wrong.

## Identifiers

`cloudId` comes from config. Never hard-code it into the skill.

Workflow transition ids are usually uniform across a company's projects — commonly
`11` To Do, `21` In Progress, `31` Blocked, `41` Done — but confirm at setup and
store them in config. `getTransitionsForJiraIssue` **excludes the current status**,
so it shows where an issue can go, not where it is. Surface available transitions as
explicit choices; never infer one.

## The label-replacement trap

`editJiraIssue` replaces the `labels` array wholesale. It does not merge.

Read the existing labels, append, then write the full set. Adding a tag by sending
only that tag silently strips every other label on the ticket, including ones other
people's tooling depends on.

## Response envelopes

`searchJiraIssuesUsingJql` may return `{issues: {nodes: [...]}}` rather than
`{issues: [...]}`. Parse with a helper that handles both.

Large results are written to a file instead of returned inline. The file is a JSON
array whose first element has a `text` key holding the payload as a **string**, so
it needs a second parse:

```python
raw = json.load(open(path))
data = json.loads(raw[0]["text"])
issues = data["issues"]
```

## Result caps

`maxResults` caps silently. A query returning exactly 100 has almost certainly been
truncated. Narrow by project or paginate — never conclude from a capped result that
something does not exist.

Unscoped text searches across a large instance return mostly noise from unrelated
projects. Scope to configured projects before searching by text.

Even scoped, `text ~` is the wrong reconcile tool. Matching five candidates against
one board by keyword returned a capped page dominated by unrelated training cards.
Pull the board's open set once — `project = X AND statusCategory != Done` — and match
candidates against that in memory. One query, no cap, no keyword guessing, and the
full set is then available for the self-blocking and stale-parent checks anyway.

## Board queries

The board is assignee-scoped with no project filter:

```
assignee = currentUser() AND labels = "<tag>" ORDER BY duedate ASC, priority DESC
```

This means the tag is safe across operators — two people can both use it and never
see each other's work, because the assignee clause separates them.

It also means **undated items sink to the bottom**. Anything that should be seen
needs a date.

Consequence worth checking every run: an item without the tag is invisible to the
board regardless of importance. Verify the labels are true rather than assuming.

## Watched boards

Read only. Weekly sweep:

```
project IN (<watched>) AND (status = Blocked OR labels = "needs-review")
```

`needs-review` is applied by the people living in those boards to flag what is
broken or unclear. It is a feedback channel from the people being onboarded, and it
is worth more than anything inferred from the outside.

Findings become cards on the shared manager board, assigned to whoever owns them.
Never comment on an individual's own board — two managers' tooling doing that turns
someone's onboarding queue into a conversation between robots.

## Excluded projects

Templates and probes. Never scanned for the operator's work.

They are still searched for the template-propagation check. Excluded means "not a
source of tasks," not "invisible."

## Writing

**Descriptions carry reasoning, not just instructions.** A ticket should survive
being read cold in three weeks by someone who was not in the meeting.

**Comments carry findings.** When an analysis check fires on an existing ticket, the
finding goes on that ticket as a comment with its evidence. This is also how
one-pager content accumulates through the week.

**Cross-reference explicitly.** When two tickets look like the same work and are
not, say so on both. Collapsing distinct grants into one ticket is how people end up
believing they have access they do not have.

**Source every mined ticket.** Name the meeting and the date in the description.
