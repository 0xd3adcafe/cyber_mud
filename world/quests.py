from __future__ import annotations

from entities.player import Player
from shared.i18n import t
from shared.locale_content import item_label
from world.content import Quest, QuestStage
from world.state import WorldState


def quest_status(player: Player, quest_id: str) -> str:
    return player.quest_flags.get(quest_id, "")


def quest_is_done(player: Player, quest_id: str) -> bool:
    return quest_status(player, quest_id) == "done"


def quest_stages(quest: Quest) -> list[QuestStage]:
    if quest.stages:
        return list(quest.stages)
    if quest.objective_type:
        return [
            QuestStage(
                objective_type=quest.objective_type,
                objective_target=quest.objective_target,
            )
        ]
    return []


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


def _quest_name(quest: Quest, locale: str) -> str:
    if locale == "en" and quest.name_en:
        return quest.name_en
    return quest.name_zh or quest.id


def quest_available(player: Player, quest: Quest) -> bool:
    if quest_is_done(player, quest.id):
        return False
    if player.street_cred < quest.street_cred_req:
        return False
    if quest.requires_quest and not quest_is_done(player, quest.requires_quest):
        return False
    return True


def accept_quest(player: Player, state: WorldState, quest_id: str, locale: str) -> list[str]:
    quest = state.world.quest(quest_id)
    if quest is None:
        return [t(locale, "gigs.missing", quest=quest_id)]

    from world.mature import gate_content_rating

    refusal = gate_content_rating(player, quest.rating, locale)
    if refusal is not None:
        return refusal

    if quest_is_done(player, quest_id):
        return [t(locale, "gigs.already_done", quest=_quest_name(quest, locale))]

    if player.active_quest and player.active_quest != quest_id:
        active = state.world.quest(player.active_quest)
        name = _quest_name(active, locale) if active else player.active_quest
        return [t(locale, "gigs.busy", quest=name)]

    status = quest_status(player, quest_id)
    if player.active_quest == quest_id and status not in {"", "started"} and status != "ready":
        return [t(locale, "gigs.already_active", quest=_quest_name(quest, locale))]

    if not quest_available(player, quest):
        if quest.requires_quest and not quest_is_done(player, quest.requires_quest):
            required = state.world.quest(quest.requires_quest)
            req_name = _quest_name(required, locale) if required else quest.requires_quest
            return [t(locale, "gigs.need_quest", quest=req_name)]
        if player.street_cred < quest.street_cred_req:
            return [
                t(
                    locale,
                    "gigs.need_cred",
                    req=str(quest.street_cred_req),
                    have=str(player.street_cred),
                )
            ]
        return [t(locale, "gigs.locked", quest=_quest_name(quest, locale))]

    if player.active_quest == quest_id:
        return [t(locale, "gigs.already_active", quest=_quest_name(quest, locale))]

    player.active_quest = quest_id
    if status in {"", "ready"}:
        player.quest_flags[quest_id] = "started"
    lines = [t(locale, "gigs.accepted", quest=_quest_name(quest, locale))]
    desc = quest.description_zh if locale == "zh" else (quest.description_en or quest.description_zh)
    if desc:
        lines.append(desc)
    return lines


def abandon_quest(player: Player, state: WorldState, locale: str) -> list[str]:
    if not player.active_quest:
        return [t(locale, "gigs.no_active")]
    quest = state.world.quest(player.active_quest)
    name = _quest_name(quest, locale) if quest else player.active_quest
    quest_id = player.active_quest
    player.active_quest = ""
    status = quest_status(player, quest_id)
    if status not in {"", "done"}:
        player.quest_flags[quest_id] = ""
    return [t(locale, "gigs.abandoned", quest=name)]


def _stage_matches(
    stage: QuestStage,
    player: Player,
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
    if stage.objective_type == "defeat_npc":
        return npc_id == stage.objective_target
    if stage.objective_type == "have_item":
        return stage.objective_target in player.inventory
    return False


def _advance_stage(player: Player, quest: Quest, locale: str) -> list[str]:
    stages = quest_stages(quest)
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
    stages = quest_stages(quest)
    if not stages:
        return []
    current = _current_stage_index(player, quest)
    if current is None:
        return []
    stage = stages[current]
    if not _stage_matches(
        stage,
        player,
        npc_id=npc_id,
        room_id=room_id,
        interactable_id=interactable_id,
    ):
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
        return _complete_quest(player, state, quest, locale)

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


def advance_quest_on_defeat(
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
    return _check_stage_progress(player, state, quest, locale, npc_id=npc_id)


def advance_quest_on_inventory(player: Player, state: WorldState, locale: str) -> list[str]:
    if not player.active_quest:
        return []
    quest = state.world.quest(player.active_quest)
    if quest is None:
        return []
    return _check_stage_progress(player, state, quest, locale)


def offer_quest_from_giver(
    player: Player,
    state: WorldState,
    npc_id: str,
    locale: str,
) -> list[str]:
    if player.active_quest:
        return []
    for quest in state.world.quests.values():
        if quest.npc_id != npc_id:
            continue
        if quest_is_done(player, quest.id):
            continue
        if not quest_available(player, quest):
            continue
        if quest_status(player, quest.id) not in {"", "started"}:
            continue
        return accept_quest(player, state, quest.id, locale)
    return []


def _complete_quest(player: Player, state: WorldState, quest: Quest, locale: str) -> list[str]:
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

    for item_id in quest.reward_items:
        item = state.world.item(item_id)
        if item is None:
            continue
        player.inventory.append(item_id)
        lines.append(
            t(
                locale,
                "quest.reward_item",
                item=item_label(item, locale),
            )
        )

    return lines


def quest_hint_for_quest(player: Player, state: WorldState, quest: Quest, locale: str) -> str:
    status = quest_status(player, quest.id)
    if status == "ready" and quest.complete_npc_id:
        npc = state.world.npc(quest.complete_npc_id)
        if npc:
            label = npc.name_zh if locale == "zh" else (npc.name_en or npc.name_zh)
            return t(locale, "quest.hint_return", npc=label)
    stages = quest_stages(quest)
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
        if stage.objective_type == "defeat_npc":
            npc = state.world.npc(stage.objective_target)
            label = npc.name_zh if npc and locale == "zh" else (npc.name_en if npc else stage.objective_target)
            return t(locale, "quest.hint_defeat", target=label or stage.objective_target)
        if stage.objective_type == "have_item":
            item = state.world.item(stage.objective_target)
            label = item_label(item, locale) if item else stage.objective_target
            return t(locale, "quest.hint_have_item", target=label)
    if locale == "zh":
        return quest.hint_zh
    return quest.hint_en or quest.hint_zh


def format_journal_lines(player: Player, state: WorldState, locale: str) -> list[str]:
    lines = [t(locale, "gigs.journal_header"), ""]
    if player.active_quest:
        quest = state.world.quest(player.active_quest)
        if quest:
            lines.append(t(locale, "gigs.journal_active", quest=_quest_name(quest, locale)))
            hint = quest_hint_for_quest(player, state, quest, locale)
            if hint:
                lines.append(t(locale, "gigs.journal_hint", hint=hint))
            lines.append("")
    done = [qid for qid in state.world.quests if quest_is_done(player, qid)]
    if done:
        lines.append(t(locale, "gigs.journal_done", count=str(len(done))))
        for qid in sorted(done):
            quest = state.world.quest(qid)
            if quest:
                lines.append(f"  · {_quest_name(quest, locale)}")
    else:
        lines.append(t(locale, "gigs.journal_none_done"))
    return lines