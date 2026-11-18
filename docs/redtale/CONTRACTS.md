# CONTRACTS · 冻结接口面（S8 只读）

> 改动这份文件 = 改契约，**只能 S7 在 S 轮里改，或者开 `Q-` 让 Aki 拍**。S8 读到不一致就停下写 `NEED-S7:`。
> 为什么冻结：这些 id / 字段名一旦进存档或进其它 mod 的解析，改名就是坏档。加一条要换 jar（`D17`）。

## 1. 三条铁律

1. **注册表项启动期冻结**：`Attribute` / `DataComponentType` / `EntityType` / 脚本原语类型，加一个就是一次发版。
2. **id 只增不减不改名**：属性 `redtale_project:<snake_case>`；内容 id 由配置给，不进注册表。
3. **内容不进注册表**：装备身份在 `ContentData` 里，物品注册 id 只有 14 个基底（`ItemBase`）。加一件新装备 = 加一份 JSON5。

## 2. 模块与包

| 包 | 职责 | 状态 |
|---|---|---|
| `com.redtale.project.core.attr` | 属性注册、spec、来源拆解、攻速 applier | 有 |
| `com.redtale.project.core.math` | `StatValue` / `Settle` / `Caps` / `Sanity` / 曲线 | 有 |
| `com.redtale.project.core.damage` | L2 乘区、白名单、trace、暴击入口（R9） | 有 |
| `com.redtale.project.core.command` | `/redtale` 子命令 | 有 |
| `com.redtale.project.core.config` | JSON5 解析、配置目录 | 有 |
| `com.redtale.project.core.datapack` | 运行期生成数据包的启用（R8）+ **`TagJson`（tag / JSON 写手，幂等，R39）** | 有 |
| `com.redtale.project.core.hook` | 事件接线（脚本 trigger / 攻速 / 乘区 / tooltip / 暴击 / 物品更新刷新点 ①②③ + `UpgradeSweep` ④） | 有 |
| `com.redtale.project.core.script` | 脚本层三张注册表 + builtin | 有 |
| `com.redtale.project.items` | `ContentData` / 基底 / 解析 / 建栈 / tooltip / `ContentItem`（唯一物品行为类，R15）/ `Repairer`（修理唯一结算点，R16） | 有 |
| `com.redtale.project.enchants` | 附魔 schema → datapack（`EnchantmentGenerator`，R21 起接进 reload）+ 唯一自定义效果 `ScriptedEnchantmentEffect`（R21） | 有 |
| `com.redtale.project.core.skill` | `SkillSpec` 纯解析（T-0021）+ `SkillRegistry` 不可变快照（R28）+ `SkillCooldowns` 冷却表（T-0022）+ 技能引擎 `SkillEngine`（R29，M5-A 主体） | 有：`RedtaleCore.skills()` / `skillEngine()`（引擎**跨 reload 存活**） |
| `com.redtale.project.mobs` | `MobSpec` 纯解析（T-0030）+ `MobRegistry` 不可变快照（R36）+ `RedtaleMob`（实体类骨架，8 原型共用）+ `RedtaleEntities`（8 个 `EntityType` 注册，R37）+ **`MobSpawner`（配置 → 实体：属性 / 体积 / 六槽装备 / 名称标签，R38）** + **`MobEntityTags`（`undead:true` 的原型追加进 `#minecraft:undead`，R39）** + **`MobSkillCaster`（怪物技能释放，R40）** + **`SpawnReplacer`（自然刷怪替换执行层，L3，R48）**。M6 四条链路齐全（生成 / 技能 / 掉落 / 刷怪替换） | 有：`RedtaleCore.mobs()`（`mobs/*.json5`，`describe()` 进 reload 日志）；`RedtaleEntities.byBase(base)` / `baseIds()`（实体 id = `MobSpec.BASES` 的八个字符串，R37-b）；`MobSpawner.spawn(level,x,y,z,def)` → `Result`（§4.22） |
| `com.redtale.project.core.progression` | 等级/经验/职业（M7）：`ExpCurve` 曲线纯函数（T-0038，L1）+ `ProgressSpec` 定义解析（T-0039，L2）+ **`ProgressRegistry` 快照（R44，L2，属性键过 80 条表并归一）+ `ProgressRules`（`progression.json5`）** + `ProgressStore` 存档 `SavedData`（R43，L3）+ **`ProgressService` 服务层（R45，L4：经验分配 / 等级派生 / 按级属性下发）**；技能树（D25）：`SkillTreeSpec` 解析（T-0045，L1）+ **`SkillTreeRegistry` 快照（R50，L2：classes 对齐 jobs/ 按 path 比、unlock_skill 对齐 skills/、属性键归一）** | 有：`RedtaleCore.progress()`（`ProgressRegistry`）/ `progressRules()` / **`skillTrees()`（`SkillTreeRegistry`，R50）**；`ProgressStore.get(server)` / `factory()`、`ProgressService.award/applyAttributes/mainLevel` 直接可用；契约见 `docs/PROGRESSION.md` / `docs/SKILL-TREE.md` |

S8 只在卡指定的包内新建文件；新建包需卡上写明。

## 3. 注册 id 清单

| 类别 | id | 说明 |
|---|---|---|
| 组件 | `redtale_project:content` | 唯一内容组件（`ContentData`） |
| 自建属性 | `redtale_project:<snake>` × 66 | 见 `docs/ATTRIBUTE-REGISTRY.md` §2，**不得增删改名** |
| 原版属性引用 | `minecraft:<...>` × 14 | 同上表「落点 = 原版」行 |
| 脚本 effect | `message` / `console_log` / `heal`（R24）/ `damage`（R27）/ `buff`·`damage_aoe`·`debuff`（R32）/ `knockback`·`pull`（R33）/ `stun`（R34）/ `dash`（R37）/ `projectile`（R39）/ `grant_exp`（R46） | `ScriptRegistries` 注册 |
| 脚本 condition | `always` / `health_below` / `chance` | 同上 |
| 脚本 trigger | `manual` / `player_join` | 同上 |
| 伤害类型 | `redtale_project:verification_strike` | 仅验收用（`scaling: never`） |
| 附魔实体效果类型 | `redtale_project:scripted` | **M4 唯一**自定义 `EnchantmentEntityEffect`（D32）；字段 `script`（ResourceLocation）+ `args`（CompoundTag，缺省空） |
| 附魔（L0） | `redtale_project:<配置文件名的 path>` | 由 `enchantments/*.json5` 生成，**不是手写 datapack**；加一个 = 写一份 JSON5 + 重启 |

命令根：`/redtale`，现有子命令 `attr` / `speed` / `damage` / `crit` / `items` / `content list` / `item scan` / `item upgrade` / `item sweep` / `use probe` / `repair` / `repair probe` / `socket` / `socket list` / `socket insert <index> <gem>` / `socket extract <index>` / `socket probe` / `give` / `tooltip` / `whitening` / `reload` / `status` / `list` / `fire`。

`use probe [内容id]` = D23 消耗品端到端：`FakePlayer` 真调一次 `ItemStack#use`，回显效果 / 饱食 / 扣件 / 冷却 / 第二遍拦截（`only_when_hungry` 另跑一组饱食 20/20 看门槛）。不带 id 时取第一个带 `use` 段的内容。

`item sweep` = D33 第 ④ 个刷新点的手动重排（`/redtale reload` 成功后会自动排一次；启动期不排）。分帧执行，命令只负责排队并把区块数回显给执行者。

`item upgrade` = D33 的写回入口：给**执行者自己**的背包 + 末影箱逐格跑 `ItemUpgrader.ensure`，回显 `扫描 / 升级 / 已最新 / 孤儿`。必须玩家上下文（控制台报 `A player is required`）。

`repair <slot>` = 修理管理员入口：用背包里第一件带 `repair` 段的内容物品修指定槽位；`repair probe [内容id]` = 磨刀石端到端三组（受损 / 满耐久 / 不可损坏），FakePlayer 真调 `ItemStack#use`。

## 4. 数据字段（改字段 = 改契约）

`ItemContent`（配置侧，**16 字段**）：`id` / `base` / `name` / `durability` / `rarity` / `weaponAttributes` / `stats` / `stripVanillaEffects` / `rev` / `source` / `consumable`（R15，`ConsumableSpec.Spec`，`null` = 不是消耗品）/ `repair`（R16，`RepairSpec.Spec`，`null` = 不是修理物品）/ `sockets`（R19，`SocketSpec.Layout`，缺省 `Layout.EMPTY`）/ `gem`（R19，`SocketSpec.Gem`，`null` = 不是宝石）/ `setId`（R20，`set_id`，空串 = 不属于任何套装；**定义型字段**，改它要 `rev`+1） / `abilities`（R30，`abilities[]`，每条带命名空间的技能 id，**定义型字段**，改它要 `rev`+1；右键施放**第一条**，空列表 = 不是技能载体）

`ContentData`（运行时组件，**12 字段**）：`content_id` / `content_rev` / `schema` / `set_id` / `upgrade_level` / `rolled_stats` / `rolled_keys` / `affixes` / `abilities` / `weapon_attributes` / `sockets`（R18，`List<String>`，`""` = 空孔）/ `gem_stats`（R18，`Map<String,Double>`）

- 新字段一律 `optionalFieldOf(..., 默认值)`，旧物品缺字段取默认。
- `rolled_stats` 是**这一件实例**的最终值，tooltip / 结算 / `/redtale attr` 三处读同一份（`D22`）。
- `stats` 一律 `ADD_VALUE`（自建属性基值 0，乘算恒 0，见 R5-a）。
- **`rev` 是发布纪律**（D33）：改任何定义型字段（`name` / `rarity` / `durability` / `weapon_attributes` / `stats` / `strip_vanilla_effects`）
  都必须把该 json5 的 `rev` +1，否则存量物品不会更新，而且**不报错**。
- `schema` 是**组件结构版本**（当前 `ContentData.CURRENT_SCHEMA = 2`，R18 从 1 升上来加了 `sockets` / `gem_stats`），改字段名/语义时 +1，并在 `ItemUpgrader` 里加迁移分支。`ItemUpgrader.SCHEMA` **引用** `ContentData.CURRENT_SCHEMA`，不得写第二份字面量。
  > **codec 事实**：`optionalFieldOf("schema", CURRENT_SCHEMA)` 在值等于默认值时不写字段 → 组件里**没有** `schema` 键 = 当前版本，显式写着 `schema:1` 的才是旧版。验迁移看「字段消失」。
- `sockets` / `gem_stats` 是**玩家资产**（M3）：`ensure` 迁移时原样带出，**不重算、不清空**。孔数变化引起的截断/补空孔由镶嵌结算负责（R18-a）。
- 迁移只重建**定义型字段**；`rolled_stats` / `affixes` / `abilities` / `upgrade_level` 是玩家资产，**任何情况下不得自动重算**（D33 / `docs/ITEM-UPDATE.md` §4.3）。
- **`rolled_keys` 语义（D33）**：只有真 roll 出来的键才写进去。迁移时——
  键在 `rolled_keys` → 保留旧值；键不在 → 取**新定义**的值；键在新定义里没了 → 丢弃并记日志；
  遍历旧键集，所以新定义新增的键不会自动出现在老物品上。**M2 词条系统落地前该列表恒空。**
- 迁移重算面板的**唯一入口**是 `ItemFactory.applyDefinition(stack, content, effectiveStats, warnings)`；
  不要另写第二份「按属性建 modifiers」的逻辑（会与白板化规则漂移）。

### 4.1 武器动作命名空间（D33，2026-11-16 放开）

| 配置文件名 | 生成到 |
|---|---|
| `weapon_attributes/<path>.json5` | `data/redtale_project/weapon_attributes/<path>.json` |
| `weapon_attributes/<ns>__<path>.json5` | `data/<ns>/weapon_attributes/<path>.json`（覆盖外部，必 WARN） |

- 内容侧 `weapon_attributes: "x"` 等价于 `"redtale_project:x"`（`WeaponAttributesGenerator.normalizeRef`）。
- **没有**对应配置文件的外部 id 一律跳过、不告警（用它 jar 内的内置项是常态）。
- 校验：ns `[a-z0-9_.-]+`、path `[a-z0-9_./-]+`、禁 `..`。

### 4.2 物品更新 API（D33，R12 定稿）

```java
ItemUpgrader.plan(ContentData current, ItemContent definition) -> Diff   // 纯函数，无 MC 依赖（R11 起归 S7）
ItemUpgrader.ensure(ItemStack stack) -> Result                           // 唯一写回点
enum Status { NOT_CONTENT, UNCHANGED, UPGRADED, ORPHAN }
```

- `ORPHAN`（定义已删）**一个数值都不改**，只让调用方去标红（§4.4）。
- 重建时取值分派在 `ensure`：`rolled_keys` 里的留旧值，其余跟**新**定义；定义里删掉的键丢弃并逐个 `LOG.info` 记账。
- 词条只删「定义里已不存在」的 id，**且词条表为空时原样保留**。
- 手写 `redtale_project:content` 组件时，`rolled_stats` 的键必须是**归一后的全名**（`minecraft:generic.attack_damage`）。
- **五个刷新点**（R17 补第 ⑤）：①登录 ②开容器 ③区块加载 ④`/redtale reload` 后分帧全扫（`UpgradeSweep`）⑤**结算路径惰性兜底**——`DamageLayer#ensureAttackerMainHand` 在 L2 乘区里对攻击者主手调一次 `ensure`（只主手；**不放 tooltip**，客户端也触发；异常按旧版结算；`UPGRADED` 且是 `ServerPlayer` 时 `broadcastChanges()` 一次）。

### 4.3 消耗品 `use` 段（D23，R15 定稿）

```java
ItemContent.consumable() -> ConsumableSpec.Spec        // 解析期落地，null = 不是消耗品
ContentItem#use(Level, Player, InteractionHand)        // 非护甲基底唯一行为入口（10 件）
ScriptEngine.runCalls(List<ScriptCall>, ScriptContext) // 跑「物品自带脚本」，不经 trigger/condition
```

- **不落进 `ContentData`**：右键时按 `contentId` 现查定义 → 改 `use` 段 + `/redtale reload` 对存量物品生效，**不必 rev+1**。
- **只能挂非护甲基底**（`sword`…`shield` / `ring` / `amulet`）。护甲基底是 `ArmorItem`，`use()` 语义为穿戴 → 解析期告警并丢弃 `use` 段。
- 客户端 `use()` 返回 `CONSUME` 不动任何状态；服务端负责效果 / 饱食 / `ItemCooldowns` / 扣件 / `use.script`。
- `consume: only_when_hungry` 在 `FoodData#needsFood()` 为假时返回 `FAIL`（不扣件、不进冷却）。
- 14 基底里**没有食物基底**：先复用 `amulet` 顶外观（Q-016 待拍板：加第 15 基底要换 jar）。

### 4.4 修理段 `repair`（D23 第二半，R16 定稿）

```java
ItemContent.repair() -> RepairSpec.Spec               // 解析期落地，null = 不是修理物品
Repairer.apply(Spec, ItemStack) -> Result            // 唯一结算点（命令与右键同一段代码）
Repairer.matches(Spec, ItemStack) -> boolean         // targets: #tag / ns:path / 裸串=内容 id
Repairer.pickTarget(Player, Spec, ItemStack tool)    // 副手优先 → 背包里损伤最重的一件
ContentItem#useRepair(...)                           // 非护甲基底唯一右键入口
```

- 与 `use` 段同口径：**不进 `ContentData`**，右键按 `contentId` 现查 → 改配置 + `/redtale reload` 对存量物品生效，不必 `rev`+1。
- `targets` 为空 = 不限制（任意可损坏物品）。三种写法：`#ns:tag`（原版物品标签）/ `ns:path`（物品注册 id）/ 裸串（内容 id）。
- `mode: amount` 修固定点数，`percent` 按**最大耐久**比例；`wanted <= 0` 按「已满」处理（不静默成功）。
- **失败不收钱**：只有 `APPLIED` 且 `consume_item` 才扣工具；创造模式不扣。
- 护甲基底一并丢弃 `use` 与 `repair`（右键语义是穿戴）。

### 4.5 孔位段 `sockets` 与宝石段 `gem`（M3，R17 定稿）

schema 全文见 `docs/ITEM-MODEL.md` §5，这里只冻结接口名：

```java
SocketSpec.parseLayout(JsonObject root, String source, List<String> warnings) -> SocketSpec.Layout
SocketSpec.parseGem(JsonObject root, String source, List<String> warnings)    -> SocketSpec.Gem | null
//   Layout(int count, List<String> types)  —— types 长度恒等于 count；count ∈ [0,6]
//   Gem(String type, int tier, String exclusiveGroup, Map<String, StatValue> stats)

AffixPools.parseStats(JsonObject root, String path, List<String> warnings) -> Map<String, StatValue>
AffixPools.normalizeKey(String raw) -> String | null
//   R17 由 private 升 public（**包装方法，零行为变更**）：宝石 / 套装的 stats 必须走同一条
//   解析与归一规则，否则同一属性两种写法会往同一个 modifier id 加两条（面板翻倍，R11-b）
```

- 孔位在**物品定义**里（`sockets.count` / `sockets.types`），宝石是**另一件内容物品**（`gem` 段）。
- 镶嵌结果落 `ContentData.sockets[]`（`""` = 空孔）+ `ContentData.gem_stats{}`（codec 键 snake_case；Java 字段名 `gemStats`）；**宝石数值不并进 `rolled_stats`**（拆宝石要能扣准，见 `ITEM-MODEL.md` §5.1）。
- 套装是独立文件 `sets/*.json5`，物品只写 `set_id`；件数加成是派生值，写固定 modifier id `redtale_project:set/<setId>/<count>`。
- `SocketSpec.Gem` 的 `stats` 由 `AffixPools.parseStats(gemObj, …)` 产出（把 `gem` 对象当 root 传），**不许另写一份 stats 解析**。
- **R19 状态（第 4 步已落地）**：`ItemContent.sockets()` / `ItemContent.gem()` 已接；`ItemFactory.build` 按布局**填空孔**；
  镶嵌 / 取出的唯一结算点是 `Socketer`（见 §4.6）；`ensure` 迁移时按新定义**补空孔**并**重算 `gem_stats`**。
- 孔数**只补不截**：定义把孔数改小不自动截断（截断 = 销毁玩家资产），`ensure` 只逐条记账要求管理员先 `socket extract`。
- 套装解析器（T-0014，R20 `VERIFIED`）：`SetSpec.parseAll(List<ConfigFile>, List<String>) -> Map<String, Definition>` / `SetSpec.activeBonuses(Definition, int wornPieces) -> List<Bonus>`；`activeBonuses` 返回**所有** `count <= wornPieces` 的档（不是只取最高档）。件数下发见 §4.7。

### 4.6 镶嵌结算 `Socketer`（M3 第 4 步，R19 定稿）

```java
Socketer.insert(ItemStack stack, int index, String gemContentId) -> Result   // 唯一镶嵌入口
Socketer.extract(ItemStack stack, int index) -> Result                       // 唯一取出入口
Socketer.solve(List<String> sockets) -> Map<String,Double>                   // gemStats 的唯一算法
Socketer.aligned(List<String> sockets, int count) -> List<String>            // 只补空孔、不截断
Socketer.accepts(String socketType, String gemType) -> boolean               // 任一侧 any 即可镶
enum Status { APPLIED, NOT_CONTENT, NO_SOCKETS, INDEX_OUT_OF_RANGE, NOT_A_GEM,
              TYPE_MISMATCH, EXCLUSIVE_CONFLICT, EMPTY_SLOT }
record Result(Status status, String affectedGemId, Map<String,Double> gemStats, String message)
//   affectedGemId：镶嵌 = 被替换下来的旧宝石（没有则空串）；取出 = 取下的宝石
```

- **面板 id 必须分开**：内容数值用 `redtale_project:content/<属性>`，宝石数值用 `redtale_project:gem/<属性>`。
  同一个 id 在 `AttributeMap` 里是「后加覆盖先加」，同属性既有词条又有宝石时会凭空少一块（R19 实测 7 + 2.1 = 9.1）。
- **取宝石 = 重算整张表**（`solve`），不是「减去那颗宝石的数」；`StatValue` 按 `ItemFactory.ITEM_LEVEL` 取当前等级值。
- 互斥组在 `insert` 拦一次、`solve` 再挡一次（先出现的生效）——后者防手写组件的数据。
- 被替换 / 被取出的宝石由**调用方**退回（`/redtale socket` 造一件新宝石塞背包，满了丢脚下）；结算层不碰背包。
- 失败一律**物品逐字未变**：所有校验都在写之前。

### 4.7 套装件数下发 `SetBonus`（M3 第 6 步，R20 定稿）

```java
SetBonus.worn(Player) -> List<ItemStack>                       // 固定 6 格：护甲 4 + 主手 + 副手
SetBonus.counts(List<ItemStack>) -> Map<String,Integer>         // 纯函数，按**内容 id** 去重（同一件戴两份只算一件）
SetBonus.countOf(Player, String setId) -> int                   // 命令 / tooltip / 结算共用的唯一口径
SetBonus.apply(Player) -> int                                   // 唯一写属性的地方；返回改写的 modifier 个数
SetBonus.clear(Player)                                          // 移除该玩家全部套装 modifier（登出 / reload）
SetBonus.applyAll(MinecraftServer) -> int
SetBonus.activeOf(Player, String setId) -> List<SetSpec.Bonus>   // 生效档（升序）
SetBonus.declaredCounts(SetSpec.Definition) -> List<Integer>     // 定义里声明过的档位数（「先整段移除」用）
SetBonus.modifierId(String setId, int count) -> ResourceLocation // redtale_project:set/<setId>/<count>
SetBonus.amount(Player, String setId, int count, AttributeSpec) -> double
SetBonus.slotOf(ItemBase) -> EquipmentSlot                      // EquipmentSlotGroup → 实际槽位（无公开反查）
```

- 数值一律 `ADD_VALUE`、**固定 modifier id**、**先按声明档位整段移除再加**（R20-c）。件数签名没变时 `apply` 直接返回 0，不碰属性（R20-e）。
- 装备变化**不是单点事件**（背包点击 / 快捷栏 / 被打掉 / 死亡掉落都改装备）→ `GameHooks` 每 20 tick 复核一次。
- 套装数值**永不进 `ContentData`**（R20-b）；`ContentData.set_id` 只是「归属」，由 `ItemFactory.build` 写、`ItemUpgrader.ensure` 取**新定义**的值（R20-a）。
- 命令：`/redtale set`（我的件数）/ `set list` / `set info <id>` / `set sync`（立刻重算）/ `set probe`（FakePlayer 0→1→2→1→0 端到端）。


### 4.8 附魔动作层 `ScriptedEnchantmentEffect`（M4 / D32，R21 定稿）

```java
package com.redtale.project.enchants;

public record ScriptedEnchantmentEffect(String script, CompoundTag args)   // R22：纯字符串 id，不是 ResourceLocation
        implements EnchantmentEntityEffect {
    public static final ResourceLocation ID;      // redtale_project:scripted，固定
    public static final MapCodec<ScriptedEnchantmentEffect> CODEC;
    public static void register(IEventBus modBus); // 走 RegisterEvent，不是 DeferredRegister
}
```

L0 JSON 里的形态（`data/<ns>/enchantment/<path>.json` 的 `effects` 内）：

```json
{ "type": "redtale_project:scripted", "script": "enchants/soul_reap", "args": { "heal_ratio": 0.08 } }
```

| 契约点 | 值 | 改了会怎样 |
|---|---|---|
| 组件 id | `redtale_project:scripted` | 已进注册表，**改名 = 所有引用它的 L0 附魔失效** |
| 字段名 | `script` / `args`（`args` 可省） | 改字段名 = 已生成的 datapack 全部解析失败 |
| `script` 的语义 | L3 脚本的 **action id**（`scripts/*.json5` 里的 `id`），按字符串全等查找 | 找不到只 WARN 一次，附魔仍生效、只是没有执行体（V10） |
| 传给脚本的变量 | `args` 的每个标量键 + `enchant_level`（int）+ `enchant_item`（ItemStack）+ `enchant_pos`（Vec3）+ `attacker`（LivingEntity，R24）+ `affected`（Entity，R24，同时是 `ctx.target()`） | 脚本读 `vars` 拿参数；复合/列表类型的 args 原样放 NBT 标签，脚本自己认 |
| 失败策略 | 一切异常在 `apply` 内吃掉 | 外抛会打断原版伤害/事件链（`post_attack` 一次可达 5 个目标） |
| `script` 的**类型** | `Codec.STRING`（R22 改） | 曾用 `ResourceLocation.CODEC`：裸 id `enchants/soul_reap` 被补成 `minecraft:enchants/soul_reap`，与脚本 id 永不相等 → **附魔生效、执行体静默不跑、零日志** |
| `apply` 的第 4 参 | `affected` 实体（`post_attack` 下是**受害者**，不是攻击者）；攻击者武器在 `EnchantedItemInUse.itemStack()` | 当成攻击者会写出「自己打自己」的执行体（R22-c） |
| 占位符 | `%player%` / `%var.<key>%`；未定义的键**原样保留** | 附魔 `args` → `vars` → effect 文本；保留原样才能看出写错的键（R22-b） |

### 4.9 伤害观测 API `DamageTrace`（M1 / R22 扩）

```java
package com.redtale.project.core.damage;

public final class DamageTrace {
    public static void skip(String damageType, double base);   // R22：白名单外也留进场值
    public static List<Double> recentPassthrough();            // 最近 8 次「原样通过」的进场值，新的在后
    public record Entry(String damageType, double base, double percent, double factor,
                        double value, boolean overflow) {}
    public static List<Entry> recent();   // 只含白名单内（redtale_project:*）的结算
}
```

`/redtale damage` 现在多打一行 `  最近放行进场值（旧→新）：[8.0, 10.0, ...]`。
**这是没有客户端时唯一的数值对账手段**：同怪同武器换一级附魔，看这串数字的差（R22-d）。

### 4.10 基底附魔归属 `EnchantableTags`（M4，R23 定稿）

```java
package com.redtale.project.enchants;

public final class EnchantableTags {
    // datapackRoot / reload 的全量配置 / 告警出口；返回「新建或内容变化」的文件数
    public static int generateAll(Path datapackRoot, List<ConfigFile> configs, List<String> warnings);
    static Map<String, List<String>> vanillaTags();   // tag 名 → 本方块 id（已排序）
    static List<String> tagsFor(ItemBase base);       // 单一基底的归属
}
```

| 契约点 | 值 | 改了会怎样 |
|---|---|---|
| 写在哪 | `data/minecraft/tags/item/enchantable/<名>.json`，`"replace": false` | 改成 `true` = **覆盖**原版与其它 mod 的同名 tag，等于改别人的数据（R22-e 的红线只针对 replace；追加是标准做法，SimplySwords / Farmer's Delight 都这么做） |
| 哪 7 个 tag | `sharp_weapon` / `weapon` / `fire_aspect` / `bow` / `armor` / `equippable` / `durability` | 少一个 = 对应那批附魔对我们的基底报 `cannot support` |
| 归属映射 | 剑=4；匕首/斧/锤/矛/法杖=3（sharp_weapon+weapon+durability）；弓=bow+durability；盾=durability；四件甲=armor+equippable+durability；饰品=durability | 映射跟着 `ItemBase` 走（基底是代码不是内容）；加第 15 种基底要改这张表并换 jar |
| 空互斥 tag | 配置里 `exclusive_set: "#redtale_project:..."` 而文件不存在 → 生成 `values: []` | 不生成就每局刷 `Not all defined tags ... are present in data pack`；生成空 = 暂无互斥，要互斥请手填 |
| 幂等 | 内容与磁盘一致就**不写**（mtime 不动） | 每次 reload 都重写会让整包反复重载，且 `git diff`/备份全是噪点 |
| 生效时机 | tag 是**资源**：`/reload` 即生效；只有附魔注册表要重启 | 与 R21-c 的「附魔要重启」不同层，别混 |

### 4.11 脚本上下文与 `heal` 原语（M4，R24 定稿）

```java
package com.redtale.project.core.script;

public final class ScriptContext {
    public static ScriptContext ofServer(MinecraftServer server);
    public static ScriptContext ofPlayer(ServerPlayer player);
    public static ScriptContext ofEntity(Entity caster, Entity target);   // R24：施法者 + 受害者
    public Entity target();          // 本次触发的作用对象，可为 null
    public boolean hasTarget();
    public ScriptContext target(Entity target);
}
```

```java
package com.redtale.project.core.script.builtin;

public final class HealEffect implements EffectType {   // id = "heal"
    // args.target: caster(缺省) | target
    // args.ratio: 按目标最大生命的比例  args.per_level: 每级追加比例  args.flat: 固定点数
}
```

| 契约点 | 值 | 改了会怎样 |
|---|---|---|
| 原语 id | `heal`（进 `ScriptRegistries`，启动期冻结） | 加/改名 = 换 jar；已有 `scripts/*.json5` 引用的 id 一旦消失，脚本加载期报「未知 effect」→ 该条脚本整体不生效 |
| `target` 取值 | `caster` 缺省：玩家走 `player()`，生物施法者走 `vars.attacker`；`target`：走 `ctx.target()`（`post_attack` 下是受害者） | 语义写反 = 给被打的人回血（实测两根分支都跑通，见 R24 日志） |
| 回血口径 | `flat + 目标最大生命 × (ratio + per_level × (等级-1))` | 等级取 `vars.enchant_level`，缺失当 1。**不是**「按打出伤害的比例」——`post_attack` 的组件签名不带伤害值（R24-a） |
| 异常保护 | 负数归零、`1e9` 硬顶、目标死亡只跳过、目标缺失 WARN 一次 | D16 口径：只留异常保护，不做平衡钳制 |
| 日志 | `[script] heal · <名> <前> → <后>（+<delta>，等级 N，目标 caster|target）` | 验 V9 的唯一证据；没有这行 = 链路某一段断了 |

### 4.12 伤害类别池 `MultiplierRules.Category`（M5 / Q-018，R26 定稿）

```java
public record MultiplierRules(List<String> damageTypes, boolean passthroughExternal,
                              List<String> percentAttributes,
                              Map<String, List<String>> conditionalAttributes,
                              List<Category> categories) {
    public record Category(String match, List<String> attributes) {}
    public List<String> attributesFor(String damageTypeId);   // first-match → 命中类别的池；未命中 → percentAttributes
    public boolean appliesTo(String damageTypeId);            // 白名单，语义不变
}
```

| 项 | 值 | 理由 |
|---|---|---|
| 冻结的伤害类型 | `redtale_project:skill_physical` / `redtale_project:skill_magical`（`data/redtale_project/damage_type/*.json`） | 启动期 datapack registry。**只有这两个**，加技能不新增类型（D17 / R26-a） |
| 类别表顺序 | 声明顺序 **first-match** | 允许「先给 `redtale_project:*` 一刀，再给具体类型例外」，不用写排除语法 |
| 未命中 | 回落 `percent_attributes` | 非技能伤害（`verification_strike` 等）原有行为不变（R26-c） |
| 条件乘区 | **不跟着分轴**，两类共用 `conditional_attributes` | 一个池相加、一次 `Settle.settle`；复制两份必漏改（R26-b） |
| 关掉分轴 | `category_attributes: []` | 配置可退，不改代码 |
| 显示 | `ContentTooltip` 仍读 `percentAttributes`（未命中池）；分轴后的 tooltip 待 M5-B 接 `abilities` 时按技能类型取 | 免得白板武器在 tooltip 上显示法术池 |

### 4.13 技能冷却表 `SkillCooldowns`（M5-A，R26 派单 T-0022）

```java
package com.redtale.project.core.skill;

public final class SkillCooldowns {
    public static int effectiveTicks(int cooldownTicks, double reduction);  // reduction 夹 [0,0.9]，结果 ≥1（cd>0 时）
    public boolean ready(UUID player, String skillId, long nowTick);
    public long remaining(UUID player, String skillId, long nowTick);       // 到期顺手清理
    public void start(UUID player, String skillId, int cooldownTicks, double reduction, long nowTick);
    public boolean tryStart(UUID player, String skillId, int cooldownTicks, double reduction, long nowTick);
    public int prune(long nowTick);
    public void clear(UUID player);
    public void clearAll();
    public int size();
}
```

**纯类**：零 `net.minecraft.*` / `net.neoforged.*` import，时间由调用方传 tick，可在 `selftest` 里直接测。
键必须是 `(UUID, 技能 id)`——按玩家名记账会让改名成为清冷却的手段（R25-b）。

### 4.14 `damage` 原语（M5-A，R27 定稿）

```java
package com.redtale.project.core.script.builtin;

public final class DamageEffect implements EffectType {   // id = "damage"
    public static final String DEFAULT_TYPE = "redtale_project:skill_physical";
    // args.amount: 白值（必填，>0）  args.damage_type: 缺省 DEFAULT_TYPE  args.radius: 不支持（>0 → WARN 忽略）
}
```

| 契约点 | 值 | 改了会怎样 |
|---|---|---|
| 原语 id | `damage`（进 `ScriptRegistries`，启动期冻结） | 加原语 = 换 jar（D17）；已有 `skills/*.json5` / `scripts/*.json5` 引用会加载期报未知 effect |
| 数值口径 | **只 `hurt(src, amount)`，绝不 `setAmount`** | 写绝对值等于绕过属性池：`physical_damage` / 条件乘区对技能全失效，且有无属性时数值不可对账（SKILLS §5 红线 1） |
| 伤害类型 | 缺省 `skill_physical`；法术技能**必须显式写** `skill_magical` | 忘写不报错，但法术会去吃物理百分比池 → 「堆法伤没反应」且日志无提示（SKILLS §5 第 4 条）。类型不在注册表 → 回缺省 + WARN 一次；连缺省都没有（数据包没加载）→ 退 `level.damageSources().generic()` + WARN，**本次不吃乘区** |
| 打谁 | `ctx.target()`（技能释放的被命中实体 / `post_attack` 的受害者）；没有就跳过 + WARN 一次 | 本原语**不**退回打自己（退回 `player()` 只会误伤施法者） |
| 施法者 | `player()` 优先，其次 `vars.attacker`（生物施法者） | 只影响记账与死亡文案，不影响数值 |
| `radius` | **不支持**，>0 → WARN 一次并忽略 | 范围伤害是 `damage_aoe`（第 2 条）的语义；两原语共用一个参数必然有人写错（R27-a） |
| 异常保护 | 缺省/非数字/负数 → 跳过 + WARN 一次；`1e9` 硬顶 | D16：只留异常保护，不做平衡钳制 |
| 观测 | `[script] damage · <名> <前> → <后>（白值 N，类型 msgId，已结算|被原版拦下）` | 端到端验收入口：`/redtale damage hit probe [amount]` 一次跑五组（零属性 / +25% 物理 / 法术只堆物理 / +50% 法术 / 未知类型回缺省） |

### 4.15 附魔可获取性 tag `EnchantObtainTags`（M4 / V4，R27 定稿）

```java
package com.redtale.project.enchants;

public final class EnchantObtainTags {
    public static int generateAll(Path datapackRoot, List<ConfigFile> configs, List<String> warnings);
}
```

| 契约点 | 值 | 改了会怎样 |
|---|---|---|
| 三条 tag（**写死**，不从配置读） | `minecraft:in_enchanting_table` / `tradeable` / `on_random_loot` | 缺一条 = 附魔台刷不出 / 村民不卖 / 战利品不掉（V4 过不了）。从配置读等于允许内容侧静默关掉获取途径 |
| 写法 | `data/minecraft/tags/enchantment/<tag>.json`，`replace: false` **追加** | `replace: true` 会抹掉原版与其它 mod 的同名 tag（R23-a 红线） |
| 取值来源 | `enchantments/*.json5` 的 `id` 字段；不含 `:` 或非字符串 → WARN 跳过 | **不按文件名猜命名空间**：文件名→id 的映射是 `EnchantmentGenerator` 的语义，复制一份必然漂 |
| 空集行为 | 仍写三份空 `values` | 语义 = 「清场」。删光附魔时不清 tag 会留下指向不存在 id 的条目，数据包加载报 Unknown entry |
| 幂等 | 文本逐字相等 → 不写、不改 mtime | reload 每次都改写 mtime 会触发整包重载 |
| 时机 | 只在 `RedtaleCore.reload()` 里跑；tag 是**资源**层，`/reload` 即生效（不用重启） | 与 `enchantment`（启动期 registry）不同层：加附魔要重启，改 tag 不用（R23 两条时机） |

### 4.16 技能引擎 `SkillEngine`（M5-A，R29 定稿）

```java
package com.redtale.project.core.skill;

public final class SkillEngine {
    public enum Status { CAST, NO_SKILL, NO_PLAYER, CONDITION, COOLDOWN, NO_MANA }   // NO_MANA = R35
    public record Result(Status status, String skillId, int remainingTicks, int effects, String failedCondition) {
        public boolean cast();
    }
    public static final double AIM_RANGE = 8.0D;

    public SkillCooldowns cooldowns();
    public ManaPool mana();                                                  // R35：跨 reload 存活
    public Result cast(net.minecraft.server.level.ServerPlayer player, String skillId);
    public static double maxManaOf(net.minecraft.server.level.ServerPlayer player);      // R35
    public static double manaRegenOf(net.minecraft.server.level.ServerPlayer player);    // R35
    public static double manaCostReduction(net.minecraft.server.level.ServerPlayer player); // R35
    public void syncMax(net.minecraft.server.level.ServerPlayer player);     // R35：属性上限变了才写
    public double tickMana(net.minecraft.server.level.ServerPlayer player);  // R35：每 tick，ticks=1
    public String manaText(net.minecraft.server.level.ServerPlayer player);  // "法力 42.0/100.0"
    public String noManaText(net.minecraft.server.level.ServerPlayer player, double rawCost);
    public static String cooldownText(String skillId, int remainingTicks);   // "技能 <id> 冷却中：<N> tick"
    public static net.minecraft.world.entity.Entity aimedTarget(net.minecraft.server.level.ServerPlayer player);
}
```

**顺序是硬约束**（R29-a + R35-c）：③ conditions 全 true → ④a `cooldowns().remaining(...)`（**只查不记**）
→ ④b `mana.spend(...)`（`NO_MANA` 在这里返回，冷却**未记**）→ ④c `cooldowns().start(...)` → ⑤ `runCalls`。
条件不过**不记冷却**、冷却不过**不跑 effects**。未知 condition type 跳过（与 `ScriptEngine#passConditions` 同口径，
解析层按 R28-d 不校验原语）。目标来自视线 raycast `AIM_RANGE` 格（只认活体、排除自己），打不中就是 null，
由 `damage` 原语自己跳过 + WARN（R29-c）。

命令：`/redtale skill list` · `cast <id>`（要玩家，取 UUID）· `probe <id>`（FakePlayer + 木桩牛，A/B 两组数值对照，
会 `cooldowns().clear()`，**验收工具不进玩法路径**，R29-e）· `cd <id>`（只读剩余冷却）· `info <id>`（只读全貌：条件/效果
逐条标注册状态 + 被哪些内容绑定，R31 补）· `mana`（自己那管蓝：当前/上限/回蓝/减免/在册人数，R35）·
`mana set <current> [max]`（运维写回，R35）· `mana probe <id>`（FakePlayer 六组：扣蓝 / 累减 / 蓝不够不扣且不记冷却 /
消耗降低 50% / 回蓝 20 tick / 上限跟属性且不补蓝，R35）。

`ScriptEngine.runCalls` 另有 `(calls, ctx, String owner)` 重载（R29-d）：技能传 `"技能 <id>"`，日志不再是「物品脚本的 effect」；
旧的两参版委托并传 `"物品脚本"`，行为零变更。

### 4.17 物品绑定技能 `abilities` + 冷却减免（M5-B，R30 定稿）

```java
// 配置（items/*.json5）—— 定义型字段，改它要 rev+1
abilities: ["redtale_project:gale_slash"]       // 数组；坏项只跳过自己并告警

// 解析（ItemContent.parse → parseAbilities）
ItemContent.abilities() -> List<String>         // 不可变；不校验技能是否存在（R28-d）

// 写入 / 迁移
ItemFactory.build(content, random)              // ContentData.abilities = content.abilities()
ItemUpgrader.ensure(stack)                      // 重建时取**新定义**的 abilities（与 set_id 同口径）

// 右键（ContentItem#use，分支优先级固定）
use 段 → repair 段 → abilities.get(0) → 什么都不做
    CAST      → CONSUME
    COOLDOWN  → FAIL + 「技能 <id> 冷却中：<n> tick」
    CONDITION → FAIL + 「技能 <id> 条件不满足（<type>）」
    NO_SKILL  → PASS + 一条 WARN（配置漂移不吞物品）

// 冷却减免（M5-B 后半）
SkillEngine.cooldownReduction(ServerPlayer) -> double   // 读 redtale_project:cooldown_reduction，异常归零
SkillCooldowns.effectiveTicks(cd, reduction)            // 夹 [0, 0.9]，结果地板 1 tick（唯一换算点）
```

- **只放第一条**：一键全放等于「按一下掏空家底」；多技能选择是键位绑定（M5-C）。
- `ContentData.abilities` 字段**早就在**（M0 起），本卡之前恒空 —— 所以 schema **不变**（仍 2），不需要迁移。
- 探针：`/redtale skill use "<内容id>"`（FakePlayer 真调 `ItemStack#use`，四组：A 施放 / B 冷却拦截 / C 无 abilities 不放 / D 减免 50%）。

### 4.18 M5-C 原语批次一：`buff` / `damage_aoe` / `debuff`（R32 定稿）

三个原语都只吃 `com.redtale.project.core.script` 包 + 原版类，**不 import `RedtaleCore`**；参数非法一律 WARN 后 return，绝不抛。

| 原语 | 参数（缺省见括号） | 打谁 / 圈心 | 硬约束 |
|---|---|---|---|
| `buff` | `target`(`caster`) · `effect`（**必填**）· `amplifier`(0，0~255) · `duration_ticks`(200，1~72000) | `target:target` → `ctx.target()`；否则 `ctx.player()`；再否则 `vars.attacker` | 只挂**时长型**效果。瞬时效果（`minecraft:instant_damage` / `instant_health`）走 `addEffect` **不结算**（R32-c） |
| `damage_aoe` | `amount`（**必填**）· `radius`(4，上限 32) · `falloff`(0.5，夹 0~1) · `max_targets`(0=不限) · `damage_type`(`skill_physical`) | **圈心 = 有 `ctx.target()` 在受害者脚下，否则施法者脚下**；施法者自身不进命中集合 | 只 `hurt(白值×衰减)`，**绝不 `setAmount`**；衰减只乘白值，倍率仍归 `DamageLayer`。命中按距离升序，`max_targets>0` 取前 N |
| `debuff` | `target`(`target`) · `effect`（**必填**）· `amplifier`(0) · `duration_ticks`(200) | 缺省**受害者**；写 `caster` 才打施法者 | 只收 `MobEffectCategory.HARMFUL`，正面效果 WARN 跳过（R32-b） |

共用约定：

| 契约点 | 值 | 改了会怎样 |
|---|---|---|
| 伤害类型回退 | `DamageEffect.source/holder/caster/num` 是**包内可见**（R32-d），三个伤害原语共用同一份回退 | 各自复制一份 → 以后改第三条必漏一份，现象是「同一技能换个原语就不吃乘区」 |
| 告警去重 | 按**文案**去重（`Set<String>`），不按脚本名 | 按脚本名去重 = 每个技能每次释放刷一行 |
| 数值保护 | 负数/非数字回缺省、`1e9` 硬顶（D16）。**这不是平衡钳制** | 加 `percentCap` 之类的上限 = 推翻 D16 |
| 验证手法 | `skill probe` 的木桩会被 `discard()` → 效果类原语要验「真挂上了」必须走附魔 `post_attack` 打真实体，再 `data get entity … active_effects` | 只验日志 = 验日志；`FakePlayer` 不在实体表里，查不到 `active_effects` |

### 4.19 M5-C 原语批次二：`knockback` / `pull`（R33 定稿）

两条位移原语**共用一份实现**：`KnockbackEffect.shove(ctx, args, defaultRadius, towards)`（包内可见），`PullEffect` 只传 `towards = true` 与缺省半径。

| 原语 | 参数（缺省见括号） | 打谁 | 硬约束 |
|---|---|---|---|
| `knockback` | `strength`(0.4) · `radius`(**0** = 只推受害者，上限 32) | `radius 0` → `ctx.target()`；`>0` → 圈心内所有活体（圈心 = 有受害者在受害者脚下，否则施法者脚下），**施法者永不被自己推** | `strength <= 0` → 一条 WARN 后**真的不位移**（R33-c）；位移只走原版 `LivingEntity#knockback`，吃 `KNOCKBACK_RESISTANCE` |
| `pull` | `strength`(0.4) · `radius`(**6**) | 同上（半径内一圈） | 方向取反；其余同 `knockback` |

| 契约点 | 值 | 改了会怎样 |
|---|---|---|
| 位移实现 | `LivingEntity#knockback(strength, x, z)` + `hurtMarked = true`。**不许** `setDeltaMovement` | 自己拼速度 = 绕过 `KNOCKBACK_RESISTANCE`（抗性 1.0 的目标会被推飞），且日志看不出是谁给的 |
| 方向符号 | 原版内部算 `-normalize(x, z)` → 推离传 `-normalize(目标−施法者)`，拉向传 `+normalize(...)` | 传反 = 击退把人吸过来，无任何日志可查 |
| 水平重合 | 退化为 `+X` + 一条 WARN | 零向量归一化 → NaN 速度（实体瞬移/消失） |
| 数值保护 | 自己写 `raw()` 读参：缺键/非数字/`NaN`/`Inf` → 缺省，**非正数原样返回**交调用方判跳过；`1e9` 硬顶 | 用 `DamageEffect.num` 会把 `strength: 0` 静默换成 0.4（实测踩过，R33-c） |
| 验收手法 | 在**旁观者**的 `Motion` 上对账（`NoAI` 旁观者不动、不吃原版平砍击退、不吃实体碰撞），不看受害者 `Pos` | 受害者同时吃三份力，`Pos` 读不出归因（R33-d）。注意 `Motion` 会收敛到 0.8 不动点，此时本轮 `Δ` 显示 `0.00` 但仍在推 |

### 4.20 M5-C 原语批次三：`stun`（R34 定稿）

「定住」在 1.21.1 没有现成接口，本原语的做法与理由全部写在这里，改之前先读。

| 原语 | 参数（缺省见括号） | 打谁 | 硬约束 |
|---|---|---|---|
| `stun` | `target`(`target`) · `radius`(**0** = 只定住目标，上限 32) · `duration_ticks`(60，`<=0` 跳过，上限 1200) | `radius 0` → `ctx.target()`；`>0` → 圈心内所有活体（圈心 = 受害者脚下），**施法者永不被自己定住** | `Mob#setNoAi(true)` + `Navigation#stop()` + 水平 `setDeltaMovement(0,·,0)`；非 `Mob`（玩家）退路 = `slowness` 7 级，**不是等价替代** |

| 契约点 | 值 | 改了会怎样 |
|---|---|---|
| 定住手段 | 只对 `Mob` 用 `setNoAi(true)`。**不**用 `slowness 255` | `slowness` 是移动速度乘数，会被任何速度修正（装备 / 药水 / 第三方 modifier）抵消成「慢慢挪」，而且怪照样能打人 |
| 在册标记 | 实体 scoreboard tag `redtale_stunned`（1.21.1 **已无** `Entity#getPersistentData()`），随 NBT 保存、`/data get entity @e[…] Tags` 可读 | 换回持久化 NBT 写法会编译不过；不写标记则重启后留下永久 `NoAI` 的怪，且没有任何日志能看出是谁干的 |
| 恢复驱动 | `GameHooks#onServerTickPost` → `StunEffect.tick()`，按「截止时刻」轮询在册表（空闲时一次 `isEmpty`） | 用延时任务（`TickTask`）在关服/`/reload` 时会丢，怪就永久定住 |
| 续定语义 | 同一实体被重复命中时**沿用首次记录的 `wasNoAi`**，只把截止时刻往后推（R34-b） | 每次重读当前状态 → 第二次读到的是「已被我们置 true」，解除时把怪**永久定住**（实测踩过） |
| 重启残留 | `EntityJoinLevelEvent` → 带标记的实体入世即 `setNoAi(false)` + 清标记，恢复值取 `false` | 原 `wasNoAi` 已随重启丢失，「能动」比「永久定住」安全；不清则关服时正在挨打的怪下次上线就成木桩 |
| 验收手法 | 看 `Tags` 是否有 `redtale_stunned` + `data get entity … NoAI`（1b）+ 日志 `[script] stun · <名> <n>t` / `stun 解除 · <名>（到点）` | 只看日志 = 验日志；`Tags` 是唯一能区分「本来就没 AI」与「被我们定住」的凭据 |


### 4.21 法力 `ManaPool` 接线（M5 收口，R35 定稿）

```java
// 定义层：SkillSpec.Definition 7 → 8 字段（位置固定，构造点只有 SkillSpec.parse 一处）
public record Definition(String id, String name, String icon, int cooldownTicks, double manaCost,
                         List<ScriptCall> conditions, List<ScriptCall> effects, String source) {}
```

| 契约点 | 值 | 改了会怎样 |
|---|---|---|
| 上限口径 | `max_mana` **绝对值**；`<=0` / 非有限 → `ManaPool.DEFAULT_MAX`（100），即「0 = 没配」（R35-a） | 按「加成」解释会让一件 +20 的戒指把上限从 100 降到 20（本轮 F 组就是这么红过一次）。备选口径见 Q-019 |
| 回复口径 | `mana_regeneration`/秒；`<=0` = **不回蓝**，不给缺省值（R35-b） | 给一个隐式缺省 = 第二份真相（D18），且「没配」与「配了」在面板上无法区分 |
| 门槛顺序 | 条件 → `cooldowns().remaining()`（只查）→ `mana.spend()` → `cooldowns().start()` → effects（R35-c） | 直接用 `tryStart` 会让「蓝不够」那次吃冷却 → 空蓝连按两下，回蓝后还要等满冷却 |
| 扣蓝公式 | `ManaPool.effectiveCost(raw, reduction)`：`reduction` 夹 `[0, 0.9]`、结果 `round` + **地板 1 点**（`raw>0` 时） | 满减免变免费；在引擎里另写一份换算 = 第二个公式（与 `SkillCooldowns.effectiveTicks` 的同一条纪律） |
| 状态隔离 | `ManaPool` 挂在 `SkillEngine` 上，随 reload 存活；`cooldowns` 与 `mana` 是两张独立的表 | 放进 `RedtaleCore` 的 reload 重建链会「reload 即回满蓝」 |
| 持久化 | **本轮不做**：重登 = 满蓝（R35-e）；`restore`/`clear` 两个口子已就位，等 `PlayerData` | 现在落盘要在「什么时候写 / 丢多少 / 多世界」三件事上先拍板，格式定错会连带改结算 |
| 观测面 | `/redtale skill list` 与 `info` 每行带 `法力 <n>`；`/redtale skill mana probe` A~F 六组；`mana` 只读当前/上限/回蓝/减免 | 没有观测面时「蓝不扣」只能靠人肉感觉，六组探针是唯一能定位到「哪一段断」的东西 |

### 4.22 怪物生成 `MobSpawner`（M6 第三步第 2 小步，R38 定稿）

```java
package com.redtale.project.mobs;

public final class MobSpawner {
    public record Result(boolean ok, String message, net.minecraft.world.entity.Mob mob, java.util.List<String> skips) {}
    public static final String TAG_PREFIX = "redtale_mob/";
    /** 失败不抛异常：ok=false + message 说明原因。 */
    public static Result spawn(net.minecraft.server.level.ServerLevel level,
                               double x, double y, double z, MobSpec.Definition def);
}
```

| 项 | 契约 |
|---|---|
| 落地顺序 | `RedtaleEntities.byBase(base)` → `EntityType#create(Level)`（**单参**，1.21.1 没有 `EntitySpawnReason`）→ `moveTo` → 属性 → 体积 → 六槽 → 名称/标签/持久化 → `addFreshEntity` → `setHealth(getMaxHealth())` |
| 属性写法 | `ADD_VALUE` **临时** modifier，id = `redtale_project:mob/<怪id>/<属性path>`；`addOrUpdateTransientModifier`，重生成是覆盖不是叠加（R38-a） |
| 数值语义 | **加法**：出厂基值（`MAX_HEALTH 20` / `ATTACK_DAMAGE 2` / `MOVEMENT_SPEED 0.25` / `ARMOR 0`）+ 配置值 × 公式 `base + per_item_level × level`。与 `max_mana` 的**绝对值**口径不同（R35-a），别互相套用 |
| 体积 | `minecraft:generic.scale` 的**基值**，`1.0` 不写（唯一走基值的字段，R38-b）；夹取在 `MobSpec` 解析期（`[0.25,4.0]`） |
| 装备 | 六槽 `mainhand/offhand/head/chest/legs/feet` → `BuiltInRegistries.ITEM`；**必须写物品 id**（`redtale_project:sword`），内容 id（`demo_longsword`）→ `skips` 一条，不纠正（纠正属运营决定） |
| 标签 | scoreboard tag `redtale_mob/<怪id>`；`setPersistenceRequired()` 防自然消失；`CustomName` = `name` 且始终可见 |
| `skips` 可达面 | 只有「装备 id 未知」「实体没有该属性」两类；**未知属性键在解析层就被 `AffixPools` 丢掉**，查 reload 告警才是正解（R38-c） |
| 不做 | 技能释放（M6 第 4 步）、刷怪替换、AI 差异、落盘等级字段 |

命令面：`/redtale mob list`（id / 原型 / 等级 / 装备件数 / 技能条数 / 体积）、`/redtale mob spawn <id> [x y z]`（坐标缺省取命令源位置，返回 1/0）。**验收前先 `forceload`**（R38-d）。
刷怪替换观测面（R48）：`/redtale spawn replace`（开关 + 已命中规则数）、`replace on|off`、`replace probe <实体> <x> <y> <z>`（只读决策树）、`replace fire <实体> <x> <y> <z>`（造真事件 POST 到总线，返回 DEFAULT/FAIL/SUCCEED）。


## 5. 路径约定

| 用途 | 路径 |
|---|---|
| 运行配置（玩家/管理员可改） | `config/redtale_project/`（`items/`、`sets/`、`scripts/`、`affixes/`、`affix_pools/`、`weapon_attributes/`、`enchantments/`、`skills/`（M5 起）、`mobs/`、`drops/`、`levels/`、`jobs/`（M7 R44 起）、`skill_trees/`（M7 R50 起）、`attack_speed.json5`、`damage.json5`、`crit.json5`、`progression.json5`（M7 R44 起）） |
| 内置默认配置（首次启动落地） | `src/main/resources/redtale/defaults/` |
| 静态数据包（随 jar） | `src/main/resources/data/redtale_project/` |
| 运行期生成的数据包 | `<world>/datapacks/redtale_project/data/<ns>/...`（`weapon_attributes/` 与 `enchantment/` 共用同一个包根） |
| 附魔 L0 生成物 | `<world>/datapacks/redtale_project/data/redtale_project/enchantment/<path>.json` —— **`/reload` 加不进注册表，要重启**（R21-c） |
| 基底附魔归属（R23） | `<world>/datapacks/redtale_project/data/minecraft/tags/item/enchantable/<7 个名>.json`（追加型）+ `data/redtale_project/tags/enchantment/exclusive_set/<名>.json`（缺失时补空）；都是 `/reload` 即生效 |
| 附魔脚本（L3，随默认配置落地） | `config/redtale_project/scripts/*.json5`（默认 `greeting.json5` + `enchants_soul_reap.json5`） |
| 技能定义（M5，R25 定稿） | `config/redtale_project/skills/<id>.json5`（一个文件一条技能，schema 见 `docs/SKILLS.md` §3）；默认两份 `gale_slash` / `ember_burst` 属 `DEFAULT_FILES`，**删文件会被 reload 重建**（想停用就改文件内容，别删） |
| 怪物定义（M6，R36） | `config/redtale_project/mobs/<id>.json5`（一个文件一只怪，schema 见 `MobSpec` 卡 T-0030）；默认 `ember_guard` / `ash_caster` 属 `DEFAULT_FILES`，**删文件会被 reload 重建** |
| 怪物实体（M6，R38） | 不落盘：`/redtale mob spawn` 现生成；识别靠 scoreboard tag `redtale_mob/<怪id>`（1.21.1 无 `getPersistentData`，R34 事实） |
| 掉落表（M6，R41） | `config/redtale_project/drops/<文件名>.json5`（`id` 是**裸名**，一个文件一张表）；默认 `ember_guard.json5` 属 `DEFAULT_FILES`。**注意**：`DEFAULT_FILES` 只在文件缺失时落地，老配置里的 `mobs/*.json5` 不会自动长出 `drops:` 键（R41 实测：测试服 R38 的 ember_guard 副本没有该键 → 死怪零产出） |
| 刷怪规则（D26 / M6，R47 起进 `DEFAULT_FILES`） | `config/redtale_project/spawn_rules/<文件名>.json5`（`id` 是**身份**、文件名随意；schema 见 `docs/SPAWN-RULES.md`）；默认 `overworld_night_elite.json5` 属 `DEFAULT_FILES`，**删文件会被 reload 重建** |
| 刷怪替换开关（D26 / M6 收口，R52 起进 `DEFAULT_FILES`） | `config/redtale_project/spawn.json5`：v1 只有 `replace_enabled`（缺省 `true`；非布尔的坏值 → 回落缺省 + 一条 WARN）。**运行期可写**：`/redtale spawn replace on|off` 会立刻回写这份文件（R52-a），`/redtale reload` 按文件重设内存；删文件会被 reload 重建为「开」 |
| 等级曲线（M7，R42 定稿；R44 起进 `DEFAULT_FILES`） | `config/redtale_project/levels/<文件名>.json5`（一个文件一条曲线，schema 见 `docs/PROGRESSION.md` §3）；默认 `main.json5` 会**在文件缺失时被重建** |
| 职业定义（M7，R44 起进 `DEFAULT_FILES`） | `config/redtale_project/jobs/<id>.json5`（一个文件一个职业，schema 见 `docs/PROGRESSION.md` §4）；默认 `miner.json5` |
| 经验面全局旋钮（M7，R44） | `config/redtale_project/progression.json5`：v1 只有 `mob_exp_multiplier`（缺省 1.0，负数 → 0 + WARN，>1e9 截断）；曲线不在这里 |
| 技能树（D25 / M7，R50 起进 `DEFAULT_FILES`） | `config/redtale_project/skill_trees/<文件名>.json5`（一个文件一棵树，schema 见 `docs/SKILL-TREE.md` §3；`id` 缺省不补命名空间）。默认 `warrior_vanguard.json5` **删文件会被 reload 重建**；它依赖 `jobs/warrior.json5` 与 `skills/quake_slam.json5` 同时存在（否则 reload 会打两条交叉校验告警） |
| 技能树里的 `classes` | 写**职业裸名**（`warrior`），与 `jobs/*.json5` 的全名 id（`redtale_project:warrior`）**按 path 比较**（R50-a）；空数组 = 所有职业可用 |
| 等级存档（M7） | `world/data/redtale_project_progress.dat`（`SavedData`，**不落** `playerdata`，也不进 config） |
| 构建锁 | `.queue/build.lock`（见 `docs/TASKS.md` §3） |

运行期生成物**不进 jar、不进 config**；jar 内的 `data/` 只放不会变的东西（如 `damage_type`）。

## 6. S8 绝对不碰

- `build.gradle` / `gradle.properties` / `src/main/resources/META-INF/neoforge.mods.toml` / `redtale_project.mixins.json`
- `PLAN.md` / `docs/CONTRACTS.md` / `docs/TASKS.md` 的规则区与别人的卡
- `core/attr/`、`core/math/Settle.java`、`core/damage/`（数值主线，S7 独占）
- `E:\server-test`（启停归 S7）、`E:\server-1.21.1`（正式服，任何人不动）

## 7. 发现契约不够用怎么办

在卡里写：

```
NEED-S7: <一句话问题> · <为什么现在的契约做不到> · <建议的最小改动>
```

然后停手，状态保持 `DOING`。**不要自己加字段、不要自己造接口名。**

### 4.23 亡灵归属 `MobSpec.undead` + `MobEntityTags`（M6 第三步配套，R39 定稿）

`MobSpec.Definition` **9 → 10 字段**：`(id, name, base, scale, level, undead, attributes, equipment, skills, source)`。
`undead` 只参与一个判断 —— 这只怪所在的**原型**要不要进 `#minecraft:undead`。它不进任何数值结算。

| 配置键 | 类型 | 缺省 | 坏值处理 |
|---|---|---|---|
| `undead` | 布尔 | `false` | 非布尔 → `false` + 1 条 WARN（**不**整条跳过，R39-b） |

```java
// com.redtale.project.mobs.MobEntityTags
public static List<String> undeadTypes(Map<String, MobSpec.Definition> defs);   // 纯函数，已排序
public static int generateAll(Path datapackRoot, Map<String, MobSpec.Definition> defs, List<String> warnings);
```

写出物：`<world>/datapacks/redtale_project/data/minecraft/tags/entity_type/undead.json`，
`{"replace": false, "values": ["redtale_project:<base>", …]}`。

**三条口径**：

1. **粒度 = 原型**（R39-a）：EntityType 按 `MobSpec.BASES` 注册，tag 只能按 EntityType 打 →
   同一 `base` 下**任一只**怪写 `undead: true`，整个原型都算亡灵。要按怪区分得等拆子类。
2. **空集也写**（`values: []`）：删光配置后旧值不能留在磁盘上。写盘走 `TagJson.write`，`replace: false` 保证原版值不丢。
3. **幂等**：内容逐字相同就不动文件、不计入 `written`（R39-d）。

**验法**（磁盘与内存是两层，要分别取证，R39-e）：文件 → `cat` / `md5sum`；内存 → `execute if entity @e[type=#minecraft:undead,type=redtale_project:<base>]`。

### 4.24 `PackEnabler` 资源级重载 + `TagJson`（D14 补漏，R39 定稿）

```java
// 旧签名保留，等价于 resourcesChanged = false
public static PackEnabler.Outcome ensureEnabled(MinecraftServer server, String packId, List<String> warnings);
public static PackEnabler.Outcome ensureEnabled(MinecraftServer server, String packId, List<String> warnings,
                                                boolean resourcesChanged);

// com.redtale.project.core.datapack.TagJson
public static boolean write(Path out, List<String> values, String label, List<String> log);      // tag 专用
public static boolean writeIfChanged(Path out, String text, String label, List<String> log);     // 任意文本

// com.redtale.project.core.RedtaleCore
public ReloadResult reload();                    // 启动期用，不重载资源
public ReloadResult reload(boolean allowResourceReload);   // /redtale reload 传 true
```

`Outcome` 新增 `ALREADY_SELECTED_AND_RELOADED`：包已选中、本次**真的写了文件**、2s 去重窗通过 → 顺手 `reloadResources`。
返回值语义：`true` = 文件被新建或内容变化；`false` = 幂等未动 **或** IO 失败（失败会记告警）。

**调用方义务**：任何往 `<world>/datapacks/redtale_project/` 写文件的生成器，①必须走 `TagJson`（拿到幂等 + 统一失败文案）；
②必须把 `true` 的条数累加进 `written`，否则 `/redtale reload` 不知道自己要不要重载资源。

### 4.25 怪物技能释放 `MobSkillCaster` + `SkillEngine.castMob`（M6 第三步第 3 小步，R40 定稿）

```java
// com.redtale.project.mobs.MobSkillCaster（零成员状态：冷却在 SkillCooldowns、随机数用 mob.getRandom()）
public static final int INTERVAL_TICKS = 10;
public record Result(boolean cast, String skillId, SkillEngine.Status status, int effects, String detail) {}
public static int tick(MinecraftServer server);                          // GameHooks 每 tick 调，内部判节拍
public static Result tryCast(Mob mob, MobSpec.Definition def, LivingEntity target);    // 真掷骰（与周期入口同方法）
public static Result forceCast(Mob mob, MobSpec.Definition def, LivingEntity target);  // 忽略 chance，验执行链

// com.redtale.project.core.skill.SkillEngine
public Result castMob(LivingEntity caster, Entity target, String skillId, int cooldownTicks);
```

`castMob` 与 `cast(player,…)` **同序同源**：条件 → 冷却**只查** → 记冷却 → effects。差异只有两处：

| 差异 | 规则 | 理由 |
|---|---|---|
| 法力 | **不扣、不判** | `max_mana` / `mana_regeneration` 是玩家面板属性，自建怪基值 0（R35-a）→ 套上去恒「蓝不够」 |
| 冷却时长 | `cooldownTicks > 0` 用调用方给的；`<= 0` 回落 `SkillSpec.Definition.cooldownTicks()` | 同一个技能玩家 120 tick、精英怪 100 tick 是合法内容 |

生物施法者（非 `ServerPlayer`）会写 `vars.attacker`，`damage` / `heal` 原语靠它认攻击者（R24/R27 既有约定）。

**`tick` 的三条门禁**：① `server.getTickCount() % 10 != 0` → 直接返回；② 实体必须带 scoreboard tag `redtale_mob/<内容id>`（手动 `/summon` 的怪不参与）；
③ `mob.getTarget()` 为空/已死 → **不掷骰**（否则冷却被「空放」吃掉）。

命令行（`core/command/MobSpawnCommand`，验收入口）：

```
/redtale mob cast <id>                  # FORCE：忽略 chance，按配置顺序试到放出去
/redtale mob cast <id> roll             # ROLL：走 tryCast（真掷骰）
/redtale mob cast <id> "<ns:skill>"     # EXPLICIT：只放点名的那条（arg 是 string()，word() 不吃冒号）
```

**复用语义（R40-c，别改回去）**：先找 16 格内带同一 tag 的同类怪，没有才 `MobSpawner.spawn`；输出带 `（复用）` / `（新生）`。
每次现生成会拿新 UUID → 冷却表干净 → 「连放第二次被拦」这条断言恒假通过。

失败输出**必须带状态**（R40-d）：`COOLDOWN 112t` / `(chance 0)` / `(未掷中)` / `没配 skills`；`detail` 为 null 属缺陷。

### 4.26 怪物掉落 `MobSpec.drops` + `MobDrops` + `DropRoll`（M6 第四层，R41 定稿）

```java
// com.redtale.project.mobs.MobSpec.Definition —— 10 → 11 字段，drops 在 skills 之后、source 之前
public record Definition(String id, String name, String base, double scale, int level, boolean undead,
                         Map<String, StatValue> attributes, Equipment equipment,
                         List<SkillRef> skills, String drops, String source) {}

// com.redtale.project.mobs.MobDrops —— GameHooks 构造期注册到 EVENT_BUS
@SubscribeEvent public void onDrops(net.neoforged.neoforge.event.entity.living.LivingDropsEvent event);

// com.redtale.project.core.RedtaleCore
public java.util.Map<String, com.redtale.project.mobs.DropSpec.Definition> drops();   // 键 = 裸 id

// com.redtale.project.mobs.DropRoll（纯函数，零 MC import）
public static Result roll(DropSpec.Definition def, java.util.Random random);
```

四条口径（改之前先读 `PLAN.md` §13.44）：

| # | 口径 | 理由 |
|---|---|---|
| R41-a | `MobSpec.drops` 是**裸 id**，不补 `redtale_project:` | `DropSpec` 的 `id` 本来就是裸名；补前缀 = R22 的 `script` 字段那个坑（永远对不上） |
| R41-b | 掉落表的 `item` 两种写法：**内容 id 用裸名**（`gem_ruby`）、**物品 id 带命名空间**（`minecraft:gold_nugget`）；写 `redtale_project:gem_ruby` 也会被容错认成内容 id | 内容栈 = 基底 id + `redtale_project:content` 组件（R5/R23），`BuiltInRegistries.ITEM` 里没有 `redtale_project:gem_ruby` |
| R41-c | xp 走 `ExperienceOrb.award`（挂在 `LivingDropsEvent`），**不挂** `LivingExperienceDropEvent` | 后者只在「原版要发经验」时触发 = 有玩家击杀；`/kill` 一只原版牛 → 0 个经验球（实测对照）→ 无客户端验收永远看不见 |
| R41-d | 掉落是**加项**：不 `clear()` 原版战利品、不重设经验 | 与 D15「只乘不覆盖」同一条纪律；自建怪的装备照掉 |

`/redtale mob check` 的头行也变了（多了「掉落表 N 张」）：
`[redtale] 怪物检查：<只数> 只 / 技能引用 <k> 条 / 掉落表 <t> 张[ · 引用完整 ✓ | / 问题 <n> 个]`，
问题行格式：`  <名称> <id>: 掉落表 <ref> 不存在（现有 <t> 张：a, b…）`。

### 4.24 进度存档 `ProgressStore`（M7 第三层，R43 定稿；v2 加技能树，R51）

```java
package com.redtale.project.core.progression;

public final class ProgressStore extends net.minecraft.world.level.saveddata.SavedData {
    public static final String FILE_NAME = "redtale_project_progress"; // world/data/<FILE_NAME>.dat
    public static final int VERSION = 2;   // v2 = 加 trees（R51）；v1 档可直接读
    public static final long MAX_TOTAL_EXP = 1_000_000_000_000_000L;

    public static SavedData.Factory<ProgressStore> factory();     // 三参构造 + DataFixTypes.LEVEL（R43-c）
    public static ProgressStore get(MinecraftServer server);      // null → 内存态空存档
    public static ProgressStore load(CompoundTag tag, HolderLookup.Provider provider);

    public long mainExp(UUID id);
    public long jobExp(UUID id, String jobId);
    public java.util.Map<String, Long> jobExps(UUID id);  // 保序不可变视图（R43-b）
    public int size();
    public java.util.Set<UUID> ids();

    public long addMainExp(UUID id, long delta);          // delta <= 0 忽略；返回加完后的值
    public long addJobExp(UUID id, String jobId, long delta);
    public void setMainExp(UUID id, long value);          // <= 0 → 0
    public boolean clear(UUID id);

    // ---- v2：技能树已点节点（按树分桶，存档层零语义，R51-a/b） ----
    public java.util.Map<String, java.util.Set<String>> trees(UUID id);          // 树 id → 节点，保序不可变
    public java.util.Set<String> nodes(UUID id, String treeId);                  // 保序不可变视图
    public boolean hasNode(UUID id, String treeId, String nodeId);
    public boolean addNode(UUID id, String treeId, String nodeId);               // 已存在 / 空 id → false，不脏
    public boolean removeNode(UUID id, String treeId, String nodeId);            // 空桶保留（保树插入序）
    public void setNodes(UUID id, String treeId, java.util.Collection<String> nodeIds); // null / 空集合 = 清空该树
    public boolean clearTree(UUID id, String treeId);                            // 洗点用

    public CompoundTag save(CompoundTag tag, HolderLookup.Provider provider);
}
```

- 存档格式 **v2**：`{ version: 2, players: [ { id: "<uuid-string>", main: <long>, jobs: { "<jobId>": <long> }, trees: { "<treeId>": ["<nodeId>", …] } } ] }`。
  **v1 档（无 `trees` / `version:1`）可直接读**，`trees` 视为空；旧扁平 `nodes` 键（只在 R51 自测档里出现过）读时忽略、写时丢弃（R51-c）。
  节点 id 只在**树内唯一**（每棵树都有 `root`），所以必须分桶存（R51-a）。
  UUID 存**字符串**；坏行（缺 `id` / 解析失败）整条跳过；负值归零；超 `MAX_TOTAL_EXP` 截断。**不存等级**（R42-b）。
- 写操作自动 `setDirty()`；落盘时机由原版 `save-all` / 自动保存决定，本类不主动写文件。
- 命令面：`/redtale progress [status|add <amount>|probe]`（`core/command/ProgressCommand`）。`probe` 用固定 UUID `00000000-0000-0000-0000-0000000000ff` 加 1000 并读回，**控制台可跑**（`add` 需要真玩家）。
- L4（`ProgressService`，R44）只允许调本类的 `add*` / `setMainExp` 与读方法，**不许自己写 NBT**。
- `trees` 一组方法**零语义**：不校验节点是否存在、前置是否满足、点数够不够、树是否存在（R51-b）。这些判定只在 `TreePoints`（L3 纯函数）与将来的 `TreeService` 里做；存档层再判一遍就是第二份真相。
- 实测（R51，测试服）：R50 留下的 126 B `version:1` 真档读起零告警 → `exp primitive` 弄脏 → `save-all` → `version:2` + `trees` 键出现、`main` 逐字保留。

### 4.27 进度服务 `ProgressService`（M7 第四层，R45 定稿）

```java
package com.redtale.project.core.progression;

public final class ProgressService {
    public static final String SRC_KILL = "kill";        // MobDrops 的 xp（唯一吃 mob_exp_multiplier）
    public static final String SRC_COMMAND = "command";   // /redtale exp add
    public static final String SRC_PRIMITIVE = "primitive";// 脚本原语 grant_exp（R46 落地）

    public record Award(long requested, long granted,
                        int mainLevelBefore, int mainLevelAfter,
                        java.util.Map<String,Integer> jobLevelsBefore,
                        java.util.Map<String,Integer> jobLevelsAfter,
                        int modifiers) {
        public boolean levelUp();
        public java.util.List<String> levelUpJobs();
        public String describe();
    }

    public static ProgressSpec.Definition mainDef();                       // 优先 id path = main，否则升序第一条
    public static int levelOf(ProgressSpec.Definition def, long totalExp); // 派生等级（到顶夹住，<=0 → 1）
    public static int mainLevel(MinecraftServer server, UUID id);

    public static Award award(MinecraftServer server, ServerPlayer player, long amount, String source);
    public static int applyAttributes(ServerPlayer player);   // 先按声明 id 全移除，再加本级 plan
    public static void onLogin(ServerPlayer player);
    public static int applyAll(MinecraftServer server);       // reload 后的在线全量重算

    public record Planned(String id, String attribute, double amount) {}   // id 无命名空间
    public static String idOf(ProgressSpec.Definition def, String attribute);
    public static java.util.List<String> declaredIds(ProgressSpec.Definition def);
    public static java.util.List<Planned> plan(ProgressSpec.Definition def, int level);
}
```

- **id 拼法**（`PROGRESSION.md` §6）：主等级 `level/<属性 path>`、职业 `job/<职业 path>/<属性 path>`；写进 `AttributeMap` 时统一加本模组命名空间 → `redtale_project:level/generic.max_health`。
- **属性键两种形态**（R45-a）：原版 `minecraft:generic.max_health`（带命名空间）、自建**裸 path** `mining_efficiency`。查属性一律 `AttributeSpecs.resolve` → `RedtaleAttributes.holder`，**禁止 `ResourceLocation.parse`**（裸 path 会被补成 `minecraft:x` → 静默不下发）。
  R46-a 补：`resolve` 现在也认**省略命名空间的 `generic.xxx`**（`generic.attack_damage` → `minecraft:generic.attack_damage`），因为 `tools/check_progress.py` 按这条宽松口径判「在不在 80 条表内」——对账工具比运行期宽松就是「放行 + 静默丢」，两边必须同一个口径。
- **数值**：`amount = per_level × (level - 1)`，四舍五入 6 位；`ADD_VALUE`；`level < 2` 只移除不加；到顶保留顶级值。
- **经验入口**：只有 `MobDrops`（`kill`，同一处记 `total_exp`）/ `/redtale exp add`（`command`）/ `grant_exp` 原语（`primitive`）。`kill` 是唯一吃 `mob_exp_multiplier` 的来源；经验球金额保持原版口径。
- **命令面**：`/redtale exp [add <amount>|sync|primitive <amount>|probe]`（`core/command/ExpCommand`）。`add` / `sync` 需真人；`primitive`（R46 新增）与 `probe` 走 `FakePlayerFactory`，**控制台可跑**。
  `probe` 7 组断言（A 首次加 / E 双累加器 / F kill 倍率 / G Σplan 对账 / B 到顶 / C 到顶不加 / D 归零清场）；
  `primitive` 把 `grant_exp` 当**真实原语调用**跑（`ScriptEngine.runCalls` → 注册表 → 原语 → `award`），打印「累计前→后 / Δ / 期望 / 主等级前→后 / 职业合计 Δ」并返回 1=通过、0=不符。
- **`grant_exp` 原语**（R46，`core/script/builtin/GrantExpEffect`，id = `grant_exp`）：`args.amount`（必填，`<=0` WARN 跳过、`>1e9` 按硬顶 `GrantExpEffect.HARD_CAP` 发并记日志）、`args.target`（`caster` 缺省 / `target`）；**只对玩家生效**（怪物没有累加器 → WARN 跳过）。来源固定 `primitive`，**不吃** `mob_exp_multiplier`（那个只给 `kill`）。加原语 = 换 jar（D17）；`SKILLS.md` §4 预算 24 → **25**。
- **重算点三处**：登入（`GameHooks.onPlayerJoin`）、`/redtale reload`（`RedtaleCore.reload` 在线全量）、等级变化（`award` 内部）。死亡 / 换维度**不重算**（modifier 随实体存活）。

### 4.28 刷怪规则 `SpawnRuleSpec` + `SpawnRegistry`（D26 / M6，R47 定稿）

```java
package com.redtale.project.mobs;

// L1 解析（S8 写的，T-0042 VERIFIED）—— 零 net.minecraft import
public final class SpawnRuleSpec {
    public record Conditions(List<String> worlds, List<String> biomes, Integer lightMin, Integer lightMax,
                             String time, Integer yMin, Integer yMax, Boolean outside, List<String> difficulties) {}
    public record Definition(String id, String name, List<String> match, String action, String mob,
                             double chance, int priority, int perChunkCap, Conditions conditions, String source) {}
    public static Map<String, Definition> parse(List<ConfigFile> configs, List<String> warnings); // LinkedHashMap，保序
}

// L2 快照（S7，R47）
public final class SpawnRegistry {
    public static final SpawnRegistry EMPTY;
    public static SpawnRegistry load(List<ConfigFile> all, MobRegistry mobs, List<String> warnings);
    public List<SpawnRuleSpec.Definition> ordered();    // priority 降序 → id 升序（执行层只认这个）
    public List<SpawnRuleSpec.Definition> declared();   // 配置文件顺序
    public SpawnRuleSpec.Definition get(String id);
    public boolean has(String id);
    public int size();
    public List<String> sortedIds();
    public List<String> warnings();
    public Map<String, Integer> countByAction();
    public int danglingCount(MobRegistry mobs);
    public String describe();                           // "1 条刷怪规则（replace 1）"
}

// com.redtale.project.core.RedtaleCore
public com.redtale.project.mobs.SpawnRegistry spawnRules();
```

四条口径（改之前先读 `PLAN.md` §13.50）：

| # | 口径 | 理由 |
|---|---|---|
| R47-a | `SpawnRegistry.load(all, mobs, warnings)` **必须排在 `MobRegistry.load` 之后**（`RedtaleCore.reload()` 已按此顺序硬排） | 交叉校验要查 `mob` 是否存在；`mobs` 还是 `EMPTY` 时每条规则都会报悬空，且**不报错**，只表现为「一改配置就满屏告警」 |
| R47-b | 悬空 `mob` → **1 条 WARN + 规则保留**；L3 见悬空**不拦**（回落原版照生成） | 「先写规则、后补怪物定义」是正常运营动作；执行层不拦是 SPAWN-RULES §8 红线 5：宁可少替换，不可把刷怪量改小 |
| R47-c | 排序 = `priority` 降序 → `id` 升序（全序，结果唯一） | 只按 `priority` 排时同优先级顺序取决于配置加载顺序，换机器就漂 |
| R47-d | L1 保持配置顺序、**排序只在 L2**；`declared()` / `ordered()` 两个视图并存 | 一个视图两用会逼调用方自己再排一次 = 第二份真相（R36-a） |

### 4.29 刷怪替换 `SpawnReplacer`（D26 / M6 第三层，R48 定稿）

```java
package com.redtale.project.mobs;

// com.redtale.project.mobs.SpawnReplacer —— 单例；GameHooks 构造期 install()，tick 尾 drain
public static void install();                                   // 注册到 NeoForge.EVENT_BUS，幂等之外无副作用
public static com.redtale.project.mobs.SpawnReplacer get();
public boolean enabled();
public boolean setEnabled(boolean value);                       // 只影响后续刷怪；已入队的补生成照跑
public int hitRules();                                          // 已命中过的规则数（观测用）

// 唯一判定点：match → conditions → 可行性 → 每区块上限 → 掷骰
public Verdict decide(net.minecraft.server.level.ServerLevel level, net.minecraft.world.entity.EntityType<?> type,
                      double x, double y, double z, java.util.function.DoubleSupplier roll);
public String explain(net.minecraft.server.level.ServerLevel level, net.minecraft.world.entity.EntityType<?> type,
                      double x, double y, double z);             // 决策树逐条文字化，只读
public void tick(net.minecraft.server.MinecraftServer server);   // 每 tick ≤8 只排空队列

// record Verdict(boolean replace, boolean add, String ruleId, String mobId, String reason)
```

事件钩子：`net.neoforged.neoforge.event.entity.living.MobSpawnEvent.PositionCheck`（**唯一**钩子，`FinalizeSpawn` 在 21.1.257 只覆盖刷怪笼，见 R42-c）。

六条口径（改之前先读 `PLAN.md` §13.51）：

| # | 口径 | 理由 |
|---|---|---|
| R48-a | 事件里**只**决策 + 入队 + `setResult(FAIL)`；生成一律 `ServerTickEvent.Post` 排空（每 tick ≤8） | 事件在 `NaturalSpawner` 循环里，同步生成撞并发修改；限量防一批命中多只时同 tick 堆实体 |
| R48-b | `decide()` 是唯一判定点（事件与命令共用），判定顺序固定；`explain()` 只读 | 命令自己再判一遍 = 第二份真相（R36-a）；顺序固定保证 RNG 消耗不依赖实体数 |
| R48-c | 可行性（`mobs().get(rule.mob()) == null`）必须在 `setResult(FAIL)` **之前**判；不可行 → 不拦 | `FAIL` 之后无法回滚（SPAWN-RULES §8 红线 5）。代价：`FAIL` 了但 spawn 失败 = 少一只，只留一条 WARN |
| R48-d | `action`：`replace` = 拦 + 生成；`add` = 不拦 + 额外生成 | `add` 是加量，不是「换成两只」 |
| R48-e | 无玩家在线 → 自然刷怪不跑 ⇒ 验收用 `spawn replace fire` 造真事件；真人验收挂账 | `fire` 走同一根总线、同一批监听器、同一条决策链 |
| R48-f | 生成沿用事件坐标（不做落地校正）；高空 `fire` 会落地吃摔伤 | 验「有没有生成」看 `Tags` / `type`，不看血量绝对值（R40-c 同源） |

**新坑（R48 实测）**：`BuiltInRegistries.ENTITY_TYPE.get(未知 id)` 返回 **`pig`**（注册表默认值），必须 `containsKey` 先判；
srg 编译面 `Entity` **没有** `entityTags()`（用 `getTags()`）；`BlockPosArgument.getLoadedBlockPos` 声明受检异常而 `getBlockPos` 不声明；
实体 id 参数用 `ResourceLocationArgument.id()`（`StringArgumentType.string()` 不吃冒号，R40 老坑第三次复发）。

### 4.30 等级观测面「当前」段 `LevelCommand.currentLine`（M7，R49 定稿）

```java
package com.redtale.project.core.command;

// com.redtale.project.core.command.LevelCommand —— 只读观测面；本段只在**玩家上下文**下出现
public static String currentLine(com.redtale.project.core.progression.ExpCurve curve, long totalExp);
// 满级（level >= maxLevel）→ "Lv100 · 本级已满 · 累计 <total>"
// 未满级          → "Lv3 · 本级 21/44 · 累计 65"（cur = total - totalExpForLevel(level)）
```

绑定方式（`/redtale level info <id>`）：`src.getPlayer() != null` 时追加一行 `"\n  当前 " + currentLine(def.curve(), total)`；
`total` 取 `ProgressStore.mainExp(uuid)`（主等级）或 `ProgressStore.jobExp(uuid, id)`（职业）。

| # | 口径 | 理由 |
|---|---|---|
| R49-a | 文案生成是**纯函数**（零 MC 依赖），上下文绑定单独 5 行 | 纯函数可离线探针直测（16/16）；控制台执行输出**逐字不变**，既有 `[VERIFIED]` 卡的文案断言零回归 |
| R49-b | 等级一律 `ExpCurve.levelFor()` 现算，不读缓存；`level >= maxLevel` 优先判，`expForLevel(maxLevel)` 返回 0 故**绝不出 `/0`** | 等级是派生值（R42-b）；`/0` 会在 tooltip 与观测面同时炸 |
| R49-c | `ExpCurve` 构造为 `maxLevel = Math.max(2, n)` → 「上限 1」实际是 2 级曲线；写探针期望时按 `maxLevel()` 取值，别按入参假设 | 实测踩到（期望错、代码对，同 R43-a） |

### 4.31 技能树快照 `SkillTreeRegistry`（D25 / M7 L2，R50 定稿）

```java
package com.redtale.project.core.progression;

// com.redtale.project.core.progression.SkillTreeRegistry —— 不可变快照，跨 reload 整份替换
public static final SkillTreeRegistry EMPTY;                       // 0 棵树
public static SkillTreeRegistry load(List<ConfigFile> all,         // 全部已加载配置，只挑 skill_trees/ 前缀
                                     ProgressRegistry progress,    // 校验 classes；null = 跳过该条校验
                                     SkillRegistry skills,         // 校验 unlock_skill；null = 跳过该条校验
                                     List<String> warnings);       // 告警汇聚点；null 时内部自建
public Map<String, SkillTreeSpec.Definition> all();                // 不可变、保配置文件顺序
public SkillTreeSpec.Definition get(String id);                    // 不存在 / null → null
public boolean has(String id);
public int size();                                                 // 棵数
public int nodeCount();                                            // 节点数合计
public int pointTotal();                                           // max_points 合计（仅摘要，不参与判定）
public List<String> sortedIds();                                   // 升序
public List<String> treesForJob(String job);                       // classes 空 = 全职业可用；按 path 比；null → 空表
public List<String> warnings();
public String describe();                                          // "1 棵技能树（10 个节点，21 点上限）"
```

三条交叉校验（文案逐字，S7 按行 grep）：

```
<source>: 树 <id> 的职业 <job> 不在 jobs/ 里（树仍保留，职业过滤时不会命中）
<source>: 树 <id> 的节点 <node> 引用的技能 <skill> 不存在（该节点点了也不给技能）
<source>: 树 <id> 的节点 <node> 的属性 <attr> 不在 80 条属性表里，已丢弃（该条不会下发）
```

| # | 口径 | 理由 |
|---|---|---|
| R50-a | `classes` 与 `jobs/` id **按 path 比**（`redtale_project:warrior` ≡ `warrior`） | §3 schema 写裸名、`jobs/` 写全名；直接 `containsKey` 会让默认树一上线就告警（本轮实测） |
| R50-b | 属性效果键在 L2 归一成 `AttributeSpec.id()`（原版 = `minecraft:generic.*`，自建 = **裸 path**）；不在表 → 丢弃该条 + 告警；**L1 产物不改** | 与 R44-b 同构；L1 保持原文才能让探针证明归一发生过，也保住 L1 零 `core.attr` 依赖 |
| R50-c | 悬空 classes / 悬空 skill **告警但保留**，执行层自然点不了 | 同 R47-b：先写树后补职业是正常顺序，丢弃会静默失败 |
| R50-d | 调用顺序：**必须排在 `progress` 与 `skills` 之后** | 交叉校验查「另一边有没有」，任一侧 EMPTY 时满屏告警且不抛异常（R47-a 第三次复现） |
| R50-e | 默认件三件套（树 + `jobs/warrior` + `skills/quake_slam`）必须同时进 `DEFAULT_FILES`；§3 示例里三个不在 80 表的键按表改写并在文件头记偏差 | 少一件 = 一启动三条告警；表是 D17 冻结的，改示例不改表 |

### 4.32 刷怪替换开关 `SpawnSettings`（D26 / M6 收口，R52 定稿）

```java
package com.redtale.project.mobs;

// com.redtale.project.mobs.SpawnSettings —— 纯解析，零 MC import（R55：record 加 perTickCap 一字段）
public record SpawnSettings(boolean replaceEnabled, int perTickCap) {
    public static final boolean DEFAULT_REPLACE_ENABLED = true;
    public static final int DEFAULT_PER_TICK_CAP = 8;
    public static final SpawnSettings DEFAULT;
    public static SpawnSettings parse(com.google.gson.JsonObject root, java.util.List<String> warnings);
    public String describe();                                   // "刷怪替换开关 开|关 · 每 tick 上限 8"
}

// com.redtale.project.mobs.SpawnReplacer —— 新增两个方法（R52）+ 上限读写（R55），判定与事件钩子不变
public void applySettings(SpawnSettings settings);              // reload 调；开关与上限一起设（变了才留日志）
public boolean persist();                                       // replace on|off|cap 调；两字段一起写
public int perTickCap();                                        // 当前每 tick 补生成上限
public int setPerTickCap(int value);                            // 夹到 [1,4096]，变了留一行日志
```

| # | 口径 | 理由 |
|---|---|---|
| R52-a | 开关**落盘**且与配置同源：`spawn.json5` 是唯一真相，`reload` 读它重设内存，`on\|off` 写完立刻回写 | 只改内存时 `replace off` 一重启就回「开」，运营以为关了其实没关 —— 静默回滚比缺功能更难查 |
| R52-b | 全局开关放配置根 `spawn.json5`，**不**混进 `spawn_rules/*.json5`（一文件一规则）、**不**塞进 `progression.json5`（经验面） | 目录结构即语义；混进去会让 `SpawnRuleSpec` 对每份规则文件都报「未知键」 |
| R52-c | `persist()` 失败只 WARN 不抛，命令文案里如实写「落盘失败（内存已生效，重启会回缺省）」 | 开关已经在内存生效，落盘失败不该让运营命令报错；但也不能假装成功 |
| R55-a | `per_tick_cap` **是防洪阀不是玩法旋钮**：合法区间 `1~4096`，`0` / 负数 / 小数 / 超界一律回落 `8` 并告警 —— **`0` 不表示「关闭/不限」** | D16 的 `0 = 关闭` 若套到这里会变成「每 tick 无限生成」，正好是这道阀要防的事故；语义反着写比缺配置更危险 |
| R55-b | `persist()` **两字段一起写**（`replace_enabled` + `per_tick_cap`） | 只写一个会把另一个手改值静默抹掉 —— 与 R52-a 同一条纪律：配置文件是唯一真相 |

R55 已闭合挂账：`per_tick_cap` 不再硬编 `DRAIN_PER_TICK = 8`，改由 `spawn.json5` 提供 + `/redtale spawn replace cap <n>` 运行期改写并落盘。

### 4.33 技能树服务层 `TreeService` + `/redtale tree` 写面（D25 / M7 L5，R53 定稿）

```java
package com.redtale.project.core.progression;

// com.redtale.project.core.progression.TreeService —— 服务层，只在服务端主线程调用
public enum Status { OK, UNKNOWN_TREE, UNKNOWN_NODE, ALREADY_TAKEN, MISSING_PREREQ,
                     NO_POINTS, NOT_TAKEN, HAS_DEPENDENTS, NO_PLAYER }
public record Result(Status status, String treeId, String nodeId, List<String> detail,
                     int removed, int added) {
    public boolean ok();                    // status == OK
    public String detailText();             // "," 连接；空 → ""
}

public static SkillTreeSpec.Definition resolve(String rawId);       // 裸名/全名都认；找不到 → null
public static List<String> selected(ServerPlayer player, SkillTreeSpec.Definition def);
public static TreePoints.State state(ServerPlayer player, SkillTreeSpec.Definition def);
public static Result take(ServerPlayer player, String rawTree, String rawNode);
public static Result untake(ServerPlayer player, String rawTree, String rawNode);
public static Result respec(ServerPlayer player, String rawTree);   // clearTree + 前缀批清；扣费挂 Q-021
public static int applyTree(ServerPlayer player, SkillTreeSpec.Definition def);  // 前缀清场 → 按已点集合重加
public static int applyAll(ServerPlayer player);                    // 全部树重下发（登录 / reload）
public static int removeAll(ServerPlayer player);                   // 只清不加（探针清场用）
public static String prefixOf(String treeId);                       // "redtale_project:tree/<path>/"
public static AttributeModifier.Operation operationOf(String raw);  // TreePlan 的字符串 → 原版枚举
public static Map<String, Double> snapshot(ServerPlayer player, SkillTreeSpec.Definition def); // id → amount，观测用
public static UUID idOf(ServerPlayer player);                       // null → 全 0 UUID
```

```text
/redtale tree state <tree>                    玩家上下文：点数/已用/剩余/已点；控制台只看上限
/redtale tree take <tree> <node>              只能由玩家执行
/redtale tree untake <tree> <node>            有已点节点依赖它 → HAS_DEPENDENTS（不级联）
/redtale tree respec <tree>                   清空 + 前缀批清，回「退回 N 个节点」
/redtale tree probe                           控制台可跑，FakePlayer 14 条断言（A~M + R54 的 N）
```

| # | 口径 | 理由 |
|---|---|---|
| R53-a | 存档键用 `def.id()`（快照全名），不用命令传参原文；`resolve()` 先精确、再按 `pathOf` 兜底 | 同一棵树两种写法会在 `ProgressStore.trees` 长出两个桶，症状「点了一半退另一半」 |
| R53-b | 清场一律 `redtale_project:tree/<path>/` **前缀扫描**，不按当前声明清单逐条清 | 改配置换了属性键后旧 modifier 挂在旧属性上，按声明清不到 → 属性残留（SKILL-TREE §5 第 4 条） |
| R53-c | `untake` 有依赖者即拒（带依赖者名单），**不级联**；批量清走 `respec` | 级联会丢玩家没打算丢的节点；点数是从已点集合现算，级联也「扣不回」 |
| R53-d | 点数上限暂取 `def.maxPoints()`，等级换点数未接（M7 剩余项） | `TreePoints` 契约已 VERIFIED；等级换点是取舍题，不在服务层发明 |
| R53-e | `TreeCommand` 由观测面扩为观测+写面（改已 VERIFIED 文件，PLAN §13 R53 记原因）；`list\|info` 输出逐字不变 | R52-c：先观测面（能看见）→ 再写面（能改），顺序不能反 |
| R53-f | `ProgressService.onLogin` / `applyAll` 各补一行 `TreeService.applyAll`，与等级属性同一次重算 | 两套 modifier 同源（都从存档派生），分两次重算就会出现「等级涨了、技能树属性还是旧的」的中间态 |

### 4.34 等级 → 技能点（D25 / M7 出口，R54 定稿）

```java
package com.redtale.project.core.progression;

// 纯函数，零 MC 依赖。capFor 是「点数上限」的唯一派生点。
public static int TreePoints.capFor(int maxPoints, int pointsPerLevel, int level);
//   pointsPerLevel <= 0            → maxPoints（0 则不限）  【关掉等级门槛，D16 风格】
//   level <= 0                     → 0
//   否则                           → maxPoints > 0 ? min(maxPoints, pointsPerLevel*level) : pointsPerLevel*level

public static TreePoints.State TreePoints.state(def, Collection<String> selected, int level);   // 上限走 capFor
public static TreePoints.Status TreePoints.canTake(def, Collection<String> selected,
                                                   String nodeId, int level);                   // NO_POINTS 走 capFor

// 旧入口语义不变（= max_points），探针 / 离线断言仍走它们：
public static TreePoints.State  TreePoints.state(def, selected);
public static TreePoints.Status TreePoints.canTake(def, selected, nodeId);

public static int TreeService.levelOf(ServerPlayer player);   // 主等级；player==null 或没定义 → 0
```

```text
/redtale tree state <tree>   玩家上下文行尾多一段：· 等级 L（P 点/级，上限 M）
                             控制台分支**逐字不变**：· 上限 M 点 · 节点 N 个（控制台不读玩家存档）
/redtale tree probe          A~M（R53 基线，主等级先顶到 max_points 之上）+ N（等级 1 → 上限 1 → cost2 NO_POINTS）
```

| # | 口径 | 理由 |
|---|---|---|
| R54-a | 上限 = `min(max_points, points_per_level × level)`；`points_per_level <= 0` = 关门槛 | 与 `SKILL-TREE.md` §3 的注释一致；`0 = 关闭` 与 D16 同语义，运营可零改码退回 R53 行为 |
| R54-b | 等级只改上限；回档后 `available` 可为负，**不自动退点、不拦已点**，只让新 `canTake` 报 `NO_POINTS` | 点数派生自已点集合；自动退点会静默丢节点且顺序不可预期 |
| R54-c | 旧两参 `state` / 三参 `canTake` 语义**一行不改**（T-0046 已 VERIFIED 文件，本次只加重载） | 探针 L 组与离线断言全走旧入口，改旧语义 = R53 的 13/13 假红 |
| R54-d | 探针先写 `1e9` 经验把主等级顶到上限之上，再跑 A~M；门槛由 N 组单独验 | L1 只有 1 点，否则整套被 `NO_POINTS` 拦成假红 |
| R54-e | 探针收尾 `store.clear(uuid)`，不用「再写大经验值」 | FakePlayer UUID 固定，残留的 `1e9` 会污染 `exp probe` 基线 |


### 4.35 `tree info` 的「当前等级能拿多少点」段 `TreeCommand.levelLine`（D25 / M7，R56 定稿）

```java
package com.redtale.project.core.command;

// 纯函数，零 MC 依赖；上限一律走 TreePoints.capFor（R54-a 的唯一派生点），不在此处重算。
public static String TreeCommand.levelLine(SkillTreeSpec.Definition def, int level);
//   → "\n  当前等级 " + level + " · 可拿 " + capFor(def.maxPoints(), def.pointsPerLevel(), level) + " 点"
//   例：max_points=21 / points_per_level=1 / level=5   → "\n  当前等级 5 · 可拿 5 点"
//       max_points=21 / points_per_level=0 / level=99  → "\n  当前等级 99 · 可拿 21 点"（关门槛）
//       max_points=0  / points_per_level=1 / level=7   → "\n  当前等级 7 · 可拿 7 点"（不限）
//       level<=0                                        → 可拿 0 点（capFor 已夹 0，不抛）
```

```text
/redtale tree info <tree>   控制台（无玩家）：11 行，**逐字不变**（T-0047 基线）
                            玩家上下文：在「职业…· 来源 …」之后、节点行之前**多一行**
                            「  当前等级 L · 可拿 N 点」
```

| # | 口径 | 理由 |
|---|---|---|
| R56-a | 追加行**只在玩家上下文**出现，控制台分支一个字节不改 | `tree info` 的 11 行是 T-0047 的验收基线；同类做法见 R49（`level info` 的「当前」段）——观测面加信息不能打破既有基线 |
| R56-b | 这一段**只报上限**（可拿多少点），不报已用/剩余 | 已用/剩余是 `tree state` 的职责（R53/R54 已定），两处都报会让「同一条信息两个来源」漂移 |
| R56-c | `levelLine` 是**纯函数**且上线（public），探针直接断言字符串 | 玩家分支没有真人在线，只能靠纯函数段离线验；玩家胶水只有「取 level → 拼串」两行 |
| R56-d | 该行**不写「已触顶」之类判断**，`可拿 N 点` 的 N 本身就是真话 | `points_per_level = 0`（关门槛）与 `max_points = 0`（不限）两种语义下，「5 点」不等于「等级 5」，多写一句注释反而会与 `capFor` 打架 |

---

### 4.36 技能解锁派生 `TreeService`（`unlock_skill` 的唯一消费方，D25 / M7 出口，R57 定稿）

**性质**：`TreeService` 的**只读派生**扩展，零存档变更（`ProgressStore` 不加表）、零注册表变更。上一版见 §4.33。

```java
public static java.util.Set<String>  gatedSkillPaths();                       // 归一到 path、保定义序、不可变
public static boolean                gated(String rawSkillId);                // 该技能是否被某棵树声明过
public static java.util.List<String> unlockedSkills(ServerPlayer player);     // 全名、跨树合并、path 去重保首次、不可变
public static boolean                isUnlocked(ServerPlayer player, String rawSkillId);
public static String                 unlockedText(ServerPlayer player);       // 每行 "  " + 全名；空 → "  （无）"
```

- **语义**
  - `gatedSkillPaths` = 把每棵树的**全部节点**当「已点」喂给 `TreeUnlocks.unlocked` 的结果（声明全集），按 path 归一后保定义序。
  - `gated(raw)` = `pathOf(raw)` 属于 `gatedSkillPaths()`；**空串/ null → false**（不设门槛）。
  - `unlockedSkills(player)` = 逐棵树 `TreeUnlocks.unlocked(def, selected(player, def))` 合并，**返回配置里的原写法（全名）**，去重按 path 保首次；`player == null` → 空列表。
  - `isUnlocked` 全名 / 裸名都认（比对走 path）。
  - `unlockedText` 空态固定 `"  （无）"`，非空每行 `"  " + 全名`，行间 `\n`，无首尾换行。
- **存放**：不落存档 —— 解锁集是「已点节点 + 树配置」的派生值（R57-b）。
- **谁消费**：`SkillCommand.cast` —— `gated(id) && !isUnlocked(player, id)` → 拒绝并回 `[redtale] 技能 <id> 未解锁（需要技能树节点，/redtale tree state 看已点）`。`SkillEngine.cast` 本身**不判**（R57-c）。
- **探针**：`/redtale tree probe` O / P / Q 三组（`TreeCommand.probe`，17/17）。

### 4.37 `/redtale tree skills <tree>` 声明/解锁观测面 `TreeCommand.skillsText`（D25 / M7，R58 定稿）

**性质**：只读观测面，零存档变更、零注册表变更、零新配置键。`list` / `info` / `state` / `take` / `untake` / `respec` 的文案与本版**无关**（T-0047 基线逐字不变）。

```java
public static String       skillsText(SkillTreeSpec.Definition def, ServerPlayer viewer);  // viewer 可空
public static java.util.List<String> declaredSkills(SkillTreeSpec.Definition def);
```

- **`declaredSkills(def)`** = `TreeUnlocks.unlocked(def, def.nodes().keySet())`（假装全点 → 声明集），`def == null` → 空列表。顺序 = `def.nodes()` 迭代序（`TreeUnlocks` 契约）。
- **`skillsText(def, null)`**（控制台）→ 严格 `声明技能 N 条（控制台不读玩家存档）` 一行标题 + 每条 `"\n  " + 技能原写法`；声明集为空 → 标题下一行 `"\n  （该树没有 unlock_skill 声明）"`。**不猜玩家状态**（R58-a）。
- **`skillsText(def, player)`** → 标题 `声明技能 N 条 · 已解锁 M 条`（M = `TreeUnlocks.unlocked(def, selected(player, def)).size()`）+ 每条 `"\n  " + 技能 + (" · 已解锁" | " · 未解锁")`；标注走 `TreeService.isUnlocked`（全名/裸名同一条，R58-c）。
- **命令**：`/redtale tree skills <tree>` —— 树不存在 → `[redtale] 没有技能树 <id>（现有 N 棵：<逗号分隔>）`（与 `state` 同一文案），返回 0；否则发送全文，返回声明集条数。
- **谁消费**：运营 / 玩家自查「这棵树管着哪些技能、我拿到了哪些」；`skill cast` 的门槛拒绝文案指向 `tree state`，本条是它的补充观测面。
- **探针**：`/redtale tree probe` **R 组**（`TreeCommand.probe`，18/18）。
