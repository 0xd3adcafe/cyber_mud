from __future__ import annotations

from entities.player import Player
from shared.i18n import t
from world.content import Quest, QuestStage
from world.state import WorldState


def quest_status(player: Player, quest_id: str) -> str:
    return player.quest_flags.get(quest_id, "")


def quest_is_done(player: Player, quest_id: str) -> bool:
    return quest_status(player, quest_id) == "done"


def _quest_stages(quest: Quest) -> list[QuestStage]:
    return quest.stages or []


def _current_stage_index(player: Player, quest: Quest) -> int | None:
    status = quest_status(player, quest.id)
    if status in {"", "started"}:
        return 0
    if status == "ready":
        return None
    if status == "done":
        return None
    if status.startswith("stage_"):
        try:
            return int(status.split("_", 1)[1])
        except ValueError:
            return 0
    return 0


def _stage_matches(
    stage: QuestStage,
    *,
    npc_id: str = "",
    room_id: str = "",
    interactable_id: str = "",
) -> bool:
    if stage.objective_type == "talk_npc":
        return npc_id == stage.objective_target
    if stage.objective_type == "visit_room":
        return room_id == stage.objective_target
    if stage.objective_type == "interact":
        return interactable_id == stage.objective_target
    return False


def _advance_stage(player: Player, quest: Quest, locale: str) -> list[str]:
    stages = _quest_stages(quest)
    if not stages:
        return []
    current = _current_stage_index(player, quest)
    if current is None:
        return []
    next_index = current + 1
    if next_index >= len(stages):
        player.quest_flags[quest.id] = "ready"
        return [t(locale, "quest.objective_done", quest=_quest_name(quest, locale))]
    player.quest_flags[quest.id] = f"stage_{next_index}"
    return [t(locale, "quest.stage_done", quest=_quest_name(quest, locale), stage=str(next_index + 1))]


def _check_stage_progress(
    player: Player,
    state: WorldState,
    quest: Quest,
    locale: str,
    *,
    npc_id: str = "",
    room_id: str = "",
    interactable_id: str = "",
) -> list[str]:
    if player.active_quest != quest.id:
        return []
    if quest_is_done(player, quest.id):
        return []
    status = quest_status(player, quest.id)
    if status == "ready":
        return []
    stages = _quest_stages(quest)
    if not stages:
        return []
    current = _current_stage_index(player, quest)
    if current is None:
        return []
    stage = stages[current]
    if not _stage_matches(stage, npc_id=npc_id, room_id=room_id, interactable_id=interactable_id):
        return []
    return _advance_stage(player, quest, locale)


def advance_quest_on_talk(
    player: Player,
    state: WorldState,
    npc_id: str,
    locale: str,
) -> list[str]:
    if not player.active_quest:
        return []
    quest = state.world.quest(player.active_quest)
    if quest is None:
        return []

    status = quest_status(player, player.active_quest)
    if status == "done":
        return []

    lines = _check_stage_progress(player, state, quest, locale, npc_id=npc_id)
    if lines:
        return lines

    if status == "ready" and npc_id == quest.complete_npc_id:
        return _complete_quest(player, quest, locale)

    return []


def advance_quest_on_visit(player: Player, state: WorldState, room_id: str, locale: str) -> list[str]:
    if not player.active_quest:
        return []
    quest = state.world.quest(player.active_quest)
    if quest is None:
        return []
    return _check_stage_progress(player, state, quest, locale, room_id=room_id)


def advance_quest_on_interact(
    player: Player,
    state: WorldState,
    interactable_id: str,
    locale: str,
) -> list[str]:
    if not player.active_quest:
        return []
    quest = state.world.quest(player.active_quest)
    if quest is None:
        return []
    return _check_stage_progress(player, state, quest, locale, interactable_id=interactable_id)


def _complete_quest(player: Player, quest: Quest, locale: str) -> list[str]:
    player.quest_flags[quest.id] = "done"
    player.active_quest = ""
    lines = [t(locale, "quest.complete", quest=_quest_name(quest, locale))]

    if quest.reward_gold > 0:
        player.gold += quest.reward_gold
        lines.append(t(locale, "quest.reward_gold", amount=str(quest.reward_gold)))

    if quest.reward_xp > 0:
        from world.progression import award_xp

        lines.extend(award_xp(player, quest.reward_xp, locale))

    if quest.reward_street_cred > 0:
        from world.street_cred import award_street_cred

        lines.extend(award_street_cred(player, quest.reward_street_cred, locale))

    return lines


def _quest_name(quest: Quest, locale: str) -> str:
    if locale == "en" and quest.name_en:
        return quest.name_en
    return quest.name_zh or quest.id


def quest_hint_for_quest(player: Player, state: WorldState, quest: Quest, locale: str) -> str:
    status = quest_status(player, quest.id)
    if status == "ready" and quest.complete_npc_id:
        npc = state.world.npc(quest.complete_npc_id)
        if npc:
            label = npc.name_zh if locale == "zh" else (npc.name_en or npc.name_zh)
            return t(locale, "quest.hint_return", npc=label)
    stages = _quest_stages(quest)
    current = _current_stage_index(player, quest)
    if current is not None and current < len(stages):
        stage = stages[current]
        if stage.objective_type == "visit_room":
            room = state.world.room(stage.objective_target)
            label = room.name_zh if room and locale == "zh" else (room.name_en if room else stage.objective_target)
            return t(locale, "quest.hint_visit", target=label or stage.objective_target)
        if stage.objective_type == "interact":
            obj = state.world.interactable(stage.objective_target)
            label = obj.name_zh if obj and locale == "zh" else (obj.name_en if obj else stage.objective_target)
            return t(locale, "quest.hint_interact", target=label or stage.objective_target)
        if stage.objective_type == "talk_npc":
            npc = state.world.npc(stage.objective_target)
            label = npc.name_zh if npc and locale == "zh" else (npc.name_en if npc else stage.objective_target)
            return t(locale, "quest.hint_talk", target=label or stage.objective_target)
    if locale == "zh":
        return quest.hint_zh
    return quest.hint_en or quest.hint_zh