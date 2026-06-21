from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from entities.player import Player
from shared.i18n import t
from shared.locale_content import item_label
from world.profiler import is_profiled, profiler_entry
from world.state import WorldState

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "profiler.yaml"

_CACHE: dict[str, dict[str, "TalkBranch"]] | None = None


@dataclass
class TalkBranch:
    trait: str
    bribe_item: str = ""
    quest_flag: str = ""
    quest_flag_value: str = "1"


def clear_profiler_talk_cache() -> None:
    global _CACHE
    _CACHE = None


def load_talk_branches(path: Path | None = None) -> dict[str, dict[str, TalkBranch]]:
    global _CACHE
    if _CACHE is not None and path is None:
        return _CACHE
    src = path or DATA_PATH
    raw = yaml.safe_load(src.read_text(encoding="utf-8")) if src.exists() else {}
    branches: dict[str, dict[str, TalkBranch]] = {}
    for npc_id, trait_map in (raw.get("talk_branches") or {}).items():
        npc_branches: dict[str, TalkBranch] = {}
        for trait, data in (trait_map or {}).items():
            npc_branches[str(trait)] = TalkBranch(
                trait=str(trait),
                bribe_item=str(data.get("bribe_item", "")),
                quest_flag=str(data.get("quest_flag", "")),
                quest_flag_value=str(data.get("quest_flag_value", "1")),
            )
        branches[str(npc_id)] = npc_branches
    if path is None:
        _CACHE = branches
    return branches


def _branch_line(locale: str, npc_id: str, trait: str) -> str:
    key = f"profiler.talk.{npc_id}.{trait}"
    line = t(locale, key)
    return line if line != key else ""


def _bribe_line(locale: str, npc_id: str, trait: str) -> str:
    key = f"profiler.talk.{npc_id}.{trait}_bribe"
    line = t(locale, key)
    return line if line != key else ""


def resolve_profiler_talk(
    player: Player,
    state: WorldState,
    npc_id: str,
    locale: str,
) -> tuple[list[str], bool]:
    """Return profiler-gated talk lines and whether world state changed."""
    if not is_profiled(player, npc_id):
        return [], False

    profile = profiler_entry(npc_id)
    if profile is None:
        return [], False

    npc_branches = load_talk_branches().get(npc_id)
    if not npc_branches:
        return [], False

    for trait in profile.traits:
        branch = npc_branches.get(trait)
        if branch is None:
            continue

        lines: list[str] = []
        world_changed = False
        main = _branch_line(locale, npc_id, trait)
        if main:
            lines.append(main)

        if branch.bribe_item and branch.bribe_item in player.inventory:
            player.inventory.remove(branch.bribe_item)
            world_changed = True
            item = state.world.item(branch.bribe_item)
            bribe = _bribe_line(locale, npc_id, trait)
            if bribe:
                lines.append(bribe)
            else:
                lines.append(
                    t(
                        locale,
                        "profiler.talk.bribe_ok",
                        item=item_label(item, locale) if item else branch.bribe_item,
                    )
                )

        if branch.quest_flag:
            player.quest_flags[branch.quest_flag] = branch.quest_flag_value
            world_changed = True

        if lines:
            return lines, world_changed

    return [], False