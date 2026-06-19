from __future__ import annotations

from entities.player import Player
from shared.i18n import t
from shared.locale_content import room_name
from world.state import WorldState
from world.weather import weather_label

DEFAULT_PROMPT = "%n> "

PROMPT_TOKENS = {
    "%n": "prompt.token.name",
    "%r": "prompt.token.room",
    "%h": "prompt.token.hp",
    "%t": "prompt.token.time",
    "%w": "prompt.token.weather",
    "%g": "prompt.token.gold",
    "%p": "prompt.token.period",
    "%f": "prompt.token.faction",
    "%m": "prompt.token.ram",
}

CP2077_TEMPLATES = {
    "street": "[%h] %n> ",
    "netrun": "%n@netrun-kali> ",
    "minimal": "%n> ",
    "full": "[%h|%m] %n@%r %p %w> ",
    "edgerunner": "[%g] %f │ %n> ",
}


def faction_label(player: Player, state: WorldState) -> str:
    if player.faction:
        return state.world.factions.get(player.faction, player.faction)
    return t(player.locale, "prompt.faction_none")


def expand_prompt(template: str, player: Player, state: WorldState) -> str:
    room = state.world.room(player.room_id)
    room_label = room_name(room, player.locale) if room else "—"
    clock = state.clock
    config = state.time_config
    weather = ""
    if room and room.district:
        weather_type = state.weather.get(room.district, "")
        if weather_type:
            weather = weather_label(weather_type, player.locale)

    replacements = {
        "%n": player.name if player.named else "旅人",
        "%r": room_label,
        "%h": f"{player.hp}/{player.max_hp}",
        "%t": clock.format_clock(player.locale),
        "%w": weather or "—",
        "%g": str(player.gold),
        "%p": clock.format_period(player.locale, config),
        "%f": faction_label(player, state),
        "%m": f"{player.ram}/{player.max_ram}",
    }
    result = template
    for token, value in replacements.items():
        result = result.replace(token, value)
    return result


def effective_prompt(player: Player) -> str:
    return player.prompt_mud.strip() or DEFAULT_PROMPT