from __future__ import annotations

import re
from typing import Any

from entities.player import Player

_HAS_ITEM_RE = re.compile(r"^has_item\(([^)]+)\)$", re.IGNORECASE)
_FACTION_RE = re.compile(r"^faction\(([^)]+)\)$", re.IGNORECASE)
_FLAG_RE = re.compile(r"^flag\(([^)]+)\)$", re.IGNORECASE)
_COMPARE_RE = re.compile(r"^(\w+)\s*(>=|<=|==|>|<)\s*(-?\d+)$", re.IGNORECASE)

_NUMERIC_ATTRS = frozenset(
    {
        "street_cred",
        "level",
        "reputation",
        "humanity",
        "body",
        "reflex",
        "tech",
        "cool",
        "intelligence",
        "wanted_level",
        "gold",
    }
)


def parse_locks(raw: dict[str, Any] | None) -> dict[str, str]:
    if not raw:
        return {}
    return {str(action): str(expr).strip() for action, expr in raw.items() if str(expr).strip()}


def _player_has_item(player: Player, item_id: str) -> bool:
    needle = item_id.strip()
    if not needle:
        return False
    if needle in player.inventory:
        return True
    if needle in player.home_stash:
        return True
    if any(equipped_id == needle for equipped_id in player.equipment.values()):
        return True
    if any(implant_id == needle for implant_id in player.cyberware.values()):
        return True
    return False


def _numeric_attr(player: Player, name: str) -> int | None:
    key = name.strip().lower()
    if key not in _NUMERIC_ATTRS:
        return None
    return int(getattr(player, key, 0))


def _compare(left: int, op: str, right: int) -> bool:
    if op == ">=":
        return left >= right
    if op == "<=":
        return left <= right
    if op == ">":
        return left > right
    if op == "<":
        return left < right
    return left == right


def evaluate_lock(expr: str, player: Player, state: Any = None) -> bool:
    text = expr.strip()
    if not text:
        return True

    match = _HAS_ITEM_RE.match(text)
    if match:
        return _player_has_item(player, match.group(1))

    match = _FACTION_RE.match(text)
    if match:
        return player.faction == match.group(1).strip()

    match = _FLAG_RE.match(text)
    if match:
        flag_key = match.group(1).strip()
        value = player.quest_flags.get(flag_key, "")
        return bool(value and value not in {"0", "false", "no"})

    match = _COMPARE_RE.match(text)
    if match:
        attr = _numeric_attr(player, match.group(1))
        if attr is None:
            return False
        return _compare(attr, match.group(2), int(match.group(3)))

    return False


def entity_locks(entity: Any) -> dict[str, str]:
    locks = getattr(entity, "locks", None)
    if isinstance(locks, dict):
        return locks
    return {}


def lock_allows(entity: Any, action: str, player: Player, state: Any = None) -> bool:
    rule = entity_locks(entity).get(action)
    if not rule:
        return True
    return evaluate_lock(rule, player, state)