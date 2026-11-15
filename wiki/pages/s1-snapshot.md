---
title: 服务器快照
role: admin
group: 管理员
order: 6
---

# 服务器快照

每小时/每日的运维快照链路：**读日志 → 生成 md → 上传资料库**。这一页说清它怎么跑、坏了看哪里。

## 链路三段

| 段 | 位置 | 干什么 |
|---|---|---|
| 采集 | `D:\redtale-ops\make_snapshot.ps1` | 增量读服务器日志，生成 `snapshots\赤物语-服务器快照-<stamp>.md` |
| 闸门 | `D:\redtale-ops\snapshot_gate.py` | 只读判断本轮要不要跑：`GATE NONE` / `QUIET` / `CHANGED` |
| 上传 | `D:\redtale-ops\upload_pending.py` | 把未上传的 md 传到资料库「赤物语服务器 / 运维快照 / YYYY-MM」，台账 `uploaded.json` |

## 采集怎么做到「不漏不重」

游标存在 `D:\redtale-ops\snapshot_state.json`：

- `lineOffset` — 上轮读到第几行，每轮只处理新增部分
- `logFile` — 上一次读的日志文件；文件名变了或文件变短 = 日志轮转，自动去最新 `.log.gz` 补读
- `seenCrashes` — 已报过的 crash-report / hs_err_pid，避免重复贴旧崩溃
- `mods` — 上轮 mod 清单，用于「配置差异」段做增减对比

所以快照是**增量**的，同一段日志不会出现两次。

## 每份快照长这样

固定五段：`元信息` / `崩溃` / `日志异常` / `配置差异` / `mod 清单`，末尾附 `测试结果` 勾选。

脱敏：IPv4 打码成 `<ip>`、UUID 打码成 `<uuid>`、主机名打码；日志异常段剔除聊天行（正则匹配 `: <玩家名> 内容`）。

## 常见故障

| 现象 | 原因 | 处理 |
|---|---|---|
| `mod 清单` 全是 `-`、版本 `?`、覆盖「读取全文 1-0 行」 | `-ServerDir` 指到了不存在的目录，采集空跑 | 检查 `make_snapshot.ps1` 的 `-ServerDir` 实际路径 |
| 在线人数 / TPS 恒为 `?` | 日志里没有 `/list` 和 TPS 输出，需要 RCON 才采得到 | 预期行为，不是故障 |
| 写 `D:\server` 却报路径不存在 | 旧服已整体迁到 `E:\server` | 见 `[[decisions]]` 里 S1 的待拍板条目 |

## 相关页面

- `[[runbook]]` — 启停、端口、RCON
- `[[backlog]]` — 运维行动清单
- `[[decisions]]` — 待拍板事项（含采集源路径的取舍）
