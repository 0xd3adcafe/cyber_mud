# Mature content authoring (18+)

> **中文：** [MATURE_CONTENT.zh.md](MATURE_CONTENT.zh.md)

All mature / NSFW-adjacent content in **cyber_mud** is **opt-in**. Default player rating is `teen`.

## Table of contents

- [Player opt-in](#player-opt-in)
- [Content pack (private submodule, M.18)](#content-pack-private-submodule-m18)
  - [Pack documentation (`cyber_mud_mature`)](#pack-documentation)
- [World data](#world-data)
- [Romance scaffold](#romance-scaffold)
- [Mature flavor hooks (look / scan / interact)](#mature-flavor-hooks-look-scan-interact)
- [Mature social & combat (M.13–M.17)](#mature-social-combat-m13m17)
- [Dual voice, persona, scene & whisper (M.19–M.26)](#dual-voice-persona-scene--whisper-m19m26)
  - [Dual voice engine (M.20)](#dual-voice-engine-m20)
  - [Persona (M.21, SFW)](#persona-m21-sfw)
  - [Scene & whisper (M.22)](#scene--whisper-m22)
  - [Client Rich formatting (M.23)](#client-rich-formatting-m23)
- [Validation](#validation)
- [Help and client](#help-and-client)

## Player opt-in

| Mechanism | Detail |
|-----------|--------|
| Register | `register <name> <password> mature` or client login checkbox (register mode) |
| Settings | `settings mature on` / `settings mature off` |
| Save field | `Player.content_rating` — `teen` or `mature` |

Teen-rated players cannot enter `tags: [mature]` rooms, use `flirt` / `spend_time`, accept mature gigs, or play mature braindances.

## Content pack (private submodule, M.18)

Mature YAML lives in **`data/mature/`**, intended as a **private** git submodule (`cyber_mud_mature`). Public clones without submodule access run in teen mode only.

| File | Purpose |
|------|---------|
| `data/mature/locale/mature_en.yaml` | English gore, trauma, romance, mature talk |
| `data/mature/locale/mature_zh.yaml` | Traditional Chinese mirror (keep keys in lockstep) |
| `data/mature/quests_mature.yaml` | Mature gigs |
| `data/mature/braindances_mature.yaml` | Mature braindances |
| `data/mature/romance.yaml` | Romance profile scaffolding |

```bash
git submodule update --init data/mature   # requires access to cyber_mud_mature
```

### Pack documentation (`cyber_mud_mature`)

English `*.md` is canonical; Traditional Chinese mirrors use `*.zh.md` (same policy as **cyber_mud**).

| English | Chinese |
|---------|---------|
| [README](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/README.md) | [README.zh.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/README.zh.md) |
| [CLAUDE.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/CLAUDE.md) | [CLAUDE.zh.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/CLAUDE.zh.md) |
| [CONTRIBUTING.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/CONTRIBUTING.md) | [CONTRIBUTING.zh.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/CONTRIBUTING.zh.md) |
| [LOCALIZATION.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/LOCALIZATION.md) | [LOCALIZATION.zh.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/LOCALIZATION.zh.md) |

**Maintainers:** edit YAML in the private pack above; push, then bump the `data/mature` submodule in **cyber_mud**. Split / purge scripts (main repo): `scripts/mature-submodule-split.sh`, `scripts/mature-history-purge.sh`. See [CONTRIBUTING.md](../CONTRIBUTING.md).

Use `shared.mature_i18n.tm(locale, "combat.crit_1")` — keys are auto-prefixed with `mature.`.

## World data

| Tag / field | Usage |
|-------------|--------|
| `tags: [mature]` on rooms | Gates `go` for teen players |
| `tags: [mature]` on NPCs | Gates `talk`; mature dialogue from `mature.talk.<talk_key>` |
| `rating: mature` on quests | Loaded from `data/mature/quests_mature.yaml`; hidden from teen `gigs` |
| `rating: mature` on braindances | Loaded from `data/mature/braindances_mature.yaml` |

## Romance scaffold

`data/mature/romance.yaml` maps NPCs to `flirt` / `spend_time` affinity stages. Copy lives under `mature.romance.*` in mature locale files.

Staged lines use suffixes `_2` and `_3` on the base key (e.g. `kabuki_flirt_2`). `world/mature_flavor.romance_line()` picks the highest tier available and falls back to the base key.

## Mature flavor hooks (look / scan / interact)

| Hook | Module | Locale keys |
|------|--------|-------------|
| Room atmosphere on `look` / `scan` | `world/mature_flavor.mature_room_flavor()` | `mature.room.<room_id>` for `kabuki_lounge`, `kabuki_vip`, `bd_den` |
| NPC detail on `look <npc>` | `world/mature_flavor.mature_npc_detail()` | `mature.npc.<npc_id>` |
| Interact message override | `world/interactables.perform_interact()` | `mature.interact.<interactable_id>` |

Only players with `content_rating=mature` in mature-tagged rooms/NPCs see these lines.

## Mature social & combat (M.13–M.17)

| Feature | Commands | Module / locale |
|---------|----------|-----------------|
| Room `say` flavor | `say <message>` in mature rooms | `commands/say.py`; `mature.social.say_ok/say_broadcast.<room>` |
| Presence flavor | `go` enter/leave mature rooms | `server/game.py`; `mature.social.presence_enter/leave.<room>` |
| Romance gifts | `give <item> <npc>` to romance NPC | `world/mature_give.py`; `mature.give.<npc_id>.<item>` or `.default` |
| Gore broadcasts | combat victory/defeat (observers) | `broadcast_mature_key`; `mature.combat.victory/defeat_broadcast_*` |
| Taunt | `taunt <npc>` (in combat, 18+) | `commands/taunt.py`; `mature.combat.taunt_*` |
| Finish | `finish` when enemy ≤30% HP (18+) | `combat/finish.py`; `mature.combat.finish_*` |

Peer broadcasts use `localized_broadcast_line()` — mature observers see mature copy; teen observers keep default locale lines.

## Dual voice, persona, scene & whisper (M.19–M.26)

Shipped (2026-06): **dual voice engine**, SFW **persona**, mature **scene** / **whisper**, and client Rich formatting. Mechanics in **cyber_mud**; copy in **`cyber_mud_mature`**. See [PHASES.md](PHASES.md) **Mature / NSFW content**.

### Dual voice engine (M.20)

Mature narration picks one of two authored voices at runtime (not LLM generation):

| Voice | Code key | Style |
|-------|----------|-------|
| **noir** | `noir` | Default — blunt cyberpunk prose; less repetitive lewd wording |
| **lewd** | `lewd` | Explicit Slutbunny-inspired RP (code key `lewd`, not `slutbunny`) |

`world/mature_voice.py` exposes `resolve_mature_voice(player, state, room) → "noir" | "lewd"`. Triggers are **OR** conditions (any match may switch to `lewd`):

- Mature-tagged rooms (`bd_den`, `kabuki_vip`, etc.)
- Active mature braindance session
- Player status: `overheat`, `bleed`, or `humanity ≤ 25`
- Specific consumables (pack-defined item IDs)
- High NETRUN trace threshold
- Per-NPC `voice_override` / `voice_triggers` in `data/mature/romance.yaml`

Locale keys: `mature.noir.*` and `mature.lewd.*` in `mature_en.yaml` / `mature_zh.yaml`. Language follows **`player.locale`**. English **lewd** authoring aligns with the [Slutbunny Lewd RP Preset](https://chub.ai/presets/bleachbunny/slutbunny-lewd-roleplay-preset-15458f06c7fd): direct anatomy, no euphemisms, SFX lines, and a banned-cliché list (enforced in M.26).

**M.19** adds `docs/STYLE.md` / `STYLE.zh.md` in the mature pack — voice rules, banned phrases, and `{persona}` / `{player}` template conventions.

### Persona (M.21, SFW)

**All players** (`teen` and `mature`) may use persona commands; copy is SFW and stored on the save.

| Command | Detail |
|---------|--------|
| `persona` | Show current persona text |
| `persona set <text>` | Set public description (≤200 chars) |
| `persona clear` | Remove custom text |

| Field | Detail |
|-------|--------|
| `Player.persona` | `str`, persisted in save JSON |
| `look <player>` | Shows **full** persona to other players (public) |
| `look me` | Keeps HP / posture / stats; persona shown separately |
| `{persona}` in NPC templates | **Appearance one-liner** for mature dialogue — custom persona if set, else auto summary from equipment + posture |

Teen players may set persona; they still cannot enter `tags: [mature]` rooms. Lewd voice **reframes** persona in narration at render time; it does **not** store a separate lewd persona field.

### Scene & whisper (M.22)

| Command | Rating | Gate | Notes |
|---------|--------|------|-------|
| `scene` / `scene status` | `mature` | Romance **stage only** (no time cooldown) | Scripted intimate beats from `romance.yaml` + locale |
| `whisper <target> <message>` | `mature` for mature targets | Same room | Player or NPC; **does not** advance romance stage |

Romance stage advances only via existing `flirt` / `spend_time` (confirmed). `whisper` to an NPC is private flavor, not affinity progression.

NPC cards in `data/mature/romance.yaml` gain `scene_min_stage`, `voice_default`, `voice_triggers`, stages 4–5 lines, and persona/power template fields. First targets: `kabuki_host`, `bd_den_clerk`, VIP dancer.

### Client Rich formatting (M.23)

`client/mature_format.py` applies Rich styling to mature log lines:

- `*action*` — italic emphasis
- `"dialogue"` — quoted speech
- `>env` — environment / narrator block
- SFX / onomatopoeia lines — distinct palette

New log channel kinds and optional `@meta mature_voice` chip (`noir` / `lewd`) in the status strip.

**M.24** wires consumable, BD, and cyberpsychosis triggers into `resolve_mature_voice`. **M.25** ships dual-voice NPC content in the mature pack. **M.26** extends `mature_validate` with ban-list checks and `noir` / `lewd` key parity between `mature_en.yaml` and `mature_zh.yaml`.

## Validation

```bash
./admin.sh validate
```

`world/mature_validate.py` checks mature locale parity, romance NPC refs, mature room exits, and mature quest/BD ratings.

## Help and client

- `help` omits the **18+ content** category unless the player has opted in.
- Client login shows an **18+ mature content** checkbox only in register mode.
- Focus block uses a blood-tinted combat style when `content_rating=mature`.
