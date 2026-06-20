from __future__ import annotations

from commands.helpers import faction_label, resolve_faction_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t


def handle(ctx: CommandContext):
    faction_name = ctx.args.strip()
    if not faction_name:
        return ok([t(ctx.player.locale, "pledge.usage")])

    faction_id = resolve_faction_id(ctx.state.world, faction_name)
    if faction_id is None:
        return ok([t(ctx.player.locale, "pledge.unknown", faction=faction_name)])

    if ctx.player.faction == faction_id:
        label = faction_label(ctx.state.world, faction_id, ctx.player.locale)
        return ok([t(ctx.player.locale, "pledge.already", faction=label)])

    ctx.player.faction = faction_id
    label = faction_label(ctx.state.world, faction_id, ctx.player.locale)
    from world.reactions import reputation_from_pledge, shift_reputation

    lines = [t(ctx.player.locale, "pledge.ok", faction=label)]
    lines.extend(shift_reputation(ctx.player, reputation_from_pledge(faction_id), ctx.player.locale))
    return ok(
        lines,
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("pledge", handle)