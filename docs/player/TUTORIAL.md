# Tutorial Walkthrough

> **中文：** [TUTORIAL.zh.md](TUTORIAL.zh.md) · Hub: [README.md](README.md)

```text
  ╔═══════════════════════════════════════════════════╗
  ║   T R A I N I N G   Y A R D   ·   S E C U R E    ║
  ║   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄   ║
  ║   instructors · holo targets · isolated net       ║
  ╚═══════════════════════════════════════════════════╝
```

Use `recall` anytime to return to the hub. Tutorial is isolated from open PvP in the city.

## Hub — Training Yard (`tutorial`)

```text
              [ Briefing ]
                   │ up
    [Combat]───[ HUB ]───[ Net Sim ]
       │ north      │ east
   [Range]      [Armory]
                 south
```

| Exit | Room | Learn |
|------|------|-------|
| `up` | Mission Briefing | gigs, stats, factions |
| `north` | Combat Drill | attack, defend, flee |
| `east` | Netrun Sim Bay | `net`, hack, RAM |
| `south` | Armory | equip, take, inventory |
| `west` | *(after ready)* Neon Square | enter Night City |

Start with:

```text
look
scan
talk <instructor>
```

## 1. Mission Briefing (`tutorial_briefing`)

```text
  ┌─ HOLO BOARD ─────────────────┐
  │  ◆ gigs · stats · recall      │
  └───────────────────────────────┘
```

Try:

```text
stats
gigs
journal
```

- **gigs** / **F7** — street job board and tracker  
- **stats** — level, XP, attribute points  
- **recall** — teleport back to Training Yard  

`down` returns to hub.

## 2. Armory (`tutorial_armory`)

```text
  ║ weapon rack │ armor │ cyber kit ║
```

Practice gear loop:

```text
take trainee_blade
inventory
equip trainee_blade
equipment
```

Use **F5** for equipment sidebar. Try `look trainee_blade` for item details.

`north` back to hub.

## 3. Combat Drill (`tutorial_combat`)

```text
   ( o )  sparring drone
   / | \  padded floor
```

| Step | Command |
|------|---------|
| Start fight | `attack <target>` or `punch patrol_dummy` |
| Mitigate | `defend` |
| Escape | `flee` |
| Ranged | `shoot` / `slash` / `bash` (if weapon equipped) |

Combat is **real-time** with cooldowns—watch the client status bar and hint line.

Branches:

- `north` → **Firing Range** (guns, smartgun)  
- `east` → **Obstacle Course** (`interact`, `scan`)  

## 4. Firing Range (`tutorial_range`)

```text
  ▄▄▄▄▄  holo lanes  ▄▄▄▄▄
```

Equip from armory first, then:

```text
equip training_sidearm
attack patrol_dummy
```

`south` → combat zone.

## 5. Obstacle Course (`tutorial_course`)

```text
  ► scan beacon ──► interact gate ──► target dummy
```

```text
scan
interact <object>
```

`west` → combat zone.

## 6. Netrun Sim Bay (`tutorial_net`)

```text
  ┌───┐ green glyphs │ RAM meter
  │ > │ coach watching
  └───┘
```

Enter NETRUN shell:

```text
net
```

Inside NETRUN (separate prompt/theme):

```text
look
probe
hack <node>
status
exit
```

`exit` returns to the physical layer. Only NETRUN-safe commands work there—see [COMMANDS.md](COMMANDS.md) § NETRUN.

`north` → **Sim Ripper Bay**.

## 7. Sim Ripper Bay (`tutorial_medbay`)

Practice cyberware **safely**:

```text
take practice_cyber_kit
install <kit>
cyberware
use med_stim
```

`south` → net bay.

## 8. Graduate to the city

From **Training Yard**:

```text
go west
```

You arrive at **Neon Square**—explore, take gigs, and survive.

```text
  ╔════════════════════════════════════╗
  ║  JACK-OUT COMPLETE · WELCOME TO    ║
  ║  N I G H T   C I T Y               ║
  ╚════════════════════════════════════╝
```

Recommended next commands: `map`, `scan`, `talk` info broker, `shop` (where available).