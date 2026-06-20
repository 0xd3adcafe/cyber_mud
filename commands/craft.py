from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.names import matches_name
from world.craft import can_craft, perform_craft


def _resolve_recipe_id(ctx: CommandContext, name: str) -> str | None:
    needle = name.strip().lower()
    for rid, recipe in ctx.state.world.recipes.items():
        if matches_name(needle, rid, recipe.name_zh, recipe.name_en):
            return rid
    return None


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    target = ctx.args.strip()
    if not target:
        lines = [t(locale, "craft.header"), ""]
        for rid, recipe in ctx.state.world.recipes.items():
            if can_craft(ctx.player, ctx.state, recipe) is None:
                status = t(locale, "craft.ready")
            else:
                status = t(locale, "craft.need_parts")
            label = recipe.name_zh if locale == "zh" else (recipe.name_en or recipe.name_zh)
            lines.append(f"  • {label or rid} — {status}")
        lines.append("")
        lines.append(t(locale, "craft.usage"))
        return ok(lines, meta=player_meta(ctx))

    rid = _resolve_recipe_id(ctx, target)
    if rid is None:
        return ok([t(locale, "craft.unknown", name=target)])

    recipe = ctx.state.world.recipe(rid)
    if recipe is None:
        return ok([t(locale, "craft.unknown", name=target)])

    lines = perform_craft(ctx.player, ctx.state, recipe, locale)
    return ok(lines, meta=player_meta(ctx), world_changed=True)


register("craft", handle)