from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.mature import is_mature, set_content_rating


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    args = ctx.args.strip().lower()
    if not args:
        rating_key = "mature" if is_mature(ctx.player) else "teen"
        return ok([t(locale, "settings.current", rating=t(locale, f"settings.rating.{rating_key}"))])

    parts = args.split()
    if len(parts) != 2 or parts[0] != "mature" or parts[1] not in {"on", "off"}:
        return ok([t(locale, "settings.usage")])

    enabled = parts[1] == "on"
    set_content_rating(ctx.player, enabled)
    key = "settings.mature_on" if enabled else "settings.mature_off"
    return ok(
        [t(locale, key)],
        meta=player_meta(ctx),
        world_changed=True,
    )


register("settings", handle)