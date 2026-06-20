# 快速上手

> **English:** [GETTING_STARTED.md](GETTING_STARTED.md) · 索引：[README.zh.md](README.zh.md)

```text
    ┌─────────────────────────────────────────┐
    │  ◈ 夜城神經連結                           │
    │  ─────────────────────────────────────  │
    │  > 連結待建立...                        │
    │  > 等待憑證                               │
    └─────────────────────────────────────────┘
```

## 1. 環境需求

- **Python 3.13**（見 repo `.python-version`）
- 終端機建議 80×24 以上
- 伺服器與 client 建議開兩個終端

## 2. 安裝與啟動

```bash
git clone https://github.com/0xd3adcafe/cyber_mud.git
cd cyber_mud
./setup.sh
```

**終端 A — 伺服器：**

```bash
./run.sh
```

**終端 B — 內建 client（正式遊玩方式）：**

```bash
./run.sh --client
```

```text
  ╔═══════════════════════════════════════╗
  ║  CLIENT ◄────TCP────► SERVER          ║
  ║  Textual TUI          asyncio 遊戲    ║
  ╚═══════════════════════════════════════╝
```

一般遊玩**不需要** MUDlet、TinTin++ 或 `nc`。

## 3. 建立帳號

MOTD 階段為訪客。首次請註冊：

```text
register <名稱> <密碼>
```

範例：

```text
register Vee hunter42
```

之後每次：

```text
login Vee hunter42
```

client 可用 **PIN** 記憶帳密（見 [CLIENT.zh.md](CLIENT.zh.md)）。

## 4. 前五分鐘

登入後建議依序：

```text
look
go north
scan
help
pda
```

| 指令 | 作用 |
|------|------|
| `look` / `l` | 房間、出口、物品、NPC |
| `go <方向>` / `n` `s` `e` `w` `u` `d` | 移動（含 **up** / **down**） |
| `scan` / `sc` | 掃描環境（client 著色） |
| `help` / `h` | 指令表（client **F3** 覆蓋層） |
| `pda` / `st` | 個人終端（**F2**） |

```text
      [ 你 ]
         │
    look ├─► 房間描述 + 出口
    go   └─► 換房
```

## 5. 新手訓練場

```text
recall
```

傳送到 **Training Yard** 安全區。完整路線：[TUTORIAL.zh.md](TUTORIAL.zh.md)。

準備進夜城：

```text
go west
```

（訓練場 → **Neon Square**）

## 6. 語系

預設英文：

```text
lang       # 顯示目前語系
lang en    # 英文
lang zh    # 繁體中文
```

## 7. 卡關時

| 狀況 | 試試 |
|------|------|
| 不懂指令 | `help` 或 [COMMANDS.zh.md](COMMANDS.zh.md) |
| 迷路 | `recall` 或 `map`（**F4**） |
| 斷線 | client `/reconnect` 或重開 client |
| log 太亂 | `/clear`（僅 client） |

下一步：[新手訓練場](TUTORIAL.zh.md) → [指令參考](COMMANDS.zh.md) → [Client](CLIENT.zh.md)。