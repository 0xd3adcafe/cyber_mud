from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.quests import quest_is_done, quest_status
from world.street_cred import street_cred_rank


def _quest_name(quest, locale: str) -> str:
    if locale == "en" and quest.name_en:
        return quest.name_en
    return quest.name_zh or quest.id


def _status_label(ctx: CommandContext, quest_id: str) -> str:
    locale = ctx.player.locale
    if quest_is_done(ctx.player, quest_id):
        return t(locale, "gigs.status.done")
    if ctx.player.active_quest == quest_id:
        status = quest_status(ctx.player, quest_id)
        if status == "ready":
            return t(locale, "gigs.status.ready")
        return t(locale, "gigs.status.active")
    return t(locale, "gigs.status.available")


def handle(ctx: CommandContext):
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
        reward = "、".join(reward_parts) if reward_parts else "—"
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
    lines.append("")
    lines.append(t(locale, "gigs.hint"))
    return ok(lines, meta=player_meta(ctx))


register("gigs", handle)
register("gig", handle)