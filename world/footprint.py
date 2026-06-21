from __future__ import annotations

from entities.player import Player
from shared.i18n import t
from world.modifiers import period_for_room
from world.state import WorldState

FOOTPRINT_MAX = 100
FOOTPRINT_DECAY_PER_TICK = 1
CORPO_SCAN_FOOTPRINT = 3
CORPO_HACK_FOOTPRINT = 5
HIGH_FOOTPRINT_THRESHOLD = 60


def _footprint_amount(player: Player, amount: int) -> int:
    if amount <= 0:
        return 0
    if player.faction == "dedsec":
        return max(1, int(amount * 0.75)) if amount > 1 else amount
    return amount


def add_footprint(
    player: Player,
    amount: int,
    state: WorldState,
    locale: str,
    *,
    reason: str = "",
) -> list[str]:
    amount = _footprint_amount(player, amount)
    if amount <= 0:
        return []
    before = player.footprint
    player.footprint = min(FOOTPRINT_MAX, player.footprint + amount)
    if player.footprint == before:
        return []
    lines = [t(locale, "footprint.gain", amount=str(amount), total=str(player.footprint))]
    if before < HIGH_FOOTPRINT_THRESHOLD <= player.footprint:
        lines.append(t(locale, "footprint.high_warning"))
    return lines


def corpo_footprint_bonus(state: WorldState, room_id: str, base: int) -> int:
    room = state.world.room(room_id)
    if room and room.district == "corpo":
        return base + 2
    return base


def tick_footprint_decay_player(player: Player, state: WorldState) -> None:
    if player.footprint <= 0:
        return
    decay = FOOTPRINT_DECAY_PER_TICK
    if period_for_room(state) == "night":
        decay += 1
    player.footprint = max(0, player.footprint - decay)


def wanted_gain_multiplier(player: Player) -> float:
    if player.footprint >= HIGH_FOOTPRINT_THRESHOLD:
        return 1.25
    if player.footprint >= 40:
        return 1.1
    return 1.0


def corp_aggro_bonus(player: Player) -> int:
    if player.footprint >= HIGH_FOOTPRINT_THRESHOLD:
        return 2
    if player.footprint >= 40:
        return 1
    return 0


def footprint_pda_row(player: Player, locale: str) -> str:
    return t(locale, "footprint.pda_row", value=str(player.footprint))