from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.prompt_tokens import DEFAULT_PROMPT, PROMPT_TOKENS, effective_prompt, expand_prompt


def handle(ctx: CommandContext):
    args = ctx.args.strip()
    if not args or args == "show":
        template = effective_prompt(ctx.player)
        expanded = expand_prompt(template, ctx.player, ctx.state)
        lines = [
            t(ctx.player.locale, "prompt.show_header"),
            t(ctx.player.locale, "prompt.template", template=template),
            t(ctx.player.locale, "prompt.expanded", expanded=expanded),
            "",
            t(ctx.player.locale, "prompt.tokens_header"),
        ]
        for token, desc_key in PROMPT_TOKENS.items():
            lines.append(t(ctx.player.locale, "prompt.token_line", token=token, desc=t(ctx.player.locale, desc_key)))
        return ok(lines, meta=player_meta(ctx))

    if args.startswith("set "):
        template = args[4:].strip()
        if not template:
            return ok([t(ctx.player.locale, "prompt.usage")])
        ctx.player.prompt_mud = template
        expanded = expand_prompt(template, ctx.player, ctx.state)
        return ok(
            [
                t(ctx.player.locale, "prompt.set_ok", template=template),
                t(ctx.player.locale, "prompt.expanded", expanded=expanded),
            ],
            meta=player_meta(ctx),
            world_changed=True,
        )

    if args == "reset":
        ctx.player.prompt_mud = ""
        expanded = expand_prompt(DEFAULT_PROMPT, ctx.player, ctx.state)
        return ok(
            [
                t(ctx.player.locale, "prompt.reset_ok"),
                t(ctx.player.locale, "prompt.expanded", expanded=expanded),
            ],
            meta=player_meta(ctx),
            world_changed=True,
        )

    return ok([t(ctx.player.locale, "prompt.usage")])


register("prompt", handle)