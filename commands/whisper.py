from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from combat.encounter import npc_label
from shared.names import matches_name
from shared.target_resolve import resolve_npc
from world.mature import gate_command, is_mature
from world.mature_voice import apply_mature_template, mature_voice_line, resolve_mature_voice
from world.romance import load_romance_profiles, profile_for_npc


def _find_peer(ctx: CommandContext, target: str):
    needle = target.strip()
    if not needle:
        return None
    candidates = list(ctx.peers)
    if ctx.player.room_id:
        for peer in ctx.all_players:
            if peer is ctx.player or not peer.named:
                continue
            if peer.room_id == ctx.player.room_id and peer not in candidates:
                candidates.append(peer)
    for peer in candidates:
        if matches_name(needle, peer.name):
            return peer
    return None


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    args = ctx.args.strip()
    if not args:
        return ok([t(locale, "whisper.usage")])

    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        return ok([t(locale, "whisper.usage")])
    target_name, message = parts[0], parts[1].strip()
    if not message:
        return ok([t(locale, "whisper.usage")])

    room = ctx.state.world.room(ctx.player.room_id)
    peer = _find_peer(ctx, target_name)
    if peer is not None:
        if is_mature(ctx.player):
            voice = resolve_mature_voice(ctx.player, ctx.state, room)
            line = mature_voice_line(
                locale,
                "whisper.player",
                voice,
                sender=ctx.player.name,
                target=peer.name,
                message=message,
            )
            if line.startswith("whisper."):
                line = t(locale, "whisper.player_ok", target=peer.name, message=message)
        else:
            line = t(locale, "whisper.player_ok", target=peer.name, message=message)
        return ok([line], meta=player_meta(ctx))

    refusal = gate_command(ctx.player, locale, "whisper")
    npc_result = resolve_npc(ctx, target_name, verb="whisper")
    if npc_result.needs_response:
        return ok(npc_result.lines)
    if not npc_result.ok:
        return ok([t(locale, "whisper.not_found", target=target_name)])

    npc_id = npc_result.value
    profiles = load_romance_profiles()
    profile = profile_for_npc(profiles, npc_id)
    voice = resolve_mature_voice(ctx.player, ctx.state, room, npc_id=npc_id)
    npc = ctx.state.world.npc(npc_id)
    npc_name = npc_label(ctx.state, npc_id, locale)

    if profile and profile.whisper_key:
        base = f"whisper.{profile.whisper_key}"
    else:
        base = f"whisper.{npc_id}"
    line = mature_voice_line(locale, base, voice, player=ctx.player.name, message=message, npc=npc_name)
    if line.startswith("whisper."):
        line = t(locale, "whisper.npc_ok", target=npc_name, message=message)
    line = apply_mature_template(line, ctx.player, locale, npc_name=npc_name, voice=voice)
    return ok([line], meta=player_meta(ctx))


register("whisper", handle)