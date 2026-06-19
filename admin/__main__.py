from __future__ import annotations

import subprocess
import sys

from world.loader import load_world


def validate() -> int:
    world = load_world()
    assert world.start_room in world.rooms, "start_room missing"
    for rid, room in world.rooms.items():
        for direction, target in room.exits.items():
            assert target in world.rooms, f"{rid}.{direction} -> missing {target}"
    print(f"OK: world valid ({len(world.rooms)} rooms, {len(world.items)} items, {len(world.npcs)} npcs)")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"], check=False)
    return result.returncode


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if cmd == "validate":
        raise SystemExit(validate())
    print(f"ERR: unknown command: {cmd}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()