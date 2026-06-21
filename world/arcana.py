from __future__ import annotations

import random

from entities.player import Player
from shared.i18n import t
from shared.mature_i18n import tm
from world.mature import is_mature
from world.mature_voice import apply_mature_template, mature_voice_line, resolve_mature_voice
from world.state import WorldState

MAJOR_ARCANA: tuple[str, ...] = (
    "fool",
    "magician",
    "priestess",
    "empress",
    "emperor",
    "hierophant",
    "lovers",
    "chariot",
    "strength",
    "hermit",
    "wheel",
    "justice",
    "hanged",
    "death",
    "temperance",
    "devil",
    "tower",
    "star",
    "moon",
    "sun",
    "judgement",
    "world",
)

PERIOD_FLAG = "arcana_period"
LAST_CARD_FLAG = "arcana_last_card"
UNLOCK_FLAGS: dict[str, str] = {
    "lovers": "idol_blackmail",
    "chariot": "tyrell_shadow",
    "star": "kabuki_spotlight",
}


def current_period(state: WorldState) -> str:
    return state.clock.period_id(state.time_config)


def arcana_on_cooldown(player: Player, state: WorldState) -> bool:
    return player.interact_flags.get(PERIOD_FLAG) == current_period(state)


def _draw_line(locale: str, card_id: str, player: Player, state: WorldState) -> str:
    key = f"arcana.draw.{card_id}"
    if is_mature(player):
        room = state.world.room(player.room_id)
        voice = resolve_mature_voice(player, state, room)
        mature_key = f"arcana.draw.{card_id}"
        line = mature_voice_line(locale, mature_key, voice)
        if not line.startswith("arcana.") and not line.startswith("mature."):
            return apply_mature_template(line, player, locale, voice=voice)
    line = t(locale, key)
    if line != key:
        return line
    return t(locale, "arcana.draw.fallback", card=card_id)


def _maybe_unlock(player: Player, card_id: str, locale: str) -> str:
    quest_id = UNLOCK_FLAGS.get(card_id, "")
    if not quest_id:
        return ""
    flag = f"arcana_unlock_{quest_id}"
    if player.quest_flags.get(flag) == "1":
        return ""
    player.quest_flags[flag] = "1"
    return t(locale, "arcana.unlocked", quest=quest_id)


def perform_arcana_draw(
    player: Player,
    state: WorldState,
    locale: str,
    *,
    spread: int = 1,
) -> list[str]:
    if arcana_on_cooldown(player, state):
        return [t(locale, "arcana.cooldown")]

    count = 3 if spread >= 3 else 1
    pool = list(MAJOR_ARCANA)
    if count > len(pool):
        count = len(pool)
    cards = random.sample(pool, count)

    lines: list[str] = []
    if count > 1:
        lines.append(t(locale, "arcana.three_header"))

    for card_id in cards:
        lines.append(_draw_line(locale, card_id, player, state))

    primary = cards[0]
    player.interact_flags[PERIOD_FLAG] = current_period(state)
    player.interact_flags[LAST_CARD_FLAG] = primary

    unlock = _maybe_unlock(player, primary, locale)
    if unlock:
        lines.append(unlock)

    return lines