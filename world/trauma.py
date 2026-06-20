from __future__ import annotations

import random

from entities.player import Player
from shared.i18n import t
from shared.mature_i18n import tm
from world.mature import is_mature
from world.status_effects import (
    EFFECT_BLEED,
    EFFECT_OVERHEAT,
    EFFECT_POISON,
    StatusEffectState,
    poison_tick_damage,
)


def player_status_state(player: Player) -> StatusEffectState:
    state = StatusEffectState()
    state.effects = dict(player.player_status)
    return state


def sync_player_status(player: Player, status: StatusEffectState) -> None:
    player.player_status = dict(status.effects)


def apply_player_bleed(player: Player, duration: int = 4) -> None:
    if not is_mature(player):
        return
    status = player_status_state(player)
    status.apply(EFFECT_BLEED, duration)
    sync_player_status(player, status)


def apply_player_poison(player: Player, duration: int = 4) -> None:
    status = player_status_state(player)
    status.apply(EFFECT_POISON, duration)
    sync_player_status(player, status)


def apply_player_overheat(player: Player, duration: int = 3) -> None:
    status = player_status_state(player)
    status.apply(EFFECT_OVERHEAT, duration)
    sync_player_status(player, status)


def maybe_bleed_on_hit(player: Player, damage: int) -> None:
    if not is_mature(player) or damage < 8:
        return
    apply_player_bleed(player, duration=3)


def maybe_poison_on_hit(player: Player, npc_id: str, damage: int, *, npc_faction: str = "") -> None:
    if damage < 4:
        return
    if npc_id != "thug" and npc_faction != "maelstrom":
        return
    if random.random() > 0.3:
        return
    apply_player_poison(player, duration=4)


def tick_player_status(player: Player, locale: str) -> list[str]:
    if not player.named or player.in_combat or not player.player_status:
        return []
    status = player_status_state(player)
    expired = status.tick()
    lines: list[str] = []
    if status.has(EFFECT_BLEED) and player.hp > 0:
        damage = max(1, player.body // 4)
        player.hp = max(0, player.hp - damage)
        key = f"trauma.bleed_{1 if damage <= 1 else 2}"
        line = tm(locale, key, damage=str(damage), hp=str(player.hp))
        if line != key:
            lines.append(line)
        else:
            lines.append(t(locale, "status.bleed_tick", damage=str(damage), hp=str(player.hp)))
    if status.has(EFFECT_POISON) and player.hp > 0:
        damage = poison_tick_damage(player.body)
        player.hp = max(0, player.hp - damage)
        lines.append(t(locale, "status.poison_tick", damage=str(damage), hp=str(player.hp)))
    if status.has(EFFECT_OVERHEAT):
        lines.append(t(locale, "status.overheat_active"))
    for effect in expired:
        if effect == EFFECT_BLEED:
            key = "trauma.bleed_stop"
            line = tm(locale, key)
            if line != key:
                lines.append(line)
            else:
                lines.append(t(locale, "status.bleed_stop"))
        elif effect == EFFECT_POISON:
            lines.append(t(locale, "status.poison_stop"))
        elif effect == EFFECT_OVERHEAT:
            lines.append(t(locale, "status.overheat_stop"))
    sync_player_status(player, status)
    return lines


def treat_trauma_at_ripperdoc(player: Player, room, locale: str) -> list[str]:
    if not is_mature(player) or not player.player_status:
        return []
    if room is None or "ripperdoc" not in room.tags:
        return []
    had_bleed = EFFECT_BLEED in player.player_status
    player.player_status.clear()
    if not had_bleed:
        return []
    key = "trauma.ripperdoc"
    line = tm(locale, key)
    return [line] if line != key else [t(locale, "trauma.ripperdoc_ok")]