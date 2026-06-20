from __future__ import annotations

import argparse
import asyncio
import time

from entities.player import Player
from server.game import ClientSession, Game, create_game
from server.heartbeat import heartbeat_loop, log_server_event
from shared.i18n import t
from shared.protocol import DEFAULT_HOST, DEFAULT_PORT, ENCODING, MAX_LINE_BYTES
from shared.server_locale import server_locale


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, game: Game) -> None:
    session = ClientSession(
        writer=writer,
        player=Player(room_id=game.state.world.start_room),
    )
    await game.add_session(session)
    loc = server_locale()
    log_server_event(t(loc, "server.connect", count=str(len(game.sessions))))
    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            if len(data) > MAX_LINE_BYTES:
                await game.handle_oversized_line(session)
                break
            line = data.decode(ENCODING).rstrip("\r\n")
            if not line:
                continue
            keep_open = await game.handle_command(session, line)
            if not keep_open:
                break
    except (ConnectionResetError, asyncio.IncompleteReadError):
        pass
    finally:
        await game.notify_disconnect(session)
        label = session.player.name if session.player.named else t(loc, "server.guest")
        game.remove_session(session)
        log_server_event(
            t(loc, "server.disconnect", name=label, count=str(len(game.sessions)))
        )
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass


async def run_server(host: str, port: int, *, dev: bool = False) -> None:
    from shared.startup import StartupReport

    boot = StartupReport()
    loc = server_locale()
    with boot.measure("load_game"):
        game, load_report = create_game()
    started_at = time.monotonic()
    tick_task = asyncio.create_task(game.tick_loop())
    combat_task = asyncio.create_task(game.combat_tick_loop())
    heartbeat_task = asyncio.create_task(
        heartbeat_loop(
            game,
            interval=game.state.time_config.tick_interval_seconds,
            started_at=started_at,
            dev=dev,
        )
    )
    dev_task = None
    if dev:
        from server.dev_reload import start_dev_watcher

        dev_task = asyncio.create_task(start_dev_watcher(game))
        print(t(loc, "server.dev_watch"))
    with boot.measure("network_listen"):
        server = await asyncio.start_server(lambda r, w: handle_client(r, w, game), host=host, port=port)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
    world = game.state.world
    print(load_report.format_console(title=t(loc, "server.load_title")))
    print(
        t(
            loc,
            "server.content",
            rooms=str(len(world.rooms)),
            items=str(len(world.items)),
            npcs=str(len(world.npcs)),
        )
    )
    print(boot.format_console(title=t(loc, "server.boot_title")))
    print(t(loc, "server.listening", addrs=addrs))
    try:
        async with server:
            await server.serve_forever()
    finally:
        tick_task.cancel()
        combat_task.cancel()
        heartbeat_task.cancel()
        if dev_task is not None:
            dev_task.cancel()
        for task in (tick_task, combat_task, heartbeat_task, dev_task):
            if task is None:
                continue
            try:
                await task
            except asyncio.CancelledError:
                pass


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="cyber_mud server")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--dev", action="store_true", help="Development mode (data + code hot-reload)")
    args = parser.parse_args(argv)
    try:
        asyncio.run(run_server(args.host, args.port, dev=args.dev))
    except KeyboardInterrupt:
        print(f"\n{t(server_locale(), 'server.stopped')}")


if __name__ == "__main__":
    main()