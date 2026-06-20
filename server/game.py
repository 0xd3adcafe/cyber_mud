from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from commands import register_builtin_commands
from combat.encounter import COMBAT_TICK_SECONDS, encounter_for_player, end_encounter
from combat.tick import process_combat_tick
from commands.registry import CommandContext
from entities.player import Player
from persistence.save import save_player
from persistence.world_state import load_world_state, save_world_state
from shared.i18n import t, t_list
from shared.protocol import MOTD_PREFIX, PANEL_PREFIX, SYS_PREFIX, meta_line, ui_line
from shared.startup import StartupReport
from world.clock import load_time_config
from world.loader import load_world
from world.state import WorldState
from world.tick import process_tick

register_builtin_commands()


@dataclass
class ClientSession:
    writer: object
    player: Player

    async def send(self, text: str) -> None:
        self.writer.write((text + "\n").encode("utf-8"))
        await self.writer.drain()

    async def send_lines(self, lines: list[str]) -> None:
        for line in lines:
            await self.send(line)

    async def send_meta(self, meta: dict[str, str]) -> None:
        for key, value in meta.items():
            await self.send(meta_line(key, value))

    async def send_panel(self, panel: str, lines: list[str], *, ui_json: str = "") -> None:
        await self.send_meta({"ui_panel": panel})
        if ui_json:
            await self.send(ui_line(ui_json))
        for line in lines:
            await self.send(f"{PANEL_PREFIX}{line}")
        await self.send_meta({"ui_panel_end": "1"})


@dataclass
class Game:
    state: WorldState
    sessions: list[ClientSession] = field(default_factory=list)
    startup: StartupReport | None = None

    def peers_in_room(self, room_id: str, *, exclude: Player | None = None) -> list[Player]:
        return [
            s.player for s in self.sessions
            if s.player.room_id == room_id and s.player is not exclude
        ]

    def all_named_players(self) -> list[Player]:
        return [s.player for s in self.sessions if s.player.named]

    def session_for_player(self, player: Player) -> ClientSession | None:
        for session in self.sessions:
            if session.player is player:
                return session
        return None

    def remove_session(self, session: ClientSession) -> None:
        if session in self.sessions:
            self.sessions.remove(session)

    def reload_world_data(self) -> None:
        from shared.i18n import clear_locale_cache
        from world.loader import load_world

        world = load_world()
        self.state.world = world
        clear_locale_cache()

    async def notify_dev_reload(self, kind: str, *, failures: list[tuple[str, str]] | None = None) -> None:
        from commands.registry import player_meta
        from server.heartbeat import log_server_event

        from shared.server_locale import server_locale

        loc = server_locale()
        if kind == "data":
            world = self.state.world
            message = t(loc, "server.reload_world_msg")
            log_server_event(
                t(
                    loc,
                    "server.reload_world",
                    rooms=str(len(world.rooms)),
                    items=str(len(world.items)),
                    npcs=str(len(world.npcs)),
                )
            )
        else:
            if failures:
                message = t(loc, "server.reload_code_msg_fail", count=str(len(failures)))
                log_server_event(t(loc, "server.reload_code_fail", count=str(len(failures))))
                for name, err in failures:
                    log_server_event(t(loc, "server.reload_fail_line", name=name, err=err))
            else:
                message = t(loc, "server.reload_code_msg")
                log_server_event(t(loc, "server.reload_code"))
        for session in self.sessions:
            await session.send(f"{SYS_PREFIX}{message}")
            if session.player.named:
                await session.send_meta(player_meta(CommandContext(session.player, self.state, "")))

    async def add_session(self, session: ClientSession) -> None:
        from commands.registry import player_meta

        self.sessions.append(session)
        locale = session.player.locale
        for line in t_list(locale, "motd.lines"):
            await session.send(f"{MOTD_PREFIX}{line}")
        if self.startup is not None:
            await session.send(
                f"{SYS_PREFIX}{t(locale, 'server.ready_line', brief=self.startup.format_brief())}"
            )
        await session.send_meta(player_meta(CommandContext(session.player, self.state, "")))

    async def broadcast_room(self, room_id: str, lines: list[str], *, exclude: ClientSession | None = None) -> None:
        for target in self.sessions:
            if target.player.room_id == room_id and target is not exclude:
                await target.send_lines(lines)

    async def broadcast_localized(self, room_id: str, key: str, *, exclude: ClientSession | None = None, **kwargs: str) -> None:
        for target in self.sessions:
            if target.player.room_id != room_id or target is exclude:
                continue
            await target.send(t(target.player.locale, key, **kwargs))

    async def handle_command(self, session: ClientSession, line: str) -> bool:
        from commands.registry import dispatch, player_meta

        unnamed_before = not session.player.named
        peers = self.peers_in_room(session.player.room_id, exclude=session.player)
        result = dispatch(line, session.player, self.state, peers, self.all_named_players())

        if result.panel:
            await session.send_panel(result.panel, result.lines, ui_json=result.ui_json)
        else:
            await session.send_lines(result.lines)

        meta = dict(result.meta) if result.meta else {}
        if result.refresh_sidebar:
            meta["refresh_sidebar"] = "1"
        if meta:
            await session.send_meta(meta)

        if result.auth_event and unnamed_before and session.player.named:
            await self.broadcast_localized(
                session.player.room_id,
                "game.enter",
                exclude=session,
                name=session.player.name,
            )
            look = dispatch("look", session.player, self.state, peers, self.all_named_players())
            await session.send_lines(look.lines)
            if look.meta:
                await session.send_meta(look.meta)
            save_player(session.player)

        if result.moved and result.presence_from_room and session.player.named:
            await self.broadcast_localized(
                result.presence_from_room,
                "presence.leave",
                exclude=session,
                name=session.player.name,
            )
            await self.broadcast_localized(
                session.player.room_id,
                "presence.enter",
                exclude=session,
                name=session.player.name,
            )

        if result.broadcast_key:
            await self.broadcast_localized(
                result.broadcast_room_id or session.player.room_id,
                result.broadcast_key,
                exclude=session,
                **result.broadcast_kwargs,
            )

        if result.world_changed:
            save_world_state(self.state)
        if session.player.named and (result.world_changed or result.moved or result.auth_event):
            save_player(session.player)

        return not result.quit_game

    async def notify_disconnect(self, session: ClientSession) -> None:
        encounter = encounter_for_player(self.state, session.player)
        if encounter is not None:
            end_encounter(self.state, session.player, encounter)
            save_world_state(self.state)
        if session.player.named:
            save_player(session.player)
            await self.broadcast_localized(
                session.player.room_id,
                "game.offline",
                exclude=session,
                name=session.player.name,
            )

    async def broadcast_time_meta(self) -> None:
        for session in self.sessions:
            if not session.player.named:
                continue
            ctx = CommandContext(session.player, self.state, "")
            await session.send_meta(
                {
                    "time": ctx.state.clock.format_clock(session.player.locale),
                    "period": ctx.state.clock.format_period(session.player.locale, self.state.time_config),
                }
            )

    async def _broadcast_tick_events(self, events) -> None:
        for event in events:
            if event.kind in {"npc_enter", "npc_leave"}:
                key = "npc.enter" if event.kind == "npc_enter" else "npc.leave"
                for target in self.sessions:
                    if target.player.room_id != event.room_id:
                        continue
                    name = (
                        event.npc_name_zh
                        if target.player.locale == "zh"
                        else (event.npc_name_en or event.npc_name_zh)
                    )
                    await target.send(t(target.player.locale, key, name=name))
            elif event.kind in {"npc_ai_fight", "npc_ai_social", "npc_ai_defeat", "npc_ai_hunt"}:
                for target in self.sessions:
                    if target.player.room_id != event.room_id:
                        continue
                    locale = target.player.locale
                    kwargs = dict(event.message_kwargs)
                    if locale == "zh":
                        for key in ("attacker", "defender", "winner", "loser", "speaker", "target", "name"):
                            en_key = f"{key}_en"
                            zh_key = f"{key}_zh"
                            if zh_key in kwargs:
                                kwargs[key] = kwargs[zh_key]
                    else:
                        for key in ("attacker", "defender", "winner", "loser", "speaker", "target", "name"):
                            en_key = f"{key}_en"
                            zh_key = f"{key}_zh"
                            if en_key in kwargs:
                                kwargs[key] = kwargs[en_key]
                            elif zh_key in kwargs:
                                kwargs[key] = kwargs[zh_key]
                    msg_key = event.message_key
                    if event.kind == "npc_ai_social":
                        base = t(locale, msg_key)
                        if base == msg_key:
                            base = t(locale, "npc.ai.msg.socialize")
                        await target.send(
                            t(
                                locale,
                                "npc.ai.social",
                                speaker=kwargs.get("speaker", ""),
                                target=kwargs.get("target", ""),
                                msg=base,
                            )
                        )
                    else:
                        await target.send(t(locale, msg_key, **kwargs))
            elif event.kind == "npc_idle":
                for target in self.sessions:
                    if target.player.room_id != event.room_id:
                        continue
                    msg = event.idle_msg_zh if target.player.locale == "zh" else (event.idle_msg_en or event.idle_msg_zh)
                    if not msg:
                        continue
                    name = event.npc_name_zh if target.player.locale == "zh" else (event.npc_name_en or event.npc_name_zh)
                    await target.send(t(target.player.locale, "npc.idle", name=name, msg=msg))
            elif event.kind == "weather_change":
                for target in self.sessions:
                    room = self.state.world.room(target.player.room_id)
                    if room is None or room.district != event.district:
                        continue
                    from world.weather import weather_label

                    label = weather_label(event.weather, target.player.locale)
                    await target.send_meta({"weather": label})
            elif event.kind == "chase_follow":
                for target in self.sessions:
                    if target.player.name != event.player_name:
                        continue
                    await target.send(
                        t(target.player.locale, event.message_key, **event.message_kwargs)
                    )
                    from commands.helpers import quest_hint_for_player
                    from commands.registry import CommandContext

                    hint = quest_hint_for_player(CommandContext(target.player, self.state, ""))
                    if hint:
                        await target.send_meta({"hint": hint})
            elif event.kind == "chase_restart":
                from commands.registry import player_meta

                for target in self.sessions:
                    if target.player.name != event.player_name:
                        continue
                    line = event.message_kwargs.get("line", "")
                    if line:
                        await target.send(line)
                    await target.send_meta(player_meta(CommandContext(target.player, self.state, "")))
            elif event.kind == "corpse_decay":
                for target in self.sessions:
                    if target.player.room_id != event.room_id:
                        continue
                    label = (
                        event.message_kwargs.get("label_zh", "")
                        if target.player.locale == "zh"
                        else event.message_kwargs.get("label_en", event.message_kwargs.get("label_zh", ""))
                    )
                    await target.send(t(target.player.locale, event.message_key, label=label))
            elif event.kind == "wanted_decay":
                for target in self.sessions:
                    if target.player.name != event.player_name:
                        continue
                    await target.send(event.message_kwargs.get("text", ""))
                    await target.send_meta({"wanted": str(target.player.wanted_level)})
            elif event.kind in {"trauma_tick", "ambient_tick"}:
                for target in self.sessions:
                    if target.player.name != event.player_name:
                        continue
                    text = event.message_kwargs.get("text", "")
                    if text:
                        await target.send(text)
                    if event.kind == "trauma_tick" and "hp" in event.message_kwargs:
                        await target.send_meta({"hp": event.message_kwargs["hp"]})
            elif event.kind == "hp_regen":
                for target in self.sessions:
                    if target.player.name != event.player_name:
                        continue
                    locale = target.player.locale
                    amount = event.message_kwargs.get("amount", "0")
                    if int(amount) > 0:
                        await target.send(
                            t(
                                locale,
                                "vitals.hp_regen",
                                amount=amount,
                                hp=event.message_kwargs.get("hp", str(target.player.hp)),
                                max_hp=event.message_kwargs.get("max_hp", str(target.player.max_hp)),
                            )
                        )
                    ram_amount = int(event.message_kwargs.get("ram_amount", "0"))
                    if ram_amount > 0:
                        await target.send(
                            t(
                                locale,
                                "vitals.ram_regen",
                                amount=str(ram_amount),
                                ram=event.message_kwargs.get("ram", str(target.player.ram)),
                                max_ram=event.message_kwargs.get("max_ram", str(target.player.max_ram)),
                            )
                        )
                    for line in event.message_kwargs.get("life_lines") or []:
                        await target.send(line)
                    meta = {
                        "hp": f"{target.player.hp}/{target.player.max_hp}",
                        "ram": f"{target.player.ram}/{target.player.max_ram}",
                        "posture": target.player.posture,
                        "fatigue": str(target.player.fatigue),
                    }
                    await target.send_meta(meta)

    async def _handle_combat_tick_results(self, combat_results) -> None:
        from combat.encounter import combat_meta
        from commands.registry import CommandContext, player_meta

        for player, combat_result in combat_results:
            session = self.session_for_player(player)
            if session and combat_result.lines:
                await session.send_lines(combat_result.lines)
            if session:
                if combat_result.moved:
                    meta = player_meta(CommandContext(player, self.state, ""))
                else:
                    meta = combat_meta(self.state, player)
                    meta["hp"] = f"{player.hp}/{player.max_hp}"
                    if combat_result.ended:
                        meta["combat"] = "0"
                await session.send_meta(meta)
            if combat_result.broadcast_key:
                await self.broadcast_localized(
                    combat_result.broadcast_room_id or player.room_id,
                    combat_result.broadcast_key,
                    **(combat_result.broadcast_kwargs or {}),
                )
            if combat_result.ended or combat_result.lines:
                save_player(player)
                save_world_state(self.state)

    async def combat_tick_loop(self) -> None:
        try:
            while True:
                interval = (
                    COMBAT_TICK_SECONDS
                    if self.state.encounters
                    else self.state.time_config.tick_interval_seconds
                )
                await asyncio.sleep(interval)
                if not self.state.encounters:
                    continue
                combat_results = process_combat_tick(self.state, self.all_named_players())
                if combat_results:
                    await self._handle_combat_tick_results(combat_results)
        except asyncio.CancelledError:
            raise

    async def tick_loop(self) -> None:
        interval = self.state.time_config.tick_interval_seconds
        try:
            while True:
                await asyncio.sleep(interval)
                result = process_tick(
                    self.state,
                    self.state.time_config,
                    players=self.all_named_players(),
                )
                if result.events:
                    await self._broadcast_tick_events(result.events)
                if result.combat_results:
                    await self._handle_combat_tick_results(result.combat_results)
                if result.time_changed or result.events or result.combat_results:
                    save_world_state(self.state)
                for event in result.events:
                    if event.kind not in {"hp_regen", "wanted_decay", "trauma_tick", "ambient_tick"}:
                        continue
                    player = next(
                        (p for p in self.all_named_players() if p.name == event.player_name),
                        None,
                    )
                    if player is not None:
                        save_player(player)
                if result.time_changed:
                    await self.broadcast_time_meta()
        except asyncio.CancelledError:
            save_world_state(self.state)
            raise


def create_game() -> tuple[Game, StartupReport]:
    startup = StartupReport()
    with startup.measure("world_data"):
        world = load_world()
    with startup.measure("clock_config"):
        config = load_time_config()
    with startup.measure("world_state"):
        state = load_world_state(world, config)
    game = Game(state=state, startup=startup)
    return game, startup