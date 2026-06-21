#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
# shellcheck source=scripts/activate-pyenv.sh
source "$ROOT/scripts/activate-pyenv.sh"

PY_BASE="3.13.12"
VENV_NAME="cyber-mud-3.13.12"

if command -v pyenv >/dev/null 2>&1; then
  if ! pyenv versions --bare | grep -qx "$PY_BASE"; then
    if python3 --version 2>/dev/null | grep -q "3.13"; then
      pyenv virtualenv "$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')" "$VENV_NAME" 2>/dev/null || \
        pyenv virtualenv "$PY_BASE" "$VENV_NAME" 2>/dev/null || true
    else
      echo "需要 Python 3.13；請安裝 pyenv 後執行: pyenv install $PY_BASE"
      exit 1
    fi
  fi
  if ! pyenv versions --bare | grep -qx "$VENV_NAME"; then
    pyenv virtualenv "$PY_BASE" "$VENV_NAME"
  fi
  pyenv local "$VENV_NAME"
fi

if command -v pyenv >/dev/null 2>&1 && pyenv which python >/dev/null 2>&1; then
  PYTHON="$(pyenv which python)"
else
  if [[ ! -d "$ROOT/.venv" ]]; then
    python3 -m venv "$ROOT/.venv" || {
      echo "無法建立 venv。請安裝 python3-venv 或 pyenv 後重試。"
      exit 1
    }
  fi
  PYTHON="$ROOT/.venv/bin/python"
fi

if ! "$PYTHON" -m pip --version >/dev/null 2>&1; then
  echo "Bootstrapping pip (ensurepip unavailable in this Python build)..."
  GET_PIP="$(mktemp)"
  curl -fsSL https://bootstrap.pypa.io/get-pip.py -o "$GET_PIP"
  "$PYTHON" "$GET_PIP"
  rm -f "$GET_PIP"
fi

"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r requirements.txt
if [[ -f "$ROOT/.gitmodules" ]] && grep -q 'data/mature' "$ROOT/.gitmodules" 2>/dev/null; then
  if timeout 15 git submodule update --init data/mature 2>/dev/null; then
    echo "✓ mature content submodule initialized"
  else
    echo "⚠ data/mature submodule skipped (no access or network)"
  fi
fi
echo "✓ cyber_mud 環境就緒。執行 ./run.sh 或 ./run.sh --client"