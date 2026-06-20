> **中文：** [PHASES.zh.md](PHASES.zh.md)

# Phased Delivery Checklist

Mirrors the original **mud** project development history for **cyber_mud** scheduling and acceptance. After each phase, run `pytest` and commit one major milestone.

## Contents

- [Phase 0: MVP](#phase-0-mvp)
- [Phase A: Time, Tick, Attributes](#phase-a-time-tick-attributes)
- [Phase B: NPCs, Weather](#phase-b-npcs-weather)
- [Phase C: Real-time Combat](#phase-c-real-time-combat)
- [Phase D: Bulk Actions & UI Polish](#phase-d-bulk-actions--ui-polish)
- [Phase E: Maintenance & UX](#phase-e-maintenance--ux)
- [Backlog](#backlog)

## Phase 0: MVP

| # | Item | Acceptance |
|---|------|------------|
| 0.1 | TCP server + line protocol | `nc` connects, receives MOTD |
| 0.2 | World load + look/go | Move across 3+ rooms |
| 0.3 | Login/register + save | Reconnect keeps progress |
| 0.4 | take/drop/inventory | Pick up and drop items |
| 0.5 | Textual client main log + status bar | `./run.sh --client` playable |
| 0.6 | help command | Lists available commands |

## Phase A: Time, Tick, Attributes

| # | Item | Key files | Acceptance |
|---|------|-----------|------------|
| A.1 | World clock | `world/clock.py`, `data/time.yaml` | `time` command, meta `time`/`period` |
| A.2 | Server tick loop | `world/tick.py`, `server/game.py` | Clock advances with real time |
| A.3 | CP2077 five stats + humanity/street cred | `entities/player.py` | `pda` shows full vitals |
| A.4 | RAM / cyberware basics | `commands/install.py`, cyber helpers | Installing cyberware affects stats |

**Original project commit reference:** `52aeccc` (batch delivery including A/B/C)

## Phase B: NPCs, Weather

| # | Item | Key files | Acceptance |
|---|------|-----------|------------|
| B.1 | Regional weather | `world/weather.py` | Weather visible in `look` or status bar |
| B.2 | NPC tick movement | `world/tick.py`, NPC data | NPCs change rooms |
| B.3 | Enter/leave awareness | broadcast / `look` signals | Same-room players see NPC enter/leave |
| B.4 | NPC idle actions | tick + throttling | Atmosphere without spam |

## Phase C: Real-time Combat

| # | Item | Key files | Acceptance |
|---|------|-----------|------------|
| C.1 | Encounter state | `combat/encounter.py` | `in_combat` set after combat starts |
| C.2 | Player commands | `attack`, `defend`, `flee`, `quickhack` | Commands work in combat |
| C.3 | Tick progression | `process_tick` | NPCs counter-attack on CD |
| C.4 | Client combat UI | `hint_bar`, meta `combat_*` | Status bar / hint shows combat state |

## Phase D: Bulk Actions & UI Polish

| # | Item | Acceptance |
|---|------|------------|
| D.1 | take/drop/equip/unequip all | `全部`, `*` work |
| D.2 | F2–F5 sidebar | pda/help/map/equipment |
| D.3 | `@ui` JSON sidebar | Structured sections |
| D.4 | Prompt token expansion | `%` tokens and client `/prompt` |
| D.5 | scan + search merge | Consistent exploration UX |
| D.6 | give, appraise | Trade and appraisal |
| D.7 | look output fix | Room in main log (not sidebar, no JSON leak) |

**Original project commit reference:** `3cf9466`, `7623666`

## Phase E: Maintenance & UX

| # | Item | Acceptance | Status |
|---|------|------------|--------|
| E.1 | Client auto-reconnect | Restore after disconnect, resend auth | ✅ |
| E.2 | `./run.sh --dev` hot reload | Code/data changes reload | ✅ |
| E.3 | Sidebar equipment auto-refresh | F2/F5 update immediately after equip | ✅ |
| E.4 | Split EN/ZH docs + README ASCII banner | Consistent `docs/` format, TOC | ✅ (partial) |

**Original project commit reference:** `34d5525` (sidebar refresh)

## Completed (formerly Backlog)

| Item | Acceptance |
|------|------------|
| `tools/generate_world.py` | `python -m tools.generate_world <district> <rows> <cols>` outputs room YAML |
| `admin.sh delete-save <name>` | Deletes `data/saves/<name>.json` |
| Extended prompt tokens (`%w` `%g` `%p` `%f` `%m`) and `prompt template` | `prompt show` lists tokens; `prompt template street` applies CP2077 template |
| Client NETRUN mode | When `net_shell=1` meta blocks normal commands; `/exit` sends `exit` |
| NETRUN server-side | `net`/`netrun` enter net layer; `hack`/`probe`/`exit` |
| `pledge`/`recall`/`talk`/`say`/`learn`/`mod` | Factions, quests, skills, weapon mods |
| NPC aggro chase on flee | `aggro` NPCs chase on failed flee, re-engage in same room |
| Weather affects combat/movement | `world/modifiers.py` adjusts damage, flee, movement |
| Passive skills & cyberware triggers | `combat/passives.py` (cyber arm, breach_protocol) |
| Shop hours, NPC schedules | `data/shops.yaml`, `data/schedule.yaml`, `world/schedule.py` |
| Client login UI | Half-height random ASCII, login/register form, masked password |
| Client themes | 7 tribute styles, `/theme`, `~/.config/cyber_mud/settings.json`, login dropdown |
| Client procedural login ASCII | 12 scenes (skyline, matrix rain, Tron grid, etc.), theme-weighted, random each login |
| Client main UI modernization | Grok CLI-style scrollback + prompt dock, `client/tui_styles.py` |
| Client login/game layout fixes | Visible input, art height, `VerticalScroll`, RichLog doesn't steal focus |
| Client sidebar fixes | `VerticalScroll`, `room_id` triggers map refresh, prefer `@ui` JSON (avoid PDA/map dupes) |
| Item/NPC English suffix | `look`/`scan`/`inventory` show `中文名 (EnglishName)` for command entry |
| Tab autocomplete | `shared/completion.py`, `MudSuggester`, `@meta complete_*`, Tab accepts suggestion |
| Hotkey bar | `#hotkey_bar` always shows Tab/F2–F6/`/reconnect`/Ctrl+C |
| Animated output prefix | `client/output_prefix.py`, Braille spinner (⠋⠙⠹…), colored by MOTD/SYS/ERR |
| Client reconnection | Disconnect exponential backoff (max 5), `/reconnect` manual, resend auth on restore, `client/reconnect.py` |
| Server code hot reload | `server/code_reload.py`; `--dev` watches `commands/` etc. `.py` + `data/*.yaml`, broadcasts SYS and updates meta |
| Client spinner in-flight indicator | Only pending command line (echo) spins; after response `❯`; rest static `›` |
| Client status animation indicators | `client/status_indicators.py`; combat ⚔, quest ▸, low HP ♥, NETRUN ⎈ spinning while active |
| Combat CD second countdown | `combat_cd` meta in seconds, `client/cd_display.py`; status bar `P:45s N:30s` and log cooldown lines count down each second |
| NPC leaves room ends combat | `combat/encounter.py` `npc_in_player_room`, `combat/actions.py` `resolve_npc_departed`; patrol/schedule moving enemy ends encounter on tick or command |
| Tab completion fix | `client/completion.py` `MudPrompt` intercepts Tab (avoid Textual `focus_next`), `client/app.py` `_apply_prompt_completion` sync fallback |
| Combat pacing speedup | `COMBAT_TICK_SECONDS=3` separate `combat_tick_loop`; player CD 3s, NPC CD 6s (no longer tied to 30s world tick) |
| Performance optimization | Combat CD tick silent (no meta/save push); combat events only send `combat_meta`; client spinner 0.2s; combat loop sleeps 30s when no encounter |
| Sidebar stack multi-panel | `sidebar_stack`/`sidebar_panels`; F2–F5 stack PDA+map etc.; same key again closes panel |
| Startup status/load timing | `shared/startup.py` `StartupReport`; server terminal summary + client login hint; SYS push server ready time after connect |
| Client input history | `client/history.py` `CommandHistory`; `MudPrompt` ↑↓/Ctrl+P/N browse, Esc restore draft, editable before send; `~/.config/cyber_mud/command_history.json` |
| Client saved credentials/PIN | `client/credentials.py` PBKDF2 + AES-GCM encryption; login PIN quick unlock, remember + set PIN, F7 clear; `~/.config/cyber_mud/credentials.json` (0600); fix cred write when login success text precedes auth meta |
| look target inspection | `look <item|NPC|equip slot|equipment>` shows description, location, stats and combat HP; Tab completion `complete_equipped` |
| quit logout to login screen | `quit` logs out (keep connection, no reconnect); client `auth=0` returns to login UI |
| Sidebar stack focus fix | Sidebar doesn't steal focus, click returns to prompt; panel refresh serialized to avoid PDA+map parallel hang |
| Client connection status bar | `#link_status_bar` shows connected/waiting/latency; log incremental append, spinner no longer full redraw every 0.2s |
| NPC corpses & looting | Knockout leaves corpse, `take <item> from <corpse>`, `look`/`scan` display; tick decay drops on ground; `world/corpses.py`, `entities/corpse.py`, `tests/test_corpses.py` |
| Corpse English suffix | `corpse_label` shows `(Street Thug)`/`(corpse)` for commands; `tests/test_corpses.py` |
| Tutorial zone expansion | `data/world.yaml` training ground 9 rooms, 10 NPCs (incl. `patrol_dummy`); briefing room/canteen/obstacle course/sim clinic; `trainee_ration`/`training_smartgun`; `data/interactables.yaml` 4 interactables; `data/shops.yaml` tutorial_supply; locale `talk.*`; `tests/test_tutorial_zone.py` |
| Shops & trade | `shop`/`buy`/`sell`, `data/shops.yaml`, `world/trade.py`; register ${STARTING_GOLD}; `tests/test_trade.py` |
| Environment output coloring | `client/env_format.py` room/exits/items/NPC colors; `tests/test_env_format.py` |
| Environment colors follow theme | `client/themes.py` `EnvPalette`/`env_palette_for_theme`; `/theme` switch redraws log |
| Exit display unified | `format_room_exits` direction Chinese + `(English)` only; description removes duplicate exit lines; `tests/test_room_exits.py` |
| Consumables system | `use`/`eat`/`drink`; food/drink/med restore HP/RAM; `world/consumables.py`; `tests/test_consumables.py` |
| defend equipment descriptions | `combat/defend_style.py` switches combat and help text by armor/helmet/weapon |
| NETRUN command passthrough | `prepare_netrun_outbound` normalizes `/probe`; `player_meta` syncs `net_shell=0`; `tests/test_net_meta_sync.py` |
| Sidebar F6 collapse fix | F6 clears stack/cancels load; `ui_panel_end` no longer force reopens; `#hotkey_bar` style stronger visibility |
| Player death corpse & respawn | Defeat leaves corpse, inventory+equipment lootable; auto teleport `respawn_room` (ripperdoc) full HP; `tests/test_player_death.py` |
| Guns & melee combat | `weapon_type` (gun/blade/blunt); `shoot`/`slash`/`bash`/`punch`/`backstab`; `combat/styles.py`, `tests/test_strike.py` |
| Connection status bar visibility | `#link_status_bar` brightened, `連線` prefix, refresh after login; `tests/test_client_app.py` |
| Hotkey bar visibility | `#top_dock`/`#bottom_dock` dock stack; chrome/hotkey `min-height:1`; F keys non-blocking fetch; typing `map`/`pda` auto-opens sidebar; loading F2 again cancels; cases in [`CLIENT_UI_DEBUG.md`](CLIENT_UI_DEBUG.md) |
| Info bar visibility | `#info_bar` `min-height:1`; remove `max-height:1` (Textual `size.height=0` blank in terminal); `tests/test_client_app.py` asserts `info.size.height` |
| Map sidebar performance | Defer `_render_sidebar` until `ui_panel_end`; coalesce meta status refresh; `map` sends `@ui` only (no duplicate `@panel` lines); `tests/test_client_app.py` `test_panel_stream_defers_sidebar_render_until_end` |
| NPC worn equipment | `entities/npc.py` `equipment`; `look` shows worn gear; on knockout goes to corpse with `loot`; `tests/test_npc_equipment.py` |
| Natural HP regen | `world/vitals.py` regen by `body`/`cool`/time period tick; non-combat pushes meta+message; `tests/test_vitals.py` |
| NPC respawn | `world/npc_respawn.py` knockout schedule, tick revive broadcast enter room; `respawn_minutes`/`tier: boss` (default 10 min, boss 60 min); `tests/test_npc_respawn.py` |
| Command repeat | `shared/repeat.py` `10 punch`/`punch.10`; interval `REPEAT_INTERVAL_SECONDS` (0.5s); `tests/test_repeat.py` |
| Server heartbeat | `server/heartbeat.py` terminal single-line periodic refresh tick/connections/combat etc.; dev reload logs; `tests/test_heartbeat.py` |
| CP2077 equipment slots & weapon types | `shared/equipment.py` seven slots (weapon/head/inner_torso/outer_torso/legs/feet/cyber); CP2077 ranged weapon types + power/tech/smart/melee; `armor` save migration; `tests/test_equip.py` |
| NETRUN English suffix | `net_node_label_with_id`; `net`/`probe`/`hack`/`status` nodes and ground items show `(English)`; `hack` Tab completion node id; `tests/test_net.py` |
| NETRUN environment/NPC interaction | `look`/`scan`/`talk`/`say` allowed in NETRUN; `look`/`scan` show nodes; client sync passthrough; `tests/test_net.py` |
| Weapon hold modes | `weapon_primary`/`weapon_secondary`; `weapon_mode` primary/secondary/two-hand/dual-wield; `training_carbine`; `tests/test_equip.py` |
| Level/skills/talents | `world/progression.py` XP level-up, attribute/talent points; `stats`/`talents`/`improve`/`learn` level gates; `data/talents.yaml`; knockout NPC/hack success grants XP; `tests/test_progression.py` |
| Street cred & gigs | `street_cred`; `gigs` Fixer job board; `world/quests.py` gig objectives/turn-in/rewards; `broker_rumor` full flow; `tests/test_gigs.py` |
| CP2077 quickhacks | `data/quickhacks.yaml` overheat/short circuit/optical reboot/synapse burn; `quickhack <name>`; status effects burn/short/blind; `tests/test_quickhacks.py` |
| Cyberware psychosis | `world/cyberpsychosis.py` humanity ≤25 outputs -15% |
| CP2077 cyberware slots | Nine slots `cyberware`/`chrome`/`uninstall`; `data/implants.yaml` expanded; ripperdoc only; `tests/test_cyberware.py` |
| Housing & stash | `rent`/`home`/`stash`; `watson_flat`; `data/housing.yaml`; `tests/test_housing_transport.py` |
| Transit & vehicles | `transit` NCART; `vehicles buy`/`drive`; `data/transit.yaml`/`vehicles.yaml` |
| Tab completion multi-candidate cycle | `shared/completion.py` `complete_input_cycle`; client `_completion_cycle_index`; `tests/test_backlog_features.py` |
| Environment interactables | `interact`; `data/interactables.yaml`; `world/interactables.py`; integrated `look`/`scan`; `tests/test_backlog_features.py` |
| Vertical movement | `go up`/`go down`; `u`/`d` aliases; `square_rooftop`/`undercity`; locale `direction.up/down` |
| Extended prompt tokens | `%l` `%c` `%v` `%x`; templates `ncpd`/`runner`; `shared/prompt_tokens.py` |
| NPC quest multi-stage | `world/quests.py` `stages`; `dock_watch` gig; `tests/test_backlog_features.py` |
| Weather/time-of-day balance | `world/modifiers.py` period modifiers damage/flee/movement; `tests/test_modifiers.py` updated |
| Passive skill tree & cyberware chains | `data/passive_chains.yaml`; `combat/passives.py` `_active_chains`; XP bonus |
| NCPD wanted | `world/wanted.py`; knockout NPC increases; tick decay; `wanted` meta |
| Multi-vehicle garage | `world/vehicles_player.py`; `vehicles buy/select`; `vehicles[]` save |
| Craft/disassemble | `craft`/`disassemble`; `data/recipes.yaml`; `world/craft.py` |
| Braindance | `braindance`/`bd`; `data/braindances.yaml`; `world/braindance.py`; booth interactable |
| NPC faction motivation AI | `faction`/`motivation`; `data/npc_ai.yaml`; `world/npc_ai.py` same-room fight/social/hunt; `tests/test_npc_ai.py` |
| Login banner MOTD dynamic display | `client/login_motd.py`; `motd.tips` locale; `#login_title` rotating tips+spinner; MOTD no longer overwrites `#login_status`; `tests/test_login_motd.py` |
| Full prompt (client live preview) | `client/prompt_preview.py`; `#prompt_preview` expands tokens on input; `/prompt template`/`show`/`reset`; meta `prompt_template`/`xp`; `tests/test_prompt_preview.py` |
| NPC quest authoring tool | `world/quest_author.py`; `tools/quest_author.py`; `./admin.sh quests list/show/validate/npc/scaffold`; `tests/test_quest_author.py` |
| Full quest system | `world/quests.py` `accept`/`abandon`/`requires_quest`/`reward_items`; objectives `defeat_npc`/`have_item`; `gigs accept`/`journal`; `alley_clearance`; `tests/test_quest_system.py` |
| Help log dropdown | `client/help_overlay.py`; `#help_dropdown` overlays `#scrollback_wrap`; F3/`help`/Esc toggle; no longer sidebar stack; `tests/test_help_overlay.py` |
| Tutorial zone second expansion | Briefing `rookie_fixer`/canteen `canteen_tech`/range `range_officer`/clinic `clinic_tutor`/obstacle `course_guide`+`patrol_dummy`; interactable job board/locker/scan pillar/demo host; `tests/test_tutorial_zone.py` 10 cases |
| Gigs sidebar tracking | `gigs`/`journal` → `ok_panel`; `commands/gigs_helpers.py`; F7 hotkey; `quest`/`hint` meta auto refresh; `tests/test_gigs.py` |
| Help command categories | `commands/help_cmd.py` `HELP_CATEGORIES`; locale `help.category.*`; overlay category headers; `tests/test_help_cmd.py` |
| Focus tracking block | `client/focus_block.py` above prompt; gig/combat/in-flight; gradient accent+timer; `focus_palette_for_theme`; `tests/test_focus_block.py` |
| Bilingual English default | Default `locale=en`; `lang` command; `server.*`/`client.*` locale; `docs/LOCALIZATION.md`; commit English primary; `tests/test_lang.py` |
| Client chrome locale | `client/ui_format.py` sidebar titles/hotkey bar; `lang` meta refreshes chrome; `client.ui.*` locale; `tests/test_ui_format.py` |
| Prompt placeholder locale | `#prompt` placeholder `client.ui.prompt_placeholder`; `_refresh_prompt_placeholder` |
| Client clear log | `/clear` local command; `AnimatedLogBuffer.clear()`; Tab completion; `tests/test_client_app.py` |
| Split EN/ZH documentation | `*.zh.md` mirrors; English default on GitHub; README ASCII banner |
| English default locale in project rules | `CLAUDE.md` § Project rules (mandatory); `LOCALIZATION.md` § Project rule; README core principle #1 |
| Project licenses | `LICENSE` Apache 2.0 (code); `LICENSE-CONTENT.md` CC BY 4.0 (world copy); README badges; `CONTRIBUTING.md` |
| Player guides (GitHub) | `docs/player/` ASCII-art tutorial, commands, client; EN + `*.zh.md`; README player section |
| Mature / NSFW content M.0–M.7 | `world/mature.py`, `combat/gore.py`, `settings mature`, `flirt`, mature locale/YAML, client 18+ login; `docs/MATURE_CONTENT.md` |
| Kabuki & district expansion (2026-06) | `kabuki_vip`, `kabuki_bazaar`, Little China, Corpo hubs; `velvet_job`; `tests/test_world_districts.py` |
| Client layout test helpers | `tests/client_ui_helpers.py`; stable sidebar/help overlay assertions in `test_client_app.py` |
| Life commands L.1–L.8 (2026-06) | `sit`/`stand`/`lie`/`rest`/`sleep`/`wake`; `world/life.py`, `data/life.yaml`; interactable rest anchors; vitals/RAM regen; wake on move/say/talk/combat; PDA + `%posture`; help category **Life & vitals**; `tests/test_life_commands.py` |
| Life command follow-ups (2026-06) | Activity fatigue gain (`move`/`combat`/`netrun`); district `safety` outdoor sleep gate; rest period/weather multipliers in `world/modifiers.py`; poison blocks sleep; high-fatigue HP regen penalty; `tests/test_life_commands.py`, `tests/test_modifiers.py` |
| World expansion W.4–W.5, W.11 (2026-06) | Story anchors `crypt`, `data_vault`; NPCs `guard`/`priest`/`rat`; `plaza_terminal`/`vault_terminal`; `hack_core` quest + `hack_net` objective; net nodes `crypt_node`/`vault_core`; `tests/test_story_anchors.py`, `tests/test_net_story.py` |
| World expansion W.1, W.2, W.14 scale (2026-06) | `tools/merge_world_grid.py`; 8 district grids → **263 rooms**; hubs `tyrell_plaza`, `combat_zone_gate`; hub↔grid links; `tests/test_world_scale.py`; `admin.sh validate` counts |
| World expansion W.3, W.6, W.7 (2026-06) | `data/districts.yaml` safety/atmosphere; `look` flavor; patrol/aggro/weather bias; `help tutorial`; `tyrell_intel` quest + faction shop/talk/entry gates; `tests/test_districts.py`, `tests/test_help_tutorial.py`, `tests/test_factions.py` |
| World expansion W.8–W.10 (2026-06) | `data/schedule.yaml` shop hours + period patrol multipliers; NPC schedules (`bazaar_fixer`, `dock_smuggler`, `corp_guard`); `docks_gray` shop + `gray_market` quest (`give_npc`); corp/street `appraise`; `give <item> <npc>`; `presence.enter`/`leave` on `go`; sender-excluded `say`/`give` broadcasts; `tests/test_schedule.py`, `tests/test_black_market.py`, `tests/test_multiplayer.py` |
| World expansion W.12–W.13 (2026-06) | `poison` tick + `antidote` consumable; player `overheat` debuff (quickhack backlash); `world/reactions.py` reputation shifts (pledge/hack/combat); broker rep/wanted talk; tick `ambient_tick` + `trauma_tick` broadcast; `tests/test_status_effects.py`, `tests/test_world_reactions.py` |
| World expansion W.14 (2026-06) | `tools/expand_world_population.py` + `data/world_population.yaml` overlay; **109 NPCs**, **45 items** on 263-room grid; loader merge; `tests/test_world_scale.py` |
| Content depth D.1–D.6 (2026-06) | Archetype `talk.*` keys + regen population; quest WARN fixes + `hub_briefing`; hub NPCs (`tyrell_liaison`, `zone_warden`, etc.); grid loot craft/disassemble + shop stock; 8 district grid net nodes + interactables; `tests/test_content_depth.py`; [WORLD_TOOLS.md](WORLD_TOOLS.md) |
| Client bare `/` input fix | `is_local_command("/")` no IndexError; show `client.local_command.usage`; unknown `/foo` stays client-side; `tests/test_client_meta.py`, `tests/test_client_app.py` |

## Multi-session development (mandatory)

When resuming work in a **new chat or parallel session**, sync with the repo **before** editing code:

```bash
git fetch origin 2>/dev/null || true
git status -sb
git log --oneline -15
git log origin/master..HEAD --oneline 2>/dev/null   # unpushed commits
pytest tests/ -q --tb=no || true
./admin.sh validate 2>/dev/null | tail -3 || true
```

Then read this file **Backlog** and [`CLAUDE.md`](../CLAUDE.md) recent-completions table. Do not re-implement items already in `git log` or “Completed (formerly Backlog)”.

**Before commit:** one major item per commit; update Backlog; English commit subject (`feat: …`).

## Backlog maintenance convention

**After each fix or feature change**, update this file before merge/commit:

1. **Completed** → add to the “Completed (formerly Backlog)” table (item + acceptance/modules)
2. **Pending/follow-up** → add to the “Backlog” list below; when done, move to completed and remove
3. **Summary** → sync the Backlog section in [`CLAUDE.md`](../CLAUDE.md) (recent completions table)

Agents and collaborators: if you change game or client behavior before delivery, you **must** update the backlog—do not change code without recording it.

## Backlog

Not yet implemented or only partially implemented.

### Environment

- pyenv native Python build (environment setup, not a game feature)

### Mature / NSFW content (18+)

**Policy:** Original homage-style cyberpunk fiction; not official IP. All mature content is **opt-in** (`content_rating` / `mature_enabled` on player save), gated at login and command layer, with copy in **separate locale files** (`data/locale/mature_en.yaml`, `mature_zh.yaml`)—never mixed into default help/MOTD.

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~M.0~~ | ~~Content rating & opt-in~~ | ✅ `Player.content_rating`; `settings mature on\|off`; register `mature`; `world/mature.py`; `tests/test_content_rating.py` |
| ~~M.1~~ | ~~Gore & bloody combat~~ | ✅ `combat/gore.py`; kill/crit/corpse lines; Focus `gore` tint; `tests/test_gore.py` |
| ~~M.2~~ | ~~Injury & trauma flavor~~ | ✅ `world/trauma.py`; bleed status; ripperdoc treat on clinic entry; tick damage |
| ~~M.3~~ | ~~Adult venues & NPCs~~ | ✅ `kabuki_lounge`, `bd_den`, `kabuki_host`; `tags: [mature]`; mature `talk` |
| ~~M.4~~ | ~~Romance & intimacy~~ | ✅ `data/romance.yaml`; `flirt` / `spend_time`; `romance_flags` on save |
| ~~M.5~~ | ~~Mature braindance & gigs~~ | ✅ `braindances_mature.yaml`, `quests_mature.yaml`; teen `gigs`/`bd` filter |
| ~~M.6~~ | ~~Client warnings & UI~~ | ✅ Login 18+ checkbox; help hides mature category; Focus gore style |
| ~~M.7~~ | ~~Authoring & admin~~ | ✅ `mature_validate.py`; `docs/MATURE_CONTENT.md`; CONTRIBUTING note |

**Suggested order:** M.0 → M.1 → M.3 → M.4 → M.5 → M.6 → M.2 → M.7. **All phases shipped (2026-06).**

### World expansion ([WORLD.md](WORLD.md))

**Baseline (2026-06):** **263 rooms**, **109 NPCs**, **45 items** — WORLD.md scale targets met; district `safety`/`atmosphere`; `help tutorial`; faction depth; schedules + gray market; poison/overheat + live world reactions (`world/reactions.py`). **World expansion W.1–W.14 shipped** — authored follow-up tracked under **Content depth** below.

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| W.1 | Procedural district grids | Merge `python -m tools.generate_world <district> <rows> <cols>` YAML into `data/world.yaml`; district-prefixed room IDs (e.g. `watson_03_06`); every public room has `district` + optional `grid_x`/`grid_y`; hub rooms connect to grid edges; `tests/test_world_scale.py` |
| W.2 | Eight-district room clusters | Full clusters for **Tyrell** and **Combat Zone**; expand partial **Watson**, **Kabuki**, **Little China**, **Corpo**, **Docks**, **Undercity** per WORLD geography table; `map` shows explored grid; locale `*_en`/`*_zh` on all new rooms |
| W.3 | District safety & atmosphere | `safety` / `atmosphere` metadata per district drives `look` flavor, NPC patrol density, aggro modifiers, and tick weather bias; `world/npc_ai.py`, `world/modifiers.py`, `world/weather.py` |
| W.4 | Story core rooms | Add **`crypt`** and **`data_vault`** anchors (alongside `square`, `alley`, `shrine`); wire exits from `data_crypt` / Undercity hub graph; onboarding path: `take glowstick` → `talk broker` → `pledge` → `hack` terminal |
| W.5 | Story anchor NPCs & loot | NPCs **`guard`**, **`priest`**, **`rat`** in core areas; in-room **`terminal`** object; ground items **`rusty_key`**, **`glowstick`** per WORLD table; `tests/test_story_anchors.py` |
| W.6 | `help tutorial` onboarding | Auto-generate tutorial text from `tutorial_*` rooms + command registry (`help tutorial`); locale keys; complements existing three-zone training ground; `tests/test_help_tutorial.py` |
| W.7 | Faction gameplay depth | **`pledge tyrell`** quests and talk branches; faction affects **dialogue**, **quest hints**, **area hostility**, **shop buy/sell rates** (`world/trade.py`, `data/shops.yaml`); reputation thresholds; `tests/test_factions.py` |
| ~~W.8~~ | ~~District weather & schedules~~ | ✅ `data/schedule.yaml` all shop hours + period patrol multipliers; NPC schedules (`broker`, `bazaar_fixer`, `dock_smuggler`, `corp_guard`); `patrol_period_multiplier`; `tests/test_schedule.py` |
| ~~W.9~~ | ~~Society & black market~~ | ✅ `docks_gray` shop, `dock_smuggler` NPC, `gray_market` quest (`give_npc`); corp/street `appraise`; `give <item> <npc>`; `tests/test_black_market.py` |
| ~~W.10~~ | ~~Multiplayer presence~~ | ✅ `presence.enter`/`leave` on `go`; sender-excluded `say`/`give` broadcasts; peer `look`; `tests/test_multiplayer.py` |
| W.11 | NETRUN story nodes | `data_vault` / `crypt` net nodes tied to physical rooms; `hack core terminal` quest step; expand `data/net_nodes.yaml`; `tests/test_net_story.py` |
| ~~W.12~~ | ~~Extended status effects~~ | ✅ `poison` tick + `antidote` (`cures_status`); player `overheat` debuff on quickhack (≠ NPC `burn`); combat damage penalty; `tests/test_status_effects.py` |
| ~~W.13~~ | ~~Live world reactions~~ | ✅ `world/reactions.py` rep shifts (pledge/NETRUN hack/combat/quickhack); broker rep/wanted talk; tick `ambient_tick`; `trauma_tick` client broadcast; `tests/test_world_reactions.py` |
| ~~W.14~~ | ~~World scale targets~~ | ✅ **263 rooms**, **109 NPCs**, **45 items**; `tools/expand_world_population.py`; `data/world_population.yaml` loader overlay; `tests/test_world_scale.py` |

**Suggested order:** W.4 → W.5 → W.11 (story anchors) → W.1 → W.2 → W.3 (geography scale) → W.6 → W.7 → W.8 → W.9 → W.10 → W.12 → W.13 → W.14.

### Content depth (post W.14 scale)

**Goal:** After procedural grid scale (W.14), replace template filler with **authored** dialogue, quests, hubs, economy, and district hooks so Night City reads as lived-in—not just counted.

**Baseline (2026-06):** **113 NPCs** (27 hand-authored + 86 procedural overlay). Procedural NPCs use archetype `talk.*` keys (21 archetypes). `./admin.sh quests validate` — 0 warnings. **Content depth D.1–D.6 shipped.**

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~D.1~~ | ~~Grid NPC dialogue~~ | ✅ Archetype `talk.*` in `tools/expand_world_population.py`; regen `data/world_population.yaml`; `data/locale/en.yaml` + `zh.yaml` |
| ~~D.2~~ | ~~Grid NPC quests & quest hygiene~~ | ✅ `talk_npc` turn-in for `gray_market`, `tyrell_intel`, `velvet_job`; `hub_briefing` gig; `./admin.sh quests` 0 WARN |
| ~~D.3~~ | ~~Hand-authored district hubs~~ | ✅ `tyrell_liaison`, `zone_warden`, `plaza_handler`, `gate_herbalist`; hub `look` flavor in `data/world.yaml` |
| ~~D.4~~ | ~~Item lore & economy~~ | ✅ `street_stim`/`gutter_blade` craft; `combat_scrap`/`black_ice_shard` disassemble; `kabuki_bazaar`/`docks_gray` stock |
| ~~D.5~~ | ~~Interactables & NETRUN on grid~~ | ✅ 7 grid interactables; 8 district `*_grid_node` in `data/net_nodes.yaml`; `tests/test_content_depth.py` |
| ~~D.6~~ | ~~Population tool workflow~~ | ✅ [WORLD_TOOLS.md](WORLD_TOOLS.md) / [WORLD_TOOLS.zh.md](WORLD_TOOLS.zh.md) |

**Suggested order:** D.2 → D.1 → D.3 → D.4 → D.5 → D.6. **All phases shipped (2026-06).**

### Life commands (posture, rest & environment)

**Goal:** `sit`, `stand`, `rest`, `sleep`, `wake`, etc. change **body state** (posture, fatigue, HP/RAM recovery) and are **modified by room, weather, time, and interactables**—not cosmetic emotes.

**Hooks (existing):** `world/vitals.py` tick regen; `world/trauma.py` `player_status`; `world/modifiers.py` period/weather; `data/interactables.yaml`; `home` / `rent`; room `tags`.

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~L.1~~ | ~~Posture & fatigue model~~ | ✅ `Player.posture`; `fatigue` 0–100; `world/life.py`; `persistence/save.py` |
| ~~L.2~~ | ~~Core life commands~~ | ✅ `commands/life.py`: `sit`, `stand`, `lie`, `rest`, `sleep`, `wake`; combat/NETRUN/chase blocks; locale `life.*` en/zh |
| ~~L.3~~ | ~~Environment rest rules~~ | ✅ `data/life.yaml`; room `tags` + district `safety` gate `sleep`; period/weather multipliers in `world/modifiers.py` + `world/life.py` |
| ~~L.4~~ | ~~Interactable rest anchors~~ | ✅ `canteen_bench`, `flat_bunk`, `clinic_bed`, `lounge_booth`; `world/interactables.py` |
| ~~L.5~~ | ~~Vitals & status integration~~ | ✅ `world/vitals.py` HP/RAM regen; rest reduces fatigue tick; activity adds fatigue; bleed/poison block sleep; high fatigue slows regen; low `humanity` penalty |
| ~~L.6~~ | ~~Risk & social presence~~ | ✅ peer posture in `look`/`scan`; sleep interrupt tick; wake on `go`/`say`/`talk`/combat |
| ~~L.7~~ | ~~Client & PDA~~ | ✅ meta `posture`/`fatigue`; PDA row; `%posture` prompt token |
| ~~L.8~~ | ~~Tests, help, tutorial~~ | ✅ `tests/test_life_commands.py`; help category **Life & vitals**; canteen bench + instructor line |

**Suggested order:** L.1 → L.2 → L.3 → L.4 → L.5 → L.6 → L.7 → L.8. **All phases shipped (2026-06).**

---

Suggested route: **0 → A → D.2/D.7 (playability) → B → C → remaining D → E**; for a social-exploration MUD, consider B before C.

World setting, districts, and factions: [WORLD.md](WORLD.md). Agent collaboration rules: [CLAUDE.md](../CLAUDE.md).