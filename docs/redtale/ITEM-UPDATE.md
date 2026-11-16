# ITEM-UPDATE · 物品更新系统与统一标记（D33）

> 建立 2026-11-16（02:00 提出、08:10 定稿）· 起因：Aki 指出「`weapon_attributes` 不应有命名空间限制，什么东西都要可改」，
> 并要求「改过属性的物品要有统一 tag，像 MMOItems 一样能全服刷新」。
> 本文回答三件事：**① 那到底是不是 MMOItems 的东西 ② 限制怎么放开 ③ 更新系统怎么做才不出事**。

---

## 0. 先纠正一个事实：`weapon_attributes` 不是 MMOItems 的物品

| | MMOItems | 我们用的 `weapon_attributes` |
|---|---|---|
| 归属 | MMOItems 自己的物品模板体系 | **BetterCombat** 的 datapack registry |
| 存储位置 | `plugins/MMOItems/item/*.yml`（服务端插件配置） | `data/<ns>/weapon_attributes/<path>.json`（数据包） |
| 内容 | `attack-damage` / `attack-speed` / 技能列表 / 模型 | `range_bonus` / `two_handed` / `pose` / `category` / `attacks[]`（挥砍动画、判定盒、音效） |
| 谁读它 | MMOItems 自己 + 客户端 | BetterCombat 服务端算判定，**客户端播动画** |
| 换 jar 才生效？ | 否，重载插件即可 | 否，`/reload` 即可（**但运行期新生成的数据包要先 `/datapack enable` 一次**，R7 实测） |

两者唯一相像的地方是「都描述武器怎么打」。我原来在 T-0001 里写「只处理 `redtale_project:` 前缀」，
**不是照搬 MMOItems 的限制，是我自己加的保守阀门**——理由是数据包优先级高于 mod 内置资源，
如果我们生成 `data/bettercombat/weapon_attributes/claymore.json`，就会把 BetterCombat 自带的
claymore 定义顶掉，整合包里所有用 claymore 的物品（包括不是我们的）动作全变。

这个风险是真的，但**结论不该是「不许改」，而是「改可以，必须显式」**。已按此修改，见 §1。

---

## 1. 命名空间已放开（2026-11-16 改）

### 1.1 规则

配置文件名决定落到哪个命名空间，`:` 在 Windows 文件名里非法，用双下划线 `__`：

| 配置文件名 | 生成到 | 说明 |
|---|---|---|
| `weapon_attributes/test_sword.json5` | `data/redtale_project/weapon_attributes/test_sword.json` | 裸名 = 自家 |
| `weapon_attributes/bettercombat__claymore.json5` | `data/bettercombat/weapon_attributes/claymore.json` | **覆盖外部** |
| `weapon_attributes/simplyswords__rapid_thrust.json5` | `data/simplyswords/weapon_attributes/rapid_thrust.json` | 同上 |

- 内容侧 `weapon_attributes: "test_sword"` 与 `"redtale_project:test_sword"` **等价**（`normalizeRef` 自动补全）。
- 覆盖外部命名空间时**必打一条 WARN**：`将覆盖外部命名空间的定义 X（来源 Y）—— 所有引用该动作的物品都会受影响`。
- 外部 id **没有**对应配置文件时照旧跳过、**不告警**（用它 jar 里的内置项是常态）。
- 校验：namespace `[a-z0-9_.-]+`，path `[a-z0-9_./-]+`，禁 `..`，禁大写。

### 1.2 为什么不是「无脑全放开」

无脑放开的效果是：我们只要**引用** `bettercombat:claymore` 就会生成一份覆盖文件。
那样「引用」和「篡改」就没区别了，别人整合包的行为会因为我们写了个 `weapon_attributes: bettercombat:claymore` 而变。

现在的语义是：**引用 = 只挂组件指向它；要改 = 在配置目录里放一份同名定义。**
两者由「配置目录里有没有那个文件」区分，可审计（`git diff` 能看出来），也能在日志里留痕。

---

## 2. 物品身份的三层模型（更新系统的基础）

这是整套设计的地基。任何「物品属性怎么改」的问题，先看它落在哪一层：

| 层 | 字段 | 谁决定 | 能不能自动改 |
|---|---|---|---|
| **身份** | `content_id` | 内容定义 id | **永不改**。发布后改名 = 所有存量物品变孤儿 |
| **定义型** | `name` / `rarity` / `durability` / `weapon_attributes` / `strip_vanilla_effects` / `ATTRIBUTE_MODIFIERS` | 当前配置 + `rolled_stats` 算出 | **可以，而且应该**——改配置就该全服生效 |
| **实例型** | `rolled_stats` / `affixes` / `abilities` / `upgrade_level` | 玩家（roll 结果、强化等级） | **永不自动改**（只做「键失效清理」，见 §4.3） |

> 关键推论：**「物品更新」不是把物品整个重建**，而是「用新定义重算定义型字段，实例型字段原样搬过去」。
> 谁要是把 `rolled_stats` 一起重算了，玩家强化过的装备会一夜回到解放前——这是这类系统最经典的事故。

---

## 3. 统一标记：一直都有，只是缺两个数字

### 3.1 现状

我们**所有**自定义物品共用一个数据组件 `redtale_project:content`（`ContentData`），
这就是「统一 tag」。它比 MMOItems 的 `mmoitems-id` + `mmoitems-type` 更统一——只有一个组件，没有第二个。

`ContentData` 本轮加三个字段，把「这物品是哪一版」和「哪些值是玩家 roll 的」变成可判定的：

| 字段 | 含义 | 变化原因 | 处理方式 |
|---|---|---|---|
| `schema` | **组件结构版本**（当前 = **2**，R18 从 1 升上来加了 `sockets` / `gem_stats`） | 字段改名 / 改语义 / 删字段 | 见 §4.3：`schemaStale` 标记 + 整体重建；**没有 if 链**（新增字段全部 `optionalFieldOf` 带默认值，旧数据自动取默认） |
| `content_rev` | **这件物品基于哪一版定义生成**（取自 json5 的 `rev`） | 改了任何定义型字段 | 重建定义型字段 |
| `rolled_keys` | **哪些键是真 roll 出来的**（M2 词条系统才填，现在恒空） | roll 时写一次 | 决定迁移时「跟定义走」还是「保留玩家值」 |

**为什么不合并成一个数字**：它们的变化源完全不同。`schema` 变是我们发版、需要迁移；`content_rev` 变是内容作者调数值、
不需要迁移。混在一起会让「改了把剑的攻击力」触发一次结构迁移，纯属浪费和风险。

### 3.3 `rolled_keys` 解决的那个矛盾

「改配置全服生效」和「不许冲掉玩家 roll 的值」这两条，只看 `rolled_stats` 是**互斥**的：

- 若迁移时全量取新定义值 → 作者把基础攻击从 20 改成 22，玩家那把 roll 出 24 的神装变回 22，资产被冲。
- 若迁移时全量保留旧值 → 那改配置对存量物品完全无效，`rev` 白加，整个系统没有意义。

加一个键集就能分开判：

| 键的位置 | 语义 | 迁移行为 |
|---|---|---|
| 不在 `rolled_keys` | 定义给的确定值 | **取新定义的新值** |
| 在 `rolled_keys` | 玩家 roll 出来的 | **保留旧值** |

- 键集只增不减：一旦 roll 过就永远是实例值，哪怕作者后来把这条属性的 roll 区间删了。
- 现在（M2 之前）`rolled_keys` 恒空 → 所有键跟定义走 → **「改配置全服生效」这条现在就能测**（U1/U2 不依赖词条系统）。
- 新定义**新增的键**不在老物品的 `rolled_stats` 里，所以不会被写进去 → 不白送（U3）。

### 3.2 发布纪律（写进 CONTRACTS）

> **改任何一件物品的定义型字段 → 必须把该 json5 的 `rev` +1。**

漏加的后果是「配置改了、老物品不更新」，而且**不会报错**，只会安静地不生效。所以：
- `/redtale content list` 的摘要行已带 `rev N`，方便肉眼对。
- M2 加一条 `/redtale content check`：比对配置文件的 `rev` 与「上次 reload 记录的 rev」，**rev 没变但文件内容变了 → 打 WARN**
  （用文件 hash 缓存实现，不阻塞 reload）。

---

## 4. 刷新时机（4 个点 + 1 个兜底）

### 4.1 时机表

| # | 时机 | 覆盖面 | 钩子 | 代价 |
|---|---|---|---|---|
| ① | 登录 / 换维度 / 复活 | 在线玩家背包 41 格 | `PlayerEvent.PlayerLoggedInEvent` / `PlayerChangedDimensionEvent` / `PlayerRespawnEvent` | O(41)，可忽略 |
| ② | 打开容器 | 该容器当前内容 | `PlayerContainerEvent.Open` → `menu.slots` 遍历 | O(槽数) |
| ③ | 区块加载 | 该区块所有容器方块实体 + 掉落物 + 展示框 | `ChunkEvent.Load` → `chunk.getBlockEntitiesPos()` 逐个 `instanceof Container`；`ItemEntity` 从实体表取 | O(方块实体数)，每区块一次 |
| ④ | `/redtale reload` 之后 | **已加载**的全部世界 | 全量扫描（`ServerLevel#getAllEntities()` + 已加载区块），**分帧**：每 tick N 个区块，不卡服 | 重，需管理员显式触发 |

**兜底 ⑤：读取时惰性**。所有我们自己经手的读路径（tooltip、伤害结算、`/redtale` 命令）先调
`ItemUpgrader.ensure(stack)`。它第一件事是 `rev` 比较，相等直接返回，成本是一次 int 比较。
这样即使上面 4 个时机全漏了，玩家**看到和打出的**也永远是新值。

> 用户猜的「读取所有在玩家身上的物品」只覆盖 ①。箱子、末影箱、掉落物、展示框都在别处，靠 ②③ 补。

### 4.2 为什么没有「物品被移出容器」这个事件

原版/NeoForge **没有**「从容器取出物品」的事件。可用的只有 `ItemTossEvent`（丢出）、
`EntityItemPickupEvent`（拾取）、`PlayerContainerEvent.Open/Close`。中间那条最常走的路——
「点一下从箱子拖进背包」——在服务端只是 `AbstractContainerMenu#clicked` 里的一次 `setItem`，没有事件。

所以我们不去追那个点，而是**把迁移压在更可靠的边界上**（区块加载 + 容器打开 + 登录）。
取出后物品已经在服务端内存里，⑤ 惰性检查保证它第一次被用到时就是新的。

### 4.3 迁移动作（`ItemUpgrader.ensure` 的语义）

```
ensure(stack):
  data = stack.get(CONTENT)              // 没有 → 不是我们的物品，原样返回 UNCHANGED
  if data.schema != CURRENT_SCHEMA       // 结构迁移：打 schemaStale 标记，走下面的整体重建。
                                        // 没有 if 分支：R18 加的 sockets/gem_stats 都是 optionalFieldOf 带默认值，
                                        // 旧数据缺键自动取默认；不需要逐版本写迁移代码。
  content = 当前配置里查 data.contentId
  if content == null                     // → ORPHAN：不改任何数值，只在 tooltip 标红「内容已失效」
  if data.contentRev == content.rev      // → UNCHANGED（快路径，绝大多数物品走这里）
  重建：
    CUSTOM_NAME / RARITY / MAX_DAMAGE / weapon_attributes / PRESET_ID  ← 全取自新定义
    rolled_stats:
      for key, oldValue in data.rolledStats:
        if key 不在 content.stats:       → 丢弃，LOG.info 记一行（键名 + 旧值 + rev 变化）
        elif key 在 data.rolledKeys:     → 保留 oldValue（玩家 roll 的，不许动）
        else:                            → 取 content.stats[key]（定义型，跟新定义走）
      // 遍历的是**旧键集**，所以新定义新增的键不会凭空出现（不白送）
    ATTRIBUTE_MODIFIERS ← ItemFactory.modifiers(content, 上面算出的 rolled_stats)
    affixes / abilities: id 仍存在才留（不补新的）
    upgrade_level: 原样
    sockets: Socketer.aligned(旧孔位, 新定义孔数) —— **只补空孔、不截断**；定义改小且孔里还有宝石 → 只 WARN 并列出，等管理员 /redtale socket extract
    gem_stats: Socketer.solve(对齐后的孔序) 重算 —— 定义改了宝石数值时，这里跟着变（改配置全服生效）
  写回 content_rev = content.rev，返回 UPGRADED
```

四条不可协商的细节：

1. **`rolled_keys` 里的值一个都不动**。没 roll 过的键跟新定义走，roll 过的保留玩家值（§3.3）。
2. **不白送新键**。新定义加了 `crit_chance: 5`，老物品**不会**自动获得——因为遍历的是旧键集。
   （否则改一次配置等于给全服发了一轮免费属性。）
3. **删键要记账**。删之前 `LOG.info` 一行：`contentId / 键 / 旧值 / rev 从A到B`。玩家投诉「我属性少了」时这是唯一证据。
4. **幂等**。同一个 rev 跑一百次结果一样。批量升级中途崩服不会坏档，最多是「有些升了有些没升」，下次登录补齐。
5. **耐久上限下调要夹损伤**。`MAX_DAMAGE` 从 600 改成 400，当前损伤 580 的物品会被夹到 399（由
   `ItemFactory.applyDefinition` 处理），否则物品直接变「已损坏且无法修复」。

### 4.4 ORPHAN 的处理（内容被删）

不静默、不销毁：
- tooltip 红字「**已失效内容**（`xxx`）」，避免玩家以为是自己看错。
- 不参与伤害/护甲结算（`settle()` 读到 ORPHAN 直接返回原始值，不叠任何东西）。
- 可以正常持有/丢弃/放箱子（不破坏存档）。
- `/redtale item stats` 能按 `contentId` 统计孤儿数量，运营据此决定「补回定义」还是「发补偿收回」。

---

## 5. 同步：服务端权威，服务端推，客户端不上报

Aki 的猜想是「物品移出容器时**向服务器发包**更新」。方向反了，这里必须纠正：

**正确顺序**：服务端改 `ItemStack` 的数据组件 → 服务端主动把新状态推给客户端。

| 场景 | 做法 |
|---|---|
| 玩家背包里的物品 | `player.inventoryMenu.broadcastFullState()`（背包菜单） |
| 打开的容器里的物品 | `player.containerMenu.broadcastChanges()`，必要时 `setRemoteSlot(i, stack)` |
| 掉落物 | 改 `ItemEntity#getItem()` 后 `itemEntity.setItem(...)`（内部已标脏，随实体同步包走） |
| 方块实体容器 | `container.setChanged()` + 该 BE 的 `setChanged()`（区块保存时落盘） |

**为什么不能让客户端上报**：客户端上报「我手里这件是什么」等于把物品属性交给客户端决定，
这是复制/改属性的头号入口。我们全程服务端权威，客户端只负责显示。

> RedtaleEconomy 那个「绑定系统」如果真有客户端发包，那是它的实现方式（大概是客户端触发一次
> 服务端校验请求），不是必须的。我们不需要——服务端本来就知道自己改了什么。

---

## 6. 离线玩家：不做 playerdata 直改

`world/playerdata/*.dat` 是 NBT 压缩文件，直接批量改写要处理：并发写、备份、版本兼容、损坏回滚。
收益只有「离线玩家的物品提前更新」，而他们登录时（①）必然会被更新一次。

**结论：不做。** 与 MMOItems 同一个取舍。写在这里是为了以后有人提「为什么不顺手改一下」时有答案。

---

## 7. 覆盖不到的角落（诚实清单）

| 位置 | 谁管 | 现状 |
|---|---|---|
| 未加载区块的容器 | ③ 区块加载 | 已覆盖（加载时补） |
| 离线玩家背包 | ① 登录 | 已覆盖（登录时补） |
| Curios 饰品槽 | 需额外扫 `curios` capability | **M6 接 Curios 时补**；当前 Curios 是可选前置（D29） |
| 村民交易里预生成的物品 | 交易时从配方生成 | 生成即新 rev，无需迁移 |
| 已生成的战利品表掉落 | 开箱时生成 | 同上 |
| 玩家端缓存的 tooltip | 服务端推送 | 由 §5 保证 |
| 其他 mod 复制的物品副本 | 它们的逻辑 | 不保证（如 `lootr` 的镜像库存随原箱同步） |

---

## 8. 命令（M2 落地）

| 命令 | 权限 | 行为 |
|---|---|---|
| `/redtale item scan` | 玩家 | **只统计不改**：背包里有几件、rev 分布、孤儿几件 |
| `/redtale item upgrade` | 玩家 | 升级自己身上 + 末影箱 |
| `/redtale item upgrade all` | OP | 分帧全量（每 tick 4 区块），完成后报「扫描 N / 升级 M / 孤儿 K / 耗时 T」 |
| `/redtale item stats` | OP | 按 `contentId` 聚合：总数 / 各 rev 分布 / 孤儿 |

`scan` 与 `upgrade` 分开是刻意的：**统计是只读的，任何时候都能跑；升级会写盘，必须显式。**

---

## 9. 测试矩阵（M2 出口条件）

| # | 操作 | 期望 |
|---|---|---|
| U1 | 改 `name`，rev +1 | 登录后名字变；`rolled_stats` 不变 |
| U2 | 删一个 stat 键，rev +1 | 该键从 `rolled_stats` 移除并入日志；tooltip 不再显示；其它键值不变 |
| U3 | 加一个新 stat 键，rev +1 | 老物品**不**获得；新 `give` 的有 |
| U4 | 删整份定义 | 物品标 ORPHAN、tooltip 红字、不参与结算、不崩 |
| U5 | rev +1 但数值完全没改 | 全服零变化（幂等），且不写盘（避免无意义 IO） |
| U6 | 改定义后把物品放进箱子 → 重载区块 | 取出时已是新值 |
| U7 | 玩家离线时改定义 → 玩家登录 | 登录即更新 |
| U8 | 批量升级跑到一半 kill 服务器 | 重启后不坏档；未升级的下次登录补齐 |
| U9 | 覆盖 `bettercombat__claymore.json5` | 日志有 WARN；`/reload` 后 claymore 行为按我们的定义 |
| U10 | 背包里有 200 件自定义物品登录 | 登录延迟 < 50ms（rev 快路径） |

---

## 10. 失败与回滚

- **单件失败不中断**：`try/catch` 包住每件，计数 + 日志，继续下一件。
- **升级前不清空**：所有写都是 `stack.set(...)` 覆盖同一个组件，旧值在日志里有一行。
- **回滚靠配置**：把 json5 的 `rev` 改回去、数值改回去，再跑一次 `upgrade all` 就是回滚。
  不做「物品级快照」，那需要另存一份 NBT，成本远高于收益。
- **不做自动备份**：全服备份由运营侧（`D:\redtale-ops`）定时做，不在 mod 里重复一套。

---

## 11. 与已有决策的关系

| 决策 | 关系 |
|---|---|
| D17 内容与代码分离 | 本条是它的必要条件：能改内容不等于改了能生效 |
| D21 白板化 | 重建 `ATTRIBUTE_MODIFIERS` 时复用 `ItemFactory.modifiers()` 的同一套逻辑，不写第二份 |
| D22 tooltip 同源 | 惰性 `ensure` 保证 tooltip 读到的就是最新 |
| D32 附魔接口 | 附魔也存在物品组件里，**不在本系统范围内**（附魔由原版 registry 管，热更走 `/reload`） |
| D29 Curios 可选 | Curios 槽位扫描在 M6 补，见 §7 |

---

## 12. 落地顺序

1. **schema/rev 字段**（本轮已完成：`ContentData` + `ItemContent.rev` + `ItemFactory` 写入）。
2. **`ItemUpgrader.ensure`**（纯函数，无事件、无 IO）→ 卡 **T-0006**。
3. **`/redtale item scan`**（只读，先让运营能看见现状）→ 派单池 **C7**。
4. **登录 + 容器 + 区块 三个钩子**（事件注册，S7 独占）→ T-0006 验收后由 S7 接。
5. **`/redtale content check`**（rev 漏加检测）→ 派单池 **C8**。
6. **测试矩阵 U1~U10** 全绿 = M2 出口。
