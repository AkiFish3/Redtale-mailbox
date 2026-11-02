# docs/ — 服务器长期文档镜像

`D:\redtale-ops\*.md` 的**只读镜像**，由 `D:\redtale-ops\mail_sync_docs.py` 生成。
要改内容请改 srv 侧的原件，不要改这里——下一轮同步会整体覆盖。
（`docs/history/` 例外：那份是手写摘要，不从源文件生成。）

同步时间见每次提交说明；体量约 2.6 MB。

## 先看哪一份

| 想知道 | 看这个 | 体量 |
|---|---|---|
| 服务器要往哪走（定位 / 循环 / 经济 / 治理） | `_srv_PLAN.md` | 300 KB |
| 下一步排期与逐项决策（最活跃的一份） | `_srv_PLAN_NEXT.md` | 410 KB |
| 有哪些待办、卡在谁身上 | `_srv_BACKLOG.md` | 330 KB |
| 外部对标与实地测量（含数字、URL、结论） | `_srv_RESEARCH.md` | 840 KB |
| 踩过的坑（按现象查处置） | `_srv_LESSONS.md` | 56 KB |
| 本机规则 R1~Rn（不可被跨机规则包覆盖） | `_srv_RULES.md` | 160 KB |
| 每轮做了什么、为什么这么做 | `_srv_META_LOG.md` | 430 KB |
| 双方需求单台账 | `_srv_REQUESTS.md` | 27 KB |
| 当前收件箱待办 | `_srv_INBOX.md` | 3 KB |
| 前史：账号更替、北岸枫林 / 未寻旅境 | `history/前史-旧服与账号.md` | 9 KB |
| 旧账号时期跨机对话逐条摘要 | `mail/对话记录-srv侧.md` | 14 KB |
| Wiki 地志队列的三份笔记 | `_srv_S5_NOTES.md` / `_srv_S5_REQUESTS.md` / `_srv_S5_WIKI.md` | 15 KB |

## 体量与检索建议

四份大的（PLAN / PLAN_NEXT / RESEARCH / META_LOG）合计约 2 MB，**不要整份读**。
它们的内部结构一致：`## 第 N 节` 分主题，末尾有「变更记录」按日期追加。
建议先 `grep -n` 定位小节号或关键词，再按行号读那一段。

```
grep -n "^## " docs/_srv_PLAN.md            # 先看目录
grep -n "北岸枫林" docs/_srv_RESEARCH.md     # 按关键词定位
```

## 谁在写这些文件

| 队列 | 节奏 | 写的文件 |
|---|---|---|
| S2·规则炼金 | 每天 05:00 | `_srv_RULES.md`、`_srv_LESSONS.md` |
| S4·发展规划 | 每天 09:00 | `_srv_PLAN*.md`、`_srv_RESEARCH.md`、`_srv_BACKLOG.md`、`_srv_REQUESTS.md` |
| S5·地志 | 每天 05:10 | `_srv_S5_*.md`、`wiki/pages/mod-*.md` |

`_srv_META_LOG.md` 是三者共同的流水账，只追加。`docs/` 这一层不产生内容，只搬运。

## 已剔除的东西

- `*.bak48` / `*.bak50` 等历史备份：纯冗余，需要时在 srv 侧 `D:\redtale-ops\` 找。
- 任何口令字面值：构建时按 `data/mc.json` 的 `rcon_password` 与 `data/inbox_token` 做全量扫描，
  命中就替换成 `***`（当前唯一被打码的是 `wiki/mcauth.py` 里写死的 rcon 默认值）。
