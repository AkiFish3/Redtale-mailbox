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
| `com.redtale.project.core.datapack` | 运行期生成数据包的启用（R8） | 有 |
| `com.redtale.project.core.hook` | 事件接线（脚本 trigger / 攻速 / 乘区 / tooltip / 暴击 / 物品更新刷新点 ①②③ + `UpgradeSweep` ④） | 有 |
| `com.redtale.project.core.script` | 脚本层三张注册表 + builtin | 有 |
| `com.redtale.project.items` | `ContentData` / 基底 / 解析 / 建栈 / tooltip / `ContentItem`（唯一物品行为类，R15）/ `Repairer`（修理唯一结算点，R16） | 有 |
| `com.redtale.project.enchants` | 附魔 schema → datapack（`EnchantmentGenerator`，R21 起接进 reload）+ 唯一自定义效果 `ScriptedEnchantmentEffect`（R21） | 有 |
| `com.redtale.project.core.skill` | `SkillSpec` 纯解析（T-0021）+ `SkillRegistry` 不可变快照（R28）+ `SkillCooldowns` 冷却表（T-0022）+ 技能引擎 `SkillEngine`（R29，M5-A 主体） | 有：`RedtaleCore.skills()` / `skillEngine()`（引擎**跨 reload 存活**） |
| `com.redtale.project.mobs` | 模板实体（M6） | **未建** |
| `com.redtale.project.progression` | 等级/技能树（M7） | **未建** |

S8 只在卡指定的包内新建文件；新建包需卡上写明。

## 3. 注册 id 清单

| 类别 | id | 说明 |
|---|---|---|
| 组件 | `redtale_project:content` | 唯一内容组件（`ContentData`） |
| 自建属性 | `redtale_project:<snake>` × 66 | 见 `docs/ATTRIBUTE-REGISTRY.md` §2，**不得增删改名** |
| 原版属性引用 | `minecraft:<...>` × 14 | 同上表「落点 = 原版」行 |
| 脚本 effect | `message` / `console_log` / `heal`（R24） | `ScriptRegistries` 注册 |
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

`ItemContent`（配置侧，**15 字段**）：`id` / `base` / `name` / `durability` / `rarity` / `weaponAttributes` / `stats` / `stripVanillaEffects` / `rev` / `source` / `consumable`（R15，`ConsumableSpec.Spec`，`null` = 不是消耗品）/ `repair`（R16，`RepairSpec.Spec`，`null` = 不是修理物品）/ `sockets`（R19，`SocketSpec.Layout`，缺省 `Layout.EMPTY`）/ `gem`（R19，`SocketSpec.Gem`，`null` = 不是宝石）/ `setId`（R20，`set_id`，空串 = 不属于任何套装；**定义型字段**，改它要 `rev`+1）

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
    public enum Status { CAST, NO_SKILL, NO_PLAYER, CONDITION, COOLDOWN }
    public record Result(Status status, String skillId, int remainingTicks, int effects, String failedCondition) {
        public boolean cast();
    }
    public static final double AIM_RANGE = 8.0D;

    public SkillCooldowns cooldowns();
    public Result cast(net.minecraft.server.level.ServerPlayer player, String skillId);
    public static String cooldownText(String skillId, int remainingTicks);   // "技能 <id> 冷却中：<N> tick"
    public static net.minecraft.world.entity.Entity aimedTarget(net.minecraft.server.level.ServerPlayer player);
}
```

**顺序是硬约束**（R29-a）：③ conditions 全 true → ④ `cooldowns().tryStart(...)` → ⑤ `runCalls`。
条件不过**不记冷却**、冷却不过**不跑 effects**。未知 condition type 跳过（与 `ScriptEngine#passConditions` 同口径，
解析层按 R28-d 不校验原语）。目标来自视线 raycast `AIM_RANGE` 格（只认活体、排除自己），打不中就是 null，
由 `damage` 原语自己跳过 + WARN（R29-c）。

命令：`/redtale skill list` · `cast <id>`（要玩家，取 UUID）· `probe <id>`（FakePlayer + 木桩牛，A/B 两组数值对照，
会 `cooldowns().clear()`，**验收工具不进玩法路径**，R29-e）· `cd <id>`（只读剩余冷却）。

`ScriptEngine.runCalls` 另有 `(calls, ctx, String owner)` 重载（R29-d）：技能传 `"技能 <id>"`，日志不再是「物品脚本的 effect」；
旧的两参版委托并传 `"物品脚本"`，行为零变更。

## 5. 路径约定

| 用途 | 路径 |
|---|---|
| 运行配置（玩家/管理员可改） | `config/redtale_project/`（`items/`、`sets/`、`scripts/`、`affixes/`、`affix_pools/`、`weapon_attributes/`、`enchantments/`、`skills/`（M5 起）、`attack_speed.json5`、`damage.json5`、`crit.json5`） |
| 内置默认配置（首次启动落地） | `src/main/resources/redtale/defaults/` |
| 静态数据包（随 jar） | `src/main/resources/data/redtale_project/` |
| 运行期生成的数据包 | `<world>/datapacks/redtale_project/data/<ns>/...`（`weapon_attributes/` 与 `enchantment/` 共用同一个包根） |
| 附魔 L0 生成物 | `<world>/datapacks/redtale_project/data/redtale_project/enchantment/<path>.json` —— **`/reload` 加不进注册表，要重启**（R21-c） |
| 基底附魔归属（R23） | `<world>/datapacks/redtale_project/data/minecraft/tags/item/enchantable/<7 个名>.json`（追加型）+ `data/redtale_project/tags/enchantment/exclusive_set/<名>.json`（缺失时补空）；都是 `/reload` 即生效 |
| 附魔脚本（L3，随默认配置落地） | `config/redtale_project/scripts/*.json5`（默认 `greeting.json5` + `enchants_soul_reap.json5`） |
| 技能定义（M5，R25 定稿） | `config/redtale_project/skills/<id>.json5`（一个文件一条技能，schema 见 `docs/SKILLS.md` §3）；默认两份 `gale_slash` / `ember_burst` 属 `DEFAULT_FILES`，**删文件会被 reload 重建**（想停用就改文件内容，别删） |
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
