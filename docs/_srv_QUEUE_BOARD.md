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
| S7·RedtaleProject | 每小时 | `E:\RedtaleProject` | MMO/Eco 系能力移植 1.21.1 NeoForge，**兼 S8 的派单与验收** | `E:\RedtaleProject`、`E:\server-test` | **正式服 `E:\server-1.21.1`** |
| S8·RedtaleProject 执行 | 每小时（与 S7 同频） | `E:\RedtaleProject` | **只做** `docs\TASKS.md` §5 卡板里已派单的卡：写码、自测、改卡状态 | 自己那张卡独占的 `.java`、`.queue\build.lock` | `docs\TASKS.md` 规则区、`docs\CONTRACTS.md`、`PLAN.md`、`core/attr`、`core/math/Settle.java`、`core/damage`、`build.gradle`、任何服务器 |

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
- 2026-11-15 12:56 · S7 · **Q-012 结案**：Aki 答「另外做，因为本质上是为了测自制的附魔接口」→ 新开 D32（自研附魔接口，不抬 `enchantmentdisabler` 上限），新增 `docs/ENCHANT-API.md`（四层接口 / 30 个 effect 组件全表 javap 实测 / 单组件 `redtale_project:scripted` / V1~V11 验收矩阵 / 3 条开工风险）；`PLAN.md` M4 出口条件与 §10 组件名同步纠正（`block_break_speed` 是属性不是组件）；`GAP-AUDIT.md` B7 结案 · `E://RedtaleProject//docs//ENCHANT-API.md` · S7 下轮仍进 M1；**M4 开工第一件事是验 R1（`ENCHANTMENT_ENTITY_EFFECT_TYPE` 能否 `RegisterEvent`）与 R2（生成物落可 reload 的 datapack）**，两条不过则 §5 热更表作废
- 2026-11-15 22:11 · 协作板 · Aki 问「能否多开队列用免费模型辅助开发」→ 评估：可并行面只有内容 JSON5 / datapack 校验 / `tools/` 脚本；**java 主线、`gradle build`、测试服启停、接口契约不可并行**（共享 `settle()`/注册表、单 build 目录、单测试服实例）。**决定：本阶段不加队列**——M1（80 属性注册 + `/redtale attr` + 攻速 mixin）是单线程活，队列多了只会各自理解一套接口。M1 出口后再议：优先「S7 改 3:1 混跑（每 4 轮 1 轮做内容）」而不是新开队列，额度省一半；真要独立队列再上 S8·内容数据（独占 `data-src/`、只读 `docs/CONTRACTS.md`、不碰 `src/main/java`） · 本板 · 各队列**不要自行提议新开队列**，要开先走 §4
- 2026-11-15 23:05 · 协作板 · **Aki 拍板上 S8（推翻本板 22:11 的「先不建」）**，机制 = 「S7 每轮派一张小卡，S8 做；没做完当长期任务续做」。新增 `E:\RedtaleProject\docs\TASKS.md`（状态机 OPEN→DOING→DONE→VERIFIED/BOUNCED、在制品 ≤3、独占文件、单卡 ≤1 类/200 行、三振拆卡、只加不删、`NEED-S7` 出口）+ `docs\CONTRACTS.md`（冻结 id/字段/路径，S8 只读）；S8 自动化已建（每小时，cwd `E:/RedtaleProject`），S7 提示词已改写为「派单 + 验收 + 自己推进」。首批派 **T-0001 weapon_attributes 生成器**、**T-0002 `/redtale content list`**。防冲突只靠两条：**卡的独占文件在 VERIFIED 前 S7 不碰** + **`.queue\build.lock`**（取不到锁就跳过构建） · `E://RedtaleProject//docs//TASKS.md`、`CONTRACTS.md` · S7 下轮开局先验收 `[DONE]`、再看要不要派 C2~C6
- 2026-11-15 20:12 · S7 · M1 第一步落地：80 条属性成表，66 条自建注册成功并挂到 99 个 EntityType（6534 处），`/redtale attr <属性> [目标]` 三乘区拆解 + `attr list`；实测原版 `/attribute` 能读写 `redtale_project:*`、拆解 (3+5)×1.25×1.4=14 与实际值一致、别人加的 `minecraft:effect.speed` 也被列出 · `E:\RedtaleProject\docs\ROUND-M1-ATTR.md`（证据）、`src/main/java/com/redtale/project/core/attr/`、`tools/gen_attr_lang.py` · 下轮：`StatValue`+`settle()` 单测 → `attack_speed.json5` → 第一个 mixin（`getCurrentItemAttackStrengthDelay`，需先单独验 mixin 配置能不能进 jar）
- 2026-11-15 21:09 · S7 · M1 第二步落地：`core/math/` 数值核心 + `gradle selftest` **28/28 PASS**；`attack_speed.json5`/`damage.json5` 落地并可热重载（`soft_cap=4` → 1024 次/秒实测 5 tick）；第一个 mixin 进 jar 并生效（导出类含 `handler$zdi000$…applyAttackSpeedRules`）。**修掉急迫双计**：1.21.1 原版 `DIG_SPEED` 自带 `ATTACK_SPEED +0.1/级`，去重后急迫 II 实测 4→4.8（原 5.76）· `docs/ROUND-M3.md`、`PLAN.md` §13.5、`src/main/java/com/redtale/project/{core/math,core/attr,mixin}/` · 下轮：`settle()` 接 `LivingIncomingDamageEvent`；M2 起步（`ContentData` + 白板化）
- 2026-11-15 22:08 · S7 · **M1 收尾：L2 伤害乘区上线**。`core/damage/`（白名单 `MultiplierRules` / `DamageLayer` 在 `LivingIncomingDamageEvent` LOWEST 上乘因子 / `DamageTrace`）+ 自建 datapack 伤害类型 `redtale_project:verification_strike` + `/redtale damage|probe|check`；`damage.json5` 新增 `multiplier` 段。实测同一数值 **10 / 12 / 10**（自建类型+无属性 ×1.0；+`physical_damage 0.2` → ×1.2；`minecraft:generic` 放行），selftest 28 → **36 PASS** · `E:\RedtaleProject\docs\ROUND-M4-DAMAGE.md`、`src/main/java/com/redtale/project/core/damage/`、`PLAN.md` §13 R4/§13.6/§13.7 · 下轮：M2 起步（`ContentData` 组件 + 14 基底物品 + 白板化验证件 + tooltip D20）；新增 Q-014（属性值口径 0.2 = +20% 还是 20 = +20%）
- 2026-11-15 22:24 · S7 · **M2 第一步落地**：装备不再注册新 `Item`，走「原版 Item + 通用 `ContentData` 组件」；14 基底（剑/斧/锤/匕首/弓…）；**白板化实测 `3 → 20 → 0`**（原版皮革胸甲 3、写 20 的胸甲 20、0 属性布袍 0，靠 `+0` 占位堵住回落）；tooltip 按 D20 出「≈ 单次伤害 /次 + 攻速 tick·次/秒」，与结算共用 `settle()`；selftest 36 → **46 PASS** · `E:\RedtaleProject\docs\ROUND-R5-ITEMS.md`、`src/main/java/com/redtale/project/items/`、`PLAN.md` §13.8 · 下轮：`weapon_attributes` datapack 生成器（BetterCombat 挥得动）+ 条件乘区（pve/pvp/undead）；Q-014 仍按「小数」默认走
- 2026-11-15 23:52 · S7 · **双队列首轮 + 条件乘区上线**。派单：T-0001（`weapon_attributes` 生成器，已代 S8 解包 BetterCombat 取真实 schema 贴进卡）、T-0002（`/redtale content list`）、新增 **T-0003**（词条定义/词条池解析器，D22 第一层）；在制品 3/3。验收：无 `[DONE]` 卡（S8 尚未领卡）。自研：`core/damage/TargetClass` + `MultiplierRules.conditionalAttributes` + `DamageLayer.sumConditional`，实测牛 ×1.2 / 亡灵 ×1.5 / pvp 对怪 ×1.0，selftest 46 → **55 PASS**。**新发现缺口**：`weapon_attributes` 只有 `ContentData` 字段、没设成 BetterCombat 物品组件 → 生成的 datapack 不会被物品自动用上（已记 `PLAN.md` §13.10 R7-1）· `E:\RedtaleProject\docs\ROUND-R6-COND.md`、`docs/TASKS.md` §5、`PLAN.md` §13 R6/§13.10 · 下一步：S8 领卡后先验 T-0001 的 datapack 落地；R7 做 `weapon_attributes` 组件接线 + `CriticalHitEvent`
- 2026-11-15 23:59 · S8 · 首轮领 **T-0001**（`weapon_attributes` 生成器）→ `[DONE]`：新建 `WeaponAttributesGenerator.generateAll()`，`RedtaleCore.reload()` 第 121 行后追加 2 行（+1 行 import，未改已有行）跑生成；`gradle build --offline` 退出码 0，离线自测（合成 ConfigFile/ItemContent 直调）written=1、目标 JSON 合法、`bettercombat:claymore` 被跳过、缺定义仅告警不崩、`pack.mcmeta` 已存在不覆盖 · `src/main/java/com/redtale/project/items/WeaponAttributesGenerator.java`、`core/RedtaleCore.java`（3 行）、`docs/TASKS.md` · 下一步：S7 验 T-0001 第 3 条（起测试服 + `/datapack list`）；注意 `PLAN.md` §13.10 R7-1（组件未接线，光有 datapack 物品还用不上）

- 2026-11-16 00:50 · S7 · **验收 T-0001 → VERIFIED**（测试服 3 轮 `Done 2.3~2.5s`，第 3 条 3/3 过）；**派 T-0004**（附魔 schema→datapack 生成器，D32 的 L1→L0，在制品 3/3）。自研打通武器动作链路：`ItemFactory.applyWeaponPreset` 按字符串查 `bettercombat:preset_id` 组件挂到物品（零 import，D15），实测 `demo_longsword → 动作 bettercombat:claymore`、`test_sword → 动作 redtale_project:test_sword`；**新坑**：运行期新生成的 datapack 只在 available 里，需一次 `/datapack enable`（重启则自动启用，`probe_pack` 实测）· `E:\RedtaleProject\docs\ROUND-R7-WEAPON.md`、`PLAN.md` §13 R7/§13.11、`docs/TASKS.md`、`items/ItemFactory.java`、`items/ContentTooltip.java` · 下轮：数据包程序化 `addPack`+`reloadResources`；验 T-0002/0003/0004
- 2026-11-16 01:12 · S8 · 领 **T-0002**（`/redtale content list`）做到自测过 → `[DONE]`：新建 `ContentListCommand`（汇总 1 行 + 每内容 1 行 `id · base · 数值条数 · 词条 · weapon_attributes`，返回内容数），`RedtaleCommand` 的 `tooltip` 前插 2 行（注释 + 注册，未改已有行）；`gradle build --offline` 退出码 0，`grep -c`=2、jar 含新类、离线 3 份默认内容 → 3 行输出 · `src/main/java/com/redtale/project/core/command/ContentListCommand.java`、`.../RedtaleCommand.java`、`docs/TASKS.md` · 下一步：S7 起测试服验「输出条数 = `config/redtale_project/items/*.json5` 数」；「词条数」列暂显 `-（词条层未接入）`（`ItemContent` 无词条字段），T-0003 落地后替换；另注：同包无需 import，验收第 2 条若要「import+调用=2」需改成 =1
- 2026-11-16 02:05 · S7 · **验收 T-0002 → VERIFIED**（3/3：build exit 0 / `grep -c`=2 / 测试服 `content list` 4 行 = 4 份 json5）；**派 T-0005**（`tools/gen_item_lang.py`，14 基底物品 lang 键实测 0 条，`/give` 显示裸键），在制品 3/3。自研 **R8-1 闭合 R7 遗留**：新 `core/datapack/PackEnabler`（`repo.reload`→`addPack`→`reloadResources`），删掉 `world/datapacks/redtale_project` 后重启 → 日志 `ENABLED_AND_RELOADED`、`/datapack list` **无需手动 enable** 即见 `file/redtale_project`；运行期删包 + `/redtale reload` 亦恢复，无循环、redtale 0 ERROR、selftest 仍 55 PASS · `E:\RedtaleProject\docs\ROUND-R8-PACK.md`、`PLAN.md` §13 R8/§13.12、`docs/TASKS.md`、`src/main/java/com/redtale/project/core/datapack/PackEnabler.java` · 下轮：`CriticalHitEvent` 暴击入口；T-0003 落地后接词条 roll

- 2026-11-16 02:10 · S7 · **暴击入口上线（M2 第三块）**：`core/damage/CritRules` + `CritLayer`（`CriticalHitEvent` @LOWEST，掷暴击率 + 只写倍率 + 必要时 `setCriticalHit(true)`）+ `crit.json5` 默认落地 + `/redtale crit|crit probe`。FakePlayer 四组实测 **100 / 200 / 100 / 100** ⇒ 强制暴击生效、且我们倍率是**替换**进场值（原版 1.5 不叠乘）；`CommonHooks.fireCriticalHit` 字节码无门禁、BetterCombat jar 内 `CriticalHitEvent` 零引用。热重载实测 `force_on_roll:false` → 四组全 100。selftest 仍 55 PASS、测试服 `Done (2.330s)` 后已停。卡板：无 `[DONE]` 可验、在制品 3/3 已满 → **本轮未派新卡**（T-0003/0004/0005 仍 OPEN，S8 两轮未领）。新增 **Q-015**（原版跳跃暴击 1.5 是否统一改 2.0）· `E://RedtaleProject//docs//ROUND-R9-CRIT.md`、`PLAN.md` §13 R9/§13.13、`src/main/java/com/redtale/project/core/damage/CritLayer.java` · 下轮：先验 T-0003/0004/0005（S8 领了才有 DONE）；T-0003 落地后接词条 roll；M2 剩消耗品(D23)与修理
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
| Q-012 | S7 | `[Q-012]` M4 原版附魔强化走哪条：用已装 `enchantmentdisabler` 的 `maxLevels` 直接抬原版上限（改配置，几分钟），还是照原计划另做「超级锋利/超级保护」新附魔（schema+datapack+互斥，几天） | **已答复（2026-11-15 12:56，Aki）：另外做——「本质上是为了测自制的附魔接口」**。落 D32 + `docs/ENCHANT-API.md`：四层接口（schema→datapack→`redtale_project:scripted` 单组件→M0 脚本层），`enchantmentdisabler` 保留但只做减法（不启用 `maxLevels`）。M4 出口改为「**加第 N 个附魔只写 JSON5、不编译**」（V11） |
| Q-013 | S7 | `[Q-013]` 1.21.1 原版急迫**自带** `ATTACK_SPEED +0.1/级`（`MobEffects.DIG_SPEED` 字节码实读），D19「原版不加」的前提在 1.21.1 不成立；我们的 0.10/级会让急迫 II = +40% | **默认：自动去重**——检测到 `minecraft:effect.haste` 就让位给原版，配置数字不动（仍写 0.10，代表「目标总加成」）。实测急迫 II 4→4.8。若 Aki 要「原版 + 我们各 10%」的双份手感，把配置改 0.20 并把去重关掉即可（一行代码） |
| Q-015 | S7 | `[Q-015]` 原版跳跃暴击固定 1.5，我们 `critical_strike_power` 基值 2.0；`apply_to_vanilla_crit` 默认 true = 全服暴击统一 2.0（实测已确认是替换不是叠乘） | **统一 2.0**（S7 默认）。两套倍率共存玩家对不上账；想保留原版 1.5 改配置 false + reload，不换 jar |
| Q-014 | S7 | `[Q-014]` 属性值口径：`redtale_project:physical_damage = 0.2` 表示 **+20%**（小数，与 `ADD_MULTIPLIED_TOTAL` 同单位），还是 `20` 表示 +20%（百分数，面板/配置更好读） | **默认：小数**（0.2 = +20%）。理由：①与属性 modifier 的 `ADD_MULTIPLIED_TOTAL` 同单位，写入零换算、零精度坑；②tooltip 只在显示时 ×100 加 `%`，逻辑层永远一个单位；③改口径要动所有内容配置 + 已发物品，越早定越便宜。M2 铺 14 基底物品时按此写配置 |

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
