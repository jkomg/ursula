# Building and releasing

Ursula runs in claude.ai. Nothing is installed on the machine where the repo lives, so
"installing" is building a zip and uploading it. `bin/install.sh` does the building.

## Why a script, and why not a local install

The loop is edit here → build → upload in claude.ai → run a dry-run → bring the
findings back. It is slow, and the slowest failure is uploading a bundle that was
broken before it left: a renamed reference file, an over-long description, a copy with
nobody sure which commit it came from. The script catches those locally, in seconds.

It does **not** copy the skill into `~/.claude/skills/` or any other local skills
directory. A copy there would run in Claude Code, which has no artifact database and
none of the connectors (`config/schema.md`), and would give a run that looks like it
worked. That path is not built; do not add it without building the rest.

## Use

```bash
bin/install.sh            # checks, then writes dist/ursula-<version>.zip
bin/install.sh --check    # checks only, writes nothing
bin/install.sh --out ~/Desktop
```

Then in claude.ai: Settings → Capabilities → Skills, upload the zip, replacing the
previous Ursula. Start a fresh chat and ask which version is running; it reads the
`VERSION` file in the bundle and should name the version the script printed. If it
names an older one, the upload did not replace the previous copy.

## What it checks

| Check | Fails when | Why |
|---|---|---|
| Frontmatter | `name` is not `ursula`, or the description is empty or over 1024 characters | claude.ai rejects these at upload, which is a slow place to learn it |
| Length | SKILL.md over about 500 lines (warning only) | Detail belongs in `reference/` |
| References | A backticked `.md`, `.html`, `.yaml` or `.sh` path in the docs does not exist | A missing reference file is how a run silently skips a check |
| Packs | A pack in the index table in `reference/analysis-checks.md` has no file | Same, for a whole pack |
| Secrets | A Slack, Atlassian or AWS token pattern, or a private key, is in a shipped file | The zip is handed to other people |
| Version | Never fails; warns when uncommitted changes are included | The version becomes `<date>-<sha>-dirty` so nobody mistakes it for a commit |

The reference check was shown to fail: pointing SKILL.md at a misspelled reference file name (minning for mining) produced `FAIL referenced but missing` and no zip. Paths like
`config/jira` are skipped on purpose — they are artifact-database documents, not files.

## What goes in the zip

One top-level folder, `ursula/`, holding `SKILL.md`, `INSTALL.md`, `README.md`,
`reference/`, `docs/`, `config/`, `artifact/`, `test/` and a generated `VERSION`.
`CLAUDE.md`, `bin/` and `dist/` stay out: they are for maintaining the repo, not for
running the skill.

The script refuses to overwrite an existing zip of the same version. Building twice
from one commit means nothing changed, or it means uncommitted edits went in both
times — either way, look before replacing.

## Assumptions to confirm

Written without watching an upload, so these are the first things to check if the
upload fails:

- claude.ai's skill upload takes a zip with one folder containing `SKILL.md`. If it
  wants `SKILL.md` at the zip root instead, change the `zip` line in the script to run
  inside `$stage/$NAME`.
- The claude.ai menu path above is the one seen at the time of writing and may move.

Record what the upload actually did in `test/golden-week.md`.
