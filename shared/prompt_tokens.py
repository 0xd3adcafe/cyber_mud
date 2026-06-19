from __future__ import annotations

from entities.player import Player
from shared.locale_content import room_name
from world.state import WorldState

DEFAULT_PROMPT = "%n> "

PROMPT_TOKENS = {
    "%n": "prompt.token.name",
    "%r": "prompt.token.room",
    "%h": "prompt.token.hp",
    "%t": "prompt.token.time",
}


def expand_prompt(template: str, player: Player, state: WorldState) -> str:
    room = state.world.room(player.room_id)
    room_label = room_name(room, player.locale) if room else "—"
    clock = state.clock.format_clock(player.locale)
    replacements = {
        "%n": player.name if player.named else "旅人",
        "%r": room_label,
        "%h": f"{player.hp}/{player.max_hp}",
        "%t": clock,
    }
    result = template
    for token, value in replacements.items():
        result = result.replace(token, value)
    return result


def effective_prompt(player: Player) -> str:
    return player.prompt_mud.strip() or DEFAULT_PROMPT