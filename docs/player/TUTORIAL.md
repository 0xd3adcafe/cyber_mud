# Tutorial Walkthrough

> **中文：** [TUTORIAL.zh.md](TUTORIAL.zh.md) · Hub: [README.md](README.md)

```text
+-------------------------------------------------------+
|  TRAINING YARD  ·  SECURE                             |
|  instructors · holo targets · isolated net            |
+-------------------------------------------------------+
```

Use `recall` anytime to return to the hub. Tutorial is isolated from open PvP in the city.

## Recommended route

| Step | Room | Practice |
|------|------|----------|
| 1 | Training Yard | `look`, `talk` instructor |
| 2 | Armory → Canteen | `equip`, `interact canteen_bench`, `sit`, `rest`, `look me` |
| 3 | Combat Drill | `attack`, `defend`, `flee` |
| 4 | Netrun Sim | `net`, `hack`, `exit` |
| 5 | Neon Square | `map`, `gigs`, explore |

Life commands (`sit`, `rest`, `sleep`, `wake`) are taught in the **Trainee Canteen**—see §2b. Full reference: [COMMANDS.md](COMMANDS.md) § Life & vitals.

## Hub — Training Yard (`tutorial`)

```text
+-------------------------------------------------------+
|                  [ Briefing ]                         |
|                       | up                            |
|   [Combat]<--+[ HUB ]+-->[ Net Sim ]                  |
|      | north      | east                              |
|   [Range]     [Armory]--west-->[Canteen]              |
|                 south                                 |
+-------------------------------------------------------+
```

| Exit | Room | Learn |
|------|------|-------|
| `up` | Mission Briefing | gigs, stats, factions |
| `east` (from briefing) | Graduation Checkpoint | rotation quest turn-in |
| `north` | Combat Drill | attack, defend, flee |
| `east` | Netrun Sim Bay | `net`, hack, RAM |
| `south` | Armory | equip, take, inventory |
| `west` (from armory) | Trainee Canteen | sit, rest, eat, drink |
| `west` (from hub) | *(after ready)* Neon Square | enter Night City |

Start with:

```text
look
scan
talk <instructor>
```

The instructor holo mentions the canteen west of the armory for `sit` / `rest` practice.

## 1. Mission Briefing (`tutorial_briefing`)

```text
+-------------------------------------------------------+
|  HOLO BOARD                                           |
|  * gigs   * stats   * recall                          |
+-------------------------------------------------------+
```

Try:

```text
stats
gigs
gigs accept tutorial_rotation
journal
```

- **gigs** / **F7** — street job board and tracker  
- **gigs accept tutorial_rotation** — multi-stage yard drill (gear, combat, NETRUN, graduate stamp)  
- **stats** — level, XP, attribute points  
- **recall** — teleport back to Training Yard  

`east` → **Graduation Checkpoint** (`tutorial_debrief`). `down` returns to hub.

## 1b. Graduation Checkpoint (`tutorial_debrief`)

```text
+-------------------------------------------------------+
|  GRAD PAD          |  WARDEN                         |
|  rotation stamp    |  talk for badge                 |
+-------------------------------------------------------+
```

After journal shows all rotation stages complete:

```text
interact tutorial_grad_pad
talk grad_warden
```

You receive a **trainee graduate badge** and street cred. `west` → briefing.

## 2. Armory (`tutorial_armory`)

```text
+-------------------------------------------------------+
|  weapon rack  |  armor  |  cyber kit                  |
+-------------------------------------------------------+
```

Practice gear loop:

```text
take trainee_blade
inventory
equip trainee_blade
equipment
interact tutorial_weapon_rack
interact tutorial_equip_mirror
talk armor_tech
```

Use **F5** for equipment sidebar. Try `look trainee_blade` for item details. The **armor tech** walks through all seven slots.

`north` back to hub. `west` → **Trainee Canteen**.

## 2b. Trainee Canteen (`tutorial_canteen`)

```text
+-------------------------------------------------------+
|  [ VENDING ]              [ BENCH ]                   |
|   eat / drink              sit / rest                 |
+-------------------------------------------------------+
```

Practice life commands and consumables:

```text
interact canteen_bench
sit
rest
look me
wake
```

- **interact canteen_bench** — sit on the bench (rest anchor)  
- **sit** / **rest** — posture and fatigue recovery over world ticks  
- **look me** — HP, fatigue, and posture (also on **F2** PDA)  
- **wake** / **stand** — clear rest before moving (`go` also wakes you)  

Also try `eat`, `drink`, and `use med_stim` with the canteen tech NPC. `east` returns to armory.

## 3. Combat Drill (`tutorial_combat`)

```text
+-------------------------------------------------------+
|      ( o )  sparring drone                            |
|      / | \  padded floor                              |
+-------------------------------------------------------+
```

| Step | Command |
|------|---------|
| Start fight | `attack <target>` or `punch patrol_dummy` |
| Mitigate | `defend` |
| Escape | `flee` |
| Ranged | `shoot` / `slash` / `bash` (if weapon equipped) |

```text
talk combat_referee
interact tutorial_combat_holo
```

Combat is **real-time** with cooldowns—watch the client status bar and hint line.

Branches:

- `north` → **Firing Range** (guns, smartgun)  
- `east` → **Obstacle Course** (`interact`, `scan`)  

## 4. Firing Range (`tutorial_range`)

```text
+-------------------------------------------------------+
|  #####  holo lanes  #####                             |
+-------------------------------------------------------+
```

Equip from armory first, then:

```text
equip training_sidearm
attack patrol_dummy
```

`south` → combat zone.

## 5. Obstacle Course (`tutorial_course`)

```text
+-------------------------------------------------------+
|  scan beacon --> interact gate --> target dummy       |
+-------------------------------------------------------+
```

```text
scan
interact <object>
```

`west` → combat zone.

## 6. Netrun Sim Bay (`tutorial_net`)

```text
+-------------------------------------------------------+
|  [ > ]  green glyphs  |  RAM meter                    |
|         coach watching                                |
+-------------------------------------------------------+
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
+-------------------------------------------------------+
|  JACK-OUT COMPLETE  ·  WELCOME TO NIGHT CITY          |
+-------------------------------------------------------+
```

Recommended next commands: `map`, `scan`, `talk` info broker, `shop` (where available).

## 9. Rest outside the tutorial

After you rent a flat or find safe rooms:

| Location | How | Commands |
|----------|-----|----------|
| `watson_flat` | `rent` at square, `home` | `sleep`, `interact flat_bunk` |
| `ripper_clinic` | `go west` from square | `rest`, `interact clinic_bed` |
| `kabuki_lounge` | via alley | `rest`, lounge booth |

Moving, `say`, `talk`, or combat wakes you from rest or sleep. See [COMMANDS.md](COMMANDS.md) § Life & vitals.