from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.quests import (
    abandon_quest,
    accept_quest,
    format_journal_lines,
    quest_available,
    quest_is_done,
    quest_status,
)
from world.street_cred import street_cred_rank


def _quest_name(quest, locale: str) -> str:
    if locale == "en" and quest.name_en:
        return quest.name_en
    return quest.name_zh or quest.id


def _status_label(ctx: CommandContext, quest_id: str) -> str:
    locale = ctx.player.locale
    quest = ctx.state.world.quest(quest_id)
    if quest_is_done(ctx.player, quest_id):
        return t(locale, "gigs.status.done")
    if ctx.player.active_quest == quest_id:
        status = quest_status(ctx.player, quest_id)
        if status == "ready":
            return t(locale, "gigs.status.ready")
        return t(locale, "gigs.status.active")
    if quest is not None and not quest_available(ctx.player, quest):
        return t(locale, "gigs.status.locked")
    return t(locale, "gigs.status.available")


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
                from shared.locale_content import item_label

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
                status=_status_label(ctx, quest.id),
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
        return _list_gigs(ctx)

    verb, _, rest = args.partition(" ")
    verb = verb.lower()

    if verb == "accept":
        quest_id = rest.strip()
        if not quest_id:
            return ok([t(locale, "gigs.accept_usage")])
        lines = accept_quest(ctx.player, ctx.state, quest_id, locale)
        return ok(lines, meta=player_meta(ctx), world_changed=True)

    if verb == "abandon":
        lines = abandon_quest(ctx.player, ctx.state, locale)
        return ok(lines, meta=player_meta(ctx), world_changed=True)

    if verb in {"journal", "log"}:
        lines = format_journal_lines(ctx.player, ctx.state, locale)
        return ok(lines, meta=player_meta(ctx))

    return _list_gigs(ctx)


register("gigs", handle)
register("gig", handle)