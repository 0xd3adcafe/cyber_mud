# Mature content authoring (18+)

> **中文：** [MATURE_CONTENT.zh.md](MATURE_CONTENT.zh.md)

All mature / NSFW-adjacent content in **cyber_mud** is **opt-in**. Default player rating is `teen`.

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

Maintainers: `scripts/mature-submodule-split.sh`, `scripts/mature-history-purge.sh`. See [CONTRIBUTING.md](../CONTRIBUTING.md).

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

## Validation

```bash
./admin.sh validate
```

`world/mature_validate.py` checks mature locale parity, romance NPC refs, mature room exits, and mature quest/BD ratings.

## Help and client

- `help` omits the **18+ content** category unless the player has opted in.
- Client login shows an **18+ mature content** checkbox only in register mode.
- Focus block uses a blood-tinted combat style when `content_rating=mature`.