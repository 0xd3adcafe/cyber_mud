from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from combat.encounter import npc_label
from shared.target_resolve import resolve_npc
from world.mature import gate_command
from world.mature_voice import apply_mature_template, resolve_mature_voice
from world.romance import affinity_for_profile, load_romance_profiles, profile_for_npc, scene_line_for_npc


def _scene_status_lines(ctx: CommandContext, locale: str) -> list[str]:
    profiles = load_romance_profiles()
    lines = [t(locale, "scene.status_header")]
    found = False
    for npc_id in ctx.state.npcs_in_room(ctx.player.room_id):
        profile = profile_for_npc(profiles, npc_id)
        if profile is None:
            continue
        label = npc_label(ctx.state, npc_id, locale)
        affinity = affinity_for_profile(ctx.player, profile.id)
        lines.append(
            t(
                locale,
                "scene.status_row",
                name=label,
                stage=str(affinity),
                min_stage=str(profile.scene_min_stage),
            )
        )
        found = True
    if not found:
        lines.append(t(locale, "scene.no_targets"))
    return lines


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    refusal = gate_command(ctx.player, locale, "scene")
    if refusal is not None:
        return ok(refusal)

    args = ctx.args.strip()
    if not args or args.lower() == "status":
        return ok(_scene_status_lines(ctx, locale), meta=player_meta(ctx))

    profiles = load_romance_profiles()
    npc_result = resolve_npc(ctx, args, verb="scene")
    if npc_result.needs_response:
        return ok(npc_result.lines)
    if not npc_result.ok:
        return ok([t(locale, "scene.usage")])

    npc_id = npc_result.value
    profile = profile_for_npc(profiles, npc_id)
    if profile is None:
        return ok([t(locale, "romance.no_profile")])

    affinity = affinity_for_profile(ctx.player, profile.id)
    if affinity < profile.scene_min_stage:
        label = npc_label(ctx.state, npc_id, locale)
        return ok(
            [
                t(
                    locale,
                    "scene.need_stage",
                    name=label,
                    stage=str(profile.scene_min_stage),
                )
            ]
        )

    if profile.scene_requires_quest:
        from world.quests import quest_is_done

        if not quest_is_done(ctx.player, profile.scene_requires_quest):
            label = npc_label(ctx.state, npc_id, locale)
            quest = ctx.state.world.quest(profile.scene_requires_quest)
            quest_name = (
                quest.name_en or quest.name_zh
                if quest and locale == "en"
                else (quest.name_zh if quest else profile.scene_requires_quest)
            )
            return ok(
                [
                    t(
                        locale,
                        "scene.need_quest",
                        name=label,
                        quest=quest_name or profile.scene_requires_quest,
                    )
                ]
            )

    if profile.scene_requires_home:
        if ctx.player.home_room_id != profile.scene_requires_home:
            label = npc_label(ctx.state, npc_id, locale)
            home = ctx.state.world.home_for_room(profile.scene_requires_home)
            home_name = (
                (home.name_en or home.name_zh)
                if home and locale == "en"
                else (home.name_zh if home else profile.scene_requires_home)
            )
            return ok(
                [
                    t(
                        locale,
                        "scene.need_home",
                        name=label,
                        home=home_name or profile.scene_requires_home,
                    )
                ]
            )

    room = ctx.state.world.room(ctx.player.room_id)
    voice = resolve_mature_voice(ctx.player, ctx.state, room, npc_id=npc_id)
    npc_name = npc_label(ctx.state, npc_id, locale)
    line = scene_line_for_npc(locale, profile, affinity, voice=voice)
    line = apply_mature_template(line, ctx.player, locale, npc_name=npc_name, voice=voice)
    return ok([line], meta=player_meta(ctx))


register("scene", handle)