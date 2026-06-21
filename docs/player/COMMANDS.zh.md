# 指令參考

> **English:** [COMMANDS.md](COMMANDS.md) · 索引：[README.zh.md](README.zh.md)

```text
+-------------------------------------------------------+
|  COMMAND MATRIX  ·  NIGHT CITY                        |
|  type in client · Tab complete · help (F3)            |
+-------------------------------------------------------+
```

指令矩陣 · 夜城 — 在 client 輸入，Tab 補全，**F3** 即時列表。

遊戲內：`help` 或 **F3**。重複執行：`10 punch` 或 `punch.10`（間隔 0.5 秒）。

## 目錄

- [簡寫別名](#簡寫別名)
- [帳號（Account）](#帳號account)
- [探索（Explore）](#探索explore)
- [生活與生命徵象（Life & vitals）](#生活與生命徵象life-vitals)
- [物品（Items）](#物品items)
- [裝備與消耗品（Gear）](#裝備與消耗品gear)
- [義體（Cyberware）](#義體cyberware)
- [住宅（Housing）](#住宅housing)
- [交通（Travel）](#交通travel)
- [商店（Trade）](#商店trade)
- [社交（Social）](#社交social)
- [戰鬥（Combat）](#戰鬥combat)
- [NETRUN](#netrun)
- [委託（Gigs）](#委託gigs)
- [成長（Progression）](#成長progression)
- [面板（Panels）](#面板panels)
- [腦舞（Braindance）](#腦舞braindance)
- [僅 Client（不送伺服器）](#僅-client不送伺服器)

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

## 生活與生命徵象（Life & vitals）

| 指令 | 說明 |
|------|------|
| `sit` | 坐下（休息姿態；戰鬥／NETRUN 中不可用） |
| `stand` | 站起（清除休息姿態） |
| `lie` | 躺下（休息時 HP 回復較佳） |
| `rest` | 休息（站立時會先坐下；tick 降低疲勞） |
| `sleep` | 睡眠（需安全房間或休息錨點；HP／RAM 回復最佳） |
| `wake` | 從休息或睡眠中醒來 |

休息／睡眠可加成 tick 回血（躺／睡時另有 RAM 回復）。訓練場餐廳長椅、公寓床、診所病床、夜總會包廂等可用 `interact`。移動、說話或進入戰鬥會喚醒。`look me` 顯示姿態與疲勞；PDA 有生活狀態列。

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
