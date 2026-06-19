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
    world_changed: bool = False
    auth_event: bool = False


_REGISTRY: dict[str, Handler] = {}


def register(name: str, handler: Handler) -> None:
    _REGISTRY[name] = handler


def ok(
    lines: list[str],
    *,
    meta: dict[str, str] | None = None,
    moved: bool = False,
    document: bool = False,
    world_changed: bool = False,
    auth_event: bool = False,
) -> CommandResult:
    return CommandResult(
        lines=lines,
        meta=meta or {},
        moved=moved,
        document=document,
        world_changed=world_changed,
        auth_event=auth_event,
    )


def ok_document(
    lines: list[str],
    *,
    meta: dict[str, str] | None = None,
    moved: bool = False,
    world_changed: bool = False,
) -> CommandResult:
    return ok(lines, meta=meta, document=True, moved=moved, world_changed=world_changed)


def player_meta(ctx: CommandContext) -> dict[str, str]:
    room = ctx.state.world.room(ctx.player.room_id)
    from shared.locale_content import room_name

    clock = ctx.state.clock
    config = ctx.state.time_config
    return {
        "name": ctx.player.name if ctx.player.named else "",
        "room": room_name(room, ctx.player.locale) if room else "—",
        "room_id": ctx.player.room_id,
        "hp": f"{ctx.player.hp}/{ctx.player.max_hp}",
        "gold": str(ctx.player.gold),
        "locale": ctx.player.locale,
        "auth": "1" if ctx.player.named else "0",
        "time": clock.format_clock(ctx.player.locale),
        "period": clock.format_period(ctx.player.locale, config),
        "ram": f"{ctx.player.ram}/{ctx.player.max_ram}",
        "humanity": str(ctx.player.humanity),
        "reputation": str(ctx.player.reputation),
    }


def dispatch(line: str, player: Player, state: WorldState, peers: list[Player], all_players: list[Player]) -> CommandResult:
    text = expand_line(line.strip(), player)
    if not text:
        return ok([])
    parts = text.split(maxsplit=1)
    verb = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if not player.named:
        from commands.auth_helpers import AUTH_COMMANDS
        from shared.i18n import t

        if verb not in AUTH_COMMANDS:

            return ok([t(player.locale, "auth.required")])

    handler = _REGISTRY.get(verb)
    if handler is None:
        from shared.i18n import t

        return ok([t(player.locale, "game.unknown_verb", verb=verb)])

    ctx = CommandContext(player=player, state=state, args=args, peers=peers, all_players=all_players)
    result = handler(ctx)
    if result.meta is None:
        result.meta = {}
    if not result.meta and verb not in {"quit"}:
        result.meta = player_meta(ctx)
    return result


def register_builtin_commands() -> None:
    from commands import (  # noqa: F401
        drop,
        go,
        help_cmd,
        inventory,
        login,
        look,
        pda,
        quit_cmd,
        register,
        take,
        time_cmd,
    )