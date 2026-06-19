from __future__ import annotations

import argparse
import asyncio

from entities.player import Player
from server.game import ClientSession, Game, create_game
from shared.protocol import DEFAULT_HOST, DEFAULT_PORT, ENCODING


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, game: Game) -> None:
    session = ClientSession(
        writer=writer,
        player=Player(room_id=game.state.world.start_room),
    )
    await game.add_session(session)
    try:
        while True:
            data = await reader.readline()
            if not data:
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
        game.remove_session(session)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass


async def run_server(host: str, port: int, *, dev: bool = False) -> None:
    game = create_game()
    tick_task = asyncio.create_task(game.tick_loop())
    dev_task = None
    if dev:
        from server.dev_reload import start_dev_watcher

        dev_task = asyncio.create_task(start_dev_watcher(game))
        print("dev 模式：監看 data/*.yaml 熱重載")
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, game), host=host, port=port)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
    print(f"cyber_mud server 監聽 {addrs}")
    try:
        async with server:
            await server.serve_forever()
    finally:
        tick_task.cancel()
        if dev_task is not None:
            dev_task.cancel()
        for task in (tick_task, dev_task):
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
    parser.add_argument("--dev", action="store_true", help="開發模式（data 熱重載）")
    args = parser.parse_args(argv)
    try:
        asyncio.run(run_server(args.host, args.port, dev=args.dev))
    except KeyboardInterrupt:
        print("\n伺服器已停止")


if __name__ == "__main__":
    main()