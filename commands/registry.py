from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from commands.aliases import expand_line
from combat.encounter import COMBAT_ALLOWED_COMMANDS, combat_meta
from entities.player import Player
import time

from shared.repeat import REPEAT_BLOCKED, REPEAT_INTERVAL_SECONDS, parse_repeat
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
    auth_failure: bool = False
    broadcast_key: str = ""
    broadcast_mature_key: str = ""
    broadcast_mature_fallback_key: str = ""
    broadcast_kwargs: dict[str, str] = field(default_factory=dict)
    broadcast_room_id: str = ""
    presence_from_room: str = ""


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
    auth_failure: bool = False,
    refresh_sidebar: bool = False,
    broadcast_key: str = "",
    broadcast_mature_key: str = "",
    broadcast_mature_fallback_key: str = "",
    broadcast_kwargs: dict[str, str] | None = None,
    broadcast_room_id: str = "",
    presence_from_room: str = "",
) -> CommandResult:
    return CommandResult(
        lines=lines,
        meta=meta or {},
        moved=moved,
        document=document,
        world_changed=world_changed,
        auth_event=auth_event,
        auth_failure=auth_failure,
        refresh_sidebar=refresh_sidebar,
        broadcast_key=broadcast_key,
        broadcast_mature_key=broadcast_mature_key,
        broadcast_mature_fallback_key=broadcast_mature_fallback_key,
        broadcast_kwargs=broadcast_kwargs or {},
        broadcast_room_id=broadcast_room_id,
        presence_from_room=presence_from_room,
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
    presence_from_room: str = "",
) -> CommandResult:
    return ok(
        lines,
        meta=meta,
        document=True,
        moved=moved,
        world_changed=world_changed,
        presence_from_room=presence_from_room,
    )


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
    from world.progression import xp_to_next_level

    meta = {
        "name": ctx.player.name if ctx.player.named else "",
        "room": room_name(room, ctx.player.locale) if room else "—",
        "room_id": ctx.player.room_id,
        "hp": f"{ctx.player.hp}/{ctx.player.max_hp}",
        "gold": str(ctx.player.gold),
        "locale": ctx.player.locale,
        "content_rating": ctx.player.content_rating,
        "auth": "1" if ctx.player.named else "0",
        "time": clock.format_clock(ctx.player.locale),
        "period": clock.format_period(ctx.player.locale, config),
        "weather": weather,
        "ram": f"{ctx.player.ram}/{ctx.player.max_ram}",
        "humanity": str(ctx.player.humanity),
        "reputation": str(ctx.player.reputation),
        "street_cred": str(ctx.player.street_cred),
        "wanted": str(ctx.player.wanted_level),
        "level": str(ctx.player.level),
        "faction": faction_label(ctx.state.world, ctx.player.faction, ctx.player.locale),
        "xp": f"{ctx.player.xp}/{xp_to_next_level(ctx.player.level)}",
        "prompt_template": effective_prompt(ctx.player),
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
    meta["net_shell"] = "1" if ctx.player.net_shell else "0"
    if ctx.player.net_shell:
        meta["net_prompt"] = t(ctx.player.locale, "net.prompt")
        meta["net_trace"] = str(ctx.player.net_trace)
    from shared.completion import completion_meta

    meta.update(completion_meta(ctx))
    meta["posture"] = ctx.player.posture
    meta["fatigue"] = str(ctx.player.fatigue)
    return meta


def _should_stop_repeat(result: CommandResult, player: Player, *, verb: str, was_in_combat: bool) -> bool:
    if result.quit_game or result.auth_event:
        return True
    if was_in_combat and not player.in_combat:
        return True
    if player.hp <= 0:
        return True
    if verb == "go" and not result.moved:
        return True
    return False


def _merge_repeat_results(
    results: list[CommandResult],
    *,
    locale: str,
    requested: int,
) -> CommandResult:
    if not results:
        return ok([])
    if len(results) == 1:
        return results[0]

    from shared.i18n import t

    lines: list[str] = []
    for result in results:
        lines.extend(result.lines)
    if len(results) < requested:
        lines.append(t(locale, "repeat.stopped", done=str(len(results)), total=str(requested)))
    else:
        lines.append(t(locale, "repeat.done", count=str(len(results))))

    last = results[-1]
    return CommandResult(
        lines=lines,
        meta=last.meta,
        moved=any(r.moved for r in results),
        document=last.document,
        panel=last.panel,
        ui_json=last.ui_json,
        refresh_sidebar=any(r.refresh_sidebar for r in results),
        quit_game=last.quit_game,
        world_changed=any(r.world_changed for r in results),
        auth_event=any(r.auth_event for r in results),
        broadcast_key=last.broadcast_key,
        broadcast_mature_key=last.broadcast_mature_key,
        broadcast_mature_fallback_key=last.broadcast_mature_fallback_key,
        broadcast_kwargs=last.broadcast_kwargs,
        broadcast_room_id=last.broadcast_room_id,
        presence_from_room=next((r.presence_from_room for r in results if r.presence_from_room), ""),
    )


def _dispatch_once(
    line: str,
    player: Player,
    state: WorldState,
    peers: list[Player],
    all_players: list[Player],
) -> CommandResult:
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

    from world.mature import gate_command

    mature_refusal = gate_command(player, player.locale, verb)
    if mature_refusal is not None:
        return ok(mature_refusal)

    if player.net_shell:
        from commands.net_shell import (
            NET_ALLOWED_MUD_COMMANDS,
            NET_SHELL_COMMANDS,
            dispatch_net,
            net_meta,
        )
        from shared.i18n import t

        ctx = CommandContext(player=player, state=state, args=args, peers=peers, all_players=all_players)
        if verb in NET_SHELL_COMMANDS:
            result = dispatch_net(text, ctx)
            if not result.meta:
                result.meta = net_meta(ctx)
            return result
        if verb not in NET_ALLOWED_MUD_COMMANDS:
            return ok([t(player.locale, "net.busy")], meta=net_meta(ctx))

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


def dispatch(line: str, player: Player, state: WorldState, peers: list[Player], all_players: list[Player]) -> CommandResult:
    count, remainder = parse_repeat(line.strip())
    if not remainder:
        return ok([])

    text = expand_line(remainder, player)
    if not text:
        return ok([])

    verb = text.split(maxsplit=1)[0].lower()
    if count > 1 and verb in REPEAT_BLOCKED:
        return _dispatch_once(text, player, state, peers, all_players)

    if count == 1:
        return _dispatch_once(text, player, state, peers, all_players)

    results: list[CommandResult] = []
    for index in range(count):
        was_in_combat = player.in_combat
        result = _dispatch_once(text, player, state, peers, all_players)
        results.append(result)
        if _should_stop_repeat(result, player, verb=verb, was_in_combat=was_in_combat):
            break
        if index + 1 < count and REPEAT_INTERVAL_SECONDS > 0:
            time.sleep(REPEAT_INTERVAL_SECONDS)

    return _merge_repeat_results(results, locale=player.locale, requested=count)


def register_builtin_commands() -> None:
    from commands import (  # noqa: F401
        appraise,
        buy,
        attack,
        shoot,
        slash,
        bash,
        punch,
        backstab,
        defend,
        drop,
        equip,
        equipment,
        flee,
        give,
        go,
        help_cmd,
        improve,
        install,
        cyberware_cmd,
        uninstall,
        rent,
        home_cmd,
        stash_cmd,
        transit_cmd,
        vehicles_cmd,
        drive,
        inventory,
        changepass,
        login,
        look,
        lang,
        learn,
        stats,
        gigs,
        talents_cmd,
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
        resume,
        scan,
        sell,
        shop_cmd,
        take,
        time_cmd,
        unequip,
        use,
        interact,
        craft,
        disassemble_cmd,
        braindance,
        settings_cmd,
        flirt,
        taunt,
        finish_cmd,
        life,
        jam,
        distract,
    )