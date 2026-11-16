# 数值管线与兼容设计（对应决策 D / E）

> 状态：草案 v1，2026-11-15。所有「证据」列都指回本机可查的文件，标「待验证」的是我还没实测的。

## 0. 一句话结论

**不要自建一套伤害结算。** 把装备数值落到「原生 Attribute + 原生附魔组件」上，我们只在两处介入：
进场伤害的**乘区层**、攻速的**饱和曲线**。所有闸门可配，超出部分走递减而不是硬截断。

---

## 1. 证据：现在服上的东西是怎么加伤害的

### 1.1 原版锋利（1.21.1，实测自 server jar）

`data/minecraft/enchantment/sharpness.json`：

```json
{
  "anvil_cost": 1,
  "effects": {
    "minecraft:damage": [
      { "effect": { "type": "minecraft:add",
                    "value": { "type": "minecraft:linear", "base": 1.0, "per_level_above_first": 0.5 } } }
    ]
  },
  "exclusive_set": "#minecraft:exclusive_set/damage",
  "max_level": 5,
  "slots": ["mainhand"],
  "supported_items": "#minecraft:enchantable/sharp_weapon",
  "weight": 10
}
```

三条可直接用的结论：

1. 附魔加成是 **AddValue 进平加池**，锋利 V = +3，不是乘算。三个伤害类附魔（锋利/亡灵杀手/节肢杀手）由 `#minecraft:exclusive_set/damage` 强制互斥，**原版自己就防了叠加爆炸**。
2. 我们的「超级锋利」只要用同一个 `minecraft:damage` 组件 + 同一个互斥 tag，就自动进同一条池子、自动跟锋利互斥、自动出现在 tooltip、自动被铁砧和砂轮正确处理。**零兼容代码。**
3. 附魔数据全在 datapack，可以启动时生成 —— 这正是 D5 要的形态。

### 1.2 `spell_power` 1.6.0（服上已有）

注册了 19 个属性，`assets/spell_power/lang/en_us.json` 实测：

```
spell_power.generic            法术强度（通用）
spell_power.{arcane,fire,frost,lightning,soul,air,water,earth,blood,nature,shadow,holy,unholy}
spell_power.healing            治疗强度
spell_power.critical_chance    法术暴击率
spell_power.critical_damage    法术暴击伤害
spell_power.haste              法术急速
spell_power.resistance.generic 法术抗性
```

**这套基本就是 MMOItems 的 stats 体系**（暴击率 / 暴击伤害 / 治疗强度 / 各系强度）。

→ **决策（2026-11-15 修正）：`spell_power` 不是我们的前置。属性全部自建，注册在 `redtale_project:` 下。** 上面这张表只当「清单参考」——用来对齐我们该做哪些属性，**不引用它的类、不读它的 Attribute、不写进依赖**。

→ 后果要说明白：整合包里同时有 `spell_power` 时，玩家面板会出现两套（我们的「暴击率」和它的「法术暴击率」）。处理方式见 §1.2.1。

#### 1.2.1 与 spell_power 共存：可选桥接，默认关

既然它可能还在整合包里（正式服现在装着），就不能装作没看见，但也不能依赖它。

```
默认（bridge = off）：
  我们的 critical_chance 是 redtale_project:critical_chance
  与 spell_power:critical_chance 互不相干，两套属性各自生效

可选（bridge = on，配置开关）：
  检测到 spell_power 存在时，把我们这几个语义重合的属性
  改为向它的 Attribute 挂 modifier，面板只显示一行
  适用：critical_chance / critical_damage / healing / haste / 13 系法强
  不适用：它没有的（护甲穿透、生命偷取、元素抗性细分…）仍归我们
```

三条约束：

1. **桥接是配置项，不是代码路径依赖**：`bridge=off` 时我们的 jar 完全不 import 它的任何类（用反射或 `Registries.ATTRIBUTE.get()` 按 id 字符串查，查不到就用自己注册的）。
2. **配置里只写逻辑名**（`critical_chance`），永不写 `spell_power:critical_chance`；完整 id 由 `StatResolver` 在运行期决定。
3. **不因为它而改变存档格式**：物品上存的是逻辑名 + 数值，换不换桥接都不影响已发出的装备。

这条设计的价值在于：你哪天把 `spell_power` 从整合包删掉，我们的装备一件都不会失效，只是面板从「一套」变回「我们自己的那套」。



### 1.3 AttributeFix 21.1.3：它把闸门拆了

jar 里只有 5 个类，做的是移除 `RangedAttribute` 的上限钳制。

原版 1.21.1 的 `generic.attack_speed` 是 `RangedAttribute(4.0, 0.0, 1024.0)`；装了 AttributeFix 后上限不再拦。

**这既是好事也是坑**：堆到 1024 就是每 0.001 秒一刀。所以「防巨量数值」不能指望原版，必须我们自己设闸门。

### 1.4 攻速的真实机制

```
base = 4.0（空手，次/秒）
剑的 modifier = -2.4  → 实际 1.6 次/秒
攻击冷却 tick = 20 / attack_speed     （1.6 → 12.5 tick）
```

**修正（2026-11-15，Aki 指出后重查）**：原版 `minecraft:haste` **不直接改 `attack_speed` 属性** —— 1.20.1 里它硬编码在 `Player.getDigSpeed()`，1.21.1 里它只加 `minecraft:player.block_break_speed`。Aki 在 1.20.1 服上确实观察到「急迫 → 攻速」，我按 SRG 名重扫了两套包，找到了体感的实际来源（见 §4.2）。结论：**急迫本身不动攻速，但你们服上有东西把「急迫」当攻速卖**。

---

## 2. 为什么不能覆盖式改写伤害

服上 228 个 mod，Iron's Spells、Cataclysm、Mowzie's、Spellblade 等各有自己的伤害入口。NeoForge 的 `LivingIncomingDamageEvent` 是**叠加式**的：大家依次加减乘，谁都不能「重置」。

所以我们的定位只能是：

```
我们的层 = 在别人算完之后，再乘一次（且乘区有上限）
```

一旦我们试图 `event.setAmount(我们算的)`，就会把前面所有 mod 的加成抹掉，立刻和一堆 mod 打架。

---

## 3. 三层模型

```
L0  基础值    原生 attack_damage 属性 + 原生 minecraft:damage 附魔 + 药水/效果
              （原版已经算好，我们不动）
L1  平加池    我们发放的 AttributeModifier（带固定 id，可整件卸下）
              上限由「每属性可发放总量」控制
L2  乘区层    LivingIncomingDamageEvent 里乘
              percent 池：所有百分比加成先相加，再整体钳制
              条件池：最多 condCount 个，每个单独钳制
L3  天花板    final clamp
```

结算函数（服务端与 tooltip 共用同一份实现）：

```java
double settle(double base, double sumPercent, List<Double> conds, Caps caps) {
    // caps 默认全 0 = 关闭（D16）。0 若直接喂给 Math.min 会把结果归零，
    // 所以每一处都**必须先判 limited**——漏一处 = 全服伤害恒 0。真实现见 core/math/Settle.java。
    double p = sumPercent;
    if (caps.percentLimited()) p = Math.min(p, caps.percentCap);

    double condProduct = 1.0;
    int applied = 0;
    for (double rawCond : conds) {
        if (caps.countLimited() && applied >= caps.condCount) break;   // 按「实际应用数」计，不是下标
        if (rawCond == 0.0) continue;                                   // 0 值不计入 condCount
        double cond = caps.condLimited() ? Math.min(rawCond, caps.condCap) : rawCond;
        condProduct *= (1.0 + cond);                                    // 条件乘区也是 (1+x)，不是 x
        applied++;
    }

    double out = base * (1.0 + p) * condProduct;
    if (caps.damageLimited()) out = Math.min(out, caps.damageCap);
    return out;
}
```

关键点：

- `sumPercent` 是**先加后乘**，不是连乘。10 个 +20% 是 +200%，不是 6.19 倍。
- 条件乘区是 **(1 + cond) 连乘**（+20% 条件 = ×1.2），不是把 cond 当乘数直接连乘。两者差一个 1，写反了「+20% 背刺」会变成 ×0.2。
- 条件乘区个数默认**不限**（`condCount: 0`）；要收紧时填数字，计数口径是「实际应用数」（0 值不占名额），不是列表下标。
- 全部钳制**可配且默认关**，`/redtale reload` 生效。

### 为什么不做硬截断

硬截断会让玩家「堆到顶就白堆」，体验差且不可解释。改为**递减增益**：

```
有效值 = cap * (1 - exp(-raw / cap))
```

raw = cap 时拿到 63%，raw = 3×cap 时拿到 95%，永远不超 cap，但堆了总有收益。这是攻速和百分比池共用的曲线，参数可配。

---

## 4. 攻速：一个 mixin 同时覆盖原版与 BetterCombat

### 4.1 证据：BetterCombat 2.4.0 **已经在正式服上**

`net/bettercombat/logic/PlayerAttackHelper#getAttackCooldownTicksCapped` 的字节码只有四步：

```
invokevirtual  Player.getCurrentItemAttackStrengthDelay()   // 原版：20 / attack_speed
getstatic      ServerConfig.attack_interval_cap             // 配置：最少几 tick
invokestatic   Math.max(float, float)
freturn
```

`config/bettercombat/server.json5` 实际值：

| 配置 | 值 | 含义 |
|---|---|---|
| `attack_interval_cap` | **2** | 两次攻击最少 2 tick → 每秒最多 10 次 |
| `allow_fast_attacks` | **true** | **绕过 `LivingEntity` 受伤无敌帧** |
| `dual_wielding_attack_speed_multiplier` | **1.2** | 双持时攻速 ×1.2 |
| `upswing_multiplier` | 0.5 | 前摇占冷却的比例 |
| `combo_reset_rate` | 3.0 | 连击在 `3×冷却` 空闲后重置 |

三条结论：

1. **BetterCombat 不改攻速计算**，只是给原版结果套一个 `max()` 下限。
2. 所以 **mixin `Player#getCurrentItemAttackStrengthDelay` 一个点，同时覆盖「原版」与「BetterCombat」两种环境** —— BetterCombat 拿到的就是已经处理过的值，不需要第二套代码。
3. `allow_fast_attacks = true` 是真正危险的一条：**没有无敌帧兜底，攻速直接线性放大 DPS**。攻速翻倍 = DPS 翻倍，没有边际递减。攻速是本项目最需要盯的属性。

### 4.2 「急迫→攻速」重查：SRG 解码 + 全包扫描

上一版我扫 1.20.1 时用了 `DIG_SPEED` 这个字符串，扫不到东西 —— **1.20.1 Forge 的字节码里字段是 SRG 名（`f_19598_`），不是官方名**，所以那次扫描无效。这次用 Mojang 官方映射 + Forge `joined.tsrg` 做了对照：

| SRG | 官方名 | 用途 |
|---|---|---|
| `f_19598_`（`MobEffects`） | **`DIG_SPEED`** | 急迫本体 |
| `f_22283_`（`Attributes`） | **`ATTACK_SPEED`** | 攻速属性 |
| `f_22281_` / `f_22282_` | `ATTACK_DAMAGE` / `ATTACK_KNOCKBACK` | 伤害 / 击退 |

（解码依据：`server.txt` 官方映射第 31686 行 `MobEffects` 块、第 34451 行 `Attributes` 块，与 `joined.tsrg` 的 `bfc/c`、`bhg/h` 交叉比对。）

重扫结果（1.20.1 服 393 jar）：

| 扫描 | 结果 |
|---|---|
| 引用 `ATTACK_SPEED` 的类 | **206** 个（武器 / 饰品 / 效果注册表，正常） |
| 同时引用 `DIG_SPEED` 与 `ATTACK_SPEED` 的类 | **2** 个：`EnigmaticLegacy.TheCube`（一件物品同时给急迫和攻速）、`dungeonsdelight.DDEffects`（效果注册表，只是并列声明） |
| 按等级把急迫换算成攻速的代码 | **没有** |
| 1.21.1 服（228 jar，官方名字节码）同类扫描 | **0** 个 |

所以：**代码里没有「急迫 → 攻速」这个公式。但 Aki 的体感有确切来源，我找到了两条。**

#### 4.2.1 来源一：SimplySwords 的 Ferocity 剑（几乎肯定是它）

1.20.1 的 `HasteSwordItem`（Twisted Blade / Ferocity）命中时给目标堆 `MobEffects.DIG_SPEED`，**最多 15 层**。它的 tooltip 原文是：

```
item.simplyswords.ferocitysworditem.tooltip2 = Chance on hit to increase your attack
item.simplyswords.ferocitysworditem.tooltip3 = speed, stacking up to 15 times.
```

也就是说：**这把武器把「急迫」当作「攻速」在卖。** 玩家看到 buff 栏里是「急迫」，tooltip 写的是 attack speed —— 这就是「急迫加攻速」在你们服上的来历。

更硬的证据在 1.21.1 版：作者把这个机制改成了独立效果 `ImplicitHasteEffect`，名字还叫「Implicit Haste」，但代码是：

```java
addAttributeModifier(Attributes.ATTACK_SPEED,
    ResourceLocation.fromNamespaceAndPath("simplyswords", "implicit_attack_speed"),
    0.10, ADD_MULTIPLIED_TOTAL);      // 真·+10% 攻速
```

**作者自己承认了「急迫 = 攻速」这个设定**，1.20.1 用急迫堆叠实现，1.21.1 改成真的攻速效果。所以 Aki 的记忆没错，是我上一版的扫描方法错了。

#### 4.2.2 来源二：咖啡（这条是真的属性修饰符）

Farmer's Respite 的 `CaffeinatedEffect`（1.20.1 2.1.2 与 1.21.1 3.0.1 字节码一致）：

```java
addAttributeModifier(Attributes.MOVEMENT_SPEED, "farmersrespite:speed",       0.10, ADD_MULTIPLIED_TOTAL);
addAttributeModifier(Attributes.ATTACK_SPEED,   "farmersrespite:attack_speed", 0.20, ADD_MULTIPLIED_TOTAL);
```

另发现 Youkai's Homecoming 的 `TeaEffect`：`ATTACK_SPEED +5%`（`MULTIPLY_BASE`）。

**这就解释了「咖啡 + 急迫叠加更高攻速」**：咖啡的 +20% 是实打实进属性池的，如果同时握 Ferocity 剑，急迫层数在 1.20.1 只加速挖掘、但玩家按 tooltip 理解成攻速 —— 观感上就是「两个都叠了」。1.21.1 版作者把急迫改成真攻速后，这条叠加就变成真的了。

> 想在你们自己的服上一次性定论（10 秒）：喝咖啡前后各跑一次 `/attribute @s minecraft:generic.attack_speed get`，再单独喝急迫药水跑一次。三个数一比，谁在动攻速一目了然。1.20.1 与 1.21.1 的 id 都是 `minecraft:generic.attack_speed`。

> **更正（2026-11-15 三查后）**：上一段里「1.20.1 的 `HasteSwordItem` 把急迫换算成攻速」这个说法**在字节码里找不到支撑** —— `HasteSwordItem` 只引用 `MobEffects.HASTE`，没有任何 `ATTACK_SPEED` 引用。准确表述是：1.20.1 **语境上**把急迫当攻速卖（tooltip + buff 栏），1.21.1 才用 `ImplicitHasteEffect` 做成真属性。所以「1.20.1 上急迫真的提速」要么来自第三方转换器，要么是观感。**不影响结论**：我们不猜别人，自己声明（4.2.3），Aki 已拍板按 0.10/级开启（D19）。

#### 4.2.3 决定：把「攻速来源」做成声明式规则（D18 + D19）

既然「急迫算不算攻速」在你们服上是**玩法口径**而非代码事实，我们就不去猜别人的实现，改成**自己声明**：

```json5
// config/redtale_project/attack_speed.json5
{
  // 急迫每级提供多少攻速（D19：默认 0.10 = 保留 1.20.1 玩法；填 0 退回纯原版）
  haste_attack_speed_per_level: 0.10,

  // 与咖啡因同类的「效果 → 攻速」映射，可继续加
  effect_attack_speed: {
    "minecraft:haste":            { per_level: 0.0 },   // 已由上面的字段覆盖，二选一
    "farmersrespite:caffeinated": { flat: 0.0 },        // 它自己已经加了，别重复加
  },

  // 饱和（0 = 关闭，D19 默认关闭）
  soft_cap: 0.0,

  // 物理地板：冷却最短多少 tick（防除零，不是平衡阀）
  min_attack_delay_ticks: 1.0,
}
```

**默认值（2026-11-15 Aki 拍板，D19）**：`haste_attack_speed_per_level = 0.10` 且 `soft_cap = 0`，即「急迫 I +10%、II +20% … VIII +80%」并且**不饱和**。理由是这条链在 1.20.1 已经成型（康普茶供时长 + 星芒抬等级 → 长时间急迫 VIII），属于该服标志性手感，不是要修掉的 bug。外部来源（咖啡 / 茶 / Ferocity / 双持）仍保持 0，避免重复计。它与咖啡的 +20% 直接在属性池里相加：

```
攻速倍率 = 1 + 0.20(咖啡) + 0.10×急迫等级 + 其它 ADD_MULTIPLIED_TOTAL
例：急迫 II + 咖啡 = 1 + 0.20 + 0.20 = 1.40 → 1.6 次/秒的剑变 2.24 次/秒
例：急迫 VIII + Ferocity 满层 + 咖啡 = 1 + 0.80 + 1.50 + 0.20 = 3.50×
```

最后那个 3.50× 就是这套玩法的天花板：`allow_fast_attacks = true` 下它等于 DPS ×3.5。**我们不砍结算层**，只保证它可被看见（`/redtale attr`）与被关掉（配置改 0），真正的阀门在投放层（药水/食物/剑的获取难度）。

三条实现约束：

1. **用 `ADD_MULTIPLIED_TOTAL` 加进 `ATTACK_SPEED` 属性**，不要自己乘冷却 —— 这样其它 mod 读到的数值和我们一致，`/attribute` 也看得见。
2. **modifier id 固定**（`redtale_project:haste_attack_speed`），急迫等级变化时先移除再加，不能叠加泄漏。
3. **绝不与已有来源重复计**：检测到 `farmersrespite` 已给攻速就不再按 `effect_attack_speed` 加一遍（默认表里已经置 0 就是为此）。

#### 4.2.4 配套：`/redtale attr` 把攻速拆开给你看

以后再遇到「到底是谁在加攻速」，不靠猜：

```
/redtale attr attack_speed
  基础            4.00
  主手武器        -2.40   (redtale_project:longsword)
  咖啡因          +0.32   (farmersrespite:attack_speed, +20%)
  急迫 II         +0.32   (redtale_project:haste_attack_speed, 规则)
  BetterCombat 双持 +0.32  (bettercombat:dual_wielding)
  ────────────────────────
  合计            2.56  → 7.8 tick / 次
```

这个命令 M1 就要做出来，比任何文档都省事 —— 加伤害的那些 mod 也一样能这么拆（`/redtale attr attack_damage`）。

### 4.3 策略：默认不饱和，只留物理地板（D19 + D16）

按你的意见**不设平衡上限**：`soft_cap` 默认 0，急迫 0.10/级全开。**唯一保留的是防除零的物理地板**，因为 `getAttackCooldownProgress()` 是 `clamp(ticker / delay, 0, 1)`：

```java
// mixin: Player#getCurrentItemAttackStrengthDelay  (@Inject at RETURN, cancellable)
double raw = 20.0 / originalDelay;                   // 还原成「次/秒」
double eff = (softCap <= 0.0) ? raw
           : softCap * (1.0 - Math.exp(-raw / softCap));   // softCap = 0 → 关闭
eff = Math.min(eff, 20.0 / minAttackDelayTicks);     // 地板：默认 1 tick → 最多 20 次/秒
return (float) (20.0 / eff);
```

- `softCap = 0` → 饱和曲线不存在（默认）。
- `minAttackDelayTicks = 1.0`（默认）→ 任何来源的攻速最多 20 次/秒。**没有这条**，delay 会算成 0 或负数，原版除零后冷却恒满 = 每 tick 出手，配合 `allow_fast_attacks = true` 直接变成「1 秒 20 刀」。这不是平衡问题，是 NaN/除零问题。
- 想更保守可设 2.0（= BetterCombat 自己的 `attack_interval_cap`），想放开到极限可设 0.5。

真要用饱和曲线（`softCap = 4.0`）时的效果：raw 8.0 → eff 3.45，raw 1024 → eff 4.00。

还有个现成的兜底：BetterCombat 自己的 `attack_interval_cap = 2`，装了它就最多每秒 10 次。但它**不在测试服里**，所以不能指望。

---

## 5. 显示：武器上写什么（D20，2026-11-15 Aki 定稿）

**默认只写「单次伤害」和「攻速」，DPS 不写进主视图**；想要 DPS / 更多细分的人，在**客户端**自己切换。

| 行 | 默认可见 | 来源 | 实现 |
|---|---|---|---|
| `+7 攻击伤害` | ✅ | 原生属性 modifier | 原版自动（`ItemAttributeModifiers` 组件） |
| `+12% 暴击率` | ✅ | `redtale_project:critical_strike_chance` modifier | 原版自动（也是属性） |
| `护甲穿透 +15%` | ✅ | 自建属性 | `ItemTooltipEvent` 追加 |
| `≈ 12.4 /次` | ✅ | 结算结果 | `ItemTooltipEvent` 追加，用**同一个 `settle()`** |
| `攻速 3.4 tick · 5.9 次/秒` | ✅（小字，灰色） | `getCurrentItemAttackStrengthDelay` 实际值 | 同上 |
| `≈ 73.2 DPS` | ⬜ 客户端开关，默认 **关** | 单次 × 次数 | 同上，仅在开关打开时追加 |

三条理由（写下来免得以后又吵）：

1. **单次伤害是玩家能对上账的数**——打出来的黄字就是它。DPS 是推导量，目标换一只就变，写死会天天被质疑。
2. **攻速必须写**。D19 让攻速能到 3.7 倍，「12.4」不配攻速就是误导；写 tick 而不是「快/很快」是因为 tick 是服务器实际计算的单位。
3. **DPS 交给客户端**是权限问题：显示什么不该由服务端强迫，也不该为不同 UI 尺寸维护多套排版。

配置（`client.json5`，纯客户端，Cloth Config 已在 D11 白名单）：

```json5
{
  tooltip: {
    show_single_hit: true,
    show_attack_speed: true,
    show_dps: false,          // 默认关，玩家自己开
    show_attribute_breakdown: false,  // 展开显示每个来源（等同 /redtale attr）
    assume_target: "dummy"    // DPS 预览的假想木桩，可选 dummy / player / undead
  }
}
```

### 5.1 效果类 tooltip：必须自己解释，不能指望原版

D19 把急迫接成攻速之后，出现一个必须补的漏洞：**原版急迫的 tooltip 只写「挖掘速度 +20%」，玩家不会知道它还给了攻速**。不解释就等着被当成外挂或 bug。

做法：`EffectTooltipEvent`（客户端）在效果描述后追加一行，数值从 `attack_speed.json5` 与当前等级现算：

```
急迫 II
挖掘速度 +40%
攻击速度 +20%（赤物语规则）      ← 我们追加，等级变化实时变
```

规范：

1. **效果名与数值都写清**，不要写「攻速提升」这类模糊话。
2. 后缀统一写 **「赤物语规则」**，与上游 mod 自带的描述区分开（玩家至少知道该找谁）。
3. **只在我们真的改了才追加**：`haste_attack_speed_per_level = 0` 时这行不出现，退回纯原版文案。
4. 同样规则适用于 B&C 4.5.0 的 `Raging`、SimplySwords 的 `Ferocity`——不为它们写文案（那是别人的效果），但 `/redtale attr` 里会如实拆出来。

> 命名纪律：项目中文名 **赤物语**（英文 Redtale），**不要写成「红物语」**。tooltip、配置注释、日志、README 一律用「赤物语」。

DPS 预览必须满足：
- 用**当前持有者**的属性算（客户端拿得到，属性本来就同步）。
- 算不到的项（目标护甲、抗性）用「假想木桩」并在行尾标 `*`，tooltip 底部一行小字说明。
- **显示公式与结算公式是同一个函数**，否则会出现「写着 12.4 打出 9」。这条写成硬约束，代码里 settle() 只允许有一个实现。

---

## 6. 与原版 / 其它 mod 的冲突面（如实列）

实测：扫了正式服 228 个 jar 的 class 常量池，按事件类名统计引用方：

| 事件 / 属性 | 引用它的 mod 数 | 谁 |
|---|---|---|
| `LivingIncomingDamageEvent` | **12** | spell_engine、Cataclysm、Twilight Forest、Create、Bumblezone、FarmersDelight、KubeJS… |
| `LivingDamageEvent` | **19** | 上面大部分 + artifacts、supplementaries、CustomNPCs、balm… |
| `CriticalHitEvent` | **1** | 只有 Cataclysm |
| `generic.attack_speed` | **4** | rogues（武器）、SimplyTooltips（显示）、Armourers Workshop（皮肤）、RecurrentComplex |

三条推论：

1. **12~19 个 mod 在同一事件里加减乘** → 再次确认「不能 `setAmount` 覆盖」，否则等于把这一堆全抹掉。
2. **`CriticalHitEvent` 只有 1 个 mod 用** → 近战暴击走这个入口，冲突面极小。（原计划想自己在 `LivingIncomingDamageEvent` 里 roll，用 `CriticalHitEvent` 更干净。）
3. **`attack_speed` 只有 4 个，真正发属性的只有 rogues** → 攻速饱和 mixin 的实际影响面很小，可以放心做。

其余判断：

| 情况 | 会不会打架 | 处理 |
|---|---|---|
| 别的 mod 加 `attack_damage` 属性 | 不会 | 同在 L0/L1 池子里相加 |
| 别的 mod 加 `minecraft:damage` 附魔 | 不会 | 同一平加池 |
| 别的 mod 自己算伤害（Iron's Spells 等） | 部分 | 它们走自己的入口，我们只在事件里乘，管不到也不该管 |
| 别的 mod 加 `attack_speed` | 会 | 我们的饱和会一起收敛它们；`attrCap` 只管我们自己发的 |
| AttributeFix | 依赖 | 它拆了原版上限，我们才有必要自建闸门 |
| **BetterCombat 2.4.0** | **会**（已装） | 它 `setAmount` 伤害、定义武器 hitbox、给攻击间隔加下限；按 §12 对接 |
| 硬核 mod 用 `setAmount` 覆盖 | 有可能 | 事件顺序决定谁最后说话，需要实测（列入 M1 冲突用例） |


---

## 7. 数值控制：默认不设上限，只留异常保护

先回答「那 200% 和 500 是什么」：

| 我原来的默认 | 是什么 | 现在 |
|---|---|---|
| `percentCap = 2.0` | **百分比加成相加后的上限**。比如堆了 10 个 +30% = +300%，会被砍回 +200% | **0 = 关闭** |
| `damageCap = 500.0` | **单次伤害的绝对天花板**，超过部分直接丢掉 | **0 = 关闭** |

你判断得对，这两个是平衡上限，不是安全阀。去掉。

### 7.1 不设上限的真实风险不在平衡，在这三件

1. **意外叠加**：条件乘区连乘、某个 mod 的 bug、附魔互斥漏配 —— 可能一刀几十万。这属于工程事故，不是玩家变强。
2. **投放不可逆**：装备发出去之后再收紧，就得回改已发出的物品（`/data modify` 或版本迁移）。**这才是最贵的**。
3. **显示与日志炸裂**：数字太长、科学计数法、排序错乱。

### 7.2 所以闸门挪到「投放层」，不去砍「结算层」

| 层 | 做什么 | 谁控制 |
|---|---|---|
| **投放** | 每件装备的 base / spread / 每级成长、套装加成、宝石数值 | 配置文件，改完 reload |
| **结算** | 只做防溢出：负数归零、超 `1e9` 硬顶、超阈值记日志 | 代码里 3 行，不参与平衡 |
| **观测** | 超过阈值的伤害写日志（采样），方便发现「哪件装备异常」 | 配置开关 |

这样你想要「数值高」就调投放层的数字，结算层永远不偷偷砍你的伤害。

```json5
{
  // 平衡闸门：0 = 关闭。默认全关，要收紧时再填数字。
  caps: {
    percentCap: 0,          // 0 = 百分比池不限制
    condCap: 0,             // 0 = 单个条件乘区不限制
    condCount: 0,           // 0 = 条件乘区个数不限制
    damageCap: 0,           // 0 = 单次伤害不限制
    attackSpeedSoftCap: 0,  // 0 = 攻速不饱和
  },

  // 异常保护：不参与平衡，只在出事故时兜底
  sanity: {
    negativeGuard: true,     // 伤害为负 → 归零
    hardCeiling: 1.0e9,      // 真正的兜底，只有溢出才会碰到
    logThreshold: 10000.0,   // 单次伤害超过它 → 记日志，不拦
    logSampleRate: 0.1,      // 采样率，避免刷屏
  },
}
```

原则没变：**每个数字都能改，代码里不写死任何平衡值**。只是默认值从「收紧」改成「放开」。

---

## 8. 附魔（对应 E）

### 8.1 形态

自制附魔 = 生成的 `data/redtale_project/enchantment/<id>.json`，走原版 `Enchantment` 注册表。

```json5
// config/redtale_project/enchantments/super_sharpness.json5
{
  id: "super_sharpness",
  max_level: 3,
  weight: 4,
  anvil_cost: 2,
  slots: ["mainhand"],
  supported_items: "#minecraft:enchantable/sharp_weapon",
  exclusive_set: "#minecraft:exclusive_set/damage",   // 与原版锋利互斥
  effects: {
    "minecraft:damage": [
      { effect: { type: "minecraft:add",
                  value: { type: "minecraft:linear", base: 2.0, per_level_above_first: 1.0 } } }
    ]
  },
  min_cost: { base: 5, per_level_above_first: 12 },
  max_cost: { base: 25, per_level_above_first: 12 },
}
```

生成后就是**真附魔**：附魔书、附魔台、铁砧、砂轮、图书管理员交易、`/enchant` 全部天然一致，不需要我们自己实现「附魔书物品」。

> **接口细节以 `docs/ENCHANT-API.md` 为准**（D32）：30 个 effect 组件实测全表、唯一自定义组件 `redtale_project:scripted`、schema→JSON 字段映射、V1~V11 验收矩阵。本节只保留形态与互斥规则。

### 8.2 与原版的兼容

- 平加类（锋利/超级锋利）→ 同一 `minecraft:damage` 池 + 同一互斥 tag，**自动不叠加**。
- 乘算类（如果要）→ 用 `minecraft:damage` 的 `multiply` 效果类型，但**必须**配互斥，否则连乘爆炸。
- 保护类 → `minecraft:damage_protection`，同理。

### 8.3 「脚本层附魔」和「数据包附魔」的分界

| 附魔类型 | 用哪种 | 原因 |
|---|---|---|
| 纯数值（锋利类、保护类、效率类） | **数据包** | 原版全链路免费，零兼容成本 |
| 触发式（命中流血、击杀回血、受伤反弹） | **脚本层**（effect/trigger/condition） | 原版附魔组件表达不了 |
| 混合 | 数据包给数值 + 脚本层给触发 | 两者可以并存于同一附魔 JSON（脚本部分用我们的组件） |

EcoEnchants 103 个附魔之所以全走脚本，是因为 Bukkit 没有原版附魔数据包这套东西。我们**有**，所以能省掉一大半工作。

---

## 9. 每轮可验证的验收点（给 S7 队列用）

1. `settle()` 单测：给定 base/percent/conds，输出可复现，边界（超 cap、负数、NaN）有断言。
2. 附魔生成器：产出 JSON 能被 1.21.1 数据包加载（`/reload` 无报错），锋利与超级锋利在铁砧里互斥。
3. 攻速 mixin：`attackSpeedSoftCap=4.0` 时，`raw=1024` 的玩家实际冷却 = 5 tick（用 `/attribute` 临时加属性实测）。
4. tooltip：DPS 预览值与实打伤害误差 ≤ 5%（对同一只靶子连打 20 次取均值）。
5. 冲突用例：与 AttributeFix / spell_power（`bridge=off` 与 `on` 各测一次）/ 任一自带伤害入口的 mod 同场，数值不出现负伤害或溢出。

## 10. 待验证清单

- [ ] 自建属性注册后，`/attribute` 能否正常读写、tooltip 是否正确显示中文名（需要 lang 条目）。
- [ ] NeoForge 21.1.257 的 `CriticalHitEvent` 是否仍可用作暴击入口（还是该在 `LivingIncomingDamageEvent` 自己 roll）。
- [ ] 攻速 mixin 的最佳注入点：`getCurrentItemAttackStrengthDelay()` vs `attackStrengthTicker` 累加处（后者影响 `getAttackStrengthScale` 的动画）。
- [ ] 事件优先级：是否需要在 `EventPriority.LOWEST` 才能让我们的乘区作用在所有 mod 之后。

---

## 11. BetterCombat 联动（已装，但不作前置）

定位：**运行期检测，代码零 import**。`ModList.get().isLoaded("bettercombat")` 为真则走对接分支，为假走原版分支。

### 11.1 六个接入点

| 接入点 | BetterCombat 做什么 | 我们怎么接 |
|---|---|---|
| **攻击间隔** | `max(原版 getCurrentItemAttackStrengthDelay(), attack_interval_cap)` | mixin 原版方法 → 它自动继承，**不需要第二套代码** |
| **伤害** | 武器 `damage_multiplier` 乘完再 `setAmount`，发生在事件之前 | 我们在 `LivingIncomingDamageEvent` 上乘，接在它之后；绝不覆盖 |
| **双持** | 攻速 ×1.2（属性 modifier），主/副手伤害倍率各 1.0 | 属性层面自然参与，无需特殊处理 |
| **横扫** | `reworked_sweeping`：多目标递减，最多 −50%（`reworked_sweeping_maximum_damage_penalty`） | 我们的条件乘区必须在它**之后**，否则会把衰减值再放大 |
| **命中判定** | 武器 hitbox 形状（`angle`/`range`）由 `weapon_attributes` 定义，**不是原版 AABB** | 我们的「攻击范围」属性要映射进它的 `range_multiplier`，只改 `entity_interaction_range` 无效 |
| **姿势 / 动画** | `weapon_attributes.animation` 决定挥砍动画 | 每件武器内容必须带一个 `weapon_attributes` 引用 |

### 11.2 我们的武器必须自带 `weapon_attributes`

BetterCombat 用 `config/bettercombat/fallback_compatibility.json` 按**物品 id 正则**猜武器类型（`claymore|great_sword`、`scythe`、`halberd`…）。我们的物品 id 不会命中任何一条 → 退化成默认挥砍。

所以内容 schema 里加一个字段：

```json5
{
  id: "red_maple_longsword",
  base: "sword",                       // 我们的基底类型
  weapon_attributes: "bettercombat:claymore",   // 或 "redtale_project:longsword"
  stats: { attack_damage: 7, attack_speed: 1.6 },
}
```

**关键收益**：`weapon_attributes` 本身是 datapack registry（`data/<ns>/weapon_attributes/*.json`），**可以热加载**。所以我们自建一整套武器动作，不需要换 jar。

### 11.3 「非前置」的具体含义

| 做法 | 允许 |
|---|---|
| 代码 `import net.bettercombat.*` | ❌ |
| 编译期 `compileOnly` / `modCompileOnly` 依赖 | ✅（不打包，不进 runtime） |
| 生成 `weapon_attributes` JSON | ✅（纯数据，没装时只是没人读的文件） |
| 反射读它的 `ServerConfig` | ✅（失败就跳过，不影响启动） |
| `depend` / `required` 声明 | ❌ |

### 11.4 待验证（M1 冲突用例要覆盖）

- [ ] 我们的乘区在 `EventPriority` 的哪一档才能稳定排在 BetterCombat 的 `setAmount` 之后。
- [ ] `reworked_sweeping` 的 −50% 是在事件前还是事件后结算。
- [ ] 双持 1.2 倍到底是 attribute modifier 还是直接乘延迟（字节码里看到 `dualWieldingAttributeMap`，倾向于前者，需实测确认）。
- [ ] `attack_interval_cap = 2` 与我们的 `attackSpeedSoftCap` 同时开启时，谁先生效（应该是我们先生效，它在外层 `max`）。
- [ ] 我们自建的 `weapon_attributes` 能否被它正确加载（registry 同步走 `WeaponRegistrySync` 包）。

## 12. 兼容层：spell_power / spell_engine（D31，2026-11-15）

前提：这两个 mod 在赤物语自研上线后**大概率整体移除**，所以兼容层的目标是「今天能用、明天能干净拆掉」，不是长期共存。

### 12.1 三条原则

1. **只读不注册**：不引用它们的类，不注册同义属性；结算时按 `ResourceLocation` 查 `BuiltInRegistries.ATTRIBUTE`，
   取 `AttributeMap` 里的值当输入。拿不到就是 0，不抛异常。
2. **全部代码隔离在 `compat/` 包**，编译期零依赖（连 `compileOnly` 都不加）。删掉这个包 = 兼容结束，core 一行不动。
3. **一个总开关**：`config/redtale_project/compat.json5` 的 `spell_engine: auto|on|off`，`auto` = `ModList` 探测。

### 12.2 spec

```json5
{
  spell_engine: "auto",
  // 外部属性 → 我们的结算输入。key 是对方属性 id，value 是我们在表达式里的变量名
  external_attributes: {
    "spell_power:fire":       "ext_fire_power",
    "spell_power:frost":      "ext_frost_power",
    "spell_power:arcane":     "ext_arcane_power",
    "spell_power:healing":    "ext_healing_power",
    "spell_power:critical_chance": "ext_spell_crit_chance",
    "spell_power:critical_damage": "ext_spell_crit_damage",
    "spell_power:haste":      "ext_spell_haste",
    "spell_power:resistance.generic": "ext_spell_resistance",
  },
  // 我们的乘区只作用于这些 damage type；其余原样放行
  multiplier_damage_types: ["redtale_project:*"],
  // 外部伤害只记录不修改（默认 true）
  passthrough_external: true,
}
```

### 12.3 伤害乘区的 tag 白名单（B3 的答案）

`spell_engine` 的 `PlatformEventsImpl` 引用了 `LivingIncomingDamageEvent`，它的伤害**会**经过我们的钩子。
所以 L2 乘区必须先判来源：

```
if (!isOurDamageType(source)) { 记录(日志级别 TRACE); return; }   // 不改 amount
```

判据用 `DamageType` 的 ResourceLocation 前缀（`redtale_project:`），不用 `instanceof` 对方的类——
这样对方换了内部实现我们也不受影响。

### 12.4 明确兼容、但不接管的清单

| 对方的 | 我们的态度 |
|---|---|
| `spell_book_creation_requirement/cost`（吃原版 XP 等级） | **不动**。我们的等级独立建（Q-010 选 A），原版 XP 留给它 |
| 法术消耗 = 饥饿值（`spell_cost_exhaust_multiplier`） | 不接管。我们的 `max_mana` 只管我们自己的技能 |
| `haste_affects_cooldown` | 不干预，它自己算 |
| `bypass_iframes` | 不干预（与 BetterCombat 的 `allow_fast_attacks` 同类，各管各的） |
| 它的 19 条属性 | 只读进表达式，**不显示在我们的面板**，避免两套「火焰法术强度」 |

### 12.5 拆除检查单（等它们下线那天照做）

- [ ] 删 `compat/` 包、删 `compat.json5`
- [ ] 检查有没有内容配置还在用 `ext_*` 变量（`grep "ext_" config/`）
- [ ] 面板与 `/redtale attr` 里去掉「外部属性」那一段
- [ ] 验证：没有它们时 `AttributeMap` 读取路径不会抛（本来就在 try 里）

> 未验证项：`spell_power:resistance.*` 是分系还是单条（lang 里看到 `resistance.generic`），M1 实测再定映射表。
