from __future__ import annotations

from commands.auth_helpers import parse_two_secret_fields
from commands.registry import CommandContext, ok, register
from persistence.passwords import hash_password, verify_password
from persistence.save import save_player
from server.audit_log import log_security_event
from server.session_tokens import issue_session_token, revoke_tokens_for
from shared.i18n import t
from shared.security import validate_password


def handle(ctx: CommandContext):
    if not ctx.player.named:
        return ok([t(ctx.player.locale, "auth.required")])

    parsed = parse_two_secret_fields(ctx.args)
    if parsed is None:
        return ok([t(ctx.player.locale, "auth.changepass_usage")])

    current_password, new_password = parsed
    if not verify_password(current_password, ctx.player.password_hash):
        log_security_event(
            "auth_changepass_failure",
            player=ctx.player.name,
            reason="bad_current_password",
        )
        return ok([t(ctx.player.locale, "auth.changepass_bad_current")])

    if verify_password(new_password, ctx.player.password_hash):
        return ok([t(ctx.player.locale, "auth.changepass_same")])

    if err := validate_password(new_password):
        return ok([t(ctx.player.locale, err)])

    ctx.player.password_hash = hash_password(new_password)
    revoke_tokens_for(ctx.player.name)
    token = issue_session_token(ctx.player.name)
    save_player(ctx.player)
    log_security_event("auth_changepass_success", player=ctx.player.name)
    return ok(
        [t(ctx.player.locale, "auth.changepass_ok")],
        meta={"session_token": token},
    )


register("changepass", handle)