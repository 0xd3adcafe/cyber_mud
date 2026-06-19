from __future__ import annotations


def matches_name(target: str, *candidates: str) -> bool:
    needle = target.strip().lower()
    if not needle:
        return False
    for candidate in candidates:
        if not candidate:
            continue
        c = candidate.strip().lower()
        if needle == c or needle in c.split():
            return True
    return False