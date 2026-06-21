from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.persona import PERSONA_MAX_LEN, normalize_persona


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    args = ctx.args.strip()
    if not args:
        persona = normalize_persona(ctx.player.persona)
        if persona:
            return ok([t(locale, "persona.show", text=persona)], meta=player_meta(ctx))
        return ok([t(locale, "persona.look_player_empty")], meta=player_meta(ctx))

    verb, _, rest = args.partition(" ")
    verb = verb.lower()
    if verb == "set":
        text = rest.strip()
        if not text:
            return ok([t(locale, "persona.usage")])
        ctx.player.persona = normalize_persona(text)
        return ok(
            [t(locale, "persona.set_ok", text=ctx.player.persona)],
            meta=player_meta(ctx),
            world_changed=True,
        )
    if verb == "clear":
        ctx.player.persona = ""
        return ok([t(locale, "persona.clear_ok")], meta=player_meta(ctx), world_changed=True)

    return ok([t(locale, "persona.usage")])


register("persona", handle)