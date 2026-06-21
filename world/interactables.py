from __future__ import annotations

from entities.player import Player
from shared.i18n import t
from shared.names import matches_name
from world.content import Interactable
from world.state import WorldState


def interactable_label(obj: Interactable, locale: str) -> str:
    if locale == "en" and obj.name_en:
        return f"{obj.name_en} ({obj.id})"
    return f"{obj.name_zh or obj.id} ({obj.id})"


def find_interactable_id(state: WorldState, room_id: str, name: str) -> str | None:
    for obj in state.world.interactables_in_room(room_id):
        if matches_name(name, obj.id, obj.name_zh, obj.name_en):
            return obj.id
    return None


def interactable_description(obj: Interactable, locale: str) -> str:
    if locale == "en" and obj.description_en:
        return obj.description_en
    return obj.description_zh or ""


def interactable_message(obj: Interactable, locale: str) -> str:
    if locale == "en" and obj.message_en:
        return obj.message_en
    return obj.message_zh or ""


def interact_once_done(player: Player, obj: Interactable) -> bool:
    if not obj.once_key:
        return False
    return player.interact_flags.get(obj.once_key) == "done"


def perform_interact(
    player: Player,
    state: WorldState,
    obj: Interactable,
    locale: str,
) -> list[str]:
    if interact_once_done(player, obj):
        return [t(locale, "interact.already", name=interactable_label(obj, locale))]

    if obj.requires_item and obj.requires_item not in player.inventory:
        item = state.world.item(obj.requires_item)
        label = item.name_zh if item and locale == "zh" else (item.name_en if item else obj.requires_item)
        return [t(locale, "interact.need_item", item=label or obj.requires_item)]

    if obj.requires_skill and obj.requires_skill not in player.skills:
        skill = state.world.skill(obj.requires_skill)
        label = skill.name_zh if skill and locale == "zh" else (skill.name_en if skill else obj.requires_skill)
        return [t(locale, "interact.need_skill", skill=label or obj.requires_skill)]

    lines: list[str] = []
    msg = interactable_message(obj, locale)
    from world.mature import is_mature

    if is_mature(player):
        from shared.mature_i18n import tm

        mature_msg = tm(locale, f"interact.{obj.id}")
        if mature_msg and not mature_msg.startswith("interact."):
            msg = mature_msg
    if msg:
        lines.append(msg)

    if obj.gives_item:
        player.inventory.append(obj.gives_item)
        item = state.world.item(obj.gives_item)
        if item:
            label = item.name_zh if locale == "zh" else (item.name_en or item.name_zh)
            lines.append(t(locale, "interact.got_item", item=label or obj.gives_item))

    if obj.requires_item and obj.gives_item:
        player.inventory.remove(obj.requires_item)

    if obj.once_key:
        player.interact_flags[obj.once_key] = "done"

    kind = getattr(obj, "kind", "")
    if kind in {"rest", "sleep"}:
        from world.life import apply_anchor_from_interactable, posture_label, set_posture, sleep_refusal

        posture, allows_sleep = apply_anchor_from_interactable(player, obj)
        if kind == "sleep":
            refusal = sleep_refusal(player, state, locale)
            if refusal and not allows_sleep:
                return [refusal]
            set_posture(player, "sleeping", anchor=player.life_anchor)
            lines.append(t(locale, "life.interact_sleep", name=interactable_label(obj, locale)))
        else:
            set_posture(player, posture, anchor=player.life_anchor)
            lines.append(
                t(
                    locale,
                    "life.interact_rest",
                    name=interactable_label(obj, locale),
                    posture=posture_label(posture, locale),
                )
            )

    if obj.braindance_id:
        from world.braindance import play_braindance

        lines.extend(play_braindance(player, state, obj.braindance_id, locale, free=True))

    if getattr(obj, "kind", "") == "arcana":
        from world.arcana import perform_arcana_draw

        spread = int(player.interact_flags.pop("_arcana_spread", "1") or "1")
        lines.extend(perform_arcana_draw(player, state, locale, spread=spread))
        return lines

    from world.quests import advance_quest_on_interact

    lines.extend(advance_quest_on_interact(player, state, obj.id, locale))
    return lines