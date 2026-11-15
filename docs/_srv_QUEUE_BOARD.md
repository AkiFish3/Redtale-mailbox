# 队列协作板（srv 全队列共用）

> **唯一写入点**：`D:\redtale-ops\_srv_QUEUE_BOARD.md`
> **镜像**：`_mailbox/docs/_srv_QUEUE_BOARD.md`（`mail_sync_docs.py` 生成，dev 侧只读）
> **建立**：2026-11-15 10:30 · 起因：S7 上线后队列间没有公共交接面，状态只存在于各自上下文里，跑完就丢。

这个文件解决一件事：**让 S1~S7 在互相看不见对方上下文的情况下，仍能知道「别人做到哪了、我在等谁」。**

---

## 0. 三条规矩

1. **开工先读**：每轮开始读 §3 最后 5 条 + §4 全部 + §5 全部。不超过 1 分钟。
2. **收工必写**：在 §3 **末尾追加**一条（≤3 行），格式见 §6。没有产出也要写「无进展 + 原因」。
3. **只追加，不编辑别人的行**。要纠正某人某条，追加一条 `更正：<原条目时间> …`，不删原文、不改原文。

配套：`Q-` 号由提出者自己取下一个空号，只增不重排；`B-` 号同理（§5）。条目超过 60 天由 S4 归档到 `_srv_META_LOG.md`。

---

## 1. 花名册

| 队列 | 节奏 | 运行目录 | 职责 | 主要写入 | 不碰 |
|---|---|---|---|---|---|
| S1·快照采集 | 每天 05:30 | `D:\redtale-ops` | 生成服务器快照并推送 | `snapshots/` | 其它 |
| S2·规则炼金 | 每天 05:00 | `D:\redtale-ops` | 日志现象 → 规则 / 流水账 | `_srv_RULES.md`、`_srv_LESSONS.md` | 规划类文档 |
| S3·跨机信箱 | 每 8 小时 | `D:\redtale-ops` | 收发信、需求单、规则包 | `mail/`、`_srv_MAIL_STATE.json` | `docs/`、`wiki/` |
| S4·发展规划 | 每天 09:00 | `D:\redtale-ops` | 外部对标 → 规划 / 研究 / 待办 | `_srv_PLAN*.md`、`_srv_RESEARCH.md`、`_srv_BACKLOG.md`、`_srv_REQUESTS.md` | 服务器本体 |
| S5·地志 | 每小时 | `E:\server-wiki` | Wiki 模组页更新 | `_srv_S5_*.md`、`wiki/pages/mod-*.md` | 其它页面 |
| S6·签到与派猫猫 | 每天 09:05 | `D:\redtale-ops` | WorkBuddy 每日签到 + 旅行 | 仅 `%USERPROFILE%\.workbuddy\` 下的凭据 | 服务器、仓库 |
| S7·RedtaleProject | 每天 10:00 | `E:\RedtaleProject` | MMO/Eco 系能力移植 1.21.1 NeoForge | `E:\RedtaleProject`、`E:\server-test` | **正式服 `E:\server-1.21.1`** |

dev 机队列不在这张表里，它们通过信箱（S3）与本板镜像通信。

> 接入状态（2026-11-15）：**S7 / S3 / S4 的自动化提示已接入本板**（开工读、收工写）。
> S1 / S2 / S5 职责窄、只写各自的文档，暂时只读不改；S6 只碰签到凭据，与本板无关。
> 它们若要写，直接按 §6 追加即可，不需要改提示。

---

## 2. 会互相踩的四件事

| 冲突面 | 具体 | 约定 |
|---|---|---|
| **git push** | 多个队列同时 push `_mailbox` 会撞 | push 前先 `pull --rebase --autostash`；失败就 `SKIP` 一行，下一轮再来，**不要强推** |
| **内存** | 正式服常驻 + S7 的 `E:\server-test`（`-Xmx4G`） | S7 跑完测试服**必须停**；S1 05:30 开工前若发现测试服在跑，写 §5 记一条，不要自己去杀 |
| **时间贴脸** | S4 09:00 / S6 09:05 / S7 10:00 / S5 每小时 | 相邻队列不许读对方"刚写了一半"的文件；以文件 mtime 早于自己开工时刻为准 |
| **谁改谁的文件** | `_srv_META_LOG.md` 是公共流水账 | 只追加，不改行；发现自己被覆盖，写 §3 一条并 @ 对方 |

---

## 3. 本轮状态（追加区，最新在最下）

格式：`- YYYY-MM-DD HH:mm · S? · 做了什么 · 留下什么 · 下一步`

- 2026-11-15 10:30 · 协作板 · 建立本文件，接入 `mail_sync_docs.py` 镜像与 `PROTOCOL.md` §13 · 本板 · 各队列下轮起按 §6 追加
- 2026-11-15 10:30 · S7 · 首轮 10:00 已执行（产出见 `E:\RedtaleProject`）· 本条为代记，**请 S7 下轮按 §6 格式补一行自己的**· 待 Aki 拍 Q-002
- 2026-11-15 10:45 · 协作板 · 查清 1.20.1「康普茶 × 星芒 = 5 分钟急迫 VIII」的机制（时长取 max、等级 +6/次、封顶 7）；1.21.1 不可复现（星芒重写、康普茶缩到 60 秒 II）。结论写进 `E:\RedtaleProject\PLAN.md` §12 · 该文件 · S7 下轮读 §12 时一并纳入投放层规则
- 2026-11-15 10:55 · 协作板 · **Q-001 结案**：Aki 定「急迫=攻速」为玩法特性，D19 新写入 `PLAN.md`（默认 0.10/级、`soft_cap=0` 不饱和、只留 1 tick 物理地板防除零）；`DAMAGE-PIPELINE.md` §4.2/§4.3 与 `ATTRIBUTE-REGISTRY.md` §4 同步；新开 Q-006（属性 64/80）、Q-007（测试服加玩法 mod） · 上述三文件 + wiki 收件箱 · S7 下轮先把攻速 mixin 与 `/redtale attr` 一起做，用 Q-007 的 jar 验收

- 2026-11-15 11:30 · S7 · 拍板 4 项落地：①构建改「镜像源 + server-srg 直编」，`gradle build --offline` **BUILD SUCCESSFUL 19s**（`docs/BUILD.md`），产物进测试服 `Done (2.353s)`；②测试服已加 6 个玩法 jar（BetterCombat/playeranim/Farmer's Respite/FarmersDelight/SimplySwords/fzzy_config）全绿；③属性定 80 条（16 条预留）；④tooltip 口径 = 单次伤害 + 攻速，DPS 客户端开关（D20）· `E:////RedtaleProject`（PLAN/DAMAGE-PIPELINE/ATTRIBUTE-REGISTRY/BUILD/ROUND-M0）· S7 下轮进 M1：80 条属性注册 + `/redtale attr` + 攻速 mixin
- 2026-11-15 11:42 · 协作板 · **运维坑**：`wiki_inbox.py resolve` 在本机 hang（`file_resolve` 里那段懒回溯正则 + 8080 假活时 `wiki_alive()` 判真），且被 kill 会留下 `.inbox.lock` 残锁（`E:////server-wiki/data/.inbox.lock`，内容是 pid，清前先确认进程已死）。绕行脚本 `C:////Users/AkiFish3/WorkBuddy/2026-10-24-05-43-33/resolve_inbox.py`（填拍板）+ `archive_inbox.py`（移入 §已定），同样持锁 + 原子写。**不要自己启 wiki 服务**。wiki 假活本身已由 S5 登记（`S5-20261115-113605`）
- 2026-11-15 12:08 · S7 · 功能面缺口审计（第二轮）：新增 `docs/GAP-AUDIT.md`——上游漏 7 项（词条/工作台/矿脉/消耗品/专业/技能树/刷怪替换），与已装 mod 撞车 9 处（spell_power 属性、spell_engine 吃 XP 等级、伤害乘区、三套饰品、lootr、enchantmentdisabler、经济缺失、owo GUI）。开 Q-009~Q-011 · `E://RedtaleProject//docs//GAP-AUDIT.md` · 等 Aki 拍 3 条后进 M1
- 2026-11-15 12:50 · S7 · 10 条拍板全落地：**D21~D31** 写进 `PLAN.md`。新增 `docs/ITEM-MODEL.md`（白板化/词条/消耗品修理/不做工作台与矿脉）与 `docs/SKILL-TREE.md`（结构+三例+schema）；`docs/DAMAGE-PIPELINE.md` §12 兼容层（只读桥接+tag 白名单+拆除检查单）；`GAP-AUDIT.md` §5 裁决表；M2/M6/M7 出口条件同步。开 Q-012（附魔强化走哪条）· `E://RedtaleProject` · S7 下轮进 M1（属性注册 + `/redtale attr` + 攻速 mixin），M1 里先做白板化验证件

---

## 4. 待拍板（Q 编号，等人，不是等机器）

**每个 `Q-` 号必须在 wiki 待拍板有一条对应条目，标题前缀写 `[Q-00x]`**（`wiki_inbox.py add`）。板是队列内部视图，wiki 才是 Aki 真正的收件箱；两边靠编号对齐，Aki 在 wiki 拍完，提出者回来在本表该行末尾追加 `已答复：<结论>`。

| 号 | 提出 | 问题 | 默认（无人否决就按这个走） |
|---|---|---|---|
| Q-001 | S7 | 1.21.1 上「急迫是否算攻速」按哪个口径：`haste_attack_speed_per_level = 0`（原版行为）还是 `0.10`（复刻 1.20.1 手感） | **已答复（2026-11-15 10:51，Aki）：按 0.10 默认开启，`soft_cap` 保持 0 不饱和。「急迫堆攻速」定性为该服玩法特性，不做平衡钳制。已落 `PLAN.md` D19 + `DAMAGE-PIPELINE.md` §4.2.3** |
| Q-002 | S7 | M0 骨架是否照「14 基底物品 + 64 属性 + 通用 `ContentData` + 32 效果原语」开工 | 照此开工 |
| Q-003 | S1/S3 | `E:\server-wiki\mcauth.py:27` 把 rcon 口令写死为默认值，镜像里已打码成 `***`，**源文件未改** | 改为读 `data/mc.json`，需 Aki 手动改（队列不动正式服配置） |
| Q-004 | S3 | `mail_sync_docs.py sync` 是否挂进 S1 每日 05:30 自动跑 | **挂**，避免文档镜像靠人手动同步 |
| Q-005 | S6 | 首次签到需一次网页授权（`web_auth.py` 贴 cURL / Cookie），凭据通道 A 被客户端独占 | 等 Aki 贴一次，之后长期有效 |
| Q-006 | S7 | `[Q-006]` 属性注册表一次注册多少条：64（够用，以后加要换 jar）还是 80（留余量，多出的不上面板） | **已答复（2026-11-15 11:22，Aki）：80**。`ATTRIBUTE-REGISTRY.md` §2F 已补 16 条预留（65~80，注册不使用、不上面板） |
| Q-007 | S7 | `[Q-007]` 测试服要不要复制正式服同版本玩法 jar 来验证急迫→攻速联动 | **已答复（2026-11-15 11:22，Aki）：复制**。已复制 6 个 jar 进 `E:/server-test/mods`（BetterCombat + player-animation-lib + Farmer's Respite + FarmersDelight + SimplySwords + fzzy_config），实测 `Done (2.353s)` 无缺依赖、已停服 |
| Q-008 | S7 | `[Q-008]` 暴击双轨（近战 `critical_strike_*` / 法术 `spell_critical_strike_*`）保留还是合并；基值是否照搬上游（暴击倍率 2.0、格挡强度 25） | **保留双轨 + 照搬基值**（S7 默认，M2 实装前可推翻） |
| Q-009 | S7 | `[Q-009]` `spell_power` 已装并在册 19 条属性，与我们自建 16 条语义重叠、ID 不同，配置无开关 | **已答复（2026-11-15 12:45，Aki）：spell_engine 系列上线后大概率移除，但先做兼容**。落 D31：只读桥接（按 ResourceLocation 查 AttributeMap），`compat/` 包可整体拆除；乘区只作用于 `redtale_project:*` 的 DamageType |
| Q-010 | S7 | `[Q-010]` `spell_engine` 拿原版经验等级当法术书门槛/花费，与 M7 等级系统冲突 | **已答复：保留原版 XP 给它的法术书用，我们的等级独立**。不接管它的饥饿消耗与 `haste_affects_cooldown` |
| Q-011 | S7 | `[Q-011]` 上游 7 项未排期功能怎么取舍 | **已答复**：做 词条(D22)/消耗品修理(D23)/专业(D24,后置)/技能树(D25)/刷怪替换(D26)；**不做** 工作台与矿脉(D27)；战利品箱复用 bountiful+lootr。另 **装备白板化**(D21)、**Curios 可选**(D29)、**owo GUI**(D30)、**经济可选桥接**(D28) |
| Q-012 | S7 | `[Q-012]` M4 原版附魔强化走哪条：用已装 `enchantmentdisabler` 的 `maxLevels` 直接抬原版上限（改配置，几分钟），还是照原计划另做「超级锋利/超级保护」新附魔（schema+datapack+互斥，几天） | **抬原版上限**（更便宜，M4 前再确认）；新附魔只用于原版组件表达不了的效果 |

---

## 5. 阻塞（互相等）

格式：`B-xx · 谁在等谁 · 等什么 · 从什么时候`

（空）

---

## 6. 追加模板

```markdown
- 2026-11-15 10:00 · S7 · 补完 M0 的 DataComponent 注册骨架，编译通过 · `src/main/java/.../ContentData.java`、`PLAN.md` §里程碑 · 下轮做 14 基底物品
```

要求：

- **一行说完**，多细节写到自己的文档里，这里只留指针。
- 「留下什么」必须给**路径或命令**，不给「已完成」这种无法验证的话。
- 「下一步」是给下一个队列看的，不是给自己看的。
- 需要别人动手，去 §5 开一条 `B-`，不要只在 §3 里抱怨。
- 需要人拍板，去 §4 开一条 `Q-`，写清「默认怎么走」——默认项是为了让队列不被卡住。
