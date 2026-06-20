from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.target_resolve import resolve_npc
from shared.i18n import t
from world.romance import flirt_with_npc, load_romance_profiles, spend_time_with_npc


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    args = ctx.args.strip()
    if not args:
        return ok([t(locale, "flirt.usage")])

    verb, _, rest = args.partition(" ")
    verb = verb.lower()
    target = rest.strip() if verb in {"spend", "time"} else args
    if verb == "spend" and rest.lower().startswith("time "):
        target = rest[5:].strip()

    profiles = load_romance_profiles()
    npc_result = resolve_npc(ctx, target, verb="flirt")
    if npc_result.needs_response:
        return ok(npc_result.lines)
    if not npc_result.ok:
        return ok([t(locale, "talk.missing", name=target or args)])
    npc_id = npc_result.value

    if verb in {"spend", "time"} or args.lower().startswith("spend time "):
        lines = spend_time_with_npc(ctx.player, npc_id, locale, profiles)
    else:
        lines = flirt_with_npc(ctx.player, npc_id, locale, profiles)

    if not lines:
        npc = ctx.state.world.npc(npc_id)
        label = npc.name_zh if locale == "zh" else (npc.name_en or npc.name_zh) if npc else target
        lines = [t(locale, "talk.silent", name=label)]
    return ok(lines, meta=player_meta(ctx), world_changed=True)


register("flirt", handle)
register("spend_time", handle)