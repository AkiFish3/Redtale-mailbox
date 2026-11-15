---
title: 架构与数值
role: admin
group: 管理员
order: 12
nav: no
---

# 架构与数值

两件事凑在一起：**一个脚本层供四个内容面复用**，以及**不能覆盖式改伤害**。原文见 `E:/RedtaleProject/docs/DAMAGE-PIPELINE.md`。

## 一个脚本层，四个内容面

```
┌───────────── scripting core ─────────────┐
│ effect 注册表 │ trigger 注册表 │ condition 注册表 │
│ 数值表达式 %level% / 曲线 / 随机            │
└──────────────────────────────────────────┘
        ↑ 复用        ↑ 复用        ↑ 复用
   items(技能/宝石)  enchants(附魔)  mobs(怪物技能)
```

四个内容面都只是「元数据 + effect 列表」。**新内容 = 写配置；新效果类型 = 写一个 effect 实现。**

这也是为什么附魔能一口气做到 100+：EcoEnchants 的 103 个附魔就是纯数据。

## 实体：6~8 个原型撑 60 只/年

| 改一个就要换 jar | 原因 |
|---|---|
| `EntityType` 注册项 | `BuiltInRegistries` 引导期冻结，NeoForge 只允许动态注册 datapack registry |
| 实体类（AI 基类、寻路、`getDimensions`） | 类决定行为骨架 |
| 渲染器类型（注册位置） | 但渲染器内部可以读数据 |

| 不换 jar，按怪配置 | 做法 |
|---|---|
| 模型 / 贴图 / 动画 | 服务端同步 `model_id`，渲染器查表 → GeckoLib `.geo.json` + png |
| 音效 | `getAmbientSound/getHurtSound/getDeathSound` 读同步的 `sound_id` |
| 技能 | 实体持「技能控制器」，从配置读 ability 列表 + 冷却 |
| 属性 / 等级 / 掉落 / 装备 | 生成时套用配置（`AttributeMap`、`setItemSlot`） |
| 体积 | `minecraft:generic.scale` **会缩放碰撞箱**，小怪/巨怪靠它区分 |
| 自定义 ID | 我们自己的内容 ID 存在实体数据 + scoreboard tag 里 |
| 刷怪蛋 | 不按实体类型给，做一个通用刷怪蛋写 mob id |

::: warn 必须接受的 4 条限制
碰撞箱只能**等比缩放**，一个模板不能同时出「细高」和「扁宽」。
按怪筛实体只能靠 tag 或 `data get`，`/kill @e[type=...]` 只能按模板类型筛。
模型与音效是客户端资源，要资源包；音效还得在客户端 `sounds.json` 里注册。
第三方模组和调试工具看到的是**一种**实体，不是 N 种。
:::

原型规划：近战 / 远程 / 施法 / 召唤 / 冲锋 / 飞行 / 精英 / 环境 —— 8 个够用。只有「原型装不下的行为」才加原型（换 jar）。

## 热更新边界

判断标准只有一条：**它是不是注册表项**。

| 能热加（写 JSON5 + `/redtale reload`） | 为什么 |
|---|---|
| 武器 / 装备 / 宝石 / 材料 | 原版 `Item` + 自定义 DataComponent，注册表项只有「组件类型」 |
| 套装定义（件数、加成） | 纯数据，挂在组件的 `set_id` 上 |
| 附魔 | 生成 datapack JSON 后调 `ReloadableServerResources`；`Enchantment` 是 datapack registry |
| 怪物定义（属性/技能/掉落/模型/音效/体积） | 模板实体 + 数据 |
| 技能配置、掉落表、刷怪规则 | 数据 |
| 经验曲线 / 等级上限 / 职业开关 / 数值闸门 | 数字与开关 |

| 不能热加（必须换 jar） | 为什么 |
|---|---|
| 新 `EntityType` | `BuiltInRegistries` 引导期冻结 |
| 新 `Attribute` | 同上 → 所以要「一次注册 64 条」 |
| 新 effect / trigger / condition 原语 | 是 Java 代码 |
| 新 DataComponent **类型** | 类型是注册表，值才是数据 |
| 新方块 / 需要自定义行为的物品 | 纯展示物品不需要类，有右键逻辑就要 |

## 伤害三层 + 四规矩

```
L0 基础：原生 attack_damage + 原生 minecraft:damage 附魔（原版算好，不动）
L1 平加：我们的 AttributeModifier（固定 id，可整件卸下，受 attrCap 限制）
L2 乘区：LivingIncomingDamageEvent 里乘
         percent 池先加后乘 → 钳制 percentCap（默认 +200%）
         条件乘区最多 2 个，每个 ≤ condCap（默认 1.5）
L3 天花板：damageCap（默认 500）
```

::: warn 四条硬规矩
绝不 `setAmount(我们算的)` —— 会把前面所有 mod 的加成一并抹掉。
先加后乘：10 个 +20% 是 +200%，不是 6.19 倍。
超限走递减 `cap*(1-exp(-raw/cap))`，不硬截断，避免「堆到顶就白堆」。
tooltip 与结算**共用同一个 `settle()`**，否则会出现「写着 12.4 打出 9」。
:::

攻速单独处理：属性值不动（保持其它 mod 读取正确），只在冷却计算处饱和，`softCap` 默认 4.0（= 5 tick 地板）。

## 冲突面（实测 228 个 jar 的常量池）

| 事件 / 属性 | 引用 mod 数 |
|---|---|
| `LivingIncomingDamageEvent` | 12（spell_engine、Cataclysm、Twilight Forest、Create…） |
| `LivingDamageEvent` | 19 |
| `CriticalHitEvent` | **1**（只有 Cataclysm）→ 近战暴击走这个入口，冲突面极小 |
| `generic.attack_speed` | 4（rogues 是真发属性，其余是显示/皮肤） |

## 原版的两个事实

- **原版锋利**：`minecraft:damage` + `add` + `linear(base 1.0, per_level 0.5)`，互斥 tag `#minecraft:exclusive_set/damage`。自制附魔走同一组件 → 天然兼容、天然互斥。
- **急迫（Haste）不影响攻击速度**，只影响挖掘（`player.block_break_speed`）。「急迫加攻速」在 1.21.1 不存在，要做只能自己写且语义混乱 —— **建议不做**。

## 附魔第一批三档

| 档 | 内容 | 实现 | 数量 |
|---|---|---|---|
| 一档 | 原版附魔强化（超级锋利、超级保护、超级效率…） | **纯数据包**，复用原版组件 | 15~20 |
| 二档 | 原版组件组合（吸血、荆棘强化、经验加成） | 数据包 + 少量组合 | 10~15 |
| 三档 | 触发式（命中流血、击杀爆炸、受伤反弹） | 脚本层 | 按需 |

一档几乎零风险先做；二档验证组合边界；三档才是脚本层真正吃重的地方。
