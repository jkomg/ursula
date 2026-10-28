# Ursula on your own machine (T3, Claude Code, Codex)

The desktop package is the only place today where the rails can run: the safety hooks,
the call ledger and the LiteLLM antagonist. Which of them run depends on the agent:

| Agent on your machine | Hooks and ledger | Antagonist |
|---|---|---|
| Claude Code | Yes, from `.claude/settings.json` | Yes |
| T3 with Claude as the provider | Yes. Seen blocking a key read, 2026-10-28 | Yes |
| Codex, or T3 with Codex | **No.** Codex does not read `.claude/settings.json` | Yes |

Under Codex the guards are absent. The receipt gate and the antagonist still run,
and a check-in has an empty ledger, so its close-out reports it partial rather than
verified. Prefer Claude as primary for check-ins. claude.ai and ChatGPT web chats run
the same procedure but cannot run hooks or reach a LiteLLM gateway, so there the
antagonist is recorded as pending (`reference/delegation.md`).

## Install or update

1. Install Python 3.8 or newer. On Windows, the `python3` that ships with Windows is
   only a Microsoft Store shortcut and does not count. Install from python.org or
   with `winget install Python.Python.3.12`. You also need Git for Windows, which
   provides `bash`.
2. Unzip `ursula-desktop-<version>.zip` somewhere you keep work, such as
   `Documents\ursula`. To update, unzip the newer one over the same folder. Your
   `ursula-project.json`, `ursula-local.json` and private state are not in the zip, so
   they are kept.
3. Open the folder in T3, Claude Code or Codex.
4. Run `bash bin/rails-check`. Every line should read `ok`, apart from the LiteLLM line
   until step 5. If anything says `FAIL`, stop and fix it first: that rail is not
   protecting you.
5. If your organization gives you a LiteLLM key, store it yourself. The prompt hides
   what you type, and the key never appears in a chat:

   | System | Command |
   |---|---|
   | Windows | `py -3 bin\litellm store`, or without the `py` launcher, `& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" bin\litellm store` in PowerShell. Paste with right-click: in a classic console, Ctrl+V types a control character, and the store refuses it |
   | Mac | `security add-generic-password -s ursula-litellm -a "$USER" -w` |

   Then run `py -3 bin\litellm check` (Mac: `python3 bin/litellm check`). It should say `"key": "accepted"`. Use
   `LITELLM_BASE_URL` if your gateway is not the Mirantis one. In T3 you can add the
   gateway as a provider instead; setup records whichever route you verify.
6. New setup: say "Set up Ursula". Existing setup: say "Ursula, check my setup after the
   update". It reruns the organization and agent questions, including which Claude,
   ChatGPT and LiteLLM accounts you have and which reviews.

## What each rail does

| Rail | Stops |
|---|---|
| `guard-secrets` | A Bash or PowerShell command reading the LiteLLM key |
| `guard-actions` | Any connector write during a check-in except a message to yourself |
| `guard-ledger`, `ledger-log` | Editing the hash-chained record of what a check-in actually called |
| receipt gate (`scripts/verify_receipts.py`) | A write whose quoted source does not exist |
| antagonist (`reference/delegation.md`) | A write that does not follow from its source, held for you to decide |

The hooks are guard rails against accidents and against text in a note talking the
agent into something. They are not a security boundary: anything running as you can
still read your files.
