# Pack: content-cleanup

For an operator whose work is a Confluence cleanup backlog: finding the pages that are
out of date, lost, duplicated or unowned, and getting each one fixed, merged, archived
or handed to an owner. Enable it with `content-cleanup` in `config/packs.enabled`.

Before this pack, Ursula read Jira tickets *about* pages and never a page. An operator
whose whole project was the pages got a run that reconciled the backlog against itself
and could not tell whether it described the space. This pack reads the space.

**Nothing in this file has run against real data yet.** Every check below is marked
unproven, and every connector detail marked *observe at setup* is a question the first
run must answer and write back here, not a fact. Do not act on a tool response shape
this file has not recorded.

## Config

`config/packs.content-cleanup`, written by the setup interview. None of these has a
default, because each one is a judgement about the operator's space that nobody else
can make.

| Field | Holds | Why it is asked, not assumed |
|---|---|---|
| `spaces` | Confluence space keys in scope | A cleanup that silently reads the wrong space reports a clean bill of health on the space that matters |
| `space_ids` | The numeric id for each key, resolved at setup | `getPagesInConfluenceSpace` takes a space **id**, not a key. Resolve with `getConfluenceSpaces` (`keys: [...]`) once and store it |
| `stale_days` | Days without a meaningful edit before a page counts as stale | Ninety days is stale for a runbook and fresh for an architecture decision. Ask; if the operator wants different thresholds per space or per label, store them per space |
| `exempt_labels` | Labels marking pages meant not to change: policies, decision records, meeting minutes | Without these, the staleness check fires on every page that is correct precisely because it is finished |
| `owner_rule` | What "owned" means in this space — see `unowned-page` | Confluence has more than one candidate for owner, and the operator's cleanup policy decides which one counts |
| `bulk_editors` | Accounts or apps whose edits do not count as maintenance | See the staleness trap below |
| `backlog_project` | The Jira project holding the cleanup tickets. Must also be in `config/jira.owned` | Pass 2 reconciles pages against it |
| `ticket_batching` | How findings become tickets: one per page, or one per check per space with the pages listed | Four hundred stale pages as four hundred tickets buries the backlog. The operator chooses |

## Passes

**Pass 1 — read the spaces.** For each space in `spaces`, list every current page. Use
`searchConfluenceUsingCql` with `space = <KEY> AND type = page`, or
`getPagesInConfluenceSpace` with the stored `space_id`. Either way:

- **Page to exhaustion.** Both tools cap at 250 results per call and return a cursor.
  This is the Drive `nextPageToken` defect again (`test/golden-week.md`, defect 6): a
  first page treated as the whole set reports a clean space while missing most of it.
  State the page count per space in the run report, so a count that stops at exactly
  25, 100 or 250 is visible as a cap.
- **Record what you read.** Per page: id, title, space, parent, created, last modified,
  last modifier, creator, labels, and whatever owner field the connector returns.
  *Observe at setup* which of these the response actually carries, and write the field
  names into this file.
- **Current pages only.** Archived and trashed pages are out of scope for the checks.
  They are in scope for `backlog-drift`, because a ticket saying "archive X" should see
  X as archived.

**Pass 2 — reconcile pages against the backlog.** Pull the open set of `backlog_project`
once (`reference/jira-conventions.md`, "Pull the board's open set") and match tickets to
pages **by page id**, taken from the page URL in the ticket (`/pages/<id>/`). Never by
title: cleanup retitles pages, so a title match finds the wrong page or none, and the
duplicate-title check is by definition the case where titles do not identify a page.

A ticket that names a page by title only, with no link, is itself a finding under
`backlog-drift` — it cannot be verified, now or later.

**Pass 3 — the checks below, after the core set.** Core checks still apply: a cleanup
backlog has deadline inversions, stale parents and self-blocking like any other.

## Checks

| Slug | Check | Proven in a test run |
|---|---|---|
| `stale-page` | No meaningful edit in `stale_days` | Not yet |
| `orphan-page` | Outside the page tree, or reachable by nothing | Not yet |
| `duplicate-title` | Two pages that are the same page | Not yet |
| `unowned-page` | No living owner under `owner_rule` | Not yet |
| `backlog-drift` | The backlog and the space disagree | Not yet |

**Report counts, then the pages that matter.** A space-wide check can fire on hundreds
of pages. Lead each check with the count per space, then list the pages ranked by
consequence — most viewed or most linked-to first where that is knowable, otherwise
those under the most important parent — and cap the inline list at what the operator
can read in the session. The full list goes into the changeset or the batched ticket,
never silently truncated.

---

### `stale-page`

A page with no meaningful edit in `stale_days`, not carrying an `exempt_labels` label.

CQL: `space = <KEY> AND type = page AND lastmodified < now("-<stale_days>d")`.

**The staleness trap.** Last-modified is the Drive `modifiedTime` problem again
(defect 1): it moves for reasons that have nothing to do with the content being
maintained. Expect a bulk operation — an editor conversion, a macro migration, a
find-and-replace across a space — to make hundreds of untouched pages look fresh on
the same day. Two defences:

- Where the last modifier is in `bulk_editors`, treat the page as unmodified since the
  edit before that one, if the connector exposes history; if it does not, say the check
  is weakened for those pages rather than calling them fresh.
- Where many pages share one last-modified date, report it as a probable bulk edit and
  ask, rather than accepting it.

When it fires, the recommendation is one of three, and the operator picks: confirm
still true (a trivial edit resets the clock and says someone looked), rewrite, or
archive. Stale is not wrong. Do not recommend archiving a page on age alone.

---

### `orphan-page`

A page that nobody can find by browsing. Two different things carry this name, and the
report must say which:

- **Tree orphan** — a page sitting at the top level of the space beside the homepage,
  outside the intended hierarchy. Visible from the parent field read in Pass 1: a page
  whose parent is the space root and which is not the homepage or a declared top-level
  section.
- **Link orphan** — a page no other page links to. Confluence shows these in the space's
  orphaned-pages report, but no CQL field for inbound links is known, and none of the
  connector tools lists incoming links. *Observe at setup* whether any response carries
  them. Until then, this half **cannot run from the connector**: say so under *what
  could not be done*, and offer to take the operator's pasted export of the space's
  orphaned-pages report instead. Do not approximate it by text-searching for the title
  — that finds mentions, not links, and would report a linked page as orphaned.

A tree orphan usually wants moving; a link orphan wants linking or archiving. Neither
is resolved by the skill.

---

### `duplicate-title`

Two pages that are the same page.

Normalise titles before comparing: case, whitespace, punctuation, and the prefixes and
suffixes that copying leaves behind — `Copy of `, `(copy)`, `v2`, `- old`, `DRAFT`,
dates. Compare within each space and across the spaces in scope. Then look at the
bodies of the matches before reporting: two pages called "Onboarding" in two teams'
spaces may both be correct.

Report the pair (or set) with created and last-modified dates, last modifier and
parent, and recommend which survives. The usual answer is the one other pages link to
and people still edit; the usual trap is keeping the newer copy because it is newer,
when it is an abandoned fork.

When the survivor is agreed, the rest become one ticket: merge anything unique into the
survivor, then archive. Never two tickets, because merging and archiving done by
different people in the wrong order loses the unique content.

---

### `unowned-page`

A page with no living owner under `owner_rule`.

Confluence offers several candidates for "owner": a page-owner field (*observe at
setup* whether the connector returns one), the creator, the last contributor, and the
owner of the parent. `owner_rule` records which one the operator's cleanup policy
means. Ask; the common answers are:

- the page-owner field, falling back to the creator when it is empty
- the creator, full stop
- whoever owns the parent section, for spaces organised by team

A page is unowned when the rule yields nobody, or yields someone who has left.
Establish "has left" from the account's active status if the connector returns it; if
it does not, match against the people map and ask about names that do not resolve,
never inferring departure from a quiet edit history.

Report unowned pages grouped by section, because an owner is usually found for a
section, not a page. Recommend a candidate owner only where the evidence names one —
the most frequent recent contributor, or the owner of the parent. Never invent an
owner (`SKILL.md`, working rules).

---

### `backlog-drift`

The backlog and the space disagree. Four shapes:

| Shape | Means |
|---|---|
| A ticket closed as done, but the page it names is unchanged since before the ticket was raised | The fix never happened, or happened somewhere else |
| A ticket says archive or delete, but the page is still current | Same, and it matters more: people are still reading it |
| A page fires a check above with no open ticket against its id | The backlog does not describe the space — this is new work, routed through Pass 5 |
| A ticket names a page by title with no link, or links a page id that no longer exists | The ticket cannot be verified; fix the ticket first |

The first two are this pack's `orphaned-commitment`: something agreed that did not
become real. They are worth more than any single stale page, because they show where
the cleanup process itself is leaking.

## Prohibitions

The Atlassian connector can create and update Confluence pages and post page comments.
**This pack never edits, moves, archives, deletes or comments on a Confluence page**,
in any mode. Every change to a page is proposed as a Jira ticket in `backlog_project`
and made by a person.

The reason is the same as for email and Slack: a comment or an edit on a shared page
speaks for the operator to everyone who reads it, and an archive done in error hides a
page from every reader at once. The skill finds and proposes. The operator and their
backlog decide.
