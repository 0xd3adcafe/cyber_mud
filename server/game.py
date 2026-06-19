from __future__ import annotations

from dataclasses import dataclass, field

from commands import register_builtin_commands
from commands.registry import CommandContext, dispatch, player_meta
from entities.player import Player
from persistence.save import save_player
from shared.i18n import t, t_list
from shared.protocol import MOTD_PREFIX, meta_line
from world.loader import load_world
from world.state import WorldState

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

        await session.send_lines(result.lines)
        if result.meta:
            await session.send_meta(result.meta)

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

        if session.player.named and (result.world_changed or result.moved or result.auth_event):
            save_player(session.player)

        return not result.quit_game

    async def notify_disconnect(self, session: ClientSession) -> None:
        if session.player.named:
            save_player(session.player)
            await self.broadcast_localized(
                session.player.room_id,
                "game.offline",
                exclude=session,
                name=session.player.name,
            )


def create_game() -> Game:
    world = load_world()
    state = WorldState(world=world, room_items={"square": ["glowstick"]})
    return Game(state=state)