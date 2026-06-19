#!/usr/bin/env python3
"""Generate a rectangular grid of rooms as YAML for data/world.yaml."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

DIRECTIONS = {
    "north": (0, -1),
    "south": (0, 1),
    "east": (1, 0),
    "west": (-1, 0),
}
OPPOSITE = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
}


def room_id(prefix: str, x: int, y: int) -> str:
    return f"{prefix}_{x}_{y}"


def build_rooms(prefix: str, district: str, rows: int, cols: int) -> dict[str, dict]:
    rooms: dict[str, dict] = {}
    for y in range(rows):
        for x in range(cols):
            rid = room_id(prefix, x, y)
            rooms[rid] = {
                "name_zh": f"{district} 街區 ({x},{y})",
                "name_en": f"{district.title()} Block ({x},{y})",
                "description_zh": (
                    f"霓虹與酸雨交織的 {district} 街道格點 ({x},{y})。"
                    "全息廣告在積水上閃爍。"
                ),
                "description_en": (
                    f"A neon-soaked {district} street grid at ({x},{y}). "
                    "Holographic ads flicker on rain-slick pavement."
                ),
                "district": district,
                "grid_x": x,
                "grid_y": y,
                "exits": {},
            }

    for y in range(rows):
        for x in range(cols):
            rid = room_id(prefix, x, y)
            exits: dict[str, str] = {}
            for direction, (dx, dy) in DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                if 0 <= nx < cols and 0 <= ny < rows:
                    exits[direction] = room_id(prefix, nx, ny)
            rooms[rid]["exits"] = exits
    return rooms


def render_yaml(rooms: dict[str, dict], *, start_room: str | None = None) -> str:
    payload: dict = {"rooms": rooms}
    if start_room:
        payload["start_room"] = start_room
    return yaml.dump(payload, allow_unicode=True, sort_keys=False, default_flow_style=False)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a rectangular grid of rooms as YAML.",
    )
    parser.add_argument("district", help="District id stored on each room (e.g. watson)")
    parser.add_argument("rows", type=int, help="Number of rows in the grid")
    parser.add_argument("cols", type=int, help="Number of columns in the grid")
    parser.add_argument(
        "--prefix",
        help="Room id prefix (default: district name)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write YAML to this file instead of stdout",
    )
    parser.add_argument(
        "--start-room",
        help="Include start_room key (default: top-left room)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.rows < 1 or args.cols < 1:
        print("ERR: rows and cols must be at least 1", file=sys.stderr)
        return 1

    prefix = (args.prefix or args.district).strip()
    if not prefix:
        print("ERR: prefix cannot be empty", file=sys.stderr)
        return 1

    rooms = build_rooms(prefix, args.district, args.rows, args.cols)
    start = args.start_room or room_id(prefix, 0, 0)
    if start not in rooms:
        print(f"ERR: start room not in grid: {start}", file=sys.stderr)
        return 1

    text = render_yaml(rooms, start_room=start)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())