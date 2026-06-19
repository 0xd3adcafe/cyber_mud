from __future__ import annotations

from commands.auth_helpers import reset_player_to_guest
from commands.registry import CommandContext, ok, player_meta, register
from persistence.save import save_player
from shared.i18n import t


def handle(ctx: CommandContext):
    if not ctx.player.named:
        return ok([t(ctx.player.locale, "auth.required")])

    ended_combat = ctx.player.in_combat
    if ended_combat:
        from combat.encounter import encounter_for_player, end_encounter

        encounter = encounter_for_player(ctx.state, ctx.player)
        if encounter is not None:
            end_encounter(ctx.state, ctx.player, encounter)

    name = ctx.player.name
    locale = ctx.player.locale
    save_player(ctx.player)
    reset_player_to_guest(ctx.player, ctx.state.world.start_room)
    return ok(
        [t(locale, "game.quit")],
        meta=player_meta(ctx),
        world_changed=ended_combat,
        broadcast_key="game.leave",
        broadcast_kwargs={"name": name},
    )


register("quit", handle)