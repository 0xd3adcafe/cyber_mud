from __future__ import annotations

from dataclasses import dataclass, field

import yaml

from world.content import Quest, QuestStage
from world.quests import quest_stages
from world.world import World

VALID_OBJECTIVE_TYPES = frozenset(
    {"talk_npc", "visit_room", "interact", "defeat_npc", "have_item", "hack_net", "give_npc"}
)


@dataclass(frozen=True)
class QuestIssue:
    quest_id: str
    severity: str
    message: str


@dataclass
class NpcQuestRole:
    quest_id: str
    roles: list[str] = field(default_factory=list)


def resolve_target_label(world: World, objective_type: str, target: str) -> str:
    if objective_type == "talk_npc":
        npc = world.npc(target)
        if npc:
            return f"{target} ({npc.name_zh or npc.name_en})"
    elif objective_type == "visit_room":
        room = world.room(target)
        if room:
            return f"{target} ({room.name_zh or room.name_en})"
    elif objective_type == "interact":
        obj = world.interactable(target)
        if obj:
            return f"{target} ({obj.name_zh or obj.name_en})"
    elif objective_type == "defeat_npc":
        npc = world.npc(target)
        if npc:
            return f"{target} ({npc.name_zh or npc.name_en})"
    elif objective_type == "have_item":
        item = world.item(target)
        if item:
            return f"{target} ({item.name_zh or item.name_en})"
    elif objective_type == "hack_net":
        node = world.net_nodes.get(target)
        if node:
            return f"{target} ({node.name_zh or node.name_en})"
    elif objective_type == "give_npc":
        npc = world.npc(target)
        if npc:
            return f"{target} ({npc.name_zh or npc.name_en})"
    return target


def _target_exists(world: World, objective_type: str, target: str) -> bool:
    if not target:
        return False
    if objective_type == "talk_npc":
        return world.npc(target) is not None
    if objective_type == "visit_room":
        return world.room(target) is not None
    if objective_type == "interact":
        return world.interactable(target) is not None
    if objective_type == "defeat_npc":
        return world.npc(target) is not None
    if objective_type == "have_item":
        return world.item(target) is not None
    if objective_type == "hack_net":
        return target in world.net_nodes
    if objective_type == "give_npc":
        return world.npc(target) is not None
    return False


def validate_quest(world: World, quest: Quest) -> list[QuestIssue]:
    issues: list[QuestIssue] = []
    qid = quest.id

    if not quest.name_zh.strip():
        issues.append(QuestIssue(qid, "error", "缺少 name_zh"))

    stages = quest_stages(quest)
    if not stages:
        issues.append(QuestIssue(qid, "error", "沒有 stages 或 objective_type"))

    if quest.npc_id and world.npc(quest.npc_id) is None:
        issues.append(QuestIssue(qid, "error", f"npc_id 不存在：{quest.npc_id}"))

    if quest.complete_npc_id and world.npc(quest.complete_npc_id) is None:
        issues.append(QuestIssue(qid, "error", f"complete_npc_id 不存在：{quest.complete_npc_id}"))

    if not quest.complete_npc_id:
        issues.append(QuestIssue(qid, "warn", "未設定 complete_npc_id"))

    if quest.requires_quest and world.quest(quest.requires_quest) is None:
        issues.append(QuestIssue(qid, "error", f"requires_quest 不存在：{quest.requires_quest}"))

    for item_id in quest.reward_items:
        if world.item(item_id) is None:
            issues.append(QuestIssue(qid, "error", f"reward_items 不存在：{item_id}"))

    for index, stage in enumerate(stages, start=1):
        if stage.objective_type not in VALID_OBJECTIVE_TYPES:
            issues.append(
                QuestIssue(
                    qid,
                    "error",
                    f"stage {index} 無效 objective_type：{stage.objective_type!r}",
                )
            )
            continue
        if not _target_exists(world, stage.objective_type, stage.objective_target):
            issues.append(
                QuestIssue(
                    qid,
                    "error",
                    f"stage {index} 目標不存在：{stage.objective_type} → {stage.objective_target}",
                )
            )
        if stage.objective_type == "give_npc" and stage.objective_item:
            if world.item(stage.objective_item) is None:
                issues.append(
                    QuestIssue(
                        qid,
                        "error",
                        f"stage {index} objective_item 不存在：{stage.objective_item}",
                    )
                )

    stage_npcs = {
        stage.objective_target
        for stage in stages
        if stage.objective_type == "talk_npc"
    }
    if quest.complete_npc_id and quest.complete_npc_id not in stage_npcs and len(stages) > 1:
        issues.append(
            QuestIssue(
                qid,
                "warn",
                f"complete_npc {quest.complete_npc_id} 未出現在任何 talk_npc 階段",
            )
        )

    for npc in world.npcs.values():
        if npc.quest_id != qid:
            continue
        if quest.npc_id and npc.id != quest.npc_id and npc.id not in stage_npcs:
            issues.append(
                QuestIssue(
                    qid,
                    "warn",
                    f"NPC {npc.id} 的 quest_id 指向此任務，但非 giver 或 stage 目標",
                )
            )

    return issues


def validate_quests(world: World) -> list[QuestIssue]:
    issues: list[QuestIssue] = []
    for quest in world.quests.values():
        issues.extend(validate_quest(world, quest))
    return issues


def format_stage_line(world: World, index: int, stage: QuestStage) -> str:
    label = resolve_target_label(world, stage.objective_type, stage.objective_target)
    return f"  {index}. {stage.objective_type} → {label}"


def format_quest_outline(quest: Quest, world: World) -> str:
    lines = [f"◈ {quest.id} — {quest.name_zh or quest.name_en or quest.id}"]
    if quest.name_en and quest.name_zh:
        lines.append(f"   {quest.name_en}")

    if quest.npc_id:
        giver = resolve_target_label(world, "talk_npc", quest.npc_id)
        lines.append(f"發佈 NPC：{giver}")
    if quest.complete_npc_id:
        completer = resolve_target_label(world, "talk_npc", quest.complete_npc_id)
        lines.append(f"交件 NPC：{completer}")
    if quest.street_cred_req:
        lines.append(f"聲望需求：{quest.street_cred_req}")

    stages = quest_stages(quest)
    lines.append("")
    lines.append("劇本流程：")
    for index, stage in enumerate(stages, start=1):
        lines.append(format_stage_line(world, index, stage))
    if quest.complete_npc_id:
        lines.append(f"  {len(stages) + 1}. talk_npc → {resolve_target_label(world, 'talk_npc', quest.complete_npc_id)}（交件）")

    rewards = []
    if quest.reward_gold:
        rewards.append(f"{quest.reward_gold} 金")
    if quest.reward_xp:
        rewards.append(f"{quest.reward_xp} XP")
    if quest.reward_street_cred:
        rewards.append(f"{quest.reward_street_cred} 聲望")
    if rewards:
        lines.append("")
        lines.append(f"獎勵：{' · '.join(rewards)}")

    cast: dict[str, set[str]] = {}
    if quest.npc_id:
        cast.setdefault(quest.npc_id, set()).add("發佈")
    if quest.complete_npc_id:
        cast.setdefault(quest.complete_npc_id, set()).add("交件")
    for index, stage in enumerate(stages, start=1):
        if stage.objective_type == "talk_npc":
            cast.setdefault(stage.objective_target, set()).add(f"階段{index}")
        elif stage.objective_type == "visit_room":
            cast.setdefault(stage.objective_target, set()).add(f"階段{index}·地點")
        elif stage.objective_type == "interact":
            cast.setdefault(stage.objective_target, set()).add(f"階段{index}·互動")

    if cast:
        lines.append("")
        lines.append("角色／目標：")
        for target_id in sorted(cast):
            roles = "、".join(sorted(cast[target_id]))
            label = resolve_target_label(
                world,
                "talk_npc" if world.npc(target_id) else (
                    "visit_room" if world.room(target_id) else "interact"
                ),
                target_id,
            )
            lines.append(f"  · {label} [{roles}]")

    return "\n".join(lines)


def npc_quest_roles(world: World) -> dict[str, list[NpcQuestRole]]:
    roles: dict[str, dict[str, set[str]]] = {}
    for quest in world.quests.values():
        if quest.npc_id:
            roles.setdefault(quest.npc_id, {}).setdefault(quest.id, set()).add("發佈")
        if quest.complete_npc_id:
            roles.setdefault(quest.complete_npc_id, {}).setdefault(quest.id, set()).add("交件")
        for index, stage in enumerate(quest_stages(quest), start=1):
            if stage.objective_type == "talk_npc":
                roles.setdefault(stage.objective_target, {}).setdefault(quest.id, set()).add(f"階段{index}")
        for npc in world.npcs.values():
            if npc.quest_id == quest.id:
                roles.setdefault(npc.id, {}).setdefault(quest.id, set()).add("連結")

    out: dict[str, list[NpcQuestRole]] = {}
    for npc_id, quest_map in sorted(roles.items()):
        out[npc_id] = [
            NpcQuestRole(quest_id=qid, roles=sorted(role_set))
            for qid, role_set in sorted(quest_map.items())
        ]
    return out


def format_npc_quest_report(world: World, npc_id: str) -> str:
    npc = world.npc(npc_id)
    if npc is None:
        return f"ERR: NPC 不存在：{npc_id}"

    label = npc.name_zh or npc.name_en or npc_id
    lines = [f"◈ {npc_id} — {label} @ {npc.room_id}"]
    if npc.quest_id:
        lines.append(f"quest_id 欄位：{npc.quest_id}")

    all_roles = npc_quest_roles(world).get(npc_id, [])
    if not all_roles:
        lines.append("（未參與任何任務編排）")
        return "\n".join(lines)

    lines.append("")
    for entry in all_roles:
        quest = world.quest(entry.quest_id)
        name = quest.name_zh if quest else entry.quest_id
        role_text = "、".join(entry.roles)
        lines.append(f"  · {entry.quest_id} ({name}) — {role_text}")
    return "\n".join(lines)


def scaffold_quest_yaml(
    quest_id: str,
    *,
    giver: str,
    complete: str,
    stages: list[tuple[str, str]],
    name_zh: str = "TODO 任務名稱",
    name_en: str = "TODO Quest Name",
    street_cred_req: int = 0,
    reward_gold: int = 0,
    reward_xp: int = 0,
    reward_street_cred: int = 0,
) -> str:
    payload: dict = {
        "name_zh": name_zh,
        "name_en": name_en,
        "npc_id": giver,
        "description_zh": "TODO 任務描述",
        "description_en": "TODO quest description",
        "hint_zh": "TODO 提示",
        "hint_en": "TODO hint",
        "complete_npc_id": complete,
        "reward_gold": reward_gold,
        "reward_xp": reward_xp,
        "reward_street_cred": reward_street_cred,
        "stages": [
            {"objective_type": kind, "objective_target": target}
            for kind, target in stages
        ],
    }
    if street_cred_req:
        payload["street_cred_req"] = street_cred_req
    return yaml.dump({quest_id: payload}, allow_unicode=True, sort_keys=False, default_flow_style=False)


def format_quest_list_line(quest: Quest, world: World) -> str:
    stage_count = len(quest_stages(quest))
    giver = quest.npc_id or "—"
    complete = quest.complete_npc_id or "—"
    req = f" sc≥{quest.street_cred_req}" if quest.street_cred_req else ""
    rewards = []
    if quest.reward_gold:
        rewards.append(f"{quest.reward_gold}g")
    if quest.reward_xp:
        rewards.append(f"{quest.reward_xp}xp")
    if quest.reward_street_cred:
        rewards.append(f"+{quest.reward_street_cred}聲望")
    reward_text = "+".join(rewards) if rewards else "—"
    name = quest.name_zh or quest.id
    return f"{quest.id:<16} [{stage_count} 階]  發佈:{giver}  交件:{complete}{req}  獎勵:{reward_text}  {name}"