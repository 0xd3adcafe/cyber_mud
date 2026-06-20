# 新手訓練場攻略

> **English:** [TUTORIAL.md](TUTORIAL.md) · 索引：[README.zh.md](README.zh.md)

```text
  ╔═══════════════════════════════════════════════════╗
  ║   訓 練 場   ·   安 全 區                        ║
  ║   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄   ║
  ║   教官 · 全息標靶 · 隔離駭入模擬                    ║
  ╚═══════════════════════════════════════════════════╝
```

隨時 `recall` 回中樞。訓練場與公開城區隔離。

## 中樞 — Training Yard (`tutorial`)

```text
              [ 簡報室 ]
                   │ up
    [戰鬥區]───[ 中樞 ]───[ 駭客區 ]
       │ north      │ east
   [靶場]        [軍械庫]
                 south
```

| 出口 | 房間 | 學習重點 |
|------|------|----------|
| `up` | Mission Briefing | gigs、stats、派系 |
| `north` | Combat Drill | attack、defend、flee |
| `east` | Netrun Sim | `net`、hack、RAM |
| `south` | Armory | equip、take、inventory |
| `west`（自軍械庫） | Trainee Canteen | sit、rest、eat、drink |
| `west`（自中樞） | *(畢業後)* Neon Square | 進入夜城 |

起手：

```text
look
scan
talk <教官>
```

## 1. 任務簡報室 (`tutorial_briefing`)

```text
  ┌─ 全息委託板 ─────────────────┐
  │  ◆ gigs · stats · recall      │
  └───────────────────────────────┘
```

```text
stats
gigs
journal
```

- **gigs** / **F7** — 街頭委託與追蹤  
- **stats** — 等級、XP、屬性點  
- **recall** — 回訓練場  

`down` 回中樞。

## 2. 軍械庫 (`tutorial_armory`)

```text
  ║ 武器架 │ 護甲 │ 義體示範包 ║
```

```text
take trainee_blade
inventory
equip trainee_blade
equipment
```

**F5** 開裝備側欄。`look trainee_blade` 看物品細節。

`north` 回中樞。`west` → **學員餐廳**。

## 2b. 學員餐廳 (`tutorial_canteen`)

```text
  ┌─ 販賣機 ──┐   ┌─ 長椅 ──┐
  │ eat drink │   │ sit rest│
  └───────────┘   └─────────┘
```

練習生活指令與消耗品：

```text
interact canteen_bench
sit
rest
look me
wake
```

- **interact canteen_bench** — 坐長椅（休息錨點）  
- **sit**／**rest** — 姿態與疲勞，隨世界 tick 緩解  
- **look me** — HP、疲勞、姿態  
- **wake**／**stand** — 移動前先起身（`go` 也會喚醒）  

也可向餐廳技師學 `eat`、`drink`、`use med_stim`。`east` 回軍械庫。

## 3. 戰鬥訓練區 (`tutorial_combat`)

```text
   ( o )  陪練機械人
   / | \  軟墊地面
```

| 步驟 | 指令 |
|------|------|
| 開戰 | `attack <目標>` 或 `punch patrol_dummy` |
| 防禦 | `defend` |
| 脫離 | `flee` |
| 遠程／刀械 | `shoot` / `slash` / `bash`（需裝備） |

即時戰鬥有冷卻 — 看狀態列與 hint。

分支：

- `north` → **靶場**  
- `east` → **障礙道**（`interact`、`scan`）  

## 4. 靶場 (`tutorial_range`)

```text
  ▄▄▄▄▄  全息射擊道  ▄▄▄▄▄
```

軍械庫裝備後：

```text
equip training_sidearm
attack patrol_dummy
```

`south` 回戰鬥區。

## 5. 障礙訓練道 (`tutorial_course`)

```text
  ► 掃描信標 ──► 互動閘門 ──► 標靶
```

```text
scan
interact <物件>
```

`west` 回戰鬥區。

## 6. 駭客模擬區 (`tutorial_net`)

```text
  ┌───┐ 綠色字元 │ RAM 監控
  │ > │ 教練監看
  └───┘
```

```text
net
```

NETRUN 內：

```text
look
probe
hack <節點>
status
exit
```

`exit` 回實體層。詳見 [COMMANDS.zh.md](COMMANDS.zh.md) § NETRUN。

`north` → **模擬義體診所**。

## 7. 模擬義體診所 (`tutorial_medbay`)

```text
take practice_cyber_kit
install <kit>
cyberware
use med_stim
```

`south` 回駭客區。

## 8. 畢業進城

訓練場中樞：

```text
go west
```

抵達 **Neon Square**。

```text
  ╔════════════════════════════════════╗
  ║  訓練完成 · 歡迎來到夜城            ║
  ╚════════════════════════════════════╝
```

建議接續：`map`、`scan`、`talk` 情報經紀人、有店鋪處 `shop`。