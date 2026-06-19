from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t


def _housing_label(home, locale: str) -> str:
    if locale == "en" and home.name_en:
        return home.name_en
    return home.name_zh or home.id


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    target = ctx.args.strip().lower()
    if not target:
        lines = [t(locale, "rent.header"), ""]
        for home in ctx.state.world.homes.values():
            if home.rent_room and home.rent_room != ctx.player.room_id:
                continue
            label = _housing_label(home, locale)
            desc = home.description_zh if locale == "zh" else (home.description_en or home.description_zh)
            lines.append(t(locale, "rent.line", name=label, cost=str(home.cost), desc=desc or ""))
        lines.append("")
        lines.append(t(locale, "rent.usage"))
        return ok(lines, meta=player_meta(ctx))

    home = ctx.state.world.home(target)
    if home is None:
        for hid, h in ctx.state.world.homes.items():
            labels = {hid.lower(), h.name_zh.lower(), h.name_en.lower()}
            if target in labels:
                home = h
                break
    if home is None:
        return ok([t(locale, "rent.unknown", name=target)])

    if home.rent_room and ctx.player.room_id != home.rent_room:
        return ok([t(locale, "rent.wrong_room")])

    if ctx.player.home_room_id == home.room_id:
        return ok([t(locale, "rent.already")])

    if ctx.player.gold < home.cost:
        return ok([t(locale, "rent.no_gold", cost=str(home.cost))])

    ctx.player.gold -= home.cost
    ctx.player.home_room_id = home.room_id
    label = _housing_label(home, locale)
    return ok(
        [t(locale, "rent.ok", name=label, cost=str(home.cost))],
        meta=player_meta(ctx),
        world_changed=True,
    )


register("rent", handle)