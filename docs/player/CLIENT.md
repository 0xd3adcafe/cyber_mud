# Client & Hotkeys

> **中文：** [CLIENT.zh.md](CLIENT.zh.md) · Hub: [README.md](README.md)

```text
+-------------------------------------------------------+
|  TEXTUAL TUI · cyber_mud official interface           |
|  log | focus | prompt | hotkeys | sidebar stack       |
+-------------------------------------------------------+
```

Launch:

```bash
./run.sh --client
```

## Layout

```text
+-------------------------------------------------------+
| status / link / chrome                                |
+-------------------------------------------------------+
| scrollback log (look, combat, MOTD)                   |
+-------------------------------------------------------+
| focus block (gig / combat / command in flight)        |
+-------------------------------------------------------+
| prompt preview (tokens while typing)                  |
+-------------------------------------------------------+
| > your command here_                                  |
+-------------------------------------------------------+
| hotkeys: Tab · F2-F7 · history                        |
+-------------------------------------------------------+
| sidebar (optional): PDA · Map · Help                  |
+-------------------------------------------------------+
```

## Function keys

| Key | Panel | Also |
|-----|-------|------|
| **Tab** | Complete command / cycle candidates | |
| **F2** | PDA — HP, posture, fatigue, stats, faction, implants | `pda` |
| **F3** | Help overlay on log | `help`, `h` |
| **F4** | Map | `map` |
| **F5** | Equipment | `equipment`, `eq` |
| **F6** | Collapse sidebar (clears stack) | |
| **F7** | Gigs / journal tracker | `gigs` |
| **F7** (login) | Clear stored credentials | |

Typing `map`, `pda`, `help`, `equipment`, `gigs` also opens the matching sidebar.

## Input

| Input | Action |
|-------|--------|
| **Enter** | Send command |
| **↑ / ↓** | Command history |
| **Ctrl+P / Ctrl+N** | History (alternate) |
| **Esc** | Restore draft after history browse |
| **Esc** | Close help overlay (when open) |

History is saved under `~/.config/cyber_mud/command_history.json`.

## Local commands (`/` prefix)

Processed by the client only—not sent to the server.

| Command | Purpose |
|---------|---------|
| `/theme list` | List visual themes |
| `/theme <id>` | Switch theme (matrix, tron, neon, …) |
| `/prompt set <template>` | Local prompt override with live preview |
| `/prompt template <name>` | CP2077-style templates (`ncpd`, `runner`, …) |
| `/prompt show` | Show expanded tokens |
| `/prompt reset` | Use server template again |
| `/reconnect` | Reconnect TCP + resend auth |
| `/clear` | Clear scrollback log |
| `/quit` | Exit the client application |

Tab completes `/clear`, `/theme`, `/prompt`, `/reconnect`.

## Login screen

- **Register / Login** modes  
- **Theme** dropdown (same as `/theme`)  
- Optional **PIN** quick unlock if credentials stored  
- Rotating MOTD tips on banner  

Stored credentials: `~/.config/cyber_mud/credentials.json` (encrypted, mode 0600).

## Prompt tokens (preview)

While typing, `#prompt_preview` expands tokens such as:

| Token | Meaning |
|-------|---------|
| `%n` | Character name |
| `%h` | HP |
| `%r` | Room |
| `%l` | Link / latency hint |
| `%c` | Combat indicator |
| `%v` | Vehicle |
| `%x` | XP |
| `%posture` | Rest posture (standing / sitting / lying / sleeping) |

Server `prompt` command and client `/prompt` share templates—see `prompt show` in game.

## NETRUN mode

When jacked in (`net`), the client switches theme and prompt. Only NETRUN-safe commands are sent; use `exit` or `/exit` to drop back to the street layer.

## Reconnect

On disconnect the client retries with backoff (up to 5 attempts). Manual:

```text
/reconnect
```

Link status bar shows connection state and round-trip hint.

## Themes & readability

- Environment colors (`look` / `scan`) follow the active theme  
- `/theme` redraws the log with new env palette  
- `lang zh` switches UI chrome strings; game text follows locale  

### Log channel legend

The scrollback prefixes help you scan output at a glance:

| Prefix | Channel | Examples |
|--------|---------|----------|
| `❯` | Your command (echo) | Typed line before server reply |
| `◎` | Environment | `look` / `scan` room header, exits, items, NPCs |
| `▸` | Movement | `go` direction line |
| `⚔` | Combat | Hits, CD, quickhack, flee, victory |
| `◆` | Gigs / quests | Objectives, stage progress, completion |
| `▲` | Progression | XP, level-up, street cred, proficiency |
| `💬` | Social | `say`, `talk`, presence enter/leave |
| `～` | Ambient (dim) | District tick, trauma, background flavor |
| `⚙` | System | Connection, client commands, NETRUN hints |
| `✗` | Error | Refused commands, disconnect |

A faint `───` rule separates new look blocks and combat rounds. Use `/clear` if the log gets noisy.

## Tips

```text
+-------------------------------------------------------+
|  RUNNER CHECKLIST                                     |
|  [x] ./run.sh + ./run.sh --client                     |
|  [x] register / login                                 |
|  [x] recall -> tutorial -> canteen sit/rest           |
|  [x] F3 help · F4 map · /clear if noisy               |
+-------------------------------------------------------+
```

Back to [Getting Started](GETTING_STARTED.md) · [Commands](COMMANDS.md).