from __future__ import annotations

from entities.corpse import Corpse
from entities.player import Player
from world.mature import is_mature
from world.mature_voice import mature_combat_line, resolve_mature_combat_voice


def is_gore_worthy(damage: int, npc_max_hp: int) -> bool:
    return damage >= max(12, npc_max_hp // 2)


def gore_crit_line(player: Player, locale: str, *, target: str, damage: str) -> str | None:
    voice = resolve_mature_combat_voice(player)
    return mature_combat_line(locale, "crit", voice=voice, target=target, damage=damage)


def gore_kill_line(player: Player, locale: str, *, target: str) -> str | None:
    voice = resolve_mature_combat_voice(player)
    return mature_combat_line(locale, "kill", voice=voice, target=target)


def gore_corpse_lines(player: Player, locale: str, *, name: str) -> list[str]:
    voice = resolve_mature_combat_voice(player)
    line = mature_combat_line(locale, "corpse", voice=voice, name=name)
    return [line] if line else []


def maybe_gore_crit(player: Player, locale: str, *, target: str, damage: int, npc_max_hp: int) -> str | None:
    if not is_mature(player) or not is_gore_worthy(damage, npc_max_hp):
        return None
    return gore_crit_line(player, locale, target=target, damage=str(damage))


def maybe_gore_kill(player: Player, locale: str, *, target: str) -> str | None:
    if not is_mature(player):
        return None
    return gore_kill_line(player, locale, target=target)


def maybe_gore_corpse(player: Player, locale: str, corpse: Corpse, state) -> list[str]:
    if not is_mature(player) or corpse.player_name:
        return []
    from world.corpses import corpse_label

    label = corpse_label(state, corpse, locale)
    return gore_corpse_lines(player, locale, name=label)