from __future__ import annotations

from shared.i18n import t
from world.world import Room

INFRA_TAGS = frozenset({"power_grid", "traffic", "surveillance", "steam"})


def room_infra_tags(room: Room | None) -> list[str]:
    if room is None:
        return []
    return [tag for tag in room.tags if tag in INFRA_TAGS]


def infrastructure_lines(room: Room | None, locale: str, *, mode: str = "look") -> list[str]:
    tags = room_infra_tags(room)
    if not tags:
        return []
    lines: list[str] = []
    for tag in tags:
        key = f"ctos.infra.{tag}.{mode}"
        line = t(locale, key)
        if line != key:
            lines.append(line)
    return lines