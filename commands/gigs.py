from __future__ import annotations

from commands.gigs_helpers import build_gigs_ui, format_gigs_panel, status_label
from commands.registry import CommandContext, ok, ok_panel, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label
from world.quests import (
    abandon_quest,
    accept_quest,
    quest_available,
    quest_is_done,
    quest_status,
)
from world.street_cred import street_cred_rank


def _quest_name(quest, locale: str) -> str:
    if locale == "en" and quest.name_en:
        return quest.name_en
    return quest.name_zh or quest.id


def _gigs_panel(ctx: CommandContext):
    return ok_panel(
        format_gigs_panel(ctx),
        panel="gigs",
        ui_json=build_gigs_ui(ctx),
        meta=player_meta(ctx),
    )


def _list_gigs(ctx: CommandContext):
    locale = ctx.player.locale
    lines = [
        t(locale, "gigs.header"),
        t(locale, "gigs.street_cred", cred=str(ctx.player.street_cred), rank=street_cred_rank(ctx.player, locale)),
        "",
    ]
    for quest in ctx.state.world.quests.values():
        desc = quest.description_zh if locale == "zh" else (quest.description_en or quest.description_zh)
        reward_parts = []
        if quest.reward_gold:
            reward_parts.append(t(locale, "gigs.reward_gold", amount=str(quest.reward_gold)))
        if quest.reward_xp:
            reward_parts.append(t(locale, "gigs.reward_xp", amount=str(quest.reward_xp)))
        if quest.reward_street_cred:
            reward_parts.append(t(locale, "gigs.reward_cred", amount=str(quest.reward_street_cred)))
        for item_id in quest.reward_items:
            item = ctx.state.world.item(item_id)
            if item:
                reward_parts.append(item_label(item, locale))
        reward = "、".join(reward_parts) if reward_parts else "—"
        req = ""
        if quest.street_cred_req:
            req = t(locale, "gigs.req_cred", amount=str(quest.street_cred_req))
        if quest.requires_quest:
            required = ctx.state.world.quest(quest.requires_quest)
            req_name = _quest_name(required, locale) if required else quest.requires_quest
            req = f"{req} {t(locale, 'gigs.req_quest', quest=req_name)}".strip()
        lines.append(
            t(
                locale,
                "gigs.line",
                name=_quest_name(quest, locale),
                status=status_label(ctx, quest.id),
                reward=reward,
                desc=desc or "",
            )
        )
        if req:
            lines.append(t(locale, "gigs.req_line", req=req))
    lines.append("")
    lines.append(t(locale, "gigs.hint"))
    return ok(lines, meta=player_meta(ctx))


def handle(ctx: CommandContext):
    args = ctx.args.strip()
    locale = ctx.player.locale
    if not args:
        return _gigs_panel(ctx)

    verb, _, rest = args.partition(" ")
    verb = verb.lower()

    if verb in {"journal", "log"}:
        return _gigs_panel(ctx)

    if verb == "accept":
        quest_id = rest.strip()
        if not quest_id:
            return ok([t(locale, "gigs.accept_usage")])
        lines = accept_quest(ctx.player, ctx.state, quest_id, locale)
        return ok(lines, meta=player_meta(ctx), world_changed=True, refresh_sidebar=True)

    if verb == "abandon":
        lines = abandon_quest(ctx.player, ctx.state, locale)
        return ok(lines, meta=player_meta(ctx), world_changed=True, refresh_sidebar=True)

    if verb == "list":
        return _list_gigs(ctx)

    return _list_gigs(ctx)


register("gigs", handle)
register("gig", handle)
register("journal", handle)