from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from commands.aliases import expand_line
from combat.encounter import COMBAT_ALLOWED_COMMANDS, combat_meta
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
    panel: str = ""
    ui_json: str = ""
    refresh_sidebar: bool = False
    quit_game: bool = False
    world_changed: bool = False
    auth_event: bool = False
    broadcast_key: str = ""
    broadcast_kwargs: dict[str, str] = field(default_factory=dict)


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
    refresh_sidebar: bool = False,
    broadcast_key: str = "",
    broadcast_kwargs: dict[str, str] | None = None,
) -> CommandResult:
    return CommandResult(
        lines=lines,
        meta=meta or {},
        moved=moved,
        document=document,
        world_changed=world_changed,
        auth_event=auth_event,
        refresh_sidebar=refresh_sidebar,
        broadcast_key=broadcast_key,
        broadcast_kwargs=broadcast_kwargs or {},
    )


def ok_panel(
    lines: list[str],
    *,
    panel: str,
    ui_json: str = "",
    meta: dict[str, str] | None = None,
    refresh_sidebar: bool = False,
) -> CommandResult:
    return CommandResult(
        lines=lines,
        meta=meta or {},
        panel=panel,
        ui_json=ui_json,
        refresh_sidebar=refresh_sidebar,
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
    from commands.helpers import faction_label, quest_hint_for_player, quest_label_for_player
    from shared.i18n import t
    from shared.locale_content import room_name
    from world.weather import weather_label

    room = ctx.state.world.room(ctx.player.room_id)

    clock = ctx.state.clock
    config = ctx.state.time_config
    weather = ""
    if room and room.district:
        weather_type = ctx.state.weather.get(room.district, "")
        if weather_type:
            weather = weather_label(weather_type, ctx.player.locale)
    from shared.prompt_tokens import effective_prompt, expand_prompt

    meta = {
        "name": ctx.player.name if ctx.player.named else "",
        "room": room_name(room, ctx.player.locale) if room else "—",
        "room_id": ctx.player.room_id,
        "hp": f"{ctx.player.hp}/{ctx.player.max_hp}",
        "gold": str(ctx.player.gold),
        "locale": ctx.player.locale,
        "auth": "1" if ctx.player.named else "0",
        "time": clock.format_clock(ctx.player.locale),
        "period": clock.format_period(ctx.player.locale, config),
        "weather": weather,
        "ram": f"{ctx.player.ram}/{ctx.player.max_ram}",
        "humanity": str(ctx.player.humanity),
        "reputation": str(ctx.player.reputation),
        "faction": faction_label(ctx.state.world, ctx.player.faction, ctx.player.locale),
        "prompt_mud": expand_prompt(effective_prompt(ctx.player), ctx.player, ctx.state),
    }
    if ctx.player.in_combat:
        meta.update(combat_meta(ctx.state, ctx.player))
    else:
        meta["combat"] = "0"
    quest_label = quest_label_for_player(ctx)
    if quest_label:
        meta["quest"] = quest_label
    hint = quest_hint_for_player(ctx)
    if hint:
        meta["hint"] = hint
    if ctx.player.net_shell:
        meta["net_shell"] = "1"
        meta["net_prompt"] = t(ctx.player.locale, "net.prompt")
    return meta


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

    if player.in_combat and verb not in COMBAT_ALLOWED_COMMANDS:
        from shared.i18n import t

        return ok([t(player.locale, "combat.busy")])

    if player.net_shell:
        from commands.net_shell import NET_SHELL_COMMANDS, dispatch_net, net_meta
        from shared.i18n import t

        if verb not in NET_SHELL_COMMANDS:
            return ok([t(player.locale, "net.busy")], meta=net_meta(CommandContext(player, state, args, peers, all_players)))
        ctx = CommandContext(player=player, state=state, args=args, peers=peers, all_players=all_players)
        result = dispatch_net(text, ctx)
        if not result.meta:
            result.meta = net_meta(ctx)
        return result

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
        appraise,
        attack,
        defend,
        drop,
        equip,
        equipment,
        flee,
        give,
        go,
        help_cmd,
        install,
        inventory,
        login,
        look,
        learn,
        map,
        mod,
        net,
        pda,
        pledge,
        recall,
        say,
        talk,
        prompt_cmd,
        quickhack,
        quit_cmd,
        register,
        scan,
        take,
        time_cmd,
        unequip,
    )