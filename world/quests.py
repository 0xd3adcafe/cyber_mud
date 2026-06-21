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


_ARCANA_QUEST_FLAGS: dict[str, str] = {
    "idol_blackmail": "arcana_unlock_idol_blackmail",
    "tyrell_shadow": "arcana_unlock_tyrell_shadow",
    "kabuki_spotlight": "arcana_unlock_kabuki_spotlight",
}


def quest_available(player: Player, quest: Quest) -> bool:
    if quest_is_done(player, quest.id):
        return False
    if player.street_cred < quest.street_cred_req:
        return False
    if quest.requires_quest and not quest_is_done(player, quest.requires_quest):
        return False
    if quest.requires_faction and player.faction != quest.requires_faction:
        return False
    arcana_flag = _ARCANA_QUEST_FLAGS.get(quest.id)
    if arcana_flag and player.quest_flags.get(arcana_flag) != "1":
        return False
    return True


def accept_quest(
    player: Player,
    state: WorldState,
    quest_id: str,
    locale: str,
    *,
    giver_npc_id: str = "",
) -> list[str]:
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
        if quest.requires_faction and player.faction != quest.requires_faction:
            return [t(locale, "gigs.need_faction", faction=quest.requires_faction)]
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
    if quest_id == "idol_fall":
        player.quest_flags["idol_fall_giver"] = giver_npc_id or quest.npc_id
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
    event: str,
    npc_id: str = "",
    room_id: str = "",
    interactable_id: str = "",
    net_node_id: str = "",
    item_id: str = "",
) -> bool:
    if stage.objective_type == "talk_npc":
        return event == "talk" and npc_id == stage.objective_target
    if stage.objective_type == "visit_room":
        return event == "visit" and room_id == stage.objective_target
    if stage.objective_type == "interact":
        return event == "interact" and interactable_id == stage.objective_target
    if stage.objective_type == "defeat_npc":
        return event == "defeat" and npc_id == stage.objective_target
    if stage.objective_type == "have_item":
        return event == "inventory" and stage.objective_target in player.inventory
    if stage.objective_type == "hack_net":
        return event == "hack" and net_node_id == stage.objective_target
    if stage.objective_type == "give_npc":
        if event != "give" or npc_id != stage.objective_target:
            return False
        if stage.objective_item:
            return item_id == stage.objective_item
        return True
    if stage.objective_type == "scan_npc":
        return event == "scan" and npc_id == stage.objective_target
    if stage.objective_type == "profile_trait":
        if event != "profile_trait":
            return False
        if stage.objective_target and item_id != stage.objective_target:
            return False
        if stage.objective_item and npc_id != stage.objective_item:
            return False
        return True
    if stage.objective_type == "hack_infra":
        return event == "hack_infra" and item_id == stage.objective_target
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
    event: str,
    npc_id: str = "",
    room_id: str = "",
    interactable_id: str = "",
    net_node_id: str = "",
    item_id: str = "",
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
        event=event,
        npc_id=npc_id,
        room_id=room_id,
        interactable_id=interactable_id,
        net_node_id=net_node_id,
        item_id=item_id,
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

    lines = _check_stage_progress(player, state, quest, locale, event="talk", npc_id=npc_id)
    if lines:
        return lines

    if status == "ready":
        if quest.id == "idol_fall":
            giver = player.quest_flags.get("idol_fall_giver", quest.complete_npc_id)
            if npc_id == giver:
                return _complete_quest(player, state, quest, locale)
        elif npc_id == quest.complete_npc_id:
            return _complete_quest(player, state, quest, locale)

    return []


def advance_quest_on_visit(player: Player, state: WorldState, room_id: str, locale: str) -> list[str]:
    if not player.active_quest:
        return []
    quest = state.world.quest(player.active_quest)
    if quest is None:
        return []
    return _check_stage_progress(player, state, quest, locale, event="visit", room_id=room_id)


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
    return _check_stage_progress(player, state, quest, locale, event="interact", interactable_id=interactable_id)


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
    return _check_stage_progress(player, state, quest, locale, event="defeat", npc_id=npc_id)


def advance_quest_on_inventory(player: Player, state: WorldState, locale: str) -> list[str]:
    if not player.active_quest:
        return []
    quest = state.world.quest(player.active_quest)
    if quest is None:
        return []
    return _check_stage_progress(player, state, quest, locale, event="inventory")


def advance_quest_on_hack(
    player: Player,
    state: WorldState,
    node_id: str,
    locale: str,
) -> list[str]:
    if not player.active_quest:
        return []
    quest = state.world.quest(player.active_quest)
    if quest is None:
        return []
    return _check_stage_progress(player, state, quest, locale, event="hack", net_node_id=node_id)


def advance_quest_on_scan(
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
    return _check_stage_progress(player, state, quest, locale, event="scan", npc_id=npc_id)


def advance_quest_on_profile_trait(
    player: Player,
    state: WorldState,
    npc_id: str,
    trait_id: str,
    locale: str,
) -> list[str]:
    if not player.active_quest:
        return []
    quest = state.world.quest(player.active_quest)
    if quest is None:
        return []
    return _check_stage_progress(
        player,
        state,
        quest,
        locale,
        event="profile_trait",
        npc_id=npc_id,
        item_id=trait_id,
    )


def advance_quest_on_infra_hack(
    player: Player,
    state: WorldState,
    hack_id: str,
    locale: str,
) -> list[str]:
    if not player.active_quest:
        return []
    quest = state.world.quest(player.active_quest)
    if quest is None:
        return []
    return _check_stage_progress(
        player,
        state,
        quest,
        locale,
        event="hack_infra",
        item_id=hack_id,
    )


def advance_quest_on_give(
    player: Player,
    state: WorldState,
    npc_id: str,
    item_id: str,
    locale: str,
) -> list[str]:
    if not player.active_quest:
        return []
    quest = state.world.quest(player.active_quest)
    if quest is None:
        return []
    return _check_stage_progress(
        player,
        state,
        quest,
        locale,
        event="give",
        npc_id=npc_id,
        item_id=item_id,
    )


def _quest_offered_by(quest: Quest, npc_id: str) -> bool:
    if quest.offer_npc_ids:
        return npc_id in quest.offer_npc_ids
    return quest.npc_id == npc_id


def offer_quest_from_giver(
    player: Player,
    state: WorldState,
    npc_id: str,
    locale: str,
) -> list[str]:
    if player.active_quest:
        return []
    for quest in state.world.quests.values():
        if not _quest_offered_by(quest, npc_id):
            continue
        if quest_is_done(player, quest.id):
            continue
        if not quest_available(player, quest):
            continue
        if quest_status(player, quest.id) not in {"", "started"}:
            continue
        return accept_quest(player, state, quest.id, locale, giver_npc_id=npc_id)
    return []


def _complete_quest(player: Player, state: WorldState, quest: Quest, locale: str) -> list[str]:
    player.quest_flags[quest.id] = "done"
    player.active_quest = ""
    if quest.id == "idol_fall":
        giver = player.quest_flags.get("idol_fall_giver", "")
        if giver == "kabuki_idol_haejin":
            player.quest_flags["idol_ending"] = "haejin"
        elif giver == "kabuki_idol_airi":
            player.quest_flags["idol_ending"] = "airi"
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
        if stage.objective_type == "hack_net":
            node = state.world.net_nodes.get(stage.objective_target)
            if node:
                label = node.name_zh if locale == "zh" else (node.name_en or node.name_zh)
                return t(locale, "quest.hint_hack_net", target=label or stage.objective_target)
            return t(locale, "quest.hint_hack_net", target=stage.objective_target)
        if stage.objective_type == "give_npc":
            npc = state.world.npc(stage.objective_target)
            npc_label_text = npc.name_zh if npc and locale == "zh" else (npc.name_en if npc else stage.objective_target)
            if stage.objective_item:
                item = state.world.item(stage.objective_item)
                item_label_text = item_label(item, locale) if item else stage.objective_item
                return t(
                    locale,
                    "quest.hint_give_npc",
                    npc=npc_label_text or stage.objective_target,
                    item=item_label_text,
                )
            return t(locale, "quest.hint_talk", target=npc_label_text or stage.objective_target)
        if stage.objective_type == "scan_npc":
            npc = state.world.npc(stage.objective_target)
            label = npc.name_zh if npc and locale == "zh" else (npc.name_en if npc else stage.objective_target)
            return t(locale, "quest.hint_scan_npc", target=label or stage.objective_target)
        if stage.objective_type == "profile_trait":
            trait_key = f"profiler.traits.{stage.objective_target}"
            trait_label = t(locale, trait_key)
            if trait_label == trait_key:
                trait_label = stage.objective_target
            npc = state.world.npc(stage.objective_item) if stage.objective_item else None
            npc_label_text = (
                npc.name_zh
                if npc and locale == "zh"
                else (npc.name_en if npc else (stage.objective_item or "any target"))
            )
            return t(
                locale,
                "quest.hint_profile_trait",
                target=npc_label_text or stage.objective_item or "a target",
                trait=trait_label,
            )
        if stage.objective_type == "hack_infra":
            return t(locale, "quest.hint_hack_infra", target=stage.objective_target)
    base = quest.hint_zh if locale == "zh" else (quest.hint_en or quest.hint_zh)
    from world.factions import faction_quest_hint_suffix

    suffix = faction_quest_hint_suffix(player, locale)
    if suffix and base:
        return f"{base} {suffix}"
    return base or suffix


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