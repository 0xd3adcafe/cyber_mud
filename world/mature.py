from __future__ import annotations

from entities.player import Player
from shared.i18n import t

RATINGS = frozenset({"teen", "mature"})
MATURE_TAG = "mature"
MATURE_COMMANDS = frozenset({"flirt", "spend_time", "taunt", "finish", "scene", "whisper"})


def is_mature(player: Player) -> bool:
    return player.content_rating == "mature"


def set_content_rating(player: Player, enabled: bool) -> None:
    player.content_rating = "mature" if enabled else "teen"


def has_mature_tag(tags: list[str]) -> bool:
    return MATURE_TAG in tags


def refuse_lines(locale: str) -> list[str]:
    return [t(locale, "mature.refused")]


def gate_command(player: Player, locale: str, verb: str) -> list[str] | None:
    if verb in MATURE_COMMANDS and not is_mature(player):
        return refuse_lines(locale)
    return None


def gate_room_entry(player: Player, room, locale: str) -> list[str] | None:
    if room is not None and has_mature_tag(room.tags) and not is_mature(player):
        return refuse_lines(locale)
    return None


def gate_content_rating(player: Player, rating: str, locale: str) -> list[str] | None:
    if rating == "mature" and not is_mature(player):
        return refuse_lines(locale)
    return None


def gate_mature_entity(player: Player, tags: list[str], locale: str) -> list[str] | None:
    if has_mature_tag(tags) and not is_mature(player):
        return refuse_lines(locale)
    return None