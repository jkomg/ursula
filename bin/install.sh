#!/usr/bin/env bash
# Build the Ursula skill bundle for upload to claude.ai.
#
# Ursula runs in claude.ai, not on this machine, so "install" means: check the skill
# is well formed, stamp it with the commit it came from, and write one zip that is
# uploaded through claude.ai's Skills menu and is also what gets handed to another
# operator. Nothing is copied into a local skills directory; see docs/release.md.
#
#   bin/install.sh              build dist/ursula-<version>.zip
#   bin/install.sh --check      run the checks only, write nothing
#   bin/install.sh --out DIR    write the zip into DIR instead of dist/
#
# Exit status is non-zero if any check fails; no zip is written in that case.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="ursula"
OUT="$ROOT/dist"
CHECK_ONLY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK_ONLY=1; shift ;;
    --out)   OUT="$(cd "${2:?--out needs a directory}" && pwd)"; shift 2 ;;
    -h|--help) sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

# What ships. Everything the skill reads at run time, plus the operator's install
# page. CLAUDE.md, bin/ and dist/ are for maintaining the repo and stay out.
SHIP=(SKILL.md INSTALL.md README.md reference docs config artifact test)

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
done < <(grep -rhoE '`(reference|docs|config|artifact|test|bin)/[A-Za-z0-9_/<>*-]+\.(md|html|yaml|sh)`' \
           SKILL.md INSTALL.md README.md reference docs config test 2>/dev/null \
         | tr -d '`' | sed 's/[.,;:]$//' | sort -u)
[ "$missing" -eq 0 ] && ok "every referenced path exists"

# 4. Every enabled-able pack named in the checks index has its file.
while IFS= read -r pack; do
  [ -f "reference/packs/$pack.md" ] || bad "pack '$pack' is listed but reference/packs/$pack.md is missing"
done < <(grep -oE '^\| `[a-z-]+` \| `reference/packs/' reference/analysis-checks.md | sed -E 's/^\| `([a-z-]+)`.*/\1/')
ok "pack files present: $(ls reference/packs | sed 's/\.md$//' | tr '\n' ' ')"

# 5. No secrets. config/schema.md forbids them anywhere shared, and a zip is shared.
if grep -rnIE '(xox[abp]-[A-Za-z0-9-]+|ATATT[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16})' "${SHIP[@]}" >/dev/null 2>&1; then
  bad "something that looks like a token or private key is in the shipped files:"
  grep -rnIE '(xox[abp]-[A-Za-z0-9-]+|ATATT[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16})' "${SHIP[@]}" | cut -c1-120
else ok "no token or key patterns in shipped files"; fi

# 6. Version. The zip is stamped with the commit it came from, so a claude.ai session
#    can say which upload it is running. -dirty means uncommitted changes went in.
if git rev-parse --git-dir >/dev/null 2>&1; then
  sha="$(git rev-parse --short HEAD)"
  if [ -n "$(git status --porcelain -- "${SHIP[@]}")" ]; then
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
cat > "$stage/$NAME/VERSION" <<EOF
$version
built $(date -u +%Y-%m-%dT%H:%M:%SZ) from $(git remote get-url origin 2>/dev/null || echo "a local checkout")
EOF

mkdir -p "$OUT"
zip_path="$OUT/$NAME-$version.zip"
if [ -e "$zip_path" ]; then
  say "exists, not overwriting: $zip_path"
  say "(same commit already built; commit again or remove the old zip yourself)"
  exit 1
fi
( cd "$stage" && zip -qr -X "$zip_path" "$NAME" )

files=$(unzip -Z1 "$zip_path" | grep -vc '/$')
say ""
say "Built $zip_path"
say "  $files files, $(du -h "$zip_path" | cut -f1 | tr -d ' ')"
say ""
say "Next: claude.ai → Settings → Capabilities → Skills → upload this zip, replacing"
say "the previous Ursula. Then start a new chat and ask \"which version of Ursula is this?\""
say "It should answer $version."
