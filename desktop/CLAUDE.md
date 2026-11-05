# Ursula desktop workspace

Read `AGENTS.md` in this folder first and follow it; it is the shared instruction
file for Claude Code, Codex and T3. In short: run `bash bin/rails-check`, read
`ursula-project.json`, then `SKILL.md`.

The hooks in `.claude/settings.json` run through `bin/run-hook`, which finds a real
Python and blocks the tool call if there is none. A denied call from one of them is
the guard working, not an error to route around.
