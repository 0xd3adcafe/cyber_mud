from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from entities.player import Player
from shared.mature_paths import romance_path
from world.mature import is_mature
from world.mature_flavor import romance_line, scene_line
from world.mature_voice import apply_mature_template, resolve_mature_voice
from world.state import WorldState
from world.world import Room

DATA_PATH = romance_path()
ROMANCE_TIER_MAX = 5


@dataclass
class RomanceProfile:
    id: str
    npc_id: str = ""
    flirt_affinity: int = 1
    spend_affinity: int = 3
    flirt_key: str = "flirt"
    spend_key: str = "spend_time"
    scene_min_stage: int = 3
    scene_key: str = ""
    whisper_key: str = ""
    voice_default: str = "noir"
    voice_override: str = ""
    voice_triggers: tuple[str, ...] = ()
    scene_requires_quest: str = ""


def load_romance_profiles(path: Path | None = None) -> dict[str, RomanceProfile]:
    src = path or DATA_PATH
    if not src.exists():
        return {}
    with src.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    profiles: dict[str, RomanceProfile] = {}
    for rid, data in (raw.get("romances") or {}).items():
        triggers = tuple(str(x) for x in (data.get("voice_triggers") or []))
        profiles[rid] = RomanceProfile(
            id=rid,
            npc_id=str(data.get("npc_id", rid)),
            flirt_affinity=int(data.get("flirt_affinity", 1)),
            spend_affinity=int(data.get("spend_affinity", 3)),
            flirt_key=str(data.get("flirt_key", "flirt")),
            spend_key=str(data.get("spend_key", "spend_time")),
            scene_min_stage=int(data.get("scene_min_stage", 3)),
            scene_key=str(data.get("scene_key", rid)),
            whisper_key=str(data.get("whisper_key", rid)),
            voice_default=str(data.get("voice_default", "noir")),
            voice_override=str(data.get("voice_override", "")),
            voice_triggers=triggers,
            scene_requires_quest=str(data.get("scene_requires_quest", "")),
        )
    return profiles


def affinity_for_profile(player: Player, profile_id: str) -> int:
    return int(player.romance_flags.get(profile_id, "0"))


def _set_affinity(player: Player, profile_id: str, value: int) -> None:
    player.romance_flags[profile_id] = str(value)


def profile_for_npc(profiles: dict[str, RomanceProfile], npc_id: str) -> RomanceProfile | None:
    for profile in profiles.values():
        if profile.npc_id == npc_id:
            return profile
    return None


def _npc_label(state: WorldState, npc_id: str, locale: str) -> str:
    from combat.encounter import npc_label

    return npc_label(state, npc_id, locale)


def flirt_with_npc(
    player: Player,
    npc_id: str,
    locale: str,
    profiles: dict[str, RomanceProfile],
    *,
    state: WorldState,
    room: Room | None,
) -> list[str]:
    if not is_mature(player):
        from shared.i18n import t

        return [t(locale, "mature.refused")]
    profile = profile_for_npc(profiles, npc_id)
    if profile is None:
        from shared.i18n import t

        return [t(locale, "romance.no_profile")]
    affinity = affinity_for_profile(player, profile.id)
    tier = min(affinity + 1, ROMANCE_TIER_MAX)
    _set_affinity(player, profile.id, tier)
    voice = resolve_mature_voice(player, state, room, npc_id=npc_id)
    if profile.voice_default == "lewd" and voice == "noir":
        voice = "lewd"
    line = romance_line(locale, profile.flirt_key, tier, voice=voice)
    line = apply_mature_template(
        line,
        player,
        locale,
        npc_name=_npc_label(state, npc_id, locale),
        voice=voice,
    )
    return [line]


def spend_time_with_npc(
    player: Player,
    npc_id: str,
    locale: str,
    profiles: dict[str, RomanceProfile],
    *,
    state: WorldState,
    room: Room | None,
) -> list[str]:
    if not is_mature(player):
        from shared.i18n import t

        return [t(locale, "mature.refused")]
    profile = profile_for_npc(profiles, npc_id)
    if profile is None:
        from shared.i18n import t

        return [t(locale, "romance.no_profile")]
    affinity = affinity_for_profile(player, profile.id)
    if affinity < profile.flirt_affinity:
        from shared.i18n import t

        return [t(locale, "romance.need_flirt")]
    tier = min(affinity + 1, ROMANCE_TIER_MAX)
    _set_affinity(player, profile.id, tier)
    spend_tier = min(max(tier - profile.flirt_affinity + 1, 1), ROMANCE_TIER_MAX)
    voice = resolve_mature_voice(player, state, room, npc_id=npc_id)
    if profile.voice_default == "lewd" and voice == "noir":
        voice = "lewd"
    line = romance_line(locale, profile.spend_key, spend_tier, voice=voice)
    line = apply_mature_template(
        line,
        player,
        locale,
        npc_name=_npc_label(state, npc_id, locale),
        voice=voice,
    )
    return [line]


def scene_line_for_npc(
    locale: str,
    profile: RomanceProfile,
    tier: int,
    *,
    voice: str = "noir",
) -> str:
    key = profile.scene_key or profile.npc_id
    return scene_line(locale, key, tier, voice=voice)