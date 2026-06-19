from __future__ import annotations

from commands.helpers import find_npc_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.progression import can_learn_skill, resolve_skill_id, skill_label

BROKER_ID = "broker"


def handle(ctx: CommandContext):
    skill_name = ctx.args.strip()
    if not skill_name:
        return ok([t(ctx.player.locale, "learn.usage")])

    skill_id = resolve_skill_id(ctx.state.world, skill_name)
    skill = ctx.state.world.skill(skill_id) if skill_id else None
    error = can_learn_skill(ctx.player, skill)
    if error:
        if error == "learn.unknown":
            return ok([t(ctx.player.locale, error, skill=skill_name)])
        if error == "learn.already":
            return ok([t(ctx.player.locale, error, skill=skill_label(skill, ctx.player.locale))])
        if error == "learn.level_req":
            return ok([t(ctx.player.locale, error, level=str(skill.level_req))])
        if error == "learn.prereq_skill":
            prereq = ctx.state.world.skill(skill.prereq_skill)
            name = skill_label(prereq, ctx.player.locale) if prereq else skill.prereq_skill
            return ok([t(ctx.player.locale, error, skill=name)])
        return ok([t(ctx.player.locale, error)])

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
    label = skill_label(skill, ctx.player.locale)
    return ok(
        [t(ctx.player.locale, "learn.ok", skill=label, cost=str(skill.gold_cost))],
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("learn", handle)