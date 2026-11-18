# RedtaleProject · 规划 v2（2026-11-15）

把 Bukkit 系 RPG 套件（MMOItems / MMOInventory / MMOCore / EcoEnchants / MythicMobs）的能力，在 **Minecraft 1.21.1 + NeoForge** 上重做成自研实现。不做兼容层、不跑 Hybrid。
源码 `E:\RedtaleProject`；jar / 反编译 / 大缓存 `D:\redtale-work`。

> 项目名：**RedtaleProject**　Mod ID：**`redtale_project`**（2026-11-15 定，见 §2）

## 1. 已定决策

| 编号 | 决策 |
|---|---|
| D1 范围 | 自定义武器、宝石、套装、技能、**等级/经验/职业（MMOCore）** 全做 |
| D2 打包 | 现在**单体 jar**，但内部按 `core/items/inventory/enchants/mobs` 分源码集；将来拆系列模组只搬目录 |
| D3 数据 | **不兼容 YAML**，全 JSON5；不写迁移器 |
| D4 怪物 | **模板实体 + 数据驱动**：新怪只写配置，新「机制」才写代码（见 §5） |
| D5 附魔 | 先做脚本层；附魔产物是真实 `Enchantment` 注册表项，与原版附魔书完全一致 |
| D6 命名 | 通用词汇（item / stat / socket / set / ability）随便用；**禁用上游专名**：`mmoitems` / `mmocore` / `mmoinventory` / `mythiclib` / `mythicmobs` / `ecoenchants` 不得出现在包名、类名、配置键、命令名、文件树里 |
| D7 许可证 | 只有 **eco 是 MIT** 可移植；**libreforge 是 BUSL 1.1，禁止把代码搬进生产模组**；MMO*/MythicMobs/EcoEnchants 闭源，只参考行为 |
| D8 协作 | 跨机沟通走 S3 信箱（`D://redtale-ops//mail_sync.py`）；遇到啃不动的点写求助信，由 Aki 调度 Opus 5.5 / GPT 6.1 Sol 支援 |
| D9 实体 | **少量 EntityType 当模板，模型/ID/技能/音效按怪配置**（见 §5） |
| D10 客户端 | **允许随整合包下发资源包 / 客户端模组** → 自定义模型、技能特效、音效全部可做（2026-11-15） |
| D11 前置 | **只吃「库型」前置**，白名单：GeckoLib / AzureLib / PlayerAnimator / Architectury / Cloth Config / Curios / Resourceful Lib / AttributeFix / KotlinForge。**白名单外一律不是前置**——`spell_power`、`spell_engine`、Iron's Spells 这类玩法型 mod 明确排除，连属性都不复用（2026-11-15 修正） |
| D12 数值 | 三层模型 + 可配闸门，**不覆盖式改写伤害**。**属性全部自建在 `redtale_project:` 下**，零 mod 依赖；`spell_power` 的 19 条属性只当清单参考。与它共存用可选桥接（`bridge`，默认 off，详见 `docs/DAMAGE-PIPELINE.md` §1.2.1） |
| D13 测试服 | `E:\server-test`，NeoForge 21.1.257 与正式服同版，**最小模组集**（12 个库型前置），端口 25567 / RCON 25577（见 §8） |
| D14 可配 | **全内容可配 + 热重载**：装备/宝石/套装/附魔/怪物/技能组合/经验曲线/等级上限/职业开关/数值闸门，全部 JSON5，`/redtale reload` 生效（见 §9） |
| D15 BetterCombat | **已装（2.4.0），但不作前置**：运行期检测、代码零 import、编译期 `compileOnly`。攻速只需 mixin `getCurrentItemAttackStrengthDelay` 一个点即可同时兼容它与原版；武器内容必须自带 `weapon_attributes`（datapack，可热加）。详见 `docs/DAMAGE-PIPELINE.md` §11 |
| D16 数值默认 | **不设平衡上限**：`percentCap` / `condCap` / `condCount` / `damageCap` / `attackSpeedSoftCap` 默认全 `0 = 关闭`。只留异常保护（负数归零、`1e9` 硬顶、超阈值记日志不拦）。数值靠「投放层」控制，不靠「结算层」砍 |
| D18 攻速来源 | **声明式**：`config/redtale_project/attack_speed.json5` 里配「效果 → 攻速」映射（`haste_attack_speed_per_level`、`effect_attack_speed`）。**急迫默认 `0.10`/级（开启，见 D19）**，其余外部来源（咖啡因 / 茶 / Ferocity / Implicit Haste / 双持）默认 `0` 以免重复计。一律用 `ADD_MULTIPLIED_TOTAL` 写进 `ATTACK_SPEED` 属性（固定 modifier id，等级变化先移除再加），不自乘冷却。配套 `/redtale attr <属性>` 把每个来源拆开打印 |
| D19 急迫=攻速 | **保留为玩法特性，不做平衡钳制（2026-11-15 Aki 拍板）**：`haste_attack_speed_per_level` 默认 **0.10**（急迫 I +10%、II +20%… VIII +80%），`soft_cap` 默认 **0 = 不饱和**。理由是「急迫堆攻速」在 1.20.1 已是成型玩法（康普茶供时长 + 星芒抬等级 → 长时间急迫 VIII），属于该服的标志性手感，不是需要修掉的 bug。**代价明示**：急迫 VIII + Ferocity 满层 + 咖啡因 ≈ 3.7× 攻速，`allow_fast_attacks=true` 下这就是线性 DPS 乘数；我们不砍结算层，靠投放层（药水/食物/剑的获取难度）与 `/redtale attr` 的可视化来管理。想关掉只需把配置改 0，不换 jar |
| D20 显示口径 | **武器 tooltip 默认写「单次伤害 + 攻速（tick / 次每秒）」，DPS 默认关**，由客户端 `client.json5` 自行切换（`show_dps` / `show_attribute_breakdown` / `assume_target`）。理由：单次伤害是玩家能对账的数，DPS 是随目标变化的推导量；攻速必须写，因为 D19 下攻速能到 3.7 倍。显示与结算共用同一个 `settle()`。详见 `docs/DAMAGE-PIPELINE.md` §5（2026-11-15 Aki 拍板） |
| D17 热更新 | **内容与代码分离**：14 基底物品 + **80 属性**（64 实用 + 16 预留，见 `docs/ATTRIBUTE-REGISTRY.md` §2F）+ 8 实体原型 + 32 原语 + 1 个通用 `ContentData` 组件。内容更新只写配置/生成 datapack，不换 jar。详见 `docs/HOT-UPDATE.md` |
| D21 白板化 | **自定义装备的数值只来自 `ContentData`**。机制（已用 21.1.257 字节码核对）：`ItemStack.forEachModifier` 在 `ATTRIBUTE_MODIFIERS` 的**列表非空**时只用组件、跳过 `item.getDefaultAttributeModifiers()`，所以设一个非空组件就屏蔽了底材（钻石甲的 8 护甲）的加成。写「20 护甲」就是 20。**坑**：0 属性装备给空列表会回落到底材，要显式加 `+0` 占位。原版附魔效果（`damage_protection` 等）**保留**，逐物品可用 `strip_vanilla_effects` 关掉。详见 `docs/ITEM-MODEL.md` §1 |
| D22 随机词条 | **做**（A1）：`affixes/*.json5` + `affix_pools/*.json5`，`prefix`/`suffix`/`core` 三类，`weight` 池内权重、`exclusive_group` 互斥、`slots` 定槽数（投放层，不做全局钳制）。**掉落时 roll**，结果存进 `ContentData.affixes[]`，tooltip / 结算 / `/redtale attr` 读同一份。重铸 = 重 roll + 扣费。详见 `docs/ITEM-MODEL.md` §2 |
| D23 消耗品与修理 | **做**（A4）：`consumable`（effects / restore_food / 饱和 / `ItemCooldowns` 冷却 / 可挂脚本 effect）与 `repair`（对目标物品按 amount 或 percent 恢复耐久，可扣费、可消耗自身），配套 `/redtale repair`。详见 `docs/ITEM-MODEL.md` §3 |
| D24 专业 | **做，但后置**（A5）：`professions/*.json5`，与主等级**双累加器**、复用同一个 ExpSource 注册表（成本很低）。**不做方块再生**（属自定义矿脉，已否）。M7 主体完成后再接 |
| D25 技能树 | **做**（A6）：节点 = `effects[]`（`attribute` / `unlock_skill` / `passive`）+ `requires` + `cost`；`pos` 可选、缺省自动布局。点数是**派生值**（Σ cost），不做独立货币；洗点走经济桥并可回滚全部 modifier。节点 id 发布后不可改名。详见 `docs/SKILL-TREE.md` |
| D26 原版刷怪替换 | **做**（A8）：`spawn_rules/*.json5`，语义对齐 MythicMobs RandomSpawns——`match` / `chance` / `priority` / `action: replace\|add` / `conditions{world,biome,light,time,y,outside,difficulty}` / 每区块上限。钩子候选两个（`MobSpawnEvent.FinalizeSpawn` 取消+手动生成 / mixin `NaturalSpawner`），**M6 先做技术验证再定**（R42 已核验：`FinalizeSpawnEvent` 在 21.1.257 只由 `BaseSpawner`/`TrialSpawner` 触发，自然刷怪只有 `MobSpawnEvent.PositionCheck` + `getPotentialSpawns`，见 §13.45 R42-c/d） |
| D27 不做工作台与矿脉 | **明确不做**（A2/A3）：原版配方 + 服上已有 `kubejs` 足够；矿脉交给 `worldweaver`/`lithostitched`。数据层只认「配方 → 产物」，将来要加台子只是包一层 GUI+计时，不动物品模型。**这不是漏项，是决定** |
| D28 经济 | **可选桥接，不拆第三个 mod**：内部 `EconomyBridge`（`balance/withdraw/deposit`）三个实现——`none`（默认，不收费只记日志）/ `command`（走 `/eco` 之类服务端命令，零编译依赖）/ `redtale`（`compileOnly` 一个纯接口小 jar）。将来真要共用再抽 `redtale_core_api`，**现在不抽**（接口未稳定，抽早了两边都被锁死） |
| D29 Curios 为可选前置 | **有则注册饰品类型，无则整类不注册**：编译期 `compileOnly`，运行期 `ModList` 探测；`DeferredRegister` 在构造器里按条件创建（注册项一旦建就进 registry，无法撤回）。数据侧 `requires: ["curios"]` 的条目在缺失时**跳过 + WARN**，不崩。**不做 Accessories 适配**（只认 Curios）。卸装 Curios 时把槽位内容导回背包并记日志 |
| D30 GUI/HUD 底座 = owo-lib | **用 owo-lib 做 GUI 与 HUD**（技能树、属性面板、物品编辑、法力条），客户端随整合包下发（D10）。但**薄封装**：数据与状态不依赖 owo 的类型，`ui/` 包可整体替换；owo 缺失时降级为原版 `AbstractContainerScreen`（功能少但能用） |
| D31 spell_engine 兼容层 | **只读桥接 + 伤害 tag 白名单 + 可整体拆除**：不 import、不 `compileOnly`、不注册同义属性；按 `ResourceLocation` 查 `AttributeMap` 读 `spell_power:*` 当表达式输入；L2 乘区只作用于 `redtale_project:*` 的 DamageType，外部伤害原样放行。不接管它的 XP 等级收费与饥饿消耗。全部代码在 `compat/`，删包即结束。详见 `docs/DAMAGE-PIPELINE.md` §12 |
| D32 附魔强化走自研接口 | **另做附魔接口，不抬原版上限**（2026-11-15 12:56 Aki）：「本质上是为了测自制的附魔接口」。L1 schema → L0 datapack 生成（可 `/reload`）+ L2 唯一自定义组件 `redtale_project:scripted`（`EnchantmentEntityEffect`，一次注册、永不新增类）+ L3 调 M0 脚本层（effect/trigger/condition）。`enchantmentdisabler` 保留但不启用 `maxLevels`，只用于禁原版附魔。**接口成立的硬指标是「加第 N 个附魔只写 JSON5、不编译」**，不是「锋利能到 V」。详见 `docs/ENCHANT-API.md` |

| D33 物品更新与统一标记 | **改配置必须全服生效，且实例值不许被冲掉**（2026-11-16 02:00 Aki：「什么东西都要可改」「改过的物品要有统一 tag，像 MMOItems 一样全服刷新」）。三件事：①`weapon_attributes` **取消命名空间限制**，配置目录里放 `ns__path.json5` 即可覆盖任意外部定义（覆盖必 WARN；只引用不生成，引用与篡改靠「有没有那个文件」区分）；②`ContentData` 补 `schema`（结构版本）+ `content_rev`（定义修订号），`ItemContent` 补 `rev`——**改任何定义型字段必须 `rev`+1**；③`ItemUpgrader.ensure` 用 rev 快路径：只重建定义型字段（name/rarity/durability/attributes/preset），`rolled_stats`/`affixes`/`upgrade_level` **一个都不动**，只清「新定义里已不存在的键」并入日志；内容被删 → 标 ORPHAN 不销毁。刷新点 4 个（登录 / 开容器 / 区块加载 / reload 后分帧全量）+ 读路径惰性兜底。**同步是服务端推（`broadcastChanges`/`broadcastFullState`），不做客户端上报**；离线 `playerdata` 不直改。详见 `docs/ITEM-UPDATE.md` |

## 2. 改名成本（回答「以后改名麻烦吗」）

| 改什么 | 成本 | 时机 |
|---|---|---|
| 项目名 / 仓库名 / 目录 / README 标题 | **零成本**，随时改 | 任何时候 |
| jar 文件名、`archivesBaseName`、CurseForge 项目名 | 低，改配置重打包 | 任何时候 |
| 包名（`com.xxx.yyy`） | 中，IDE 全局重命名 | 发版前 |
| **Mod ID / 命名空间**（`redtale_project:foo`） | **高**：物品 ID、方块 ID、属性 ID、附魔 ID、配置目录、datapack 路径、存档里的 ItemStack 全带它 | **发版上线后基本改不动** |
| 存档物品 | 极难（要写 NBT 迁移） | — |

结论：**名字随便改，ID 只能定一次**。Mod ID 已定 `redtale_project`，此后不再动。

## 3. 上游真面目

| 来源 | 规模 | 复刻什么 | 许可 |
|---|---|---|---|
| MMOItems 6.10 | 676 类 | 属性值 `{base,scale,spread,max-spread}`、物品类型、宝石孔、套装、技能、掉落 | 闭源 |
| MMOCore 1.13 | 667 类 | 等级 / 22 类经验源 / 职业 / 属性点 | 闭源 |
| MMOInventory 1.9 | 86 类 | 槽位 + 4 类限制（职业/等级/Lore/权限） | 闭源 |
| **MythicLib 1.7** | **2505 类** | 属性注册表、伤害管线、占位符、GUI、兼容层 | 闭源 |
| EcoEnchants 2026.46 | 119 类 + 103 份附魔 YAML | **effect/trigger/condition 脚本模型** | 闭源 |
| eco 2026.46 | 7891 类 | 脚本引擎宿主、GUI 框架、SQL ORM | **MIT** |
| MythicMobs 5.14 | 12417 类 | 424 个机制 + 全 YAML 内容 | 闭源 |

真实工作量在 **MythicLib（2505 类）**，不在这五个插件本身。

## 4. 架构：一个脚本层，四个内容面

EcoEnchants 的 103 个附魔没有一行代码，全是 `effects: [{id, args, triggers}]`。所以核心不是「附魔系统」，而是：

```
┌───────────── scripting core ─────────────┐
│ effect 注册表    │ trigger 注册表 │ condition 注册表 │
│ 数值表达式 %level% / 曲线 / 随机          │
└──────────────────────────────────────────┘
        ↑ 复用            ↑ 复用            ↑ 复用
   items(技能/宝石)   enchants(附魔)   mobs(怪物技能)
```

四个内容面都只是「元数据 + effect 列表」，新内容 = 写配置；新效果类型 = 写一个 effect 实现。

模块边界（源码集，不对外暴露）：

| 源码集 | 职责 |
|---|---|
| `core` | 属性注册表、`StatValue{base,scale,spread,maxSpread}`、伤害管线、脚本层（effect/trigger/condition）、配置热载、GUI 基座 |
| `items` | 物品类型、武器、宝石与孔、套装、技能绑定、掉落表 |
| `inventory` | Curios 槽位映射、4 类限制、装备面板 |
| `enchants` | 附魔 schema → 生成内置 datapack → 真实 `Enchantment`；自定义 effect component |
| `mobs` | 模板实体、属性/等级缩放、技能原语、刷怪规则 |
| `progression` | 等级、经验源、职业、属性点（对应 MMOCore） |

## 5. 实体：少量 EntityType + 按怪配置（回答「模型/ID/技能/音效能不能不同」）

**能，且这是推荐路线。** 前提是我们自己写实体类，把可变项做成「同步数据 + 配置」。

固定不变的（改一个就要换 jar）：

| 项 | 原因 |
|---|---|
| `EntityType` 注册项 | `BuiltInRegistries` 引导期冻结，NeoForge 只允许动态注册 datapack registry |
| 实体类（AI 基类、寻路类型、`getDimensions`） | 类决定行为骨架 |
| 渲染器类型（`EntityRenderer` 的注册位置） | 但渲染器内部可以读数据 |

可按怪配置的（不换 jar）：

| 项 | 做法 |
|---|---|
| 模型 / 贴图 / 动画 | 服务端同步 `model_id`，渲染器查表 → GeckoLib 的 `.geo.json` + `png`（**服上已有 GeckoLib 4.9.3 / AzureLib 3.1.19**），无需为每只怪注册实体。PlayerAnimator 2.0.4 有 1.21.1 NeoForge 版但**服上未装**，只在要做「玩家自身动作动画」时才引入（它是客户端动画库，实体动画 GeckoLib 已够） |
| 音效 | 实体类里 `getAmbientSound/getHurtSound/getDeathSound` 读同步的 `sound_id` |
| 技能 | 实体持一个「技能控制器」，从配置读 ability 列表 + 冷却；行为原型只提供执行入口 |
| 属性 / 等级 / 掉落 / 装备 | 生成时套用配置（属性走 `AttributeMap`，装备走 `setItemSlot`） |
| 体积 | 1.20.5+ 的 `minecraft:generic.scale` 属性**会缩放碰撞箱**，小怪/巨怪靠它区分 |
| 自定义 ID | 我们自己的内容 ID（`redtale_project:mob/xxx`）存在实体数据 + scoreboard tag 里 |
| 刷怪蛋 | 不按实体类型给，做一个通用「刷怪蛋」物品写 mob id |

必须接受的 4 条限制：

1. **碰撞箱只能等比缩放**，不能一个模板同时出「细高」和「扁宽」。
2. `/kill @e[type=...]`、`/data get entity @e[type=...]` 只能按模板类型筛；按怪筛要用 tag 或 `data get`。
3. 模型与音效是**客户端资源**：需要一个资源包（或客户端模组内置），音效还必须在客户端 `sounds.json` 里注册。
4. 第三方模组/调试工具看到的是「一种实体」，不是 N 种。

结论：6~8 个原型（近战 / 远程 / 施法 / 召唤 / 冲锋 / 飞行 / 精英 / 环境）足够撑 60 只/年，新增怪纯配置。只有出现「原型装不下的行为」时才加原型（换 jar）。

## 6. 里程碑

| 阶段 | 内容 | 出口条件 |
|---|---|---|
| **M0** 地基 | Gradle(JDK21，**镜像源 + 服务端 libraries 直编**，见 `docs/BUILD.md`) + 配置热载 + 脚本层骨架（注册 effect/trigger/condition 各 1 个示例） | `/redtale reload` 生效，一条配置能触发一个 effect |
| M1 属性 | 属性注册表 + `StatValue` 四段式 + 伤害管线 | 3 个自定义属性能算出伤害并显示在 Lore |
| M2 武器 | 物品类型（含**白板化** D21）+ **随机词条**（D22）+ **消耗品与修理**（D23）+ 等级门槛 + Lore + 掉落表 + **物品更新系统**（D33） | 自定义剑打出自定义伤害/暴击，词条在 tooltip 与结算同源；一件消耗品能右键生效、一件磨刀石能修耐久；**改 json5 的 `rev`+1 后，已发放物品登录即更新且 `rolled_stats` 不变**（U1~U10 全绿，见 `docs/ITEM-UPDATE.md` §9） |
| M3 宝石/套装 | 孔位、镶嵌/取出、套装件数加成 | 3 件套触发加成，Lore 正确 |
| M4 附魔 | **自研附魔接口**（D32）：schema → datapack 生成 + `redtale_project:scripted` 组件 + 2 个示例（纯属性 / 脚本触发） | V1~V11 全绿（`docs/ENCHANT-API.md` §6）；硬指标是「新加一个附魔只写 JSON5、不编译」（V11），不是「锋利能到 V」 |
| M5 技能 | 技能原语 + 绑定 + 冷却/消耗 | 右键释放技能，冷却消耗正确 |
| M6 怪物 | 模板实体 + 技能/掉落/等级缩放 + **原版刷怪替换**（D26） | 配置出来的怪能放技能并掉落；野外原版刷出的怪按概率被替换 |
| M7 进度 | 等级、经验源、职业、属性点、**技能树**（D25）、**专业**（D24，后置） | 打怪给经验、升级加属性点；点满一条分支并解锁技能；洗点能完整回滚 |

## 7. 未定（2026-11-15 清账后）

已答：客户端形态 → 允许（D10）；测试服 → 已建（D13）；附魔范围 → 先做接口，优先「原版附魔强化」类，数量尽量多（见 §10）。

仍空：

1. **属性清单要预制多少条**：属性是启动期注册表，**不能热加**，而且现在不复用 `spell_power`，等于要自己覆盖法强/暴击/治疗那些品类。**已定一次注册 80 条**（Aki 2026-11-15：64 实用 + 16 预留；近战 12 / 防御 18 / 法术资源 18 / 采集移动 10 / 通用 6 / 预留 16）。等反编译 MythicLib 后按它的表补齐再定。
2. **技能原语第一批做几个**：建议 24 个（直伤 / 范围 / 投射物 / 位移 / 增益 / 减益 / 召唤 / 治疗），够拼出 80% 的技能。
3. **套装首批做几套**：数据可热加，先做 2 套示范即可，不是阻塞项。
4. ~~**功能面缺口（2026-11-15 第二轮审计）**~~ → **已裁决（D21~D31，2026-11-15 12:45）**：做词条/消耗品修理/专业/技能树/刷怪替换；不做工作台与矿脉；spell_engine 走只读兼容层；Curios 可选；GUI 用 owo；经济可选桥接；自定义装备**白板化**。依据与取舍见 `docs/GAP-AUDIT.md` §5、`docs/ITEM-MODEL.md`、`docs/SKILL-TREE.md`。原文留档：：见 `docs/GAP-AUDIT.md`。上游还有 7 项没进里程碑（随机词条 / 自定义工作台 / 矿脉生成 / 消耗品与修理 / 专业 / 技能树 / 原版刷怪替换），另有 9 处与正式服已装 mod 的撞车（`spell_power` 的 19 条属性、`spell_engine` 吃原版 XP 等级、伤害乘区范围、三套饰品系统、`lootr`、`enchantmentdisabler`、经济归 RedtaleEconomy、GUI 是否用 owo）。对应协作板 Q-009 ~ Q-011。
5. **职业要不要照 MMOCore 的分类**：还是按赤物语的世界观自己定（战士/游侠/法师/…）。数量与命名等 M7 再定。


## 8. 测试服 `E:/server-test`（D13）

| 项 | 值 |
|---|---|
| 版本 | NeoForge **21.1.257** / MC 1.21.1（与正式服同版，libraries 直接复制，177 MB） |
| 位置 | `E:/server-test`（world 独立，不碰正式服） |
| 端口 | 游戏 25567 / RCON 25577（正式服 25565 / 25575，不冲突） |
| 内存 | `-Xms2G -Xmx4G`（正式服 7G/12G，故意压低） |
| `level-type` | `minecraft:normal`（正式服是 `wover:normal`；测试服不装 WOVER） |
| `online-mode` | `false`（同正式服） |
| 启动 | `run-test.bat`，或 `java -Xms2G -Xmx4G @libraries/net/neoforged/neoforge/21.1.257/win_args.txt nogui` |

### 8.1 已装模组（12 个，全是库型前置，无玩法内容）

```
architectury 13.0.11          cloth-config 15.0.140     kotlinforforge 5.11.0
resourcefullib 3.0.12         glitchcore 2.1.0.2        curios 9.5.1
geckolib 4.9.3                azurelib 3.1.19           attributefix 21.1.3
bookshelf 21.1.81             prickle 21.1.11           terrablender 4.1.0.8
```

（`attributefix` 硬依赖 `bookshelf` + `prickle`，首次启动就是因为缺这两个报的 FATAL，已补。）

### 8.2 实测

首次成功引导：`Done (5.354s)!`，12 mods，RCON 起在 25577，`Preparing spawn area` 正常。

### 8.3 用法约定

- **只加不改**：需要测某个 mod 冲突时，临时把那个 jar 丢进 `mods\`，测完移除。不要把它当成正式服的副本。
- 正式服任何 `world` / `mods` / `config` 都不能从这里同步回去。
- 测试服 `world` 可以直接删掉重建（本来就是一次性的）。

## 9. 热更新边界：什么能 reload，什么必须换 jar（回答 G / D17）

> 完整方案（四个容器、通用组件、热加载路径、代价、客户端侧）见 `docs/HOT-UPDATE.md`。本节只留结论。

这是本项目最重要的一条工程约束。判断标准是**「它是不是注册表项」**。

### 能热加（写配置 + `/redtale reload`）

| 内容 | 为什么能 |
|---|---|
| **武器 / 装备 / 宝石 / 材料** | 用**原版 `Item` + 自定义 DataComponent**，不是每件一个 `Item` 类。1.21 的 data component **值**可以任意，注册表项只有「组件类型」 |
| **套装定义**（件数、加成） | 纯数据，挂在组件的 `set_id` 上 |
| **附魔** | 生成 datapack JSON 后调 `ReloadableServerResources` 重载；`Enchantment` 是 datapack registry，**可以**运行时重载 |
| **怪物定义**（属性/技能/掉落/模型/音效/体积） | 模板实体 + 数据，见 §5 |
| **技能配置**（原语组合、冷却、消耗） | 数据 |
| **经验曲线 / 等级上限 / 职业开关 / 职业列表** | 数字与开关 |
| **掉落表、刷怪规则、数值闸门** | 数据 |

### 不能热加（必须换 jar）

| 内容 | 为什么 |
|---|---|
| **新 EntityType** | `BuiltInRegistries` 引导期冻结（这也是 D9 要「预制原型」的原因） |
| **新 Attribute** | 同上，属性注册表启动冻结 → §7 第 1 条要「一次注册 48 条」 |
| **新 effect / trigger / condition 原语** | 是代码，注册在 Java 侧 |
| **新 DataComponent 类型** | 组件**类型**是注册表，值才是数据 |
| **新方块 / 新物品类**（需要自定义行为时） | 纯展示物品不需要；有特殊右键逻辑就得有类 |

结论：**套装后期加 = 写一份 JSON5 + reload，完全不换 jar。** 经验曲线/等级上限/职业开关同理。真正会逼你换 jar 的只有「新原型实体」「新属性」「新效果原语」三类，所以这三类要在 M0/M1 一次性预留够。

## 10. 附魔第一批范围（E）

分三档，按「能复用原版组件」的比例排优先级：

| 档 | 内容 | 实现方式 | 数量 |
|---|---|---|---|
| **一档** | 原版附魔强化（超级锋利、超级保护、超级效率、超级耐久、多重射击强化…） | **纯数据包**，复用 `minecraft:damage` / `damage_protection` / `attributes`（效率走属性）/ `item_damage` / `projectile_count` 等原版组件 | 15~20 |
| **二档** | 原版组件的组合（吸血=伤害+自我治疗、荆棘强化、经验加成） | 数据包 + 少量原版组件组合 | 10~15 |
| **三档** | 触发式（命中流血、击杀爆炸、受伤反弹、周期性 buff） | **脚本层**（effect/trigger/condition） | 按需 |

一档几乎零风险，先做；二档验证组件组合的边界；三档才是真正吃脚本层的地方。

**组件名核对（2026-11-15，字节码实测见 `docs/ENCHANT-API.md` §1 F3）**：1.21.1 的 `EnchantmentEffectComponents` 只有 30 个组件，**没有 `block_break_speed`**——`block_break_speed` / `mining_efficiency` 是**属性**，效率类附魔要写 `minecraft:attributes` + `{"attribute": "minecraft:player.mining_efficiency", ...}`。三档的分界不变，但「三档」现在有具体落点：原版 `post_attack` / `tick` / `hit_block` 等触发组件 + `redtale_project:scripted` 调脚本层（D32），**不自建触发器**。

**与 D 的兼容**：一档全部走 `minecraft:damage` 平加池 + `#minecraft:exclusive_set/damage` 互斥，所以「锋利 + 超级锋利」不可能同时生效，也不可能叠加出巨量伤害。详见 `docs/DAMAGE-PIPELINE.md` §8。

**急迫与攻速（2026-11-15 定稿，D18/D19）**：原版 `minecraft:haste` 不直接改 `attack_speed`（1.20.1 硬编码在 `Player.getDigSpeed()`，1.21.1 只加 `player.block_break_speed`）。但 Aki 在 1.20.1 服上确认「急迫 → 攻速」是既有玩法，且 1.21.1 的 SimplySwords 已把它换成独立效果（`ImplicitHasteEffect` +10%、`FerocityEffect` 0.10/层），说明作者也认这条玩法。**我们按 Aki 的决定把它作为特性保留**：`haste_attack_speed_per_level` 默认 **0.10**、`soft_cap` 默认 **0**（不饱和），见 §12 与 D19。

## 11. 数值管线速查（D12 / D16）

完整设计在 `docs/DAMAGE-PIPELINE.md`，这里只放结论。

```
L0 基础：原生 attack_damage + 原生 minecraft:damage 附魔（原版算好，不动）
L1 平加：我们的 AttributeModifier（带固定 id，可整件卸下）
L2 乘区：LivingIncomingDamageEvent 上乘，先加后乘
         默认不设任何上限（percentCap / condCap / condCount / damageCap 全为 0）
L3 兜底：负数归零、超 1e9 硬顶、超阈值记日志（只观测，不拦）
```

四条硬规矩：

1. **绝不 `setAmount(我们算的)`** —— 会把前面 19 个 mod 的加成一并抹掉。
2. **先加后乘**：10 个 +20% 是 +200%，不是 6.19 倍。
3. **不设平衡上限**，但闸门保留为配置项（`0 = 关闭`），需要时一行配置就能开。
4. **tooltip 与结算共用同一个 `settle()` 实现**，否则会出现「写着 12.4 打出 9」。

攻速：mixin `Player#getCurrentItemAttackStrengthDelay` 一个点，同时覆盖原版与 BetterCombat（BetterCombat 的 `getAttackCooldownTicksCapped` 就是在它外面套 `max(cap)`）。默认不饱和（`attackSpeedSoftCap = 0`）。

BetterCombat 的两条现实约束（`config/bettercombat/server.json5` 实测）：`allow_fast_attacks = true` 绕过受伤无敌帧 → **攻速是 DPS 的线性乘数**；`attack_interval_cap = 2` → 任何来源的攻速最多每秒 10 次。

**攻速来源是开放的**：`attack_speed.json5` 里声明「哪个效果/属性贡献多少攻速」。**急迫默认 0.10/级（D19，保留 1.20.1 玩法）**，其余外部来源默认 0 以免重复计；`attackSpeedSoftCap` 默认 0 = 不饱和。我们只读**最终属性值**，任何来源（咖啡因、Ferocity、双持、我们自己的规则）都自动被算进去。详见 `docs/DAMAGE-PIPELINE.md` §4.2 / §12。


## 12. 攻速来源表（D18）

我们不判断「谁对谁错」，只声明「谁能加攻速」。所有条目都写进 `ATTACK_SPEED` 属性，用 `ADD_MULTIPLIED_TOTAL` 相加。

| 来源 | 数值 | 归属 | 我们要做的 |
|---|---|---|---|
| 武器基础 | 剑 −2.4（4.0 → 1.6） | 原版 | 不动 |
| BetterCombat 双持 | ×1.2（属性 modifier） | 它自己 | 不重复加 |
| 咖啡因 Caffeinated | +20% | Farmer's Respite | 不重复加（默认表置 0） |
| 茶 Tea | +5% | Youkai's Homecoming | 不重复加 |
| Ferocity（Twisted Blade） | 1.21.1：`+0.10/层`，最多 15 层 → 满层 **+150%** | SimplySwords | 不重复加 |
| Implicit Haste（twinblade / chakram 命中触发） | `+10%` 固定（不随等级、不随层数） | SimplySwords | 不重复加 |
| **急迫 Haste（原版药水）** | 原版不加；**我们自己按 0.10/级换算**（I +10% … VIII +80%），默认开启 | 我们 | 加（D19，保留玩法） |
| 装备 / 宝石 / 套装 | 内容配置里的 `attack_speed` | 我们 | 加 |
| 技能 buff | 原语 `modify_attribute` | 我们 | 加 |

> **2026-11-15 复核（扫的是 1.21.1 正式服实际 jar）**
> `simplyswords-neoforge-1.70.2` 里 `MobEffects.DIG_SPEED` 出现 10 处，全是 `addEffect` 派发（BattleStandard / Waxweaver / Storm's Edge / Zephyr / Unstable / FlameSeed / Onslaught / DeathKnell / Phase4 / Phase5），**没有一处把它换算成 `ATTACK_SPEED`**；真正加攻速的是 `effect/ImplicitHasteEffect`（`+0.10`、固定）与 `effect/FerocityEffect`（`config.twisted_blade.attackSpeedPerStack`，默认 0.10/层）× `TwistedBladeAbilityManager#updateMasteryAttackSpeed` 按层数下发。
> 1.20.1 的 `1.56.0` 同样没有这个换算（mixin 只有 `LivingEntityMixin` / `ServerPlayerEntityMixin`，`HasteSwordItem` 里也没有 `ATTACK_SPEED`/`DIG_SPEED` 的引用）——当年是这把剑**把急迫当攻速卖**，tooltip 写的 attack speed，buff 栏写 Haste。
> **对 D18/D19 的影响（2026-11-15 定稿）**：代码里没有「急迫→攻速」的换算，所以这个手感**只能由我们补**——`haste_attack_speed_per_level` 默认 **0.10**，把玩家在 1.20.1 上感受到的那套玩法在 1.21.1 上显式实现出来，并且 `soft_cap = 0` 不饱和。**投放层不禁叠**（急迫 + Ferocity + 咖啡允许共存），只在 `/redtale attr` 与 tooltip 里如实展示每一级来源。

> **2026-11-15 追加：1.20.1 的「康普茶 × 星芒」为什么能做出 5 分钟急迫 VIII**
> 实测配置（`E:\server\config\simplyswords_main\unique_effects.json5`）：`celestialSurgeDuration=120`、`celestialSurgeStacks=6`、`celestialSurgeCooldown=120`。
> 机制：`HelperMethods.incrementStatusEffect(entity, effect, dur, inc, cap)` = 时长取 `max(现有, dur)`、等级 `+inc`、封顶 `cap`；星芒第二段对急迫传 `(dur/2=60 tick, +6, cap 7)`。
> 康普茶（Brewin' And Chewin 3.0.6）给 `haste` **I / 6000 tick（5 分钟）**。于是：喝康普茶 → 按一次星芒（amp 0→6，时长仍是 6000）→ 再按一次（amp 7 = 急迫 VIII，时长仍是 6000）。**这就是「长时间急迫」的全部秘密：康普茶供时长，星芒只抬等级，且时长永远取 max。**
> 1.21.1 现状：B&C 4.5.0 的康普茶改成 `haste` **II / 1200 tick（60 秒）**；SimplySwords 1.70.2 把星芒重写成 `StarsEdgeAbilityManager`（冲刺 + 记录位移 + 延迟引爆），用到的效果只有 `ABSORPTION / GLOWING / INVISIBILITY / SLOWNESS / SPEED`，**没有 HASTE**，`celestialSurge*` 配置键已不存在 → **这条 combo 在 1.21.1 不可复现**。
> 1.21.1 真正存在的「喝酒→攻速」是 B&C 4.5.0 新增的 `Raging`：每层 +5% `ATTACK_SPEED`（`ADD_MULTIPLIED_TOTAL`），最多 4 层（+20%），出手叠层，`RagingAttachment` 直接读 `getCurrentItemAttackStrengthDelay` 算衰减。

两条铁律：

1. **同一个来源只算一次**。默认表里把别人已经给的（咖啡、茶、Ferocity）置 0，就是为了避免「喝咖啡 +40%」这种事。
2. **tooltip 与 `/redtale attr` 必须同源**。都调用同一个 `AttributeBreakdown`，它遍历 `AttributeMap` 里所有 modifier，按 id 分组 —— 别人加的也在里面，所以玩家看到的永远等于服务器算的。

`/redtale attr` 是 M1 的验收项，不是可选项：这是唯一能让「急迫到底加没加、加了多少」不靠猜的办法。

## 13. 进度台账（S7 队列每轮追加）

> 只追加，不改上面任何已定决策。详细证据见 `docs/ROUND-*.md`。

| 轮次 | 日期 | 里程碑 | 做了什么 | 结论 |
|---|---|---|---|---|
| R1.5 | 2026-11-15 | 构建链修复 | Aki 拍「用镜像源」→ 实测 neoform-runtime 五家镜像全 404；改为镜像源 + `server-srg`/`neoforge-universal` 直编（`compileOnly files(...)` 顺序敏感），`build.gradle` 重写、旧 MDG 脚本留 `build-mdg.gradle.disabled`、新增 `docs/BUILD.md` | `gradle build --offline` → **BUILD SUCCESSFUL 19s**，产物 44 KB 进测试服 `Done (2.353s)`。`runClient` 仍不可用（需 NFRT） |
| R1.6 | 2026-11-15 | M4 立项（D32） | Aki 答 Q-012「**另外做，因为本质上是为了测自制的附魔接口**」→ 新增 `docs/ENCHANT-API.md`：四层接口、30 个 effect 组件全表（javap 实测，纠正 `block_break_speed` 实为属性）、单组件 `redtale_project:scripted` 设计、V1~V11 验收矩阵、3 条开工风险；`PLAN.md` D32 + M4 出口条件 + §10 组件名同步 | M4 出口从「示例附魔能附上」改为「**加第 N 个附魔只写 JSON5、不编译**」。开工前先验 R1（`ENCHANTMENT_ENTITY_EFFECT_TYPE` 能否 `RegisterEvent`）与 R2（生成物落在可 reload 的 datapack） |
| R1 | 2026-11-15 | **M0：出口条件已达成** | Gradle 骨架（MDG 2.0.148 + NeoForge 21.1.257 + wrapper 8.8）+ 22 个源文件：自写 JSON5 解析器、配置目录管理、脚本层三张注册表（effect 2 / trigger 2 / condition 3）、`/redtale reload\|status\|list\|fire`、默认脚本自动落地、`tools/offline_check.py`、`tools/rcon.py` | 测试服实测通过：启动即加载 1 条脚本、`fire` 跑通、改文本 reload 立刻生效、坏配置只跳过坏的那条。**Gradle `build` 被 `maven.neoforged.net` 网络阻断**（`neoform-runtime` 五个镜像全 404），本轮用离线 javac + 手工打 jar 出产物，详见 `docs/ROUND-M0.md` |
| R2 | 2026-11-15 | **M1 第一步：属性注册表 + 来源拆解** | 80 条属性成表（`core/attr/`，`AttributeSpecs` 类初始化断言 80 条 / id 不重复）；66 条自建 `DeferredRegister<Attribute>` + `setSyncable(true)`；`EntityAttributeModificationEvent` 挂到 99 个 EntityType（6534 处）；`/redtale attr <属性> [目标]` 三乘区拆解 + `attr list`；`tools/gen_attr_lang.py` 生成 zh_cn/en_us 各 66 键 | 构建 `BUILD SUCCESSFUL in 8s`、测试服 `Done (2.328s)`。实测：原版 `/attribute` 能读写 `redtale_project:*` 且显示英文名（NeoForge 服务端 LanguageHook 读了 jar 内 lang）；拆解 (3+5)×1.25×1.4 = 14 与实际值一致；原版 `minecraft:effect.speed` 的 modifier 同样被列出。**玩家上下文 attack_speed 未验证（无客户端）**。详见 `docs/ROUND-M1-ATTR.md` |
| R3 | 2026-11-15 | **M1 第二步：数值核心 + 声明式攻速 + 第一个 mixin** | `core/math/`（`Caps`/`Sanity`/`Settle`/`StatValue`/`AttackSpeedCurve`/`DamageRules`）+ `gradle selftest` 离线单测；`attack_speed.json5` + `damage.json5` 默认落地 + 热重载；`AttackSpeedApplier`（每 5 tick 写 transient modifier，固定 id，先移除再加）；mixin `Player#getCurrentItemAttackStrengthDelay` + `redtale_project.mixins.json` + `mods.toml [[mixins]]`；`/redtale speed` / `speed probe` | `selftest` **28/28 PASS**；mixin 三重证据（jar 条目 / `Mixing ... into Player` 日志 / 导出类 `handler$zdi000$redtale_project$redtale$applyAttackSpeedRules`）；`soft_cap=4.0` 时 1024 次/秒实测 **5 tick**（对上 DAMAGE-PIPELINE §9 第 3 条）；**发现并修掉急迫双计**：1.21.1 原版 `MobEffects.DIG_SPEED` 自带 `ATTACK_SPEED +0.1/级`，我们默认 0.10 会让急迫 II = +40%，改为自动让位后实测 **4 → 4.8**。详见 `docs/ROUND-M3.md` |
| R4 | 2026-11-15 | **M1 收尾：L2 伤害乘区** | `core/damage/`（`MultiplierRules` 白名单 / `DamageLayer` 在 `LivingIncomingDamageEvent` **LOWEST** 上乘因子 / `DamageTrace` 环形记录）；`damage.json5` 新增 `multiplier` 段（默认 `["redtale_project:*"]`、百分比只取 `physical_damage`）；自建 datapack `data/redtale_project/damage_type/verification_strike.json`（`scaling: never`）；`/redtale damage` / `damage probe` / `damage check <id>`；`gen_attr_lang.py` 加 `EXTRA`（非属性 lang 键不会被重新生成抹掉）；selftest 28 → **36 PASS** | 三组实测同一数值打出 **10 / 12 / 10**：自建类型+无属性 → ×1.0；自建类型+`physical_damage 0.2` → **×1.2 = 12**；`minecraft:generic` → 放行 10。`/redtale damage` 能列出每次的因子与百分比池；`reload` 后计数归零。**只乘因子不写绝对值**（`amount × settle(amount)/amount`）。详见 `docs/ROUND-M4-DAMAGE.md` |
| R5 | 2026-11-15 | **M2 第一步：内容组件 + 14 基底 + 白板化 + tooltip** | `items/`（`ContentData` 单组件 7 字段 / `ItemBase` 14 基底 / `RedtaleItems` / `ItemContent` 解析 / `ItemContentRegistry` 快照 / `ItemFactory` 建栈 / `ContentTooltip` / `ItemTooltipHook` / `StatFormat`）；默认配置 `items/demo_{longsword,chestplate,robe}.json5`；命令 `/redtale items\|give\|tooltip\|whitening`，`status` 加内容计数 | 构建 exit 0、selftest **46 PASS**（36→46）；测试服 `Done (2.189s)`。**白板化实测 `3 → 20 → 0`**（原版皮革胸甲 3、写 20 的胸甲 20、0 属性布袍 0 —— `+0` 占位堵住回落）；tooltip 实测 `≈ 9.6 /次`（1.0+7=8 ×1.2）与 `12.5 tick · 1.6 次/秒`。三条新事实：玩家 attack_damage 基值 **1.0**（非注册表 2.0）、装备属性要等 tick 才进 `AttributeMap`、自建属性基值 0 故内容数值只能 `ADD_VALUE`。详见 `docs/ROUND-R5-ITEMS.md` |
| R6 | 2026-11-15 | **M2 第二步：条件乘区（pve/pvp/undead）** | 新类 `core/damage/TargetClass`（目标分类唯一实现：玩家→pvp；亡灵→pve+undead；其它→pve）；`MultiplierRules` 加第 4 组件 `conditionalAttributes`（+三参兼容构造 / `describe()` 打条件段 / 解析 `conditional_attributes`，错键告警）；`DamageLayer` 拆 `sumAttributes` + 新增 `sumConditional`；默认 `damage.json5` 加条件段（三条全开） | 构建 exit 0、selftest 46 → **55 PASS**。四组实测（`verification_strike`，基数 10，攻击者 husk）：牛+pve0.2 → **×1.2=12**；牛+pve0.2+undead0.3 → **×1.2**（undead 不算）；husk+pve0.2+undead0.3 → **×1.5=15**；牛+只剩 pvp0.5 → **×1=10**。`MobEffects` 之外的前提也已字节码确认（`EntityTypeTags.UNDEAD` / `EntityType#is(TagKey)`）。**pvp 真目标未验（无客户端）**。详见 `docs/ROUND-R6-COND.md` |
| R7 | 2026-11-16 | **双队列 R2 轮：验收 T-0001 + 打通武器动作链路** | 验收 T-0001 → `VERIFIED`（3 条全过）；派 **T-0004**（附魔 schema→datapack 生成器，D32 的 L1→L0）；自研 **R7-1**：`ItemFactory.applyWeaponPreset` 用 `BuiltInRegistries.DATA_COMPONENT_TYPE` 按字符串取 `bettercombat:preset_id` 并挂到物品（零 import），`ContentTooltip` 追加「动作 <id>」行；selftest 仍 **55 PASS** | 测试服三轮 `Done (2.3~2.5s)`。实测 `test_sword → 动作 redtale_project:test_sword`（自家生成）、`demo_longsword → 动作 bettercombat:claymore`（外部命名空间只挂引用不生成文件）。**字节码证据**：`WeaponRegistry.getAttributes(ItemStack)` 第一步 `stack.get(WEAPON_PRESET_ID)`，组件缺失才回落按物品 id 查 → 「只生成数据包不挂组件」= 整条链不通，R6 的缺口已闭。新发现：运行期新生成的数据包**不会自动启用**（`probe_pack` 实测：重启即自动启用，运行期需一次 `/datapack enable`）。详见 `docs/ROUND-R7-WEAPON.md` |
| R8 | 2026-11-16 | **双队列 R3 轮：验收 T-0002 + 数据包自动启用（R7 遗留闭合）** | 验收 T-0002 → `VERIFIED`（3/3，测试服 `content list` 4 行 = 4 份 `items/*.json5`）；派 **T-0005**（`tools/gen_item_lang.py`，14 基底物品 lang 全缺）；自研 **R8-1** 新包 `core/datapack/PackEnabler.java`（`repo.reload()` → `addPack` → `server.reloadResources(selectedIds)` 三步）+ `RedtaleCore.reload()` 接线 2 行 | 测试服两轮：**删掉 `world/datapacks/redtale_project` 后重启**，`Done (2.449s)` → 日志 `生成数据包状态：ENABLED_AND_RELOADED` → `/datapack list` 直接见 `file/redtale_project (world)` **无需手动 enable**（R7 的失败场景已复现并修掉）；运行期再删包 + `/redtale reload` → 文件重生成、仍选中（`ALREADY_SELECTED`）、`/datapack list` 不变。无 `StackOverflow`、无 redtale ERROR、只重载一次。**启动期不主动重载**（`isRunning()` 为假时只选中）。详见 `docs/ROUND-R8-PACK.md` |
| R9 | 2026-11-16 | **双队列 R4 轮：暴击入口（M2 第三块）** | 卡板：无 `[DONE]` 可验、在制品 3/3 已满 → **未派新卡**。自研：`core/damage/CritRules.java`（`crit.json5` 解析）+ `CritLayer.java`（`CriticalHitEvent` @LOWEST，掷暴击率 + 写倍率）+ `GameHooks` 注册 + `crit.json5` 默认落地 + `/redtale crit` 与 `crit probe`（FakePlayer 真打木桩四组对照） | `build --offline` exit 0（jar 172409 B）、`selftest` 仍 **55 PASS**、测试服 `Done (2.330s)`。四组实测 **100 / 200 / 100 / 100**：强制暴击生效（×2.0）、且 `power=1.0` 时回到基线 ⇒ **我们的倍率替换进场值，原版 1.5 不叠加**。`CommonHooks.fireCriticalHit` 字节码无门禁（永远返回事件）；BetterCombat jar 内 `CriticalHitEvent` **零引用**（它不自己算暴击）。热重载实测：`force_on_roll: false` → 四组全 100 且判定文案变「符合预期」。**卡板**：本轮 S8 把 **T-0003 交付 `[DONE]`** → 验收 **3/3 通过 → `VERIFIED`**（build exit 0 / `grep -c parseDefs|parsePools` = 1/1 / jar 内 `items/AffixPools` 4 条）；随即**派 T-0006**（`ItemUpgrader.plan` 差异单纯函数，D33 的判定核心），在制品 T-0004/T-0005/T-0006 = 3/3。**并行写入者**：Aki 于 02:00 新增 **D33 物品更新与统一标记** + `docs/ITEM-UPDATE.md`，并把 `ContentData` 扩到 9 字段（+`schema`/`content_rev`）、`ItemContent` 加 `rev`——本轮只在既有接口上叠加，未改其口径。详见 `docs/ROUND-R9-CRIT.md` |
| R10 | 2026-11-16 | **物品更新系统（D33）**：Aki 指出 `weapon_attributes` 不该有命名空间限制，并要求像 MMOItems 的统一刷新 | ①查证：`weapon_attributes` 是 **BetterCombat** 的 datapack registry，与 MMOItems 无关；原「只处理自家前缀」是自己加的保守阀门；②`WeaponAttributesGenerator` 改「文件名定命名空间」（`ns__path.json5`，覆盖外部必 WARN，`normalizeRef` 补全裸名）；③`ContentData` +`schema`/`content_rev`、`ItemContent` +`rev`（json5 可写）、`ItemFactory` 写入当前 rev；④新增 `docs/ITEM-UPDATE.md`（三层身份模型 / 4 刷新点 + 惰性兜底 / 服务端推送同步 / U1~U10 矩阵）；⑤`PLAN.md` D33 + M2 出口条件 | `build --offline` exit 0、`selftest` 仍 **55 PASS**。关键取舍写进文档：**迁移只重建定义型字段，`rolled_stats`/`affixes`/`upgrade_level` 一个都不动**；不白送新键；删键必记日志；rev 相等走快路径不写盘；离线 `playerdata` 不直改；同步是服务端推、不做客户端上报 |
| R11 | 2026-11-16 | **词条 roll（D22 第二层）**：接受 T-0004、派 T-0007 | ①验收 **T-0004 → `VERIFIED`**（3/3 + 离线探针 15/15：3 份写出 / 子目录 / 外部 ns / 缺 `supported_items` 跳过 / 幂等）；②`AffixPools.Def.stats` 升 `Map<String,StatValue>`（R9 欠账）+ 键归一；③新增 `items/AffixRoller`（纯函数，槽位/等级区间/同组互斥/不放回/累加）+ `ItemFactory.build(content, Random)` 接 roll，`rolledStats`/`rolledKeys`/`affixes` 一次写全；④`RedtaleCore` 加 `affixDefs()`/`affixPools()` 快照 + `ConfigStore.DEFAULT_FILES` 加 4 份词条默认；⑤tooltip 加「词条 N：…」行 | `build --offline` exit 0、`selftest` **55 → 70 PASS**；测试服 `Done (` 后 `/redtale reload` = **13 份配置文件**，`tooltip demo_longsword` 三摇：`sharp·of_the_bear` → **12.096**（(1+7+2.08)×1.2）、`heavy·of_the_bear` → **15**（(1+7+4)×1.25）。同组互斥、`per_item_level` 曲线、词条与内容进同一百分比池三条全部实测成立。详见 `docs/ROUND-R11-AFFIX.md` |

| R12 | 2026-11-16 | **物品更新落地（D33 的 `ensure` + 三个刷新点）**：验收 T-0006、派 T-0008 | ①验收 **T-0006 → `VERIFIED`**（3/3 + S7 自写独立探针 **14/14**：null/ID 不匹配/schema 落后/快路径/删键不白送/保序/不可变/20 万次快路径 < 200ms）；②`ItemUpgrader.ensure(ItemStack)` = D33 唯一写回点，四条出口 `NOT_CONTENT`/`ORPHAN`/`UNCHANGED`/`UPGRADED`，取值分派（`rolled_keys` 留旧值 / 其余跟新定义 / 删键逐个记账）；③新 `core/hook/ItemUpgradeHooks`（登录 / 换维度 / 复活 / 开容器 / 区块加载）+ `GameHooks` 注册 1 行；④**派 T-0008**（消耗品 `use` 段解析器，D23 第一层），在制品 T-0007+T-0008 = 2/3 | `build --offline` exit 0（jar 207220 B）；测试服 **1 次启动**实测三组：A 组 `rev 0→3` → `generic.attack_damage` **5.0 保留**（在 `rolled_keys`）、`physical_damage` **0.1→0.25**（跟新定义）、`ghost_key` 删除 + 逐条日志、`custom_name`/`rarity epic`/`max_damage 500` 重建；B 组 `rev` 相等、C 组孤儿（`ghost_sword`）组件**逐字未变**。日志 `刷新点 chunk[minecraft:overworld] 更新 1 件`；`/redtale reload` 后 5 件内容正常、ERROR 仍为 4 条既有噪声；测试服已停（25567 关闭）。**新记两条事实**：手写组件时 `rolled_stats` 键必须用归一全名（`minecraft:generic.attack_damage`），裸名会被当「定义里没有」删掉；`ContentData` 构造器 `Map.copyOf` 会让 `rolled_stats` 迭代序跨 JVM 不保证。详见 `docs/ROUND-R12-UPGRADE.md` |
| R13 | 2026-11-16 | **D33 收尾：命名空间放开 + `rolled_keys` 口径定型 + 派 T-0009** | ①`WeaponAttributesGenerator` 从「只处理 `redtale_project:` 前缀」改为「文件名定命名空间」（`<ns>__<path>.json5` → `data/<ns>/weapon_attributes/<path>.json`），覆盖外部必 WARN，`normalizeRef` 让裸名等价于自家命名空间，非法 id 跳过不抛；②`docs/ITEM-UPDATE.md` 补 §3.3：`rolled_stats` 单看无法同时满足「改配置全服生效」与「不许冲玩家资产」，故 `rolled_keys` 定三分支（在里→保旧值 / 不在→取新定义值 / 定义已删→丢弃并记账）；③T-0006 卡的规则 5 按三分支校正（`ensure` 实现本就如此，卡面原写法与之不符）；④撤 T-0005 让位，派 **T-0009**（`/redtale item upgrade`） | `build --offline` exit 0、`selftest` **70 PASS**（T-0003/0004/0006/0007 已 VERIFIED/DONE，`/redtale item scan` 已在）。T-0009 的 `RedtaleCommand` 挂行由 S7 在 S8 交货后做 |
| R14 | 2026-11-16 | **D33 第 ④ 个刷新点（reload 后分帧全量刷新）**：验 T-0007、派 T-0010 | ①验收 **T-0007 → `VERIFIED`**（3/3：build exit 0 / `grep -c "ItemScanCommand::scan"`=1 / jar 内该 class ×1；测试服 0 玩家时输出 2 行空表并按规范返回 0；件数对账因无在线玩家挂账第 13 轮）；②新类 `core/hook/UpgradeSweep`（队列存 `(level, chunkX, chunkZ)` 不存区块对象；每 tick 8 块；玩家背包→掉落物/展示框走 `getAllEntities()`→容器按区块排队）+ `ItemUpgradeHooks` 改单例、`ensure` 提为包内可见 + `GameHooks` 挂 `ServerTickEvent.Post` + `/redtale item sweep`；③**派 T-0010**（`RepairSpec` 解析器，D23 第二半），在制品 T-0008/T-0009/T-0010 = 3/3 | `build --offline` exit 0（jar 217382 B）、`selftest` 仍 **70 PASS**（sweep 无离线可测面，测试在测试服）。测试服两次启动：**启动期零排程**；手写过期件（`content_rev 0`）放进**已强制加载**区块的箱子 → 等 6s **逐字未变** → `/redtale reload` 回显「全量刷新已排程 52 个区块」→ 6s 后 `content_rev 0→3`、`rolled_stats` 的 `attack_damage` **5.0 保留**、名称/稀有度/耐久重建，日志 `52 区块（跳过 1899）/ 升级 1 件 / 315 ms`；掉落物分支 `1 个实体 / 升级 1 件` 同样成立。**新记三条事实**：`MinecraftServer.isRunning()` 在 `ServerStartedEvent` 已为真（不能拿它区分启动期）；`ChunkMap#getChunks()` 是 `protected`（反射一次 + 缓存，取不到退化成只扫实体）；`getTickingChunk()` 不含出生点/强制加载区块，要补 `getChunkToSend()`。详见 `docs/ROUND-R14-SWEEP.md` |

| R15 | 2026-11-16 | **M2 出口剩余两块之一：消耗品右键生效（D23 第二层）**：验 T-0008、派 T-0011 | ①验收 **T-0008 → `VERIFIED`**（3/3 + S7 独立探针 `build/probe/S7ConsProbe.java` **48/48**：两条非消耗品路径零告警 / `use` 非对象 / §3.1 样例逐字段 / `use:{}` 六项缺省 / 越界夹取 8 条告警逐条 / `chance` 恰为 0.0·1.0 不告警 / 坏项 7 条告警且幸存项正确 / 两表不可变 / 非数字走默认）；②自研：新类 `items/ContentItem`（`extends Item`，**只覆写 `use()`**）→ 非护甲基底改用它（护甲仍 `ArmorItem`）；`ItemContent` 加第 11 字段 `consumable` + 护甲基底丢弃 `use` 并 WARN；`ScriptEngine.runCalls`（物品自带脚本，不进 `scripts/` 注册表）；`MessageEffect` 加 `connection == null` 守卫（FakePlayer 会 NPE）；`/redtale use probe [id]`；`DEFAULT_FILES` + `items/demo_stew.json5`；③**派 T-0011**（`tools/gen_item_lang.py`，原 T-0005 重派，14 基底物品 lang 全缺），在制品 T-0009/T-0010/T-0011 = 3/3 | `build --offline` exit 0（jar 232756 B）、`selftest` 仍 **70 PASS**。测试服起停 **2 次**（`Done (2.480s)` / `Done (2.356s)`，均已停服、25567/25577 无监听）。**A 组 `demo_stew`**（持 2 件、饱食 0）：`饱食 0→6`、效果 2 条（`regeneration 200t×1` + `saturation 1t×0`）、件数 `2→1`、冷却 400t 已进入、第二遍 `6→6 / 1→1` 被拦 → **五项全过**；`console_log` 侧证据 `[script] [redtale] demo_stew 被 [Minecraft] 使用（use.script）` 证明 `runCalls` 真跑了 `use.script`。**B 组 `probe_hungry`**（`only_when_hungry`）：饿时 `0→4` 并扣件；饱食 20/20 时**件数 1→1 挡住**。**C 组负路径**：`demo_longsword` → 「没有 use 段」；`base: chestplate` + `use` → reload WARN「护甲基底，use 段已忽略」且按非消耗品处理。**新记三条事实**：`FoodData#setFoodLevel/setSaturation/setExhaustion` 都是 public（造饿/不饿两组不用 NBT）；`sendSuccess` 的 lambda 在**发送时**求值（「使用前饱和 6.0」的假象即此，值要先落 `final` 局部量）；FakePlayer **没有 `connection`**，`sendSystemMessage` 会 NPE（已被 `runCalls` 的 catch 吞成 ERROR 日志，属功能缺陷，已修）。详见 `docs/ROUND-R15-CONSUME.md` |
| R16 | 2026-11-16 | **M2 收尾：修理结算上线（D23 第二半）**：验 T-0009 / T-0010、派 T-0012 | ①验收 **T-0010 → `VERIFIED`**（3/3 + S7 独立探针 `build/probe/S7RepairProbe.java` **38/38**：缺 `repair` 两条路径零告警 / `{}` 六项缺省 / 越界夹取逐条 / 边界 0·0.0 **不告警** / `AMOUNT` 大写与数字 mode 各回落 + 1 告警 / targets 空串·数字·null 逐条跳过且幸存项 trim / cost 五种形态 / 不可变）；**T-0009 → `VERIFIED`**（2/3 全过 + 第 3 条部分：挂行已补，控制台执行返回 `A player is required` = 已注册并走到 `getPlayerOrException`；`rev` 落后 → 计数 → 客户端 tooltip 立刻变仍挂账，需真人）；②自研 **R16-1 修理链路**：新类 `items/Repairer`（`apply`/`matches`/`pickTarget`/`specOf`，**唯一结算点** —— 命令与右键同一段代码）+ `ItemContent` 第 **12** 字段 `repair`（+ 护甲基底一并丢弃 `use`/`repair` 并 WARN）+ `ContentItem#useRepair`（副手优先 → 背包里损伤最重的一件）+ `/redtale repair <slot>` 与 `repair probe` + `DEFAULT_FILES` 加 `items/demo_whetstone.json5`（`amount 120`、`targets: []` = 任意可损坏）；③**派 T-0012**（`/redtale content check` 的 `rev` 漏加检测，C8），在制品 T-0011/T-0012 = 2/3 | `build --offline` exit 0（jar 252285 B→修复后同尺寸）、`selftest` 仍 **70 PASS**。测试服起停 **4 次**（`Done (2.334/2.320/2.406/2.490s)`，均已停、25567/25577 无监听）；`/redtale reload` = **17 份配置文件 / 8 件内容**，`items` 里 `demo_whetstone · 修理品 · rev 1` 已载入。**`repair probe` 三组全过**：受损目标（`demo_longsword` 损伤 600/1200）**600 → 480（应 −120）**、工具 **2 → 1**、返回 `CONSUME`；满耐久目标工具 2→2 未扣；不可损坏（原版石头）2→2 未扣。零 redtale ERROR，`ERROR` 计数仍为 **4**（R7 起的 RecipeManager 既有噪声）。**新记三条事实**：①`FakePlayer` 的 `setItemInHand(OFF_HAND, x)` 确实写进了 `inventory.offhand`，但 **`getItemInHand(OFF_HAND)` / `getItemBySlot(OFFHAND)` 恒返回 `air`**（同一次调用里两个入口自相矛盾）→ 探测/结算读副手要读 `inventory.offhand.get(0)`；②`FakePlayer` 默认 **`instabuild = true`**，验「扣件」必须先置 `false`，否则「修好了但没扣」会被误判成缺陷；③`ItemStack#use` 的返回值在真修好后是 **`CONSUME`**、失败分支返回 `PASS` —— 探测里拿返回枚举当判据比拿计数更早暴露问题。详见 `docs/ROUND-R16-REPAIR.md` |
| R17 | 2026-11-16 | **双队列 R17 轮：验收 T-0011 + D33 惰性兜底 ⑤（结算路径）**：验 T-0011、派 T-0013 | ①验收 **T-0011 → `VERIFIED`**（3/3：`python tools/gen_item_lang.py` exit 0 且 14 个 id 由 `ItemBase.java` 正则得出 / zh/en `item.*` 各 **14** 且 `attribute.*` 仍 **66**（jar 内实测同数）/ 连跑两次 md5 逐字相同 `8f869d98…`、`41df1b72…`，UTF-8 无 BOM）；②**T-0013 派单**（`SocketSpec` 孔位布局 + 宝石定义解析器，M3 第一层），在制品 T-0012+T-0013 = 2/3；③自研 **惰性兜底 ⑤**：`DamageLayer#ensureAttackerMainHand`（白名单判定通过后、求和前调 `ItemUpgrader.ensure` 于攻击者主手），四条口径 ⑤-a~d；④`ITEM-MODEL.md` **§5 孔位与套装 schema 定稿**（三层身份 / 宝石数值单列 `gemStats` 不与 `rolled_stats` 合并 / 孔类型开放 / 套装加成是派生值 / §5.5 落地顺序表）；⑤`AffixPools.parseStats` 与 `normalizeKey` 升 public（**包装方法，零行为变更**） | `build --offline` exit 0（jar 255210 B）、`selftest` 仍 **70 PASS**。测试服 **1 次启动**（`Done (2.563s)`，已停、25567/25577 无监听）：手写 `content_rev 0` 的 `t_upg_sword` 放进 husk 主手 → 原版 `/damage … by husk` 触发 → 组件从「只有 content_id + rolled_stats」变为 **`content_rev: 3` + `custom_name 更新测试剑` + `rarity epic` + `max_damage 500` + `attribute_modifiers` 重建**，且 `rolled_stats` 的 `attack_damage` **5.0 保留**（在 `rolled_keys` 里）→ D33 三分支在结算路径上成立；第二次同件再打，components **逐字不变**（快路径）；redtale 零 ERROR/WARN，`ERROR` 仍 4 条既有噪声。**负路径教训**：拿没写 `rev` 的 `demo_*` 当「过期件」永远测不出升级（缺省 rev 0 = 手写 rev 0 → `UNCHANGED`）。详见 `docs/ROUND-R17-LAZY.md` |
| R18 | 2026-11-16 | **双队列 R18 轮：验收 T-0012 + M3 第 3 步（`ContentData` 容器扩容 / schema 1→2）**：验 T-0012、派 T-0014 | ①验收 **T-0012 → `VERIFIED`**（3/3 + 功能四跑：首次建基线 `17 份 json5（items 8 份）· rev 漏加 0` → 改 `demo_longsword` 的 `physical_damage` 不加 rev 报**1 份**且文案逐字对上 → `rev:1` 后报 **0** → 还原文件报「**rev 倒退（基线 1 → 当前 0）**」且 missed 不计；运行期确认 `content list` 与 `content check` 两条同名 `content` 兄弟节点合并后都可用）；②**派 T-0014**（`SetSpec` 套装定义解析器 + `activeBonuses` 纯函数，M3 第 5 步），在制品 T-0013+T-0014 = 2/3；③自研 **M3 第 3 步**：`ContentData` 由 10 字段扩到 **12**（`+sockets[]` / `+gemStats{}`，均 `optionalFieldOf` 带默认值 → 老 NBT 照常解码，不需要 NBT 迁移）、`CURRENT_SCHEMA` **1 → 2**、`ItemUpgrader.SCHEMA` 改为**引用** `ContentData.CURRENT_SCHEMA`（两处各写数字早晚漂一次，漂一次就静默永不迁移）、`ensure` 重建时 **孔序与宝石数值原样带出**（玩家资产，镶进去的宝石不能因一次 reload 消失）、新增 `withSockets` / `hasSockets` | `build --offline` exit 0（jar 262440 B）、`selftest` 仍 **70 PASS**。测试服 **2 次启动**（`Done (2.398s)` / `Done (2.297s)`，均已停、25567/25577 无监听）：手写两件 `t_upg_sword`（rev 3）进箱子，A 件 `schema:1`+`sockets:["",""]`+`gem_stats`，B 件 `schema:2` 同数据 → `/redtale reload` **全量刷新 43 区块 / 5 实体 / 升级 1 件 / 260 ms** → A 件补出 `attribute_modifiers`（`attack_damage 5.0`，`rolled_keys` 保旧值）、`custom_name 更新测试剑`、`rarity epic`、`max_damage 500`，且 `sockets ["",""]` 与 `gem_stats {"minecraft:physical_damage":0.3}` **逐字保留**；B 件组件**逐字未变**（快路径）。**新记一条事实（务必记住）**：`Codec.INT.optionalFieldOf("schema", CURRENT_SCHEMA)` 在值**等于默认值时不写字段** → 组件里**没有** `schema` 键 = 当前版本（2），显式写着 `schema:1` 才是旧版；验迁移要看「字段消失」而不是「字段变成 2」。另：`physical_damage` 未出现在面板是**正确**的（手写件 `rolled_stats` 里没有它，U3 不白送）。详见 `docs/ROUND-R18-SCHEMA.md` |
| R19 | 2026-11-16 | **M3 第 4 步：镶嵌 / 取出结算 + 孔位接线**：验收 T-0013、派 T-0015 | ①验收 **T-0013 → `VERIFIED`**（3/3 + S7 独立探针 `build/probe/S7SockProbe.java` **49/49**：缺段 `EMPTY`/`null` 零告警 / `count` 夹取 0~6 / `types` 非法项换 `any` **孔序不错位** / 截断有告警 / count 0..6 全档 `types.size()==count` / `gem` 默认值与归一 / `stats` 与 `AffixPools.parseStats` 键集全等 / 不可变）；②**派 T-0015**（`/redtale validate` 引用完整性检查，只读），在制品 T-0014+T-0015 = 2/3；③自研 **M3 第 4 步**：`ItemContent` 12→**14** 字段（`+sockets` / `+gem`）、`ItemFactory.build` 按布局**填空孔**、`ItemFactory.modifiers(content, stats, gemStats)` 把宝石数值并进同一个 `ATTRIBUTE_MODIFIERS`（**id 前缀分开** `content/` vs `gem/`）、新类 `items/Socketer`（`insert`/`extract`/`solve`/`aligned`/`accepts` + 8 个 `Status`，唯一结算点）、`ContentTooltip` 加孔位行与宝石行、`/redtale socket [list\|insert\|extract\|probe]`、`ItemUpgrader.ensure` 补空孔 + 重算 `gemStats`、默认配置 `items/gem_ruby.json5` / `items/gem_sapphire.json5` + `demo_longsword` 加 2 孔（rev 0→1） | `build --offline` exit 0（jar 284933 B）、`selftest` 仍 **70 PASS**。测试服起停 2 次（`Done (2.256s)` / `Done (2.211s)`，均已停、25567 无监听）：`/redtale reload` = **19 份配置 / 10 件内容**，`items` 里 `demo_longsword · 孔位 2 · rev 1`、`gem_ruby · 宝石 offensive T1`、`gem_sapphire · 宝石 defensive T2`；**`/redtale socket probe` 11/11 全过**：新发放孔序 = 2 空孔 → 镶 ruby 得 `physical_damage 0.05` + `attack_damage 2.1`（2+0.1×1）→ 面板 `gem/` 两条 + `content/generic.attack_damage` 一条**并存**、攻击伤害合计 **9.1**（7+2.1，不是互相覆盖）→ 同组第二颗 ruby `EXCLUSIVE_CONFLICT` → offensive 孔塞 defensive 宝石 `TYPE_MISMATCH` → any 孔收 sapphire 得 3 条 → tooltip `孔位 2：[offensive] gem_ruby · [any] gem_sapphire` → 取出孔 0 后 `gemStats` 只剩 1 条（**重算而非相减**）→ 空孔再取 `EMPTY_SLOT` → 下标 5 `INDEX_OUT_OF_RANGE`。**D33 迁移实测**：手写 `content_rev 0` 且无 `sockets` 的 `demo_longsword` 进箱 → `/redtale reload` 后 `sockets: ["", ""]` **自动补齐**、`content_rev 0→1`、`rolled_stats` 的 `attack_damage 5.0` 保留；redtale 零 ERROR（4 条 RecipeManager 既有噪声）。详见 `docs/ROUND-R19-SOCKET.md` |
| R20 | 2026-11-16 | **M3 第 6 步：套装件数统计 + 属性下发**：验收 T-0014、派 T-0016 | ①验收 **T-0014 → `VERIFIED`**（3/3 + S7 独立探针 `build/probe/S7SetProbe.java` **36/36**，不复用 S8 的 `SetProbe`：`sets/` 前缀筛 / 子目录 id 保斜杠 / 空 id 跳过 / 非字符串 id 与 name 回落 / 跨文件重复保留先出现 / pieces 去重+trim+空项跳过 / `count` 缺·非数字·`<1` 全跳过、小数取整、同 count 稳定升序 / **`stats` 键集与值与 `AffixPools.parseStats` 逐条相同** / `activeBonuses` 全档生效且升序 / 三处不可变 / `configs=null`·`warnings=null` 不抛 / 两次解析顺序一致）；②**派 T-0016**（`/redtale set check` 套装引用与可达性校验，只读单类），在制品 T-0015+T-0016 = 2/3；③自研 **M3 第 6 步**：`ItemContent` 14→**15** 字段（`+setId`，`set_id` 空白按无归属）、`ItemFactory.build` 写 `set_id`、`ItemUpgrader.ensure` 重建时取**新定义**的 `set_id`（定义型字段）、新类 `items/SetBonus`（`worn`/`counts`/`countOf`/`apply`/`clear`/`applyAll`/`activeOf`/`declaredCounts`/`modifierId`/`amount`/`slotOf`）、`GameHooks` 每 20 tick 复核件数（签名没变不碰属性）、`ContentTooltip` 加套装行、`/redtale set [list\|info\|sync\|probe]`、`RedtaleCore.sets()` + reload 后给在线玩家作废签名并重算、默认 `sets/emberforged.json5` 进 `DEFAULT_FILES`、三个 demo 件加 `set_id`（rev +1） | `build --offline` exit 0（jar 309350 B）、`offline_check.py` exit 0。测试服 1 次启动 **`Done (2.036s)`**（已停、25567/25577 无 LISTEN）：`/redtale reload` = **20 份配置 / 10 件内容**、`set list` = `套装定义 1 个：emberforged · 炽锻 · 2 件 · 档位 1/2`；`set info emberforged` 两件 pieces 都解析到真实内容（`demo_longsword` / `demo_chestplate`）、两档各 1 / 2 条属性；**`/redtale set probe` 5/5 全过**：0 件无残留 → 1 件下发 `1 件档`（**最大生命 20.0 → 22.0**）→ 2 件下发 `2 件档`（`redtale_project:set/emberforged/2`，**攻击伤害 1.0 → 3.0**）→ **脱回 1 件后高档 modifier 消失、低档保留** → `clear` 全清；`/redtale tooltip demo_longsword` 多出 `套装 炽锻 0/2` 行（无 holder = 未穿）。redtale 零 ERROR（4 条 RecipeManager 既有噪声）。**新记一条事实**：`ItemBase.slot()` 是 `EquipmentSlotGroup`，1.21.1 **没有公开的 group→slot 反查**，塞装备要自己按单例 `==` 映射（`SetBonus.slotOf`）。 |
| R21 | 2026-11-16 | **M4 开工：L2 组件 `redtale_project:scripted` 注册成功（R1 风险解除）+ L1→L0 生成接线**：验收 T-0015、派 T-0017 | ①验收 **T-0015 → `VERIFIED`**（3/3：`build --offline` exit 0（jar 313235 B）/ `grep -c "ValidateCommand::validate"`=1 / jar 内该类=1；**功能四跑**：造三份坏配置 → `问题 4 条（外部引用 1 条未校验）`，四条文案逐字对上（缺定义文件 / 未定义词条 / `applies_to 的 redtale_project:wand 不是 14 基底之一` / `权重合计 <= 0`），删掉后 `/redtale reload` → `0 条` + `（没有引用问题）`；两次连跑输出逐字相同）；②**派 T-0017**（`tools/gen_enchant_lang.py`，附魔 lang 键生成器），在制品 T-0016+T-0017 = 2/3；③自研 **M4 第一块**：新类 `enchants/ScriptedEnchantmentEffect`（record，`script` + `args` NBT，`RegisterEvent` 进 `ENCHANTMENT_ENTITY_EFFECT_TYPE`，`apply` 转成 `ScriptContext` + `fireById`，脚本缺失只 WARN 一次）+ `RedtaleProject` 注册 1 行 + `GameHooks` 开局打一行注册体检；④**L1→L0 接线**：`EnchantmentGenerator.generateAll` 接进 `RedtaleCore.reload()`（与 `weapon_attributes` 同一个数据包根）+ 两份默认 `enchantments/{super_sharpness,soul_reap}.json5` 进 `DEFAULT_FILES`（`description_en` 给 en_us 用） | `build --offline` exit 0（jar 319698 B）。测试服起停 **5 次**，全部已停（25567/25577 无 LISTEN），redtale 零 ERROR（`ERROR` 仍 4 条 RecipeManager 既有噪声）。**R1 已解除**：日志 `附魔实体效果注册：redtale_project:scripted 存在=true（表内共 14 条）`（两次启动复现）→ 内置表**可以**用 `RegisterEvent` 写入，不需要 mixin 兜底。**L1→L0 实测**：`reload` 后 `world/datapacks/redtale_project/data/redtale_project/enchantment/` 出现 `super_sharpness.json` / `soul_reap.json`（字段顺序与 §3.1 白名单一致、`description` 只留 translate 键、`effects` 原样透传），零 `Failed to parse`；**下次启动**后 `/enchant` 实测 `Applied enchantment enchantment.redtale_project.super_sharpness III` 与 `... soul_reap II`。**新记两条事实（务必记住）**：①`/reload` **加不了 L0 附魔**（文件已在包内仍报 `Can't find element ... of type 'minecraft:enchantment'`），`enchantment` 属启动期加载的 datapack registry → 加附魔 = 改 JSON5 + `/redtale reload` 生成 + **重启一次**才进注册表（热更边界按 `ENCHANT-API` §8 R2 兜底执行）；②启动期 `RedtaleCore.reload()` 生成的文件，**本次启动必然看不到**（注册表早于 `ServerStartedEvent` 加载），所以「首次加附魔要重启两次」是本轮实测序列的自然结果，不是 bug。详见 `docs/ROUND-R21-M4.md` |
| R22 | 2026-11-16 | **M4 第二块：`post_attack` → 脚本层真跑通（V9/V10）+ V8 数值对账**：验 T-0016、派 T-0018 | ①验收 **T-0016 → `VERIFIED`**（3/3 + 功能五跑：4 组坏定义 → `5 个定义 · 9 件 pieces · 问题 4 条`，四条文案逐字对上、一个检查各命中一条；连跑 `diff` 空；移走坏定义 → `问题 0 条` + `（套装引用完整）`；`cap==0` 分支只报一条不逐档刷屏）；②**派 T-0018**（`/redtale validate` 补第 5 条套装引用 + 裸名 `applies_to` 提示，只读、`ValidateCommand` 独占），在制品 T-0017+T-0018 = 2/3；③自研 **M4-2**：默认 `enchantments/soul_reap.json5` 的执行体落地为 `scripts/enchants_soul_reap.json5`（进 `DEFAULT_FILES`）；`ScriptContext#expand` 支持 `%var.<key>%`（附魔 `args` 灌进 `vars`）；**修掉 L2 的静默断链**——`ScriptedEnchantmentEffect.script` 由 `ResourceLocation` 改为 `Codec.STRING`（裸 id `enchants/soul_reap` 原被补成 `minecraft:enchants/soul_reap`，与 `scripts/*.json5` 的 `id` 永远对不上 → 附魔生效但执行体静默不跑）；④**V8 可观测**：`DamageTrace.skip` 收进场值 + `/redtale damage` 打印「最近放行进场值（旧→新）」 | `build --offline` exit 0（jar 325236 B）、`selftest` 仍 **70 PASS**。测试服起停 **4 次**，全部已停（25567/25577 无 LISTEN），redtale 零 ERROR（`ERROR` 仍 4 条 RecipeManager 既有噪声）。**V9 成立**：尸壳持 `iron_sword[redtale_project:soul_reap:2]` 打村民 → 日志 `[script] [soul_reap] 触发 · 施法者 server · 等级 2 · heal_ratio=0.08 · per_level=0.02`（args 三个值全到位、脚本每次命中都跑）。**V10 成立**：把脚本 id 改成 `enchants/soul_reap_v10` + `/redtale reload` → 连打多次**只有 1 条** WARN `附魔脚本 enchants/soul_reap 不存在（附魔仍生效，只是这次触发没有执行体）`，附魔组件仍在剑上、伤害不变、不崩。**V8 对账（同一只尸壳、同一只 10 万血村民）**：白板铁剑进场值 **8.0** → `super_sharpness I` **10.0**（linear base 2.0 → +2.0）→ `super_sharpness III` **12.0**（2.0+1.0×2 = +4.0），逐级差值精确等于 JSON5 里写的数 ⇒ L0 附魔数值真的进结算且我们没动它。**新记三条事实（务必记住）**：①`EnchantmentEntityEffect.apply` 的第 4 参 `owner` 在 `post_attack` 里传的是 **affected 实体（受害者）**，不是攻击者（攻击者武器从 `EnchantedItemInUse.itemStack()` 拿）；②`ScriptedEnchantmentEffect` 的 `script` 必须是**纯字符串 id**，用 `ResourceLocation.CODEC` 会静默改命名空间；③我们的 14 基底物品**不在** `#minecraft:enchantable/sharp_weapon`（数据驱动 item tag 只列原版 id）→ `/enchant minecraft:iron_sword` 成功、`redtale_project:sword` 报 `cannot support` ⇒ 内容武器吃自家附魔需要生成自己的 item tag（下轮做）。详见 `docs/ROUND-R22-M4B.md` |
| R23 | 2026-11-16 | **M4 第三块：14 基底的附魔归属（`EnchantableTags`）+ 空互斥 tag 收口**：验 T-0017、派 T-0019 | ①验收 **T-0017 → `VERIFIED`**（3/3：脚本 exit 0 且两份 lang 各 83 键 / 断言输出 `超级锋利 摄魂 66 14 Soul Reap`（`attribute.*` 66、`item.*` 14 一条没丢）/ 连跑两次 md5 逐字相同 `8ed45104…`、`07a7f16c…`）；②**派 T-0019**（`/redtale enchant list` 读生成结果，独占 `EnchantListCommand.java` + `RedtaleCommand.java` 追加 2 行），在制品 T-0018+T-0019 = 2/3；③自研 **R23-1 基底附魔归属**：新类 `enchants/EnchantableTags`（`vanillaTags`/`tagsFor`/`generateAll`/`writeTag`）→ 按 `ItemBase` 写 7 份 `data/minecraft/tags/item/enchantable/*.json`（`replace:false` 追加）+ 缺失的自家 `exclusive_set` tag 补空文件 + `RedtaleCore.reload()` 接线 2 行；④**口径修订 R22-e → R23-a**（见 §13.26） | `build --offline` exit 0（jar 330306 B）、`selftest` 仍 **70 PASS**。测试服起停 2 次（`Done (2.132s)` / `Done (2.086s)`，均已停、25567/25577 无 LISTEN）。**第一次启动**：8 份新 tag 落盘（7 item + 1 空互斥），8/8 `json.load` 通过；同启动内 `/reload` 后木桩僵尸主手换 `redtale_project:sword` → `minecraft:sharpness III` **Applied**（R22 报 `cannot support` 的那条）、`redtale_project:soul_reap I` **Applied**；再叠 `super_sharpness` 被拒（`#minecraft:exclusive_set/damage` 互斥）、干净剑上 `super_sharpness II` **Applied**；`bow`+`power II`、`helmet`+`protection II`/`unbreaking III`、`shield`+`unbreaking II` 全 Applied，`ring`+`sharpness` 被拒（饰品不进武器批）。**第二次启动**：`Not all defined tags … present` WARN **1 → 0**；不跑任何 reload，`dagger` 直接吃 `super_sharpness I`；8 份 tag mtime 在二次启动 + 一次 reload 后仍是 20:02:40（幂等未重写）；redtale 零 ERROR。详见 `docs/ROUND-R23-TAGS.md` |
| R24 | 2026-11-16 | **M4 第四块：`soul_reap` 真回血（V9 从「只打日志」变「有玩法」）+ V11 硬指标演练**：验 T-0018、派 T-0020 | ①验收 **T-0018 → `VERIFIED`**（3/3：`build --offline` exit 0（jar 330921 B）/ `grep -c set_id` = **2**、`grep -c 个套装` = **1** / 离线探针沿用 S8 的 `Validate2Probe` 21/21；本轮不重跑，改为测试服**四跑**功能验，见右）；②**派 T-0020**（附魔可获取性 tag：`in_enchanting_table` / `tradeable` / `on_random_loot`，新建 `enchants/EnchantObtainTags.java` + `RedtaleCore` 追加 1 行），在制品 T-0019 + T-0020 = 2/3；③自研 **R24-1 脚本层双实体上下文 + `heal` 原语**：`ScriptContext` 新增 `target()` / `hasTarget()` / `ofEntity(caster, target)`；新类 `core/script/builtin/HealEffect`（`target` 取 `caster` 或 `target`、`ratio`、`per_level`、`flat`，负数归零 / `1e9` 硬顶 / 目标缺失只 WARN 一次）；`Builtins` 注册 1 行；`ScriptedEnchantmentEffect` 把 `item.owner()`（施法者）与第 4 参（受害者）分别塞进 `vars.attacker` / `ctx.target()`；`ScriptEngine.onCooldown` 加 `server == null` 守卫；默认 `scripts/enchants_soul_reap.json5` 加 `heal` 一条 | `build --offline` exit 0（jar **334577 B**）、`selftest` 仍 **70 PASS**。测试服起停 **2 次**（`Done (2.037s)` / `Done (2.064s)`，均已停、25567/25577 无 LISTEN），redtale 零 ERROR/WARN（4 条 RecipeManager + 若干第三方 refmap WARN 属既有噪声）。**T-0018 功能四跑**：基线 `10 件内容 / 1 个套装 · 问题 0 条` + `（没有引用问题）` → 造三处坏配置（套装 piece 写错 / 内容 `set_id` 悬空 / `applies_to` 裸名 `axe`）→ reload 后 `问题 3 条`，三行文案逐字对上（`sword_common: applies_to 的 axe 没写命名空间（会被当成 minecraft:axe）` / `emberforged: piece demo_longsword_typo 不存在` / `probe_badset: set_id ghostset 没有对应套装定义（写错一个字母就静默不生效）`）→ 还原后回 `问题 0 条`。**V9 真绿（两条分支都实测）**：尸壳持 `soul_reap 2` 打村民，`caster` 分支日志 `[script] heal · test_husk 8.00 → 10.00（+2.00，等级 2，目标 caster）`、下一击 `10.00 → 12.00`（= 20 × (0.08 + 0.02×1) 精确）；把脚本改成 `target: target` 后日志目标变成**受害者** `heal · Villager 20.00 → 20.00（…目标 target）` ⇒ `ctx.target()` 接线正确（满血 `+0.00` 合法）。**V11 硬指标成立**：只往 `config/redtale_project/enchantments/` 写一份 `frost_edge.json5`（**零编译**）→ `/redtale reload` 生成 `data/redtale_project/enchantment/frost_edge.json` → 同启动内 `/enchant` 仍报 `Can't find element`（复现 R21-c 边界）→ **重启**后 `Applied enchantment enchantment.redtale_project.frost_edge III`。演练文件归档到 `D:/redtale-work/drills/v11_frost_edge.json5` 并从测试服移除（保持 T-0019 的 2 条基线） |
| R25 | 2026-11-17 | **M5 开工：`docs/SKILLS.md` 定稿（schema + 24 条原语 + 释放链路）+ 派 T-0021**：本轮无卡可验（T-0019 / T-0020 仍 `OPEN`，S8 自 11-16 19:04 起零交付） | ①卡板：`[DONE]` 0 张 → 只派不验；在制品 **T-0019 + T-0020 + T-0021 = 3/3** 封顶。②新 `docs/SKILLS.md`（10 节）：边界表（技能 / 附魔 / 套装 / 技能树各归各位）、**五步释放链路**（绑定 → 触发 → 条件 → 门槛 → 执行，**不新建触发器体系**，直接复用 `ScriptEngine.runCalls`）、`skills/*.json5` **v1 schema**（一个文件一条技能，`id` / `name` / `icon` / `cooldown_ticks` / `conditions` / `effects`）+ 解析口径表、**24 条原语总表**（直伤 4 / 控场 4 / 位移 3 / 投射 3 / 增益 4 / 减益 3 / 召唤 2 / 表现 1；现状仅 `heal` ✅）、伤害口径三条红线（绝不 `setAmount` / 类型必须在 `redtale_project:` 下 / `damage_type` 是启动期 registry 要重启）、冷却与法力分三段（M5-A 内存冷却、M5-B 法力池）、绑定四阶段（命令 → 物品 `abilities` → 键位 → 怪物 AI）、K1~K8 验收矩阵、交付顺序、10 条不做。③**派 T-0021**（`core/skill/SkillSpec.java` 技能定义解析器，纯函数；验收 = build + `grep` + `SkillProbe` ≥18 断言）。④`CONTRACTS.md` §2 加 `core.skill` 包、§5 加 `skills/` 配置路径 | `build --offline` exit 0（jar **334577 B**，本轮零代码改动）、`selftest` **70 PASS**、`docs/SKILLS.md` §4 原语表 **24 行**（`grep -c` 断言不变）。**新记（§13.28）**：技能**没有** `trigger` 字段（触发是引擎入口不是内容）、冷却按**玩家 UUID** 而非名字（改名清冷却 = 漏洞）、`damage` 原语只 `hurt` 白值从不 `setAmount`。**卡点**：S8 静默 10 小时（最后交付 = 11-16 19:04 的 T-0018），协作板 §5 开 `B-` 挂账；M4 出口仍 8/11，剩下 V4 / V5 / V6 **全是 GUI 面**（等带客户端窗口，V4 另依赖 T-0020）。 |
| R26 | 2026-11-17 | **验收 T-0019（含测试服实测）+ 派 T-0022 + 伤害类别池落地（Q-018 默认 A）** | ①卡板：T-0019 `[DONE]` → **`[VERIFIED]`**（S8 05:41 交付）。在制品 T-0020 + T-0021 + T-0022 = **3/3**，只派不增。②**T-0019 验收全过**：`build` exit 0（jar 340493 B）、`grep -c EnchantListCommand.node()`=1、jar 内该类 1 条；测试服 RCON 实测 `已生成附魔 3 条`——**比卡面预期多 1 条**（`frost_edge` 是 R24 手测留下的落盘产物，配置目录只有两份），三行字段与磁盘 JSON 逐字段对上、排序升序、`soul_reap` 无「脚本不存在」；负向验：改名 `scripts/` 后该行尾出现「脚本不存在」，改回即消失。采纳 S8 的单引号口径偏差（默认脚本写 `id: 'enchants/soul_reap'`）。③**派 T-0022**（`core/skill/SkillCooldowns.java` 冷却表，纯数据 + 注入 tick，验收 = build + 零 MC import + 探针 ≥16 断言）。④**自己写：伤害类别池**（Q-018 默认 A 落地）——`MultiplierRules` 加第 5 分量 `List<Category>`（`record Category(match, attributes)`）+ `attributesFor(damageTypeId)`（first-match，未命回落 `percent_attributes`），`appliesTo` 与它共用 `normalise`/`matches`；`DamageLayer` 第 90 行改吃 `attributesFor(typeId)`；新增两个**冻结** damage_type（`skill_physical` / `skill_magical`）+ 两条死亡提示 lang；`damage.json5` 加 `category_attributes` 段（缺省 = 两条默认，显式 `[]` = 关掉分轴）。⑤`/redtale damage` 线上实测输出 `类别池 redtale_project:skill_magical=magical_damage / redtale_project:skill_physical=physical_damage`；`/damage` 打猪两次（magical 生效、physical 因无敌帧被拒属正常）→ `观测：进场 2 次 · 白名单内 2 次`，说明两个新类型都进了 registry 且过白名单 | `build --offline` exit 0（jar **344079 B**）、`selftest` **78 PASS**（+8 条类别池断言）、测试服两次启停均 `Done` + 干净退出（`console_r26.log` / `console_r26b.log`）。**新记（§13.29）**：分轴 ≠ 按技能注册 damage_type（只冻结两个通用类型）；条件乘区不跟着分轴（两类共用）；`percent_attributes` 仍是「未命中类别」的兜底池，不是废字段。**卡点**：M4 出口 8/11 余 V4/V5/V6 全为 GUI 面；T-0020/T-0021 仍无人领。 |
| R27 | 2026-11-17 | **M4 收尾（V4 的可获取性 tag）+ M5-A 第一条原语 `damage`**：T-0020 收回自做、派 T-0023 | ①卡板：无 `[DONE]` 可验（T-0021/T-0022 05:50 派单，S8 尚未交付）；**T-0020 连挂两轮无人领 → `[DROPPED] (S8 静默两轮，S7 自做)`**，按 B-01·默认 执行；**派 T-0023**（`/redtale enchant obtain` 可获取性 tag 只读对账），在制品 T-0021+T-0022+T-0023 = 3/3。②自研：新类 `enchants/EnchantObtainTags`（三份原版 tag `in_enchanting_table`/`tradeable`/`on_random_loot`，`replace:false` 追加、幂等不重写 mtime）+ `RedtaleCore` 1 行接线 + 探针 `build/probe/ObtainProbe.java` **20/20**；新原语 `core/script/builtin/DamageEffect`（`damage`，只 `hurt(白值)`、`damage_type` 缺省 `skill_physical`、`radius` 不支持）+ `Builtins` 1 行 + `/redtale damage hit probe [amount]`。③实测（测试服 1 次启动 `Done (2.213s)`，已停、25567/25577 无 LISTEN）：三份 tag 落盘且 values 2 条升序；`reload` 后 mtime 未变（幂等）；`damage hit probe` **五组全过**（白值 10→10 / +25% 物理→12.5 / 法术只堆物理→10 / +50% 法术→15 / 未知类型回缺省→12.5）；redtale 只有 1 条预期 WARN，4 条 RecipeManager 既有噪声。④数字：`build --offline` exit 0（jar 354540 B）、`selftest` **78 PASS**、`grep -c "^| [0-9]" docs/SKILLS.md` = 24 |
| R28 | 2026-11-17 | **双队列 R28 轮：验收 T-0021（技能解析器）+ 技能快照 `SkillRegistry` 落地 + 默认两份技能**：验 T-0021、派 T-0024 | ①卡板：T-0021 `[DONE]`（S8 06:52 交付）→ **`[VERIFIED]`**（3/3：`build --offline` exit 0（jar 360261 B）/ `grep -c "Definition> parse("` = 1 / jar 内 `core/skill/SkillSpec` 两条目；**S7 独立探针 `build/probe/S7SkillProbe.java` 50/50**，不复用 S8 的 `SkillProbe`：id 五态 / 重复保先 / name·icon 缺省 / cooldown 四态（-5→0、1e10→1e9、`'x'`→0 各 1 告警）/ conditions 三态 / effects 四态 / args 三态（缺失 = `ScriptCall.EMPTY` 同一实例、对象原样透传）/ 三处不可变 / 键序稳定）。**S8 提的四处口径偏差全部采纳**（详见 T-0021 卡进度行）。②**派 T-0024**（`/redtale content list` 行字段刷新，清掉 R11 之前的 `AFFIX_PENDING` 过期占位，单类只读），在制品 T-0022 + T-0023 + T-0024 = **3/3** 封顶。③自研 **M5-A 第 1 步：技能快照层**——新类 `core/skill/SkillRegistry`（`EMPTY` / `load` / `all` / `get` / `has` / `size` / `sortedIds` / `warnings` / `effectCount` / `primitiveTypes` / `describe`，不可变快照 + 与解析告警同源）+ `RedtaleCore` 加字段与 `skills()` 访问器 + reload 接线 2 行；默认 `skills/gale_slash.json5`（物理 6.0 / cd 120）与 `skills/ember_burst.json5`（法术 8.0 / cd 200 / `health_below 0.9`）进 `DEFAULT_FILES`。④reload 回显与日志带上技能计数，作为 K1 在命令卡落地前的观测面 | `build --offline` exit 0（jar **364183 B**）、`selftest` 仍 **78 PASS**、独立探针 `build/probe/S7SkillRegProbe.java` **14/14**。测试服起停 **2 次**（`Done (2.070s)` / `Done (2.102s)`，均已停、25567/25577 无 LISTEN）：日志 `配置重载完成：2 条脚本，25 个文件，10 件装备内容，2 条技能（4 条 effect，原语 4 种）`，`config/redtale_project/skills/` 两份默认落地。**负向（K6 同型）**：写 `skills/probe_bad.json5`（缺 id + `effects: []` + `cooldown_ticks: "x"`）→ reload 回显 `1 条告警`、日志 `skills/probe_bad.json5: id 缺失或不是字符串（必填），已跳过这条技能`、技能数仍 2、零 ERROR。**正向（K1 同型）**：只再加一份合法 `skills/probe_new.json5`（不换 jar）→ 技能 **2 → 3 条**（5 条 effect）；删掉后回 2 条。reload 回显最终形态 `已载入 2 条脚本 + 10 件装备内容 + 2 条技能（25 份配置文件）` |
| R29 | 2026-11-17 | **M5-A 引擎落地（`SkillEngine` + `/redtale skill`）+ 验收 T-0022/T-0023 + 派 T-0025** | ①卡板：T-0022 / T-0023 `[DONE]` → **`[VERIFIED]`**（各 3/3，另跑 S7 独立探针 `S7CdProbe` 54/54、`S7ObtainProbe` 19/19，均不复用 S8 断言）；T-0024 仍 `[OPEN]`；**派 T-0025**（`/redtale validate` 补第 6 条「技能引用的原语是否存在」，单文件只读），在制品 T-0024+T-0025 = 2/3。②自研 `core/skill/SkillEngine`（`Status{CAST,NO_SKILL,NO_PLAYER,CONDITION,COOLDOWN}` + `Result` 记录；条件不过不记账、冷却不过不跑 effects；目标 = 视线 raycast 8 格；effects 走新 `runCalls(calls,ctx,owner)` 重载）+ `core/command/SkillCommand`（`list`/`cast`/`probe`/`cd`）+ `RedtaleCore.skillEngine()`（**跨 reload 存活**）+ `RedtaleCommand` +2 行。③实测（测试服起停 3 次已停）：K1 `skill list` 立即见 2 条且显示中文名（只改配置不换 jar）；K2 连放 `43 tick`→`37 tick` 递减、掉血 0；K3 `条件不满足（health_below）` 且日志无 `[skill]`；K4 两 effect 全跑；**K5 A/B 对照 6→7.5（×1.25）**、法术 8→8（×1.00 分轴）；K6 四份坏技能 → 4 条告警文案逐字对、服务端照跑。`build --offline` EXIT=0（jar 385865 B）、`selftest` **78 PASS**、redtale 零 ERROR。 | 引擎是「三层技能」唯一缺的一层：快照能列、冷却能算，但没有人把它们串起来放一次；`SKILLS.md` §2 的五步链路里 ③④⑤ 一直没实现。`probe` 特意做成 A/B 两组（零属性 vs `physical_damage +0.25`）——只验一组的话「原语自己乘了」与「`DamageLayer` 没接上」两种 bug 都能漏（沿用 R27 的方法论）。 |
| R30 | 2026-11-17 | **M5-B 物品绑定技能 + 冷却减免 + 验收 T-0024 + 派 T-0026** | ①卡板：T-0024 `[DONE]` → **`[VERIFIED]`**（3/3 + 测试服 `content list` 五计数对账、10 行 × 7 字段、`demo_longsword 孔位 2 / 套装 emberforged / rev 2`；卡面 `rev 1` 是 R20 前的陈旧期望，判过）；**派 T-0026**（`buff` 原语，新建 `BuffEffect.java` + `Builtins` 1 行），在制品 T-0025+T-0026 = 2/3。②自研 M5-B：`ItemContent` 15→**16** 字段（`+abilities`，坏项逐条告警）、`ItemFactory.build` 写 `ContentData.abilities`、`ItemUpgrader.ensure` 重建取**新定义** abilities（与 `set_id` 同口径）、`ContentItem#use` 分支优先级 `use → repair → abilities.get(0)`、`SkillEngine.cooldownReduction()` 接 `cooldown_reduction`（异常归零，换算仍在 `SkillCooldowns.effectiveTicks`）、tooltip 加「技能 N：…」行、`demo_longsword` 加 `abilities` 且 rev 2→3、新命令 `/redtale skill use "<内容id>"`（FakePlayer 真调 `ItemStack#use`，四组）。③实测（测试服起停 2 次均已停，25567/25577 无 LISTEN）：A 组 `CONSUME` + 木桩掉血 **6** + 剩余冷却 **120**（定义 120）；B 组立刻再按 `FAIL` + 掉血 **0**；C 组无 abilities 的 `gem_ruby` `PASS` + 冷却记录 **0**；D 组 `cooldown_reduction +0.5` → 剩余 **60** tick。`build --offline` EXIT=0（jar **392955 B**）、`selftest` **78 PASS**、redtale 零 ERROR（4 条 RecipeManager 既有噪声）。 | 「技能能放」到「武器右键能放」之间还差一次组件落地 —— `ContentData.abilities` 字段 M0 就在，但从来没人填，所以 schema **不用动**（仍 2），这是 D17「注册表项预制」的回报。冷却减免**只读属性面板**、换算只在 `SkillCooldowns` 一处，避免「装备 + 药水 + 技能各自乘一遍」的三份真相（D18 同思路）。探针特意加 C 组（无 abilities 的武器）——只验「右键能放技能」会漏掉「凡右键都放技能」这一种反向 bug。 |
| R31 | 2026-11-17 | **验收 T-0025 + `/redtale skill info` + 派 T-0027** | ①卡板：T-0025 `[DONE]` → **`[VERIFIED]`**（3/3：build exit 0 / 两条 grep 各 **2** / 测试服实测基线 `技能 2 条 · 问题 0 条` → 写 `skills/t_bad.json5` → `技能 3 条 · 问题 2 条` 且两条文案逐字对（`conditions 引用了未注册的原语 no_such_condition` / `effects 引用了未注册的原语 dash`）、连跑两次逐字同、删文件后回落到 `技能 2 条 · 问题 0 条` + `（没有引用问题）`）；**派 T-0027**（`content list` 补「技能」列 + 汇总 `带技能 K 件`，独占 `ContentListCommand.java`），在制品 T-0026+T-0027 = 2/3。②自研 `/redtale skill info <id>`（`SkillCommand` 加 1 个 literal + 2 个静态方法）：打印 id/名称/冷却/图标/来源，`conditions` 与 `effects` **逐条标注册状态**（`core.registries()` 与执行期同源，不另写白名单），再列「被哪些内容绑定」。③实测（测试服起停 2 次均已停，25567/25577 无 LISTEN）：`gale_slash` → 3 条原语全 ✅ + `被内容绑定 1 件：demo_longsword`；`ember_burst` → `damage {"amount":8.0,"damage_type":"redtale_project:skill_magical"}` args 摘要正常；坏技能 `t_bad2` → `✗ 未注册 no_such_condition` / `✗ 未注册 dash {"distance":4}` + 尾部 `✗ 2 条原语未注册`；不存在的 id → `没有技能 … （现有 2 条：…）` 不抛异常。`validate` 与 `content list` 零回归。`build --offline` exit 0（jar **395979 B**）、`selftest` **78 PASS**、redtale 零 ERROR（4 条 RecipeManager 既有噪声）。 | M5-C 的原语（`buff`/`damage_aoe`/`debuff`）全要改 `Builtins.registerAll` —— 那是 T-0026 的独占文件，**在它 VERIFIED 之前 S7 一行都不能碰**（防冲突机制的全部意义）。所以本轮 S7 做的是「不改 Builtins 的观测面」：`validate` 报「有问题」，`skill info` 报「这条技能哪个原语缺、谁在用它」—— 两者读同一份 `core.registries()` 快照，不会出现「一个说缺一个说没事」。 |
| R32 | 2026-11-17 | **验收 T-0026（`buff` 原语）+ M5-C 放量（`damage_aoe` / `debuff`）+ 派 T-0028** | ①卡板：T-0026 `[DONE]` → **`[VERIFIED]`**（3/3 + 功能四组，见下）；T-0027 仍 `OPEN` 零进度（11:48 派）；**派 T-0028**（`tools/check_defaults.py`：`ConfigStore.DEFAULT_FILES` ↔ `resources/redtale/defaults/**` 双向对账，纯 Python 零 Java），在制品 T-0027+T-0028 = 2/3。②**T-0026 验收**：`build --offline` exit 0（jar **399417 B**）/ `grep -c "new BuffEffect()"`=1 / `grep -c 'return "buff"'`=1 / jar 内 `script/builtin/BuffEffect.class`=1；功能四组（测试服 RCON）：`skill probe t_buff`（`buff target:target`）→ `[script] buff · Cow + minecraft:instant_damage 20t×0`；`t_buff_self`（`target:caster`）→ `[script] buff · [Minecraft] + minecraft:strength 200t×1`（FakePlayer 走 `player()` 分支）；**附魔链路真实体**：临时给 `enchants/soul_reap` 加一条 `buff caster → minecraft:glowing 600t` → 尸壳打村女后 `data get entity … active_effects` = `{duration: 387, amplifier: 0b, id: "minecraft:glowing"}`（写 600，已过 213 tick）；坏 id 连跑两次只 **1 条** WARN `buff 找不到效果：minecraft:no_such_effect`（去重成立）。S8 两处偏差采纳（`duration_ticks<=0` 补一条 WARN；`pick` 的 `args.target` 非字符串仍会抛，与 `HealEffect` 同源，记 §13.35-c 不改）。③自研 M5-C 两条原语：新类 `core/script/builtin/DamageAoeEffect`（`damage_aoe`：圈心 = **有受害者在受害者脚下、否则施法者脚下**；`falloff` 线性衰减只乘白值；`max_targets` 按距离由近到远截断；**施法者不进命中集合**）+ 新类 `DebuffEffect`（`debuff`：**缺省打受害者**、只收 `MobEffectCategory.HARMFUL`、写正面效果 WARN 跳过）+ `DamageEffect` 的 `source`/`holder`/`caster`/`num` 由 `private` 改**包内可见**（零行为变更，第二份「伤害类型回退」逻辑不再复制）+ `Builtins` +2 行 + `SKILLS.md` §4 的 2/15/19 三行 `—`→`✅ R32`。④实测（测试服起停 **2 次**，`Done (2.208s)` / `Done (2.202s)`，均已停、25567/25577 无 LISTEN）：启动日志 `原语 5 种 → 7 种`；`skill info t_aoe` → `✅ damage_aoe`；`skill probe t_aoe` **A 组 10 / B 组 12.5（×1.25）**（范围伤害照样过 `DamageLayer`）；附魔链路多目标 `damage_aoe · 圈心 (8.5, 71.0, 8.5) · 半径 4.0 · 命中 2/2 · Villager(0.0格×1.00) Cow(2.0格×0.75)` → 牛 10→2.5，第二击 `3.5格×0.56` 打死；`debuff · Husk + minecraft:slowness 600t×1` 且 `data get` 实测 `{amplifier: 1b, duration: 510}`；改缺省目标后 `debuff · Villager + minecraft:slowness 600t×1`；`debuff` 写 `minecraft:strength` → 1 条 WARN `不是负面效果`、零效果。⑤夹具全部移除、脚本已还原（`skills/` 回到 2 件、配置 25 份、redtale 零 ERROR）。 | `build --offline` exit 0（jar **407520 B**）、`selftest` 仍 **78 PASS**、`docs/SKILLS.md` §4 原语表 **24 行**（`grep -c` 断言不变）、redtale 零 ERROR（4 条 RecipeManager 既有噪声）。**新记（§13.35）**：①瞬时效果（`minecraft:instant_damage`）走 `addEffect` **不结算伤害** —— 连原版 `/effect give … instant_damage` 都不掉血，`buff` 因此不能当直伤用；②`MobEffectCategory.HARMFUL` 是 `debuff` 的唯一准入判据（正面效果必须显式 WARN，否则「debuff 能加血」会静默通过）；③测试服地面 y=-58 是实心方块，`summon` 进去直接 `suffocated in a wall`（实体 10 秒死光，看起来像「召唤失败」）—— 立靶要 `fill <y> stone` 做**空中平台**；④`ActiveEffects` 的 `duration` 会随 tick 掉，验收对账只能比「初始值 − 已过 tick」，不能要求等值。 | M5-C 的第二、三条原语。两条都**只能改 `Builtins.registerAll`**（单点），所以必须等 T-0026 VERIFIED 之后 S7 才能落 —— 本轮前半段验收、后半段放量，正好把 T-0026 占着的注册表收回来。`damage_aoe` 特意**不复制** `DamageEffect` 的伤害类型回退逻辑，而是把它改成包内可见复用：两份回退 = 以后改第三条原语必漏一份，现象是「同一个技能换个原语就不吃乘区」。 |
| R33 | 2026-11-17 | **验收 T-0027 + M5-C 控场前两条（`knockback` / `pull`）+ 派 T-0029** | ①卡板：T-0027 `[DONE]` → **`[VERIFIED]`**（3/3：build exit 0 / `grep -c abilitiesText`=2 / `grep -c "带技能 "`=1 / jar 内该类=1；测试服 RCON `/redtale content list` → 10 行每行末尾都有 `· 技能 `、`demo_longsword` = `技能 1: redtale_project:gale_slash`、汇总 `带技能 1 件`，与实测 1 件一致）；**派 T-0029**（`core/skill/ManaPool`：法力池纯数据类，接口逐字写死 12 个方法 + 8 条行为，零 MC import、注入 tick），在制品 T-0028+T-0029 = 2/3。②自研 M5-C 两条控场原语：新类 `core/script/builtin/KnockbackEffect`（`knockback`：`strength` 缺省 0.4、`radius` 缺省 **0 = 只推受害者**、>0 推圈心内活体；**位移一律走原版 `LivingEntity#knockback`**，吃 `KNOCKBACK_RESISTANCE`，再补 `hurtMarked = true` 让 `ServerPlayer` 走运动包）+ 新类 `PullEffect`（`pull`：方向取反 + `radius` 缺省 **6**，直接调 `KnockbackEffect.shove`，**共用一份位移实现**）+ `Builtins` +2 行 + `SKILLS.md` §4 第 5/6 行 `—`→`✅ R33`。③实测（测试服起停 **2 次**，`Done (2.262s)`，均已停、25567/25577 无 LISTEN；验法 = 附魔 `post_attack` → 脚本 → 打真实体，在**旁观牛**（`NoAI`、不进命中判定的受害者之外）的 `Motion` 上对账）：`knockback radius 6` → 牛 `Motion.x = -0.798`（推离，尸壳在 +X 侧）；同位置改 `pull radius 6` → 牛 `Motion.x = +0.797`（拉向）；目标 `knockback_resistance 1.0` → `推动 1/2` 里 `Villager(0.6格 Δ0.00)`（原版抗性生效）；`strength: 0` → 41 次触发只 **1 条** WARN `strength 缺失或 <= 0` 且牛 `Motion` 全程 `0.0`；`skill info` → `✅ knockback` / `✅ pull` / `✓ 全部原语已注册`。夹具全部移除、脚本已还原（`scripts/` 回默认件、`skills/` 回 2 件、25 份配置）。 | `build --offline` exit 0（jar **413740 B**）、`selftest` 仍 **78 PASS**、`docs/SKILLS.md` §4 原语表 **24 行**（`grep -c` 断言不变）、redtale 零 ERROR（4 条 RecipeManager 既有噪声）。**新记（§13.36）**：①`DamageEffect.num` 把**非正数也换成缺省值**——`strength: 0` 会被静默变成 0.4，所以两条位移原语改用自己读的 `raw()`，非正数原样返回交给调用方判跳过；②`LivingEntity#knockback(s,x,z)` 内部算的是 `-normalize(x,z)`（字节码实读），推离要传**反**方向；③`NoAI` 实体**不跑 `travel`（物理不生效）但 `Motion` 照样读得到**——验位移方向用 `Motion` 比用 `Pos` 干净；④重复击退的 `Motion` 收敛到 `0.8` 不动点（每周期的 `old/2 + 0.4`），此时日志里的本轮 `Δ` 会显示 `0.00` 但**仍在推**，别把 `Δ0` 读成没生效。 | M5-C 的第三、四条原语（控场类）。卡在 `Builtins` 的前提这次不成立（T-0028 是纯 Python 卡，不碰 Java），所以本轮 S7 可以放手改注册表；派出去的 T-0029 特意选了**与 `Builtins` 完全正交**的纯数据类，避免「刚拿到注册表又要让出去」。两条位移原语共用 `shove` 一份实现，是 R32-d「同一语义只有一个实现」的直接延续。 |

| R35 | 2026-11-17 | **验收 T-0029 + M5 收口第一步（法力进引擎）+ 派 T-0031** | ①卡板：**T-0029 → `VERIFIED`**（3/3：build exit 0 / `grep -c net.minecraft`=0 且 `synchronized|ConcurrentHashMap`=0 且 138 行 / 自写探针 **85/85**（`build/probe/S7ManaProbe.java`，不复用 S8 断言）；**派 T-0031**（`dash` 原语：单类 + `Builtins` 2 行，`motion` 纯函数可离线断言 ≥20 条），在制品 T-0030+T-0031 = 2/3。②M5 收口第一步：`SkillSpec.Definition` 7→**8** 字段（`+manaCost`，`mana_cost` 缺省 0、负数/非数字告警、`1e9` 硬顶）；`SkillEngine` 持有 `ManaPool`（跨 reload 存活）+ 新门槛 `Status.NO_MANA` + 三个属性读点（`max_mana` / `mana_regeneration` / `mana_cost_reduction`）+ `syncMax` / `tickMana` / `manaText` / `noManaText`；`GameHooks` 每 tick 回蓝（`ticks=1` 交回池里累积）；`SkillCommand` 新 `mana` / `mana set` / `mana probe`（A~F 六组）+ `list`/`info` 补「法力」列；默认内容 `skills/arc_bolt.json5`（`mana_cost 40`）进 `DEFAULT_FILES`。③实测（测试服起停 **4 次**，`Done (2.131/2.0x/2.0x/2.0x s)`，均已停、25567/25577 无 LISTEN）：`reload` = 26 份配置 / **3 条技能**（`skill list` 每行带 `法力 40` / `法力 0`）；`skill mana probe arc_bolt` **六组全过** —— A 满蓝 100→60（扣 40，CAST）/ B 再放 60→20（累减）/ C 蓝不够 **39→39、`NO_MANA`、冷却就绪 true**（不扣也不吃冷却）/ D 消耗降低 50% 100→80（应扣 20）/ E 回蓝 20/秒 × 20 tick 余额 **20.0**（小数累积不丢）/ F `max_mana=150` → 上限 150、当前 20→20（**抬上限不补蓝**）；负向夹具两份（`mana_cost: "abc"` / `mana_cost: -5`）→ reload **2 条告警**文案逐字对、两条技能仍以 `法力 0` 载入、删文件后回 3 条 0 告警；`/redtale skill mana` 控制台执行返回 `这条命令要玩家执行（法力账按 UUID 记）`。④**F 组第一次是红的**：`max_mana` 自建属性基值 0（R5 事实），`+50` modifier 得到的是 **50** 不是 150 —— 我按「加成」写的期望，实际口径是**绝对值**。改期望为 150 并把它写进口径（§13.38 R35-a）。 | `build --offline` exit 0（jar **432032 B**）、`selftest` 仍 **78 PASS**、`S7ManaProbe` **85/85**、redtale 零 ERROR / 零 WARN（4 条 RecipeManager 既有噪声本轮为 0）。**新记（§13.38）**：①`max_mana` 是**绝对值**且 `0 = 没配` → 默认 100，内容侧写 500 就是 500；②`mana_regeneration` 不给缺省回蓝（0 = 不回蓝），回蓝速度只有属性一个来源；③法力门槛在**记冷却之前**（否则空蓝连按把技能锁死）；④`ManaPool` 挂在 `SkillEngine` 上跨 reload 存活，持久化（`PlayerData`）留给下一步。**未验证**：真人玩家的 `/redtale skill mana` 面板与登录还原（无客户端，挂账）。详见 `docs/ROUND-R35-MANA.md` |
| R36 | 2026-11-17 | **验收 T-0030 + M6 第二层（`MobRegistry` 快照）+ 派 T-0032** | ①卡板：T-0030 `[DONE]` → **`[VERIFIED]`**（3/3：build exit 0 / `grep -c net.minecraft`=0、197 行、`parse(` 签名 1 处、jar 内 4 个 `mobs/MobSpec*`；S8 探针 90/90，S7 独立探针 `build/probe/S7MobSpecProbe.java` **71/71**）；**派 T-0032**（`/redtale mob check` 装备/技能引用只读校验，独占 `MobCheckCommand.java` + `RedtaleCommand` 1 行），在制品 T-0031+T-0032 = 2/3。②M6 第二层：新类 `mobs/MobRegistry`（`EMPTY`/`load`/`all`/`get`/`has`/`size`/`sortedIds`/`warnings`/`countByBase`/`skillCount`/`describe`，不可变快照 + 告警随快照换代，与 `SkillRegistry` 同构）+ `RedtaleCore.mobs()` + `reload()` 接线 + 回显带怪物数；默认内容 `mobs/ember_guard.json5`（elite / 带剑+胸甲 / 1 条技能）与 `mobs/ash_caster.json5`（caster / 法杖+头盔 / 2 条技能 / 带 `max_mana`）进 `DEFAULT_FILES`。③实测（测试服 1 次启动 `Done (2.239s)`，已停、25567/25577 无 LISTEN）：启动日志 `2 只怪物（3 条技能引用，原型 2 种）`、28 份配置、**零配置告警**（说明两份默认件的属性键全部命中 80 条表，否则 `AffixPools` 会告警丢弃）；`/redtale reload` 回显 `2 只怪物`；`/redtale validate` 仍 `问题 0 条`；手写 `mobs/t_probe_mob.json5`（charger）→ reload **2→3 只（29 份）**、删文件 → **回落 2 只（28 份）**，全程零 jar 更换（D17/D14 对怪物层成立）。④方法论：`mob check` 类型卡**必须先有快照层**，否则卡只能自己解析配置（第二份真相）——所以本轮先写 `MobRegistry` 再派卡。 | `build --offline` exit 0（jar **445907 B**）、`selftest` 仍 **78 PASS**、`S7MobRegProbe` **39/39**、redtale 零 ERROR / 零 WARN（4 条 RecipeManager 既有噪声，与 R8 起同）。**新记（§13.39）**：①怪物层三层与技能层同构（`MobSpec` 解析 / `MobRegistry` 快照 / 后续 `MobSpawner` 执行）；②`MobRegistry.describe()` 是「解析是否真的吃到内容」的唯一廉价证据（0 只 = 目录空 or 全被跳过）；③默认件必须**每条属性键都在 80 条表内**，否则静默丢弃（本轮靠「零告警」反证）。**未验证**：真人刷怪、实体生成、模型体积（M6 第三/四步）。详见 `docs/ROUND-R36-MOBREG.md` |
| R37 | 2026-11-17 | **验收 T-0031（`dash`）+ M6 第三步第 1 小步（8 个模板 EntityType 冻结）+ 派 T-0033** | ①卡板：T-0031 `[DONE]` → **`[VERIFIED]`**（3/3：build exit 0（jar 449435 B）/ 136 行 / `setDeltaMovement`=1 / 禁用词=0 / jar 内该类=1 / `Builtins` **+2 -0**；S7 独立探针 `build/probe/S7DashProbe.java` **34/34**）；S8 的五条 NEED-S7 **全部采纳**（`apply`→`run` 是我卡面写错，`EffectType` 冻结签名只有 `run`）。**派 T-0033**（`projectile` 原语 v1：只做「射出去」，`on_hit` 不支持），在制品 T-0032+T-0033 = 2/3。②真机验 `dash`（测试服起停 3 次，均已停、25567/25577 无 LISTEN）：`skills/t_dash.json5`（`power 1.6 / up 0.35`）→ `/redtale skill probe` 日志 `[script] dash · [Minecraft] · look · 力度 1.60 · 上抛 0.35 · 速度 (1.600, 0.350, 0.000)`；`direction: back` → `速度 (-1.000, 0.000, -0.000)`；`power: 0` → 1 条 WARN `args.power <= 0，已跳过` 且**零位移**；`up: 'abc'` + `direction: 'away'` → 两条 WARN 且回落 `上抛 0.20` / `look`。速度能不能落地另证：`data merge entity <husk> {Motion:[0,0,0.6]}` → `Pos` 从 z=12.8 移到 29.8（服务端采纳写出的速度）。③M6 第三步第 1 小步：新类 `mobs/RedtaleMob`（`extends Monster`，一份出厂属性表 8 个原型共用）+ 新类 `mobs/RedtaleEntities`（`DeferredRegister<EntityType<?>>`，id 与 `MobSpec.BASES` **一一对应**：melee/ranged/caster/summoner/charger/flyer/elite/ambient，尺寸表按原型给，飞行/精英追踪距离 10）+ `RedtaleProject` 3 行接线 + `EntityAttributeCreationEvent` 绑属性。实测（`Done` 后逐个 `/summon`）：**8/8 全部召唤成功**、`Health 20.0`、`generic.scale 1.0`、`redtale_project:physical_damage` 基值 0.0 存在（说明自建属性自动挂到新类型，`EntityAttributeModificationEvent` 的 `getTypes()` 覆盖到它们）。 | `build --offline` exit 0（jar **454110 B**）、`selftest` 仍 **78 PASS**、redtale 零 ERROR（4 条 RecipeManager 既有噪声）。**新记（§13.40）**：①`server-*-srg.jar` 里**没有** `MobType`（javap + unzip 双证）→ 8 个原型要算亡灵只能往 `#minecraft:undead` 实体标签追加 id（`replace:false`，同 R23 手法），v1 未做；②**无玩家在线时怪物 AI 不跑、但物理照跑**（同一只 husk：`Motion`/`Pos` 全程不动 = 不走 AI；`data merge Motion` 后立刻位移 17 格）→ 想用「怪自己攻击 → `post_attack` → 脚本」验原语，没有真人在线时**根本不会触发**，本轮因此改用 `skill probe`（FakePlayer）+ 直接写 `Motion` 两段取证；③`/summon` 显示的是 lang 键 `entity.redtale_project.melee`（14 基底物品同款问题）→ 实体 lang 生成器待补（`gen_item_lang.py` 已可仿）。**未验证**：玩家客户端侧的 `dash`（SKILLS §4 第 9 行要求分帧给速度，v1 是一次性写速度，会被客户端校正拉回）、8 原型的 AI 差异、模型/音效。详见 `docs/ROUND-R37-DASH.md` |
| R34 | **M5-C 控件第 3 条 `stun`（停 AI 定住）+ 验收 T-0028 + 派 T-0030** | ①卡板：**T-0028 → `VERIFIED`**（3/3：基线 21/21 `EXIT=0`；假清单项 → `[仅清单有]` + `EXIT=1`；移走真实 `crit.json5` → `EXIT=1`（**卡面第 3 条我写成「仅磁盘有」，语义上应为「仅清单有」，采纳 S8 偏差不打回**）；另补 `[仅磁盘有]` 与 `EXIT=2` 两支）；**派 T-0030**（`mobs/MobSpec` v1 解析器：身份 / 属性 / 装备 / 技能引用，M6 第一层），在制品 T-0029 + T-0030 = 2/3。②自研 `stun`：新类 `core/script/builtin/StunEffect`（`Mob#setNoAi(true)` + `Navigation#stop()`；`radius 0` = 只定住目标、`>0` = 圈心内活体且**排除施法者**；在册标记写 scoreboard tag `redtale_stunned`（1.21.1 已无 `getPersistentData`）；恢复走 `ServerTickEvent.Post` 轮询截止时刻；`EntityJoinLevelEvent` 清重启残留）+ `Builtins` 1 行 + `GameHooks` 2 处 + `SKILLS.md` §4 第 7 行 ✅ R34。③实测（测试服起停 **3 次**，均已停、25567/25577 无 LISTEN）：走「尸壳持 `soul_reap` 铁剑 → `post_attack` → 脚本 → `stun`」，铁傀儡（受害者）+ 牛（旁观者）**两个都拿到 tag、`NoAI=1b`**，尸壳自己**没有** tag；边界分支 `半径 3.0 内只有目标本身`；杀尸壳 8s 后 `stun 解除 · Cow（到点）`/`（Iron Golem（到点））` 且 `Tags` 清空。④**两个只有实测能抓的 bug**：施法者被自己的圈定住（`casterOf` 加入排除）；续定反复重读 `isNoAi()` 导致解除时**永久定住**（改为沿用首次 `wasNoAi`）。 | `build --offline` exit 0（jar **420488 B**）、`selftest` **78 PASS**、`docs/SKILLS.md` §4 原语表 **24 行**（`grep -c` 断言不变）（预算不变，原语现状 **8/24**）。**新记（§13.37）**：①`slowness 255` 是速度乘数，被装备/药水/第三方 modifier 一抵就成「慢慢挪」，而且怪照样打人 → 定住只能用停 AI；②1.21.1 **没有** `Entity#getPersistentData()`（编译期实证）→ 用 scoreboard tag 记在册；③续定必须沿用首次 `wasNoAi`，否则「打第二下」会把怪变成永久木桩；④测试服 x≈0 一带地表 y≈60，随机 y summon 会被顶到地表 → 立靶统一先 `fill` y=99 空中平台。**未验证**：玩家被定住（无客户端）、重启残留清理日志、原本 AI 开启的怪恢复后回到 AI 开启（夹具两只牛混读）。详见 `docs/ROUND-R34-STUN.md` |
| R38 | 2026-11-17 | **验收 T-0032（`/redtale mob check`）+ M6 第三步第 2 小步（`MobSpawner` + `/redtale mob spawn`）+ 派 T-0034** | ①卡板：T-0032 `[DONE]` → **`[VERIFIED]`**（3/3：build exit 0（jar 457719 B，`MobCheckCommand.class` 1 条）/ 88 行、`BuiltInRegistries.ITEM`=1、`MobCheckCommand.node()`=1、`RedtaleCommand` **+1 行**；测试服 `Done (2.137s)` 四步：基线 `2 只 / 技能引用 3 条 · 引用完整 ✓` → 夹具 `t_badmob` + reload（29 份配置 / 3 只）→ `3 只 / 技能引用 4 条 / 问题 2 个` 且两行文案逐字对 → 连跑 diff 空 → 删夹具回落；四条 NEED-S7 全采纳）。**派 T-0034**（`tools/gen_entity_lang.py`，8 个 `entity.redtale_project.*` 键，合并写入，照抄 `gen_item_lang.py` 形态），在制品 T-0033+T-0034 = 2/3。②M6 第三步第 2 小步：新类 `mobs/MobSpawner`（`spawn(ServerLevel,x,y,z,Definition)` → 属性 `ADD_VALUE` 临时 modifier（id `mob/<怪id>/<属性path>`）→ `generic.scale` 基值 → 六槽 `setItemSlot` → 名称/`redtale_mob/<id>` 标签/持久化 → 落地 → `setHealth(max)`；`Result(ok,message,mob,skips)`）+ 新类 `core/command/MobSpawnCommand`（`/redtale mob list`、`/redtale mob spawn <id> [x y z]`）+ `RedtaleCommand` **+1 行**。③实测（测试服起停 2 次，`Done (2.137s)` / `Done (2.143s)`，均已停、25567/25577 无 LISTEN）：`mob list` 2 行；`spawn ember_guard 106 101 106` → `128/128 血`，`Pos [106,100,106]`、`CustomName "炽焰守卫"`、`Tags ["redtale_mob/ember_guard"]`、`HandItems` 剑 + `ArmorItems` 胸甲、`generic.scale` 基值 **1.15**；`/attribute … get` 四值 **attack_damage 11.0**（2+9）、**max_health 128.0**（20+60+4×12）、**movement_speed 0.27**（0.25+0.02）、**armor 9.0**（0 配置 6 + 胸甲 3）。夹具 `t_spawn_bad`（flyer / scale 0.6 / `mainhand: demo_longsword` / `spell_power`）→ `属性 1 条 · 装备 1 件 · 体积 ×0.60` + `⚠ 装备 mainhand 的物品 id 未知：demo_longsword`，头盔真穿上（`ArmorItems[3]`）、`attack_damage 6.0`（2+4）、`scale 0.6`；同一夹具下 `mob check` 也报同一条 → 两个观测面一致。负向：`spawn nope` → `没有怪物 nope（现有 2 只：ash_caster, ember_guard）`。 | `build --offline` exit 0（jar 467339 B）、`selftest` 仍 **78 PASS**、redtale 零 ERROR（1 条预期配置告警 = 夹具的 `spell_power`）。**新记（§13.41）**：①怪物属性 = 出厂基值 + `ADD_VALUE`，**不** `setBaseValue`（可拆解 + 重生成同 id 覆盖不叠加），代价是「`max_health: 60` 得 128 血」= 加法口径；②体积是唯一走**基值**的字段（形态不是数值），`1.0` 不写；③未知属性键在**解析层**就被 `AffixPools` 丢掉 → spawner 的「未知属性」分支对配置不可达，`skips` 实际只有「装备 id 写错」「实体没这个属性」两类；④**未加载区块里生成会掉到地形**（首测两只掉到 y=54、`@e` 也找不到）→ 验生成先 `forceload`。**未验证**：客户端看到的体积/名牌、8 原型的 AI 差异、技能释放（M6 第 4 步）。详见 `docs/ROUND-R38-SPAWN.md` |
| R39 | 2026-11-17 | **验收 T-0033（`projectile`）+ M6 第三步配套（`#minecraft:undead` 标签）+ 派 T-0035** | ①卡板：T-0033 `[DONE]` → **`[VERIFIED]`**（4/4：build exit 0（jar 471397 B）/ 152 行 / `addFreshEntity`=1 / 禁用词=0 / `Builtins` **+2 -0** / jar 内该类=1；S8 探针 **38/38** + S7 独立探针 `build/probe/S7ProjProbe.java` **26/26**；测试服 `Done (2.105s)` 跑 `skills/t_arrow.json5` → 日志 `[script] projectile · [Minecraft] · minecraft:arrow · 速度 3.00`，**`/tick freeze` 后读 `Motion = [2.2079, -2.0310, 2.7e-16]`，模长恰 3.0000**）。S8 四条 NEED-S7 全采纳。**派 T-0035**（`mobs/DropSpec` 掉落表解析器 v1，M6 第四层，纯解析单类 + 探针），在制品 T-0034+T-0035 = 2/3。②M6 第三步配套：`MobSpec.Definition` 9→**10** 字段（`+undead`，缺省 false、非布尔降级 false + WARN）+ 新类 `mobs/MobEntityTags`（把 `undead:true` 的原型追加进 `data/minecraft/tags/entity_type/undead.json`，`replace:false`，空集也写）+ 新类 `core/datapack/TagJson`（三处 tag 写手收口成一份，含幂等比较）+ `RedtaleCore.reload()` 接线 + 默认 `mobs/ash_caster.json5` 加 `undead: true`。③**修掉 D14 的一个真漏点**：`PackEnabler` 原来在「包已选中」时直接 `return ALREADY_SELECTED`，一个字节都不重载 → 运行期重写的 tag 只在磁盘上，`@e[type=#minecraft:undead]` 匹配不到（实测：reload 后 tag 文件已含 `redtale_project:caster`，选择器仍 `count 0`，必须再敲一次原版 `/reload`）。改为 `ensureEnabled(..., boolean resourcesChanged)`：包已选中且本次真写了文件 → `reloadResources` → 新 `Outcome.ALREADY_SELECTED_AND_RELOADED`；`/redtale reload` 传 `true`，开服那次不传。④同时把 `EnchantmentGenerator` / `WeaponAttributesGenerator` 改成**幂等写**（`TagJson.writeIfChanged`）：原来无条件 `writeString`，内容没变也刷 mtime，`written` 恒 ≥3 → 每次 reload 都白重载一遍。⑤实测（测试服起停 4 次，`Done (2.105/1.997/2.078s)`，均已停、25567/25577 无 LISTEN）：**A 组**启动期 `生成数据包状态：ALREADY_SELECTED（本次写出 0 个文件）` + 启动即 `@e[type=#minecraft:undead,type=redtale_project:caster]` **count 2**（上一轮写好的 tag 随包加载）；**B 组**`/redtale reload` → `ALREADY_SELECTED（写出 0 个文件）`（不再白重载）；**C 组**删掉 `undead: true` → reload → `ALREADY_SELECTED_AND_RELOADED（写出 1 个文件）`、tag `values: []`、caster **立刻掉出**选择器（husk 仍 count 1）；**D 组**恢复 → reload 写 1 → 立刻回到 count 2；`mob spawn ash_caster` → 68/68 血、进标签（count 3）；`mob check` / `validate` 零回归。 | `build --offline` exit 0（jar **474566 B**）、`selftest` **78 PASS**、`S7UndeadProbe` **19/19**、redtale 零 ERROR / 零 WARN。**新记（§13.42）**：①亡灵归属只能落在 **tag** 上，而 tag 只能按 EntityType 打 → 粒度上限就是 8 个原型（`undead` 写在一只怪上，整个原型都进 tag）；②验「写出去的东西进内存了没」必须看**选择器命中**，不能看文件内容（本轮 C 组前的误判就来自只看 `cat`）；③`/redtale reload` 触发的资源重载会**重放 4 条 RecipeManager 既有噪声**（每次 4 条，不是新 bug）；④验初速一律 `tick freeze`（箭矢 1 tick 就掉 0.99/重力 0.05）。**未验证**：真人客户端侧的 undead 判定与伤害数字、`pve+undead` 双键在自建怪身上的实测堆叠（无客户端，挂账）。详见 `docs/ROUND-R39-UNDEAD.md` |
| R40 | 2026-11-18 | **验收 T-0034/T-0035 + M6 第三步第 3 小步（怪物技能释放）+ 派 T-0036** | ①卡板：T-0034 `[DONE]` → **`[VERIFIED]`**（3/3：脚本 exit 0 + `解析到 8 个原型 id：melee, ranged, caster, summoner, charger, flyer, elite, ambient`；zh/en 各 `93 键 / entity 8 / attribute 66 / item 14`；连跑两次 md5 逐字相同（zh `73193e14` / en `2afe2065`）；117 行 ≤130；`py_compile` 0）。T-0035 `[DONE]` → **`[VERIFIED]`**（3/3：build exit 0 + jar 内 `mobs/DropSpec.class`=1；118 行 ≤190、`net.minecraft`=1、`Registr`=0；**S7 独立探针 `build/probe/S7DropProbe.java` 52/52**，不复用 S8 的 `DropSpecProbe`；S8 四条口径备注全采纳）。**派 T-0036**（`mobs/DropRoll` 掉落掷骰纯函数，M6 第四层第二步），在制品 1/3。②M6 第三步第 3 小步：新类 `mobs/MobSkillCaster`（`tick` 每 10 tick 扫全服、只认 scoreboard tag `redtale_mob/<id>`、目标取 `mob.getTarget()`（没有就不掷骰，免得空放吃冷却）；`tryCast` 掷骰 / `forceCast` 忽略概率；**零成员状态**：冷却在 `SkillCooldowns`、随机数用 `mob.getRandom()`）+ `SkillEngine.castMob(caster,target,skillId,cooldownTicks)`（条件 → 冷却只查 → 记冷却 → effects，与 `cast` 同序同源；**不算法力**、冷却时长可被 `SkillRef.cooldownTicks` 覆盖、生物施法者灌 `vars.attacker`）+ `GameHooks` +1 行 + `/redtale mob cast <id> [roll\|<skill>]` 三模式。③**修掉一个会让验收永远假通过的坑**：命令原来每次都现生成一只怪 → 新 UUID = 干净冷却账本，「连放第二次应被冷却拦」根本验不出来；改为**优先复用 16 格内同类怪**（输出标 `复用`/`新生`）。④实测（测试服起停 5 次，`Done (2.042 / 2.057 / 2.188 / 2.117s)`，均已停、25567/25577 无 LISTEN）：A 组 `cast ember_guard`（新生）→ `施放 redtale_project:gale_slash · CAST · 2 条 effect`、靶牛 10 → **4**（白值 6 未被原语自乘）；B 组立刻再放 → **`COOLDOWN 106t`**、血量不动；C 组点名 `"redtale_project:gale_slash"` → `COOLDOWN 112t`；D 组 `t_chance0` → `(chance 0)`；E 组 `t_chance1` 首次 CAST、立刻再放 `COOLDOWN 92t`；F 组 `t_noskill` → `没配 skills`；G 组 `no_such_mob` → 报现有列表；夹具删除 + reload → 5 只落回 2 只（31 → 28 份配置）；`validate` 问题 0 条、`mob check` 引用完整 ✓。 | `build --offline` exit 0（jar **490223 B**）、`selftest` 仍 **78 PASS**、redtale 零 ERROR / 零 WARN（4 条 RecipeManager 既有噪声）。**新记（§13.43）**：①冷却键是 `(UUID, 技能 id)` → 验「冷却是真的」必须复用同一只施法者，否则每次新 UUID 让这条断言恒真；②`StringArgumentType.word()` 不吃冒号 → 点名技能的参数改 `string()`（RCON 侧加引号才传得进 `ns:id`）；③「未施放」必须回状态（`COOLDOWN 112t` / `(chance 0)` / `(未掷中)`）：只回 null 时「冷却中」与「没这个技能」长得一模一样；④场上残余夹具（本轮那只 `Invulnerable:1b` 的村民）会让 `damage` 原语的 `hurt()` 静默 no-op（日志「被原版拦下」）→ 验伤害数值前先清场。**未验证**：`tick` 路径的真人 AI 选目标（R37-b：无玩家在线 AI 不跑）→ 挂账第 40 轮；`SkillEngine.castMob` 的生物施法者属性面板（damage 原语已带 `vars.attacker`，但 `physical_damage` 类乘区在怪身上未实测）。详见 `docs/ROUND-R40-MOBCAST.md` |
| R41 | 2026-11-18 | **验收 T-0036 + M6 第四层接线（掉落：`MobSpec.drops` → `DropSpec` → `DropRoll` → 地上物品）+ 派 T-0037** | ①卡板：T-0036 `[DONE]` → **`[VERIFIED]`**（3/3：build exit 0 / jar 内 `mobs/DropRoll`=3 / 43 行 ≤120、`net.minecraft`=0、`nextInt`=1；**S7 独立探针 `build/probe/S7DropRollProbe.java` 27/27**，自编 A~M 组，不复用 S8 的 `DropRollProbe`）；**派 T-0037**（`/redtale drop list` 掉落表只读清单 + 反向引用，单类 + `RedtaleCommand` ≤2 行），在制品 1/3。②自研 M6 第四层：`MobSpec.Definition` 10→**11** 字段（`+drops`，裸 id）；`RedtaleCore.drops()` 快照 + `DropSpec.parse` 接线；新类 `mobs/MobDrops`（`LivingDropsEvent` → 认 tag `redtale_mob/<id>` → 表 → `DropRoll.roll` → `ItemEntity`；`ExperienceOrb.award` 发 xp；**不 clear 原版战利品**）；`MobCheckCommand` 补「掉落表引用」问题类型 + 头行带表数；默认 `drops/ember_guard.json5`（进 `DEFAULT_FILES`）+ `mobs/ember_guard.json5` 加 `drops:`。③实测（测试服起停 3 次，`Done (2.137/2.138/2.108s)`，均已停、25567/25577 无 LISTEN）：基线 `2 只 / 技能引用 3 条 / 掉落表 1 张 · 引用完整 ✓`；确定性夹具（stone 1~1 chance 1.0 + `xp: 7`）→ 掉落物 `{count: 1, id: minecraft:stone}`、经验球 `Value 7s`；**内容 id 掉落**（表里写 `redtale_project:gem_ruby`）→ 掉出 `redtale_project:amulet` + `redtale_project:content {content_id: gem_ruby}` + `custom_name 赤红宝石` + `rarity rare`；`ember_guard` 连杀 4 只 → 金粒聚合 `count: 4`、第 4 只出火焰粉；悬空引用夹具 → `问题 1 个` + `掉落表 nope 不存在（现有 2 张：…）` + 死亡时 1 条 WARN，服务端照跑；删夹具 → 回落 `2 只 / 1 张 / 引用完整 ✓`、`validate 问题 0 条`、29 份配置。④数字：build exit 0（jar **499381 B**）、`selftest` **78 PASS**、redtale 零 ERROR / 零 WARN（4 条 RecipeManager 既有噪声）。 | `DropRoll` 是纯函数层，本来可以离线验；但「掉落是不是真的落到地上」必须过 `LivingDropsEvent` —— 这条链上有个坑只有实测能看见：**内容 id 不是物品 id**（14 基底各只有一个物品 id，`gem_ruby` 只是 `content_id`），只查 `BuiltInRegistries.ITEM` 时自建装备永远掉不出来且只有一条 WARN。xp 那一半也不能用 `LivingExperienceDropEvent`：对照实验（`/kill` 一只原版牛 → 0 个经验球）证明它只在玩家击杀时触发，无客户端验收里永远为 0 —— 所以改成 `LivingDropsEvent` 里主动 `ExperienceOrb.award`，并把「掉落是加项」写成 R41-d。第三条教训是工程性的：`DEFAULT_FILES` 只在文件缺失时落地，改默认 `mobs/*.json5` 不会让老服的副本长出 `drops:`，第一轮实测「死怪零产出」正是这个（R41-e）。 |
| R42 | 2026-11-18 | **验收 T-0037 + M7 契约定稿（`docs/PROGRESSION.md`）+ 派 T-0038 + D26 钩子核验（javap）** | ①卡板：T-0037 `[DONE]` → **`[VERIFIED]`**（3/3：build `--offline` EXIT=0、jar 内 `core/command/DropListCommand`=1、`wc -l`=69≤160、`grep -c DropRoll`=0；测试服 RCON 文案逐字对 `[redtale] 掉落表 1 张 · 条目合计 3 条 · 被引用 1 张` + `  ember_guard · xp 12 · 条目 3 · 引用 1 只：炽焰守卫`；回归 `validate` 问题 0 / `mob check` 引用完整 ✓）。**派 T-0038**（`core/progression/ExpCurve` 曲线纯函数，M7 第一层，独占一个新文件），在制品 **1/3**。②M7 契约定稿：新 `docs/PROGRESSION.md`（10 节）= 双累加器数据流（事件→定量→分配→升级→下发）+ `levels/*.json5` / `jobs/*.json5` v1 schema + **曲线数学写死**（`geometric: round(base×growth^(L-1))` / `polynomial: round(base×L^exponent)`，单步硬顶 1e9）+ 三条经验来源（`kill`/`command`/`primitive`）+ 属性下发固定 id `level/<path>`、`job/<job>/<path>`（`ADD_VALUE`，先移除再加）+ 存档走 `SavedData`（`world/data/redtale_project_progress.dat`，**等级是派生值不存**）+ K1~K6。`CONTRACTS.md` §2/§5 同步。③D26 钩子核验（`javap` 读 21.1.257 三个 jar，非猜测）：`FinalizeSpawnEvent` 存在且 cancellable，但**全 jar 只有 `BaseSpawner` / `TrialSpawner` 引用它**；补丁后的 `Mob.finalizeSpawn` 只写 `spawnType` 字段，**不调 `EventHooks.finalizeMobSpawn`**；`NaturalSpawner` 只调 `EventHooks.checkSpawnPosition`×2 / `getMaxSpawnClusterSize` / `getPotentialSpawns`。④数字：`build --offline` exit 0（jar **502715 B**、零代码改动）、`selftest` 78 PASS、测试服起停 1 次 `Done` 后已停（25567/25577 无 LISTEN）、redtale 零 ERROR（4 条 RecipeManager 既有噪声）、构建锁已删。 | 这一轮的价值全在「先定契约再派解析器」：M5 的教训（R25）是解析器先落地再补 schema，结果 schema 漏了三处口径要回头改卡。M7 的曲线是全项目唯一需要精确数学的地方（`round` vs 截断、到顶、反查边界），把这些写成显式定点值（`expForLevel(3)=125`、`totalExpForLevel(4)=352`）以后，S8 写错就会在探针里立刻红，而不是等玩家升级时才发现少 1 点经验。D26 那一段是本轮唯一的「推翻既有假设」：PLAN D26 原文把 `MobSpawnEvent.FinalizeSpawn` 当首要候选，字节码显示它在 1.21.1 只覆盖刷怪笼/试炼笼 —— 若照原文开工，验收会表现为「自然刷怪完全没被替换」而毫无报错。
| R43 | 2026-11-18 | **验收 T-0038 + M7 第三层存档落地（`ProgressStore` SavedData + `/redtale progress`）+ 派 T-0039** | ①卡板：T-0038 `[DONE]` → **`[VERIFIED]`**（3/3：build `--offline` EXIT=0（jar 504603 B）/ jar 内 `core/progression/ExpCurve`=1 / `wc -l`=90≤180、`net.minecraft`=0、两个工厂各 1 处；**S7 独立探针 `build/probe/S7ExpCurveProbe.java` PASS 284 / FAIL 0 / TOTAL 284**，自编 A~J 十组：九条定点 + 累计=单步之和 L=1..50 逐一手算 + `levelFor(total(L))==L` L=1..100 + `levelFor(total(L)-1)==L-1` L=2..100 + 三条夹取 + `expForLevel(0)` 抛 IAE + 1e9 硬顶 + polynomial `round` 口径 + 无状态重入 + maxLevel=2/1000 两端）。**S7 裁定：卡面 `totalExpForLevel(4)=352` 是笔误，`337` 正确，不打回**（语义 4 写死 `Σ_{i=1..L-1}`，同卡面 `totalExpForLevel(3)=212` 已印证 L-1 口径；352 只能是 `212+exp(4)=212+140` 含 L 项）。**派 T-0039**（`core/progression/ProgressSpec` —— `levels/*.json5` + `jobs/*.json5` 解析器，M7 第二层，独占一个新文件 ≤200 行，13 条语义 + 10 条探针断言），在制品 **1/3**。②自研 L3 存档层：新类 `core/progression/ProgressStore`（`extends SavedData`，`FILE_NAME=redtale_project_progress`、`VERSION=1`、`MAX_TOTAL_EXP=1e15`；API `mainExp/jobExp/jobExps/size/ids/addMainExp/addJobExp/setMainExp/clear` + `load(CompoundTag,Provider)` + `factory()` + `get(MinecraftServer)`；NBT v1 = `{version, players:[{id:"<uuid>", main, jobs:{}}]}`，UUID 存字符串、坏行整条跳过、负值归零、超顶截断）+ 新类 `core/command/ProgressCommand`（`/redtale progress [status|add|probe]`，`probe` 用固定 UUID `00000000-…-00ff` 故控制台可跑）+ `RedtaleCommand` 1 行 + `GameHooks` 开局 `computeIfAbsent` 一行日志。③实测（测试服起停 2 次 `Done (2.226s)` / `(2.037s)`，均已停、25567/25577 无 LISTEN）：首启日志 `进度存档就绪：0 名玩家（redtale_project_progress.dat）`；RCON `progress probe` `0 → 1000` 再 `1000 → 2000`、`status` 玩家 0→1 名；`save-all` 后 `world/data/redtale_project_progress.dat` **104 B 落盘**（此前目录里无此文件）；**重启后** `status` 直接 `1 名`、`probe` `2000 → 3000`（= 从磁盘读回，非内存残留）；回归 `reload` 29 份配置 / `validate` 问题 0 / `drop list` 文案不变 / redtale 零 ERROR/WARN。④数字：`build --offline` exit 0（jar **512605 B**）、`selftest` **78 PASS**、`offline_check` `sources: 114 exit: 0`、`S7StoreProbe` **48/48**、构建锁已删。 | 本轮两件事都指向同一条纪律「先钉死纯函数/数据层，再接生命周期」。`ExpCurve` 的验收没有走「S8 自测贴数字就算过」的老路，而是自写 284 条：其中 149 条是 `levelFor(total(L))==L` / `levelFor(total(L)-1)==L-1` 的全量对拍 —— 这类「边界差 1」的错在人工抽查里几乎必然漏掉，而它直接表现为玩家永远差 1 点经验。定点表里那条 352 也正是同一类问题的镜像：卡面自己算错一次，若照抄打回，会把一个正确的实现判成失败，所以写进 R43-a 作为口径而不是默默改卡。存档层是本轮真正的新证据：`SavedData` 的**重启读回**只能实测，离线探针只能证明 NBT 序列化闭环（48 条），证明不了 `DimensionDataStorage` 是否真的把文件写到 `world/data` 并在下个进程读回来。顺手踩到两个坑：`Map.copyOf`/`Set.copyOf` 不保迭代序（R18 记过一次，本轮被自己的探针当场抓住，48→47 红一条），以及 srg 编译面上 `SavedData.Factory` **只有 3 参构造**（2 参是 universal 补丁后的，javap 看得到、编译器看不到）。 |

| R44 | 2026-11-18 | **验收 T-0039 + M7 第二层快照（`ProgressRegistry` + `ProgressRules`）+ 派 T-0040** | ①卡板：T-0039 `[DONE]` → **`[VERIFIED]`**（3/3：build `EXIT=0`（jar 526008 B）/ jar 内 `core/progression/ProgressSpec`=**2** / `wc -l`=**141**≤200、`net.minecraft`=0、`Logger`=0 / `git status` 只有该新文件 + TASKS；**S7 独立探针 `build/probe/S7ProgressSpecProbe.java` PASS 83 / FAIL 0**，自编 A~K 十一组，不复用 S8 的 `ProgressSpecProbe`）。S8 两处「卡面没写死的文案」照单采纳。**派 T-0040**（`/redtale level list|info`，只读快照，独占 `LevelCommand.java` + `RedtaleCommand` 1 行），在制品 **1/3**。②自研 M7 L2：新类 `core/progression/ProgressRegistry`（`EMPTY`/`load`/`levels`/`jobs`/`get`/`has`/`size`/`levelCount`/`jobCount`/`attributeCount`/`sortedIds`/`warnings`/`describe`；**属性键过 80 条表校验**（不在表内丢弃 + WARN）并**归一成全名**（`attack_damage`/`generic.attack_damage`/`minecraft:attack_damage` → `minecraft:generic.attack_damage`，两种写法冲突后者覆盖 + WARN）；同 id 同时写进 `levels/` 与 `jobs/` → 留主等级、丢职业那份 + WARN）+ 新类 `core/progression/ProgressRules`（`progression.json5`，v1 只有 `mob_exp_multiplier`，负数→0、>1e9 截断）+ `RedtaleCore.progress()/progressRules()` + reload 接线 2 行 + reload 回显/日志带「N 条等级定义」+ 默认 `levels/main.json5` / `jobs/miner.json5` / `progression.json5` 进 `DEFAULT_FILES`。③实测（测试服 1 次启动 `Done (2.001s)`，已停、25567/25577 无 LISTEN）：启动日志 `主等级 1 条 / 职业 1 条（3 条按级属性）`、32 份配置；`/redtale reload` 回显 `2 条等级定义`；热加 `levels/t_probe.json5`（含 `spell_power`）→ **3 条 + 1 条告警**，文案 `levels/t_probe.json5: redtale_project:probe_level 的属性 spell_power 不在 80 条属性表里，已丢弃（该条不会下发）`；删回 2 条；负向 `t_bad`（id 无冒号）+ `t_dup`（job 冒充 `redtale_project:main`）→ 2 条 + **3 条告警**（id / curve 缺 / 同 id 跨级），文案逐字对；`validate` 仍 `问题 0 条`。④数字：build exit 0（jar **526041 B**）、`selftest` **78 PASS**、`S7ProgressRegProbe` **47/47**、`S7ProgressSpecProbe` 83/83、构建锁已删 | **口径（§13.47 R44-a~d）**：①**校验放快照层不放解析层**——`ProgressSpec` 只认 schema，属性表是 L2 的知识（R44-a）；②属性键**必须归一成全名**再存快照，否则同一属性两种写法会在 `AttributeMap` 上生成两个 modifier、面板翻倍（R11-b 的坑，R44-b）；③`progression.json5` 只放跨内容旋钮，曲线/来源不搬进来（R44-c）；④`levels/` 与 `jobs/` 同 id 时**留主等级、丢职业**，不是"各存一份"（R44-d）。**顺手修一处**：`ProgressSpec` 的不可变集合从 `Map.copyOf`/`List.copyOf` 改成保序包装，理由与 `R43-b` 一致（卡面写的是 `Map.copyOf`，但它与 R43-b 冲突，已在卡进度行记原因） |
| R45 | 2026-11-18 | **验收 T-0040 + M7 L4 服务层（`ProgressService`）+ 派 T-0041** | ①卡板：T-0040 `[DONE]` → **`[VERIFIED]`**（3/3：build `EXIT=0`（jar 530331 B）/ jar 内 `core/command/LevelCommand`=1、`wc -l`=116≤160、`grep -c ProgressSpec`=0 / `git status` 仅三个文件；测试服 `Done (2.001s)` 时 `level list` **三行逐字相符**、`info "redtale_project:miner"` 首行逐字相符、负向 `info nope` 不抛异常；补测 `max_level: 2` 夹具 → `L2→L3 -`，夹具已删）。卡面负向样例写成「a, b」（逗号带空格），实现是 `String.join(",")` → **按正文档位「逗号分隔」裁定实现正确、样例笔误，不打回**（同 R43-a 口径）。**派 T-0041**（`tools/check_progress.py` 起飞前对账：属性键命中 80 条表 / 同 id 跨目录 / curve 必填 / `max_level`；原定的 `LevelModifiers` 被 L4 内联，12:05 改卡），在制品 **1/3**。②自研 M7 L4：新类 `core/progression/ProgressService`（`mainDef`/`levelOf`/`mainLevel`/`award`/`applyAttributes`/`onLogin`/`applyAll`；`Award` 记录含主+职业等级前后与 modifier 条数；`kill` 是唯一吃 `mob_exp_multiplier` 的来源；属性下发 `ADD_VALUE` + **声明 id 全移除再加**、`level<2` 只移除）+ 新类 `core/command/ExpCommand`（`/redtale exp [add|sync|probe]`）+ `RedtaleCommand` 1 行 + `RedtaleCore.reload()` 在线玩家重算 1 处 + `GameHooks.onPlayerJoin` 重算 1 处 + `MobDrops` **同一处**记 `total_exp`（不新开事件）。③实测（测试服起停 6 次，均已停、25567/25577 无 LISTEN）：`exp probe` **7/7** —— A `+1000 → Lv 7 · 最大生命 23.0`、E 双累加器（夹具 `jobs/t_cmd.json5` 吃 `command` → `t_cmd=1000`、`miner=0`）、F `kill ×1.5 → 实发 1500`、G `Σplan → mining_efficiency Δ5.08`、B 加满 `Lv 100/100 · 69.5`、C 到顶再加 10 万不动、D 归零回基线 20.0；`redtale exp` / `exp add` 控制台 → 「只能由玩家执行」；`validate` 0 问题、redtale 零 ERROR（4 条 RecipeManager 既有噪声）。④数字：build exit 0（jar **548580 B**）、`selftest` **78 PASS** | **口径（§13.48 R45-a~f）**：①属性键有**两种形态**（原版带命名空间、自建是裸 path），必须走 `AttributeSpecs.resolve` + `RedtaleAttributes.holder`，**不许 `ResourceLocation.parse`**（裸 path 会被补成 `minecraft:x`，静默查不到 = 职业属性全线不下发，本轮实测踩到）；②`MobDrops` 是经验唯一入口，**同一处**再记一份 `total_exp`，经验球仍原版口径；③`level<2` 只移除不加，移除按**声明 id** 全清（不是按当前 plan）；④`award` 不写等级只写 `total_exp`，等级现算（R42-b）；⑤`/redtale exp probe` 每组断言都用「按当前配置算出的期望值」而不是硬编码数字，改倍率/加职业后仍自洽（本轮 1.0→1.5 直接复用同一探针就是靠这条） |

### 13.1 R1 定下的子决策
| # | 决策 | 理由 |
|---|---|---|
| R1-a | reload 分两级失败：**文件语法错误**整体回滚（旧配置继续跑）；**单条脚本语义错误**只跳过该条 | 一个逗号不该停摆整套脚本，也不能静默 |
| R1-b | 配置目录 `config/redtale_project/`，文件名以 `_` 开头跳过 | 临时停用不删文件 |
| R1-c | `config/redtale_project/README.md` 由注册表每次 reload 重写 | schema 与代码永不脱节；代价是手改会被覆盖（README 首行已写明） |
| R1-d | 构建绕行 `tools/offline_check.py`（拿测试服 `libraries` 当 classpath 做 javac） | 网络阻断期的验证通道，**不作为发布构建** |

### 13.2 下一步（R2）

1. 属性注册表落地（M1 第一步）：按 `docs/ATTRIBUTE-REGISTRY.md` 一次注册，`DeferredRegister<Attribute>` + lang 条目 + `/attribute` 实测；`/redtale attr` 与 `AttributeBreakdown` 同批做（D18 的验收项）。
2. `StatValue{base,scale,spread,maxSpread}` 与 `settle()` 单测（纯 Java，可离线跑）。
3. `attack_speed.json5` 声明式攻速来源表（D18），**急迫默认 0.10/级开启、其余外部来源 0、soft_cap 0 不饱和（D19）**。
4. 构建链路等 Aki 拍板（`docs/ROUND-M0.md` §7 三个选项）。

> 第 1 项已在 R2 完成（见上表与 `docs/ROUND-M1-ATTR.md`）；第 2~4 项顺延为 R3。

### 13.3 下一步（R3）

1. `StatValue{base,scale,spread,maxSpread}` + `settle()`：先写纯 Java 单测（离线可跑），再接管线。
2. `attack_speed.json5` 声明式表（D18）+ 急迫 0.10/级 applier（固定 modifier id，等级变化先移除再加）。
3. 第一个 mixin：`Player#getCurrentItemAttackStrengthDelay`（D19 的 `min_attack_delay_ticks = 1.0` 物理地板）。需新增 `redtale_project.mixins.json` 并在 `META-INF/neoforge.mods.toml` 里 `[[mixins]]` 声明——**这是本项目的构建风险点，先单独验一次再叠功能**。
4. 有玩家在线时补验 `/redtale attr attack_speed`（玩家上下文；绝大多数生物没有 `minecraft:generic.attack_speed`，僵尸实测报「没有属性」）。

### 13.4 下一步（R4）

1. `settle()` 接进 `LivingIncomingDamageEvent`（L2 乘区 + damage type 白名单 `redtale_project:*`），顺带验证 `CriticalHitEvent` 是否仍可作为暴击入口。
2. 有客户端时补验玩家上下文攻速：手持不同武器看 `/redtale attr attack_speed` 与 `getCurrentItemAttackStrengthDelay` 的对应关系（FakePlayer 只验证了基值路径）。
3. M2 起步：`ContentData` 组件 + 14 基底物品 + 白板化（D21）验证件。
4. tooltip（D20）：`ItemTooltipEvent` 追加「单次伤害 + 攻速（tick / 次每秒）」，复用 `core/math/AttackSpeedCurve` 与 `Settle`。

### 13.5 R3 的更正（不改 D19 结论，只修前提）

> **D19 / §12 的一条事实前提在 1.21.1 上不成立**：原文写「原版 `minecraft:haste` 不直接改 `attack_speed`」。
> 1.21.1 的 `MobEffects.DIG_SPEED` 注册时自带
> `addAttributeModifier(ATTACK_SPEED, minecraft:effect.haste, 0.1, ADD_MULTIPLIED_TOTAL)`
> （server jar 字节码实读），即**原版急迫每级 +10% 攻速**。那条结论只在 1.20.1 成立。
>
> 处理：**数值口径不动**（急迫 I +10% … VIII +80%），改为「检测到原版 `minecraft:effect.haste` 就让位」，
> 避免双计。实测急迫 II：4 → 4.8（去重前 5.76）。已开 Q-013 让 Aki 确认。
> 另记一个字段名坑：`MobEffects` 没有 `HASTE` 字段，是 `DIG_SPEED`（注册 id 仍为 `minecraft:haste`）。

### 13.6 下一步（R5）

1. **M2 起步：`ContentData` 组件 + 14 基底物品**。`DataComponentType` 是启动期冻结的注册表项，先定 schema 再铺内容（D17）。
   第一件验证件要同时验三件事：白板化（D21：`ATTRIBUTE_MODIFIERS` 非空即屏蔽底材）、自定义伤害类型
   （复用 `verification_strike` 的模式，M2 起每把武器带自己的 `redtale_project:*` 类型，才会进 L2 乘区）、
   tooltip（D20：单次伤害 + 攻速 tick / 次每秒，`show_dps` 默认关）。
2. **条件乘区**：`pve_damage` / `pvp_damage` / `undead_damage` 需要按目标分类，与 `ItemTooltipEvent` 同批做，
   保证 tooltip 与结算同源（`Settle` 只有一份实现这条已经守住）。
3. **`CriticalHitEvent`**：M2 验它能否同时作为原版与 BetterCombat 的暴击入口（冲突面只有 1 个 mod）。
4. **玩家上下文补验**：仍有客户端缺口，`/redtale attr attack_speed` 在真人手持不同武器时的值待验（R2 起挂账）。

### 13.7 R4 的三条实现口径（供后续沿用）

| # | 口径 | 理由 |
|---|---|---|
| R4-a | L2 只写**因子**（`amount × factor`），永不写绝对值 | `DAMAGE-PIPELINE` §2 的硬约束靠代码形状守住，不靠注释 |
| R4-b | 乘区事件优先级固定 **LOWEST** | 读到的是所有人算完的数；实测无冲突（原 §10 待验证项已闭环） |
| R4-c | 验收用伤害类型 `scaling: never` | `when_caused_by_living_non_player` 会按难度缩放（0.5/1.0/1.5），对账时会被误判成 bug |

### 13.8 R5 的四条口径 + 下一步（R6）

| # | 口径 | 理由 |
|---|---|---|
| R5-a | 内容 `stats` **一律 `ADD_VALUE`**，百分比只影响显示（`StatFormat`） | 自建属性基值全是 0，`ADD_MULTIPLIED_TOTAL` 乘 0 恒为 0 |
| R5-b | `attack_speed` 在内容里写**目标次/秒**，建栈换算成 `目标 − 4.0` | 与原版剑 `-2.4` 同形态；配置侧不用心算，已发物品重发即可 |
| R5-c | 玩家 `attack_damage` 基值 = **1.0**（`Player#createAttributes` 字节码 `dconst_1`），不是注册表默认 2.0 | 用错每把武器凭空多 1 点（实测 10.8 vs 9.6） |
| R5-d | 白板化验收读 `ItemStack#forEachModifier`，**不要**用 `setItemSlot` + 读 `ARMOR` | 装备属性每 tick 才刷进 `AttributeMap`，不 tick 的 `FakePlayer` 三组全 0 |

下一步（R6）：

1. **`weapon_attributes` 生成器**：把内容里的 `weapon_attributes` 写成 `data/<ns>/weapon_attributes/*.json` 进 `world/datapacks/redtale_project/`，`/reload` 生效；一件真剑在 BetterCombat 下挥得动 = M2 出口的一半。
2. **条件乘区**：`pve_damage` / `pvp_damage` / `undead_damage` 按目标分类，与 tooltip 同批（同一个 `settle()`）。
3. **`CriticalHitEvent`** 验暴击入口（冲突面只有 Cataclysm 一个 mod）。
4. **玩家上下文补验**（挂账 4 轮）：`/redtale give` → 手持 → tooltip → 平砍对账，需要一次带客户端或真人的验收窗口。

### 13.9 双队列分工（2026-11-15 23:05，Aki 拍板）

S8 上线。机制 = **S7 派单 / S8 写码 / S7 验收**，卡板是唯一接口。

- 规则与卡板：`docs/TASKS.md`（状态机、在制品 ≤3、独占文件、单卡 ≤1 类 / 200 行、三振拆卡、只加不删、`NEED-S7` 出口）。
- 冻结接口：`docs/CONTRACTS.md`（S8 只读；要改走 S7 或开 `Q-`）。
- S7 每轮顺序：验 `[DONE]` → 拆超期 `[DOING]` → 在制品 <3 时派 1 张新卡 → 再推进自己的里程碑。派单必须给定**接口签名**，不许让 S8 自己设计。
- S8 只做卡上的事；卡外文件一律不碰。半成品保持 `[DOING]`，下轮**续做优先**。
- 防冲突只靠两条：卡上「独占文件」在 `VERIFIED` 前 **S7 不碰**；`.queue/build.lock` 取不到就跳过构建，不删别人的锁。
- 台账口径：S8 的产出记在卡上，`VERIFIED` 之后才进本表，避免半成品污染里程碑。

首批派单：**T-0001** `weapon_attributes` 生成器（R6-1）、**T-0002** `/redtale content list`。

### 13.10 R6 的四条口径 + 下一步（R7）

| # | 口径 | 理由 |
|---|---|---|
| R6-a | 条件项与无条件项**进同一个百分比池相加**，不连乘 | 物理 +20% + 对亡灵 +30% = ×1.5，不是 ×1.56；与 §11「先加后乘」一致，玩家对账也按加法 |
| R6-b | 分类：玩家→`pvp`；亡灵（`#minecraft:undead`）→`pve`+`undead`；其它→`pve` | 「对怪物」覆盖全部非玩家，「对亡灵」是其子集加成；互斥会让换目标时整段失效 |
| R6-c | 条件段默认全开，不设独立开关 | 三条属性基值都是 0，没内容写时行为与关着一致（D1 全做，不为省事留开关） |
| R6-d | 错键（非 `pvp/pve/undead`）**告警 + 跳过**，不静默 | 写错键不生效比报错更难查，与 R1-a 分级失败同源 |

下一步（R7）：

1. **`weapon_attributes` 只有数据、没有组件**（R6 查代码新发现）：`ItemFactory` 把 id 写进 `ContentData`，但从未设成 BetterCombat 的 `bettercombat:weapon_attributes` 物品组件 → T-0001 生成的 datapack 文件**不会被物品自动用上**。
   做法：取 `BuiltInRegistries.DATA_COMPONENT_TYPE.get(id).codec()`，用 `JsonOps` 把内容里的定义 JSON 解析成组件值再 `stack.set(...)`，**全程不 import BetterCombat 类**（D15）。
2. **条件乘区分项显示**：`DamageTrace.Entry` 加条件键，`/redtale damage` 把 `0.5` 拆成「物理 0.2 / 亡灵 0.3」。要改 `RedtaleCommand.java` —— 等 T-0002 `VERIFIED`（那是它的独占文件）。
3. **`CriticalHitEvent`** 验暴击入口（R6 顺延，冲突面只有 Cataclysm）。
4. **玩家上下文补验**（挂账第 6 轮）：攻速 + pvp 真目标两件事都要一次带客户端的窗口。
5. **验收 T-0001 / T-0002 / T-0003**：T-0001 的测试服那条（datapack 落地 + `/datapack list` + demo_longsword 的 `bettercombat:claymore` 未被覆盖）归 S7。

### 13.11 R7 的四条口径 + 下一步（R8）

| # | 口径 | 理由 |
|---|---|---|
| R7-a | 武器动作拆成**两件事**：数据包给定义，物品组件给引用。只做前者等于没做 | `WeaponRegistry#getAttributes(ItemStack)` 先读组件 `bettercombat:preset_id`，拿不到才按物品注册 id 回落（字节码实读） |
| R7-b | **生成器**只转 `redtale_project:` 的定义；**组件**任何命名空间都挂 | `bettercombat:claymore` 的定义在别人 jar 里（不能写、不能覆盖），但物品要引用它只能靠组件；引用 ≠ 覆盖 |
| R7-c | 武器动作组件按**字符串**运行期查（`BuiltInRegistries.DATA_COMPONENT_TYPE.get`），零 import、零 `compileOnly` | D15：BetterCombat 不作前置；没装时 `get` 返回 null，静默跳过，不报错 |
| R7-d | tooltip 报「动作 <id>」= **组件挂上了**，不声称「挥得动」 | 后者要客户端；服务端能证的只有组件与数据包 |

下一步（R8）：

1. **数据包自动启用**（R7 唯一遗留）：运行期新生成的 datapack 只在「available」里，不 `/datapack enable` 就不生效。
   做法：reload 生成完文件后，查 `server.getPackRepository()` 的可用 id 是否含 `file/redtale_project` 且未 selected，
   是则 `addPack` + `reloadResources`（一次，失败只告警）。**未验证能否在 reload 中重入，先单独验再接线。**
2. **验收 T-0002 / T-0003 / T-0004**（三张都在制，S8 领了才有 `DONE`）。
3. **`CriticalHitEvent`** 验暴击入口（R4 起顺延，冲突面只有 Cataclysm）。
4. **玩家上下文补验**（挂账第 7 轮）：攻速 + 真目标 pvp，都要一次带客户端的窗口。
5. **D15 收口**：BetterCombat 双持 ×1.2 与我们的 `ADD_MULTIPLIED_TOTAL` 是否重复计（需要真人双持，挂账）。

### 13.12 R8 的三条口径 + 下一步（R9）

| # | 口径 | 理由 |
|---|---|---|
| R8-a | 运行期生成的数据包必须走**三步**：`repo.reload()`（让新目录进 available）→ `addPack(id)`（选中）→ `server.reloadResources(selectedIds)`（真重载） | 少任一步都不生效：不 reload 则 available 里没有；不 addPack 则不在 selected 里；不 reloadResources 则注册表还是旧的。这三步就是原版 `/reload` 的内部动作 |
| R8-b | **启动期只选中、不重载**（`server.isRunning()` 为假时返回 `ENABLED_PENDING_RELOAD`） | `ServerStartedEvent` 里资源刚加载完，再重载纯浪费；启动期新包由下一次原版/我们自己的 `/reload` 带入 |
| R8-c | 重载**按时间窗去重**（2s 内只触发一次） | 防止「启动事件 + 手动 reload」在同一窗口各调一次 `reloadResources`，重载会把 `RecipeManager` 等全跑一遍（测试服里 SimplySwords 的坏配方日志会刷两次） |

下一步（R9）：

1. **`CriticalHitEvent`** 验暴击入口（R4 起顺延 4 轮，冲突面只有 Cataclysm；`enchantment` 侧已确认原版 `damage` 组件走平加池）。
2. **T-0003 落地后接词条 roll**（D22）：`AffixPools.parseDefs/parsePools` 已给接口，`ItemFactory` 里 roll 一次写进 `ContentData.affixes`，tooltip 的「词条」列（T-0002 留的占位）换成真实计数。
3. **验收 T-0003 / T-0004 / T-0005**（三张都在制；T-0004 的转换正确性要 S7 用样例跑）。
4. **玩家上下文补验**（挂账第 8 轮）：攻速 + 真目标 pvp，都要一次带客户端的窗口。
5. **14 基底物品 lang**：T-0005 交付后起测试服 `/give` 一件确认显示中文名而非 `item.redtale_project.sword`。

### 13.13 R9 的四条口径 + 下一步（R10）

| # | 口径 | 理由 |
|---|---|---|
| R9-a | 暴击**只走 `CriticalHitEvent`**，不在 `LivingIncomingDamageEvent` 自己 roll | 一个点覆盖原版与 BetterCombat（后者 jar 内 `CriticalHitEvent` 零引用）；暴击在「出手」，乘区在「落地」，不抢同一个数 |
| R9-b | 只写**倍率**（`setDamageMultiplier`），永不写绝对值 | 与 R4-a 同源 |
| R9-c | 原版跳跃暴击默认**换成我们的倍率**（`apply_to_vanilla_crit: true`；1.5 → 2.0） | Q-008 已定倍率基值照搬上游 2.0；两套倍率共存会让玩家对不上账。想保留原版 1.5 改一行配置 |
| R9-d | 暴击探测必须**同基数**：`attackStrengthTicker` 顶满、`invulnerableTime` 归零、木桩护甲 0 | `attack_damage × (0.2 + scale²×0.8)`，scale 不满或吃无敌帧，比值无意义 |

下一步（R10）：

1. **验收 T-0004 / T-0005 / T-0006**（T-0003 本轮已 `VERIFIED`）。T-0004 的转换正确性要 S7 用样例跑（3 条写出 / 缺 `supported_items` 跳过 1 条 / 外部命名空间落对目录）；T-0005 要验两份 lang 的 `item.redtale_project.*` = 14 且 `attribute.*` 仍 66、幂等 md5 不变。
2. **词条 roll 接线**（D22，T-0003 已 `VERIFIED` → `AffixPools` 归 S7）：先把 `AffixPools.Def.stats` 升到 `StatValue`（`base` + `per_item_level`，ITEM-MODEL §2 的曲线形态，当前签名只装平加值——这是 R9 记下的欠账），再在 `ItemFactory` 里 roll 一次写进 `ContentData.affixes`，`ContentTooltip` 与 `/redtale content list` 的「词条」列换真实计数。
3. **M2 剩下的两块**：消耗品（D23 右键生效）与修理（磨刀石）。这两块可以自己写，也可以拆卡给 S8——先做消耗品，它需要 `Item.use` 覆写（14 基底已固定，加行为不用换注册表）。
4. **玩家上下文补验**（挂账第 9 轮，含 R9 遗留三条）：原版跳跃暴击走我们倍率、BetterCombat 真挥砍是否也走 `Player#attack`、`/redtale attr attack_speed` 真人手持、真目标 pvp。全部要一次带客户端的窗口。


### 13.14 R10 的五条口径 + 下一步（R11）

| # | 口径 | 理由 |
|---|---|---|
| R10-a | `weapon_attributes` **不限制命名空间**，但「引用」与「覆盖」必须可区分：只引用 → 只挂组件；要改 → 配置目录里放 `ns__path.json5` | 无脑放开会让「引用一个外部 id」等于「篡改它」，别人整合包的行为会因我们写一行配置而变。代码可审计（`git diff`）+ 日志留痕（WARN） |
| R10-b | 「统一 tag」= `ContentData` 单组件，加 `schema`（结构版本）与 `content_rev`（定义修订号）两个数字，**不合并** | 变化源不同：`schema` 变是发版要迁移，`content_rev` 变是作者调数值不需迁移。合并会让「改剑的攻击力」触发一次结构迁移 |
| R10-c | 迁移**只重建定义型字段**，`rolled_stats` / `affixes` / `upgrade_level` 一个都不动；只清「新定义里已不存在的键」并 `LOG.info` 记账 | 这是这类系统最经典的事故：全量重建会把玩家强化过的装备冲回出厂值。删键必须留证据，否则投诉「属性少了」时无从对账 |
| R10-d | **不白送新键**：新定义加 `crit_chance`，老物品不自动获得 | 否则改一次配置 = 给全服免费发一轮属性 |
| R10-e | 同步方向：**服务端改完推**（`broadcastChanges` / `broadcastFullState` / `setRemoteSlot`），**不做客户端上报** | 客户端上报物品属性 = 复制与改属性作弊的头号入口。服务端本来就知道自己改了什么，没有上报的必要 |

下一步（R11）：

1. **验收 T-0003 / T-0004**（仍在 `OPEN`，S8 未领）。本轮把 `T-0005` 撤下换 `T-0006`（`ItemUpgrader`），因为它卡住 M2 出口。
2. **`ItemUpgrader.ensure` 落地后立刻接三个钩子**（登录 / `PlayerContainerEvent.Open` / `ChunkEvent.Load`）——钩子归 S7，事件注册在 `GameHooks`。
3. **`/redtale item scan`** 先上（只读，让运营能看见 rev 分布与孤儿数），再做 `upgrade`。
4. **玩家上下文补验**（挂账第 10 轮）：U6（箱子里的物品重载区块后更新）必须真开一次箱子，这是唯一能证明「不是只有登录才更新」的证据。

### 13.15 R11 的五条口径 + 下一步（R12）

| # | 口径 | 理由 |
|---|---|---|
| R11-a | 词条三样一次写全：数值进 `rolledStats`、键进 `rolledKeys`、id 进 `affixes` | tooltip / 结算 / 迁移读同一份；少写一样就出现「tooltip 有词条、面板没数值」 |
| R11-b | 属性键在**解析期**归一（`AttributeSpecs.resolve`），不在消费期 | 消费期归一救不了「同一 modifier id 两条」，面板会翻倍 |
| R11-c | `AffixRoller` 用 `java.util.Random`，零 MC 依赖 | 要能被 `gradle selftest` 离线跑，seed 固定就能验收 |
| R11-d | 物品等级固定 `ITEM_LEVEL = 1` | 等级系统（M3）未接；接上只改一个常量 |
| R11-e | 默认词条配置必须进 `DEFAULT_FILES` | `ensureDefaults` 是白名单，只放 resources 里 = 新环境静默无词条 |

下一步（R12）：

1. **验收 T-0006 / T-0007**（T-0006 仍 `OPEN`，S8 未领；T-0007 本轮新派）。
2. **`ItemUpgrader.ensure` + 三个刷新钩子**（登录 / `PlayerContainerEvent.Open` / `ChunkEvent.Load`）：卡交付后立刻接，钩子归 S7。
3. **`/redtale content list` 词条列换真实计数** + `/redtale affix`（看分布 / 手动 roll），两件都是 `RedtaleCommand` 的插入，等 T-0007 `VERIFIED` 再做。
4. **M2 剩下的两块**：消耗品（D23 右键生效，`Item.use` 覆写不改注册表）与修理（磨刀石，作用于别的物品）。
5. **玩家上下文补验**（挂账第 11 轮）：原版跳跃暴击走我们倍率、BetterCombat 真挥砍是否也走 `Player#attack`、真人手持 `attack_speed`、真目标 pvp、词条在真人背包里的 tooltip。

### 13.16 R12 的四条口径 + 下一步（R13）

| # | 口径 | 理由 |
|---|---|---|
| R12-a | `ensure` 只走四条出口：`NOT_CONTENT` / `ORPHAN` / `UNCHANGED` / `UPGRADED`；**`ORPHAN` 一个数值都不改** | §4.4：孤儿不是错误数据，是「内容被删」的正常状态；改了会让「补回定义」失去意义 |
| R12-b | 词条只删「定义里已不存在」的 id，**且词条表为空时原样保留** | 没装词条配置 ≠ 全服词条作废。空表当「全部失效」是典型静默数据事故 |
| R12-c | `plan` 只做过滤，**取值分派在 `ensure`**（`rolled_keys` 的保留旧值 / 其余跟新定义） | T-0006 卡面的边界划分；`plan` 保持纯过滤 → 无 MC 依赖、可离线单测 |
| R12-d | 刷新点日志**只在真改了东西时打** | 三个钩子每 tick 可能触发，静默路径不能刷屏；改了就一定要留证据（删键逐条记账） |

实测（测试服，箱子 + `forceload remove/add` 强制区块重载）：A 组 `rev 0→3` 同时验证「`rolled_keys` 保留 5.0 / 未 roll 的 `physical_damage` 跟新定义 0.1→0.25 / `ghost_key` 删除并记账 / 名称·稀有度·耐久上限重建」；B 组 `rev` 相等与 C 组孤儿**组件逐字未变**。

**新记一条操作事实**：手写 `redtale_project:content` 组件时 `rolled_stats` 的键必须是**归一后的全名**（`minecraft:generic.attack_damage`），写裸名 `attack_damage` 会被当成「定义里没有」而删掉。`ItemFactory.build` 自己写的是全名，不会踩；运营手写 `/give` 会踩（日志有记录）。

下一步（R13）：

1. **验收 T-0007**（`/redtale item scan`）与 **T-0008**（消耗品 `use` 段解析器）。在制品 2/3。
2. **`ensure` 接进结算路径**（惰性兜底 ⑤）：`ItemTooltipHook` 客户端也会触发，改写物品必须限定服务端；放 `DamageLayer` 更合适。
3. **刷新点 ④**：`/redtale reload` 之后按 tick 分帧扫已加载区块（每 tick N 块）。
4. **M2 最后一块**：消耗品右键生效 + 修理（D23）。`ConsumableSpec` 交付后由 S7 接线。
5. **挂账（第 12 轮）**：真人登录 / 背包 / 副手 / 末影箱的更新、`/redtale item scan` 的真人背包分布、tooltip 在真人客户端的样子。

### 13.17 R14 的四条口径 + 下一步（R15）

| # | 口径 | 理由 |
|---|---|---|
| R14-a | ④ 号刷新点**只挂在「管理员显式 `/redtale reload`」**上，不挂 `RedtaleCore.reload()` | 启动期那次 reload 不存在「配置换了」这件事；实测 `isRunning()` 在 `ServerStartedEvent` 已为真，靠它拦不住（第一版因此开局扫了 25 区块） |
| R14-b | 队列存**坐标**不存 `LevelChunk` | 持有区块对象会阻止回收（内存泄漏），且排队期间区块可能卸载；取的时候再 `getChunkNow`，取不到就跳过，交给 ③ 号钩子补 |
| R14-c | 覆盖分三层：**玩家背包（立即）→ 掉落物/展示框（立即）→ 容器（排队）** | 实体不在方块实体表里，`§4.1 ③` 的 `getBlockEntitiesPos()` 扫不到掉落物与展示框；背包才 41 格，不值得进队列 |
| R14-d | 每 tick **8 区块**写死，不做配置项（先） | 实测 52 区块 315~344ms 总耗时，单 tick ~6ms；等正式服区块量真的压出卡顿再提成 `chunks_per_tick`，不提前造旋钮 |

下一步（R15）：

1. **验收 T-0008 / T-0009 / T-0010**（三张在制）。T-0009 的交付含 `ItemUpgradeCommand`，`RedtaleCommand` 的挂行归 S7（T-0002 同款做法）。
2. **惰性兜底 ⑤**：`ItemTooltipHook` 客户端也会触发，改写必须限定服务端 → 放 `DamageLayer`（结算路径）与 `/redtale` 读路径，**不放 tooltip**。
3. **M2 出口剩余两块**：消耗品右键生效（等 T-0008）、磨刀石修耐久（等 T-0010 后 S7 做 `/redtale repair`）。
4. **挂账第 13 轮**（需要一次带客户端的窗口）：`item scan` 件数/rev 分布、`/redtale give` 真人手持、tooltip 真人样子、真人 pvp、真人双持 ×1.2。

### 13.18 R15 的五条口径 + 下一步（R16）

| # | 口径 | 理由 |
|---|---|---|
| R15-a | 消耗品定义**不进 `ContentData`**，右键时按 `contentId` 现查 | 改 `use` 段 + `/redtale reload` 对存量物品立刻生效，不必 rev+1；D33 的迁移面不扩大 |
| R15-b | `use` 段**只能挂非护甲基底**（武器 8 + 饰品 2），护甲基底解析期丢弃 + WARN | 护甲基底是 `ArmorItem`，`use()` 的语义是「穿戴」；抢过来会让护甲穿不上，失败方式还很隐蔽 |
| R15-c | 客户端 `use()` 一律 `CONSUME`，**一切副作用只在服务端** | 客户端不知道有没有 `use` 段、够不够饿；双端各算一遍 = 双扣物品 |
| R15-d | `only_when_hungry` 不满足 → `FAIL`（不扣件 / 不进冷却 / 不生效） | 与「用了但没效果」区分开，玩家一眼看出被门槛挡住 |
| R15-e | `use.script` 走 `ScriptEngine.runCalls`，**不进 `scripts/` 注册表** | 那段脚本属于这件物品，不是全服触发器；单条失败只记日志，其余照跑 |

**14 基底里没有「食物」这一格**（`ITEM-MODEL.md` §3.1 的样例写的是 `base: "minecraft:rabbit_stew"`，而我们的 `base` 只认 14 个 `ItemBase`）。
本轮按「复用 `amulet` 顶外观」落地（零注册表变更），并开 **Q-016** 待拍板（默认 A 复用饰品基底 / B 加第 15 基底要换 jar / C 允许 `base` 写原版物品）。

下一步（R16）：

1. **验收 T-0009 / T-0010 / T-0011**（三张在制）。T-0009 交货后 `RedtaleCommand` 的挂行归 S7（T-0002 同款做法）。
2. **M2 最后一块**：`RepairSpec` 到位后做磨石结算 + `/redtale repair`。
3. **惰性兜底 ⑤**：`DamageLayer` 与 `/redtale` 读路径上调 `ItemUpgrader.ensure`（**不放 tooltip**，客户端也会触发）。
4. **挂账第 14 轮**（需一次带客户端的窗口）：真人右键消耗品（手势 / 冷却 HUD）、`item scan` 真人背包分布、tooltip 真人样子、真人 pvp、BetterCombat 双持 ×1.2。

### 13.19 R16 的四条口径 + 下一步（R17）

| # | 口径 | 理由 |
|---|---|---|
| R16-a | 修理结算只有一份实现 `Repairer.apply(spec, target)`，右键与 `/redtale repair` **同一段代码** | 一份数值两处入口必然漂移；命令里不留「管理员版逻辑」，管理员多的只是「指定槽位」 |
| R16-b | 目标选择 = **副手优先 → 否则背包里损伤最重且匹配的一件**；工具按**对象身份**排除，绝不会修到自己 | 右键必须可预期（磨刀石有代价），「副手优先」给精确控制，「最破的那件」给不想切手的顺路便利。Q-017 已登记待 Aki 定 |
| R16-c | 失败一律返回 `PASS` 而不是 `FAIL`（目标不可修 / 已满 / 不匹配）；扣件只在 `APPLIED` 且 `consume_item` 时 | `FAIL` 会让「右键看到消息」变成「这次右键作废」，把副手格的其他用途也一起挡掉 |
| R16-d | `repair` 段与 `use` 段同口径：**不进 `ContentData`**，右键按 `contentId` 现查 | 改配置 + `/redtale reload` 对存量物品立刻生效，D33 的迁移面不扩大（少一个要 rev+1 的字段） |

**三条实测事实（写进 memory，别再踩）**：

1. `FakePlayer` 的 `setItemInHand(OFF_HAND, x)` 确实把物品写进了 `player.getInventory().offhand`，但同一时刻 `getItemInHand(OFF_HAND)` 与 `getItemBySlot(EquipmentSlot.OFFHAND)` **都返回 `air`**（列表里有、读不到）。→ 探测与结算读副手统一用 `inventory.offhand.get(0)`；对真玩家两者等价。
2. `FakePlayer` 默认 **`instabuild = true`**：不置 `false` 就验不出「扣件」，会误判成「修好了但没扣」。
3. `ItemStack#use` 的真修好分支返回 **`CONSUME`**、失败分支 `PASS`。探测里先看返回枚举，比看计数更早暴露「分支没进去」。

下一步（R17）：

1. **验收 T-0011 / T-0012**（T-0011 十四基底 lang，T-0012 `rev` 漏加检测）。T-0012 的功能验收要三次运行（建基线 → 改文件不加 rev → 加 rev），归 S7。
2. **M3 起步（宝石 / 套装）**：先在 `docs/ITEM-MODEL.md` 补 §5「孔位与套装」schema（`sockets` / `set_id` / 件数加成），再派解析器 —— 顺序不能反，S8 没有设计上下文。
3. **惰性兜底 ⑤**：`DamageLayer` 与 `/redtale` 读路径上调 `ItemUpgrader.ensure`（**不放 tooltip**）。
4. **M2 剩余两块非阻塞项**：等级门槛（`level_requirement`）与掉落表；M2 出口的 U1~U10 已在 R14 全绿，这两项属于「M2 的完整性」而非出口条件。
5. **挂账第 15 轮（需一次带客户端的窗口）**：`rev` 落后物品 → `/redtale item upgrade` 计数 → 客户端 tooltip 立刻变；真人右键磨刀石（副手/最破）、真人右键消耗品、`item scan` 真人背包分布、tooltip 真人样子、真人 pvp、BetterCombat 双持 ×1.2。

### 13.20 R17 的四条口径 + 下一步（R18）

| # | 口径 | 理由 |
|---|---|---|
| R17-a | 惰性兜底 ⑤ 只处理**攻击者主手**，不遍历背包 | L2 只读攻击者属性，别的槽位读了也没用；遍历会把热路径变成背包扫描 |
| R17-b | 惰性兜底**不放 tooltip** | `ItemTooltipEvent` 客户端也触发，在客户端改物品 = 让客户端凭空造属性（R10-e 同源） |
| R17-c | `ensure` 在结算路径上抛异常 → **按旧版结算** + WARN，不中断本次伤害 | 结算路径崩一次 = 一次打不出伤害；宁可让这件物品旧一版 |
| R17-d | `UPGRADED` 且执行者是 `ServerPlayer` → `inventoryMenu.broadcastChanges()` 一次 | `ensure` 改的是同一个 `ItemStack` 实例（服务端内存已新），客户端仍是旧组件，必须主动推 |

**宝石数值的容器口径（M3 定稿，写进 `ITEM-MODEL.md` §5.1）**：宝石数值单列 `ContentData.gemStats{}`，**不并进 `rolled_stats`**。同一属性若被词条与宝石各加过，并在一个键里 → 拆宝石会把词条那部分一起扣掉（扣不准）。两表分开后，拆宝石 = 重算 `gemStats`，词条一个数都不动。

**一条操作事实（别再踩）**：`demo_*.json5` 都**没写 `rev`**（缺省 0），所以拿它们当「过期件」永远走 `UNCHANGED` 快路径。要验迁移必须用带 `rev` 的定义（如 `t_upg_sword` rev 3）。

下一步（R18）：

1. **验收 T-0012 / T-0013**。T-0012 的功能验收要三次运行（建基线 → 改文件不加 rev → 加 rev +1），归 S7。
2. **M3 第 3 步**：`ContentData` 加 `sockets[]` / `gemStats{}`，`CURRENT_SCHEMA` 1 → 2，`ItemUpgrader` 加迁移分支（属 S7：注册表结构 + codec 会牵动 `ItemFactory` / `ItemUpgrader` / `ItemScanCommand` 三处读路径）。
3. **M3 第 4 步**：镶嵌 / 取出结算 + tooltip 孔位行 + `/redtale socket`。
4. **挂账第 16 轮（需一次带客户端的窗口）**：`rev` 落后物品 → `/redtale item upgrade` 计数 → 客户端 tooltip 立刻变；真人右键磨刀石 / 消耗品；`item scan` 真人背包分布；tooltip 真人样子；真人 pvp；BetterCombat 双持 ×1.2；本次惰性兜底的 `broadcastChanges` 在真人客户端是否立刻刷新。

### 13.21 R18 的四条口径 + 下一步（R19）

| # | 口径 | 理由 |
|---|---|---|
| R18-a | `sockets` / `gemStats` 是**玩家资产**，`ensure` 重建时**原样带出**，不重算、不清空 | 玩家镶进去的宝石不能因为一次 `/redtale reload` 消失。孔位**布局**（孔数）对齐属第 4 步镶嵌结算，入口在 socket 结算处，不在 `ensure` 里猜 |
| R18-b | `ItemUpgrader.SCHEMA` 写成 **`ContentData.CURRENT_SCHEMA` 的引用**，不写字面量 | 两处各写一个数字，早晚漂一次；漂一次的后果是「schema 判据恒假 → 全服物品永不迁移」，静默且难查 |
| R18-c | 新增字段一律 `optionalFieldOf` + 默认值，**不做 NBT 迁移**；靠 schema 版本触发一次重建 | 老 NBT 缺字段要能照常解码，否则玩家存档里的物品会整批反序列化失败；而「孔序要与定义对齐」这件事需要一次真实重建，靠 schema 版本号触发比靠 rev 变更干净 |
| R18-d | 面板只体现「这件实例真有的键」（`rolled_stats` ∩ 定义），缺的**不白送** | 手写件只写了 `attack_damage` 时，面板就只有 `attack_damage`；`physical_damage` 虽在定义里但不补（U3） |

**一条 codec 事实（务必记住）**：`Codec.INT.optionalFieldOf("schema", CURRENT_SCHEMA)` 在值**等于默认值时不写字段**。所以升级到 schema 2 之后，物品组件里**看不到** `schema` 键 —— 那表示「当前版本」，不是「没迁移」。验迁移的判据是「字段消失」；显式写着 `schema:1` 的才是旧版。

**一条边界（第 4 步要做）**：定义把孔数**改小**要截断 `sockets`、**改大**要补空孔，且被截掉的孔里若有宝石要退回玩家背包（不能静默吞）。现在 `ensure` 只带出，不做这件事。

下一步（R19）：

1. **验收 T-0013 / T-0014**。T-0013 的解析正确性由 S7 用离线探针跑（缺段返 null/EMPTY 且零告警 / count 夹取 / types 补齐与截断 / 非法项换 `any` / `stats` 走 `AffixPools` 同一条归一 / 不可变）。
2. **M3 第 4 步（S7）**：`ItemContent` 加 `sockets` 段（`SocketSpec.Layout`）→ `ItemFactory.build` 按布局填空孔 → 镶嵌 / 取出结算（`gemStats` 重算 + 互斥）→ tooltip 孔位行 → `/redtale socket`。**顺序不能反**：先让定义能写出孔数，再谈镶嵌。
3. **`sets/*.json5` 默认配置 + `DEFAULT_FILES`**（R11-e 的教训：只放 `resources` 不会落地），随 T-0014 验收后一起做。
4. **挂账第 17 轮（需一次带客户端的窗口）**：`rev` 落后物品 → `/redtale item upgrade` 计数 → 客户端 tooltip 立刻变；真人右键磨刀石 / 消耗品；`item scan` 真人背包分布；tooltip 真人样子；真人 pvp；BetterCombat 双持 ×1.2；schema 1→2 全量迁移后真人客户端面板是否刷新。

### 13.22 R19 的五条口径 + 下一步（R20）

| # | 口径 | 理由 |
|---|---|---|
| R19-a | 内容数值与宝石数值的 modifier id **必须分开**（`content/<属性>` vs `gem/<属性>`） | `AttributeMap` 同 id 是「后加覆盖先加」；同属性既有词条又有宝石时会凭空少一块，且只在特定组合下复现（实测 9.1 = 7 + 2.1） |
| R19-b | 取宝石 = **重算整张 `gemStats`**（`Socketer.solve`），不是「减去那颗宝石的数」 | 相减会累积误差；重算永远与当前孔序一致，探针 `取出孔 0 → 只剩 1 条` 即此 |
| R19-c | 孔数**只补不截**：`ensure` 按新定义补空孔，改小时**不截断**，只逐条记账 | 截断 = 无声销毁玩家资产（R10-c 的延伸）；代价是「改小孔数」需要管理员先 `socket extract`，看得见 |
| R19-d | 宝石是**内容物品**（`gem` 段），不是注册表项、不是新组件 | 加一颗宝石 = 写一份 json5 + `/redtale reload`（D17）；因此镶嵌引用的是**内容 id**，不是物品注册 id |
| R19-e | 结算层不碰背包：被替换 / 取出的宝石由**调用方**退回 | 结算要能被命令、NPC、脚本三处复用；退回策略（塞背包 / 掉地上）属于入口的职责 |

**两条实测事实（记牢）**：
1. `ItemFactory.modifierId(spec)` 产出的是 `content/<spec.path()>`，而 `spec.path()` 对原版属性是 **`generic.attack_damage`**（带组前缀），
   所以面板里的 id 是 `redtale_project:content/generic.attack_damage` —— 验收时 grep `:content/attack_damage` 会**假失败**。
2. `ItemContent` 从 12 字段变 14 字段是**编译期硬断点**：全仓库只有 `ItemContent.parse` 一处构造，改 record 后必须同步那一处（已确认唯一）。

下一步（R20）：

1. **验收 T-0014 / T-0015**（T-0014 套装解析器在制；T-0015 `/redtale validate` 本轮新派）。T-0014 的解析正确性由 S7 用离线探针跑（`sets/` 前缀筛 / id 空串跳过 / pieces 去重 / `count<1` 跳过 / 档位升序 / `activeBonuses` 全档生效 / 不可变）。
2. **M3 第 6 步（S7）**：`ItemContent.setId` + `ItemFactory` 写 `ContentData.set_id` + 件数统计（护甲 4 + 主副手）+ 属性下发（固定 id `redtale_project:set/<setId>/<count>`，先移除再加）+ tooltip 套装行 + `/redtale set`；`sets/*.json5` 默认配置必须进 `DEFAULT_FILES`（R11-e 的教训）。
3. **`/redtale socket` 的真人路径**（挂账）：真人手持 → 镶嵌 → 客户端 tooltip 立刻变（服务端已 `broadcastChanges`，但没客户端没验过）。
4. **挂账第 18 轮（需一次带客户端的窗口）**：`rev` 落后物品 → `/redtale item upgrade` 计数 → 客户端 tooltip 立刻变；真人右键磨刀石 / 消耗品 / 镶嵌；`item scan` 真人背包分布；tooltip 真人样子；真人 pvp；BetterCombat 双持 ×1.2；schema 1→2 全量迁移后真人客户端面板是否刷新。



### 13.23 R20 的五条口径 + 下一步（R21）

| # | 口径 | 理由 |
|---|---|---|
| R20-a | `set_id` 是**定义型字段** → `ItemUpgrader.ensure` 重建时取**新定义**的值，不是照抄旧的 | 照抄 = 改了 `set_id` 老物品永远不跟，与「改定义型字段要 rev+1」自相矛盾。对比 R18-a：`sockets` / `gemStats` 是玩家资产才「原样带出」 |
| R20-b | 套装数值**永不进 `ContentData`**，只写玩家属性上固定 id `redtale_project:set/<setId>/<count>` | 件数是「玩家穿了一组」的派生态。写进物品组件 = 把派生数据当事实存，脱一件还得去改另一件的组件 |
| R20-c | 每轮重算**先按「定义里声明过的档位」整段移除，再按当前件数加回** | 只加不减是这类机制最常见的漏：件数 3→2 时 `.../3` 的 id 留在属性上，面板虚高且只在这个操作序列下复现（本轮 probe 第 ④ 步专测这一条） |
| R20-d | 件数按**内容 id 去重**，格子固定 6 个（护甲 4 + 主手 + 副手） | §5.4 的口径：同一件戴两份只算一件。按槽位计数会让「两个一样的戒指」白送档位 |
| R20-e | 复核周期 **20 tick**（不是每 tick），且**签名没变就完全不碰属性** | 换装没有可靠单点事件（背包点击 / 快捷栏 / 被打掉 / 死亡掉落都会改装备），只能轮询；而 `AttributeInstance` 一写就重算+同步，每 tick 写等于每 tick 同步一次属性 |
| R20-f | 套装档位只取 `StatValue.base()`，`per_item_level` 曲线不参与 | 套装没有「物品等级」这个概念；写进曲线也不会被用（在 `SetBonus.add` 的注释里写明） |

**一条实测事实（务必记住）**：`ItemBase.slot()` 返回 `EquipmentSlotGroup`（`MAINHAND` / `HEAD` …），
而 `LivingEntity#setItemSlot` 要 `EquipmentSlot`；1.21.1 **没有公开的 group→slot 反查**。
`SetBonus.slotOf(base)` 按组单例 `==` 映射（组是原版单例），塞装备的入口统一走它。

**一条内容纪律**：`sets/*.json5` 的 `pieces` 允许写「永远穿不上」的件数档吗 —— 不允许。
本轮默认集故意把 `demo_robe` 排除在外：它与 `demo_chestplate` 同为胸甲基底，写进去就是造一个
「3 件档永远到不了」的静默坑。这项检查归 T-0016（`/redtale set check`）。

下一步（R21）：

1. **验收 T-0015 / T-0016**。T-0015 的功能验要造三份坏配置（`weapon_attributes` 指空 / 池引用未定义词条 / `applies_to` 指 `redtale_project:wand`），
   看问题条数与文案，删掉后回到「没有引用问题」。
2. **M4 起步（S7）**：`ENCHANT-API.md` §3 的 `redtale_project:scripted` 组件 codec + 附魔配方/触发接线。
   顺序：先 codec（组件是注册表项，加字段要换 jar），再脚本层。
3. **`/redtale validate` 加第 5 条检查**（套装引用）：`SetCommand.danglingSets()` 已备好纯函数，等 T-0015 落定再并进去（现在并会撞卡）。
4. **挂账第 19 轮（需一次带客户端的窗口）**：`rev` 落后物品 → `/redtale item upgrade` → tooltip 立刻变；真人穿戴套装 → 客户端属性面板刷新；
   真人右键磨刀石 / 消耗品 / 镶嵌；`item scan` 真人背包分布；tooltip 真人样子；真人 pvp；BetterCombat 双持 ×1.2。

### 13.24 R21 的五条口径 + 下一步（R22）

| # | 口径 | 理由 |
|---|---|---|
| R21-a | 附魔动作层**只做一个** `redtale_project:scripted`，参数走 `CompoundTag` 的 `args` | 一个 effect 实现 = 一个注册表项 = 一次换 jar（F5）。触发时机交给原版 30 个组件，执行体交给 L3 脚本，接口才「加第 N 个附魔只写 JSON5」 |
| R21-b | `scripted.apply` 里**任何异常都不外抛**（脚本缺失 WARN 一次、执行失败 ERROR 一次） | 附魔 effect 跑在伤害/事件链内，抛出去会打断原版流程。`post_attack` 连锁到 5 个目标时刷屏更糟，故脚本 id 报过就进 `Set` 去重 |
| R21-c | L0 附魔**必须重启生效**，`/reload` 只保证「文件写出来了」 | 实测：`/reload` 后文件在包内、`/enchant` 仍 `Can't find element`；重启后立刻可用。`enchantment` 是启动期加载的 datapack registry，这条是 1.21.1 的硬边界，不是配置错误 |
| R21-d | 附魔 JSON5 的中文名**不进 L0 JSON**，只写 `translate` 键，值由 lang 生成器负责 | 与物品/属性同一套（R5、R17 一致）。L0 里塞中文 = 每个语言包都要改 datapack |
| R21-e | `/redtale validate` 的 `applies_to` 检查只认 `redtale_project:` 命名空间；裸名会被 `ResourceLocation.tryParse` 补成 `minecraft:` 而**逃过检查** | 已实测（`applies_to: ["sword"]` → 0 问题）。这是 S8 主动报的口径，认账；R22 补一条「裸名 = 疑似笔误」提示，不改判定语义 |

**一条内容纪律**：`enchantments/*.json5` 的 `effects` 里只允许两类东西——原版组件（原样透传）与 `redtale_project:scripted`。
出现第三个自定义 effect 类型，说明我们在发明 L2，回到 `ENCHANT-API` §4.1 重看一遍。

下一步（R22）：

1. **验收 T-0016 / T-0017**（`set check` 与附魔 lang 生成器；T-0016 的功能验要造三个坏定义）。
2. **M4 第二块（S7）**：`scripted` 的 V9/V10 实测——写 `scripts/enchants_soul_reap.json5` 让 `post_attack` 真跑起来（脚本 id 用 `enchants/soul_reap`），故意写错 id 验「只 WARN 一次、附魔仍在、不崩」。
3. **V8 数值对账（S7）**：`super_sharpness` 已能附上，下一步用 `/redtale damage` 的 trace 对 `minecraft:damage` 的 `linear` 结果（同怪、白板剑 vs 附魔剑）。
4. **`/redtale validate` 第 5 条检查**（套装引用）与**裸名 `applies_to` 提示**（R21-e），T-0015 已归 S7，可以动。
5. **挂账第 20 轮（需一次带客户端的窗口）**：附魔 tooltip 中文名、`rev` 落后物品 → `item upgrade` → tooltip 立刻变；真人穿戴套装面板刷新；真人右键磨刀石/消耗品/镶嵌；真人 pvp；BetterCombat 双持 ×1.2。

### 13.25 R22 的五条口径 + 下一步（R23）

| # | 口径 | 理由 |
|---|---|---|
| R22-a | 附魔 JSON5 里 `script` 字段是**纯字符串脚本 id**，`ScriptedEnchantmentEffect.script` 用 `Codec.STRING` | 用 `ResourceLocation.CODEC` 时裸 id `enchants/soul_reap` 被静默补成 `minecraft:enchants/soul_reap`，与 `scripts/*.json5` 的 `id` 永不相等 → 附魔生效、执行体静默不跑。这类失败**没有任何报错**，只能靠「打了怪却没日志」发现 |
| R22-b | 脚本层占位符只认 `%player%` 与 `%var.<key>%`；**未定义的键原样保留** | 附魔 `args` 先灌进 `ScriptContext.vars` 再交给 effect。保留原样是为了让写错的占位符在日志里可见（换成空串就看不出问题） |
| R22-c | `post_attack` 里 `EnchantmentEntityEffect.apply` 的第 4 参是 **affected 实体（受害者）**，不是攻击者；攻击者武器从 `EnchantedItemInUse.itemStack()` 取 | `EnchantmentHelper.doPostAttackEffectsWithItemSource` 的 `affected` 语义。写「吸血 / 反伤」类执行体时目标就是这具实体，别再去 `vars` 里找攻击者 |
| R22-d | 数值对账（V8）用 `/redtale damage` 的「**最近放行进场值（旧→新）**」，不用血量采样 | 尸壳攻击节奏不受控，血量采样出 3/7/10 混值（同一次窗口里两个来源交错）。进场值是逐事件的精确读数：白板 8.0 / 锋利 I 10.0 / 锋利 III 12.0 |
| R22-e | 内容物品吃自家附魔，靠**生成自己的 item tag**（`data/redtale_project/tags/item/enchantable/weapon.json`），不往原版 `#minecraft:enchantable/*` 里塞 | 1.21.1 的 item tag 是数据驱动、只列原版 id；实测 `/enchant` 对 `minecraft:iron_sword` 成功、对 `redtale_project:sword` 报 `cannot support that enchantment`。改原版 tag 等于改别人的数据 |

**一条排查纪律**：附魔「附上了但没反应」时，按 L0→L2→L3 三段分开验——
`/enchant` 能否附上（L0 在不在注册表）→ 打怪后有没有 `附魔脚本 ... 不存在` 的 WARN（L2 的 id 对不对）→
有没有 `[script] ...` 日志（L3 的脚本 id / effect 对不对）。三段都过才是「链路通」，跳过任一段都会误判。

下一步（R23）：

1. **验收 T-0017 / T-0018**（`gen_enchant_lang.py` 的幂等与 66+14 保留；`validate` 第 5 条要造三条坏定义：piece 不存在 / `set_id` 写错 / 裸名 `applies_to`）。
2. **自建 item tag 生成**（R22-e）：`EnchantmentGenerator` 或新生成器写 `tags/item/enchantable/weapon.json`，两份默认附魔的 `supported_items` 改指向它；验收 `/enchant redtale_project:sword redtale_project:soul_reap 1` 成功、`/redtale tooltip` 仍正常。
3. **`soul_reap` 的执行体**：需要 `heal` 原语 + `ScriptContext` 带 affected 实体（现在 `ofServer` 拿不到实体）。加原语 = 换 jar，按 D17 记账；不加的话这份附魔就只有日志没有玩法。
4. **`exclusive_set` 指向缺失 tag**：启动 WARN `Not all defined tags for registry enchantment are present in data pack: redtale_project:exclusive_set/lifesteal`。编辑器要么生成空的 tag 文件、要么在 `validate` 里报出来（现在没人管）。
5. **挂账第 21 轮（需一次带客户端的窗口）**：附魔 tooltip 中文名（T-0017 做完才能验）、`rev` 落后 → `item upgrade` → tooltip 立刻变、真人穿戴套装面板刷新、真人右键、真人 pvp、BetterCombat 双持 ×1.2。

### 13.26 R23 的五条口径 + 下一步（R24）

| # | 口径 | 理由 |
|---|---|---|
| R23-a | **修订 R22-e**：可以往 `data/minecraft/tags/*` 写，但**只能追加**（`"replace": false`，values 只放自家 id）；`replace: true` 才是红线 | R22-e 的红线位置画错了。实测 `[冒险]simplyswords` 的 jar 内就有 `data/minecraft/tags/item/enchantable/{sharp_weapon,sword,weapon,fire_aspect,durability}.json`，`[农业]FarmersDelight` 也往 `data/minecraft/tags/enchantment/` 写 —— 1.21 的 tag 默认按值合并，「往别人命名空间写 tag」本身就是生态通行做法；真正会抹掉别人数据的是 `replace: true` |
| R23-b | 基底→tag 的映射**跟着 `ItemBase` 走，不跟内容走** | 内容栈的 item id 就是基底 id（`demo_longsword` 的 item 是 `redtale_project:sword`），所以内容加多少件都不用改 tag；反过来把 tag 写成「按内容 id 列」会让每次加武器都要重生成一份新的 tag |
| R23-c | tag 生成**幂等**：内容与磁盘一致就不写（mtime 不动） | 每次 reload 都重写 8 份文件会让整包反复重载，备份与 diff 全是噪点；判据是「文本相等」而不是「文件存在」 |
| R23-d | 缺失的自家 `exclusive_set` tag 补**空**文件 + 一条告警，不猜内容 | 不补就每局刷 `Not all defined tags … are present in data pack`；自动填「谁和谁互斥」是发明语义，必须人造 |
| R23-e | tag（资源）与附魔注册表（启动期 datapack registry）**生效层不同**：前者 `/reload` 即生效，后者必须重启 | 同一个数据包里两样东西时机不同。排障口诀：**「换件能不能附」看 tag（reload 级），「附魔在不在」看注册表（重启级）** |

下一步（R24）：

1. **验收 T-0018 / T-0019**（T-0018 已连挂两轮 `OPEN` 且零进度行；若下轮仍无动静，按 §2.5 换一张更小的卡）。
2. **`soul_reap` 的执行体**：需要 `heal` 原语 + `ScriptContext` 带 affected 实体（`ofServer` 拿不到实体）。加原语 = 换 jar，按 D17 记账。
3. **V11 硬指标演练**：不编译，只写一份新的 `enchantments/*.json5` → `/redtale reload` → 重启 → `/enchant` 附上。这是 M4 的出口条件原文。
4. **挂账第 23 轮（需一次带客户端的窗口）**：附魔 tooltip 中文名（T-0017 已 VERIFIED，可以验了）、`rev` 落后 → `item upgrade` → tooltip 立刻变、真人穿戴套装面板刷新、真人右键、真人 pvp、BetterCombat 双持 ×1.2。

### 13.27 R24 的五条口径 + 下一步（R25）

| # | 口径 | 理由 |
|---|---|---|
| R24-a | `heal` 的数值口径是**目标最大生命 × (ratio + per_level × (等级-1)) + flat**，**不是**「按打出伤害的比例」 | `EnchantmentEntityEffect#apply(level, enchLevel, item, affected, pos)` 的签名里**没有伤害值**，`post_attack` 也不给。想按伤害抽血必须让伤害管线把数值递进脚本上下文（结构调整，排 M5 与技能层一起做）。这一版先用最大生命比例：可预测、可验收，实测 `8.00 → 10.00`（20 × 0.10）精确 |
| R24-b | `ScriptContext` 里「施法者」与「受害者」分两处：受害者进 `target()`（`ofEntity` 的第 2 参），施法者进 `player()`（是玩家时）或 `vars.attacker`（生物时）；`affected` 另存一份进 `vars` 供文本占位 | R22-c 已确认 `apply` 的第 4 参是受害者，但「谁回血」需要施法者；`EnchantedItemInUse.owner()` 在 1.21.1 是 `LivingEntity`（`javap` 实测），拿到它才算把两个实体都握在手里 |
| R24-c | `heal` 的日志行是 **V9 的唯一判据**：`[script] heal · <名> <前> → <后>（+<delta>，等级 N，目标 caster\|target）` | 满血时 `+0.00` 是**正确输出**（`LivingEntity#heal` 到上限即停），不能当成没生效。判「目标对没对」看 `目标` 字样，判「算得对不对」看 delta |
| R24-d | V11 的实测边界：**只写 config 的 JSON5 + `/redtale reload` + 重启**即生效，`/enchant` 全程没编译；但**进发布包**仍要放进 jar 的 `resources/redtale/defaults/` 或随整合包下发 `config/` | 运行期新增的附魔**没有中文名**（`tools/gen_enchant_lang.py` 只扫仓库默认配置），tooltip 会显示裸键 `enchantment.redtale_project.<id>`。运营侧加附魔 = 加 JSON5 + 补 lang + 重启，三步都要写进投放手册 |
| R24-e | 新增 effect 原语 `heal` = **加注册表项 = 换 jar**（D17 记账） | `ScriptRegistries` 启动期冻结。本轮加它是因为 `soul_reap` 只有日志没有玩法（M4 的 V9 名不副实）；原语清单与 24 条总表见 `docs/SKILLS`（M5 起草时补齐），后续加原语要走同一份记账 |

**一条排查顺序（本轮踩过）**：验「附魔脚本有没有执行体」时，先看 `[soul_reap] 触发` 有没有（L2 通了），再看 `heal ·` 有没有（L3 的原语通了）。
只有前者 = 脚本跑了但原语没生效（查 args / 目标）；两者都没有 = L2 没进（查 `script` 的字符串 id，R22-a）。
另：测试服验「扣血后回血」时，`/effect give <目标> resistance 600 4` 是 **100% 免伤**（amplifier 4 = V 级），`/damage` 会打不动、日志一路 `+0.00`，别误判成 heal 坏了。

下一步（R25）：

1. **验收 T-0019 / T-0020**（`/redtale enchant list` 与附魔可获取性 tag；T-0019 的功能验 = 测试服 2 行，`soul_reap` 行尾不带「脚本不存在」）。
2. **M4 出口盘点**：V1 / V2 / V3 / V7 / V8 / V9 / V10 / V11 已绿（8/11）；**V4 / V5 / V6 全是 GUI 面**（附魔台 / 铁砧 / 砂轮），只能等一次带客户端的窗口；V4 另依赖 T-0020 的 tag。
3. **M5 起步先写 schema**：`docs/SKILLS.md` 的 `skills/*.json5` 段（触发 / 目标 / 原语序列 / 冷却 / 消耗 / 绑定），再派解析器给 S8 —— **不要先派代码**（S8 没有设计上下文）。
4. **挂账第 24 轮（需一次带客户端的窗口）**：附魔 tooltip 中文名（含新增附魔的 lang）、`rev` 落后 → `item upgrade` → tooltip 立刻变、真人穿戴套装面板刷新、真人右键、真人 pvp、BetterCombat 双持 ×1.2、附魔台/铁砧/砂轮三项（V4~V6）。


### 13.28 R25 的五条口径 + 下一步（R26）

| # | 口径 | 理由 |
|---|---|---|
| R25-a | **技能不带 `trigger` 字段**：`skills/*.json5` 只有 `conditions` + `effects`，触发由引擎入口决定（右键 / 命令 / 怪物 AI） | 附魔那条路是 `trigger → 脚本`，因为附魔本身就是「挂在事件上」；技能是「主动释放」，多一个 `trigger` 字段只会让两种语义混在一起（玩家会写 `trigger: post_attack` 然后奇怪为什么不生效）。复用点是 effect / condition 原语，不是 trigger |
| R25-b | 技能冷却按 **(玩家 UUID, 技能 id)** 记在 `SkillEngine` 自己的表里，**不借** `ScriptEngine.cooldownTicks` | 脚本冷却是「脚本 id + 玩家名」，按名字记账 → 改名即清冷却；技能是玩法资源，必须按 UUID。两套冷却分开也避免「一条技能改了 id 就绕过冷却」 |
| R25-c | `damage` 原语只做 `entity.hurt(src, 白值)`，**永不** `setAmount`；倍率一律由 `DamageLayer` 乘 | D12 三层模型的字面执行：原语是「一层」，属性池是「二层」。写绝对值会让 `physical_damage` / 条件乘区对技能失效，且同一技能在有无属性时数值不可对账 |
| R25-d | 技能伤害类型只留一个通用 `redtale_project:skill`，不按技能分 `damage_type` | `damage_type` 是启动期 datapack registry（同附魔，R21-c）：按技能分类型意味着每加一个技能都要重启一次，与 D17「内容更新不换 jar、不重启」冲突 |
| R25-e | 原语表**只登记 24 条**，加原语走 D17 记账（换 jar），表里状态列必须同步 | 24 条是 §7 定的预算（够拼 80% 技能）；不记账的后果是注册表悄悄膨胀，且没人知道哪条已实现。机器可判的断言 = `grep -c "^| [0-9]" docs/SKILLS.md` |

下一步（R26）：

1. **验收 T-0019 / T-0020 / T-0021**（T-0019/T-0020 若仍 `OPEN` 无人领 → 按 §2.5 精神**收回自做**：它们是 M4 出口的两块，不能让 S8 的静默拖住里程碑）。
2. **M5-A 引擎（S7）**：`SkillEngine`（冷却表 + `runCalls`）、`/redtale skill list|cast`、默认 `skills/*.json5` 两份 + `DEFAULT_FILES` 接线、K1~K6。
3. **`MultiplierRules` 加伤害类别轴**（Q-018 默认：分轴，物理 → `physical_damage`，法术 → `spell_power`），否则法术技能吃物理百分比。
4. **M4 收尾还差 V4**：T-0020 的 tag 落地后，附魔台能刷出自家附魔（GUI 面仍需客户端窗口）。
### 13.29 R26 的三条口径 + 下一步（R27）

| # | 口径 | 理由 |
|---|---|---|
| R26-a | **技能伤害只冻结两个 `damage_type`**：`redtale_project:skill_physical` / `skill_magical`。**绝不**按技能各注册一个类型 | Q-018 选 A（分轴）后最容易走歪的一步是「每个技能一个 `damage_type`」——`damage_type` 是启动期 datapack registry，按内容注册就要重启，直接撞 D17。两个通用类型 + 一张「类型 → 属性池」配置表，加技能只写 JSON5 |
| R26-b | 分轴的落点是 `MultiplierRules.attributesFor(id)`（first-match），**不是**新开一套乘区；条件乘区（pvp/pve/undead）**不跟着分轴**，两类共用 | 物理与法术的差别只在「吃哪条百分比属性」；把条件乘区也复制成两份会让「对亡灵 +30%」在两条轴上各写一遍，改数值必漏一边。一个池相加、一次 `Settle.settle`，仍然只有一条结算路径（D20 显示与结算共用 `settle()`） |
| R26-c | `percent_attributes` **保留**为「未命中类别」的兜底池，不是历史遗留；显式写 `category_attributes: []` 即关掉分轴 | 已有内容（`verification_strike` 等非技能类型）全靠它。删掉它等于逼所有非技能伤害都进类别表，配置噪音翻倍 |

下一步（R27）：

1. **验收 T-0020 / T-0021 / T-0022**（T-0020 自 11-16 21:15 派单起**两轮无人领**，若仍 `OPEN` → 按 §2.5 精神收回自做，它卡着 V4）。
2. **M5-A 引擎（S7）**：`SkillEngine`（`SkillCooldowns` + `ScriptEngine.runCalls` + `cooldown_reduction` 属性接入）、`/redtale skill list|cast`、默认 `skills/*.json5` 两份 + `DEFAULT_FILES` 接线、K1~K6。
3. **`CONTRACTS.md` 补 damage_type 契约**：两个类型 id 是冻结接口，S8 与内容侧都不得新增。
4. **M4 收尾 V4**：T-0020 落地后附魔台可刷出自家附魔（GUI 面仍等客户端窗口）。

### 13.30 R27 的四条口径 + 下一步（R28）

| # | 口径 | 理由 |
|---|---|---|
| R27-a | **`damage` 原语只做单体**，`radius` 从它的参数表移出（读到 `>0` 打一行 WARN 并忽略），范围伤害留给 `damage_aoe` | 两个原语共用一个参数，内容侧必然有人写 `damage` + `radius` 然后奇怪「为什么只打到一只」。语义分家比「一个参数两种行为」便宜：WARN 会立刻指出该换哪个原语 |
| R27-b | 伤害类型解析**两级回退**：类型不在注册表 → 回 `skill_physical` + WARN 一次；连缺省都查不到（数据包没加载）→ 退 `level.damageSources().generic()` + WARN，**本次不吃乘区** | D16 的精神：宁可「这一次少乘」，也不要为了乘一次去 NPE。少乘有日志可查，崩了只会让整个技能静默消失 |
| R27-c | 可获取性 tag 在**空集时也写三份空文件**（不清空就跳过） | 语义 = 「清场」。删光 `enchantments/*.json5` 若不清 tag，数据包会留着指向不存在 id 的条目 → 启动期 `Unknown entry` 报错，而那个错和「写错附魔」长得一模一样 |
| R27-d | 卡「静默两轮无人领」→ 标 `[DROPPED] (S8 静默 N 轮，S7 自做)` 后**由 S7 把该卡进度行补成完整交付记录**，且**不重派同内容卡** | 重派等于让 S8 去改 S7 刚写完的文件（独占文件冲突的另一种形态）。卡板是审计面，DROPPED 的卡也要能看出「谁做的、怎么验的」 |

下一步（R28）：

1. **验收 T-0021 / T-0022 / T-0023**（T-0021/T-0022 是 05:50 派的纯函数卡，S8 若交付按卡面 3 条跑，另写 S7 独立探针；T-0023 重点看 RCON 输出格式是否逐字对）。
2. **M5-A 引擎（S7）**：`SkillEngine`（`SkillCooldowns` + `ScriptEngine.runCalls` + `cooldown_reduction` 属性接入）、`/redtale skill list|cast`、默认 `skills/*.json5` 两份 + `DEFAULT_FILES` 接线、K1~K6。**前置 = T-0021 / T-0022 落地**（引擎要 import 那两个类）。
3. **V4 的最后一格**：tag 与附魔都已落盘，剩下「附魔台真能刷出」——需要客户端窗口，挂账（不阻塞 M5）。
4. **`soul_reap` 补 `damage` 原语版对照**：现 `soul_reap` 只回血，等 `SkillEngine` 能跑 `skills/*.json5` 后，用它验「同一技能在有无 `physical_damage` 时数值不同」。

### 13.31 R28 的五条口径 + 下一步（R29）

| # | 口径 | 理由 |
|---|---|---|
| R28-a | 技能分三层落地：`SkillSpec`（纯解析，S8）/ `SkillRegistry`（不可变快照 + 告警同源，S7）/ `SkillEngine`（冷却 + `runCalls`，S7，**等 T-0022 冷却表 VERIFIED 再写**） | 引擎要 import `SkillCooldowns`，而那个文件在 T-0022 的独占清单里。先写快照层，等卡合流再写引擎 —— 这是独占文件规则唯一能走通的顺序，不是拖延 |
| R28-b | 默认技能的 `name` **直接写中文可读名**（`疾风斩` / `灼焰爆`），不写 lang 键 | schema 的缺省值是 lang 键 `skill.redtale.<path>`，但仓库里**没有**生成 `skill.*` 的通道（`gen_item_lang.py`/`gen_enchant_lang.py` 各自只管自己的前缀）→ 写 lang 键只会让命令输出显示裸键。等 M5-B 上 GUI 再补 `skill.*` 生成器，那时才值得为此加一个脚本 |
| R28-c | `SkillRegistry` 与 `SkillSpec` **分开**，且 `warnings` 在 `load` 时**一起快照**（`List.copyOf`） | 换配置时告警必须跟着换代：否则上一份配置的「id 缺失」会一直挂在 `configWarnings()` 里，让人以为新配置还有问题 |
| R28-d | 解析层**不校验原语是否存在**，`SkillRegistry.primitiveTypes()` 只提供「引用了哪些 type」，校验留给 `/redtale validate` 与执行期 WARN | 注册表是启动期冻结的（D17 基石 2），解析器必须保持纯函数才能离线探针。反过来说：`primitiveTypes()` 已经把「该校验什么」算好了，validate 接进去只是几行 |
| R28-e | 技能计数进 **reload 回显 + 日志**（`… + N 条技能（M 条 effect，原语 K 种）`），不新开命令 | K1 的判据是「只写 JSON5 就能被看见」，而 `/redtale skill list` 还卡在 `RedtaleCommand` 的独占里（T-0023）。计数先落在既有回显上，观测面不用等 |

下一步（R29）：

1. **验收 T-0022 / T-0023 / T-0024**（T-0022 冷却表用 S7 独立探针复跑卡面 16 条断言，重点看 `r > 0.9` 夹取与 `< 1` 地板；T-0023 看输出格式逐字；T-0024 由 S7 在测试服跑 `content list`）。
2. **M5-A 引擎（T-0022 一落就写）**：`core/skill/SkillEngine`（`SkillCooldowns` + `conditions` 全 true 才继续 + `ScriptEngine.runCalls` 跑 effects + 冷却文案 `技能 <id> 冷却中：<剩余> tick`）、`/redtale skill cast <id>`（`RedtaleCommand` 追加行须等 T-0023 释放）、K2/K3/K4/K5。
3. **`primitiveTypes()` 接进 `/redtale validate`**：未知原语 type 报一条（现在只在执行期 WARN）。
4. **V4 最后一格**（附魔台真刷出）仍需客户端窗口，继续挂账。

### 13.32 R29 的五条口径 + 下一步（R30）

| # | 口径 | 理由 |
|---|---|---|
| R29-a | 引擎只做「放一次」：**条件不过不记冷却**、冷却不过不跑 effects | 「条件不满足也吃冷却」是最常见的实现顺序错误（先 tryStart 再判条件），玩家看到的是「按了没反应还得等 6 秒」，且日志里没有任何痕迹 |
| R29-b | `SkillEngine` 由 `RedtaleCore` 持有，**跨 reload 存活**，`/redtale reload` 不清冷却 | reload 清冷却 = 一个免费刷技能的漏洞（改一个无关配置就能重置全部 CD）。代价是「改了 `cooldown_ticks` 之后旧记录仍是旧值」，到期自然淘汰，可接受 |
| R29-c | 技能目标 = **视线 raycast**（`AIM_RANGE = 8` 格、只认活体、排除自己），打不中即 null，由 `damage` 原语自己跳过 + WARN | 引擎替原语找目标会让「为什么打到了别的怪」无法解释；原语已经有「没有可用目标」的 WARN（R27），分工清楚 |
| R29-d | `ScriptEngine.runCalls` 新增 `(calls, ctx, owner)` 重载，旧的两参版委托并传 `"物品脚本"` | 技能复用 `runCalls` 是对的（单条失败不影响后续），但日志里写「物品脚本的 effect」会让排障走错方向。零行为变更，只改文案 |
| R29-e | `SkillCommand.probe` 会 `cooldowns().clear(uuid)`，是**验收工具**，不进玩法路径 | 探针要 A/B 两组数值对照就必须连放两次；真人 `cast` 永远走正常冷却。M5-B 的右键释放不走 probe |

下一步（R30）：

1. **验收 T-0024 / T-0025**（T-0024 由 S7 在测试服跑 `content list` 看七个字段与 `孔位 2` / `套装 emberforged` / `rev 1`；T-0025 看 build + 两条 grep + 坏技能多 2 条问题）。
2. **M5-B（跨 3 文件，S7）**：`ItemContent` 15→16 加 `abilities`、`ItemFactory.build` 写进 `ContentData.abilities`、`ContentItem#use` 在**没有 `use` 段**时施放绑定技能（K7）；`cooldown_reduction` 属性在这里一并接进 `SkillEngine.cast`（现在写死 0.0）。
3. **M5-C 原语**：`damage_aoe` / `dash` / `buff` / `debuff` / `fx`（`SKILLS.md` §4 状态列 `—`→`✅`，每加一条改那行计数）。
4. V4 的「附魔台真刷出」仍需客户端窗口，继续挂账。


### 13.33 R30 的五条口径 + 下一步（R31）

| # | 口径 | 理由 |
|---|---|---|
| R30-a | `abilities` 是**定义型字段**：`ItemFactory.build` 随 rev 写入，`ItemUpgrader.ensure` 重建时取**新定义**（不照抄旧值），改它要 `rev`+1 | 与 `set_id` 同口径。若照抄旧值，那么「给存量武器补一个技能」永远不会生效，且没有任何报错 —— 静默不更新比报错难查。探针用例因此把 `demo_longsword` 2→3 |
| R30-b | **只放第一条**（`abilities.get(0)`），多技能留给 M5-C 键位 | 一键全放 = 「按一下掏空家底」，且冷却会一次性全记上。排后面的技能不告警：配置写了不生效是内容作者的责任，刷屏无助于定位 |
| R30-c | 右键分支优先级写死 `use → repair → abilities.get(0) → 无动作`，不自动二选一 | 同一件东西既有 `use` 又有 `abilities` 时，两种语义都「说得通」——自动挑一种会让作者猜不到。固定顺序 + 文档写死，比智能更可预测 |
| R30-d | 冷却减免**只读属性面板**（`AttributeMap`），异常值（负数 / NaN / Inf）归零；换算与钳制只在 `SkillCooldowns.effectiveTicks` 一处 | 装备 / 药水 / 套装各自乘一遍会变成「三份真相」（D18 同思路）。`SkillCooldowns` 早就有 `MAX_REDUCTION = 0.9` 与「地板 1 tick」，别再在引擎里写第二份公式 |
| R30-e | `cooldown_reduction` 的验证**只能显式挂瞬时 modifier**：FakePlayer 不 tick，手持装备的 `ATTRIBUTE_MODIFIERS` 刷不进 `AttributeMap`（R5 事实） | 想验「减免生效」就得绕过装备链路；D 组因此直接给 FakePlayer 挂 `+0.5`。只验 A/B/C 三组会得出「属性没接」的错结论 |

下一步（R31）：

1. **验收 T-0025 / T-0026**（T-0025 看 build + 两条 grep + 坏技能多 2 条问题；T-0026 看 build + 3 条 grep，功能由 S7 写 `skills/t_buff.json5` 放一次技能）。
2. **M5-C 原语放量**：`damage_aoe` / `debuff`（`buff` 由 T-0026 交付）—— 每加一条改 `SKILLS.md` §4 状态列 `—`→`✅` 与该行计数（`grep -c "^| [0-9]"` 恒 24）。
3. **tooltip / `content list` 补 `abilities` 列**（现在 `content list` 只有 7 字段，技能载体在清单里看不出来）。
4. V4 的「附魔台真刷出」+ tooltip 技能行仍需真人客户端，继续挂账。

### 13.34 R31 的五条口径 + 下一步（R32）

| # | 口径 | 理由 |
|---|---|---|
| R31-a | `/redtale skill info <id>` 判「原语是否存在」**只读 `core.registries()`**，不另写白名单、不读 `SKILLS.md` | 与 `SkillEngine` 执行期判断同源。写第二份清单 = 「info 说 ✅ 但放出去 WARN」这种最难查的分裂，且清单早晚漂 |
| R31-b | 注册状态分**两处**统计（conditions / effects 各一遍），但**只有 effects 与 conditions 的缺失合计**进尾部结论；返回值 = `缺失 == 0 ? 1 : 0` | 命令返回值要被验收脚本用（RCON 看不到 return，但控制台/`execute store` 能看到）；把「有没有问题」放进返回值，比让人读中文更可靠 |
| R31-c | `args` 摘要只做**显示**（空参数不打、超 80 字符截断加 `…`），绝不动数据 | `SkillCall.args()` 是 `JsonObject`，原样透传是解析层的契约（R28-d）；摘要一旦参与判断就会变成「第二个解析器」 |
| R31-d | 「被内容绑定」= 遍历 `contentItems().all()` 找 `abilities().contains(skillId)`，**不建反向索引** | 内容件是个位数到百位数，一遍遍历够快；索引要维护失效（reload / 热加内容），漏刷就是「info 说没人用，其实是索引旧」 |
| R31-e | M5-C 原语卡**不能并发派**：`Builtins.registerAll` 是单点，两张卡同时改必然冲突 → 一张 `buff` 未 VERIFIED 前，S7 只做观测面，不碰注册表 | 防冲突机制的意义就在这儿。本轮 S7 的三件事（验收 / skill info / content list 卡）**全都不碰 `Builtins.java`**，与 T-0026 完全正交 |

下一步（R32）：

1. **验收 T-0026 / T-0027**（T-0026 功能由 S7 写 `skills/t_buff.json5` 放一次看效果与时长；T-0027 看 `content list` 每行末尾 `· 技能` 与汇总 `带技能 K 件`）。
2. **M5-C 原语放量**：`buff` VERIFIED 后立刻做 `damage_aoe` / `debuff`（README 口径：加一条原语 = 换 jar，D17 记账；每加一条改 `SKILLS.md` §4 状态列 `—`→`✅`，`grep -c "^| [0-9]"` 恒 24）。
3. V4「附魔台真刷出」+ tooltip 技能行仍需真人客户端，继续挂账（第 5 / 15 / 30 轮同项）。

### 13.35 R32 的五条口径 + 下一步（R33）

| # | 口径 | 理由 |
|---|---|---|
| R32-a | `damage_aoe` 的**圈心写死两级**：有 `ctx.target()` → 受害者脚下；没有 → 施法者脚下。不做「攻击点 / 命中点」第三选项 | SKILLS §4 备注要求「AOI 中心必须显式」。两级刚好覆盖两种真实用法（命中型技能 / 自爆光环），第三选项没人用，却会让内容作者每次都要查文档 |
| R32-b | `debuff` 的**缺省目标是受害者**（与 `buff` 缺省施法者相反），且只收 `MobEffectCategory.HARMFUL` | 减益的默认语义就是打在挨打的人身上；正面效果写进 `debuff` 必须报 WARN —— 否则「debuff 能加血」会静默通过，以后查数值没人会想到这里 |
| R32-c | **瞬时效果不结算伤害**：`minecraft:instant_damage` / `instant_health` 走 `addEffect` 一点血都不掉（原版 `/effect give … instant_damage` 同样不掉） | 1.21.1 的瞬时效果只在「投掷药水 / 区域云 / `applyInstantenousEffect` 显式调用」那条路上结算。`buff` 因此只适合时长型效果；直伤一律用 `damage` / `damage_aoe`。这条已回写 `SKILLS.md` §4 第 15 行 |
| R32-d | 伤害原语之间**共用一份「伤害类型回退」**：`DamageEffect.source/holder/caster/num` 改包内可见，`DamageAoeEffect` 直接调 | 两份回退 = 以后改第三条原语必漏一份，现象是「同一技能换个原语就不吃乘区」—— 这类 bug 只能靠「只有一个实现」预防 |
| R32-e | 验收「效果真的挂上去了」只能用**真实体**：`skill probe` 的木桩牛会被 `discard()`，所以 `buff`/`debuff` 走「附魔 `post_attack` → 脚本 → 打 caster」并在 `data get … active_effects` 上对账 | 只验「日志打出来了」等于验日志；`FakePlayer` 的效果查询不到（它不在世界实体表里）。时长对账只能比「初始 − 已过 tick」（`duration` 每 tick 掉） |

下一步（R33）：

1. **验收 T-0027 / T-0028**（T-0027 看 `content list` 每行 `· 技能` + 汇总 `带技能 K 件`；T-0028 看脚本 exit 0 与「故意删一条 `DEFAULT_FILES` 项 → exit 1」）。
2. **M5-C 继续放量**：控场四条（`knockback` / `pull` / `stun` / `slow`）—— 仍是「一卡一原语 + `Builtins` 1 行」，但 `Builtins` 单点限流，一次只能派一张。
3. **M5 收口还差**：法力池（`mana`，SKILLS §3 第二段）、技能树（D25，M6 之后）、`content list` 之外的 tooltip 技能行已做。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标（第 5 / 15 / 30 轮同项）。


### 13.36 R33 的四条口径 + 下一步（R34）

| # | 口径 | 理由 |
|---|---|---|
| R33-a | 位移原语（`knockback` / `pull`）**只用原版 `LivingEntity#knockback(strength, x, z)`**，绝不自己 `setDeltaMovement` | 它内部按 `Attributes.KNOCKBACK_RESISTANCE` 打折（实测抗性 1.0 → `Δ0.00` 一位不动），并自己置 `hasImpulse`。自己拼速度 = 绕过抗性，现象是「重甲玩家被推飞」，而且没有任何日志能看出是谁干的。我们只额外补 `hurtMarked = true`（与 `Explosion` 同做法），让 `ServerPlayer` 把速度走运动包下发 |
| R33-b | 方向语义：`knockback` 传 `-normalize(目标 − 施法者)`、`pull` 传 `+normalize(...)`；两者水平重合时**退化为 +X 并记一条 WARN**，不随机、不朝视线 | `LivingEntity#knockback` 内部算的是 `-normalize(x, z)`（`javap -c` 实读，不是猜的），所以「推离」要传反方向 —— 传错的表现是「击退把人吸过来」，而这在日志里看不见。零向量归一化会得到 NaN 速度（实体瞬间消失），所以退化分支必须有 |
| R33-c | **`strength: 0` 必须真的不位移**：两条位移原语用自己写的 `raw()` 读参（非正数原样返回），不用 `DamageEffect.num` | `DamageEffect.num` 对非正数返回**缺省值**（那是给 `radius`/`falloff` 这类正数量设计的，R32-d 的共用口径）。照抄它的后果是「配置写 0 反而按 0.4 推」——实测确认过（改 0 后仍打 `强度 0.40`）才改成 `raw()`。**共用辅助方法要按语义挑，不能按「就近」挑** |
| R33-d | 位移验收在**旁观者的 `Motion`** 上对账，不在受害者的 `Pos` 上 | 受害者同时吃「原版平砍击退 + 我们的原语 + 与攻击者的实体碰撞推挤」三份力，`Pos` 的位移方向读不出是谁给的。旁观者（`radius > 0` 圈进来、不被攻击、`NoAI` 不动）只吃我们一份力：同位置同强度下 `knockback` = `Motion.x -0.798`、`pull` = `+0.797`，符号即结论。另外 `NoAI` 实体不跑 `travel` 所以 `Motion` 不衰减，读数稳定；反过来它 `Pos` 永远不动，别拿 `Pos` 验 |

下一步（R34）：

1. **验收 T-0028 / T-0029**（T-0028 看 `python tools/check_defaults.py` 的 exit 0 与「故意删一条 → exit 1」；T-0029 看 `ManaPool` 的探针断言数）。
2. **M5-C 剩余控场两条**：`stun`（停 AI + 禁移动，**不**用 `slowness 255`，会被抗性减免）/ `slow`（原版 `slowness`，走 `MobEffect`）。`slow` 与 `debuff` 只差缺省参数，考虑直接由 `debuff` 派生以少一条实现。
3. **M5 收口**：`ManaPool` 合流后接 `SkillEngine`（`mana_cost` + `max_mana` / `mana_regeneration` / `mana_cost_reduction` 三条属性）与 `PlayerData` 持久化。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标（第 5 / 15 / 30 轮同项）。

### 13.37 R34 的四条口径 + 下一步（R35）

| # | 口径 | 理由 |
|---|---|---|
| R34-a | `stun` 只对 `Mob` 用 `setNoAi(true)`；**非 `Mob`（玩家）退路 = `slowness` 7 级**，日志明确标「退路」 | 1.21.1 没有「禁止玩家移动」的合法接口。`slowness` 是速度乘数：装备/药水/第三方 modifier 一抵就变成「慢慢挪」，而且怪照样能打人 —— 拿它当定住手段是**语义错**，不是参数没调好 |
| R34-b | 续定时**沿用首次记录的 `wasNoAi`**，只把截止时刻往后推；解除按该值恢复 | 连击会反复重入 `freeze`，每次重读 `isNoAi()` 读到的都是「已被我们置 true」→ 解除时把怪永久定住。实测（铁傀儡解除后仍 `NoAI=1b`）才暴露 |
| R34-c | 在册标记用 **scoreboard tag `redtale_stunned`**，不用持久化 NBT | 1.21.1 已删除 `Entity#getPersistentData()`（编译期实证）；tag 随 NBT 保存、`/data get entity … Tags` 可读，是**唯一**能区分「本来没 AI」与「被我们定住」的凭据 |
| R34-d | 恢复用「截止时刻轮询」（`ServerTickEvent.Post`，空闲 `isEmpty` 直接返回），不用 `TickTask` 延时任务 | 延时任务在关服 / `/reload` 时丢，丢了就是永久定住；轮询在册表通常 0~5 条，代价可忽略。重启残留另由 `EntityJoinLevelEvent` 兜底，恢复值取 `false`（「能动」比「永久定住」安全） |

下一步（R35）：

1. **验收 T-0029 / T-0030**（T-0029 看 `ManaPool` 探针 ≥24 断言与 `grep -c net.minecraft` = 0；T-0030 看 `mobs/MobSpec` ≤200 行、`net.minecraft` 零 import、探针 ≥30 断言）。
2. **M5 收口**：`ManaPool` 合流 → `skills/*.json5` 加 `mana_cost` + `SkillEngine` 施法扣蓝 + 三条属性（`max_mana` / `mana_regeneration` / `mana_cost_reduction`）+ `PlayerData` 持久化。
3. **M5-C 剩余**：`slow` **不单独做原语**（`debuff` 写 `minecraft:slowness` 即等价，R34 之后文档同步），余下按 `SKILLS.md` §4 优先级推 (`dash` / `projectile`)。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标、玩家被 `stun`（第 5 / 15 / 30 / 34 轮同项）。

### 13.38 R35 的五条口径 + 下一步（R36）

| # | 口径 | 理由 |
|---|---|---|
| R35-a | `max_mana` 是**绝对值**，且 `0` 的含义是「**没配**」→ 回落到 `ManaPool.DEFAULT_MAX`（100）。配了正数就完全听属性的（不设软上限，D16） | 自建属性基值全 0（R5 事实），0 若按「上限为零」解释，一个没穿装备的法师永远放不出技能 —— 那种状态没有玩法意义。**踩过的坑**：探针 F 组我按「加成」写了期望（`+50` → 150），实测 50；改正后写死为「绝对值口径，内容侧写 500 就是 500」。代价是「小加成戒指」会**降**上限（内容写 +20 得 20），已在 `SKILLS.md` §6 标明「只在整套装备里写一次」。备选口径见 Q-019 |
| R35-b | `mana_regeneration` **不给缺省回蓝**：`<=0` 就是「不回蓝」 | 凭空给「每秒 5 点」会让「没配」与「配了 5 点」在面板上完全一样，而且是**第二份真相**（D18 同思路：数值只有一个来源）。代价是新服默认不回蓝 —— 由内容（装备/药水/套装 modifier）负责，这也正是 `arc_bolt` 示范件要配的内容 |
| R35-c | 法力门槛排在 **记冷却之前**：条件 → 冷却查询（只查不记）→ 扣蓝 → 记冷却 → effects | `SkillCooldowns.tryStart` 是「查 + 记」一体，直接用会让「蓝不够」那次也吃冷却，现象是「空蓝按两下，回蓝后还要等 10 秒」。拆成 `remaining()` + `start()` 两步，代价是多一行，收益是 C 组能断死「冷却就绪 = true」 |
| R35-d | `ManaPool` 实例挂在 **`SkillEngine`** 上（不是 `RedtaleCore` 新字段），因此随 reload 存活；`tickMana` 用 `ticks = 1` 每 tick 交回池里累积 | 引擎已经是「跨 reload 存活的运行期状态」的家（冷却表就在这儿）。`ticks = 1` 而不是每 20 tick 一次 `ticks = 20`：小数余额留在 `current` 里，「每秒 0.5 蓝」才不会因取整永远回 0（T-0029 行为 5 的同一条纪律） |
| R35-e | 持久化（`PlayerData`）**不在本轮**：现在重登 = 满蓝。这是有意的半步，不是遗漏 | 持久化要定「什么时候写盘 / 崩溃丢多少 / 多世界怎么算」三件事，那是一个独立卡的量；而「扣蓝 → 不够 → 回蓝」这条链路本身已经能独立验穿（六组探针不依赖持久化）。先把链路打通，再决定落盘格式，避免格式定错后连带改结算 |

下一步（R36）：

1. **验收 T-0030 / T-0031**（T-0030 看 `mobs/MobSpec` ≤200 行 + `net.minecraft` 零 import + 探针 ≥30 条；T-0031 看 `motion` 五个必过例 + 夹取/退化，`Builtins` 只 +2 行）。
2. **M5 收口第二步**：`PlayerData`（当前法力落盘 + 登录还原 + 退出清账）——`ManaPool.restore/clear` 两个口子已经就位，只差「写哪儿、什么时候写」。
3. **M6 起步**：`MobSpec` 合流 → `MobRegistry` 快照 → 8 个模板 EntityType 注册（注册表结构归 S7，不派）。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标、玩家被 `stun`、真人 `/redtale skill mana` 面板（第 5 / 15 / 30 / 34 / 35 轮同项）。

### 13.39 R36 的三条口径 + 下一步（R37）

| # | 口径 | 理由 |
|---|---|---|
| R36-a | 怪物层与技能层**同构三层**：`MobSpec`（纯解析）/ `MobRegistry`（不可变快照 + 告警同源）/ 后续 `MobSpawner`（执行）。快照层先落地，**命令卡才许派** | 每层职责唯一：解析层不查注册表（离线可测）、快照层不查内容、命令层只读快照。R34 派 `MobSpec` 时没快照层，若当时派 `mob check`，那张卡只能自己再解析一遍配置 —— 那就是**第二份真相**，改 schema 时两处漂 |
| R36-b | `MobRegistry.describe()` 是「解析到底吃到内容没有」的**唯一廉价证据**，必须进 `reload` 日志与回显；`0 只怪物` 的两种成因（目录空 / 全被跳过）靠 `warnings` 区分 | 本轮 `2 只怪物（3 条技能引用，原型 2 种）` 一次就把「两份默认件都进了、技能引用条数对、base 只用了 2 种」三件事同时证实。只报 `size()` 的话，「3 条技能引用」这类半失效（技能段被丢）看不出来 |
| R36-c | 默认 `mobs/*.json5` 的每条属性键**必须命中 80 条表**，否则 `AffixPools.parseStats` 静默丢弃那一条（只留一条告警）。验法是「零告警」反证，不是看属性面板 | 属性表是启动期注册表（D12/D17），写 `spell_power`、`attack_speed`（非 `generic.` 全名）这类上游名一律丢。本轮 `ash_caster` 初稿写了 `spell_power`，改成 `magical_damage` + `fire_damage` 后零告警 |

下一步（R37）：

1. **验收 T-0031 / T-0032**（T-0031 看 `motion` 五个必过例 + `Builtins` 只 +2 行 + `grep -c setDeltaMovement`=1；T-0032 看 140 行内 + `BuiltInRegistries.ITEM` 出现 1 次 + 测试服三分支文案）。
2. **M5 收口第二步**：`PlayerData`（法力落盘 + 登录还原 + 退出清账）——`ManaPool.restore/clear` 已就位，缺「写哪儿 / 何时写 / 崩了丢多少」三条决定。
3. **M6 第三步**：8 个模板 `EntityType` 注册（注册表结构归 S7，不派）+ `mobs/*.json5` 的 `minecraft:generic.scale` 落到实体 + 装备六槽装配。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标、玩家被 `stun`、真人 `/redtale skill mana` 面板、真人刷怪（第 5 / 15 / 30 / 34 / 35 / 36 轮同项）。

### 13.40 R37 的三条口径 + 下一步（R38）

| # | 口径 | 理由 |
|---|---|---|
| R37-a | `dash` v1 的参数字面是 **`power` / `up` / `direction`**（一次性 `setDeltaMovement`），**不是** `SKILLS.md` §4 原写的 `distance` / `duration_ticks`（分帧）。文档本轮已按实现改正，分帧版留作 M5-C 后续 | 分帧要一张「跨 tick 的位移事务表」，那是新的运行期状态（还要处理下线 / 死亡 / 换维度）；一次性写速度在**怪物**身上完全够用（AI 自己会接着走），只在**玩家**身上会被客户端校正拉回。先落地能验的，再决定要不要为玩家加事务表 —— 与 R35-e「先通链路再定落盘」同一条纪律。**踩点**：卡面写 `distance 4` 会让 S8 去实现一个没有时长概念的距离衰减，那是另一个原语 |
| R37-b | 8 个模板 `EntityType` 的 id **就是** `MobSpec.BASES` 的八个字符串（`redtale_project:melee` … `:ambient`），`base` 字段因此可以直接当实体 id 用 | 两处各写一套白名单，早晚漂一次（`base: "elite"` 配 `redtale_project:elite_mob` 这种）。现在 `MobSpec.base` 校验用 `BASES`、刷怪用 `RedtaleEntities.byBase(base)`，**同一个字符串**，多一层映射就多一个错法 |
| R37-c | 8 个原型**共用同一个类 + 同一份出厂属性表**；差异化一律走「生成时套配置」（属性写 `AttributeMap`、装备 `setItemSlot`、体积 `generic.scale`） | 注册项冻结但类不冻结，所以先占 id 再拆子类不丢兼容。共用属性表的收益是「改 elite 的出厂血量不会顺手改掉 caster」—— 每原型一份 supplier 的写法一旦有人复制粘贴，漂移是静默的（没有断言能发现） |

下一步（R38）：

1. **验收 T-0032 / T-0033**（T-0032 看 140 行内 + `BuiltInRegistries.ITEM` 1 次 + 测试服三分支文案；T-0033 看 `velocity` 八个必过例 + `Builtins` 只 +2 行 + `addFreshEntity` 1 次）。
2. **M6 第三步第 2 小步**：`/redtale mob spawn <id>` —— 按 `MobSpec` 生成（`RedtaleEntities.byBase` + 属性写 `AttributeMap` + 六槽 `setItemSlot` + `generic.scale` + scoreboard tag 记内容 id）。这是「配置出来的怪」第一次变成真实体。
3. **实体 lang**：`tools/gen_entity_lang.py`（8 个 `entity.redtale_project.*` 键），并可顺手把 `#minecraft:undead` 实体标签生成接进 `reload()`。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标、玩家被 `stun`、真人 `/redtale skill mana` 面板、真人刷怪、**玩家客户端侧 `dash`（R37 新）**。

### 13.41 R38 的四条口径 + 下一步（R39）

| # | 口径 | 理由 |
|---|---|---|
| R38-a | 怪物属性 = **出厂基值 + `ADD_VALUE` 临时 modifier**（id 固定 `mob/<怪id>/<属性path>`），**不** `setBaseValue`。因此 `max_health: {base:60, per_item_level:4}` 在等级 12 得 **128 血**（出厂 20 + 108），不是 108 | 基值是「出厂值」，改了就看不出谁给的（D18 可拆解性的同一条纪律）。固定 id 让「同一只怪重生成」是覆盖而不是叠加。代价是加法口径：运营要绝对血量得自己减掉出厂 20 —— 与 R35-a（`max_mana` 绝对值）口径**不同**，两处都已在文档写死，别互相套用 |
| R38-b | 体积是**唯一走基值**的字段（`minecraft:generic.scale`），`1.0` 不写 | 体积是「形态」不是内容数值：它不进伤害结算、不参与三乘区，写成 modifier 只会让 `/redtale attr scale` 多一条无意义的 `+0.15`。`MobSpec` 解析期已夹 `[0.25,4.0]`，spawner 不再夹 |
| R38-c | spawner 的 `skips` 实际只有**两类可达**：装备槽写错 id、实体没有该属性。「未知属性键」在**解析层**就被 `AffixPools` 丢掉（R36-c），命令看不到 | 夹具 `t_spawn_bad` 写 `spell_power` → reload 1 条告警、`attributes` 只剩 1 条、spawner 报「属性 1 条」。所以「属性没生效」要查 reload 告警，**不是**查 spawn 输出 |
| R38-d | 验生成**必须先 `forceload`**：未加载区块里 `addFreshEntity` 仍返回 true，但实体落不到方块上（首测两只掉到 y=54，`@e` 也找不到 → 看着像「生成失败」） | 与 R34「`/summon` 进实心方块 = `suffocated in a wall`」同源：服务端把实体放进一个它还没算好的地形里。可复现脚本：`forceload add` → `fill` 平台 → `spawn <id> x y z` → `data get` → `kill` → `forceload remove` |

下一步（R39）：

1. **验收 T-0033 / T-0034**（T-0033 看 `velocity` 八个必过例 + `addFreshEntity` 1 次 + `setAmount|teleport|knockback(` 0 次 + 测试服 `[script] projectile · … · 速度 3.00`；T-0034 看 `8 66 14` 键数与二次 md5 相同）。
2. **M6 第三步第 3 小步**：怪物技能释放（`MobSkillCaster`：按 `MobSpec.skills` 的 `cooldown_ticks` / `chance` 掷骰 → `SkillEngine` 以怪物为施法者放 → 需要真人在线才跑 AI，见 R37-b）。
3. **`#minecraft:undead` 实体标签生成**（8 原型按配置追加，`replace:false`，同 R23 手法）+ `tools/gen_entity_lang.py` 产出接进 jar 资源。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标、玩家被 `stun`、真人 `/redtale skill mana` 面板、`mob spawn` 的客户端体积/名牌。

### 13.42 R39 的五条口径 + 下一步（R40）

| # | 口径 | 理由 |
|---|---|---|
| R39-a | 「亡灵」的**唯一判据**是实体标签 `#minecraft:undead`，而 tag 只能按 **EntityType** 打 → 内容侧 `undead: true` 的粒度上限是**原型**（同一 `base` 下任一只怪声明，整个原型都算亡灵） | R37-b 定下「8 个原型的 id 就是 `MobSpec.BASES`」，实体身上没有「我是哪只怪」的注册表身份（内容 id 只活在 scoreboard tag / `ContentData` 里）。要按怪区分只能等真的拆子类（注册项冻结、类不冻结），在那之前写死在文档里，免得以后有人当 bug 修 |
| R39-b | `MobSpec.undead` 坏值（非布尔）**降级成 false + 1 条 WARN**，不整条跳过 | 漏标亡灵只让这只怪少吃 `undead_damage`（少了加成）；整条跳过等于「这只怪不生成」（少了怪）。两害相权，选轻的那个并留告警 |
| R39-c | `/redtale reload` 在「本次真的写了文件」时**自己调 `reloadResources`**（`ALREADY_SELECTED_AND_RELOADED`）；开服起步那次不做 | 包早就选中 → 老逻辑直接返回，运行期重写的 tag 永远只在磁盘上（实测：文件里有 id、选择器 count 0，必须手动 `/reload`）。这条同时把 D14「全内容可配 + 热重载」从「配置热」补成「资源也热」；开服不做是为了不白多加载一遍 |
| R39-d | 所有数据包写盘点必须**幂等**（`TagJson.writeIfChanged`）：内容逐字相同就不动文件、也不计入 `written` | 只要有一个生成器无条件重写，「本次写出 N 个文件」就恒 ≥1 → 每次 reload 都触发整包重载（本轮实测 3 个文件恒变，白重载 + 日志失真）。幂等同时保住 mtime，复盘时「变了的文件」才是真信号 |
| R39-e | 验「写出去的东西进内存了没」**只能看选择器/命令输出**，不能看 `cat` 文件；反过来验「文件是否被重写」只能看 mtime/md5 | 本轮先看文件内容（已含 `caster`）就以为生效，实际内存里还是旧 tag。磁盘与内存是两层，证据要分别取 |

下一步（R40）：

1. **验收 T-0034 / T-0035**（T-0034 看 `8 66 14` 键数 + 二次 md5 相同；T-0035 看 ≤190 行 + `net.minecraft` 只 1 处 + 探针 ≥24 条）。
2. **M6 第三步第 3 小步**：怪物技能释放（`MobSkillCaster`：按 `MobSpec.skills` 的 `cooldown_ticks` / `chance` 掷骰 → `SkillEngine` 以怪物为施法者放）。**前置**：需要真人在线才跑 AI（R37-b），验收脚本要写成「有玩家时观察日志」+「无玩家时用 `skill probe` 走同一条引擎路径」两段。
3. **M6 第四层接线**：`DropSpec` 落地后接进 `MobSpec`（`drops:` 引用）+ 死亡掉落（`LivingDropsEvent` 或 `LivingDeathEvent`），并进 `mob check` / `validate` 的引用校验。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标、玩家被 `stun`、真人 `/redtale skill mana` 面板、`mob spawn` 的客户端体积/名牌、**玩家客户端侧 `dash`**、**自建怪的 `pve+undead` 双键实测堆叠（R39 新）**。

### 13.43 R40 的四条口径 + 下一步（R41）

| # | 口径 | 理由 |
|---|---|---|
| R40-a | 怪物技能与玩家技能**同一条执行链**（`SkillEngine.castMob`），差异只有两处：**不算法力**、**冷却时长可被 `MobSpec.SkillRef.cooldownTicks` 覆盖**（`<= 0` 回落技能定义值） | 法力读的是玩家面板 `max_mana` / `mana_regeneration`，自建怪身上这两条基值都是 0（R35-a「0 = 没配 → 100」只对玩家成立）→ 套上去恒「蓝不够」等于给怪物上锁。冷却覆盖是玩法需要：同一个 `gale_slash` 玩家 120 tick、精英怪 100 tick 是合法内容。**不新建触发器体系**（SKILLS §2），所以改原语时玩家与怪物同时生效，不会出现第二份真相 |
| R40-b | `MobSkillCaster` **零成员状态**：冷却记在 `SkillCooldowns`（键 `(UUID, 技能 id)`）、随机数用 `mob.getRandom()`、节拍用 `server.getTickCount() % 10` | 有状态就要管「reload 清不清 / 下线要不要抖 / 死亡残留」三件事，而这三件全都已有答案（冷却表跨 reload、UUID 天然隔离、实体没了就查不到）。节拍取 10 tick：每 tick 遍历全服在 271 模组整合包上是纯浪费，而怪物 AI 的决策粒度本来就在秒级；副作用是「掷骰失败」不会每 tick 重试 |
| R40-c | 验收命令**必须能复用同一只施法者**：`mob cast` 先找 16 格内同 tag 的同类怪，没有才新生成，输出标 `复用`/`新生` | 本轮踩到的最贵一课：第一版每次现生成 → 新 UUID → 冷却表里干净 → 「立刻再放应被拦」这条**必然假通过**（实测连放两次都 CAST，靶牛 10→4→0）。冷却键是 `(UUID, 技能 id)`（R25-b），所以「冷却是真的」只能在同一只怪身上验 |
| R40-d | 失败必须回**状态 + 剩余 tick**，不许回 null：三模式分别给 `COOLDOWN 112t` / `(chance 0)` / `(未掷中)` / `没配 skills` | `Result.detail` 原本对 EXPLICIT 路径传 `failedCondition()`（冷却时是 null）→ 输出 `未施放（null）`，与「技能不存在」无法区分。掷骰路径更糟：`tryCast` 把「掷不中」与「掷中了但冷却挡」压成同一句「没有技能通过掷骰或门槛」→ 调 `chance` 时完全看不出是谁在挡 |

下一步（R41）：

1. **验收 T-0036**（`mobs/DropRoll`：看 ≤120 行 / `net.minecraft`=0 / `nextInt` 只在掷骰处出现 / 探针 ≥20 条含同种子确定性 + 聚合顺序）。
2. **M6 第四层接线**：`MobSpec` 加 `drops:` 引用 → `MobRegistry` 快照带出 → 死亡掉落（`LivingDropsEvent`）+ `mob check` / `validate` 的引用校验。**注意**：`DropSpec` 的 `id` 不带命名空间，接线时只用裸 id 查表，别顺手补 `redtale_project:`。
3. **`tick` 路径补验**：需要真人在线（R37-b：无玩家不跑 AI）→ 写成「玩家在场时观察 `[mob] … 施放` 日志」的一段脚本，留给有客户端的轮次；本轮已用 `mob cast … roll` 覆盖同一方法。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标、玩家被 `stun`、真人 `/redtale skill mana` 面板、`mob spawn` 的客户端体积/名牌、玩家客户端侧 `dash`、自建怪 `pve+undead` 双键堆叠、**`tick` 路径真人 AI（R40 新）**。

### 13.44 R41 的五条口径 + 下一步（R42）

| # | 口径 | 理由 |
|---|---|---|
| R41-a | `MobSpec.drops` 是**裸 id**（`ember_guard`），不补 `redtale_project:` | `DropSpec` 的 `id` 本来就是裸名；补前缀 = R22 `script` 字段那个坑（`ResourceLocation.CODEC` 静默改命名空间，两边永远对不上） |
| R41-b | 掉落表的 `item` 两种写法：**内容 id 用裸名**（`gem_ruby`）、**物品 id 带命名空间**（`minecraft:gold_nugget`）；写 `redtale_project:gem_ruby` 也容错认成内容 id | 14 基底各只有**一个**物品 id（`redtale_project:amulet`），`gem_ruby` 是 `content_id` —— `BuiltInRegistries.ITEM.containsKey("redtale_project:gem_ruby")` 恒 false，只查注册表则永远掉不出装备（实测 WARN 一条、零产出） |
| R41-c | xp 走 `ExperienceOrb.award`（在 `LivingDropsEvent` 里发），**不挂** `LivingExperienceDropEvent` | 后者只在「原版要发经验」时触发 = **有玩家击杀**；对照实验：`/kill` 一只原版牛 → 0 个经验球。挂它等于「无客户端验收永远为 0」，而且非玩家死亡的怪本来也该给经验 |
| R41-d | 掉落是**加项**：不 `clear()` 原版战利品、不重设经验 | 与 D15「只乘不覆盖」同一条纪律；自建怪的装备/原版战利品照掉，表只往上加 |
| R41-e | `DEFAULT_FILES` 只在**文件缺失**时落地 → 改默认配置**不会**给老副本补新键；新增字段必须写进发布说明 | 本轮第一版「ember_guard 死怪零产出」就是它：测试服副本是 R38 的，没有 `drops:` 键，解析成 `""` = 不掉表，全程无告警 |

下一步（R42）：

1. **验收 T-0037**（`/redtale drop list`：看 ≤160 行 / `grep -c DropRoll`=0 / 测试服两行文案逐字对）。
2. **M6 收口评估**：掉落已通（解析 → 快照 → 事件 → 物品/经验）。剩下的 M6 条目是 **D26 刷怪替换**（按生物群系/难度替换原版刷怪）—— 那是新的一层（`SpawnRule`），要先定 schema 再派卡。
3. **M7 起步前置**：等级/经验/职业的 schema 还没写（M5 的教训：先写 `docs/*.md` 再派解析器卡）。经验来源已经有一条现成的（掉落表的 `xp`），M7 要把「谁吃到这份经验」接上。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标、玩家被 `stun`、真人 `/redtale skill mana` 面板、`mob spawn` 的客户端体积/名牌、玩家客户端侧 `dash`、自建怪 `pve+undead` 双键堆叠、`tick` 路径真人 AI、**玩家击杀时「原版经验 + 表内 xp」两层相加（R41 新）**、**装备槽原版掉落与表并存（样本不足，R41 新）**。

### 13.45 R42 的四条口径 + 下一步（R43）

| # | 口径 | 理由 |
|---|---|---|
| R42-a | M7 分 **L1~L5 五层**，L1 是纯函数 `ExpCurve`（零 MC import / 零 Logger / 无命令），**先落地 L1 才许派 L2 解析器** | 曲线是全项目唯一需要精确数学的一层：`Math.round` vs 截断、到顶返回 0、反查的「阈值 −1 停在前一级」三个边界写错都不会崩、只会让玩家少 1 点经验。纯函数层能离线探针把这三条钉死，混进解析器就再也测不准 |
| R42-b | **等级是派生值，不存**：`SavedData` 只存 `total_exp`（主 + 每职业），等级 = `ExpCurve.levelFor(total)` 现算 | 存等级就必须处理「改曲线后等级和 exp 打架」；派生则改曲线后重算即自洽，且 K4（改曲线 → 等级变、exp 不变）成为一条可机器验的断言 |
| R42-c | **D26 的钩子改判**：`MobSpawnEvent.FinalizeSpawn` **不是**自然刷怪的挂点（1.21.1 只从 `BaseSpawner` / `TrialSpawner` 触发），自然刷怪可用的只有 `MobSpawnEvent.PositionCheck`（`SUCCEED`/`DEFAULT`/`FAIL`）与 `EventHooks.getPotentialSpawns` | javap 实测：补丁后 `Mob.finalizeSpawn` 只写 `spawnType` 字段、不调 `EventHooks.finalizeMobSpawn`；`NaturalSpawner` 的 `EventHooks` 调用只有 `checkSpawnPosition`×2 / `getMaxSpawnClusterSize` / `getPotentialSpawns`。照 D26 原文开工 → 「自然刷怪完全没被替换」且**零报错**，是最难查的那类失败 |
| R42-d | D26 的接线方式收敛为 **`PositionCheck` 否决 + 手动生成**，`spawn_rules/*.json5` 的 `action: replace` 用这条；`getPotentialSpawns` 只用来「加」不进替换 | `PositionCheck` 拿到 `getEntity()` / `getLevel()` / `getX/Y/Z` / `getSpawnType()`，`FAIL` 即可拦下这一次生成并在同坐标 `MobSpawner.spawn`；`getPotentialSpawns` 只能改 biome 的候选表，无法表达「按世界/群系/难度条件替换」这一整套 `match/conditions` |

下一步（R43）：

1. **验收 T-0038**（`ExpCurve`：≤180 行 / `net.minecraft`=0 / 两个工厂各 1 处 / 探针 ≥24 条含 9 条定点值与 `levelFor(totalExpForLevel(L))==L` 全量对拍）。
2. **M7 L2**：`ProgressSpec`（`levels/*.json5` + `jobs/*.json5` 解析，照 `PROGRESSION.md` §3/§4 的夹取与告警口径）+ `ProgressRegistry` 不可变快照 + `RedtaleCore.levels()/jobs()`；`progression.json5`（`mob_exp_multiplier`）进 `DEFAULT_FILES`。
3. **M6 D26 技术验证**（不写内容层）：在 `PositionCheck` 上挂一个只读探针事件，用 `/redtale reload` 打开开关，观察自然刷怪是否被拦（**需要真人在线才刷怪**，R37-b → 无客户端时只验「事件被注册 + 开关日志」，真机挂账）。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标、玩家被 `stun`、真人 `/redtale skill mana` 面板、`mob spawn` 的客户端体积/名牌、玩家客户端侧 `dash`、自建怪 `pve+undead` 双键堆叠、`tick` 路径真人 AI、玩家击杀时「原版经验 + 表内 xp」两层相加、装备槽原版掉落与表并存、**自然刷怪替换真人验收（R42 新）**。

### 13.46 R43 的四条口径 + 下一步（R44）

| # | 口径 | 理由 |
|---|---|---|
| R43-a | **累计经验的唯一真相是语义，不是定点表**：`totalExpForLevel(L) = Σ_{i=1..L-1} expForLevel(i)`；卡面 `totalExpForLevel(4)=352` 判为笔误（正确 `337`），实现在此口径上不打回 | 352 只能是 `total(3)+exp(4)=212+140`，即把第 L 项也加进去；同卡面 `total(3)=212`（100+112）已经证明是 L-1 口径。定点值是「防写错的锚」，锚自己算错一次就会把正确实现判红 —— 以后定点表与语义冲突，**一律按语义裁，并在台账留一行** |
| R43-b | 对外返回的不可变集合**必须保序**：`Collections.unmodifiableMap(new LinkedHashMap<>(src))` / `unmodifiableSet(new LinkedHashSet<>(src))`，**不用** `Map.copyOf` / `Set.copyOf` | `Map.copyOf` 走 `ImmutableCollections` 的随机 SALT，跨 JVM 迭代序不保证（R18 记过一次，本轮 `S7StoreProbe` L1 当场红：`jobExps(a)` 第一个键不是 `miner`）。存档层的职业表顺序直接影响 `/redtale level info` 的行序与 diff 噪点，且「顺序随机」是那种永远复现不了的 bug |
| R43-c | `SavedData.Factory` 用**三参**构造（`new SavedData.Factory<>(ProgressStore::new, ProgressStore::load, DataFixTypes.LEVEL)`） | srg 编译面上 record 只有 3 参构造；2 参构造存在于 universal 补丁版（javap 看得到、`javac` 看不到，报「actual and formal argument lists differ in length」）。这也顺带回答了「要不要 datafix」：`DataFixTypes.LEVEL` 只是让 storage 层知道这是世界数据，我们自己的 `version` 字段照旧自管 |
| R43-d | 存档层**只存 `total_exp`**（主 + 每职业），不存等级；坏行（缺 id / 坏 UUID）整条跳过、负值归零、`MAX_TOTAL_EXP=1e15` 截断，**不抛不告警** | 这是 R42-b 的落地面：等级随时可由 `ExpCurve.levelFor` 重算，存了就要处理「改曲线后两数打架」。`1e15` 不是平衡钳制（D16）：`geometric(maxLevel=1000, growth=1.05)` 的累计量级在 `1e12`，取 `1e15` 只挡溢出。存档层不告警是因为它没有 `ConfigStore` 那样的「配置目录上下文」，坏行告警归 L4 读出去的时候 |

下一步（R44）：

1. **验收 T-0039**（`ProgressSpec`：≤200 行 / `net.minecraft`=0 / `Logger`=0 / 探针 ≥24 条含跨目录不互吃、`max_level` 三类坏值、`attributes` 坏值丢弃且键原样、`exp_sources` 去重与 `[]` 不回缺省）。
2. **M7 L2 快照层**（S7 自做）：`ProgressRegistry`（不可变快照 + 80 条属性表校验 + 告警随快照换代）+ `RedtaleCore.levels()/jobs()` + reload 接线 + `progression.json5`（`mob_exp_multiplier`）进 `DEFAULT_FILES` + 默认 `levels/main.json5` / `jobs/miner.json5`。
3. **M7 L4 服务层**（S7）：`ProgressService`（击杀经验入双累加器 / `level/` `job/` 属性下发先移除再加 / 登录重算）+ 把 `MobDrops` 的 xp 接到 store。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标、玩家被 `stun`、真人 `/redtale skill mana` 面板、`mob spawn` 的客户端体积/名牌、客户端侧 `dash`、`tick` 路径真人 AI、**自然刷怪替换真人验收（R42）**、**真人玩家 `progress add` / 等级属性面板（R43 新）**。

### 13.47 R44 的四条口径 + 下一步（R45）

| # | 口径 | 理由 |
|---|---|---|
| R44-a | **属性表校验放 L2 快照层，不放 L1 解析层**：`ProgressSpec` 只认 schema（键原样保留、不补命名空间），`ProgressRegistry` 才拿 `AttributeSpecs.resolve` 过一遍 | 解析层故意不认识属性表 —— 这是它能零 MC import、能离线探针的前提。把校验塞进去等于让 L1 依赖 `core.attr`，探针也跟着要带服务端 jar。契约（`PROGRESSION.md` §8 红线 3）本来就写「职业想要的属性必须已在表内，否则该条丢弃 + WARN」，落地位置由 L2 承担 |
| R44-b | 快照里的属性键**一律归一成全名**（`AttributeSpecs.resolve(key).id()`），两种写法冲突时后者覆盖 + 一条 WARN | R11-b 的原样复现：属性面板按 modifier id 去重，`attack_damage` 与 `generic.attack_damage` 各生成一个 id → 面板翻倍且没人报错。归一放在「进快照」这一个点上，L4 下发时不用再考虑写法 |
| R44-c | `progression.json5` 只放**跨内容的全局旋钮**（v1 = `mob_exp_multiplier`），曲线与经验来源仍留在 `levels/` `jobs/` 里 | 曲线是**每条定义各自**的（主等级与每个职业都不同），倍率是**全局**的。混在一份文件里，改职业曲线要动全局文件，等于每次调数值都在冒险改倍率 |
| R44-d | `levels/` 与 `jobs/` 出现**同 id** → 留主等级、**丢掉职业那份** + WARN，不是"各存一份" | `get(id)` 会按主等级优先返回，但 `jobs()` 里那份还在 → L4 遍历职业下发属性时会多下发一套 `job/…/…` modifier，且命令面看不到（两个视图不一致）。要么全留要么全丢，留一份才是唯一自洽解 |

下一步（R45）：

1. **验收 T-0040**（`/redtale level list|info`：≤160 行 / `grep -c ProgressSpec`=0 / 测试服三行文案逐字对 + 负向文案）。
2. **M7 L4 服务层**（S7 自做）：`ProgressService` —— 击杀经验入双累加器（`ProgressStore` + `ProgressRegistry` 曲线）、`level/` 与 `job/<职业>/<path>` 属性下发（`ADD_VALUE`，**先移除再加**，`level < 2` 只移除）、登录重算、`/redtale reload` 后重算；把 `MobDrops` 的 xp 接到 store（**同一处**加一份 `total_exp`，不新开事件，R41-c 的孪生口径）。
3. **经验来源第二条**：`/redtale exp add <amount>`（`command` 源）+ 脚本原语 `grant_exp`（`primitive` 源，加原语要换 jar，D17 记账）。
4. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标、玩家被 `stun`、真人 `/redtale skill mana` 面板、`mob spawn` 的客户端体积/名牌、客户端侧 `dash`、`tick` 路径真人 AI、自然刷怪替换真人验收、真人 `progress add` / 等级属性面板、**真人升级后 `level/` modifier 的面板读数（R44 新）**。

### 13.48 R45 的六条口径 + 下一步（R46）

| # | 口径 | 理由 |
|---|---|---|
| R45-a | **属性键两种形态**：原版 `minecraft:generic.max_health`（带命名空间）、**自建是裸 path**（`mining_efficiency`，`AttributeSpecs` 里就这么记）。L4 查属性一律 `AttributeSpecs.resolve(key)` → `RedtaleAttributes.holder(spec)`，**禁止 `ResourceLocation.parse`** | 本轮实测：第一版直接 `ResourceLocation.parse("mining_efficiency")` 被补成 `minecraft:mining_efficiency` → `getHolder` 空 → 职业那条 modifier **静默不下发**（不报错、等级正常、面板只差一点，属于最难发现的一类）。这类「键名形态」错误只能靠 `G Σplan` 这种对账断言抓，靠肉眼读日志抓不到 |
| R45-b | 经验的唯一入口是 `MobDrops`，在**同一处**再记一份 `total_exp`；**不挂第二个事件**、不新建第二份经验表 | R41-c 的孪生口径（`LivingExperienceDropEvent` 只在玩家击杀时触发）。经验球金额保持原版口径（表内 `xp`），`mob_exp_multiplier` 只作用于 `total_exp` —— 球是给玩家看的即时反馈，累加器是成长 |
| R45-c | `level < 2` 时**只移除不加**，且移除按「定义里声明过的全部 id」清，不是按当前 `plan` | 只按 `plan` 移除会在降级时把高档 modifier 留在属性上（R20 的「只增不减」同源）。降级路径（改小曲线 `base`/`growth`）不是异常路径，是 K4 的正常玩法 |
| R45-d | `award` 只写 `total_exp`，等级 `ExpCurve.levelFor` 现算；`Award` 记录里带「主等级前后 + 每个职业前后 + modifier 条数」 | 命令、日志、探针三处都要报「升了几级」，让它们读同一个记录，就不会出现「命令说升了、日志说没升」的第二份真相 |
| R45-e | 探针的期望值必须**按当前配置算**（`wantA = baseline + 0.5×(lv-1)`、`wantF = round(1000×mult)`），不硬编码 23.0 / 1000 | 本轮中途把 `mob_exp_multiplier` 从 1.0 改到 1.5 复跑同一支探针，F 组自动变成「期望 1500」并全绿 —— 硬编码数字的探针在改配置后只会给假红/假绿 |
| R45-f | `/redtale exp` 三子命令都要求真人；只有 `probe` 用 `FakePlayerFactory.getMinecraft` 且**每次先 `store.clear(uuid)`** | FakePlayer 的 UUID 在同一进程内固定，不清场就会「上一轮加满 100 级 → 这一轮 A 组直接顶到 100」；清场还顺带验了 `clear` + 「先移除再加」的清场能力 |

下一步（R46）：

1. **验收 T-0041**（`tools/check_progress.py`：默认件 0 退出 / 三份坏夹具各 1 条问题 / `--dir` 指向测试服配置也 0）。
2. **M7 L5 收尾**：`grant_exp` 脚本原语（`primitive` 源，加原语要换 jar，D17 记账；`SKILLS.md` §4 预算 +1 要同步）；`/redtale level info` 补「当前玩家在这条定义上的等级」（只读，接 `ProgressService.levelOf`）。
3. **真人验收三件**（无客户端做不了，攒一批一起验）：`/redtale exp add` 后 `level/` modifier 的 `/attribute` 读数、登录重算日志、K4「改曲线 → reload → 等级变、exp 不变」。
4. **M6 收口最后一块**：D26 自然刷怪替换（`MobSpawnEvent.PositionCheck` 否决 + 同坐标 `MobSpawner.spawn`，R42-c/d 已定钩子），要先写 `docs/SPAWN-RULES.md` schema 再派卡。
5. 挂账不变：V4「附魔台真刷出」、tooltip 真人客户端、pvp 真目标、玩家被 `stun`、真人 `/redtale skill mana` 面板、`mob spawn` 的客户端体积/名牌、客户端侧 `dash`、`tick` 路径真人 AI、自然刷怪替换真人验收、真人 `progress add` / 等级属性面板、**真人升级后 `level/` modifier 面板读数（R44）**、**击杀路径 `MobDrops → ProgressService` 的真人验收（R45 新，本轮只验了 `command` / `kill` 两条 award 调用，没有真人持剑杀怪）**。
