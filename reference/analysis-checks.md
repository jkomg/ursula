# The analysis checks

Run all nine every cadence. Report what fired; state plainly when a check ran clean.

Every example below is real, from the week this skill was written.

---

## 1. Deadline inversion

A dependency scheduled after the thing that consumes it.

Compare each item's due date against the due date of anything that needs its output.
Check especially against the one-pager date, which is the most common consumer.

> NOM-3, the audit that produces "pillars with owners," was due Friday. The
> one-pager that reports that number was due Thursday night. The note would have
> shipped without its headline figure.

Look for this wherever a number, a decision or an artifact is promised to someone on
a fixed date.

---

## 2. Policy conflict

A proposal that contradicts the operator's own written policy.

Config lists the policies. Check every new proposal, especially ones arriving from
outside the operator's team, where the policy is not known.

> A shared service account was proposed for a paid AI tool. The operator's written
> policy is per-person credentials with no shared service accounts. Cost was being
> debated in the room; the identity conflict was not.

Do not resolve these. Raise them as decisions with a recommendation.

---

## 3. Capability confusion

Someone believes an access grant does something it does not.

Read the actual description of an access ticket rather than its title. Grants that
sound equivalent usually are not.

> "I have access, I can get in through the proxy" — but the open items were a
> break-glass key and a vault decryption key. The proxy is the everyday path.
> Break-glass exists precisely for when the everyday path is the broken thing, and
> without the vault key the tooling cannot reach the fleet at all.

Especially important when the work depends on deliberately breaking something.

---

## 4. Scope drift

A ticket's title understates its actual size by an order of magnitude.

Compare ticket titles against what source documents say the work involves.

> "Walk the Swamp workflows" turned out to be 300-plus composable workflows, each
> requiring a human operator run before automation could be trusted. Unsized,
> unowned, and sitting inside a five-week handover window.

Trigger on vague verbs — walk, review, look at, align, understand — attached to
things that might be large.

---

## 5. Template propagation

A fix applied to live instances while the source stays broken.

Whenever a correction touches anything cloned from a template, search the excluded
template projects for the same item. Excluded means not scanned for work — it does
not mean invisible.

> Three per-person onboarding boards had a card with a bad training link. Fixing
> those three leaves two template boards untouched, so the next hire inherits the
> same bad link on day one.

---

## 6. Orphaned commitments

Said in a meeting, never became a ticket.

Every mined action item is checked against Jira. Anything without a match is either
a new ticket or a deliberate decision not to track it — and the decision gets said
out loud, not assumed.

Watch for commitments made *by* other people to the operator. Those get tracked as
dependencies with a name attached, because they are the raw material for "blocked
and on whom."

---

## 7. Self-blocking

The operator is the blocker on someone else's board.

Sweep watched boards for items blocked, awaiting review, or with an unanswered
comment where the operator is the one who owes something. These rarely appear on
the operator's own board, which is exactly why they rot.

> Unanswered comments and unmade introductions across three onboarding boards all
> traced back to one queue.

---

## 8. Stale parents

A parent item so overdue it makes its children's dates meaningless.

Check epics and phase parents against their children. A phase epic a quarter overdue
signals that nobody believes any date underneath it.

> A phase epic still open with a due date ten weeks in the past, with active
> children carrying dates as if it meant something.

Resolution is binary: close the parent, or give it an honest new date.

---

## 9. Calendar collisions

Double-bookings, and meetings sitting on top of higher-value ones.

Scan the cadence window for overlaps. Report with a recommendation on which to drop,
including whether the operator is actually required at each — an attendance list
that says "all sales personnel" is not a claim on a delivery manager's Wednesday.

Also flag recurring meetings the operator has decided to skip but never declined.
A decision that lives only in someone's head is invisible to everyone reading their
calendar.

---

## Reporting

Lead with what fired, ordered by consequence, not by check number. Each finding gets
the evidence, the consequence, and a recommendation.

State when checks ran clean. "Nothing self-blocking this week" is information, and
its absence makes the operator wonder whether the check ran at all.
