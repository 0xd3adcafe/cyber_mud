from __future__ import annotations

import argparse

from client.app import CyberMudApp
from shared.protocol import DEFAULT_HOST, DEFAULT_PORT


def main() -> None:
    parser = argparse.ArgumentParser(description="cyber_mud client")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args, _ = parser.parse_known_args()
    CyberMudApp(args.host, args.port).run()


if __name__ == "__main__":
    main()