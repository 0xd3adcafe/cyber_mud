from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from shared.mature_paths import (
    braindances_mature_path,
    mature_content_available,
    mature_locale_path,
    quests_mature_path,
    romance_path,
)

ROMANCE_PATH = romance_path()
QUESTS_MATURE_PATH = quests_mature_path()
BRAINDANCES_MATURE_PATH = braindances_mature_path()


@dataclass
class MatureIssue:
    severity: str
    message: str


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _locale_keys(locale: str) -> set[str]:
    path = mature_locale_path(locale)
    data = _load_yaml(path)
    mature = data.get("mature") or {}

    def walk(node: dict, prefix: str) -> set[str]:
        keys: set[str] = set()
        for key, value in node.items():
            full = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                keys.update(walk(value, full))
            elif isinstance(value, str):
                keys.add(full)
        return keys

    return walk(mature, "mature")


def validate_mature_content(world) -> list[MatureIssue]:
    if not mature_content_available():
        return [
            MatureIssue(
                "warn",
                "mature content pack missing — init submodule: git submodule update --init data/mature",
            )
        ]
    issues: list[MatureIssue] = []
    en_keys = _locale_keys("en")
    zh_keys = _locale_keys("zh")
    missing_zh = sorted(en_keys - zh_keys)
    missing_en = sorted(zh_keys - en_keys)
    for key in missing_zh:
        issues.append(MatureIssue("error", f"mature locale missing zh key: {key}"))
    for key in missing_en:
        issues.append(MatureIssue("warn", f"mature locale missing en key: {key}"))

    romance = _load_yaml(ROMANCE_PATH).get("romances") or {}
    for rid, data in romance.items():
        npc_id = str(data.get("npc_id", rid))
        if npc_id not in world.npcs:
            issues.append(MatureIssue("error", f"romance {rid} references missing npc {npc_id}"))

    mature_bds = _load_yaml(BRAINDANCES_MATURE_PATH).get("braindances") or {}
    for bid in mature_bds:
        if bid in world.braindances and world.braindances[bid].rating != "mature":
            issues.append(MatureIssue("error", f"braindance {bid} rating must be mature"))

    mature_quests = _load_yaml(QUESTS_MATURE_PATH).get("quests") or {}
    for qid, data in mature_quests.items():
        if str(data.get("rating", "mature")) != "mature":
            issues.append(MatureIssue("error", f"quest {qid} in quests_mature.yaml must be rated mature"))
        npc_id = str(data.get("npc_id", ""))
        if npc_id and npc_id not in world.npcs:
            issues.append(MatureIssue("error", f"mature quest {qid} references missing npc {npc_id}"))

    for rid, room in world.rooms.items():
        if "mature" in room.tags:
            for direction, target in room.exits.items():
                if target not in world.rooms:
                    issues.append(MatureIssue("error", f"mature room {rid}.{direction} -> missing {target}"))

    for nid, npc in world.npcs.items():
        if "mature" in npc.tags and npc.room_id and npc.room_id not in world.rooms:
            issues.append(MatureIssue("error", f"mature npc {nid} room missing: {npc.room_id}"))

    return issues