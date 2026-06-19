from __future__ import annotations

from commands.helpers import find_item_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label


def _at_home(ctx: CommandContext) -> bool:
    return bool(ctx.player.home_room_id) and ctx.player.room_id == ctx.player.home_room_id


def _stash_capacity(ctx: CommandContext) -> int:
    for home in ctx.state.world.homes.values():
        if home.room_id == ctx.player.home_room_id:
            return home.stash_capacity
    return 10


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    if not ctx.player.home_room_id:
        return ok([t(locale, "stash.no_home")])

    parts = ctx.args.strip().split(maxsplit=1)
    verb = parts[0].lower() if parts else ""
    target = parts[1].strip() if len(parts) > 1 else ""

    if not verb:
        lines = [t(locale, "stash.header"), ""]
        if ctx.player.home_stash:
            for item_id in ctx.player.home_stash:
                item = ctx.state.world.item(item_id)
                lines.append(f"  • {item_label(item, locale) if item else item_id}")
        else:
            lines.append(t(locale, "stash.empty"))
        cap = _stash_capacity(ctx)
        lines.append("")
        lines.append(t(locale, "stash.capacity", count=str(len(ctx.player.home_stash)), max=str(cap)))
        lines.append(t(locale, "stash.hint"))
        return ok(lines, meta=player_meta(ctx))

    if not _at_home(ctx):
        return ok([t(locale, "stash.not_home")])

    if verb in {"put", "store", "drop"}:
        if not target:
            return ok([t(locale, "stash.put_usage")])
        item_id = find_item_id(ctx.state, target, inventory=ctx.player.inventory)
        if item_id is None:
            return ok([t(locale, "stash.missing_item")])
        cap = _stash_capacity(ctx)
        if len(ctx.player.home_stash) >= cap:
            return ok([t(locale, "stash.full", max=str(cap))])
        ctx.player.inventory.remove(item_id)
        ctx.player.home_stash.append(item_id)
        item = ctx.state.world.item(item_id)
        return ok(
            [t(locale, "stash.put_ok", item=item_label(item, locale) if item else item_id)],
            meta=player_meta(ctx),
            world_changed=True,
        )

    if verb in {"take", "get"}:
        if not target:
            return ok([t(locale, "stash.take_usage")])
        item_id = find_item_id(ctx.state, target, inventory=ctx.player.home_stash)
        if item_id is None:
            return ok([t(locale, "stash.missing_stash")])
        ctx.player.home_stash.remove(item_id)
        ctx.player.inventory.append(item_id)
        item = ctx.state.world.item(item_id)
        return ok(
            [t(locale, "stash.take_ok", item=item_label(item, locale) if item else item_id)],
            meta=player_meta(ctx),
            world_changed=True,
        )

    return ok([t(locale, "stash.hint")])


register("stash", handle)