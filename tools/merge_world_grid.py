#!/usr/bin/env python3
"""Merge procedural district grids into data/world.yaml."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from tools.generate_world import OPPOSITE, build_rooms

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "world.yaml"

GRID_SPECS: list[tuple[str, int, int]] = [
    ("watson", 8, 8),
    ("tyrell", 6, 6),
    ("combat_zone", 6, 6),
    ("kabuki", 5, 5),
    ("little_china", 4, 4),
    ("corpo", 4, 4),
    ("docks", 4, 4),
    ("undercity", 5, 5),
]

EXTRA_HUB_ROOMS: dict[str, dict] = {
    "tyrell_plaza": {
        "name_zh": "泰瑞廣場",
        "name_en": "Tyrell Plaza",
        "description_zh": "高聳實驗室大樓與冷色全息廣告，精英與禁忌科技交會之地。",
        "description_en": "Towering labs and cold holo ads—elites and forbidden tech meet here.",
        "district": "tyrell",
        "grid_x": 0,
        "grid_y": 0,
        "tags": ["transit", "corpo"],
        "exits": {"west": "corpo_plaza", "south": "tyrell_3_5"},
    },
    "combat_zone_gate": {
        "name_zh": "戰鬥區界碑",
        "name_en": "Combat Zone Gate",
        "description_zh": "燒毀的界碑與塗鴉警告：越過此線，規則由槍桿決定。",
        "description_en": "A scorched marker and graffiti warn: past this line, guns set the rules.",
        "district": "combat_zone",
        "grid_x": 0,
        "grid_y": 0,
        "tags": ["transit"],
        "exits": {"west": "docks", "south": "combat_zone_3_0"},
    },
}

# (hub_room_id, hub_direction, grid_room_id)
HUB_GRID_LINKS: list[tuple[str, str, str]] = [
    ("ripper_clinic", "north", "watson_3_2"),
    ("kabuki_bazaar", "north", "kabuki_2_3"),
    ("little_china_gate", "south", "little_china_2_0"),
    ("corpo_plaza", "north", "corpo_3_1"),
    ("corpo_plaza", "east", "tyrell_plaza"),
    ("docks", "south", "docks_2_1"),
    ("docks", "east", "combat_zone_gate"),
    ("bd_den", "east", "undercity_4_2"),
]


def _link_bidirectional(rooms: dict[str, dict], a_id: str, a_dir: str, b_id: str) -> None:
    b_dir = OPPOSITE[a_dir]
    rooms[a_id].setdefault("exits", {})[a_dir] = b_id
    rooms[b_id].setdefault("exits", {})[b_dir] = a_id


def merge_grids(raw: dict) -> dict:
    rooms: dict[str, dict] = dict(raw.get("rooms") or {})
    for hub_id, data in EXTRA_HUB_ROOMS.items():
        if hub_id not in rooms:
            rooms[hub_id] = dict(data)

    for district, rows, cols in GRID_SPECS:
        generated = build_rooms(district, district, rows, cols)
        for rid, room in generated.items():
            if rid in rooms:
                continue
            rooms[rid] = room

    for hub_id, direction, grid_id in HUB_GRID_LINKS:
        if hub_id not in rooms or grid_id not in rooms:
            raise ValueError(f"hub link missing room: {hub_id} / {grid_id}")
        _link_bidirectional(rooms, hub_id, direction, grid_id)

    raw["rooms"] = rooms
    return raw


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Merge procedural grids into data/world.yaml.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DATA_PATH,
        help="World YAML path (default: data/world.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print room count only; do not write.",
    )
    args = parser.parse_args(argv)

    src = args.output
    raw = yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    before = len(raw.get("rooms") or {})
    merged = merge_grids(raw)
    after = len(merged.get("rooms") or {})
    print(f"rooms: {before} -> {after} (+{after - before})", file=sys.stderr)
    if args.dry_run:
        return 0
    src.write_text(yaml.dump(merged, allow_unicode=True, sort_keys=False, default_flow_style=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())