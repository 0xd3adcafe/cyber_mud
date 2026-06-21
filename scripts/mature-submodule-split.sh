#!/usr/bin/env bash
# Publish data/mature to private cyber_mud_mature and wire submodule (M.18).
# Run from repo root after gh auth works. Requires: git, gh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MATURE_DIR="$ROOT/data/mature"
PRIVATE_REPO="${CYBER_MUD_MATURE_REPO:-0xd3adcafe/cyber_mud_mature}"

if [[ ! -f "$MATURE_DIR/locale/mature_en.yaml" ]]; then
  echo "error: $MATURE_DIR pack missing" >&2
  exit 1
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

cp -a "$MATURE_DIR/." "$WORK/"
cp "$ROOT/data/mature/README.md" "$WORK/README.md" 2>/dev/null || true

cd "$WORK"
git init -b master
git add -A
git commit -m "feat: initial mature content pack"

if ! timeout 30 gh repo view "$PRIVATE_REPO" >/dev/null 2>&1; then
  timeout 60 gh repo create "$PRIVATE_REPO" --private --source=. --remote=origin --push
else
  git remote add origin "https://github.com/${PRIVATE_REPO}.git"
  git push -u origin master
fi

echo "Private repo ready: https://github.com/${PRIVATE_REPO}"
echo "Next (in cyber_mud): git rm -r --cached data/mature && git submodule add git@github.com:${PRIVATE_REPO}.git data/mature"
echo "Then run: scripts/mature-history-purge.sh"