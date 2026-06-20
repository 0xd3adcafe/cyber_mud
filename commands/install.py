from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.target_resolve import resolve_item_id
from shared.cyberware_slots import slot_label
from shared.i18n import t
from world.cyberware import can_install, install_implant


def implant_label(implant, locale: str) -> str:
    if implant is None:
        return "?"
    if locale == "en" and implant.name_en:
        return implant.name_en
    return implant.name_zh or implant.id


def _at_ripperdoc(ctx: CommandContext) -> bool:
    room = ctx.state.world.room(ctx.player.room_id)
    if room is None:
        return False
    return "ripperdoc" in room.tags


def handle(ctx: CommandContext):
    if not ctx.args:
        return ok([t(ctx.player.locale, "install.usage")])

    result = resolve_item_id(ctx, ctx.args, scopes=("inventory",), verb="install")
    if result.needs_response:
        return ok(result.lines)
    if not result.ok:
        return ok([t(ctx.player.locale, "install.missing")])
    item_id = result.value

    item = ctx.state.world.item(item_id)
    if item is None or not item.implant_id:
        return ok([t(ctx.player.locale, "install.not_implant")])

    implant = ctx.state.world.implant(item.implant_id)
    if implant is None:
        return ok([t(ctx.player.locale, "install.unknown_implant")])

    if implant.ripperdoc_only and not _at_ripperdoc(ctx):
        return ok([t(ctx.player.locale, "install.need_ripperdoc")])

    error = can_install(ctx.player, implant)
    if error:
        if error == "install.slot_taken":
            slot_name = slot_label(implant.slot, ctx.player.locale)
            return ok([t(ctx.player.locale, error, slot=slot_name)])
        return ok([t(ctx.player.locale, error)])

    ctx.player.inventory.remove(item_id)
    install_implant(ctx.player, implant)
    label = implant_label(implant, ctx.player.locale)

    if implant.side_effect_minutes > 0 and ctx.player.named:
        from world.scheduler import minutes_to_ticks

        delay = minutes_to_ticks(
            implant.side_effect_minutes,
            minutes_per_tick=ctx.state.time_config.minutes_per_tick,
        )
        ctx.state.scheduler.cancel_kind("implant_side_effect", player_name=ctx.player.name)
        ctx.state.scheduler.schedule_once(
            ctx.state.tick_count + delay,
            "implant_side_effect",
            player_name=ctx.player.name,
            payload={"implant_id": implant.id, "label": label},
        )
    slot_name = slot_label(implant.slot, ctx.player.locale)
    return ok(
        [
            t(
                ctx.player.locale,
                "install.ok",
                label=label,
                slot=slot_name,
                humanity=str(ctx.player.humanity),
                body=str(ctx.player.body),
            )
        ],
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("install", handle)