from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Player:
    name: str = "Traveler"
    room_id: str = "square"
    locale: str = "en"
    named: bool = False
    hp: int = 100
    max_hp: int = 100
    gold: int = 0
    level: int = 1
    xp: int = 0
    attribute_points: int = 0
    perk_points: int = 0
    perks: list[str] = field(default_factory=list)
    body: int = 3
    reflex: int = 3
    tech: int = 3
    cool: int = 3
    intelligence: int = 3
    humanity: int = 100
    reputation: int = 0
    street_cred: int = 0
    faction: str = ""
    ram: int = 4
    max_ram: int = 8
    inventory: list[str] = field(default_factory=list)
    equipment: dict[str, str] = field(default_factory=dict)
    implants: list[str] = field(default_factory=list)
    cyberware: dict[str, str] = field(default_factory=dict)
    home_room_id: str = ""
    home_stash: list[str] = field(default_factory=list)
    vehicle_id: str = ""
    vehicles: list[str] = field(default_factory=list)
    active_vehicle: str = ""
    wanted_level: int = 0
    interact_flags: dict[str, str] = field(default_factory=dict)
    braindance_flags: dict[str, str] = field(default_factory=dict)
    visited_rooms: list[str] = field(default_factory=list)
    prompt_mud: str = ""
    skills: list[str] = field(default_factory=list)
    proficiency_levels: dict[str, int] = field(default_factory=dict)
    proficiency_xp: dict[str, int] = field(default_factory=dict)
    password_hash: str = ""
    auth_failed_attempts: int = 0
    auth_locked_until: float = 0.0
    in_combat: bool = False
    encounter_id: str = ""
    active_quest: str = ""
    quest_flags: dict[str, str] = field(default_factory=dict)
    quest_hint: str = ""
    net_shell: bool = False
    weapon_mods: dict[str, list[str]] = field(default_factory=dict)
    chased_by_npc: str = ""
    content_rating: str = "teen"
    romance_flags: dict[str, str] = field(default_factory=dict)
    player_status: dict[str, int] = field(default_factory=dict)
    posture: str = "standing"
    fatigue: int = 0
    life_anchor: str = ""
    profiled_npcs: list[str] = field(default_factory=list)
    footprint: int = 0
    discovered_net_links: list[str] = field(default_factory=list)