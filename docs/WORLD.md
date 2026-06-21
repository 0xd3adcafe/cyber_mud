# World Setting — Night City

> **中文：** [WORLD.zh.md](WORLD.zh.md)

> English-primary documentation. See [LOCALIZATION.md](LOCALIZATION.md). Play in Chinese via `lang zh` and localized world fields.

> Night City lore and `data/` world definitions for **cyber_mud**.
> Style pays homage to **Blade Runner** and **Cyberpunk 2077**; this is original MUD narrative, not officially licensed storyline.

## Table of Contents

- [In One Sentence](#in-one-sentence)
- [Era & Atmosphere](#era--atmosphere)
- [Night City Geography](#night-city-geography)
- [Story Core Areas](#story-core-areas)
- [New Player Training Ground](#new-player-training-ground)
- [Factions & Allegiances](#factions--allegiances)
- [Characters & Augmentation](#characters--augmentation)
- [Night City & NETRUN](#night-city--netrun)
- [Weather & Time](#weather--time)
- [Society & Economy](#society--economy)
- [Gameplay Anchors](#gameplay-anchors)
- [World Scale & Data](#world-scale--data)
- [Reskinning the World for a New Theme](#reskinning-the-world-for-a-new-theme)

## In One Sentence

Players jack in through a **neural link** to neon-drenched **Night City**, surviving among corporations, gangs, and the black market—rewriting their fate with cyberware, firearms, and netrunner protocols.

## Era & Atmosphere

| Element | Setting |
|------|------|
| Tone | Cyberpunk: high-density urban sprawl, neon ads, pervasive surveillance |
| Visual reference | Rain-slick reflections, smoke, and holographic billboards (Blade Runner vibe) |
| Social reference | Megacorp monopolies, street gangs, widespread cyberware, RAM and the cost of humanity (CP2077 vibe) |
| Player identity | First connection is an anonymous **traveler**; after registration, an independent **edgerunner** in Night City |
| Interface metaphor | Client banner / MOTD is “establishing neural link”; disconnect is “neural link severed” |

The world is not a static backdrop: server **tick** advances time-of-day and weather; NPCs move, idle, and fight; player actions (factions, hacking, combat) change personal state and reputation.

## Night City Geography

The world is organized on a **grid**; the `map` command gives a bird’s-eye view of explored areas. Procedural generation divides the city into **8 districts**, each with safety level and atmosphere that drive NPC patrols, weather, and `look` descriptions.

| District | Atmosphere |
|------|----------|
| **Watson** | Chaotic streets, night markets, clinics, and underground deals; one starting point for outward exploration |
| **Kabuki** | Neon entertainment, bazaars, intel, and gray-market services |
| **Corpo** | Corporate towers, security, heavy surveillance; strong Arasaka / Militech influence |
| **Tyrell** | High-rises, labs, elites, and forbidden tech (homage to Blade Runner corporate aesthetics) |
| **Little China** | Chinatown alleys, temples, street stalls, and gang turf |
| **Docks** | Containers, smuggling, acid rain and fog; black market and frequent combat |
| **Combat Zone** | High hostility, gunfire and gang wars; main battlefield for combat and scavenging |
| **Undercity** | Sewers, ruins, data crypts; puzzle and hacking entry points |

Room ID convention includes a district prefix (e.g. `watson_03_06`); the `district` field is used by tick / weather / NPC AI.

## Story Core Areas

On world regeneration, a set of main-story anchors is **deliberately preserved** as hubs for puzzles, hacking, and faction play:

| Room ID | Narrative role |
|---------|----------|
| `square` | **Neon Plaza** — public hub where the city meets and intel circulates |
| `alley` | Narrow alleys, ambushes, and black-market leads |
| `shrine` | Shrine / ritual space; humanity and faith contrasted with technology |
| `crypt` | Underground crypt; danger and secrets |
| `data_vault` | Data vault; corporate secrets and hacking targets |

Common associated NPCs / objects (also referenced in tests and tutorials):

- NPCs: `guard`, `priest`, `rat`, `terminal`; street **info broker**
- Items: `lantern`, `rusty_key`, `glowstick`, etc.

Example player path: `take glowstick` → `talk info broker` → `pledge arasaka` → `hack core terminal` (actual room names per `data/`).

## New Player Training Ground

The `recall` command defaults to **`tutorial`** — the new-player training ground (a safe zone isolated from public Night City).

The training ground has **three zones**, each teaching core gameplay:

| Zone | Teaching focus |
|------|----------|
| **Instructor zone** | Movement, `look`, items, basic social |
| **Combat zone** | `attack`, `defend`, `flee`, real-time combat and cooldowns |
| **Netrunner zone** | `net` / NETRUN, `quickhack`, RAM and protocols |

`help tutorial` auto-generates onboarding from world and commands; after training, players enter public areas such as `square`.

## Factions & Allegiances

Players swear allegiance to factions via `pledge`; the PDA shows current **faction** and **reputation**.

| Faction ID | Direction |
|---------|----------|
| `arasaka` | **Arasaka** — megacorp security, surveillance, high-end tech, and cold order |
| `maelstrom` | **Maelstrom** — fanatical cyberware, street violence, machine worship |
| `militech` | **Militech** — mercenaries, firepower, war economy |
| `tyrell` | **Tyrell** — gene / cyberware experiments, elitism (Blade Runner homage) |

Factions affect dialogue, quest hints, hostility in some areas, and shop attitudes (see `data/` and `commands/pledge.py`). Unpledged players are independent **edgerunners**, surviving on contacts and the black market.

## Characters & Augmentation

Character stats use **CP2077-style** five attributes and netrunner resources, readable in PDA / combat / NETRUN:

| Category | Field | Narrative meaning |
|------|------|----------|
| Survival | `hp`, `gold` | Physical damage and street currency |
| Five stats | Body, Reflex, Technical, Cool, Intelligence | Melee, dodge, tech, composure, netrunner intellect |
| Netrunner | `ram` / `max_ram`, `skills` (protocols) | Quickhack and combat hack quota |
| Humanity | `humanity` | Cost of cyberware installs and augmentation |
| Reputation | `reputation` | Credit and intimidation in Night City |
| Status | `status_effects` | Bleeding, poison, cyberware overheat, etc. (extensible) |

**Cyberware (implants)**: `install` slots corporate / black-market implants into cyber slots, changing stats and combat bonuses.  
**Gear**: firearms, armor, weapon mods (`mod`) — street and corporate armament made tangible.  
**Skill protocols**: `learn` grants combat and hack abilities such as `quickhack`.

## Night City & NETRUN

The game has **two layers of experience**, narratively “body on the street, mind diving the net”:

### Night City (physical layer)

- Default mode: Textual client **Night City theme**
- Explore, talk, gunfights, loot, factions
- Prompt and status bar show room, HP, time, weather, etc.

### NETRUN (hack layer)

- `net` / `netrun` enters a **Hacknet-style grid shell**
- Separate **NETRUN theme**, prompt (e.g. `ghost@netrun-kali`), command history and completion
- Tied to in-world `hack`, `probe`, `terminal`, and similar objects
- Client constraint: in NETRUN mode you cannot run normal MUD commands directly (use `exit` to return to Night City)

Layer switching is core to the setting: **one character, two interfaces, two kinds of risk**.

## Weather & Time

| System | Behavior |
|------|------|
| **World clock** | Day / night, time bands (dawn / noon / dusk / night…); query with `time`; status bar `@meta time` |
| **District weather** | Acid rain, fog, smog, neon glare, dry heat, etc.; changes with tick |
| **Effects** | `look` text and atmosphere; extensible vision, movement, combat / NETRUN modifiers |

Night City never sleeps: time bands shift NPC routines (shops, patrols); weather shifts the street narrative tone.

## Society & Economy

- **Corporations**: control data, cyberware, and security; Corpo / Tyrell high districts are heavily monitored
- **Gangs**: turf wars in Combat Zone and Undercity; Maelstrom embodies cyberware fanaticism
- **Black market**: intel, weapons, banned protocols in Kabuki and Docks; `appraise` for pricing, `give` for trade
- **Intel**: info brokers, `scan` / `search` to explore the environment and hidden interactions
- **Multiplayer**: players see each other enter and leave (broadcast); `look` in the same room reveals NPC / player activity

Money (`gold`) is street survival, not corporate credits; megacorp resources come indirectly through factions, hacking, and quests.

## Gameplay Anchors

Mapping setting concepts to concrete commands:

| Setting concept | In-game expression |
|------------|----------|
| Personal terminal | `pda` / `status` (F2 sidebar) |
| Street gear | `equip`, `equipment` (F5) |
| Cyberware | `install`, `mod` |
| Gunfights | `attack`, `defend`, `flee`, real-time encounter |
| Quickhacks | `quickhack` (spends RAM) |
| Net dive | `net`, `hack`, `probe` |
| Faction pledge | `pledge arasaka`, etc. |
| Return to training | `recall` → `tutorial` |
| Explore map | `map` (F4), `go`, `look` |

## World Scale & Data

**cyber_mud** procedurally generates much of the world via `tools/generate_world.py` (see **[WORLD_TOOLS.md](WORLD_TOOLS.md)** for the full CLI pipeline), targeting roughly:

| Type | Count (approx.) |
|------|------------|
| Rooms | 200 |
| Items | 45 |
| NPCs | 109 |

Static definitions live in `data/world.yaml` (and items / npcs / skills / implants, etc.); dynamic state in `world_state.json` (ground items, clock, weather, combat, etc.). Copy keys in `data/locale/zh.yaml`, `en.yaml`.

**Start location**: new connections land per `world.start_room` (public area or tutorial entry — per data).

## Reskinning the World for a New Theme

If you reskin **cyber_mud** with a new theme, only these layers need edits; program architecture can stay:

1. **District names and atmosphere** — `generate_world.py` or hand-written `data/`
2. **Faction table** — `factions` and `pledge` copy
3. **Locale** — MOTD, room descriptions, NPC dialogue
4. **Tutorial three-zone theme** — `tutorial` rooms and `help tutorial`
5. **NETRUN skin** — theme colors and prompt; mechanics can remain

Keep the skeleton of “physical exploration + hack layer + PDA + factions + tick world” for lowest reskin cost and fullest experience.

---

Related docs: [IMPLEMENTATION.md](IMPLEMENTATION.md) (system implementation), [PHASES.md](PHASES.md) (feature phases), [BOOTSTRAP.md](BOOTSTRAP.md) (start from zero).