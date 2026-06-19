# cyber_mud

以原 **mud** 專案為藍本的**實作文件 fork**，用於在本機從零建立新的文字型多人冒險遊戲（MUD）。

已初始化 **MVP 程式骨架**（`look`／`go`／`help`／`quit` + 夜城起點世界），並保留完整實作文件。

## 文件索引

| 文件 | 用途 |
|------|------|
| [docs/WORLD.md](docs/WORLD.md) | **世界觀**：夜城設定、區域、派系、敘事錨點 |
| [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) | **主文件**：完整實作藍圖 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 系統架構與模組依賴 |
| [docs/BOOTSTRAP.md](docs/BOOTSTRAP.md) | 新專案啟動步驟（MVP） |
| [docs/PHASES.md](docs/PHASES.md) | 分階段實作清單（Phase 0–E） |

## 建議閱讀順序

1. [WORLD.md](docs/WORLD.md) — 夜城是什麼、玩家扮演誰  
2. [ARCHITECTURE.md](docs/ARCHITECTURE.md) — 整體長什麼樣  
3. [BOOTSTRAP.md](docs/BOOTSTRAP.md) — 先做出最小可玩版本  
4. [IMPLEMENTATION.md](docs/IMPLEMENTATION.md) — 各模組怎麼做  
5. [PHASES.md](docs/PHASES.md) — 排期與驗收

## 核心原則

1. **內建 Textual client** 為正式介面，不用第三方 MUD client。  
2. **世界放 `data/`**，程式只負責解讀。  
3. **一指令一模組**，`commands/` 註冊制。  
4. **繁體中文**為預設語系。

## 取得原專案原始碼（可選）

若你有權限存取原 OneDrive bare repo（在**有原始碼的電腦**上）：

```bash
git clone "/path/to/mud.git" mud
cd mud
./setup.sh
pytest tests/
```

原專案最後已知 commit 約 **`34d5525`**（含側欄裝備自動刷新）。  
本文件 fork 整理自此版本前的完整實作脈絡。

## 快速開始

```bash
cd cyber_mud
./setup.sh          # 首次：安裝依賴
./run.sh            # 啟動伺服器
./run.sh --client   # 另一終端：內建 TUI client
./admin.sh validate # 驗證世界 + 測試
```

依 [PHASES.md](docs/PHASES.md) 擴充登入、戰鬥、NETRUN 等功能。