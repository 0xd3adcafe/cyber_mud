from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from entities.player import Player
from shared.i18n import t
from world.modifiers import period_for_room, weather_for_room
from world.state import WorldState
from world.status_effects import EFFECT_BLEED
from world.world import Room

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "life.yaml"

POSTURE_STANDING = "standing"
POSTURE_SITTING = "sitting"
POSTURE_LYING = "lying"
POSTURE_SLEEPING = "sleeping"

REST_POSTURES = frozenset({POSTURE_SITTING, POSTURE_LYING, POSTURE_SLEEPING})


@dataclass
class PostureProfile:
    fatigue_delta: int = 0
    hp_regen_mult: float = 1.0
    ram_regen: int = 0


@dataclass
class LifeAnchor:
    posture: str = POSTURE_SITTING
    hp_mult: float = 1.0
    allows_sleep: bool = False


@dataclass
class LifeConfig:
    fatigue_max: int = 100
    postures: dict[str, PostureProfile] = field(default_factory=dict)
    sleep_room_tags: frozenset[str] = frozenset()
    rest_room_tags: frozenset[str] = frozenset()
    indoor_room_tags: frozenset[str] = frozenset()
    weather_outdoor_mult: dict[str, float] = field(default_factory=dict)
    period_hp_mult: dict[str, float] = field(default_factory=dict)
    districts_no_outdoor_sleep: frozenset[str] = frozenset()
    anchors: dict[str, LifeAnchor] = field(default_factory=dict)


_CONFIG: LifeConfig | None = None


def load_life_config(path: Path | None = None) -> LifeConfig:
    global _CONFIG
    if _CONFIG is not None and path is None:
        return _CONFIG
    raw = yaml.safe_load((path or DATA_PATH).read_text(encoding="utf-8")) or {}
    postures: dict[str, PostureProfile] = {}
    for pid, data in (raw.get("postures") or {}).items():
        postures[str(pid)] = PostureProfile(
            fatigue_delta=int(data.get("fatigue_delta", 0)),
            hp_regen_mult=float(data.get("hp_regen_mult", 1.0)),
            ram_regen=int(data.get("ram_regen", 0)),
        )
    anchors: dict[str, LifeAnchor] = {}
    for aid, data in (raw.get("anchors") or {}).items():
        anchors[str(aid)] = LifeAnchor(
            posture=str(data.get("posture", POSTURE_SITTING)),
            hp_mult=float(data.get("hp_mult", 1.0)),
            allows_sleep=bool(data.get("allows_sleep", False)),
        )
    cfg = LifeConfig(
        fatigue_max=int(raw.get("fatigue_max", 100)),
        postures=postures,
        sleep_room_tags=frozenset(str(x) for x in (raw.get("sleep_room_tags") or [])),
        rest_room_tags=frozenset(str(x) for x in (raw.get("rest_room_tags") or [])),
        indoor_room_tags=frozenset(str(x) for x in (raw.get("indoor_room_tags") or [])),
        weather_outdoor_mult={str(k): float(v) for k, v in (raw.get("weather_outdoor_mult") or {}).items()},
        period_hp_mult={str(k): float(v) for k, v in (raw.get("period_hp_mult") or {}).items()},
        districts_no_outdoor_sleep=frozenset(str(x) for x in (raw.get("districts_no_outdoor_sleep") or [])),
        anchors=anchors,
    )
    if path is None:
        _CONFIG = cfg
    return cfg


def _cfg() -> LifeConfig:
    return load_life_config()


def is_resting(player: Player) -> bool:
    return player.posture in REST_POSTURES


def posture_label(posture: str, locale: str) -> str:
    key = f"life.posture.{posture}"
    label = t(locale, key)
    return label if label != key else posture


def life_blocked(player: Player, locale: str) -> str | None:
    if player.in_combat:
        return t(locale, "life.blocked_combat")
    if player.net_shell:
        return t(locale, "life.blocked_netrun")
    if player.chased_by_npc:
        return t(locale, "life.blocked_chase")
    return None


def wake_player(player: Player) -> bool:
    changed = player.posture != POSTURE_STANDING or player.life_anchor
    player.posture = POSTURE_STANDING
    player.life_anchor = ""
    return changed


def set_posture(player: Player, posture: str, *, anchor: str = "") -> None:
    player.posture = posture
    player.life_anchor = anchor if anchor else ""


def clamp_fatigue(player: Player) -> None:
    player.fatigue = max(0, min(_cfg().fatigue_max, player.fatigue))


def _room_tags(room: Room | None) -> set[str]:
    return set(room.tags) if room else set()


def _is_indoor(room: Room | None, cfg: LifeConfig) -> bool:
    tags = _room_tags(room)
    return bool(tags & cfg.indoor_room_tags)


def _room_allows_sleep(player: Player, room: Room | None, cfg: LifeConfig) -> bool:
    if room is None:
        return False
    tags = _room_tags(room)
    if tags & cfg.sleep_room_tags:
        return True
    if player.home_room_id and room.id == player.home_room_id:
        return True
    return False


def _anchor_profile(player: Player, cfg: LifeConfig) -> LifeAnchor | None:
    if not player.life_anchor:
        return None
    return cfg.anchors.get(player.life_anchor)


def sleep_refusal(player: Player, state: WorldState, locale: str) -> str | None:
    room = state.world.room(player.room_id)
    cfg = _cfg()
    if EFFECT_BLEED in player.player_status:
        return t(locale, "life.sleep_bleed")
    if player.player_status:
        return t(locale, "life.sleep_status")
    anchor = _anchor_profile(player, cfg)
    if anchor and anchor.allows_sleep:
        return None
    if _room_allows_sleep(player, room, cfg):
        return None
    if room and room.district in cfg.districts_no_outdoor_sleep and not _is_indoor(room, cfg):
        return t(locale, "life.sleep_unsafe")
    return t(locale, "life.sleep_nowhere")


def rest_environment_mult(player: Player, state: WorldState, period_id: str) -> float:
    cfg = _cfg()
    room = state.world.room(player.room_id)
    mult = 1.0
    tags = _room_tags(room)
    if tags & cfg.rest_room_tags:
        mult *= 1.15
    if player.home_room_id and room and room.id == player.home_room_id:
        mult *= 1.25
    anchor = _anchor_profile(player, cfg)
    if anchor:
        mult *= anchor.hp_mult
    if room and not _is_indoor(room, cfg):
        weather = weather_for_room(state, room.id)
        mult *= cfg.weather_outdoor_mult.get(weather, 1.0)
        if room.district in cfg.districts_no_outdoor_sleep:
            mult *= 0.5
    mult *= cfg.period_hp_mult.get(period_id, 1.0)
    if player.humanity <= 25:
        mult *= 0.85
    return mult


def posture_hp_mult(player: Player) -> float:
    if player.posture == POSTURE_STANDING:
        return 0.0
    profile = _cfg().postures.get(player.posture)
    return profile.hp_regen_mult if profile else 0.0


def posture_ram_regen(player: Player) -> int:
    profile = _cfg().postures.get(player.posture)
    if profile is None:
        return 0
    return profile.ram_regen


def apply_life_tick(player: Player, state: WorldState, period_id: str) -> list[str]:
    if not player.named or player.in_combat or player.posture == POSTURE_STANDING:
        return []
    cfg = _cfg()
    profile = cfg.postures.get(player.posture)
    if profile is None:
        return []
    locale = player.locale
    lines: list[str] = []
    if profile.fatigue_delta < 0 and player.fatigue > 0:
        player.fatigue = max(0, player.fatigue + profile.fatigue_delta)
    if player.posture == POSTURE_SLEEPING:
        lines.extend(_maybe_interrupt_sleep(player, state, locale))
    return lines


def _maybe_interrupt_sleep(player: Player, state: WorldState, locale: str) -> list[str]:
    room = state.world.room(player.room_id)
    cfg = _cfg()
    chance = 0.0
    if player.wanted_level >= 2:
        chance += 0.08 + player.wanted_level * 0.02
    if room and room.district in cfg.districts_no_outdoor_sleep and not _is_indoor(room, cfg):
        chance += 0.12
    weather = weather_for_room(state, player.room_id) if room else ""
    if weather == "acid_rain" and room and not _is_indoor(room, cfg):
        chance += 0.1
    if chance <= 0 or random.random() >= chance:
        return []
    wake_player(player)
    return [t(locale, "life.sleep_interrupted")]


def apply_anchor_from_interactable(player: Player, obj) -> tuple[str, bool]:
    """Return (posture, allows_sleep) from interactable kind/profile."""
    cfg = _cfg()
    profile_id = getattr(obj, "life_profile", "") or getattr(obj, "kind", "")
    anchor = cfg.anchors.get(profile_id)
    if anchor is None:
        kind = getattr(obj, "kind", "")
        if kind == "sleep":
            player.life_anchor = obj.id
            return POSTURE_LYING, True
        if kind == "rest":
            player.life_anchor = obj.id
            return POSTURE_SITTING, False
        return POSTURE_STANDING, False
    player.life_anchor = profile_id or obj.id
    return anchor.posture, anchor.allows_sleep


def peer_posture_line(peer: Player, locale: str) -> str:
    if peer.posture == POSTURE_STANDING:
        return peer.name
    return t(locale, "life.peer_line", name=peer.name, posture=posture_label(peer.posture, locale))


def format_self_life(player: Player, locale: str) -> list[str]:
    lines = [
        t(locale, "life.self_header", name=player.name),
        t(
            locale,
            "life.self_vitals",
            hp=f"{player.hp}/{player.max_hp}",
            fatigue=str(player.fatigue),
        ),
        t(
            locale,
            "life.self_posture",
            posture=posture_label(player.posture, locale),
        ),
    ]
    if player.life_anchor:
        lines.append(t(locale, "life.self_anchor", anchor=player.life_anchor))
    return lines