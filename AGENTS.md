# Maintaining Ursula

Ursula is a reusable skill for Claude and ChatGPT/Codex, with shared cadence,
checks and config shapes. Read `SKILL.md` first. Runtime differences belong in
`reference/runtime.md`; do not fork the analysis instructions by provider.

Preserve existing operator edits. Keep the entrypoint under about 500 lines and
put detailed procedures in `reference/`. Keep config, personal data and credentials
out of bundles and Git. Preserve the prohibitions and calendar approval tiers.

The Claude live board requires its artifact runtime. The portable renderer produces
an explicitly dated snapshot, with no connector calls or write controls. Do not
claim a static export is live, or that Claude's board works in another host.

Run `bin/install.sh --target all --check` after edits. Check executable helpers
locally; this does not verify the cadence. Do not mock connectors or add CI that
claims to validate agent behaviour. Live acceptance requires configured connectors
and an operator's dry-run. Record changes and real findings in `test/golden-week.md`.

<!-- coding-harness review workflow -->
## Task and code review

Before accepting substantive task plans or delivering code, follow
[the review workflow](.review-harness/assets/adversarial-review.md). Preserve all
existing project checks, approval gates and credential rules. Use deterministic
checks and a bounded local reviewer first; Mirantis LiteLLM is limited to verified
Mirantis-authorized work. Personal/IREN work stays local or account-matched.
Record findings and fixes or rebuttals; at most two automatic repair/review rounds.
Unexecuted review remains pending. Model agreement does not establish correctness.
The portable packet helper is `.review-harness/scripts/review.py`; it sends nothing
until explicitly invoked with `send` after account and content verification.
<!-- end coding-harness review workflow -->
