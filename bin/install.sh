#!/usr/bin/env bash
# Build Ursula skill bundles for Claude or ChatGPT/Codex.
#
# "Install" means package, not configure: check the skill, stamp its version, and
# write host-labelled zips. Nothing is copied into a local skills directory;
# see docs/release.md and docs/chatgpt.md for the separate runtime setup.
#
#   bin/install.sh              build dist/ursula-<version>.zip
#   bin/install.sh --check      run the checks only, write nothing
#   bin/install.sh --out DIR    write the zip into DIR instead of dist/
#   bin/install.sh --target openai  build the ChatGPT/Codex bundle
#   bin/install.sh --target desktop build the desktop workspace (T3/Claude Code/Codex):
#                                   the skill plus hooks, rails-check and bin/litellm
#   bin/install.sh --target all     build all three
#
# Exit status is non-zero if any check fails; no zip is written in that case.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="ursula"
OUT="$ROOT/dist"
CHECK_ONLY=0
TARGET=claude

while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK_ONLY=1; shift ;;
    --out)   OUT="${2:?--out needs a directory}"; shift 2 ;;
    --target) TARGET="${2:?--target needs claude, openai, desktop or all}"; shift 2 ;;
    -h|--help) sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
case "$TARGET" in claude|openai|desktop|all) ;; *) echo "invalid target: $TARGET" >&2; exit 2 ;; esac
# Resolve relative output paths against the caller, before changing into the repo.
case "$OUT" in /*|[A-Za-z]:[/\\]*) ;; *) OUT="$PWD/$OUT" ;; esac   # C:/ is absolute too

# What ships. Everything the skill reads at run time, plus the operator's install
# page. CLAUDE.md, bin/ and dist/ are for maintaining the repo and stay out.
SHIP=(SKILL.md INSTALL.md README.md reference docs config artifact test scripts agents)
# The desktop workspace adds the rails. Its AGENTS.md/CLAUDE.md are operator instructions
# from desktop/, not this repo's maintainer files (which say "do not run Ursula here").
DESKTOP_BIN=(bin/run-hook bin/rails-check bin/guard-secrets bin/guard-actions bin/guard-ledger bin/ledger-log bin/litellm)
DESKTOP_EXTRA=(.claude/settings.json desktop/AGENTS.md desktop/CLAUDE.md)

cd "$ROOT"
fail=0
say()  { printf '%s\n' "$*"; }
bad()  { printf 'FAIL  %s\n' "$*"; fail=1; }
ok()   { printf 'ok    %s\n' "$*"; }
warn() { printf 'warn  %s\n' "$*"; }

# 1. Frontmatter. claude.ai reads name and description from it; a missing or
#    over-long description is rejected at upload, which is a slow place to find out.
fm_name="$(awk '/^---$/{n++; next} n==1 && /^name:/{sub(/^name: */,""); print; exit}' SKILL.md)"
fm_desc="$(awk '/^---$/{n++; next} n==1 && /^description:/{sub(/^description: */,""); print; exit}' SKILL.md)"
if [ "$fm_name" = "$NAME" ]; then ok "SKILL.md name is '$NAME'"; else bad "SKILL.md name is '$fm_name', expected '$NAME'"; fi
dlen=${#fm_desc}
if [ "$dlen" -eq 0 ]; then bad "SKILL.md has no description"
elif [ "$dlen" -gt 1024 ]; then bad "SKILL.md description is $dlen characters; the limit is 1024"
else ok "SKILL.md description is $dlen characters (limit 1024)"; fi

# 2. SKILL.md length. CLAUDE.md sets a budget of about 500 lines; past it, detail
#    belongs in reference/.
lines=$(wc -l < SKILL.md | tr -d ' ')
if [ "$lines" -gt 500 ]; then warn "SKILL.md is $lines lines; budget is about 500"; else ok "SKILL.md is $lines lines"; fi

# 3. Every file path the docs mention exists. A reference to a file that was renamed
#    or never written is how a run silently skips a check: Claude looks, finds
#    nothing, and carries on. Only paths with a file extension count: `config/jira`
#    and the like are artifact-database documents, not files. Placeholders like
#    <pack> are skipped.
missing=0
while IFS= read -r ref; do
  case "$ref" in *'<'*|*'*'*) continue ;; esac
  [ -e "$ref" ] || { bad "referenced but missing: $ref"; missing=1; }
done < <(grep -rhoE '`(reference|docs|config|artifact|test|bin|scripts|agents)/[A-Za-z0-9_/<>*-]+\.(md|html|yaml|sh|py)`' \
           SKILL.md INSTALL.md README.md reference docs config test 2>/dev/null \
         | tr -d '`' | sed 's/[.,;:]$//' | sort -u)
[ "$missing" -eq 0 ] && ok "every referenced path exists"

# 4. Every enabled-able pack named in the checks index has its file.
while IFS= read -r pack; do
  [ -f "reference/packs/$pack.md" ] || bad "pack '$pack' is listed but reference/packs/$pack.md is missing"
done < <(grep -oE '^\| `[a-z-]+` \| `reference/packs/' reference/analysis-checks.md | sed -E 's/^\| `([a-z-]+)`.*/\1/')
ok "pack files present: $(ls reference/packs | sed 's/\.md$//' | tr '\n' ' ')"

# 5. No secrets. config/schema.md forbids them anywhere shared, and a zip is shared.
#    Report where, never what: the match itself must not end up in a terminal log.
secret_hits="$(grep -rnIE '(xox[abp]-[A-Za-z0-9-]+|ATATT[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16})' "${SHIP[@]}" 2>/dev/null | cut -d: -f1,2 || true)"
if [ -n "$secret_hits" ]; then
  bad "a token or private-key pattern is in the shipped files (value not shown):"
  printf '      %s\n' $secret_hits
else ok "no token or key patterns in shipped files"; fi

# 5b. Desktop rails present, and wired through the launcher rather than a bare python3,
#     which on Windows is often the Store stub and made every hook fail silently.
for f in "${DESKTOP_BIN[@]}" "${DESKTOP_EXTRA[@]}"; do [ -f "$f" ] || bad "desktop file missing: $f"; done
if grep -q '"python3 ' .claude/settings.json; then bad ".claude/settings.json calls python3 directly; use bin/run-hook"
else ok "desktop rails present; hooks go through bin/run-hook"; fi

# 6. Version. The zip is stamped with the commit it came from, so a claude.ai session
#    can say which upload it is running. -dirty means uncommitted changes went in.
if git rev-parse --git-dir >/dev/null 2>&1; then
  sha="$(git rev-parse --short HEAD)"
  if [ -n "$(git status --porcelain -- "${SHIP[@]}" "${DESKTOP_BIN[@]}" "${DESKTOP_EXTRA[@]}" bin/install.sh)" ]; then
    version="$(date +%Y%m%d)-$sha-dirty"
    warn "uncommitted changes in shipped files; version will be $version"
  else
    version="$(date +%Y%m%d)-$sha"
    ok "clean tree; version $version"
  fi
else
  version="$(date +%Y%m%d)-nogit"
  warn "not a git checkout; version $version"
fi

if [ "$fail" -ne 0 ]; then say ""; say "Checks failed. No bundle written."; exit 1; fi
if [ "$CHECK_ONLY" -eq 1 ]; then say ""; say "Checks passed (--check: nothing written)."; exit 0; fi

# Build. The zip holds one top-level folder named after the skill, with SKILL.md
# directly inside it: the layout claude.ai's skill upload expects.
stage="$(mktemp -d "${TMPDIR:-/tmp}/ursula-build.XXXXXX")"
trap 'rm -rf "$stage"' EXIT
mkdir -p "$stage/$NAME"
for p in "${SHIP[@]}"; do cp -R "$p" "$stage/$NAME/"; done
find "$stage" -name .DS_Store -delete
find "$stage" -type d -name __pycache__ -prune -exec rm -rf {} +
cat > "$stage/$NAME/VERSION" <<EOF
$version
built $(date -u +%Y-%m-%dT%H:%M:%SZ) from $(git remote get-url origin 2>/dev/null || echo "a local checkout")
EOF

targets=("$TARGET")
[ "$TARGET" != all ] || targets=(claude openai desktop)
suffix_for() { case "$1" in openai) echo "-openai" ;; desktop) echo "-desktop" ;; *) echo "" ;; esac; }
# make_zip DIR ZIP: zip DIR/$NAME. Git Bash on Windows has no zip(1), so fall back to
# Python's zipfile, keeping executable bits so bin/ scripts still run after unzip.
make_zip() {
  if command -v zip >/dev/null 2>&1; then ( cd "$1" && zip -qr -X "$2" "$NAME" ); return; fi
  bash "$ROOT/bin/run-hook" --which >/dev/null 2>&1 || { say "no zip and no Python; cannot build"; exit 1; }
  local out="$2"
  command -v cygpath >/dev/null 2>&1 && out="$(cygpath -w "$2")"   # Windows Python cannot open /tmp/...
  ( cd "$1" && bash "$ROOT/bin/run-hook" --python - "$out" "$NAME" <<'PY'
import os, sys, zipfile
out, top = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for base, dirs, files in os.walk(top):
        dirs.sort()
        for name in sorted(files):
            path = os.path.join(base, name)
            info = zipfile.ZipInfo(path.replace(os.sep, "/"), (1980, 1, 1, 0, 0, 0))
            mode = 0o755 if path.replace(os.sep, "/").split("/")[1:2] == ["bin"] else 0o644
            info.external_attr = (0o100000 | mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(path, "rb") as f:
                z.writestr(info, f.read())
PY
  )
}
mkdir -p "$OUT"
# Check every destination before writing the first bundle.
for host in "${targets[@]}"; do
  suffix="$(suffix_for "$host")"
  zip_path="$OUT/$NAME$suffix-$version.zip"
  if [ -e "$zip_path" ]; then
    say "exists, not overwriting: $zip_path"
    exit 1
  fi
done
for host in "${targets[@]}"; do
  suffix="$(suffix_for "$host")"
  zip_path="$OUT/$NAME$suffix-$version.zip"
  if [ "$host" = desktop ]; then
    # The skill plus the rails, with operator instructions in place of the maintainer files.
    dstage="$stage/desktop-build"; rm -rf "$dstage"; mkdir -p "$dstage"
    cp -R "$stage/$NAME" "$dstage/$NAME"
    mkdir -p "$dstage/$NAME/bin" "$dstage/$NAME/.claude"
    for f in "${DESKTOP_BIN[@]}"; do cp "$f" "$dstage/$NAME/bin/"; done
    cp .claude/settings.json "$dstage/$NAME/.claude/"
    cp desktop/AGENTS.md desktop/CLAUDE.md "$dstage/$NAME/"
    printf '%s\n' desktop > "$dstage/$NAME/HOST"
    make_zip "$dstage" "$zip_path"
  else
    printf '%s\n' "$host" > "$stage/$NAME/HOST"
    make_zip "$stage" "$zip_path"
  fi
  files=$(unzip -Z1 "$zip_path" | grep -vc '/$')
  say "Built $zip_path ($files files)"
done
say "Claude: upload the Claude zip through the claude.ai Skills menu."
say "ChatGPT/Codex: see docs/chatgpt.md for installing the OpenAI bundle."
say "Desktop (T3/Claude Code/Codex): see docs/desktop.md; unzip over the existing folder to update."
say "Start a fresh chat and ask which Ursula version is running; expect $version."
