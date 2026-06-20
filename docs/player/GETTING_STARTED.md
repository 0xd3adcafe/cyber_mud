# Getting Started

> **中文：** [GETTING_STARTED.zh.md](GETTING_STARTED.zh.md) · Hub: [README.md](README.md)

```text
    ┌─────────────────────────────────────────┐
    │  ◈ NIGHT CITY NEURAL LINK               │
    │  ─────────────────────────────────────  │
    │  > link pending...                      │
    │  > awaiting credentials                 │
    └─────────────────────────────────────────┘
```

## 1. Requirements

- **Python 3.13** (see repo `.python-version`)
- Terminal with decent size (80×24 minimum; taller is better)
- Two terminals if you run server + client separately

## 2. Install & run

```bash
git clone https://github.com/0xd3adcafe/cyber_mud.git
cd cyber_mud
./setup.sh
```

**Terminal A — server:**

```bash
./run.sh
```

**Terminal B — built-in client (official way to play):**

```bash
./run.sh --client
```

```text
  ╔═══════════════════════════════════════╗
  ║  CLIENT ◄────TCP────► SERVER          ║
  ║  Textual TUI          asyncio game    ║
  ╚═══════════════════════════════════════╝
```

Do **not** need MUDlet, TinTin++, or `nc` for normal play.

## 3. Create an account

At the MOTD you are a guest. Register once:

```text
register <name> <password>
```

Example:

```text
register Vee hunter42
```

Then each session:

```text
login Vee hunter42
```

The client can remember credentials behind a **PIN** (see [CLIENT.md](CLIENT.md)).

## 4. First five minutes

After login, try this sequence:

```text
look
go north
scan
help
pda
```

| Command | What it does |
|---------|----------------|
| `look` / `l` | Room description, exits, items, NPCs |
| `go <dir>` / `n` `s` `e` `w` `u` `d` | Move (includes **up** / **down**) |
| `scan` / `sc` | Scan environment (colored in client) |
| `help` / `h` | Command list (**F3** overlay in client) |
| `pda` / `st` | Personal agent panel (**F2**) — includes posture and fatigue |

```text
      [ YOU ]
         │
    look ├─► room text + exits
    go   └─► new room
```

## 5. Training yard

New characters can practice safely in the **tutorial** district:

```text
recall
```

That sends you to the **Training Yard** hub. Full walkthrough: [TUTORIAL.md](TUTORIAL.md).

When ready for Night City proper:

```text
go west
```

(from Training Yard → **Neon Square**)

## 6. Language

Default is English. Switch display language:

```text
lang       # show current
lang en    # English
lang zh    # Traditional Chinese
```

## 7. When stuck

| Problem | Try |
|---------|-----|
| Unknown command | `help` — or [COMMANDS.md](COMMANDS.md) |
| Lost | `recall` (training) or `map` (**F4**) |
| Disconnected | `/reconnect` in client, or restart client |
| Clear log spam | `/clear` (client only) |

Next: [Tutorial Walkthrough](TUTORIAL.md) → [Command Reference](COMMANDS.md) → [Client & Hotkeys](CLIENT.md).