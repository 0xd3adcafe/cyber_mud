from __future__ import annotations

from entities.player import Player
from shared.i18n import t
from world.content import Quest
from world.state import WorldState


def quest_status(player: Player, quest_id: str) -> str:
    return player.quest_flags.get(quest_id, "")


def quest_is_done(player: Player, quest_id: str) -> bool:
    return quest_status(player, quest_id) == "done"


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

    if status in {"", "started"} and quest.objective_type == "talk_npc" and npc_id == quest.objective_target:
        player.quest_flags[player.active_quest] = "ready"
        return [t(locale, "quest.objective_done", quest=_quest_name(quest, locale))]

    if status == "ready" and npc_id == quest.complete_npc_id:
        return _complete_quest(player, quest, locale)

    return []


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
    if locale == "zh":
        return quest.hint_zh
    return quest.hint_en or quest.hint_zh