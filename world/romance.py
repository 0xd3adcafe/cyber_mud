from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from entities.player import Player
from world.mature import is_mature
from world.mature_flavor import romance_line

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "romance.yaml"


@dataclass
class RomanceProfile:
    id: str
    npc_id: str = ""
    flirt_affinity: int = 1
    spend_affinity: int = 3
    flirt_key: str = "flirt"
    spend_key: str = "spend_time"


def load_romance_profiles(path: Path | None = None) -> dict[str, RomanceProfile]:
    src = path or DATA_PATH
    if not src.exists():
        return {}
    with src.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return {
        rid: RomanceProfile(
            id=rid,
            npc_id=str(data.get("npc_id", rid)),
            flirt_affinity=int(data.get("flirt_affinity", 1)),
            spend_affinity=int(data.get("spend_affinity", 3)),
            flirt_key=str(data.get("flirt_key", "flirt")),
            spend_key=str(data.get("spend_key", "spend_time")),
        )
        for rid, data in (raw.get("romances") or {}).items()
    }


def _affinity(player: Player, profile_id: str) -> int:
    return int(player.romance_flags.get(profile_id, "0"))


def _set_affinity(player: Player, profile_id: str, value: int) -> None:
    player.romance_flags[profile_id] = str(value)


def profile_for_npc(profiles: dict[str, RomanceProfile], npc_id: str) -> RomanceProfile | None:
    for profile in profiles.values():
        if profile.npc_id == npc_id:
            return profile
    return None


def flirt_with_npc(player: Player, npc_id: str, locale: str, profiles: dict[str, RomanceProfile]) -> list[str]:
    if not is_mature(player):
        from shared.i18n import t

        return [t(locale, "mature.refused")]
    profile = profile_for_npc(profiles, npc_id)
    if profile is None:
        from shared.i18n import t

        return [t(locale, "romance.no_profile")]
    affinity = _affinity(player, profile.id)
    tier = min(affinity + 1, 3)
    _set_affinity(player, profile.id, tier)
    return [romance_line(locale, profile.flirt_key, tier)]


def spend_time_with_npc(player: Player, npc_id: str, locale: str, profiles: dict[str, RomanceProfile]) -> list[str]:
    if not is_mature(player):
        from shared.i18n import t

        return [t(locale, "mature.refused")]
    profile = profile_for_npc(profiles, npc_id)
    if profile is None:
        from shared.i18n import t

        return [t(locale, "romance.no_profile")]
    affinity = _affinity(player, profile.id)
    if affinity < profile.flirt_affinity:
        from shared.i18n import t

        return [t(locale, "romance.need_flirt")]
    tier = min(affinity + 1, 3)
    _set_affinity(player, profile.id, tier)
    spend_tier = min(max(tier - profile.flirt_affinity + 1, 1), 3)
    return [romance_line(locale, profile.spend_key, spend_tier)]