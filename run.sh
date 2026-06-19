#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
# shellcheck source=scripts/activate-pyenv.sh
source "$ROOT/scripts/activate-pyenv.sh"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

if command -v pyenv >/dev/null 2>&1 && pyenv which python >/dev/null 2>&1; then
  PYTHON="$(pyenv which python)"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi

DEV=0
CLIENT=0
for arg in "$@"; do
  case "$arg" in
    --dev) DEV=1 ;;
    --client) CLIENT=1 ;;
  esac
done

if [[ "$CLIENT" -eq 1 ]]; then
  exec "$PYTHON" -m client "$@"
fi

if [[ "$DEV" -eq 1 ]]; then
  exec "$PYTHON" -m server.main --dev "$@"
fi

exec "$PYTHON" -m server.main "$@"