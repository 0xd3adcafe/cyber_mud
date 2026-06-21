# Command Reference

> **中文：** [COMMANDS.zh.md](COMMANDS.zh.md) · Hub: [README.md](README.md)

```text
+-------------------------------------------------------+
|  COMMAND MATRIX  ·  NIGHT CITY                        |
|  type in client · Tab complete · help (F3)            |
+-------------------------------------------------------+
```

In-game: `help` or **F3**. Repeat commands: `10 punch` or `punch.10` (0.5s between).

## Table of contents

- [Short aliases](#short-aliases)
- [Account](#account)
- [Explore](#explore)
- [Life & vitals](#life-vitals)
- [Items](#items)
- [Gear & consumables](#gear-consumables)
- [Cyberware](#cyberware)
- [Housing](#housing)
- [Transit & vehicles](#transit-vehicles)
- [Shops](#shops)
- [Social](#social)
- [Combat](#combat)
- [NETRUN](#netrun)
- [Gigs](#gigs)
- [Progression](#progression)
- [UI panels](#ui-panels)
- [Braindance](#braindance)
- [Client-only (not sent to server)](#client-only-not-sent-to-server)

## Short aliases

| Alias | Expands to |
|-------|------------|
| `l` | `look` |
| `i`, `inv` | `inventory` |
| `get` | `take` |
| `n` `s` `e` `w` | `go north` … `go west` |
| `u` `d` | `go up` · `go down` |
| `h` | `help` |
| `q` | `quit` |
| `eq` | `equipment` |
| `st` | `status` / `pda` |
| `sc` | `scan` |

---

## Account

| Command | Description |
|---------|-------------|
| `register <name> <password>` | Create character |
| `login <name> <password>` | Log in |
| `help` | Command list (F3) |
| `quit` | Log out (stay connected; client returns to login) |
| `lang [en\|zh]` | Display language |

---

## Explore

| Command | Description |
|---------|-------------|
| `look [target]` | Room or target (item, NPC, equipment slot) |
| `go <direction>` | Move — `north` `south` `east` `west` `up` `down` |
| `scan` | Scan surroundings |
| `map` | Exploration map (F4) |
| `interact <object>` | Use interactable in room |
| `time` | World clock and period |
| `recall` | Teleport to Training Yard |

---

## Life & vitals

| Command | Description |
|---------|-------------|
| `sit` | Sit down (rest posture; blocked in combat / NETRUN) |
| `stand` | Stand up (clear rest posture) |
| `lie` | Lie down (better HP regen while resting) |
| `rest` | Rest (auto-sit if standing; reduces fatigue over ticks) |
| `sleep` | Sleep (needs safe room or rest anchor; best HP/RAM regen) |
| `wake` | Wake from rest or sleep |

Rest and sleep boost tick HP (and RAM while lying/sleeping). Use `interact` on benches or beds in the tutorial canteen, your flat, ripper clinic, or lounge. Moving, speaking, or combat wakes you. `look me` shows posture and fatigue; PDA lists life state.

---

## Items

| Command | Description |
|---------|-------------|
| `take <item>` | Pick up (`take all`) |
| `drop <item>` | Drop (`drop all`) |
| `inventory` | Backpack |
| `give <item> <player>` | Give to another player |
| `appraise <item>` | Street value |
| `craft <recipe>` | Craft (at shop / ripperdoc) |
| `disassemble <item>` | Break down item |

---

## Gear & consumables

| Command | Description |
|---------|-------------|
| `equip <item>` | Wear / wield |
| `unequip <item\|slot>` | Remove gear |
| `equipment` | Gear panel (F5) |
| `mod <chip>` | Weapon mod chip |
| `use <item>` | Use consumable |
| `eat <food>` | Eat |
| `drink <drink>` | Drink |

---

## Cyberware

| Command | Description |
|---------|-------------|
| `install <kit>` | Install implant (ripper clinic) |
| `cyberware` / `chrome` | View implants |
| `uninstall <slot>` | Remove implant |

---

## Housing

| Command | Description |
|---------|-------------|
| `rent <flat>` | Rent apartment (at square) |
| `home` | Fast travel home |
| `stash put\|take <item>` | Apartment locker |

---

## Transit & vehicles

| Command | Description |
|---------|-------------|
| `transit <destination>` | NCART public transit |
| `vehicles buy\|select <model>` | Garage (docks) |
| `drive <dest>` | Drive to destination |

---

## Shops

| Command | Description |
|---------|-------------|
| `shop` | List wares |
| `buy <item>` | Purchase |
| `sell <item>` | Sell |

---

## Social

| Command | Description |
|---------|-------------|
| `talk <npc>` | Talk to NPC |
| `say <message>` | Speak in room |
| `pledge <faction>` | Join faction (e.g. `arasaka`, `maelstrom`) |
| `learn <skill>` | Learn protocol from broker |

---

## Combat

Real-time encounter—watch cooldowns in status / hint bar.

| Command | Description |
|---------|-------------|
| `attack [style] <enemy>` | Attack (style from weapon if omitted) |
| `shoot` | Firearm |
| `slash` | Blade |
| `bash` | Blunt |
| `punch` | Empty hands |
| `backstab` | Blade, longer CD |
| `defend` | Halve next hit |
| `flee` | Leave combat |
| `quickhack [name]` | RAM quickhack (overheat, short_circuit, …) |

---

## NETRUN

| Command | Description |
|---------|-------------|
| `net` / `netrun` | Enter hacking shell |

**Inside NETRUN:** `look`, `scan`, `probe`, `hack <node>`, `status`, `talk`, `say`, `exit`.  
General MUD commands are blocked until `exit`.

---

## Gigs

| Command | Description |
|---------|-------------|
| `gigs` / `gig` / `journal` | Job board & tracker (F7) |

Use `gigs accept <id>` when offered. Track progress in sidebar.

---

## Progression

| Command | Description |
|---------|-------------|
| `stats` | Level, XP, points |
| `talents` | Talent tree (`talent <name>` to learn) |
| `improve <stat>` | Spend attribute point |

---

## UI panels

| Command | Description |
|---------|-------------|
| `pda` / `status` | Vitals, faction, implants (F2) |
| `prompt set\|show\|template` | Server prompt templates |

Client-only overrides: `/prompt` — see [CLIENT.md](CLIENT.md).

---

## Braindance

| Command | Description |
|---------|-------------|
| `braindance <clip>` / `bd` | Experience BD at a booth |

---

## Client-only (not sent to server)

| Command | Description |
|---------|-------------|
| `/theme [id\|list]` | UI theme |
| `/prompt set\|template\|show\|reset` | Local prompt preview |
| `/reconnect` | Force reconnect |
| `/clear` | Clear log buffer |
| `/quit` | Exit client app |

Full client guide: [CLIENT.md](CLIENT.md).
