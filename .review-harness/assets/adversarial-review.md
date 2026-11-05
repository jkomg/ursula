# Task and code review

Use this workflow before accepting a substantive task plan and before delivering
code. Keep existing project tests, approval gates and credential policies.

1. Read the project's instructions. Identify the organization and verify the active
   provider account. Folder names and CLI flags do not prove authorization.
2. Run deterministic checks first. Use one bounded local reviewer where available;
   verify its actual model. For Mirantis-authorized work, use Mirantis LiteLLM as
   the independent adversarial reviewer. For personal/IREN work, use local or
   account-matched review. Never silently route between organizations.
3. Prepare a short requirements file and select relevant source/evidence files.
   Include the candidate plan for task reviews, or code plus relevant tests for
   code reviews. Include prior findings and responses for a second round.
4. Inspect the packet before transmission. Path filters are not secret scanning;
   remove credentials and unrelated private information from ordinary source files.
5. Review the frozen packet. Record each finding's location, failure scenario,
   evidence and fix or reasoned rebuttal. Maximum two automatic review/repair rounds;
   unresolved findings go to the lead. Review is pending until actually executed.
6. Re-run project checks after fixes. Model agreement is not test evidence, approval,
   a receipt-verification gate, or permission to deploy. Reprepare after source edits.

## Commands

With the coding-harness skill installed, from your project directory:

```sh
python3 ~/.codex/skills/coding-harness/scripts/review.py prepare --scope mirantis --kind code --brief REVIEW-BRIEF.md --file src/example.py --file tests/test_example.py
```

Use `--kind task` with the proposed plan and its source receipts. Substitute your
actual paths; no file is collected automatically. The command prints a private
packet path outside the project. Read it, then check freshness:

```sh
python3 ~/.codex/skills/coding-harness/scripts/review.py check /absolute/packet.json
```

Only after verifying a Mirantis account and Mirantis-authorized content:

```sh
python3 ~/.codex/skills/coding-harness/scripts/review.py send /absolute/packet.json --provider-instance codex_mirantis --confirmed-mirantis-input
```

Sending requires the optional Token Factory app, its existing Mirantis credential,
and a known provider budget below the review threshold. `--runner` overrides the
installed app path. The CLI account flag is an assertion, not a login check.
MirCloud must use its Swamp vault and approval workflow; do not use this sender's
Keychain/environment credential route there. Its T3 review action is guidance only
until a vault-backed adapter is integrated through that project's workflow.

Without LiteLLM, supply the inspected packet to an authorized local/account-matched
reviewer and save its findings with the packet hash. This helper doesn't invoke
local agents or automatically enforce review across hosts. Native Windows uses
`python` and an explicit skill path; WSL/macOS use `python3`. No T3 is required.

## T3 and existing workflows

The manual **Review workflow** project action prints this guide. **Prepare review
(help)** lists packet options; it sends nothing. Ask the project agent: “Follow the
coding-harness task/code review workflow; prepare explicit evidence, run the
appropriate reviewer, resolve findings and run our existing checks.”

For persistent adoption, append a link to this workflow in your existing shared
agent instructions after checking project-specific rules. Do not replace AGENTS.md,
CLAUDE.md, CI or Makefiles. Skill-only users can prepare/check packets without Token
Factory or a cloud account. The optional sender needs Token Factory separately.

Reports and packets are private local files, not ledger records. Token Factory
stores only reported usage metadata. Selected-file hashes do not verify the whole
repository, dependencies, submodules or a test run. Files may change after checking;
review refers to the captured bytes, not a claim about current source or deployment.
