from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from commands import register_builtin_commands
from combat.encounter import encounter_for_player, end_encounter
from commands.registry import CommandContext, dispatch, player_meta
from entities.player import Player
from persistence.save import save_player
from persistence.world_state import load_world_state, save_world_state
from shared.i18n import t, t_list
from shared.protocol import MOTD_PREFIX, PANEL_PREFIX, meta_line, ui_line
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

    async def add_session(self, session: ClientSession) -> None:
        self.sessions.append(session)
        locale = session.player.locale
        for line in t_list(locale, "motd.lines"):
            await session.send(f"{MOTD_PREFIX}{line}")
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

        if result.broadcast_key:
            await self.broadcast_localized(
                session.player.room_id,
                result.broadcast_key,
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
                for target in self.sessions:
                    if target.player.name != event.player_name:
                        continue
                    line = event.message_kwargs.get("line", "")
                    if line:
                        await target.send(line)
                    await target.send_meta(player_meta(CommandContext(target.player, self.state, "")))

    async def _handle_combat_tick_results(self, combat_results) -> None:
        for player, combat_result in combat_results:
            session = self.session_for_player(player)
            if session and combat_result.lines:
                await session.send_lines(combat_result.lines)
            if session:
                ctx = CommandContext(player, self.state, "")
                await session.send_meta(player_meta(ctx))
            if combat_result.broadcast_key:
                await self.broadcast_localized(
                    player.room_id,
                    combat_result.broadcast_key,
                    **(combat_result.broadcast_kwargs or {}),
                )
            if combat_result.world_changed or combat_result.ended:
                save_player(player)
                save_world_state(self.state)

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
                if result.time_changed:
                    await self.broadcast_time_meta()
        except asyncio.CancelledError:
            save_world_state(self.state)
            raise


def create_game() -> Game:
    world = load_world()
    config = load_time_config()
    state = load_world_state(world, config)
    return Game(state=state)