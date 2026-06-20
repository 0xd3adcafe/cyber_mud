# Client 與快捷鍵

> **English:** [CLIENT.md](CLIENT.md) · 索引：[README.zh.md](README.zh.md)

```text
+-------------------------------------------------------+
|  TEXTUAL TUI · cyber_mud official interface           |
|  log | focus | prompt | hotkeys | sidebar stack       |
+-------------------------------------------------------+
```

Textual TUI · cyber_mud 正式介面

啟動：

```bash
./run.sh --client
```

## 版面

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

## 功能鍵

| 鍵 | 面板 | 等同 |
|----|------|------|
| **Tab** | 補全／輪替候選 | |
| **F2** | PDA（HP、姿態、疲勞、屬性、派系、義體） | `pda` |
| **F3** | 說明覆蓋 log | `help` |
| **F4** | 地圖 | `map` |
| **F5** | 裝備 | `equipment` |
| **F6** | 收合側欄 | |
| **F7** | 委託追蹤 | `gigs` |
| **F7**（登入） | 清除記憶帳密 | |

輸入 `map`、`pda`、`help` 等也會自動開側欄。

## 輸入

| 操作 | 作用 |
|------|------|
| **Enter** | 送出指令 |
| **↑↓** | 指令歷史 |
| **Esc** | 還原草稿／關閉說明層 |

歷史：`~/.config/cyber_mud/command_history.json`

## 本機指令（`/` 開頭）

| 指令 | 用途 |
|------|------|
| `/theme list` / `/theme <id>` | 主題 |
| `/prompt set\|template\|show\|reset` | 本機提示符預覽 |
| `/reconnect` | 手動重連 |
| `/clear` | 清除 log |
| `/quit` | 結束 client 程式 |

Tab 可補全 `/clear`、`/theme` 等。

## 登入畫面

註冊／登入、主題下拉、PIN 快速解鎖、MOTD 輪播提示。

憑證：`~/.config/cyber_mud/credentials.json`（加密）

## Prompt token

`%n` 名稱 · `%h` HP · `%r` 房間 · `%l` 連線 · `%c` 戰鬥 · `%v` 載具 · `%x` XP · `%posture` 姿態 等。

## NETRUN 模式

`net` 後切換主題與提示符；僅駭入層指令可用，`exit` 回街頭。

## 重連

斷線自動退避重試；手動 `/reconnect`。連線列顯示狀態與延遲。

## 小抄

```text
+-------------------------------------------------------+
|  RUNNER CHECKLIST                                     |
|  [x] ./run.sh + ./run.sh --client                     |
|  [x] register / login                                 |
|  [x] recall -> tutorial -> canteen sit/rest           |
|  [x] F3 help · F4 map · /clear if noisy               |
+-------------------------------------------------------+
```

[快速上手](GETTING_STARTED.zh.md) · [指令](COMMANDS.zh.md)