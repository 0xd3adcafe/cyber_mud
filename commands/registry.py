from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from commands.aliases import expand_line
from entities.player import Player
from world.state import WorldState

Handler = Callable[["CommandContext"], "CommandResult"]


@dataclass
class CommandContext:
    player: Player
    state: WorldState
    args: str
    peers: list[Player] = field(default_factory=list)
    all_players: list[Player] = field(default_factory=list)


@dataclass
class CommandResult:
    lines: list[str]
    meta: dict[str, str] = field(default_factory=dict)
    moved: bool = False
    document: bool = False
    quit_game: bool = False


_REGISTRY: dict[str, Handler] = {}


def register(name: str, handler: Handler) -> None:
    _REGISTRY[name] = handler


def ok(lines: list[str], *, meta: dict[str, str] | None = None, moved: bool = False, document: bool = False) -> CommandResult:
    return CommandResult(lines=lines, meta=meta or {}, moved=moved, document=document)


def ok_document(lines: list[str], *, meta: dict[str, str] | None = None) -> CommandResult:
    return ok(lines, meta=meta, document=True)


def player_meta(ctx: CommandContext) -> dict[str, str]:
    room = ctx.state.world.room(ctx.player.room_id)
    from shared.locale_content import room_name

    return {
        "name": ctx.player.name if ctx.player.named else "",
        "room": room_name(room, ctx.player.locale) if room else "—",
        "room_id": ctx.player.room_id,
        "hp": f"{ctx.player.hp}/{ctx.player.max_hp}",
        "gold": str(ctx.player.gold),
        "locale": ctx.player.locale,
        "auth": "1" if ctx.player.named else "0",
    }


def dispatch(line: str, player: Player, state: WorldState, peers: list[Player], all_players: list[Player]) -> CommandResult:
    text = expand_line(line.strip(), player)
    if not text:
        return ok([])
    parts = text.split(maxsplit=1)
    verb = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    handler = _REGISTRY.get(verb)
    if handler is None:
        from shared.i18n import t

        return ok([t(player.locale, "game.unknown_verb", verb=verb)])
    ctx = CommandContext(player=player, state=state, args=args, peers=peers, all_players=all_players)
    return handler(ctx)


def register_builtin_commands() -> None:
    from commands import go, help_cmd, look, quit_cmd  # noqa: F401