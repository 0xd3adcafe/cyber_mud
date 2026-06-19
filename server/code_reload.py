from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CODE_PACKAGES: tuple[str, ...] = (
    "commands",
    "combat",
    "entities",
    "persistence",
    "shared",
    "world",
)

_SKIP_MODULES = frozenset(
    {
        "commands.registry",
        "commands.__init__",
    }
)


def iter_code_files() -> list[Path]:
    files: list[Path] = []
    for package in CODE_PACKAGES:
        base = ROOT / package
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            if path.is_file():
                files.append(path)
    return files


def snapshot_code_mtimes() -> dict[Path, float]:
    return {path: path.stat().st_mtime for path in iter_code_files()}


def _module_names_for_reload() -> list[str]:
    prefixes = tuple(f"{package}." for package in CODE_PACKAGES)
    names = [
        name
        for name in list(sys.modules)
        if name in CODE_PACKAGES or name.startswith(prefixes)
    ]
    names.sort(key=lambda name: name.count("."), reverse=True)
    return [name for name in names if name not in _SKIP_MODULES]


def reload_application_code() -> list[tuple[str, str]]:
    from commands.registry import _REGISTRY, register_builtin_commands

    _REGISTRY.clear()
    failures: list[tuple[str, str]] = []

    for name in _module_names_for_reload():
        module = sys.modules.get(name)
        if module is None:
            continue
        try:
            importlib.reload(module)
        except Exception as exc:
            failures.append((name, str(exc)))

    if not _REGISTRY:
        register_builtin_commands()
    return failures