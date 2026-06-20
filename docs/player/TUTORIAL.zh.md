# 新手訓練場攻略

> **English:** [TUTORIAL.md](TUTORIAL.md) · 索引：[README.zh.md](README.zh.md)

```text
+-------------------------------------------------------+
|  TRAINING YARD  ·  SECURE                             |
|  instructors · holo targets · isolated net            |
+-------------------------------------------------------+
```

訓練場 · 安全區 — 教官、全息標靶、隔離駭入模擬。

隨時 `recall` 回中樞。訓練場與公開城區隔離。

## 建議路線

| 步驟 | 房間 | 練習 |
|------|------|------|
| 1 | Training Yard | `look`、`talk` 教官 |
| 2 | Armory → Canteen | `equip`、`interact canteen_bench`、`sit`、`rest`、`look me` |
| 3 | Combat Drill | `attack`、`defend`、`flee` |
| 4 | Netrun Sim | `net`、`hack`、`exit` |
| 5 | Neon Square | `map`、`gigs`、探索 |

生活指令（`sit`、`rest`、`sleep`、`wake`）在 **學員餐廳** 教學 — 見 §2b。完整說明：[COMMANDS.zh.md](COMMANDS.zh.md) § 生活與生命徵象。

## 中樞 — Training Yard (`tutorial`)

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

教官全息會提示：軍械庫西邊餐廳可練 `sit`／`rest`。

## 1. 任務簡報室 (`tutorial_briefing`)

```text
+-------------------------------------------------------+
|  HOLO BOARD                                           |
|  * gigs   * stats   * recall                          |
+-------------------------------------------------------+
```

全息委託板

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
+-------------------------------------------------------+
|  weapon rack  |  armor  |  cyber kit                  |
+-------------------------------------------------------+
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
+-------------------------------------------------------+
|  [ VENDING ]              [ BENCH ]                   |
|   eat / drink              sit / rest                 |
+-------------------------------------------------------+
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
- **look me** — HP、疲勞、姿態（**F2** PDA 亦有）  
- **wake**／**stand** — 移動前先起身（`go` 也會喚醒）  

也可向餐廳技師學 `eat`、`drink`、`use med_stim`。`east` 回軍械庫。

## 3. 戰鬥訓練區 (`tutorial_combat`)

```text
+-------------------------------------------------------+
|      ( o )  sparring drone                            |
|      / | \  padded floor                              |
+-------------------------------------------------------+
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
+-------------------------------------------------------+
|  #####  holo lanes  #####                             |
+-------------------------------------------------------+
```

軍械庫裝備後：

```text
equip training_sidearm
attack patrol_dummy
```

`south` 回戰鬥區。

## 5. 障礙訓練道 (`tutorial_course`)

```text
+-------------------------------------------------------+
|  scan beacon --> interact gate --> target dummy       |
+-------------------------------------------------------+
```

```text
scan
interact <物件>
```

`west` 回戰鬥區。

## 6. 駭客模擬區 (`tutorial_net`)

```text
+-------------------------------------------------------+
|  [ > ]  green glyphs  |  RAM meter                    |
|         coach watching                                |
+-------------------------------------------------------+
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
+-------------------------------------------------------+
|  JACK-OUT COMPLETE  ·  WELCOME TO NIGHT CITY          |
+-------------------------------------------------------+
```

訓練完成 · 歡迎來到夜城

建議接續：`map`、`scan`、`talk` 情報經紀人、有店鋪處 `shop`。

## 9. 訓練場外的休息

租公寓或找到安全房間後：

| 地點 | 方式 | 指令 |
|------|------|------|
| `watson_flat` | 廣場 `rent`、`home` | `sleep`、`interact flat_bunk` |
| `ripper_clinic` | 廣場 `go west` | `rest`、`interact clinic_bed` |
| `kabuki_lounge` | 經小巷 | `rest`、包廂互動 |

移動、`say`、`talk` 或戰鬥會喚醒。見 [COMMANDS.zh.md](COMMANDS.zh.md) § 生活與生命徵象。