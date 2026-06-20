from __future__ import annotations

import random

from commands.helpers import current_room, format_look
from commands.registry import CommandContext, ok, ok_document, player_meta, register
from shared.i18n import t
from world.modifiers import movement_blocked_by_weather
from world.schedule import shop_is_open


def handle(ctx: CommandContext):
    direction = ctx.args.strip().lower()
    if not direction:
        return ok([t(ctx.player.locale, "game.no_exit")])

    room = current_room(ctx)
    if room is None or direction not in room.exits:
        return ok([t(ctx.player.locale, "game.no_exit")])

    dest_id = room.exits[direction]
    dest = ctx.state.world.room(dest_id)
    from world.mature import gate_room_entry

    refusal = gate_room_entry(ctx.player, dest, ctx.player.locale)
    if refusal is not None:
        return ok(refusal)

    if dest is not None and dest.shop_id:
        hour = ctx.state.clock.hour
        if not shop_is_open(dest.shop_id, hour):
            return ok([t(ctx.player.locale, "schedule.shop_closed", shop=dest.name_zh if ctx.player.locale == "zh" else (dest.name_en or dest.name_zh))])

    if movement_blocked_by_weather(ctx.state, ctx.player.room_id, roll=random.random()):
        weather_key = "modifiers.movement_blocked"
        return ok([t(ctx.player.locale, weather_key)])

    life_lines: list[str] = []
    if ctx.player.posture != "standing":
        from world.life import wake_player

        if wake_player(ctx.player):
            life_lines.append(t(ctx.player.locale, "life.wake_on_move"))

    ctx.player.room_id = dest_id
    from world.quests import advance_quest_on_visit
    from world.trauma import treat_trauma_at_ripperdoc

    quest_lines = advance_quest_on_visit(ctx.player, ctx.state, dest_id, ctx.player.locale)
    trauma_lines = treat_trauma_at_ripperdoc(ctx.player, dest, ctx.player.locale)
    lines = [t(ctx.player.locale, "go.ok", direction=direction), ""]
    lines.extend(life_lines)
    lines.extend(quest_lines)
    lines.extend(trauma_lines)
    lines.extend(format_look(ctx))
    return ok_document(
        lines,
        meta=player_meta(ctx),
        moved=True,
        world_changed=bool(quest_lines) or bool(trauma_lines),
    )


register("go", handle)