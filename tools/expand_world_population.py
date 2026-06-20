#!/usr/bin/env python3
"""Generate procedural NPCs and items for district grid rooms (W.14 scale)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "world.yaml"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "world_population.yaml"

GRID_DISTRICTS = (
    "watson",
    "tyrell",
    "combat_zone",
    "kabuki",
    "little_china",
    "corpo",
    "docks",
    "undercity",
)

DISTRICT_NPC_COUNTS: dict[str, int] = {
    "watson": 21,
    "tyrell": 11,
    "combat_zone": 11,
    "kabuki": 9,
    "undercity": 9,
    "docks": 8,
    "corpo": 8,
    "little_china": 9,
}

DISTRICT_ARCHETYPES: dict[str, list[str]] = {
    "watson": ["street_runner", "thug", "fixer"],
    "tyrell": ["lab_tech", "corp_guard", "runner"],
    "combat_zone": ["raider", "scavenger", "merc"],
    "kabuki": ["bouncer", "dealer", "dancer"],
    "little_china": ["vendor", "monk", "triad"],
    "corpo": ["corp_guard", "exec", "scout"],
    "docks": ["docker", "smuggler", "thug"],
    "undercity": ["scavenger", "ghost", "rat"],
}

ARCHETYPE_DEFS: dict[str, dict] = {
    "street_runner": {
        "name_zh": "街區行者",
        "name_en": "Street Runner",
        "hp": 35,
        "attack": 2,
        "hostile": False,
        "talk_key": "street_runner",
        "idle_msg_zh": "低頭刷著訊息，匆匆走過。",
        "idle_msg_en": "Scrolls a feed and hurries past.",
    },
    "thug": {
        "name_zh": "街頭暴徒",
        "name_en": "Street Thug",
        "hp": 42,
        "attack": 5,
        "hostile": True,
        "aggro": 6,
        "faction": "maelstrom",
        "talk_key": "street_thug",
        "loot": ["mod_chip"],
        "idle_msg_zh": "義體手臂上的刀刃在霓虹下反光。",
        "idle_msg_en": "Blades on a cyber-arm catch the neon glare.",
    },
    "fixer": {
        "name_zh": "街頭中介",
        "name_en": "Street Fixer",
        "hp": 40,
        "attack": 2,
        "hostile": False,
        "talk_key": "fixer",
        "idle_msg_zh": "低聲對著空氣嘀咕著價碼。",
        "idle_msg_en": "Mumbles prices to no one in particular.",
    },
    "lab_tech": {
        "name_zh": "實驗室技師",
        "name_en": "Lab Tech",
        "hp": 38,
        "attack": 2,
        "hostile": False,
        "faction": "tyrell",
        "talk_key": "lab_tech",
        "idle_msg_zh": "抱著樣本箱匆匆穿過走廊。",
        "idle_msg_en": "Rushes past with a sample case.",
    },
    "corp_guard": {
        "name_zh": "企業保全",
        "name_en": "Corpo Guard",
        "hp": 65,
        "attack": 6,
        "hostile": False,
        "faction": "arasaka",
        "talk_key": "corp_guard",
        "idle_msg_zh": "掃描證件與武器。",
        "idle_msg_en": "Scans IDs and weapons.",
    },
    "runner": {
        "name_zh": "企業跑腿",
        "name_en": "Corpo Runner",
        "hp": 36,
        "attack": 2,
        "hostile": False,
        "talk_key": "runner",
        "idle_msg_zh": "抱著加密平板快步離開。",
        "idle_msg_en": "Clutches an encrypted slate and moves on.",
    },
    "raider": {
        "name_zh": "戰區掠奪者",
        "name_en": "Zone Raider",
        "hp": 48,
        "attack": 6,
        "hostile": True,
        "aggro": 8,
        "faction": "maelstrom",
        "talk_key": "raider",
        "loot": ["pipe"],
    },
    "scavenger": {
        "name_zh": "拾荒者",
        "name_en": "Scavenger",
        "hp": 32,
        "attack": 3,
        "hostile": False,
        "talk_key": "scavenger",
        "idle_msg_zh": "翻找廢墟裡還能賣的零件。",
        "idle_msg_en": "Digs for parts worth selling in the rubble.",
    },
    "merc": {
        "name_zh": "雇傭兵",
        "name_en": "Mercenary",
        "hp": 55,
        "attack": 7,
        "hostile": True,
        "aggro": 7,
        "talk_key": "merc",
        "equipment": {"weapon_primary": "liberty_pistol"},
    },
    "bouncer": {
        "name_zh": "門禁保鑣",
        "name_en": "Bouncer",
        "hp": 50,
        "attack": 5,
        "hostile": False,
        "talk_key": "bouncer",
        "idle_msg_zh": "掃視排隊的人潮。",
        "idle_msg_en": "Eyes the queue.",
    },
    "dealer": {
        "name_zh": "灰市攤販",
        "name_en": "Gray Dealer",
        "hp": 38,
        "attack": 3,
        "hostile": False,
        "talk_key": "dealer",
        "idle_msg_zh": "敲了敲晶片托盤。",
        "idle_msg_en": "Taps a tray of chips.",
    },
    "dancer": {
        "name_zh": "全息舞者",
        "name_en": "Holo Dancer",
        "hp": 30,
        "attack": 1,
        "hostile": False,
        "talk_key": "dancer",
        "idle_msg_zh": "殘影在霓虹裡旋轉。",
        "idle_msg_en": "A ghost image spins in the neon.",
    },
    "vendor": {
        "name_zh": "路邊攤販",
        "name_en": "Street Vendor",
        "hp": 34,
        "attack": 2,
        "hostile": False,
        "talk_key": "vendor",
        "idle_msg_zh": "攪拌著冒熱氣的麵湯。",
        "idle_msg_en": "Stirs steaming noodle broth.",
    },
    "monk": {
        "name_zh": "神社行者",
        "name_en": "Shrine Walker",
        "hp": 36,
        "attack": 1,
        "hostile": False,
        "talk_key": "monk",
        "idle_msg_zh": "低聲念誦，手持香爐。",
        "idle_msg_en": "Murmurs a prayer, incense in hand.",
    },
    "triad": {
        "name_zh": "幫會打手",
        "name_en": "Triad Enforcer",
        "hp": 45,
        "attack": 5,
        "hostile": True,
        "aggro": 5,
        "talk_key": "triad",
        "equipment": {"weapon_primary": "knife"},
    },
    "exec": {
        "name_zh": "企業主管",
        "name_en": "Corpo Exec",
        "hp": 40,
        "attack": 2,
        "hostile": False,
        "faction": "arasaka",
        "talk_key": "exec",
        "idle_msg_zh": "對著全息會議點頭。",
        "idle_msg_en": "Nods at a holo conference.",
    },
    "scout": {
        "name_zh": "企業偵察員",
        "name_en": "Corpo Scout",
        "hp": 48,
        "attack": 4,
        "hostile": False,
        "faction": "militech",
        "talk_key": "scout",
        "idle_msg_zh": "義眼不停掃描路人識別碼。",
        "idle_msg_en": "Cyber eyes scan every passerby.",
    },
    "docker": {
        "name_zh": "碼頭工人",
        "name_en": "Dock Worker",
        "hp": 40,
        "attack": 3,
        "hostile": False,
        "talk_key": "docker",
        "idle_msg_zh": "拖著貨櫃吊鉤匆匆走過。",
        "idle_msg_en": "Hauls a container hook past you.",
    },
    "smuggler": {
        "name_zh": "走私客",
        "name_en": "Smuggler",
        "hp": 38,
        "attack": 3,
        "hostile": False,
        "talk_key": "smuggler",
        "idle_msg_zh": "別問貨從哪來。",
        "idle_msg_en": "Do not ask where the cargo came from.",
    },
    "ghost": {
        "name_zh": "地下幽影",
        "name_en": "Undercity Ghost",
        "hp": 33,
        "attack": 4,
        "hostile": False,
        "talk_key": "ghost",
        "idle_msg_zh": "半透明的殘影一閃而過。",
        "idle_msg_en": "A translucent afterimage flickers past.",
    },
    "rat": {
        "name_zh": "鼠幫浪人",
        "name_en": "Rat Gang Ronin",
        "hp": 36,
        "attack": 4,
        "hostile": True,
        "aggro": 6,
        "talk_key": "rat_gang",
        "loot": ["rusty_key"],
    },
}

NEW_ITEMS: dict[str, dict] = {
    "gutter_blade": {
        "name_zh": "陰溝短刃",
        "name_en": "Gutter Blade",
        "description_zh": "磨過的街頭短刃，便宜但夠用。",
        "description_en": "A filed street blade—cheap but sharp enough.",
        "takeable": True,
        "slot": "weapon",
        "weapon_type": "blade",
        "weapon_class": "melee",
        "weapon_damage": 5,
        "value": 18,
    },
    "street_stim": {
        "name_zh": "街頭興奮劑",
        "name_en": "Street Stim",
        "description_zh": "黑市單劑興奮劑，能撐過一場衝突。",
        "description_en": "A black-market stim dose for one ugly fight.",
        "takeable": True,
        "consumable": "medicine",
        "hp_restore": 20,
        "value": 22,
    },
    "corpo_token": {
        "name_zh": "企業通行證",
        "name_en": "Corpo Pass Token",
        "description_zh": "過期仍值錢的企業識別籌碼。",
        "description_en": "An expired corpo pass chip—still worth something.",
        "takeable": True,
        "value": 40,
    },
    "smuggler_pack": {
        "name_zh": "走私壓縮包",
        "name_en": "Smuggler Pack",
        "description_zh": "碼頭流通的壓縮口糧與電解液組合。",
        "description_en": "Dock-grade ration and electrolyte combo.",
        "takeable": True,
        "consumable": "food",
        "hp_restore": 10,
        "ram_restore": 1,
        "value": 16,
    },
    "combat_scrap": {
        "name_zh": "戰區廢鐵",
        "name_en": "Combat Zone Scrap",
        "description_zh": "戰鬥區撿來的義體殘件，回收商會收。",
        "description_en": "Cyber scrap from the zone—buyers still pay.",
        "takeable": True,
        "value": 28,
    },
    "neon_patch": {
        "name_zh": "霓虹貼片",
        "name_en": "Neon Patch",
        "description_zh": "歌舞伎區流行的發光裝飾貼片。",
        "description_en": "A glowing Kabuki fashion patch.",
        "takeable": True,
        "value": 14,
    },
    "grid_ration": {
        "name_zh": "格點口糧",
        "name_en": "Grid Ration",
        "description_zh": "企業配發的壓縮口糧。",
        "description_en": "Corporate-issue calorie brick.",
        "takeable": True,
        "consumable": "food",
        "hp_restore": 8,
        "value": 6,
    },
    "black_ice_shard": {
        "name_zh": "黑冰碎片",
        "name_en": "Black Ice Shard",
        "description_zh": "非法 ICE 殘片，駭客會出價收購。",
        "description_en": "Illegal ICE shard—hackers pay for these.",
        "takeable": True,
        "value": 55,
    },
    "tyrell_sample": {
        "name_zh": "泰瑞樣本管",
        "name_en": "Tyrell Sample Vial",
        "description_zh": "實驗室遺落的樣本管，標籤已模糊。",
        "description_en": "A lost lab vial with a faded label.",
        "takeable": True,
        "value": 70,
    },
    "dock_manifest": {
        "name_zh": "碼頭貨單",
        "name_en": "Dock Manifest",
        "description_zh": "走私貨櫃的加密貨單影本。",
        "description_en": "An encrypted copy of a smuggler manifest.",
        "takeable": True,
        "value": 32,
    },
    "kabuki_token": {
        "name_zh": "歌舞伎籌碼",
        "name_en": "Kabuki Token",
        "description_zh": "夜總會兌換用的霓虹籌碼。",
        "description_en": "A neon token for the nightlife circuit.",
        "takeable": True,
        "value": 25,
    },
    "china_incense": {
        "name_zh": "小中國線香",
        "name_en": "Little China Incense",
        "description_zh": "小中國街廟口常見的線香束。",
        "description_en": "Incense bundle from Little China shrines.",
        "takeable": True,
        "value": 9,
    },
    "undercity_filament": {
        "name_zh": "地下光纖",
        "name_en": "Undercity Filament",
        "description_zh": "地下城剝下來的舊光纖，仍能導電。",
        "description_en": "Stripped undercity fiber—still conducts.",
        "takeable": True,
        "value": 20,
    },
}

ROOM_LOOT_ITEMS = list(NEW_ITEMS.keys())

GRID_ROOM_RE = re.compile(r"^([a-z_]+)_(\d+)_(\d+)$")


def _grid_rooms(raw: dict, district: str) -> list[str]:
    rooms = raw.get("rooms") or {}
    matches: list[str] = []
    for rid, data in rooms.items():
        if data.get("district") != district:
            continue
        if GRID_ROOM_RE.match(rid):
            matches.append(rid)
    return sorted(matches)


def _neighbor_patrol(rooms: dict, room_id: str) -> list[str]:
    room = rooms.get(room_id) or {}
    exits = room.get("exits") or {}
    if not exits:
        return [room_id]
    first = next(iter(exits.values()))
    return [room_id, first]


def _pick_rooms(grid_rooms: list[str], count: int) -> list[str]:
    if count <= 0 or not grid_rooms:
        return []
    if count >= len(grid_rooms):
        return grid_rooms
    step = len(grid_rooms) / count
    picks: list[str] = []
    for i in range(count):
        idx = int(i * step)
        picks.append(grid_rooms[idx])
    return picks


def build_population(raw: dict) -> dict:
    rooms = raw.get("rooms") or {}
    npcs: dict[str, dict] = {}
    room_items: dict[str, list[str]] = {}

    for district, count in DISTRICT_NPC_COUNTS.items():
        grid_rooms = _grid_rooms(raw, district)
        archetypes = DISTRICT_ARCHETYPES[district]
        for index, room_id in enumerate(_pick_rooms(grid_rooms, count)):
            archetype = archetypes[index % len(archetypes)]
            spec = dict(ARCHETYPE_DEFS[archetype])
            name_zh = spec.pop("name_zh")
            name_en = spec.pop("name_en")
            match = GRID_ROOM_RE.match(room_id)
            suffix = f"{match.group(2)}_{match.group(3)}" if match else str(index)
            npc_id = f"{district}_{archetype}_{suffix}"
            npc: dict = {
                "name_zh": name_zh,
                "name_en": name_en,
                "room_id": room_id,
                "description_zh": f"{district} 格點上的{name_zh}。",
                "description_en": f"A {name_en.lower()} on the {district} grid.",
                "hp": spec.pop("hp"),
                "attack": spec.pop("attack", 3),
                "hostile": spec.pop("hostile", False),
            }
            for key in (
                "aggro",
                "faction",
                "talk_key",
                "idle_msg_zh",
                "idle_msg_en",
                "loot",
                "equipment",
            ):
                if key in spec:
                    npc[key] = spec.pop(key)
            if npc.get("hostile"):
                npc["patrol"] = _neighbor_patrol(rooms, room_id)
            npcs[npc_id] = npc

    loot_rooms: list[str] = []
    for district in GRID_DISTRICTS:
        loot_rooms.extend(_pick_rooms(_grid_rooms(raw, district), 4))
    for index, room_id in enumerate(loot_rooms[: len(ROOM_LOOT_ITEMS)]):
        item_id = ROOM_LOOT_ITEMS[index % len(ROOM_LOOT_ITEMS)]
        room_items.setdefault(room_id, []).append(item_id)

    return {
        "items": NEW_ITEMS,
        "npcs": npcs,
        "room_items": room_items,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate world_population.yaml overlay.")
    parser.add_argument("--source", type=Path, default=DATA_PATH)
    parser.add_argument("-o", "--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    raw = yaml.safe_load(args.source.read_text(encoding="utf-8")) or {}
    base_npcs = len(raw.get("npcs") or {})
    base_items = len(raw.get("items") or {})
    payload = build_population(raw)
    total_npcs = base_npcs + len(payload["npcs"])
    total_items = base_items + len(payload["items"])
    print(
        f"npcs: {base_npcs} + {len(payload['npcs'])} -> {total_npcs}",
        file=sys.stderr,
    )
    print(
        f"items: {base_items} + {len(payload['items'])} -> {total_items}",
        file=sys.stderr,
    )
    print(f"room_items: +{len(payload['room_items'])} rooms", file=sys.stderr)
    if args.dry_run:
        return 0
    args.output.write_text(
        yaml.dump(payload, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())