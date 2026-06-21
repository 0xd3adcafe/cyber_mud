from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.target_resolve import resolve_npc
from shared.i18n import t
from world.mature import has_mature_tag


def has_mature_talk(npc) -> bool:
    return has_mature_tag(npc.tags) or (npc.talk_key or "").startswith("mature_")


def handle(ctx: CommandContext):
    target = ctx.args.strip()
    if not target:
        return ok([t(ctx.player.locale, "talk.usage")])

    npc_result = resolve_npc(ctx, target, verb="talk")
    if npc_result.needs_response:
        return ok(npc_result.lines)
    if not npc_result.ok:
        return ok([t(ctx.player.locale, "talk.missing", name=target)])
    npc_id = npc_result.value

    npc = ctx.state.world.npc(npc_id)
    if npc is None:
        return ok([t(ctx.player.locale, "talk.missing", name=target)])

    from world.mature import gate_mature_entity, is_mature
    from shared.mature_i18n import tm

    refusal = gate_mature_entity(ctx.player, npc.tags, ctx.player.locale)
    if refusal is not None:
        return ok(refusal)

    lines: list[str] = []
    woke = False
    if ctx.player.posture == "sleeping":
        from world.life import wake_player

        if wake_player(ctx.player):
            woke = True
            lines.append(t(ctx.player.locale, "life.wake_on_talk"))
    from world.factions import faction_talk_key

    talk_key = faction_talk_key(npc.talk_key or npc.id, ctx.player)
    if is_mature(ctx.player) and has_mature_talk(npc):
        dialogue = tm(ctx.player.locale, f"talk.{talk_key}")
        if dialogue == f"talk.{talk_key}":
            dialogue = t(ctx.player.locale, f"talk.{talk_key}")
    else:
        dialogue = t(ctx.player.locale, f"talk.{talk_key}")
    if dialogue == f"talk.{talk_key}" and talk_key != (npc.talk_key or npc.id):
        dialogue = t(ctx.player.locale, f"talk.{npc.talk_key or npc.id}")
    if dialogue != f"talk.{talk_key}":
        lines.append(dialogue)

    from world.reactions import broker_talk_extra

    extra = broker_talk_extra(ctx.player, npc_id, ctx.player.locale)
    if extra:
        lines.append(extra)

    from world.profiler_talk import resolve_profiler_talk

    profiler_lines, profiler_changed = resolve_profiler_talk(
        ctx.player,
        ctx.state,
        npc_id,
        ctx.player.locale,
    )
    if profiler_lines:
        lines.extend(profiler_lines)

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

    world_changed = bool(offer_lines) or bool(quest_lines) or woke or profiler_changed
    return ok(lines, meta=player_meta(ctx), world_changed=world_changed)


register("talk", handle)