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

## Copy files (do not mix into default locale)

| File | Purpose |
|------|---------|
| `data/locale/mature_en.yaml` | English gore, trauma, romance, mature talk |
| `data/locale/mature_zh.yaml` | Traditional Chinese mirror (keep keys in lockstep) |

Use `shared.mature_i18n.tm(locale, "combat.crit_1")` — keys are auto-prefixed with `mature.`.

## World data

| Tag / field | Usage |
|-------------|--------|
| `tags: [mature]` on rooms | Gates `go` for teen players |
| `tags: [mature]` on NPCs | Gates `talk`; mature dialogue from `mature.talk.<talk_key>` |
| `rating: mature` on quests | Loaded from `data/quests_mature.yaml`; hidden from teen `gigs` |
| `rating: mature` on braindances | Loaded from `data/braindances_mature.yaml` |

## Romance scaffold

`data/romance.yaml` maps NPCs to `flirt` / `spend_time` affinity stages. Copy lives under `mature.romance.*` in mature locale files.

## Validation

```bash
./admin.sh validate
```

`world/mature_validate.py` checks mature locale parity, romance NPC refs, mature room exits, and mature quest/BD ratings.

## Help and client

- `help` omits the **18+ content** category unless the player has opted in.
- Client login shows an **18+ mature content** checkbox only in register mode.
- Focus block uses a blood-tinted combat style when `content_rating=mature`.