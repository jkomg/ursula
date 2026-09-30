# Building and releasing

Ursula runs in Claude or ChatGPT/Codex. Nothing is installed by the build script, so
"installing" is building a zip and uploading it. `bin/install.sh` does the building.

## Why a script, and why not a local install

The loop is edit here → build → upload in claude.ai → run a dry-run → bring the
findings back. It is slow, and the slowest failure is uploading a bundle that was
broken before it left: a renamed reference file, an over-long description, a copy with
nobody sure which commit it came from. The script catches those locally, in seconds.

It does **not** copy the skill into a local skills directory. Installation and live
connector verification are separate from packaging. The OpenAI adapter uses private
JSON state or an explicit export rather than Claude's database (`docs/chatgpt.md`).

## Use

```bash
bin/install.sh            # checks, then writes dist/ursula-<version>.zip
bin/install.sh --check    # checks only, writes nothing
bin/install.sh --target openai  # ChatGPT/Codex bundle
bin/install.sh --target all     # both bundles
bin/install.sh --out ~/Desktop/ursula-bundles  # creates missing output directories
```

Then in claude.ai: Settings → Capabilities → Skills, upload the zip, replacing the
previous Ursula. Start a fresh chat and ask which version is running; it reads the
`VERSION` file in the bundle and should name the version the script printed. If it
names an older one, the upload did not replace the previous copy. For the OpenAI
bundle, follow `docs/chatgpt.md`; do not upload it as a second Claude installation.

## OpenAI installation details for maintainers

The operator-facing guide is `docs/chatgpt.md`; users do not need build commands.
For local Codex discovery, extract the OpenAI bundle's `ursula/` folder into
`~/.agents/skills/` for user scope, or `.agents/skills/` in the intended repository.
On Windows, use the user's home folder for the user-scoped location. Install one
copy to avoid duplicate skill names, then invoke `$ursula` in a fresh chat.
Verify the installation method in the target app on Windows or Mac. For ChatGPT
desktop, use its supported skill installation flow; web/mobile distribution needs
a plugin, which this standalone bundle does not provide. See the
[official skills guide](https://learn.chatgpt.com/docs/build-skills).

The packaging script requires Bash and the `zip`/`unzip` utilities. Windows
maintainers need an environment providing those tools, such as WSL or Git Bash
with the utilities available. Operators can receive the finished zip instead.

The renderer has tests in `test/test_snapshot.py`. Run them from the repo root with:

```bash
python3 -m unittest discover -s test
```

Not `python3 -m unittest test/test_snapshot.py`: the `test` directory shadows the
standard library's `test` package, so that form fails to import and looks like a
broken test rather than a wrong command.

For the portable board, use Python 3 to run `scripts/render_snapshot.py` with an
export path and `--out` pointing to the agreed board file. Use actual paths on the
operator's computer, quoted if they contain spaces. For example on Mac:

```bash
python3 scripts/render_snapshot.py /private/ursula/export.json --out /private/ursula/board.html
```

On Windows, use the available Python 3 command and Windows file paths. Keep both
the export and output outside the skill package and repository. Ordinary users
should receive the board file or a written review, without running the helper.

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
`reference/`, `docs/`, `config/`, `artifact/`, `test/`, `scripts/`, `agents/` and
generated `VERSION` and `HOST` files. Claude builds retain the original
`ursula-<version>.zip` name; OpenAI builds use `ursula-openai-<version>.zip`.
The shared resources ship in both; `HOST` identifies the intended runtime.
`CLAUDE.md`, `AGENTS.md`, `bin/` and `dist/` stay out: they are for maintaining the repo, not for
running the skill.

The script refuses to overwrite an existing zip of the same version. Building twice
from one commit means nothing changed, or it means uncommitted edits went in both
times — either way, look before replacing. With `--target all`, both destinations
are checked before either bundle is written. Bytecode caches are omitted and detected
secret values are never printed.

## Assumptions to confirm

Written without watching an upload, so these are the first things to check if the
upload fails:

- claude.ai's skill upload takes a zip with one folder containing `SKILL.md`. If it
  wants `SKILL.md` at the zip root instead, change the `zip` line in the script to run
  inside `$stage/$NAME`.
- The claude.ai menu path above is the one seen at the time of writing and may move.

Record what the upload actually did in `test/golden-week.md`.
