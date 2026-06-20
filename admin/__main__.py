from __future__ import annotations

import subprocess
import sys

from persistence.save import delete_save, list_saves
from world.loader import load_world
from world.quest_author import validate_quests


def validate() -> int:
    world = load_world()
    assert world.start_room in world.rooms, "start_room missing"
    for rid, room in world.rooms.items():
        for direction, target in room.exits.items():
            assert target in world.rooms, f"{rid}.{direction} -> missing {target}"
    print(f"OK: world valid ({len(world.rooms)} rooms, {len(world.items)} items, {len(world.npcs)} npcs)")
    quest_errors = [issue for issue in validate_quests(world) if issue.severity == "error"]
    quest_warnings = [issue for issue in validate_quests(world) if issue.severity == "warn"]
    for issue in quest_warnings:
        print(f"WARN [quest:{issue.quest_id}] {issue.message}")
    if quest_errors:
        for issue in quest_errors:
            print(f"ERR  [quest:{issue.quest_id}] {issue.message}")
        return 1
    print(f"OK: quests valid ({len(world.quests)} quests, {len(quest_warnings)} warnings)")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"], check=False)
    return result.returncode


def quests_cmd() -> int:
    from tools.quest_author import main as quest_main

    return quest_main(sys.argv[2:])


def saves() -> int:
    names = list_saves()
    if not names:
        print("No saves.")
        return 0
    for name in names:
        print(name)
    return 0


def delete_save_cmd() -> int:
    if len(sys.argv) < 3:
        print("ERR: usage: delete-save <name>")
        return 1
    name = sys.argv[2]
    if not delete_save(name):
        print(f"ERR: save not found: {name}")
        return 1
    print(f"OK: deleted save {name}")
    return 0


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if cmd == "validate":
        raise SystemExit(validate())
    if cmd == "saves":
        raise SystemExit(saves())
    if cmd == "delete-save":
        raise SystemExit(delete_save_cmd())
    if cmd == "quests":
        raise SystemExit(quests_cmd())
    print(f"ERR: unknown command: {cmd}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()