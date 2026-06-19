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

    if npc.quest_id and ctx.player.quest_flags.get(npc.quest_id) != "done":
        quest = ctx.state.world.quest(npc.quest_id)
        if quest and not ctx.player.active_quest:
            ctx.player.active_quest = npc.quest_id
            ctx.player.quest_flags[npc.quest_id] = "started"
            quest_line = t(ctx.player.locale, f"talk.{talk_key}_quest")
            if quest_line != f"talk.{talk_key}_quest":
                lines.append(quest_line)
            else:
                desc = quest.description_zh if ctx.player.locale == "zh" else (quest.description_en or quest.description_zh)
                if desc:
                    lines.append(desc)

    if not lines:
        label = npc.name_zh if ctx.player.locale == "zh" else (npc.name_en or npc.name_zh)
        lines.append(t(ctx.player.locale, "talk.silent", name=label))

    return ok(lines, meta=player_meta(ctx), world_changed=bool(npc.quest_id))


register("talk", handle)