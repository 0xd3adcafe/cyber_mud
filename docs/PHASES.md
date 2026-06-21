> **中文：** [PHASES.zh.md](PHASES.zh.md)

# Phased Delivery Checklist

Phased delivery checklist and acceptance criteria for **cyber_mud**. After each phase, run `pytest` and commit one major milestone.

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

## Phase E: Maintenance & UX

| # | Item | Acceptance | Status |
|---|------|------------|--------|
| E.1 | Client auto-reconnect | Restore after disconnect, resend auth | ✅ |
| E.2 | `./run.sh --dev` hot reload | Code/data changes reload | ✅ |
| E.3 | Sidebar equipment auto-refresh | F2/F5 update immediately after equip | ✅ |
| E.4 | Split EN/ZH docs + README ASCII banner | Consistent `docs/` format, TOC | ✅ |

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
| Target disambiguation TD.1–TD.5 | `shared/target_resolve.py`; `target.*` locale; ordinal/scope/ambiguous lists on look, take/drop/equip/unequip/use/install/mod/sell/stash/give/appraise/disassemble, talk/flirt/taunt/attack, interact/hack, buy/craft/braindance; `tests/test_target_resolve.py` |
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
| CP2077 proficiency skills (2026-06) | `data/proficiencies.yaml`; `world/proficiencies.py` use-based level 1–60 (Body/Reflex/Tech/INT/Cool); combat/net/craft/move XP; damage/quickhack bonuses; `stats` proficiency panel; `tests/test_proficiencies.py` |
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
| Mature / NSFW content M.0–M.17 | `mature_social.py`, combat broadcasts, mature say/presence, romance gifts, `taunt`/`finish`; `docs/MATURE_CONTENT.md` |
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
| Content depth D.7–D.10 (2026-06) | 8 district spotlight NPCs; `district.grid.*` look flavor; 4 district quest chains; full `world.ambient.*`; `tests/test_content_depth.py` |
| Client bare `/` input fix | `is_local_command("/")` no IndexError; show `client.local_command.usage`; unknown `/foo` stays client-side; `tests/test_client_meta.py`, `tests/test_client_app.py` |
| Client log UX CL.1–CL.8 (2026-06) | `log_classifier.py`/`log_styles.py`/`LogPalette`; combat/env/social/progression channels; block separators; `tests/test_log_classifier.py`; `docs/player/CLIENT.md` legend |
| Client log UX CL.9–CL.11 (2026-06) | `/log compact`; `/log hide`/`show` channel toggles; `/log export`; `log_settings.py`; `tests/test_log_settings.py`; settings.json persistence |
| Validate speedup (2026-06) | Cache `load_world`/`default_room_items`/time+weather YAML; `pytest-xdist` in `./admin.sh validate`; `clear_world_cache()` on dev reload; ~6 min → ~50s |
| Security ASVS L1 ASVS.1–5 (2026-06) | PBKDF2 passwords + legacy rehash; unified `invalid_credentials`; save path validation; input bounds; per-connection auth rate limit; save `0600`; `docs/SECURITY.md`; `tests/test_security_auth.py` |
| Tutorial zone T.2–T.7 (2026-06) | `tutorial_debrief`; 3 NPCs; 8 interactables; 3 items; `tutorial_rotation` quest; `tests/test_tutorial_zone.py` 13 cases |
| PDA integrated growth panel (2026-06) | Single `pda` merges vitals, proficiencies, skill list, full talent catalog; `build_pda_ui` sidebar sections; `stats` / `talents` unchanged; `tests/test_pda.py` |
| Sidebar refresh performance (2026-06) | `client/sidebar_refresh.py` debounced fetch (2s) + 15s poll; meta patch for open PDA vitals; coalesced `_render_sidebar`; `tests/test_sidebar_refresh.py` |

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

### Architecture (incremental)

**Goal:** Adopt useful Evennia-style patterns without a full entity migration—YAML-driven gates and deferred tick tasks on the existing `world/tick.py` loop.

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~ARCH.1~~ | ~~Lock simplified (YAML predicates)~~ | ✅ `shared/locks.py`; `commands/lock_helpers.py`; room/item/net node/interactable `locks:` in YAML; `go` / `use` / `hack` / `interact`; `data_vault` + `vault_core` examples; `tests/test_locks.py` |
| ~~ARCH.2~~ | ~~Scheduler thin layer~~ | ✅ `world/scheduler.py`; `tick_count` once/interval + cancel; `world_state.json` restore; implant `side_effect_minutes` on install; `tests/test_scheduler.py` |

**Suggested order:** ARCH.1–2 shipped. **Deferred** (replaces removed `TODO.md` Phase 1.2–1.3 scope).

### Surveillance hacking (Watch Dogs homage)

**Policy:** Original homage to **connected-city surveillance fantasy** (ctOS-style OS, profiler intel, infrastructure hacks)—not Ubisoft IP, characters, or Chicago geography. Night City stays Blade Runner + CP2077 flavored; borrow **systems and tone**, not lore canon.

**Watch Dogs analysis (what to steal):**

| Layer | Watch Dogs (Ubisoft) | Night City today | Gap |
|-------|----------------------|------------------|-----|
| **World** | Smart city run by Blume **ctOS**; traffic, bridges, steam, cameras on one network; **DedSec** vs corps | Districts, corpo tags, `data_vault`, Tyrell surveillance tone | No city-wide OS layer; hacks are node/combat-centric |
| **Profiler** | Scan civilians → job, income, traits, criminal record; unlocks social/combat hacks | `scan` lists room entities; `look <npc>` shows stats | No persistent **intel profile** or trait-gated actions |
| **Hacking** | Context hacks on **connected objects** (blackout, traffic, distract, bridge); smartphone hub | NETRUN `hack`/`probe` on `net_nodes`; combat `quickhack` | Little **room infrastructure** interaction outside NETRUN shell |
| **Economy / gigs** | **Fixers** hand contracts; privacy invasions; convoy takedowns | `gigs`/`journal`, multi-stage quests, street cred | Few objectives tied to **scan-then-act** loops |
| **Heat** | Police notoriety from crimes + failed hacks | `wanted_level` tick decay (NCPD) | No **digital footprint** from surveillance districts |
| **Progression** | Skill tree: hacking / combat / driving | Skills, talents, proficiencies, implants | No hacking branch for **environment control** |

**Goal:** Text MUD expressions of profiler intel + infrastructure hacks + surveillance heat—reusing NETRUN, `scan`, `wanted`, gigs, ARCH.1 locks, ARCH.2 scheduler.

**Client (shipped 2026-06):** `/theme` + login dropdown — `ctos` (City OS surveillance cyan), `dedsec` (hacktivist magenta/teal), `profiler` (intel amber/cyan); `client/themes.py`, `login_art.py` scene bias; `tests/test_themes.py`.

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~WD.1~~ | ~~Profiler data model~~ | ✅ `data/profiler.yaml`; `Player.profiled_npcs`; `scan <npc>`; `world/profiler.py`; `tests/test_profiler.py` |
| ~~WD.2~~ | ~~Infrastructure room tags~~ | ✅ `power_grid`/`traffic`/`surveillance`/`steam` room tags; `world/infrastructure.py`; `look`/`scan` ctOS lines; `tests/test_infrastructure.py` |
| ~~WD.3~~ | ~~Environment hacks (NETRUN)~~ | ✅ `hack blackout`/`jam_signals`/`overload` on tagged rooms; `world/ctos_hacks.py`; RAM + street cred; `tests/test_ctos_hacks.py` |
| ~~WD.4~~ | ~~Digital footprint & surveillance heat~~ | ✅ `Player.footprint`; corpo `scan`/`hack`; wanted/aggro buffs; tick decay; PDA row; `tests/test_footprint.py` |
| ~~WD.5~~ | ~~Profiler-gated social engineering~~ | ✅ `world/profiler_talk.py`; trait branches + bribe/flags; `tests/test_profiler_talk.py` |
| ~~WD.6~~ | ~~Fixer profiler contracts~~ | ✅ `profiler_contract` quest; `scan_npc`/`profile_trait`/`hack_infra`; `tests/test_profiler_gigs.py` |
| ~~WD.7~~ | ~~Jam / distract patrol NPCs~~ | ✅ `jam`/`distract` commands; `security_detail` resistance; `tests/test_ctos_distract.py` |
| ~~WD.8~~ | ~~ctOS node connection map~~ | ✅ `net_nodes.yaml` `links:`; `probe`/`map` mesh; cross-district `link_locks`; `tests/test_ctos_mesh.py` |
| ~~WD.9~~ | ~~Scheduled city events~~ | ✅ `world/ctos_events.py`; scheduler `ctos_*`; district restore on tick; `tests/test_ctos_events.py` |
| ~~WD.10~~ | ~~DedSec faction & tutorial beat~~ | ✅ Faction `dedsec`; `pledge`; tutorial profiler lesson; help **City OS**; `tests/test_dedsec.py` |

**Suggested order:** WD.1–WD.10 shipped (2026-06).

**Deferred (out of scope for text MUD):** open-world driving, physical parkour, smartphone UI clone, real-time multiplayer ctOS invasion.

### Hacknet-style NETRUN (HN)

**Policy:** Original homage to **terminal breach fantasy** (Hacknet-style trace pressure, multi-step connect, proxy hops)—not Matt Trobbiani IP or story canon. Integrates with existing NETRUN shell, RAM, ctOS mesh (WD.8), footprint (WD.4), and district events (WD.9).

**Goal:** NETRUN is a **persistent session** with trace pressure; the physical world (combat, movement, blackout, surveillance heat) can **force disconnect**.

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~HN.1~~ | ~~Trace meter~~ | ✅ `Player.net_trace` 0–100; `world/net_session.py` tick gain; full trace → disconnect + penalty; meta `net_trace`; `tests/test_net_trace.py` |
| ~~HN.2~~ | ~~Multi-step breach~~ | ✅ `connect` / `breach` / `exploit`; `hack` auto-pipeline; node `security` in YAML; `tests/test_net_breach.py` |
| ~~HN.3~~ | ~~Environment disconnect~~ | ✅ Combat / chase / `go` force `net_shell` off; `net.disconnect.*`; client + registry allow `go`; `tests/test_net_disconnect.py` |
| ~~HN.4~~ | ~~Trace environment modifiers~~ | ✅ `blackout` / footprint / wanted accelerate trace; `tests/test_net_trace.py` |
| ~~HN.5~~ | ~~Node files & cover~~ | ✅ `files:` on `net_nodes.yaml`; `cat` / `cover`; `tests/test_net_files.py` |
| ~~HN.6~~ | ~~Mesh proxy route~~ | ✅ `route <node>` via mesh `links`; slower trace, RAM upkeep; `tests/test_net_route.py` |

**Suggested order:** HN.1–6 shipped (2026-06).

### Mature / NSFW content (18+)

**Policy:** Original homage-style cyberpunk fiction; not official IP. All mature content is **opt-in** (`content_rating` / `mature_enabled` on player save), gated at login and command layer, with copy in the private **`cyber_mud_mature`** pack (`data/mature/locale/mature_en.yaml`, `mature_zh.yaml`)—never mixed into default help/MOTD.

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~M.0~~ | ~~Content rating & opt-in~~ | ✅ `Player.content_rating`; `settings mature on\|off`; register `mature`; `world/mature.py`; `tests/test_content_rating.py` |
| ~~M.1~~ | ~~Gore & bloody combat~~ | ✅ `combat/gore.py`; kill/crit/corpse lines; Focus `gore` tint; `tests/test_gore.py` |
| ~~M.2~~ | ~~Injury & trauma flavor~~ | ✅ `world/trauma.py`; bleed status; ripperdoc treat on clinic entry; tick damage |
| ~~M.3~~ | ~~Adult venues & NPCs~~ | ✅ `kabuki_lounge`, `bd_den`, `kabuki_host`; `tags: [mature]`; mature `talk` |
| ~~M.4~~ | ~~Romance & intimacy~~ | ✅ `data/mature/romance.yaml`; `flirt` / `spend_time`; `romance_flags` on save |
| ~~M.5~~ | ~~Mature braindance & gigs~~ | ✅ `data/mature/braindances_mature.yaml`, `quests_mature.yaml`; teen `gigs`/`bd` filter |
| ~~M.6~~ | ~~Client warnings & UI~~ | ✅ Login 18+ checkbox; help hides mature category; Focus gore style |
| ~~M.7~~ | ~~Authoring & admin~~ | ✅ `mature_validate.py`; `docs/MATURE_CONTENT.md`; CONTRIBUTING note |
| ~~M.8~~ | ~~Mature look/scan flavor~~ | ✅ `world/mature_flavor.py`; `look`/`scan` room lines; `look <npc>` detail for mature NPCs |
| ~~M.9~~ | ~~Staged romance lines~~ | ✅ `romance_line()` tier `_2`/`_3`; expanded `mature.romance.*` for host/dancer/clerk |
| ~~M.10~~ | ~~Mature interact copy~~ | ✅ `world/interactables.py` mature override; `lounge_chrome_bar`, `vip_preview_pod`, `bd_den_archive` |
| ~~M.11~~ | ~~BD den clerk & chrome_mirage~~ | ✅ `bd_den_clerk` NPC; `chrome_mirage` BD; `chrome_pull` gig; clerk romance profile |
| ~~M.12~~ | ~~Tests & docs~~ | ✅ `tests/test_mature_content.py` depth cases; `docs/MATURE_CONTENT.md` flavor/romance notes |
| ~~M.13~~ | ~~Mature combat broadcasts~~ | ✅ Per-observer `broadcast_mature_key`; `combat.victory/defeat_broadcast_*` in mature locale |
| ~~M.14~~ | ~~Mature say in clubs~~ | ✅ `social.say_ok/say_broadcast.<room>` for kabuki/bd_den; teen-safe default fallback |
| ~~M.15~~ | ~~Mature presence flavor~~ | ✅ `social.presence_enter/leave.<room>` on `go` in mature venues |
| ~~M.16~~ | ~~Romance gift reactions~~ | ✅ `world/mature_give.py`; `give <item> <romance_npc>` mature copy + broadcast |
| ~~M.17~~ | ~~Combat taunt & finish~~ | ✅ `taunt <npc>` in combat; `finish` coup de grace when enemy ≤30% HP; help mature category |
| ~~M.18~~ | ~~Mature private submodule + history purge~~ | ✅ Private `0xd3adcafe/cyber_mud_mature`; `data/mature` submodule; pack docs (`README`, `CLAUDE`, `CONTRIBUTING`, `LOCALIZATION` + `*.zh.md`, English default); `scripts/mature-submodule-split.sh`; `scripts/mature-history-purge.sh` (legacy + `data/mature/*` paths); teen fallback when pack missing; `tests/test_mature_paths.py` |
| ~~M.19~~ | ~~Mature pack style guide~~ | ✅ `data/mature/docs/STYLE.md` + `STYLE.zh.md`; noir/lewd voice rules; banned cliché list; `{persona}` / `{player}` template conventions |
| ~~M.20~~ | ~~Dual voice resolver~~ | ✅ `world/mature_voice.py`; `resolve_mature_voice()` → `noir` \| `lewd`; `data/mature/voice.yaml`; `mature.noir.*` / `mature.lewd.*` locale keys |
| ~~M.21~~ | ~~Persona (SFW, all players)~~ | ✅ `persona` / `persona set` / `persona clear`; `Player.persona` on save; `look <player>` public; `tests/test_persona.py` |
| ~~M.22~~ | ~~Scene + whisper~~ | ✅ `scene` / `scene status`; `whisper <target> <msg>`; expanded `romance.yaml`; `tests/test_mature_social.py` |
| ~~M.23~~ | ~~Client mature Rich format~~ | ✅ `client/mature_format.py`; `*action*` / dialogue / `>env` / SFX palettes; `mature` log channel; `@meta mature_voice` status chip; `tests/test_mature_format.py` |
| ~~M.24~~ | ~~Lewd trigger wiring~~ | ✅ Mature BD `_voice_mature` flag; cleared on `go`; consumable/trace/humanity/status hooks in `resolve_mature_voice` |
| ~~M.25~~ | ~~Dual-voice NPC content~~ | ✅ `kabuki_host`, `bd_den_clerk`, `kabuki_dancer`; stages 4–5; noir + lewd line sets in mature pack |
| ~~M.26~~ | ~~Mature validate expansion~~ | ✅ `BANNED_LEWD_CLICHES`; noir/lewd key parity; EN lewd ban-list scan |

**Suggested order:** M.0–M.26 shipped (2026-06).

### World expansion ([WORLD.md](WORLD.md))

**Baseline (2026-06):** **263 rooms**, **109 NPCs**, **45 items** — WORLD.md scale targets met; district `safety`/`atmosphere`; `help tutorial`; faction depth; schedules + gray market; poison/overheat + live world reactions (`world/reactions.py`). **World expansion W.1–W.14 shipped** — authored follow-up tracked under **Content depth** below.

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~W.1~~ | ~~Procedural district grids~~ | ✅ `tools/merge_world_grid.py`; district-prefixed IDs (`watson_3_2`); `grid_x`/`grid_y`; hub↔grid links; `tests/test_world_scale.py` |
| ~~W.2~~ | ~~Eight-district room clusters~~ | ✅ 8 districts merged → **263 rooms**; `map` explored grid; locale `*_en`/`*_zh` on grid cells |
| ~~W.3~~ | ~~District safety & atmosphere~~ | ✅ `data/districts.yaml`; `look` atmosphere; patrol/aggro/weather bias; `tests/test_districts.py` |
| ~~W.4~~ | ~~Story core rooms~~ | ✅ `crypt`, `data_vault`; Undercity graph; onboarding path wired |
| ~~W.5~~ | ~~Story anchor NPCs & loot~~ | ✅ `guard`, `priest`, `rat`; terminals; `rusty_key`, `glowstick`; `tests/test_story_anchors.py` |
| ~~W.6~~ | ~~`help tutorial` onboarding~~ | ✅ `help tutorial`; `tests/test_help_tutorial.py` |
| ~~W.7~~ | ~~Faction gameplay depth~~ | ✅ `pledge tyrell`; faction talk/shop/hostility; `tests/test_factions.py` |
| ~~W.8~~ | ~~District weather & schedules~~ | ✅ `data/schedule.yaml` all shop hours + period patrol multipliers; NPC schedules (`broker`, `bazaar_fixer`, `dock_smuggler`, `corp_guard`); `patrol_period_multiplier`; `tests/test_schedule.py` |
| ~~W.9~~ | ~~Society & black market~~ | ✅ `docks_gray` shop, `dock_smuggler` NPC, `gray_market` quest (`give_npc`); corp/street `appraise`; `give <item> <npc>`; `tests/test_black_market.py` |
| ~~W.10~~ | ~~Multiplayer presence~~ | ✅ `presence.enter`/`leave` on `go`; sender-excluded `say`/`give` broadcasts; peer `look`; `tests/test_multiplayer.py` |
| ~~W.11~~ | ~~NETRUN story nodes~~ | ✅ `crypt_node`, `vault_core`; `hack_core` quest; `tests/test_net_story.py` |
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

#### Content depth round 2 (D.7–D.10)

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~D.7~~ | ~~District grid look flavor~~ | ✅ `district.grid.*`; `grid_flavor_line()` in `look` on procedural cells |
| ~~D.8~~ | ~~District quest chains~~ | ✅ `watson_pulse`, `docks_courier`, `kabuki_whisper`, `zone_sweep`; 0 quest WARN |
| ~~D.9~~ | ~~District spotlight NPCs~~ | ✅ 8 named grid NPCs; unique `talk.*` in `data/world.yaml` |
| ~~D.10~~ | ~~District ambient tick copy~~ | ✅ `world.ambient.*` all eight districts; `tests/test_content_depth.py` |

**Suggested order:** D.9 → D.8 → D.7 → D.10. **All phases shipped (2026-06).**

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

### Client log UX (readability & channel identity)

**Goal:** Make the main `#log` / `#scrollback_wrap` area scannable—combat, exploration, social, progression, and system lines should be **instantly distinguishable** without reading every word.

**Baseline (2026-06):** `client/animated_log.py` + `client/output_prefix.py` classify only `motd` / `sys` / `err` / `text` / `echo`; `client/env_format.py` colors look/scan entity lists inside `text`; combat CD countdown rewrites lines; `/clear` clears buffer. Most game output still shares the same dim `›` prefix.

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~CL.1~~ | ~~Log kind taxonomy~~ | ✅ `client/log_classifier.py`; auto-classify combat/quest/social/progression/ambient/env; `app._append_log` |
| ~~CL.2~~ | ~~Per-kind visual identity~~ | ✅ `client/log_styles.py`; `themes.py` `LogPalette`; `/theme` redraws log |
| ~~CL.3~~ | ~~Combat log channel~~ | ✅ Combat palette + CD → `combat` kind; `───` separator between rounds; `cd_display.py` preserved |
| ~~CL.4~~ | ~~Environment blocks~~ | ✅ `env_format.py` desc/flavor tiers; `───` before new look header; scan/entity colors |
| ~~CL.5~~ | ~~Social & presence~~ | ✅ `say`/`talk`/presence EN+ZH markers → `social` channel |
| ~~CL.6~~ | ~~Progression & gigs feed~~ | ✅ XP/level/street cred/proficiency + `◈` quest lines → `progression`/`quest` |
| ~~CL.7~~ | ~~Ambient & world tick~~ | ✅ `ambient` kind dim italic via `LogPalette` |
| ~~CL.8~~ | ~~Tests & docs~~ | ✅ `tests/test_log_classifier.py`; `tests/test_output_prefix.py`; `CLIENT_UI_DEBUG.md`; `docs/player/CLIENT.md` legend; client UI test fixes |
| ~~CL.9~~ | ~~Compact display mode~~ | ✅ `/log compact on|off`; plain `›` prefix; no `───` separators; `settings.json` |
| ~~CL.10~~ | ~~Channel toggles~~ | ✅ `/log hide`/`show`/`show all`; filter ambient/social/combat/env/quest/progression/text at render |
| ~~CL.11~~ | ~~Export & tests~~ | ✅ `/log export [path]`; `plain_lines()`; `tests/test_log_settings.py`; `tests/test_client_app.py` |

**Suggested order:** CL.1 → CL.2 → CL.3 + CL.4 → CL.5 + CL.6 → CL.7 → CL.8 → CL.9 → CL.10 → CL.11. **All phases shipped (2026-06).**

### Client UI modernization (Grok-style + NETRUN HUD)

**Goal:** Minimal chrome, browser-tab overlay (Help + NETRUN HUD), F1–F12 hotkey map, mesh sidebar on NETRUN. Full spec: [`CLIENT_UI_REDESIGN.md`](CLIENT_UI_REDESIGN.md).

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~CU.1~~ | ~~Status strip~~ | ✅ `#status_strip`; `client/status_strip.py` |
| ~~CU.2~~ | ~~Overlay panel + tabs~~ | ✅ `#overlay_panel`; `⎈ NET` / `? Help` tabs; F2 help; Esc close |
| ~~CU.3~~ | ~~NETRUN HUD~~ | ✅ `client/overlay_panel.py`; trace bar; expand on `net`; 50% height |
| ~~CU.4~~ | ~~NETRUN log + sidebar snapshot~~ | ✅ `netrun-active` log tint; F11/F12; restore stack on exit |
| ~~CU.5~~ | ~~Mesh panel + auto-open~~ | ✅ `commands/mesh.py`; NETRUN auto mesh; `/overlay netrun-sidebar off` |
| ~~CU.0~~ | ~~Login ASCII rotation~~ | ✅ `scene_for_carousel`; 10s tick |

**Hotkeys (in-game):** F1 PDA · F2 Help · F3 Map · F4 Gear · F5 Gigs · F6 Mesh · F7–F10 reserved · **F11** sidebar · **F12** NETRUN overlay. Login: **F8** clear stored credentials.

**Suggested order:** CU.1 → CU.2 → CU.3 → CU.4 → CU.5 (one milestone commit); CU.0 after.

### Security (OWASP ASVS L1)

**Goal:** Align authentication and save I/O with [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) Level 1 for the hobby MUD threat model. Full matrix: [`SECURITY.md`](SECURITY.md) / [`SECURITY.zh.md`](SECURITY.zh.md).

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~ASVS.1~~ | ~~Password hashing~~ | ✅ PBKDF2-HMAC-SHA256 600k iter; legacy SHA-256 verify + login rehash; `persistence/passwords.py` |
| ~~ASVS.2~~ | ~~Unified login errors~~ | ✅ `auth.invalid_credentials` on bad name/password; no enumeration; `commands/auth_helpers.py` |
| ~~ASVS.3~~ | ~~Save path validation~~ | ✅ Reject `..`, `/`, `\`, control chars; `shared/security.py`, `persistence/save.py` |
| ~~ASVS.4~~ | ~~Input bounds~~ | ✅ Name/password length; `maxsplit=1` passwords with spaces; 4 KiB line cap; `shared/protocol.py`, `server/main.py` |
| ~~ASVS.5~~ | ~~Auth rate limiting~~ | ✅ Per-connection 5 fails / 60s → 5 min block; `server/rate_limit.py`, `server/game.py` |
| ~~ASVS.6~~ | ~~Idle / connection limits~~ | ✅ `server/connection_limits.py`; per-IP cap + guest/auth idle prune; `auth.too_many_connections` / `auth.idle_disconnect`; `tests/test_security_auth.py` |
| ~~ASVS.7~~ | ~~Save file permissions~~ | ✅ `chmod 0o600` files; save dir `0o700`; `persistence/save.py` |
| ~~ASVS.8~~ | ~~Transport encryption~~ | ✅ Optional TLS `--tls-cert`/`--tls-key`; VPN-only doc in `SECURITY.md` |
| ~~ASVS.9~~ | ~~Reconnect without password replay~~ | ✅ `server/session_tokens.py`; `resume` command; client token storage |
| ~~ASVS.10~~ | ~~`changepass` command~~ | ✅ `commands/changepass.py`; token rotate on change |
| ~~ASVS.11~~ | ~~Account lockout~~ | ✅ `persistence/account_lockout.py`; save-backed lockout |
| ~~ASVS.12~~ | ~~Security audit log~~ | ✅ `server/audit_log.py` structured stderr |
| ~~ASVS.13~~ | ~~Client credential hygiene~~ | ✅ PIN-encrypted session token only; `client/credentials.py` |
| ~~ASVS.14~~ | ~~Security regression suite~~ | ✅ Expanded `tests/test_security_auth.py` (30+ cases) |

**Suggested order:** ASVS.1–14 shipped (2026-06). See [`SECURITY.md`](SECURITY.md).

### Tutorial zone (onboarding depth)

**Goal:** The training yard teaches every core loop—movement, gear, combat, NETRUN, cyberware, life commands, and gigs—via authored NPCs, ground loot, interactables, and a multi-stage rotation quest before Neon Square.

**Baseline (2026-06):** **10 rooms**, **13 NPCs**, **8 interactables** (third expansion), `tutorial_rotation` gig, `field_bandage` / `training_tech_pistol` / `tutorial_badge`; `tests/test_tutorial_zone.py`.

| Phase | Item | Module / acceptance |
|-------|------|---------------------|
| ~~T.1~~ | ~~Prior expansions~~ | ✅ 9 rooms → briefing/canteen/range/course/medbay; 10 NPCs; 4 interactables; `tutorial_supply` shop |
| ~~T.2~~ | ~~Graduation checkpoint room~~ | ✅ `tutorial_debrief`; `grad_warden`; east from briefing |
| ~~T.3~~ | ~~Gear & combat NPCs~~ | ✅ `armor_tech`, `combat_referee`; talk keys en/zh |
| ~~T.4~~ | ~~Scenario interactables~~ | ✅ weapon rack, equip mirror, combat holo, course gate, range lane, net jack, stim crane, grad pad |
| ~~T.5~~ | ~~Training items~~ | ✅ `field_bandage`, `training_tech_pistol`, `tutorial_badge`; ground loot + shop stock |
| ~~T.6~~ | ~~Rotation quest~~ | ✅ `tutorial_rotation` in `data/quests.yaml`; accept via `gigs`; turn-in `grad_warden` |
| ~~T.7~~ | ~~Tests & player guide~~ | ✅ `tests/test_tutorial_zone.py` 13 cases; `docs/player/TUTORIAL.md` debrief section |

**Suggested order:** T.1 (prior) → T.2 → T.3 → T.4 → T.5 → T.6 → T.7. **All phases shipped (2026-06).**

---

Suggested route: **0 → A → D.2/D.7 (playability) → B → C → remaining D → E**; for a social-exploration MUD, consider B before C.

World setting, districts, and factions: [WORLD.md](WORLD.md). Agent collaboration rules: [CLAUDE.md](../CLAUDE.md).