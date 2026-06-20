from __future__ import annotations

from commands.helpers import find_npc_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t


def handle(ctx: CommandContext):
    target = ctx.args.strip()
    if not target:
        return ok([t(ctx.player.locale, "talk.usage")])

    npc_id = find_npc_id(ctx.state, target, ctx.player.room_id)
    if npc_id is None:
        return ok([t(ctx.player.locale, "talk.missing", name=target)])

    npc = ctx.state.world.npc(npc_id)
    if npc is None:
        return ok([t(ctx.player.locale, "talk.missing", name=target)])

    lines: list[str] = []
    talk_key = npc.talk_key or npc.id
    dialogue = t(ctx.player.locale, f"talk.{talk_key}")
    if dialogue != f"talk.{talk_key}":
        lines.append(dialogue)

    from world.quests import advance_quest_on_talk, offer_quest_from_giver

    offer_lines = offer_quest_from_giver(ctx.player, ctx.state, npc_id, ctx.player.locale)
    if offer_lines:
        talk_key = npc.talk_key or npc.id
        quest_line = t(ctx.player.locale, f"talk.{talk_key}_quest")
        if quest_line != f"talk.{talk_key}_quest":
            lines.insert(0, quest_line)
        lines = offer_lines + lines

    quest_lines = advance_quest_on_talk(ctx.player, ctx.state, npc_id, ctx.player.locale)
    lines.extend(quest_lines)

    if not lines:
        label = npc.name_zh if ctx.player.locale == "zh" else (npc.name_en or npc.name_zh)
        lines.append(t(ctx.player.locale, "talk.silent", name=label))

    world_changed = bool(offer_lines) or bool(quest_lines)
    return ok(lines, meta=player_meta(ctx), world_changed=world_changed)


register("talk", handle)