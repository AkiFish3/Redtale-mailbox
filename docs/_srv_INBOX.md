# 待拍板收件箱（S1–S5 共用）

> 一句话：**要 Aki 签字的事，只能通过 `wiki_inbox.py` 写进 wiki 的「待拍板」页，不能自己动手，也不能只写在回复里。**

## 为什么

以前队列把「需要拍板」的事写在回复末尾或 BACKLOG 里。回复会滚走，BACKLOG 越来越长，
Aki 要翻三份文档才知道有哪些事卡住了。现在统一到一个页面：打开 wiki → 管理员 → 待拍板，从上往下答。

## 怎么加

```bat
python D:\redtale-ops\wiki_inbox.py add --queue "S4·发展规划" --title "要不要给暮色加独立经济" ^
    --question "暮色现在的产出直接进主经济，是否拆分" ^
    --option "A|拆分，暮色独立货币" --option "B|维持统一" ^
    --default "维持统一" --link worlds
```

- `--queue` 写队列名（S1 快照 / S2 规则炼金 / S3 跨机信箱 / S4 发展规划 / S5 地志）
- `--title` 一句话，Aki 在列表里只看得到这个
- `--option` 可多次；`A|说明` 里的竖线会被换成空格
- `--default` 没人答时队列按这个走，**必须写**，否则队列会卡住
- `--link` 指向 wiki 里的页面 slug（可省）

## 怎么读

```bat
python D:\redtale-ops\wiki_inbox.py list --open          :: 只看没答的
python D:\redtale-ops\wiki_inbox.py list --queue S4 --json
```

`拍板：` 不是 `_待填_` 就是 Aki 的答复。

## 答完怎么收

```bat
python D:\redtale-ops\wiki_inbox.py resolve S4-20261102-1140 --note "按 A 拆分，已更新 BACKLOG T54" --by "S4·发展规划"
```

条目会被挪到「已定」区并留下指板内容与归档时间，页面上不会消失（可追溯）。

## 边界（重要）

| 允许 | 禁止 |
|---|---|
| 调 `wiki_inbox.py`（内部走 `POST /api/inbox`，带锁、去重、原子写） | 直接改 `E:\server-wiki\data\pages\decisions.md` |
| 队列读 `list --open` | 任何队列启动/重启 wiki（`python app.py`、`启动.bat`） |
| 一轮最多 3 条 | 同一件事重复登记（先 `list` 看一眼） |

`solve`/`add` 打印 `INBOX OK / DUP / SKIP`：
- `OK` 写进去了
- `DUP` 这个 key 已存在（正常，不要重试）
- `SKIP` 没写进去（wiki 没起且文件也写不了）→ 回复里写一行 `INBOX SKIP <原因>`，**不要重试超过一次，也不要改成直接改文件**

## 实现对照

| 部分 | 位置 |
|---|---|
| 服务端写入口 | `E:\server-wiki\app.py` → `inbox_add` / `inbox_resolve` / `POST /api/inbox` |
| 令牌 | `E:\server-wiki\data\inbox_token`（换令牌后队列自动生效，脚本每次现读） |
| 页面 | `E:\server-wiki\data\pages\decisions.md`（`## 待处理` / `## 已定` 两节，别删这两行标题） |
| 客户端 | `D:\redtale-ops\wiki_inbox.py` |

页面结构被改坏（少了 `## 待处理` 或 `## 已定`）时，写入会返回 `SKIP 缺少小节`，修好标题即可恢复。
