# 指令參考

> **English:** [COMMANDS.md](COMMANDS.md) · 索引：[README.zh.md](README.zh.md)

```text
╔══════════════════════════════════════════════════════════════╗
║  ◈ 指 令 矩 陣   ·   夜 城                                   ║
║  在 client 輸入 · Tab 補全 · help 即時列表                    ║
╚══════════════════════════════════════════════════════════════╝
```

遊戲內：`help` 或 **F3**。重複執行：`10 punch` 或 `punch.10`（間隔 0.5 秒）。

## 簡寫別名

| 別名 | 展開 |
|------|------|
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

## 帳號（Account）

| 指令 | 說明 |
|------|------|
| `register <名> <密碼>` | 註冊 |
| `login <名> <密碼>` | 登入 |
| `help` | 指令表（F3） |
| `quit` | 登出（連線保留，回登入畫面） |
| `lang [en\|zh]` | 顯示語系 |

## 探索（Explore）

| 指令 | 說明 |
|------|------|
| `look [目標]` | 房間或目標察看 |
| `go <方向>` | 移動 |
| `scan` | 掃描環境 |
| `map` | 地圖（F4） |
| `interact <物件>` | 環境互動 |
| `time` | 世界時間 |
| `recall` | 回訓練場 |

## 物品（Items）

`take` `drop` `inventory` `give` `appraise` `craft` `disassemble`（支援 `all` 批次）

## 裝備與消耗品（Gear）

`equip` `unequip` `equipment`（F5） `mod` `use` `eat` `drink`

## 義體（Cyberware）

`install` `cyberware` / `chrome` `uninstall`（診所）

## 住宅（Housing）

`rent` `home` `stash put|take`

## 交通（Travel）

`transit` `vehicles buy|select` `drive`

## 商店（Trade）

`shop` `buy` `sell`

## 社交（Social）

`talk` `say` `pledge <派系>` `learn`

## 戰鬥（Combat）

`attack` `shoot` `slash` `bash` `punch` `backstab` `defend` `flee` `quickhack`

即時戰鬥 — 注意冷卻與狀態列。

## NETRUN

`net` / `netrun` 進入駭入層；內層：`look` `scan` `probe` `hack` `status` `exit`。

## 委託（Gigs）

`gigs` / `journal`（F7）— `gigs accept <id>` 接案。

## 成長（Progression）

`stats` `talents` `improve`

## 面板（Panels）

`pda` / `status`（F2） `prompt set|show|template`

## 腦舞（Braindance）

`braindance <clip>` / `bd`

## 僅 Client（不送伺服器）

`/theme` `/prompt` `/reconnect` `/clear` `/quit` — 見 [CLIENT.zh.md](CLIENT.zh.md)。

完整英文表與細節：[COMMANDS.md](COMMANDS.md)。