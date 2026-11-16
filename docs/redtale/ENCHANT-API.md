# 附魔接口（M4 主线 · D32）

> **2026-11-15 12:56 Aki 拍板**：「另外做，因为本质上是为了测自制的附魔接口。」
>
> → M4 **不做**「用 `enchantmentdisabler` 抬原版上限」，改为**先做自己的附魔接口**，第一批附魔跑在这个接口上。

## 0. 这条决策否掉了什么

| 路线 | 成本 | 实际验证到的东西 |
|---|---|---|
| 抬 `enchantmentdisabler` 的 `maxLevels` | 改一行 TOML，几分钟 | 「别人的配置项能改」。接口一行没测 |
| **另做附魔接口（选定）** | 几天 | schema → 生成 JSON → 进注册表 → 附魔台/铁砧/砂轮全链路 → **自定义 effect 能 dispatch 到我们的脚本层** |

M4 的目的不是「让锋利变成 V 级」，而是让**后面 100 个附魔都不用再写 Java**。抬上限对这种能力零贡献，所以另做。

`enchantmentdisabler` 保留在整合包里，但**不启用 `maxLevels`/`globalMaxLevel`**，只在「要禁掉某条原版附魔」时用 `disabledEnchantments`（它只做减法，不做加法）。

## 1. 事实底（`server-1.21.1-20240808.144430-srg.jar` javap 实测，非记忆）

| # | 事实 | 后果 |
|---|---|---|
| F1 | `net.minecraft.world.item.enchantment.Enchantment` 是 **datapack registry** 元素（`data/<ns>/enchantment/*.json`） | 附魔本体**可以 `/reload` 热更**，不用换 jar |
| F2 | `Enchantment.EnchantmentDefinition` = `supported_items` / `primary_items`(Optional) / `weight` / `max_level` / `min_cost` / `max_cost` / `anvil_cost` / `slots` | schema 的字段就这 8 个 + `effects` / `description` / `exclusive_set` |
| F3 | `EnchantmentEffectComponents` 共 **30** 个静态组件：`damage` `damage_protection` `damage_immunity` `smash_damage_per_fallen_block` `knockback` `armor_effectiveness` `post_attack` `hit_block` `item_damage` `attributes` `equipment_drops` `location_changed` `tick` `ammo_use` `projectile_piercing` `projectile_spawned` `projectile_spread` `projectile_count` `trident_return_acceleration` `fishing_time_reduction` `fishing_luck_bonus` `block_experience` `mob_experience` `repair_with_xp` `crossbow_charge_time` `crossbow_charging_sounds` `trident_sound` `prevent_equipment_drop` `prevent_armor_change` `trident_spin_attack_strength` | **没有 `block_break_speed` 组件**。效率类走 `attributes` + 属性 `minecraft:player.block_break_speed`（或 `player.mining_efficiency`），`PLAN.md` §10 原来的写法是错的，以本文为准 |
| F4 | `EnchantmentEntityEffect` 是 interface：`apply(ServerLevel, int level, EnchantedItemInUse, Entity, Vec3)` + `MapCodec codec()` | 自定义 effect 就是实现它，一个类 |
| F5 | **effect 类型注册表是内建静态表** `BuiltInRegistries.ENCHANTMENT_ENTITY_EFFECT_TYPE`（`Registry<MapCodec<? extends EnchantmentEntityEffect>>`），不是 datapack registry | 加一个**新的 effect 类**必须换 jar（启动期注册）；而**用现有类配不同参数**不换 jar。→ 所以第 4 节只做一个万能容器 |
| F6 | `LevelBasedValue` 6 种子类：`constant` / `linear`(base, per_level_above_first) / `lookup` / `clamped` / `fraction` / `levels_squared` | 等级曲线全部数据化，`linear` 覆盖 90% |
| F7 | `Attributes.BLOCK_BREAK_SPEED` 与 `Attributes.MINING_EFFICIENCY` 都存在，但都是**属性** | `attributes` 组件里写 `{"attribute": "minecraft:player.mining_efficiency", "amount": <LevelBasedValue>, "operation": "add_value"}` |

> 与 `DAMAGE-PIPELINE.md` §8 的关系：§8.1 定的是 schema 形态与互斥规则，本文定的是**工程接口与验收**。字段解释以本文 §3 为准。

## 2. 四层接口

```
L3 脚本层   config/redtale_project/scripts/*.json5     effect/trigger/condition（M0 已有）
             ↑ 被调用
L2 组件层   redtale_project:scripted（Java，一个类）     ← 唯一需要换 jar 的东西
             ↑ 出现在 effects 里
L1 schema   config/redtale_project/enchantments/*.json5  JSON5 → JSON
             ↓ 生成
L0 datapack data/redtale_project/enchantment/*.json     真·原版 Enchantment
```

| 层 | 改它要重启吗 | 谁受影响 |
|---|---|---|
| L0 | `/reload` 即可（F1） | 无 |
| L1 | `/redtale reload`（重生成 L0 再 reload） | 无 |
| L2 | **换 jar + 重启**（F5） | 所有引用该组件类型的附魔 |
| L3 | `/redtale reload` | 引用该脚本的附魔 |

**设计目标**：M4 把 L2 一次做到「够用到关服」，之后 100 个附魔全部落在 L1+L3，永不换 jar。这就是「测接口」的真正验收标准——不是「锋利能到 V」，而是「加第 51 个附魔时只写 JSON5」。

## 3. schema（JSON5 → JSON）

```json5
// config/redtale_project/enchantments/super_sharpness.json5
{
  id: "redtale_project:super_sharpness",   // 命名空间可省，缺省补 redtale_project:
  description: "超级锋利",                  // 生成 lang key enchantment.redtale_project.super_sharpness
  max_level: 3,
  weight: 4,
  anvil_cost: 2,
  slots: ["mainhand"],
  supported_items: "#minecraft:enchantable/sharp_weapon",
  primary_items: null,                      // 可选，缺省不写
  min_cost: { base: 5, per_level_above_first: 12 },
  max_cost: { base: 25, per_level_above_first: 12 },
  exclusive_set: "#minecraft:exclusive_set/damage",
  effects: {
    "minecraft:damage": [
      { effect: { type: "minecraft:add",
                  value: { type: "minecraft:linear", base: 2.0, per_level_above_first: 1.0 } } }
    ]
  }
}
```

脚本化附魔（走 L2+L3）：

```json5
// config/redtale_project/enchantments/soul_reap.json5
{
  id: "redtale_project:soul_reap",
  description: "摄魂",
  max_level: 2, weight: 2, anvil_cost: 4,
  slots: ["mainhand"],
  supported_items: "#minecraft:enchantable/sword",
  exclusive_set: "#redtale_project:exclusive_set/lifesteal",
  effects: {
    "minecraft:post_attack": [
      {
        enchanted: "attacker",          // 原版 TargetedConditionalEffect 字段
        affected: "victim",
        effect: {
          type: "redtale_project:scripted",
          script: "enchants/soul_reap",
          args: { heal_ratio: 0.08 }     // 透传给脚本层，可被脚本读
        }
      }
    ]
  }
}
```

### 3.1 字段映射（JSON5 键 → L0 JSON 键）

| JSON5 | L0 `enchantment/*.json` | 备注 |
|---|---|---|
| `id` | 文件名 + `#` 前缀决定 | 文件名 = 去掉命名空间的 path |
| `description` | `description` | 同时写 lang，不在 JSON 里塞中文 |
| `max_level` / `weight` / `anvil_cost` | 同名 | |
| `slots` | `slots` | `EquipmentSlotGroup` 名，如 `mainhand` / `armor` / `hand` |
| `supported_items` / `primary_items` | 同名 | tag（`#`）或物品 id 列表 |
| `min_cost` / `max_cost` | 同名 | `{base, per_level_above_first}` |
| `exclusive_set` | `exclusive_set` | tag |
| `effects` | `effects` | 组件名 → 列表，原样透传（我们只补缺省、不改语义） |

**透传原则**：`effects` 里除 `redtale_project:scripted` 外，**一律原样写进 JSON**，不做二次抽象。原版组件已经够表达的东西，我们不再发明一层 DSL——多一层就多一层出错面。

## 4. L2：唯一自定义组件 `redtale_project:scripted`

### 4.1 为什么只有一个

F5 决定了每个新 effect 类都是一次换 jar。若按「一个附魔一个类」做，100 个附魔 = 100 次发版。所以只做一个**通用调用器**：把「什么时候触发」交给原版 30 个组件，把「触发后干什么」交给 L3 脚本层。

```java
// scripted/ScriptedEnchantmentEffect.java
// ⚠ R22 已改：script 是 **纯字符串 id**，不是 ResourceLocation（本段曾按旧形态写，2026-11-17 dev 复核指出）。
//   用 ResourceLocation.CODEC 会把裸 id `enchants/soul_reap` 补成 `minecraft:enchants/soul_reap`，
//   与脚本 id 永不相等 → 附魔生效、执行体静默不跑、零日志。冻结口径见 CONTRACTS §4.8。
public record ScriptedEnchantmentEffect(String script, CompoundTag args)
        implements EnchantmentEntityEffect {

    public static final MapCodec<ScriptedEnchantmentEffect> CODEC =
        RecordCodecBuilder.mapCodec(i -> i.group(
            Codec.STRING.fieldOf("script").forGetter(ScriptedEnchantmentEffect::script),
            CompoundTag.CODEC.optionalFieldOf("args", new CompoundTag())
                          .forGetter(ScriptedEnchantmentEffect::args)
        ).apply(i, ScriptedEnchantmentEffect::new));

    @Override public MapCodec<? extends EnchantmentEntityEffect> codec() { return CODEC; }

    @Override
    public void apply(ServerLevel level, int enchLevel, EnchantedItemInUse item,
                      Entity owner, Vec3 pos) {
        ScriptRegistry.fire(script, new ScriptContext(level, owner, item, pos, enchLevel, args));
    }
}
```

注册（NeoForge，启动期一次）：

```java
// 在 mod 构造器里，或 RegisterEvent 里
event.register(BuiltInRegistries.ENCHANTMENT_ENTITY_EFFECT_TYPE,
    id("scripted"), () -> ScriptedEnchantmentEffect.CODEC);
```

> **M4 第一天必须验证**：`BuiltInRegistries.ENCHANTMENT_ENTITY_EFFECT_TYPE` 在 NeoForge 21.1 下能否用 `RegisterEvent` 写入（它是内置表，不是 `DeferredRegister` 目标）。这条不通，L2 整层就不成立，要先解决。

### 4.2 dispatch 到 L3

脚本层的三张表 M0 已有（effect / trigger / condition）。`scripted` 组件做的事只有一件：

1. 按 `script` 找脚本；**找不到 → WARN 一次 + 不生效**（不崩、不刷屏，用 `Set<ResourceLocation>` 记住已报过）。
2. 把 `{level, owner, item, pos, args}` 塞进脚本上下文。
3. 交给脚本层执行 `effects[]`。

这样「命中流血」= 原版 `post_attack` 触发 + 我们的 `scripted` 调 `enchants/bleed` 脚本；「击杀爆炸」= `post_attack` + condition 判死亡 + 脚本 `explode`。**触发时机不重复造轮子，只造执行体。**

### 4.3 参数不是自由文本

`args` 走 `CompoundTag`（NBT），不用字符串拼装：脚本读 `args.heal_ratio` 是数值，能参与表达式；字符串只能 switch。这条是 D14「全内容可配」在附魔上的落地形式。

## 5. 生成与热更

| 步骤 | 位置 | 触发 |
|---|---|---|
| 读 JSON5 | `config/redtale_project/enchantments/*.json5` | 启动 / `/redtale reload` |
| 生成 L0 | `data/redtale_project/enchantment/<path>.json`（写进 mod 的 datapack 源） | 同上 |
| 生成 lang | `assets/redtale_project/lang/zh_cn.json` 的 `enchantment.*` 段 | 同上 |
| 让服务端吃下 | `ReloadableServerResources` 重载 | `/reload` 或 reload 后自动触发 |
| 互斥 tag 追加 | `data/minecraft/tags/enchantment/exclusive_set/damage.json`（`replace: false`，只列自己的） | 同上 |

**已知坑（写进验收）**：

- `/reload` 后**已附在物品上的附魔不会重算**——组件里存的是 `Holder<Enchantment>`，数据换了但物品没变。改数值后要重新拿一件才能看到差异，测试时别误判成「没生效」。
- 生成路径若落在 `config/` 下而不是 mod 的 `data/`，服务端读不到。生成物必须进 **datapack 源目录**（`src/main/resources/data/redtale_project/enchantment/`），config 只是「源稿」。这一点决定 `/redtale reload` 到底能不能热更附魔：**能改 config，但改不到已打包的 resources**，所以热更路径要落到**世界目录的 datapack**（`world/datapacks/redtale_generated/`）才是真正可 reload 的。← **M4 必须先验证这条，否则 §5 整张表都是假的。**

## 6. M4 验收矩阵

每条都能一个人一台测试服勾完，不依赖客户端。

| # | 验收项 | 怎么验 | 通过标准 |
|---|---|---|---|
| V1 | effect 类型注册成功 | 启动日志 + `/data` 无报错 | `redtale_project:scripted` 在 `ENCHANTMENT_ENTITY_EFFECT_TYPE` 里可查 |
| V2 | schema 生成合法 JSON | `/redtale reload` 后看生成文件 | 无 `Failed to parse` / `Unknown registry element` |
| V3 | 进注册表 | `/enchant @s redtale_project:super_sharpness 3` | 物品拿到 III 级，tooltip 显示中文名 |
| V4 | 附魔台可出 | 30 级书 + 剑，刷 20 次 | 至少 1 次出（不出则调 `weight` / `min_cost`） |
| V5 | 铁砧可合 | 两本 I 级合成 | 得到 II 级，扣对等级 |
| V6 | 砂轮可去 | 砂轮放附魔剑 | 附魔消失、返经验 |
| V7 | 互斥生效 | 已附锋利 V 的剑附超级锋利 | 拒绝 / 附上则锋利消失，**不能并存** |
| V8 | 纯数值附魔真加伤害 | 白板剑 vs 附魔剑打同一种怪，`/redtale attr` 对账 | 差值 = `linear` 算出的值（含 L2 前的基础伤害） |
| V9 | `scripted` 能跑脚本 | 打怪触发 `enchants/soul_reap` | 脚本日志出现 + 玩家回血 |
| V10 | 脚本缺失不崩 | 故意写不存在的 `script` | 一条 WARN、附魔仍在、不崩服 |
| V11 | 加第 N 个附魔只写 JSON5 | 新写一个 `.json5` → `/redtale reload` | 生效，**全程没编译** |

**M4 出口 = V1~V11 全绿。** 其中 V11 是「接口成立」的唯一硬指标，其余是「接口没写错」。

## 7. 与已装 mod 的边界

| 对象 | 关系 | 处理 |
|---|---|---|
| `enchantmentdisabler` | 只做减法 | 不启用上限提升；仅在要禁原版附魔时填 `disabledEnchantments` |
| 原版附魔台/铁砧/砂轮 | 天然一致 | 不自建附魔 UI，除非 owo 面板做「附魔预览」（D30，非 M4） |
| 原版可获取性 tag | `in_enchanting_table` / `tradeable` / `on_random_loot` / `on_mob_spawn_equipment` / `on_traded_equipment` | 想让村民卖 / 战利品出，**必须**把 id 追加进对应 tag；缺省只保证 `/enchant` 与铁砧。tag 真实名以 vanilla client jar 的 `data/minecraft/tags/enchantment/` 为准（**M4 核对项**） |
| `#minecraft:exclusive_set/damage` | 原版 tag | 我们只**追加**，`replace: false`；绝不重写整个文件 |
| `spell_engine` / `spell_power` | 无交集 | 不注册同义附魔，见 D31 |

## 8. 风险（M4 开工先干掉前两条）

| # | 风险 | 兜底 |
|---|---|---|
| R1 | `BuiltInRegistries.ENCHANTMENT_ENTITY_EFFECT_TYPE` 不能用 `RegisterEvent` 注册 | 退回 `Mixin` 进 `EnchantmentEntityEffect.bootstrap`，或改用原版现成组件 + 脚本层轮询（性能差） |
| R2 | 生成物写不到「可 reload 的 datapack」位置 | 生成到 `world/datapacks/redtale_generated/` + 重启一次，放弃附魔热更（可接受，M4 只要求能生成） |
| R3 | 附魔台刷不出（`weight` 被原版 cost 参数压住） | 调 `min_cost` / `max_cost`，或只用 `/enchant` 与铁砧发放（M4 允许） |
| R4 | 与 `apotheosis` 类附魔 mod 冲突 | 当前未装，先在 `compat.json5` 留白名单空位（D31 同款机制） |
