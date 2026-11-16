# 属性注册表清单（M1 预制草案）

> 状态：**已定 80 条**（Aki 2026-11-15 拍板：64 实用 + 16 预留）。属性是启动期冻结的注册表项，加一条就要换 jar，所以这份表一次定死。
> 依据：`D:\redtale-work\upstream\MythicLib-1.7.jar` 内的两处实证 + `docs/DAMAGE-PIPELINE.md` §1.2。

## 0. 证据

| 证据 | 位置 | 拿到什么 |
|---|---|---|
| A | `MythicLib-1.7.jar` → `default/stats.yml`（3,041 B，解包于 `D:\redtale-work\cache\mythiclib-extract\default\stats.yml`） | 上游对属性设的上下限与默认基值：`CRITICAL_STRIKE_CHANCE: 0 = 80`、`BLOCK_POWER: 25 = 75`、`CRITICAL_STRIKE_POWER` 基值 200、`MOVEMENT_SPEED: 0 = .3`、`DEFENSE: 0 = 10000` 等 |
| B | `io/lumine/mythic/lib/api/stat/SharedStat.class`（常量池提取） | **61 条共用属性 id**，见 §1 |
| C | `MMOItems-6.10.jar` → `net/Indyuce/mmoitems/stat/*.class` 共 **115 个类** | 其中约 90 个是**物品元数据**（附魔、Lore、模型、颜色…），真正是数值属性的约 20 个：AttackDamage / AttackSpeed / MaxHealth / Armor / ArmorToughness / BlockBreakSpeed / MovementSpeed / KnockbackResistance / MaxAbsorption / Scale / JumpStrength / StepHeight / SweepingDamageRatio / MiningEfficiency / MovementEfficiency / OxygenBonus / SneakingSpeed / SubmergedMiningSpeed / WaterMovementEfficiency / FallDamageMultiplier |
| D | `spell_power` 1.6.0 `assets/spell_power/lang/en_us.json`（见 DAMAGE-PIPELINE §1.2） | 19 条：通用法强 + 13 系 + 治疗 + 法术暴击率/暴击伤害/急速 + 法术抗性。**只当清单参考，不复用它的属性** |

证据 B 的 61 条原文（按类内常量顺序）：

```
ATTACK_SPEED ATTACK_DAMAGE MAX_HEALTH LUCK HEALTH_REGENERATION MOVEMENT_SPEED
SPEED_MALUS_REDUCTION KNOCKBACK_RESISTANCE ARMOR ARMOR_TOUGHNESS MAX_ABSORPTION
BLOCK_BREAK_SPEED BLOCK_INTERACTION_RANGE ENTITY_INTERACTION_RANGE FALL_DAMAGE_MULTIPLIER
GRAVITY JUMP_STRENGTH SAFE_FALL_DISTANCE SCALE STEP_HEIGHT BURNING_TIME
EXPLOSION_KNOCKBACK_RESISTANCE MINING_EFFICIENCY MOVEMENT_EFFICIENCY OXYGEN_BONUS
SNEAKING_SPEED SUBMERGED_MINING_SPEED SWEEPING_DAMAGE_RATIO WATER_MOVEMENT_EFFICIENCY
MAX_MANA MAX_STAMINA MAX_STELLIUM MANA_REGENERATION STAMINA_REGENERATION
STELLIUM_REGENERATION LIFESTEAL SPELL_VAMPIRISM CRITICAL_STRIKE_CHANCE
CRITICAL_STRIKE_POWER SPELL_CRITICAL_STRIKE_CHANCE SPELL_CRITICAL_STRIKE_POWER
BLOCK_POWER BLOCK_RATING BLOCK_COOLDOWN_REDUCTION DODGE_RATING DODGE_COOLDOWN_REDUCTION
PARRY_RATING PARRY_COOLDOWN_REDUCTION ADDITIONAL_EXPERIENCE COOLDOWN_REDUCTION
PVP_DAMAGE PVE_DAMAGE UNDEAD_DAMAGE PVP_DEFENSE PVE_DEFENSE MAGICAL_DAMAGE
PHYSICAL_DAMAGE PROJECTILE_DAMAGE WEAPON_DAMAGE SKILL_DAMAGE DAMAGE_REDUCTION
```

## 1. 落点策略（先说清楚，不然 80 条会有歧义）

不是所有属性都自建。三类落点：

| 落点 | 判据 | 做法 |
|---|---|---|
| **原版属性** | 语义在原版已存在，且**必须**被原版管线读到（攻击伤害、攻速、生命、护甲） | 复用 `minecraft:generic.*`，我们只往上挂 modifier（DAMAGE-PIPELINE §3 的 L1） |
| **自建属性** | 原版没有（暴击、穿透、法术强度、生命偷取…） | 注册在 `redtale_project:` 下，零 mod 依赖（D12） |
| **纯逻辑值** | 不需要 `Attribute`（如「经验加成」只在我们自己的经验结算里用） | 仍注册成 `Attribute`，这样 `/attribute` 与 tooltip 免费可用 |

理由：注册成 `Attribute` 的成本只有启动期一条注册，但换来 `/attribute` 可读写、原版 tooltip 自动显示、其它 mod 能看到。**唯一不注册的理由**是它压根不参与任何数值结算。

## 2. 建议的 80 条（Aki 2026-11-15 定：80，非 64）

> **与 D16 的关系**：D16 已定「默认不设任何平衡上限，闸门保留为配置项，`0 = 关闭`」。
> 下表「默认上限」列写的数字是**建议初始值**，实现时全部落在 `balance.json5` 的 `attrCap`；
> 按 D16，出厂配置里这些值应为 `0`，只有 Aki 需要收紧时才填数字。

`id` 列是 `redtale_project:` 下的路径名；`落点 = 原版` 的行写的是 `minecraft:` 全名。

### A. 近战与物理（12）

| # | id | 落点 | 说明 | 默认上限（attrCap） |
|---|---|---|---|---|
| 1 | `minecraft:generic.attack_damage` | 原版 | 基础攻击伤害 | +60 |
| 2 | `minecraft:generic.attack_speed` | 原版 | 攻速（另有饱和曲线，见 §4） | +2.0 |
| 3 | `physical_damage` | 自建 | 物理伤害百分比 | %200 |
| 4 | `weapon_damage` | 自建 | 武器伤害百分比 | %200 |
| 5 | `projectile_damage` | 自建 | 投射物伤害百分比 | %200 |
| 6 | `critical_strike_chance` | 自建 | 近战暴击率（0~1） | 0.8 |
| 7 | `critical_strike_power` | 自建 | 暴击倍率（1.0 = 不额外加成，基值 2.0） | 5.0 |
| 8 | `armor_penetration` | 自建 | 护甲穿透百分比 | 0.8 |
| 9 | `lifesteal` | 自建 | 生命偷取百分比 | 0.3 |
| 10 | `pvp_damage` | 自建 | 对玩家伤害% | %200 |
| 11 | `pve_damage` | 自建 | 对怪物伤害% | %200 |
| 12 | `undead_damage` | 自建 | 对亡灵伤害% | %200 |

### B. 防御与减伤（18）

| # | id | 落点 | 说明 | 默认上限 |
|---|---|---|---|---|
| 13 | `minecraft:generic.armor` | 原版 | 护甲 | +30 |
| 14 | `minecraft:generic.armor_toughness` | 原版 | 护甲韧性 | +20 |
| 15 | `minecraft:generic.max_health` | 原版 | 最大生命 | +40 |
| 16 | `minecraft:generic.knockback_resistance` | 原版 | 击退抗性 | 1.0 |
| 17 | `damage_reduction` | 自建 | 全局减伤% | 0.75 |
| 18 | `block_rating` | 自建 | 格挡评级 | 80 |
| 19 | `block_power` | 自建 | 格挡强度（基值 25） | 75 |
| 20 | `block_cooldown_reduction` | 自建 | 格挡冷却缩减% | 0.8 |
| 21 | `dodge_rating` | 自建 | 闪避评级 | 80 |
| 22 | `dodge_cooldown_reduction` | 自建 | 闪避冷却缩减% | 0.8 |
| 23 | `parry_rating` | 自建 | 招架评级 | 80 |
| 24 | `parry_cooldown_reduction` | 自建 | 招架冷却缩减% | 0.8 |
| 25 | `pvp_defense` | 自建 | 对玩家减伤% | 0.75 |
| 26 | `pve_defense` | 自建 | 对怪减伤% | 0.75 |
| 27 | `magic_resistance` | 自建 | 法术抗性% | 0.75 |
| 28 | `health_regeneration` | 自建 | 生命回复（点/秒） | 5 |
| 29 | `max_absorption` | 自建 | 伤害吸收上限 | 20 |
| 30 | `reflect_damage` | 自建 | 反伤% | 1.0 |

### C. 法术与资源（18）

| # | id | 落点 | 说明 | 默认上限 |
|---|---|---|---|---|
| 31 | `magical_damage` | 自建 | 法术伤害% | %200 |
| 32 | `spell_critical_strike_chance` | 自建 | 法术暴击率 | 0.8 |
| 33 | `spell_critical_strike_power` | 自建 | 法术暴击倍率 | 5.0 |
| 34 | `spell_vampirism` | 自建 | 法术吸血% | 0.3 |
| 35 | `max_mana` | 自建 | 法力上限 | 500 |
| 36 | `mana_regeneration` | 自建 | 法力回复/秒 | 50 |
| 37 | `cooldown_reduction` | 自建 | 冷却缩减% | 0.7 |
| 38 | `healing_power` | 自建 | 治疗强度% | %200 |
| 39 | `fire_damage` | 自建 | 火系强度% | %200 |
| 40 | `frost_damage` | 自建 | 冰系强度% | %200 |
| 41 | `lightning_damage` | 自建 | 雷系强度% | %200 |
| 42 | `arcane_damage` | 自建 | 奥术强度% | %200 |
| 43 | `nature_damage` | 自建 | 自然强度% | %200 |
| 44 | `shadow_damage` | 自建 | 暗影强度% | %200 |
| 45 | `holy_damage` | 自建 | 神圣强度% | %200 |
| 46 | `water_damage` | 自建 | 水系强度% | %200 |
| 47 | `earth_damage` | 自建 | 土系强度% | %200 |
| 48 | `spell_resistance` | 自建 | 法术抗性（元素平均） | 0.75 |

### D. 采集与移动（10）

| # | id | 落点 | 说明 |
|---|---|---|---|
| 49 | `minecraft:generic.movement_speed` | 原版 | 移动速度（上游上限 0.3） |
| 50 | `minecraft:generic.block_break_speed` | 原版 | 挖掘速度倍率 |
| 51 | `minecraft:generic.jump_strength` | 原版 | 跳跃力 |
| 52 | `minecraft:generic.safe_fall_distance` | 原版 | 安全下落距离 |
| 53 | `minecraft:generic.step_height` | 原版 | 跨步高度 |
| 54 | `minecraft:generic.oxygen_bonus` | 原版 | 水下呼吸加成 |
| 55 | `sneaking_speed` | 自建 | 潜行速度% |
| 56 | `water_movement_efficiency` | 自建 | 水中移动效率% |
| 57 | `mining_efficiency` | 自建 | 挖掘效率% |
| 58 | `fall_damage_multiplier` | 自建 | 摔落伤害倍率 |

### E. 通用与进度（6）

| # | id | 落点 | 说明 |
|---|---|---|---|
| 59 | `minecraft:generic.luck` | 原版 | 幸运 |
| 60 | `additional_experience` | 自建 | 经验加成% |
| 61 | `skill_damage` | 自建 | 技能伤害% |
| 62 | `max_stamina` | 自建 | 耐力上限（冲刺/闪避消耗） |
| 63 | `stamina_regeneration` | 自建 | 耐力回复/秒 |
| 64 | `minecraft:generic.scale` | 原版 | 体型（D9 怪物体积也用它） |

### F. 预留 16 条（65~80，不上面板、不出现在 tooltip）

> **为什么先注册**：属性是启动期冻结的注册表项，加一条要换 jar，改名等于换 ID、存档不兼容。
> 这 16 条**注册但不使用**——没有物品/技能会给它们值，`/redtale attr` 不列，面板不显示。
> 用到时只写配置（D17「内容与代码分离」），不换 jar。这是 Aki 选 80 而不是 64 的全部理由。

| # | id | 用途（留白给谁） |
|---|---|---|
| 65 | `air_damage` | 风系强度%（四系补齐的第一条） |
| 66 | `soul_damage` | 魂系强度% |
| 67 | `blood_damage` | 血系强度% |
| 68 | `unholy_damage` | 邪系强度% |
| 69 | `true_damage` | 真实伤害%（不吃减伤，高危属性，默认不给） |
| 70 | `attack_range` | 近战触及距离（原版 `entity_interaction_range` 的便捷别名） |
| 71 | `sweeping_damage_ratio` | 横扫伤害比例（上游有此属性） |
| 72 | `hunger_efficiency` | 饥饿消耗降低%（跑图/长时间战斗） |
| 73 | `mana_cost_reduction` | 法力消耗降低%（与 `cooldown_reduction` 分轴） |
| 74 | `charge_speed` | 蓄力速度%（弓 / 三叉戟 / 重击） |
| 75 | `projectile_velocity` | 投射物速度% |
| 76 | `healing_received` | 受治疗加成%（奶妈向套装用） |
| 77 | `armor_durability` | 装备耐久消耗降低%（负 modifier = 加速磨损，也留了口子） |
| 78 | `potion_duration` | 药水/食物效果时长%（与 D19 的急迫时长直接相关） |
| 79 | `knockback_power` | 击退强度（不是抗性） |
| 80 | `critical_damage_resistance` | 暴击伤害减免%（PVP 克制暴击流） |

## 3. 与上游的差异（有意为之，不是漏项）

| 上游有 | 我们的处理 | 原因 |
|---|---|---|
| `MAX_STELLIUM` / `STELLIUM_REGENERATION` | **不做** | 是上游某个特定玩法货币，赤物语没有 |
| `SPEED_MALUS_REDUCTION` | **暂不做** | 依赖上游的「减速惩罚」机制，我们没有 |
| `BLOCK_INTERACTION_RANGE` / `ENTITY_INTERACTION_RANGE` / `GRAVITY` / `BURNING_TIME` / `EXPLOSION_KNOCKBACK_RESISTANCE` / `SWEEPING_DAMAGE_RATIO` / `SUBMERGED_MINING_SPEED` | **不做** | 1.20.5+ 原版已是独立属性，直接用 `minecraft:` 的，不重复造 |
| `air` / `soul` / `blood` / `unholy` 系法强 | **暂不做** | 先 9 系，留出扩容空间（见 §5） |
| `DEFENSE`（0~10000 的防御评级） | **不做** | 与 `damage_reduction` 语义重叠，上游两套并存是历史包袱 |

## 4. 攻速为什么单列

`attack_speed` 是原版属性，价值上限不是「数值」而是「冷却」。DAMAGE-PIPELINE §4 的方案是属性值不动、只在冷却计算处处理。**按 D19，饱和曲线 `soft_cap` 默认 0 = 关闭**（急迫 0.10/级全开，不砍）；唯一保留的是**物理地板** `min_attack_delay_ticks = 1.0`：`getCurrentItemAttackStrengthDelay()` 返回值一旦到 0，原版 `getAttackCooldownProgress` 会除以 0 → 恒为 1 → 每 tick 都能出手。这不是平衡阀，是防除零。AttributeFix 拆掉原版上限后，属性值可以到 1024 次/秒，这条地板必须从 M1 就在。

## 5. 拍板结果

| # | 问题 | 结论 |
|---|---|---|
| 1 | 注册 64 还是 80 条 | **80**（Aki 2026-11-15 拍板）→ 见 §2 F 段 16 条预留，注册但不使用、不上面板 |
| 2 | 暴击双轨要不要 | **待 Aki**，S7 默认保留双轨（近战 `critical_strike_*` / 法术 `spell_critical_strike_*`）。理由：合并后做不出「法系暴击」与「物理暴击」两套流派。M2 实装前可推翻 |
| 3 | 基值表照搬上游吗 | **待 Aki**，S7 默认照搬：`critical_strike_power` 基值 **2.0**（= 200%）、`block_power` 基值 **25**。要改走 `balance.json5`，不改代码 |

## 6. 未验证

- ~~自建属性在 1.21.1 的 `/attribute` 里能否正常读写、tooltip 中文名是否只需要 lang 条目~~ →
  **R2 已实测（2026-11-15）**：`/attribute @e[type=zombie,limit=1] redtale_project:damage_reduction get`
  返回 `Value of attribute Damage Reduction for entity Zombie is 0.0`，`modifier add` 也能正常加。
  英文名来自 jar 内 `assets/redtale_project/lang/en_us.json`（NeoForge 服务端 `LanguageHook` 会读），
  所以 **lang 键必须与 `RangedAttribute` 的 descriptionId 一致**（`attribute.redtale_project.<path>`）。
  客户端 tooltip 的中文名仍未验证（无客户端）。证据：`docs/ROUND-M1-ATTR.md` §3.3。
- `RangedAttribute` 的 ±1e9 边界未实测超界钳制（原版 `/attribute` 会先拒绝超大数值输入），留到 `settle()` 有单测时一起验。
- 玩家上下文的 `attack_speed` 拆解未验证：测试服无客户端；且绝大多数生物没有 `minecraft:generic.attack_speed`，僵尸实测报「没有属性」。
- `minecraft:generic.scale` 对碰撞箱的缩放是否对所有模板实体生效（D9 的体积方案依赖它）→ 归 M6。
