> **English（GitHub 預設）：** [WORLD_TOOLS.md](WORLD_TOOLS.md)

# 世界編寫工具

`tools/` 下的 CLI 工具，用於程序生成區域格點、人口覆蓋層與任務腳手架。請在專案根目錄執行（`./admin.sh`、`./run.sh` 會自動設定 `PYTHONPATH`）。

## 目錄

- [流程總覽](#流程總覽)
- [前置條件](#前置條件)
- [`generate_world.py`](#generate_worldpy)
- [`merge_world_grid.py`](#merge_world_gridpy)
- [`expand_world_population.py`](#expand_world_populationpy)
- [`quest_author.py`](#quest_authorpy)
- [`admin.sh`](#adminsh)
- [手寫 vs 程序生成](#手寫-vs-程序生成)
- [常見工作流](#常見工作流)

## 流程總覽

夜城規模內容分層建置：

```text
data/world.yaml（手寫核心＋樞紐）
        │
        ├─► merge_world_grid.py ──► 併入 8 區格點房（W.1／W.2）
        │
        ├─► expand_world_population.py ──► data/world_population.yaml（W.14／D.1）
        │         （載入時由 world/loader.py 合併）
        │
        └─► quests.yaml／商店／互動物（手寫）
```

| 層級 | 檔案 | 工具 |
|------|------|------|
| 房間（格點） | `data/world.yaml` `rooms:` | `generate_world.py`、`merge_world_grid.py` |
| NPC／物品（程序） | `data/world_population.yaml` | `expand_world_population.py` |
| 主線／樞紐／委託 | `data/world.yaml`、`data/quests.yaml` | 手動編輯＋`quest_author.py` |

## 前置條件

```bash
./setup.sh          # Python 3.13 虛擬環境
export PYTHONPATH=. # 或使用 ./admin.sh／./run.sh
```

重產世界資料後務必驗證：

```bash
./admin.sh validate
```

## `generate_world.py`

產生**單一矩形格點**的房間 YAML（一次一個區域）。

```bash
python -m tools.generate_world <district> <rows> <cols> [選項]
```

| 參數／旗標 | 說明 |
|------------|------|
| `district` | 寫入各房的區域 id（如 `watson`） |
| `rows`、`cols` | 格點行列數（≥ 1） |
| `--prefix` | 房間 id 前綴（預設區域名）→ `watson_3_2` |
| `-o`、`--output` | 寫入檔案，否則輸出到 stdout |
| `--start-room` | 輸出含 `start_room:`（預設左上角） |

**範例** — 預覽 4×4 Watson 格點：

```bash
python -m tools.generate_world watson 4 4
```

**範例** — 存成暫存檔審閱：

```bash
python -m tools.generate_world tyrell 6 6 -o /tmp/tyrell_grid.yaml
```

產出含 `district`、`grid_x`、`grid_y` 與四方 `exits`。敘事為模板字串；併入後可在 `data/world.yaml` 手改。

## `merge_world_grid.py`

將**八區格點**併入 `data/world.yaml`，並串接樞紐↔格點出口（目前交付：263 房）。

```bash
python -m tools.merge_world_grid [選項]
```

| 旗標 | 說明 |
|------|------|
| `-o`、`--output` | 目標世界檔（預設 `data/world.yaml`） |
| `--dry-run` | 只印房間數變化，不寫檔 |

**範例：**

```bash
python -m tools.merge_world_grid --dry-run
python -m tools.merge_world_grid
./admin.sh validate
```

區域大小與樞紐連線在 `tools/merge_world_grid.py` 設定（`GRID_SPECS`、`HUB_GRID_LINKS`、`EXTRA_HUB_ROOMS`）。`world.yaml` 裡**已存在**的房間 id 不會被覆蓋，只補缺少的格點。

**何時執行：** 擴充或重連區域格點（W.1／W.2）。日常內容工作較少需要。

## `expand_world_population.py`

產生**人口覆蓋層**——格點上的程序 NPC、區域戰利品與地上掉落。

```bash
python -m tools.expand_world_population [選項]
```

| 旗標 | 說明 |
|------|------|
| `--source` | 基礎世界檔（預設 `data/world.yaml`） |
| `-o`、`--output` | 覆蓋層路徑（預設 `data/world_population.yaml`） |
| `--dry-run` | 只印 npc／物品數量，不寫檔 |

**範例：**

```bash
python -m tools.expand_world_population --dry-run
python -m tools.expand_world_population
./admin.sh validate
```

stderr 會顯示合併後總數，例如 `npcs: 27 + 86 -> 113`。

**設定檔：** `tools/expand_world_population.py`

- `DISTRICT_NPC_COUNTS` — 各區 NPC 數量
- `DISTRICT_ARCHETYPES` — 各區原型輪替
- `ARCHETYPE_DEFS` — HP、敵意、`talk_key`、戰利品、巡邏
- `NEW_ITEMS` — 程序物品定義

修改原型 `talk_key` 後，須同步 `data/locale/en.yaml` 與 `zh.yaml` 的 `talk.*`。

**何時執行：** 格點房變更，或調整原型／數量／對話／戰利品。**不必**為 `world.yaml` 裡的手寫樞紐 NPC、任務或商店而重產。

載入合併：`world/loader.py` 讀取 `POPULATION_PATH`，將 `npcs`、`items`、`room_items` 疊到基礎世界上。

## `quest_author.py`

驗證與腳手架化 `data/quests.yaml`／`data/mature/quests_mature.yaml`（mature 內容包 submodule）的**多階段委託**。

透過 `./admin.sh quests` 呼叫（轉發至 `python -m tools.quest_author`）。

```bash
./admin.sh quests list
./admin.sh quests show <quest_id>
./admin.sh quests validate
./admin.sh quests npc <npc_id>
./admin.sh quests scaffold <quest_id> --giver broker --complete broker \
  --stage talk_npc:zone_warden --stage visit_room:tyrell_plaza \
  --stage talk_npc:broker --name-zh "樞紐座標" --reward-gold 80
```

| 子命令 | 用途 |
|--------|------|
| `list` | 所有委託摘要 |
| `show <id>` | 單一委託階段大綱 |
| `validate` | 檢查 NPC／房間是否存在、`complete_npc` 是否在 `talk_npc` 階段 |
| `npc <id>` | 某 NPC 的任務角色（發佈、階段目標、交件） |
| `scaffold` | 輸出新多階段委託的 YAML 範本 |

**階段格式：** `objective_type:target`，例如 `talk_npc:broker`、`visit_room:docks`、`give_npc:broker`、`hack_net:terminal`、`defeat_npc:thug`。

將 scaffold 輸出貼入 `data/quests.yaml`，再執行 `./admin.sh quests validate`。

## `admin.sh`

| 命令 | 用途 |
|------|------|
| `./admin.sh validate` | 世界圖、任務、mature 內容，再跑 `pytest tests/` |
| `./admin.sh quests …` | 任務編寫 CLI（見上） |
| `./admin.sh saves` | 列出存檔 |
| `./admin.sh delete-save <name>` | 刪除單一存檔 |

提交前以 `validate` 為驗收門檻。

## 手寫 vs 程序生成

| 放在 `data/world.yaml` | 放在覆蓋層／工具 |
|------------------------|------------------|
| `broker`、樞紐 NPC、主線錨點 | 格點 NPC（`watson_thug_0_3`） |
| 樞紐房（`tyrell_plaza`、`square`…） | 格點房模板敘事（可批量重產） |
| `data/quests.yaml` 委託 | 原型戰利品表 |
| 商店、互動物、主線 net 節點 | `gutter_blade`、`combat_scrap` 等程序物品 |

**原則：** 若手改 `world_population.yaml` 裡的程序 NPC，下次重產會**覆蓋**。永久角色請寫在 `world.yaml`，或改生成器規則。

## 常見工作流

### 新增原型對話（D.1）

1. 改 `tools/expand_world_population.py` 的 `ARCHETYPE_DEFS` `talk_key`
2. 在 `data/locale/en.yaml`、`zh.yaml` 加 `talk.<key>`
3. `python -m tools.expand_world_population`
4. `./admin.sh validate`

### 修復任務警告（D.2）

1. `./admin.sh quests validate`
2. 在 `quests.yaml` 補 `talk_npc` 交件階段或調整 `complete_npc_id`
3. `./admin.sh quests show <id>` 確認大綱

### 擴充單區格點（W.1）

1. 視需要調整 `tools/merge_world_grid.py` 的 `GRID_SPECS`
2. `python -m tools.merge_world_grid`
3. `python -m tools.expand_world_population`（重新分配 NPC 到格點）
4. `./admin.sh validate`

### 新增多階段委託

1. `./admin.sh quests scaffold my_gig --giver broker --complete broker --stage …`
2. 貼入 `data/quests.yaml`
3. `./admin.sh quests validate` && `./admin.sh validate`

---

另見：[WORLD.zh.md](WORLD.zh.md)（區域）、[PHASES.zh.md](PHASES.zh.md)（W.1–W.14、D.1–D.6）、[CONTRIBUTING.md](../CONTRIBUTING.md)。