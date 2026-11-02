---
title: 世界生成与结构
role: admin
group: 管理员
order: 6
---

# 世界生成与结构

## 一、原版结构是三套机制

| 层 | 负责什么 | 文件 | 数据包能改吗 |
|---|---|---|---|
| 模板层 | 建筑长什么样 | `.nbt` | 完全自由 |
| 拼装层 | 哪块接哪块 | `template_pool` | **只有 jigsaw 结构** |
| 放置层 | 多密、在哪个群系 | `structure_set` + biome tag | 全部 38 个都开放 |

1.21.1 的 38 个 structure 定义里，**只有 15 个是 `minecraft:jigsaw`**：远古城市、堡垒、掠夺者前哨、考古废墟、试炼密室、5 种村庄。

其余 23 个各用各的 type（`mineshaft` / `stronghold` / `fortress` / `ocean_monument` / `ruined_portal` / `shipwreck` …）——它们的**形状由 Java 里的 StructurePiece 写死**，数据包只能改密度和群系，改不了长相。

但它们**也大量用 `.nbt` 模板**：原版 jar 里 1180 个模板文件、14 个目录。区别只在「这一块往哪接」是代码决定的。

## 二、四种方案的实际结论

| 方案 | 真结构 | Lootr | 维度精确 | 成熟度 |
|---|---|---|---|---|
| **数据包** | ✅ | ✅ | ❌ | 原版机制，稳 |
| Ruins | ❌ | ❌ | ⚠️ 按 path | 稳但老 |
| RC Volts | ⚠️ 聚合 | ❌ | ⚠️ 逐结构 | 0.7.x |
| Astruct | ⚠️ 自己的 locate | ✅ | ✅ | 0.1.1，很早 |

**关键结论（都来自实际拆包验证，不是推测）**：

- **Ruins 和 RC 的箱子 Lootr 接管不了**。两者的战利品都在生成时被「烘焙」成具体 ItemStack 写进箱子，箱子上没有 `LootTable` 标签，Lootr 无表可接。RC 的 187 个内置结构里 35 个带箱子，**全部**只带 `reccomplex:inventory_generation_tag`，一个 `LootTable` 都没有。
- **Ruins 生成的不是真结构**。`/locate structure` 不查世界方块，只跑确定性算法，Ruins 的方块不在算法结果集里，所以永远找不到。
- **只有 Astruct 能精确锁维度**（JSON 里写 `"dimension": "resource_world:twilight_forest"`）。它也有 `StructureDef` 只有 10 个字段的代价：**没有 `max_distance_from_center`、没有 `terrain_adaptation`、没有 `spawn_overrides`、没有共享网格**，做不了堡垒那种多段拼装。

## 三、双暮色的硬限制

主暮色 `twilightforest:twilight_forest` 和资源暮色 `resource_world:twilight_forest` **用的是同一批群系**。

原版结构没有维度字段，只有群系字段 → **biome tag 分不开这两个世界**。这是机制层面的，不是写法问题。

务实做法：接受它。主暮色的那批当常驻考古点，资源暮色的跟着 `/resourceworld reset` 一起重刷——本来就该是「再来一遍」。

## 四、数据包流程（单体建筑）

```
world/datapacks/redtale_ruins/
├── pack.mcmeta                          pack_format: 48
└── data/redtale/
    ├── structure/tw_hut.nbt
    ├── worldgen/template_pool/tw_hut.json
    ├── worldgen/structure/tw_hut.json
    ├── worldgen/structure_set/tw_huts.json
    └── tags/worldgen/biome/has_structure/tw_hut.json
```

**导出 `.nbt` 的两条路**：

1. **结构方块** —— 原版，48×48×48 上限，小建筑够用。
2. **Forgematica 转导** —— 选区存 `.litematic` → Schematic Manager → 「导出为：**原版结构**」。底层调的是同一个 `StructureTemplate.fillFromWorld`，**和结构方块等价但没有 48³ 限制**。

> 注意：只有 `.litematic` 能转，界面报错原文是「仅Litematica原理图支持导出为其他格式！」。

**做箱子必须先挂表**（在导出之前）：

```
/data merge block <x> <y> <z> {LootTable:"minecraft:chests/simple_dungeon",LootTableSeed:0L,Items:[]}
```

`Items:[]` 不能省，否则之前手动塞的东西会跟战利品一起出现。

**原点对齐**：导出的结构以选区**最小角**为 (0,0,0)。选区最底层必须正好是建筑地面，多框一层泥土就会整栋埋进地里。

## 五、可调字段速查

### structure（jigsaw）

| 字段 | 说明 |
|---|---|
| `biomes` | 群系 tag 或列表 |
| `start_pool` | 起点池 |
| `size` | 递归深度，村庄 6 / 单体 1 |
| `max_distance_from_center` | 半径上限，村庄和堡垒都是 80 |
| `start_height` | `{"absolute":n}` 或 `{"uniform":{...}}` |
| `project_start_to_heightmap` | `WORLD_SURFACE_WG` 等 |
| `terrain_adaptation` | `none` / `beard_thin` / `beard_box` / `bury` / `encapsulate` |
| `step` | `surface_structures` / `underground_structures` |
| `spawn_overrides` | 结构内刷怪 |
| `use_expansion_hack` | 村庄 true，堡垒 false |

### structure_set（random_spread 全部字段）

| 字段 | 原版实例 |
|---|---|
| `salt` | 每个 set 唯一 |
| `spacing` / `separation` | 32 / 8 是常用起手 |
| `spread_type` | `linear` 均匀 / `triangular` 扎堆（末地城、海底神殿用） |
| `frequency` | 0.01~0.2，前哨站 0.2 |
| `frequency_reduction_method` | `default` / `legacy_type_1` / `legacy_type_2` |
| `locate_offset` | 埋藏宝藏用 `[9,0,9]` |
| `exclusion_zone` | `{"chunk_count":10,"other_set":"minecraft:villages"}` |
| `structures[].weight` | 同格多结构比例 |

> `exclusion_zone` 很实用：想让自定义遗迹不和原版村庄撞车，直接写进去。

### 三个容易被忽略的定制点

1. **`worldgen/processor_list/*.json`** —— pool 里 `processors` 指过去。按概率替换方块（石头→苔石）、模拟崩塌、做风化。「遗迹感」全靠这个。
2. **`loot_table/chests/*.json`** —— 自定义战利品表。
3. **引用原版 pool 当素材** —— `single_pool_element` 的 `location` 不限命名空间，可以把原版村庄的房子混进自己的池子。

## 六、调试命令

```
/reload
/datapack list
/locate structure redtale:tw_hut
/place structure redtale:tw_hut
/place jigsaw redtale:fort/core minecraft:empty 6 ~ ~ ~
```

`/place jigsaw` 是拼装结构的调试利器——直接从起点池往下拼 N 层，站着就能看对不对，不用等自然生成。

**已生成区块不会补结构**。老地方 `/locate` 找不到是真没有。

## 七、当前状态

- Ruins：**装着**（`[魔改]ruins-1.21.1.2NF.jar`），在各维度默默生成遗迹。走数据包路线的话建议把 `tries_per_chunk_normal` 设 0，否则两套遗迹打架。
- RC Volts：装着，内置结构开启，只在主世界/下界/末地生成。
- Astruct：**没装**。
- 数据包：**还没建**，`world/datapacks/` 下目前只有 `redtale_bountiful_fix`。
