from __future__ import annotations

from commands.helpers import find_npc_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t


BROKER_ID = "broker"


def handle(ctx: CommandContext):
    skill_name = ctx.args.strip()
    if not skill_name:
        return ok([t(ctx.player.locale, "learn.usage")])

    skill_id = None
    skill = None
    for sid, data in ctx.state.world.skills.items():
        if skill_name.lower() in {sid.lower(), data.name_zh.lower(), data.name_en.lower()}:
            skill_id = sid
            skill = data
            break
    if skill is None:
        return ok([t(ctx.player.locale, "learn.unknown", skill=skill_name)])

    if skill_id in ctx.player.skills:
        label = skill.name_zh if ctx.player.locale == "zh" else (skill.name_en or skill.name_zh)
        return ok([t(ctx.player.locale, "learn.already", skill=label)])

    broker_here = find_npc_id(ctx.state, BROKER_ID, ctx.player.room_id) == BROKER_ID
    if not broker_here:
        broker_npc = ctx.state.world.npc(BROKER_ID)
        if broker_npc:
            label = broker_npc.name_zh if ctx.player.locale == "zh" else (broker_npc.name_en or broker_npc.name_zh)
            return ok([t(ctx.player.locale, "learn.no_teacher", teacher=label)])
        return ok([t(ctx.player.locale, "learn.no_teacher", teacher=BROKER_ID)])

    if skill.gold_cost > 0 and ctx.player.gold < skill.gold_cost:
        return ok([t(ctx.player.locale, "learn.no_gold", cost=str(skill.gold_cost))])

    if skill.gold_cost > 0:
        ctx.player.gold -= skill.gold_cost

    ctx.player.skills.append(skill_id)
    label = skill.name_zh if ctx.player.locale == "zh" else (skill.name_en or skill.name_zh)
    return ok(
        [t(ctx.player.locale, "learn.ok", skill=label, cost=str(skill.gold_cost))],
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("learn", handle)