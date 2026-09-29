# Pack: service-delivery

For an operator who onboards people onto per-person boards cloned from templates, and
who arranges access for them. Enable it with `service-delivery` in
`config/packs.enabled`.

The golden-week fixture assumes this pack is enabled. Two of its three hardest findings
come from here.

## Config

None beyond the core. It reads the owned, watched and excluded projects already in
`config/jira`. The `excluded` list matters more with this pack on: it is where the
templates live.

## Passes

- **Pass 2** — when reconciling an access item, read the ticket description, not just
  the title. Capability confusion hides in the gap between the two.
- **Pass 3** — the checks below, after the core set.

## Checks

| Slug | Check | Proven in a test run |
|---|---|---|
| `capability-confusion` | An access grant believed to do something it does not | Not yet |
| `template-propagation` | A fix applied to clones while the template stays broken | Not yet |

---

### `capability-confusion`

Someone believes an access grant does something it does not.

Read the actual description of an access ticket rather than its title. Grants that
sound equivalent usually are not.

> "I have access, I can get in through the proxy" — but the open items were a
> break-glass key and a vault decryption key. The proxy is the everyday path.
> Break-glass exists precisely for when the everyday path is the broken thing, and
> without the vault key the tooling cannot reach the fleet at all.

Especially important when the work depends on deliberately breaking something.

When it fires, cross-reference the tickets on both sides and say on each that they are
different grants (`reference/jira-conventions.md`, "Cross-reference explicitly").

---

### `template-propagation`

A fix applied to live instances while the source stays broken.

Whenever a correction touches anything cloned from a template, search the excluded
template projects for the same item. Excluded means not scanned for work — it does
not mean invisible.

> Three per-person onboarding boards had a card with a bad training link. Fixing
> those three leaves two template boards untouched, so the next hire inherits the
> same bad link on day one.

Match on the card's title and the offending content (the link, the name, the date),
not the title alone: a template card is often retitled once cloned.
