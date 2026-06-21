#!/usr/bin/env bash
# Remove mature plaintext paths from all git history (M.18). Destructive — coordinate before force push.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v git-filter-repo >/dev/null 2>&1; then
  echo "Install git-filter-repo first (pip install git-filter-repo or apt)." >&2
  exit 1
fi

PATHS=(
  data/locale/mature_en.yaml
  data/locale/mature_zh.yaml
  data/quests_mature.yaml
  data/braindances_mature.yaml
  data/romance.yaml
  data/mature/locale/mature_en.yaml
  data/mature/locale/mature_zh.yaml
  data/mature/quests_mature.yaml
  data/mature/braindances_mature.yaml
  data/mature/romance.yaml
  data/mature/README.md
)

ARGS=()
for p in "${PATHS[@]}"; do
  ARGS+=(--path "$p")
done

echo "This will rewrite history and remove mature plaintext from all commits."
echo "Paths: ${PATHS[*]}"
if [[ "${MATURE_PURGE_YES:-}" != "1" ]]; then
  read -r -p "Continue? [y/N] " ans
  [[ "$ans" == "y" || "$ans" == "Y" ]] || exit 0
fi

git filter-repo "${ARGS[@]}" --invert-paths --force

echo "Done. Run: git push --force-with-lease origin master"
echo "Delete and recreate any release tags that pointed at old commits."