from __future__ import annotations

from commands.registry import CommandContext
from shared.i18n import t
from shared.locale_content import item_label
from shared.ui_json import panel_json
from world.quests import quest_available, quest_hint_for_quest, quest_is_done, quest_status
from world.street_cred import street_cred_rank


def _quest_name(quest, locale: str) -> str:
    if locale == "en" and quest.name_en:
        return quest.name_en
    return quest.name_zh or quest.id


def status_label(ctx: CommandContext, quest_id: str) -> str:
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


def _reward_summary(ctx: CommandContext, quest) -> str:
    locale = ctx.player.locale
    parts: list[str] = []
    if quest.reward_gold:
        parts.append(t(locale, "gigs.reward_gold", amount=str(quest.reward_gold)))
    if quest.reward_xp:
        parts.append(t(locale, "gigs.reward_xp", amount=str(quest.reward_xp)))
    if quest.reward_street_cred:
        parts.append(t(locale, "gigs.reward_cred", amount=str(quest.reward_street_cred)))
    for item_id in quest.reward_items:
        item = ctx.state.world.item(item_id)
        if item:
            parts.append(item_label(item, locale))
    return "、".join(parts) if parts else "—"


def format_gigs_panel(ctx: CommandContext) -> list[str]:
    locale = ctx.player.locale
    lines = [
        t(locale, "gigs.header"),
        t(
            locale,
            "gigs.street_cred",
            cred=str(ctx.player.street_cred),
            rank=street_cred_rank(ctx.player, locale),
        ),
        "",
    ]
    if ctx.player.active_quest:
        quest = ctx.state.world.quest(ctx.player.active_quest)
        if quest:
            lines.append(t(locale, "gigs.journal_active", quest=_quest_name(quest, locale)))
            hint = quest_hint_for_quest(ctx.player, ctx.state, quest, locale)
            if hint:
                lines.append(t(locale, "gigs.journal_hint", hint=hint))
            lines.append("")
    from world.mature import is_mature

    for quest in ctx.state.world.quests.values():
        if quest.rating == "mature" and not is_mature(ctx.player):
            continue
        lines.append(
            t(
                locale,
                "gigs.line",
                name=_quest_name(quest, locale),
                status=status_label(ctx, quest.id),
                reward=_reward_summary(ctx, quest),
                desc="",
            )
        )
    done = [qid for qid in ctx.state.world.quests if quest_is_done(ctx.player, qid)]
    lines.append("")
    if done:
        lines.append(t(locale, "gigs.journal_done", count=str(len(done))))
        for qid in sorted(done):
            quest = ctx.state.world.quest(qid)
            if quest:
                lines.append(f"  · {_quest_name(quest, locale)}")
    else:
        lines.append(t(locale, "gigs.journal_none_done"))
    lines.append("")
    lines.append(t(locale, "gigs.panel_hint"))
    return lines


def build_gigs_ui(ctx: CommandContext) -> str:
    locale = ctx.player.locale
    sections: list[dict] = [
        {
            "kind": "row",
            "label": t(locale, "gigs.panel_cred_label"),
            "value": t(
                locale,
                "gigs.street_cred",
                cred=str(ctx.player.street_cred),
                rank=street_cred_rank(ctx.player, locale),
            ),
        },
    ]
    if ctx.player.active_quest:
        quest = ctx.state.world.quest(ctx.player.active_quest)
        if quest:
            active_lines = [t(locale, "gigs.journal_active", quest=_quest_name(quest, locale))]
            hint = quest_hint_for_quest(ctx.player, ctx.state, quest, locale)
            if hint:
                active_lines.append(t(locale, "gigs.journal_hint", hint=hint))
            sections.append({"kind": "text", "lines": active_lines})
    from world.mature import is_mature

    quest_items = [
        t(
            locale,
            "gigs.panel_quest_line",
            name=_quest_name(quest, locale),
            status=status_label(ctx, quest.id),
        )
        for quest in ctx.state.world.quests.values()
        if not (quest.rating == "mature" and not is_mature(ctx.player))
    ]
    sections.append({"kind": "list", "title": t(locale, "gigs.panel_quests_title"), "items": quest_items})
    done = [qid for qid in ctx.state.world.quests if quest_is_done(ctx.player, qid)]
    if done:
        done_items = []
        for qid in sorted(done):
            quest = ctx.state.world.quest(qid)
            if quest:
                done_items.append(_quest_name(quest, locale))
        sections.append(
            {
                "kind": "list",
                "title": t(locale, "gigs.journal_done", count=str(len(done))),
                "items": done_items,
            }
        )
    return panel_json(panel="gigs", title=t(locale, "gigs.header"), sections=sections)