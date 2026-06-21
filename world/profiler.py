from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from entities.npc import NPC
from entities.player import Player
from shared.i18n import t
from shared.locale_content import npc_label_with_id

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "profiler.yaml"

_CACHE: dict[str, "NpcProfile"] | None = None


@dataclass
class NpcProfile:
    npc_id: str
    occupation_zh: str = ""
    occupation_en: str = ""
    income_band: str = ""
    traits: list[str] = field(default_factory=list)
    vulnerability_zh: str = ""
    vulnerability_en: str = ""


def clear_profiler_cache() -> None:
    global _CACHE
    _CACHE = None


def load_profiler_profiles(path: Path | None = None) -> dict[str, NpcProfile]:
    global _CACHE
    if _CACHE is not None and path is None:
        return _CACHE
    src = path or DATA_PATH
    raw = yaml.safe_load(src.read_text(encoding="utf-8")) if src.exists() else {}
    profiles: dict[str, NpcProfile] = {}
    for npc_id, data in (raw.get("profiles") or {}).items():
        profiles[str(npc_id)] = NpcProfile(
            npc_id=str(npc_id),
            occupation_zh=str(data.get("occupation_zh", "")),
            occupation_en=str(data.get("occupation_en", "")),
            income_band=str(data.get("income_band", "")),
            traits=[str(tag) for tag in (data.get("traits") or [])],
            vulnerability_zh=str(data.get("vulnerability_zh", "")),
            vulnerability_en=str(data.get("vulnerability_en", "")),
        )
    if path is None:
        _CACHE = profiles
    return profiles


def profiler_entry(npc_id: str) -> NpcProfile | None:
    return load_profiler_profiles().get(npc_id)


def is_profiled(player: Player, npc_id: str) -> bool:
    return npc_id in player.profiled_npcs


def profile_npc(player: Player, npc_id: str) -> bool:
    """Cache profiler intel for npc_id. Returns True if newly profiled."""
    if npc_id in player.profiled_npcs:
        return False
    player.profiled_npcs.append(npc_id)
    return True


def _occupation(profile: NpcProfile, locale: str) -> str:
    if locale == "zh":
        return profile.occupation_zh or profile.occupation_en
    return profile.occupation_en or profile.occupation_zh


def _vulnerability(profile: NpcProfile, locale: str) -> str:
    if locale == "zh":
        return profile.vulnerability_zh or profile.vulnerability_en
    return profile.vulnerability_en or profile.vulnerability_zh


def _trait_labels(profile: NpcProfile, locale: str) -> list[str]:
    labels: list[str] = []
    for trait in profile.traits:
        key = f"profiler.traits.{trait}"
        label = t(locale, key)
        labels.append(label if label != key else trait)
    return labels


def format_profile_scan(
    profile: NpcProfile,
    npc: NPC | None,
    player: Player,
    *,
    cached: bool = False,
) -> list[str]:
    locale = player.locale
    name = npc_label_with_id(npc, locale) if npc else profile.npc_id
    header_key = "profiler.header_cached" if cached else "profiler.header"
    lines = [t(locale, header_key, name=name), ""]
    occupation = _occupation(profile, locale)
    if occupation:
        lines.append(t(locale, "profiler.occupation", value=occupation))
    if profile.income_band:
        band_key = f"profiler.income_band.{profile.income_band}"
        band_label = t(locale, band_key)
        if band_label == band_key:
            band_label = profile.income_band
        lines.append(t(locale, "profiler.income", value=band_label))
    traits = _trait_labels(profile, locale)
    if traits:
        lines.append(t(locale, "profiler.line_traits", value=", ".join(traits)))
    vulnerability = _vulnerability(profile, locale)
    if vulnerability:
        lines.append(t(locale, "profiler.vulnerability", value=vulnerability))
    return lines