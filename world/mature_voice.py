from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

from entities.player import Player
from shared.mature_i18n import tm
from shared.mature_paths import MATURE_DATA_ROOT
from world.mature import has_mature_tag, is_mature
from world.state import WorldState
from world.status_effects import EFFECT_BLEED, EFFECT_OVERHEAT
from world.world import Room

VOICE_PATH = MATURE_DATA_ROOT / "voice.yaml"
MatureVoice = str  # "noir" | "lewd"


@dataclass
class VoiceConfig:
    lewd_consumables: frozenset[str] = frozenset()
    lewd_trace_min: int = 70
    lewd_humanity_max: int = 25
    mature_rooms: frozenset[str] = frozenset()
    voice_mature_bd_flag: str = "_voice_mature"


@lru_cache(maxsize=1)
def load_voice_config(path: Path | None = None) -> VoiceConfig:
    src = path or VOICE_PATH
    if not src.exists():
        return VoiceConfig()
    with src.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return VoiceConfig(
        lewd_consumables=frozenset(str(x) for x in (raw.get("lewd_consumables") or [])),
        lewd_trace_min=int(raw.get("lewd_trace_min", 70)),
        lewd_humanity_max=int(raw.get("lewd_humanity_max", 25)),
        mature_rooms=frozenset(str(x) for x in (raw.get("mature_rooms") or [])),
        voice_mature_bd_flag=str(raw.get("voice_mature_bd_flag", "_voice_mature")),
    )


def reset_voice_config() -> None:
    load_voice_config.cache_clear()


def _resolved_mature_line(locale: str, key: str, **kwargs: str) -> str | None:
    line = tm(locale, key, **kwargs)
    bare = key.removeprefix("mature.")
    if not line or line == key or line == bare:
        return None
    return line


def mature_voice_line(locale: str, base_key: str, voice: str, **kwargs: str) -> str:
    bare = base_key.removeprefix("mature.")
    for candidate in (f"mature.{voice}.{bare}", f"mature.noir.{bare}", f"mature.{bare}"):
        if line := _resolved_mature_line(locale, candidate, **kwargs):
            return line
    return tm(locale, f"mature.{bare}", **kwargs)


def _mature_bd_active(player: Player, cfg: VoiceConfig) -> bool:
    return player.braindance_flags.get(cfg.voice_mature_bd_flag) == "1"


def _lewd_consumable_carried(player: Player, cfg: VoiceConfig) -> bool:
    return bool(cfg.lewd_consumables & set(player.inventory))


def _status_lewd(player: Player) -> bool:
    status = player.player_status
    return status.get(EFFECT_BLEED, 0) > 0 or status.get(EFFECT_OVERHEAT, 0) > 0


def _room_lewd(room: Room | None, cfg: VoiceConfig) -> bool:
    if room is None:
        return False
    if room.id in cfg.mature_rooms:
        return True
    return has_mature_tag(room.tags)


def _npc_voice_lewd(
    player: Player,
    state: WorldState,
    room: Room | None,
    *,
    npc_id: str,
) -> bool:
    from world.romance import load_romance_profiles, profile_for_npc

    profiles = load_romance_profiles()
    cfg = load_voice_config()
    targets: list[str] = []
    if npc_id:
        targets.append(npc_id)
    elif room is not None:
        targets.extend(state.npcs_in_room(room.id))

    for nid in targets:
        profile = profile_for_npc(profiles, nid)
        if profile is None:
            continue
        if profile.voice_override == "lewd":
            return True
        if profile.voice_triggers and _profile_triggers_met(player, state, room, profile.voice_triggers, cfg):
            return True
    return False


def _profile_triggers_met(
    player: Player,
    state: WorldState,
    room: Room | None,
    triggers: tuple[str, ...],
    cfg: VoiceConfig,
) -> bool:
    checks = {
        "mature_room": lambda: _room_lewd(room, cfg),
        "bd_session": lambda: _mature_bd_active(player, cfg),
        "bleed": lambda: player.player_status.get(EFFECT_BLEED, 0) > 0,
        "overheat": lambda: player.player_status.get(EFFECT_OVERHEAT, 0) > 0,
        "low_humanity": lambda: player.humanity <= cfg.lewd_humanity_max,
        "high_trace": lambda: player.net_trace >= cfg.lewd_trace_min,
        "lewd_consumable": lambda: _lewd_consumable_carried(player, cfg),
    }
    for trigger in triggers:
        fn = checks.get(trigger)
        if fn and fn():
            return True
    return False


def resolve_mature_voice(
    player: Player,
    state: WorldState,
    room: Room | None,
    *,
    npc_id: str = "",
) -> MatureVoice:
    if not is_mature(player):
        return "noir"

    cfg = load_voice_config()
    if _room_lewd(room, cfg):
        return "lewd"
    if _mature_bd_active(player, cfg):
        return "lewd"
    if _status_lewd(player):
        return "lewd"
    if player.humanity <= cfg.lewd_humanity_max:
        return "lewd"
    if player.net_trace >= cfg.lewd_trace_min:
        return "lewd"
    if _lewd_consumable_carried(player, cfg):
        return "lewd"
    if _npc_voice_lewd(player, state, room, npc_id=npc_id):
        return "lewd"
    return "noir"


def apply_mature_template(
    text: str,
    player: Player,
    locale: str,
    npc_name: str = "",
    *,
    voice: str = "noir",
) -> str:
    from world.persona import persona_one_liner

    persona = persona_one_liner(player, locale, voice=voice)
    replacements = {
        "player": player.name,
        "persona": persona,
        "npc": npc_name,
    }
    try:
        return text.format(**replacements)
    except KeyError:
        return text