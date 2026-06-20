> **中文：** [WORLD_TOOLS.zh.md](WORLD_TOOLS.zh.md)

# World authoring tools

CLI utilities under `tools/` for procedural district grids, population overlays, and quest scaffolding. Run from the repo root with `PYTHONPATH=.` (handled automatically by `./admin.sh` and `./run.sh`).

## Contents

- [Pipeline overview](#pipeline-overview)
- [Prerequisites](#prerequisites)
- [`generate_world.py`](#generate_worldpy)
- [`merge_world_grid.py`](#merge_world_gridpy)
- [`expand_world_population.py`](#expand_world_populationpy)
- [`quest_author.py`](#quest_authorpy)
- [`admin.sh`](#adminsh)
- [Hand-authored vs generated](#hand-authored-vs-generated)
- [Typical workflows](#typical-workflows)

## Pipeline overview

Night City scale content is built in layers:

```text
data/world.yaml (hand-authored core + hubs)
        │
        ├─► merge_world_grid.py ──► adds 8 district room grids (W.1/W.2)
        │
        ├─► expand_world_population.py ──► data/world_population.yaml (W.14/D.1)
        │         (merged at load by world/loader.py)
        │
        └─► quests.yaml / shops / interactables (hand-authored)
```

| Layer | File | Tool |
|-------|------|------|
| Rooms (grid cells) | `data/world.yaml` `rooms:` | `generate_world.py`, `merge_world_grid.py` |
| NPCs / items (procedural) | `data/world_population.yaml` | `expand_world_population.py` |
| Story / hubs / gigs | `data/world.yaml`, `data/quests.yaml` | hand edit + `quest_author.py` |

## Prerequisites

```bash
./setup.sh          # Python 3.13 venv
export PYTHONPATH=. # or use ./admin.sh / ./run.sh
```

Always validate after regenerating world data:

```bash
./admin.sh validate
```

## `generate_world.py`

Generate a **single rectangular room grid** as YAML (one district at a time).

```bash
python -m tools.generate_world <district> <rows> <cols> [options]
```

| Argument / flag | Description |
|-----------------|-------------|
| `district` | District id stored on each room (e.g. `watson`) |
| `rows`, `cols` | Grid size (≥ 1) |
| `--prefix` | Room id prefix (default: district name) → `watson_3_2` |
| `-o`, `--output` | Write to file instead of stdout |
| `--start-room` | Include `start_room:` key (default: top-left cell) |

**Example** — preview a 4×4 Watson grid:

```bash
python -m tools.generate_world watson 4 4
```

**Example** — save to a scratch file for review:

```bash
python -m tools.generate_world tyrell 6 6 -o /tmp/tyrell_grid.yaml
```

Output rooms include `district`, `grid_x`, `grid_y`, and cardinal `exits`. Locale uses template `name_*` / `description_*` strings; customize in `data/world.yaml` after merge.

## `merge_world_grid.py`

Merge **all eight district grids** into `data/world.yaml` and wire hub↔grid exits (current shipped layout: 263 rooms).

```bash
python -m tools.merge_world_grid [options]
```

| Flag | Description |
|------|-------------|
| `-o`, `--output` | Target world file (default: `data/world.yaml`) |
| `--dry-run` | Print room count delta only; do not write |

**Example:**

```bash
python -m tools.merge_world_grid --dry-run
python -m tools.merge_world_grid
./admin.sh validate
```

Edits district sizes and hub links in `tools/merge_world_grid.py` (`GRID_SPECS`, `HUB_GRID_LINKS`, `EXTRA_HUB_ROOMS`). Existing room ids in `world.yaml` are **not** overwritten—only missing grid cells are added.

**When to run:** expanding or re-linking district grids (W.1/W.2). Rare in day-to-day content work.

## `expand_world_population.py`

Generate the **population overlay** — procedural grid NPCs, district loot items, and ground spawns.

```bash
python -m tools.expand_world_population [options]
```

| Flag | Description |
|------|-------------|
| `--source` | Base world YAML (default: `data/world.yaml`) |
| `-o`, `--output` | Overlay path (default: `data/world_population.yaml`) |
| `--dry-run` | Print npc/item counts only; do not write |

**Example:**

```bash
python -m tools.expand_world_population --dry-run
python -m tools.expand_world_population
./admin.sh validate
```

Stderr reports merge totals, e.g. `npcs: 27 + 86 -> 113`.

**Configure in** `tools/expand_world_population.py`:

- `DISTRICT_NPC_COUNTS` — NPCs per district grid
- `DISTRICT_ARCHETYPES` — archetype rotation per district
- `ARCHETYPE_DEFS` — HP, hostility, `talk_key`, loot, patrol
- `NEW_ITEMS` — procedural item definitions

After changing archetype `talk_key`, add matching `talk.*` keys to `data/locale/en.yaml` and `zh.yaml`.

**When to run:** after grid room changes or archetype/count/talk/loot edits. **Not** needed for hand-authored hub NPCs, quests, or shops in `world.yaml`.

Loader merge: `world/loader.py` reads `POPULATION_PATH` and overlays `npcs`, `items`, and `room_items` onto the base world.

## `quest_author.py`

Validate and scaffold **multi-stage gigs** in `data/quests.yaml` / `data/quests_mature.yaml`.

Invoked via `./admin.sh quests` (forwards to `python -m tools.quest_author`).

```bash
./admin.sh quests list
./admin.sh quests show <quest_id>
./admin.sh quests validate
./admin.sh quests npc <npc_id>
./admin.sh quests scaffold <quest_id> --giver broker --complete broker \
  --stage talk_npc:zone_warden --stage visit_room:tyrell_plaza \
  --stage talk_npc:broker --name-en "Hub Coordinates" --reward-gold 80
```

| Subcommand | Purpose |
|------------|---------|
| `list` | Summary of all quests |
| `show <id>` | Stage outline for one quest |
| `validate` | ERR/WARN for missing NPCs, rooms, `complete_npc` in `talk_npc` stages |
| `npc <id>` | Quest roles for one NPC (giver, stage target, completer) |
| `scaffold` | Print YAML snippet for a new multi-stage quest |

**Stage format:** `objective_type:target`, e.g. `talk_npc:broker`, `visit_room:docks`, `give_npc:broker`, `hack_net:terminal`, `defeat_npc:thug`.

Paste scaffold output into `data/quests.yaml`, then run `./admin.sh quests validate`.

## `admin.sh`

| Command | Purpose |
|---------|---------|
| `./admin.sh validate` | World graph, quests, mature content, then `pytest tests/` |
| `./admin.sh quests …` | Quest authoring CLI (see above) |
| `./admin.sh saves` | List player saves |
| `./admin.sh delete-save <name>` | Delete one save |

`validate` is the acceptance gate before commit.

## Hand-authored vs generated

| Keep in `data/world.yaml` | Keep in overlay / tools |
|---------------------------|-------------------------|
| `broker`, hub NPCs, story anchors | Grid cell NPCs (`watson_thug_0_3`) |
| Hubs (`tyrell_plaza`, `square`, …) | Template grid room prose (optional bulk regen) |
| `data/quests.yaml` gigs | Archetype loot tables |
| Shops, interactables, net story nodes | `gutter_blade`, `combat_scrap`, … procedural items |

**Rule:** If you edit a procedural NPC in `world_population.yaml` by hand, the next regen **overwrites** it. For permanent characters, use `world.yaml` or change the generator.

## Typical workflows

### Add archetype dialogue (D.1)

1. Edit `ARCHETYPE_DEFS` `talk_key` in `tools/expand_world_population.py`
2. Add `talk.<key>` to `data/locale/en.yaml` + `zh.yaml`
3. `python -m tools.expand_world_population`
4. `./admin.sh validate`

### Fix quest warnings (D.2)

1. `./admin.sh quests validate`
2. Add `talk_npc` stage for `complete_npc_id` or adjust stages in `quests.yaml`
3. `./admin.sh quests show <id>` to verify outline

### Expand one district grid (W.1)

1. Adjust `GRID_SPECS` in `tools/merge_world_grid.py` if needed
2. `python -m tools.merge_world_grid`
3. `python -m tools.expand_world_population` (re-seat NPCs on new cells)
4. `./admin.sh validate`

### New multi-stage gig

1. `./admin.sh quests scaffold my_gig --giver broker --complete broker --stage …`
2. Paste into `data/quests.yaml`
3. `./admin.sh quests validate` && `./admin.sh validate`

---

See also: [WORLD.md](WORLD.md) (districts), [PHASES.md](PHASES.md) (W.1–W.14, D.1–D.6), [CONTRIBUTING.md](../CONTRIBUTING.md).