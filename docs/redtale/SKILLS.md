# 技能（M5）：schema、24 条原语、释放链路

2026-11-17 · R25 定稿。回答「右键释放技能，冷却消耗正确」这一出口条件具体长什么样。
本文件是 **M5 的接口契约**：`skills/*.json5` 的字段、原语清单、伤害口径由这里定，S8 只照卡实现，不设计。

## 1. 边界：技能不是什么

| 系统 | 给什么 | 复用谁的实现 |
|---|---|---|
| **技能**（本条，M5） | 一次主动释放：条件 → 冷却 → 原语序列 | 脚本层的 `effect` / `condition` 原语（不新开一套「触发器」） |
| 附魔（M4） | 命中/受击时的被动 | `redtale_project:scripted` → 脚本层 |
| 套装（M3） | 穿戴件数触发的永久属性 | `SetBonus` 直接写 `AttributeMap` |
| 技能树（M7） | 解锁「能不能用」某个技能 | `unlock_skill` 效果 + 本表的技能 id |
| 属性（M1） | 数值 | `AttributeSpecs` 的 80 条，技能只读不建 |

一句话：**技能 = 带冷却与释放条件的脚本包**。内容加多少技能都不用换 jar；加原语才换 jar（D17）。

## 2. 释放链路（五步，缺一步就静默不生效）

```
① 绑定  物品的 abilities[] 里有这个技能 id（M5-B）  /  v1 用 /redtale skill cast <id>
② 触发  右键（ContentItem#use）→ SkillEngine.cast(player, skillId, level)
③ 条件  skill.conditions（脚本层 condition 原语，全部 true 才继续）
④ 门槛  冷却（按 玩家 × 技能 id）→ 资源（M5-B 的法力池）
⑤ 执行  skill.effects 顺序跑（复用 ScriptEngine.runCalls，单条失败只记日志不影响后续）
```

- **不新建触发器体系**：技能没有 `trigger` 字段。触发是引擎的入口（右键 / 命令 / M6 怪物 AI），不是内容。
- **不做「技能等级」**：v1 里一条技能只有一档数值；等级缩放排在 M7（技能树 + 职业）之后，避免同时引入两个缩放轴。
- 冷却与脚本层的 `cooldown_ticks` 是两件事：脚本冷却按「脚本 id + 玩家名」记在 `ScriptEngine`；技能冷却按「技能 id + 玩家 UUID」记在 `SkillEngine`，**互不借道**。

## 3. `skills/*.json5` schema（v1，一个文件一条技能）

```json5
// config/redtale_project/skills/gale_slash.json5
{
  id: "redtale_project:gale_slash",   // 必填，必须含 `:`；缺了就跳过这条（不猜命名空间）
  name: "skill.redtale.gale_slash",   // 可选，缺省 skill.redtale.<id 的 path>
  icon: "minecraft:iron_sword",       // 可选，缺省 minecraft:paper（只给 GUI 用，服务端不管）
  cooldown_ticks: 120,                // 可选，缺省 0 = 无冷却；负数/非数字 → 0 + 一条 WARN

  // 可选，脚本层 condition 原语，全部 true 才释放；某项坏掉只丢该项
  conditions: [
    { type: "health_below", args: { ratio: 0.5 } },
  ],

  // 必填，至少 1 条有效项；全坏 → 整条技能跳过 + 一条 WARN
  effects: [
    { type: "console_log", args: { text: "[skill] gale_slash by %player%" } },
    { type: "damage", args: { amount: 6.0, radius: 3.5 } },
  ],
}
```

解析口径（`SkillSpec.parse` 的契约，与 `scripts/*.json5` 的 R1-a 分级失败一致）：

| 情况 | 处理 |
|---|---|
| `id` 缺失 / 空白 / 不含 `:` | 整条跳过 + 1 条 WARN（不补命名空间，避免 `a:b` 与 `b` 被静默合并） |
| 同一 id 出现两次 | 保留**先出现**的 + 1 条 WARN（与 `EnchantmentGenerator` 同口径） |
| `effects` 缺失 / 空数组 / 全项坏 | 整条跳过 + 1 条 WARN（没有可执行 effect 的技能是配置错误） |
| 单项 `type` 缺失或非字符串 | 丢该项 + 1 条 WARN，其余照跑 |
| `args` 非对象 | 该项按空 args 处理 + 1 条 WARN |
| `cooldown_ticks` 越界 | 负数 → 0；`> 1e9` → `1e9`（D16 只留异常保护，不设玩法上限） |

**解析层不校验原语是否存在**：那需要 `ScriptRegistries`，属启动期冻结的注册表，交给运行期（`runCalls` 对未知 type 打一行 WARN）与 `/redtale validate`（后续并入）。解析器保持纯函数 = 可离线探针。

## 4. 24 条原语总表（8 类）

状态：`✅` 已注册 · `—` 待实现（**加原语 = 换 jar，D17 必须记账**）。
已注册的 3 条 effect（`message` / `console_log` / `heal`）里只有 `heal` 计入 24 条，前两条是 M0 的调试原语。

| # | id | 类 | 参数（全部可选，缺省见右） | 状态 | 备注 |
|---|---|---|---|---|---|
| 1 | `damage` | 直伤 | `amount` 白值 · `radius` 0=单体 · `damage_type` 缺省 `redtale_project:skill` · `falloff` 0 | — | **只给白值**，倍率由 `DamageLayer` 统一乘（§5） |
| 2 | `damage_aoe` | 直伤 | `amount` · `radius` · `falloff` 0.5 · `max_targets` 0=不限 | — | 与 1 分开：AOI 中心是施法者脚下还是命中点要显式 |
| 3 | `damage_over_time` | 直伤 | `amount` · `duration_ticks` · `interval_ticks` 20 · `damage_type` | — | 每个 tick 走一次 `hurt`，不吃暴击 |
| 4 | `execute` | 直伤 | `threshold` 0.2（目标血量比例）· `damage_type` | — | 达标直接结算，不走倍率也不会暴击 |
| 5 | `knockback` | 控场 | `strength` 0.4 · `radius` 0 | — | |
| 6 | `pull` | 控场 | `strength` 0.4 · `radius` 6 | — | 反向击退；对玩家生效要判 `no_knockback` |
| 7 | `stun` | 控场 | `duration_ticks` 40 | — | 停 AI + 禁移动，**不**用 `slowness 255`（会被抗性减免） |
| 8 | `slow` | 控场 | `amplifier` 1 · `duration_ticks` 100 | — | 原版 `slowness`，走 `MobEffect` |
| 9 | `dash` | 位移 | `distance` 4 · `duration_ticks` 6 | — | 分帧给速度，一次性 `setDeltaMovement` 会被服务端校正拉回 |
| 10 | `teleport` | 位移 | `distance` 8 · `require_line_of_sight` true | — | 视线 raycast 落点，落点必须在可站立方块上 |
| 11 | `leap` | 位移 | `up` 0.5 · `forward` 0.3 | — | |
| 12 | `projectile` | 投射 | `entity` 缺省 `minecraft:arrow` · `speed` 2.0 · `on_hit` 原语序列 | — | 命中回调要能把 `damage` 塞进去（M5-C） |
| 13 | `beam` | 投射 | `range` 12 · `damage` · `damage_type` | — | 瞬间命中，无实体，纯 raycast |
| 14 | `aura` | 投射 | `radius` 4 · `duration_ticks` 100 · `interval_ticks` 20 · `on_tick` 原语序列 | — | 跟随施法者的持续范围 |
| 15 | `buff` | 增益 | `effect` 原版 id · `amplifier` 0 · `duration_ticks` | — | |
| 16 | `heal` | 增益 | `target` caster·`ratio`·`per_level`·`flat` | ✅ R24 | 按最大生命比例（R24-a） |
| 17 | `shield` | 增益 | `amount` · `duration_ticks` | — | `absorption` 心形护盾，不进 `DamageLayer` |
| 18 | `cleanse` | 增益 | `max_count` 0=全清 | — | 只清负面 `MobEffect` |
| 19 | `debuff` | 减益 | `effect` · `amplifier` · `duration_ticks` | — | |
| 20 | `ignite` | 减益 | `seconds` 4 | — | 走 `setRemainingFireTicks`，不是 `MobEffect` |
| 21 | `weaken` | 减益 | `attribute` · `operation` · `amount` · `duration_ticks` | — | 限时属性 modifier，id 固定 `redtale_project:skill/<skill>/<n>`，到点必移除 |
| 22 | `summon` | 召唤 | `entity` · `count` 1 · `lifetime_ticks` 0=永久 · `inherit_owner` true | — | M6 的模板实体就位后才有内容价值 |
| 23 | `trap` | 召唤 | `radius` 2 · `trigger_radius` 1.5 · `duration_ticks` 200 · `on_trigger` 原语序列 | — | 落一个不可见标记实体（`Marker`），踩到即触发 |
| 24 | `fx` | 表现 | `particle` · `sound` · `count` 8 | — | 纯客户端表现；**不带任何数值**，单独一条便于给技能加手感而不改结算 |

**计数口径**：24 = 直伤 4 + 控场 4 + 位移 3 + 投射 3 + 增益 4 + 减益 3 + 召唤 2 + 表现 1。
`grep -c "^| [0-9]" docs/SKILLS.md` = 24 是本表唯一机器可判的断言，S7 每轮加原语时同步改这一行。

## 5. 伤害口径（三层模型不许破）

技能伤害**只准走这一条路**：

```
damage 原语   entity.hurt(skillDamageSource(), amount)      ← 只给白值（D12 的「一层」）
   ↓
LivingIncomingDamageEvent（LOWEST）
   ↓  DamageLayer 乘属性池（physical_damage / spell_power / 条件乘区）  ← 「二层」
   ↓
最终值 = 原版护甲/抗性结算                                 ← 「三层」原版
```

三条红线：

1. **绝不 `setAmount()`**：`damage` 原语只 `hurt`，不碰事件里的 amount。谁写绝对值谁破坏 `DAMAGE-PIPELINE` 的可加性。
2. **技能类型必须在 `redtale_project:` 下**：`DamageLayer` 的白名单是 `redtale_project:*`（R4），写 `minecraft:generic` 的技能伤害**不会被乘**（等于绕过整套属性）。
3. **`damage_type` 是启动期 datapack registry**：新增技能伤害类型 = 生成 `data/redtale_project/damage_type/*.json` + **重启**（与附魔同层，R21-c）。所以 v1 先用一个通用 `redtale_project:skill`，不按技能分类型。

**M5-A 要补的一件事（S7 做，不派卡）**：`MultiplierRules` 现在只取 `physical_damage`（R4 口径），法术技能会吃物理百分比。需要按 `damage_type` 分「物理 / 法术」两轴，各自取自己的属性池；这是 `core/damage` 的结构改动，S7 独占。

## 6. 冷却与资源

| 项 | v1（M5-A） | 之后 |
|---|---|---|
| 冷却 | `SkillEngine` 内存表 `key = (玩家 UUID, 技能 id)` → 到期 tick；重启清零 | `cooldown_reduction` 属性接入（M5-B），仍按固定公式 `cd × (1 - min(0.9, 值))`，**不设 0 冷却**（下限 1 tick，理由同 D19 的物理地板） |
| 法力 | 不耗 | M5-B：`max_mana` 上限 + `mana_regeneration`/秒回复 + `mana_cost_reduction` 折算；当前法力是**玩家持久状态**（`PlayerData`），登录同步 |
| 物品消耗 | 无 | M5-C：`cost.item` / `cost.durability`，复用 `Repairer` 的扣件口径 |

冷却文案：`技能 <id> 冷却中：<剩余tick> tick`（写死便于 grep）。**冷却按 UUID 不按名字**（改名清冷却是个漏洞）。

## 7. 绑定（谁能放这个技能）

| 阶段 | 做法 | 换 jar？ |
|---|---|---|
| v1（M5-A） | `/redtale skill cast <id> [等级]`，只验引擎 | 否 |
| v1.5 | 物品绑定：`items/*.json5` 的 `abilities: ["redtale_project:gale_slash"]` → `ItemContent` 第 16 字段 → 写进 `ContentData.abilities`（字段**已存在**，只是没人填）→ `ContentItem#use` 里没有 `use` 段时尝试施放 | 是（`ItemContent` 加字段） |
| M5-C | 键位绑定（客户端 mod + payload，D10 允许随包下发） | 是 |
| M6 | 怪物技能：同一 `SkillEngine`，`SkillController` 从怪配置读 ability 列表 | 是 |

右键释放的取舍：**武器右键 = 施放绑定技能**（`ContentItem#use`），不再单独占键位。BetterCombat 不占右键（已验），所以不冲突；代价是「右键格挡」这类未来功能要让位给键位。

## 8. 验收矩阵（M5 出口）

| # | 项 | 判据 |
|---|---|---|
| K1 | 注释/配置零编译 | 只写一份 `skills/*.json5` → `/redtale reload` → `/redtale skill list` 见该条（**不换 jar**） |
| K2 | 冷却 | 连放两次：第一次生效，第二次返回「冷却中」且剩余 tick 递减；`cooldown_ticks: 0` 时不拦 |
| K3 | 条件 | `conditions` 不满足时一句「条件不满足」且 `effects` 一条都没跑（用 `console_log` 作证） |
| K4 | 原语序列 | 一条技能里 3 个 effect 按序全跑；中间一个参数写坏只丢那一条 |
| K5 | 伤害走管线 | `damage` 技能打木桩：白板 10 → 属性 `physical_damage 0.2` 时 **12**（证明吃 L2 乘区，不是 `setAmount`） |
| K6 | 坏配置不崩 | 缺 `id` / `id` 不含 `:` / `effects` 空 / `cooldown_ticks: "x"` → reload 各 1 条 WARN，服务端照跑 |
| K7 | 绑定 | 带 `abilities` 的武器右键施放，空手右键不施放（M5-B） |
| K8 | 怪物技能 | 配置的怪能放同一技能（M6 验） |

## 9. 交付顺序

| 段 | 内容 | 谁做 |
|---|---|---|
| M5-A | `SkillSpec`（解析，纯函数，派 S8）→ `SkillEngine`（冷却表 + `runCalls`）→ `/redtale skill list\|cast` → 默认 2 条技能配置 → K1~K6 | S8 解析器；引擎与命令 S7 |
| M5-B | `ItemContent.abilities` + `ContentData` 写入 + 右键施放 + `cooldown_reduction`/法力池 | S7（跨 3 文件） |
| M5-C | 6 条高频原语（`damage` / `damage_aoe` / `dash` / `buff` / `debuff` / `fx`）+ 默认技能放量 | S7 定接口，可按原语逐条派卡 |
| M6 | 怪物技能控制器复用 `SkillEngine` | S7 |

## 10. 不做

- 不做技能等级/技能点（M7 技能树的 `unlock_skill` 只管「能不能用」）。
- 不做「技能热键栏」GUI（owo 排后，M5 只做命令 + 右键）。
- 不做 `projectile` 的自定义弹道形状（原版实体 + 参数够用；要曲线弹道再单开原语）。
- 不做技能与 `spell_engine` 的任何互操作（D11：连属性都不复用）。
- 不做「按打出伤害抽血」：`post_attack` 组件签名不带伤害值（R24-a），技能侧由 `damage` 原语自己 `hurt`，天然有值；附魔侧维持「按最大生命」口径。
