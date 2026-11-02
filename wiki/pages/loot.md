---
title: 战利品与 Lootr
role: admin
group: 管理员
order: 7
---

# 战利品与 Lootr

## Lootr 是怎么工作的

Lootr 接管容器靠两个注入点：

1. **`setLootTable`** —— 方块放下时把方块实体排队，**延到下一个 tick** 才真正转换。
2. **`unpackLootTable`** —— 拦截原版解包，改由 Lootr 按玩家分发。

第二个注入有一个**前置判断**：

```java
if (!level.isClientSide() && level instanceof ServerLevel) { ... } else { return false; }
```

意思是：**拿到的是 `WorldGenRegion`（世界生成阶段）就不接管**。

## 所以能不能被接管，只看一件事

**箱子落到世界里的时候，`LootTable` 标签还在不在。**

- 在 → 下一 tick Lootr 的 ticker 接住，按玩家独立
- 不在 → 只打一条 `Potential block entity ... has no loot table` 然后跳过，箱子变成**全体共享的一次性箱子**

## 各方案实测结论

| 方案 | 箱子带 LootTable | Lootr 能接管 |
|---|---|---|
| **原版数据包结构** | ✅ 原样保留 | ✅ |
| **Astruct** | ✅ 不调 `unpackLootTable` | ✅ |
| Ruins | ❌ 生成时立即 `unpackLootTable(null)` | ❌ |
| RC Volts | ❌ 战利品烘焙成 ItemStack | ❌ |

### Ruins 为什么不行

`realizeBlock` 给容器调 `setLootTable(...)`，**紧接着立刻**调 `unpackLootTable(null)`。这一句在世界生成期执行，Lootr 因为拿到的不是 `ServerLevel` 而放弃拦截，原版解包照常跑完 → 表被清空、物品被写死。

到下一个 tick，Lootr 的 ticker 来处理时已经没有表了。

附带限制：Ruins 只在 `BuiltInLootTables.all()` 里找表，**只能引用原版内置表**，数据包自定义表它不认，表名对不上箱子直接是空的。

### RC 为什么不行

jar 内**零处** `setLootTable` 调用。放置时走 `LegacyInventoryGenerationHandler`，用 `LegacyVanillaLootTableAdapter` 把 loot table `fill()` 出来后**烘焙成具体 ItemStack** 写进箱子。

它只是把原版表当「取材来源」，不是把表挂到箱子上。没有表，Lootr 无从接管。

## 验证方法

放进世界之后，对着箱子：

```
/data get block <x> <y> <z> LootTable
```

- 有返回值 → Lootr 会接管
- `not found` → 这个箱子是共享一次性的

或者看方块 id：被接管的会变成 `lootr:lootr_chest`。

## 服务器现状

装了两个：

- `[毛线]lootr-neoforge-1.21.1-1.11.38.127.jar`
- `twilight_lootr-neoforge-1.21.1-0.0.0.1.jar`

暮色的 boss 战利品箱已经按玩家独立，这是 `twilight_lootr` 做的。

**但 Ruins 和 RC 生成的箱子不受保护**——它们在世界生成时就把东西定死了。

## 想自定义战利品表

数据包路线：`data/<ns>/loot_table/chests/*.json`，然后 `.nbt` 里的箱子写这个表名。

注意目录名是 `loot_table`（单数），1.21 改过命名。
