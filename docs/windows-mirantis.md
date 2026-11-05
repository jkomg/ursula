# Windows: Mirantis-only setup

Use the portable Ursula skill from the `always-on` branch. Keep the machine's
approved Windows, WSL and security configuration; setup must inspect it before
installing tools. The skill does not require T3 or a local GPU.

## Update an existing checkout

From its folder in PowerShell:

```powershell
git status --short
git fetch origin
git switch always-on
git pull --ff-only origin always-on
```

If there are local edits or a diverged branch, stop and merge deliberately. Do not
reset, clean or overwrite user configuration. Updating Git does not update a skill
already uploaded to a web host: rebuild/reinstall that copy and start a fresh chat.
Packaging uses Bash, zip and unzip; use an existing approved WSL/Git Bash environment
with those tools, or receive a built ZIP. No WSL is needed for a chat-only ZIP setup.

## Start setup

Give the agent this prompt with the skill files:

> Configure Ursula for this Mirantis-only Windows machine. Read SKILL.md and
> reference/organization-profiles.md first. Inspect existing host/tool setup and
> preserve its particular configuration. Use only verified Mirantis accounts and
> connectors. Ask which approved Claude, ChatGPT/Codex or Gemini sources I want.
> Prefer verified local Ollama when useful and supported; otherwise use approved
> Mirantis hosted models. Mirantis LiteLLM is optional and requires explicit setup.
> Never use IREN or personal accounts. Start in dry-run, verify actual capabilities,
> and report missing prerequisites rather than claiming installation succeeded.

Record profile `mirantis` and organization `mirantis` in the project policy. Select
only the agent sources actually approved and available; choose primary and reviewer
from different provider families. Leave `allow_mirantis_litellm` false unless that
service is explicitly configured. It requires separate credential provisioning via
approved secret storage; never paste credentials into chat or the repository.

In T3, enable verified Mirantis providers and recommend disabling unrelated ones.
Keep local OpenCode only when its explicit model/backend is verified as local.
Do not auto-change global provider settings used by other sessions. In web hosts,
attach the policy or put it in project instructions: local files aren't automatically
visible. Confirm which account and workspace is actually signed in.

Optional helper check from the project folder, with Python 3.11+:

```powershell
py -3 scripts/project_policy.py ursula-project.json --profile mirantis
```

This validates declared routing, not login or live access. Keep private state outside
Git and separate from any other organization's state. Live Windows host installation,
identity verification and connector access must be checked on the target machine.
