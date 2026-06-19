#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
# shellcheck source=scripts/activate-pyenv.sh
source "$ROOT/scripts/activate-pyenv.sh"
VENV_PKGS="$ROOT/.venv/local/lib/python3.13/dist-packages"
if [[ -d "$VENV_PKGS" ]]; then
  export PYTHONPATH="$ROOT:$VENV_PKGS:${PYTHONPATH:-}"
else
  export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
fi
if command -v pyenv >/dev/null 2>&1 && pyenv which python >/dev/null 2>&1; then
  PYTHON="$(pyenv which python)"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi
exec "$PYTHON" -m admin "$@"