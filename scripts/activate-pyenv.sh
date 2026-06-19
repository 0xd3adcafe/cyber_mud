#!/usr/bin/env bash
export PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
if [[ -d "$PYENV_ROOT/bin" ]]; then
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init - bash 2>/dev/null)" || true
  eval "$(pyenv virtualenv-init - 2>/dev/null)" || true
fi