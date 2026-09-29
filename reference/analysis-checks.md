# The analysis checks

Every operator runs the **core set** below. On top of it, each operator enables the
**domain packs** that match their work, listed in `config/packs.enabled`. Run the core
set and every enabled pack, every cadence. Report what fired; state plainly when a check
ran clean.

Every example below is real, from the week this skill was written.

## Why core plus packs

The first version shipped nine checks as a single list, all drawn from one operator's
service-delivery work. Two of them — capability confusion and template propagation —
only make sense for someone onboarding people onto cloned boards and access grants. The
second operator's only project is a Confluence cleanup backlog; for them those two checks
could never fire, and the checks that *could* matter — stale pages, duplicate titles,
pages nobody owns — did not exist, because Ursula read Jira tickets about pages and never
read a page.

So the checks split by who they apply to, not by how important they are:

| Set | File | Applies to |
|---|---|---|
| Core | this file | Anyone with a Jira board, a calendar and a manager |
| `service-delivery` | `reference/packs/service-delivery.md` | Onboarding hires, access grants, boards cloned from templates |
| `content-cleanup` | `reference/packs/content-cleanup.md` | A Confluence cleanup backlog: stale, orphaned, duplicate and unowned pages |

A pack is not optional polish. An operator whose work matches a pack and does not enable
it gets a run that looks complete and misses the findings that justify the skill.

**Check ids are stable.** Each check has a slug (`deadline-inversion`,
`stale-page`, …). The slug is what goes into a finding key
(`<person>-<check>-<week>`) and into `state/findings`, so renaming one breaks the
duplicate-card check between two operators and the new-versus-carried comparison between
weeks. Add checks; do not rename them.

## Core checks

| Slug | Check | Proven in a test run |
|---|---|---|
| `deadline-inversion` | A dependency due after the thing that consumes it | Not yet |
| `policy-conflict` | A proposal against the operator's written policy | Yes |
| `scope-drift` | A title that understates the work by an order of magnitude | Yes |
| `orphaned-commitment` | Said in a meeting, never became a ticket | Yes |
| `self-blocking` | The operator is the blocker on someone else's board | Yes |
| `stale-parent` | A parent so overdue its children's dates mean nothing | Yes |
| `calendar-collision` | Double-bookings and meetings on top of better ones | Yes |

"Not yet" means the check has never fired against real data. It is not evidence the
check is wrong, and it is not evidence it works.

---

### `deadline-inversion`

A dependency scheduled after the thing that consumes it.

Compare each item's due date against the due date of anything that needs its output.
Check especially against the one-pager date, which is the most common consumer.

> NOM-3, the audit that produces "pillars with owners," was due Friday. The
> one-pager that reports that number was due Thursday night. The note would have
> shipped without its headline figure.

Look for this wherever a number, a decision or an artifact is promised to someone on
a fixed date.

---

### `policy-conflict`

A proposal that contradicts the operator's own written policy.

Config lists the policies. Check every new proposal, especially ones arriving from
outside the operator's team, where the policy is not known.

> A shared service account was proposed for a paid AI tool. The operator's written
> policy is per-person credentials with no shared service accounts. Cost was being
> debated in the room; the identity conflict was not.

Do not resolve these. Raise them as decisions with a recommendation.

---

### `scope-drift`

A ticket's title understates its actual size by an order of magnitude.

Compare ticket titles against what source documents say the work involves.

> "Walk the Swamp workflows" turned out to be 300-plus composable workflows, each
> requiring a human operator run before automation could be trusted. Unsized,
> unowned, and sitting inside a five-week handover window.

Trigger on vague verbs — walk, review, look at, align, understand, clean up — attached
to things that might be large.

---

### `orphaned-commitment`

Said in a meeting, never became a ticket.

Every mined action item is checked against Jira. Anything without a match is either
a new ticket or a deliberate decision not to track it — and the decision gets said
out loud, not assumed.

Watch for commitments made *by* other people to the operator. Those get tracked as
dependencies with a name attached, because they are the raw material for "blocked
and on whom."

---

### `self-blocking`

The operator is the blocker on someone else's board.

Sweep watched boards for items blocked, awaiting review, or with an unanswered
comment where the operator is the one who owes something. These rarely appear on
the operator's own board, which is exactly why they rot.

> Unanswered comments and unmade introductions across three onboarding boards all
> traced back to one queue.

An operator with no watched boards still runs this check against Slack mentions and
mail threads awaiting their reply (`reference/mining.md`). "No watched boards" is not
"nothing to check".

---

### `stale-parent`

A parent item so overdue it makes its children's dates meaningless.

Check epics and phase parents against their children. A phase epic a quarter overdue
signals that nobody believes any date underneath it.

> A phase epic still open with a due date ten weeks in the past, with active
> children carrying dates as if it meant something.

Resolution is binary: close the parent, or give it an honest new date.

---

### `calendar-collision`

Double-bookings, and meetings sitting on top of higher-value ones.

Scan the cadence window for overlaps. Report with a recommendation on which to drop,
including whether the operator is actually required at each — an attendance list
that says "all sales personnel" is not a claim on a delivery manager's Wednesday.

Also flag recurring meetings the operator has decided to skip but never declined.
A decision that lives only in someone's head is invisible to everyone reading their
calendar.

---

## Writing a new pack

A pack is one file in `reference/packs/`. It must state:

1. **Who it is for** — the kind of work that makes it apply, in one paragraph.
2. **Config it needs** — fields under `config/packs.<pack>`, each asked in the setup
   interview and each verified by execution in the completion contract
   (`docs/setup.md`).
3. **Which passes it adds to** — usually Pass 1 (what else to read) and Pass 2 (what to
   reconcile against).
4. **Its checks** — each with a stable slug, a definition, a worked example, and what
   the operator should do when it fires.
5. **Its prohibitions** — any writes the pack's connectors make possible and the skill
   must never do.

Mark every check in a new pack "not yet proven" until it has fired against real data,
and log the run that proved it in `test/golden-week.md`.

## Reporting

Lead with what fired, ordered by consequence, not by check or pack. Each finding gets
the evidence, the consequence, and a recommendation.

State when checks ran clean, by slug, including the pack checks. "Nothing
self-blocking this week" is information, and its absence makes the operator wonder
whether the check ran at all. A check that could not run — a space unreachable, a field
the connector does not return — goes under *what could not be done*, never under
*clean*.
