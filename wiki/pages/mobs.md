---
title: 自定义生物方案
role: admin
group: 管理员
order: 9
---

# 自定义生物方案

> 起因：想做出「插件端 MythicMobs」那种效果——自定义模型、有技能的 boss、多阶段、区域刷怪。

## 一、候选：DBE's Spark Engine（星火引擎）

CurseForge ID `1659148`，作者 DBE_inLang，**只有 NeoForge 1.21.1**，当前版本 `DBE-1.21.1-neoforge-1.0.1044-SNAPSHOT.jar`。

它把 MythicMobs 那套「写配置 → 进游戏看效果」的循环，搬成了**游戏内 GUI**：

| 模块 | 干什么 |
|---|---|
| 自定义 NPC 编辑器 | 建 NPC、配属性、批量存读 |
| 状态树 | 按条件切换行为，等价于 MM 的 phases + AI 目标 |
| 动画图 | 基础动画、混合、节点式逻辑 |
| 动作库 | 借鉴 UE 的 Montage + GAS，时间轴编技能（动画/粒子/判定框/音效） |
| 骨骼碰撞体 | 碰撞检测挂到单根骨骼上，做精确的命中判定 |
| 标签 / 输入路由 | 把动画、战斗、状态串起来 |

**它没覆盖的**（这些才是 MythicMobs 真正的骨架）：

- 刷怪点调度（MythicSpawner 的冷却、上限、区域）
- 带条件的掉落表
- 派系 / 伤害修正 / 免疫
- 占位符与变量
- 配置版本管理、热重载

## 二、结论：它不是 MythicMobs 的替代品，是「技能编辑器」

Spark Engine 解决的是**「这个 boss 长什么样、会什么招」**，剩下**「它什么时候出现、死后掉什么、数值怎么算」**要靠别的东西拼。

## 三、拼法

| MythicMobs 的能力 | 用什么补 |
|---|---|
| 刷怪点 / 定时刷新 | KubeJS 定时任务 + 召唤；或 `In Control!` 管自然生成规则 |
| 掉落表（带条件） | **LootJS**（KubeJS 插件）或数据包 `loot_table` |
| 数值 / 属性 | `Apothic Attributes` / `AttributeFix`；KubeJS 直接改 attribute |
| 血条 / 阶段提示 | 原版 `/bossbar` 命令 + KubeJS 驱动 |
| 复杂逻辑判断 | **KubeJS** 脚本 |
| 无模型的动态实体 | **EntityJS**（KubeJS 插件，1.21.1 可用） |

**EntityJS 值得单独说**：它用 KubeJS 动态注册实体，带 AI 目标、动画，脚本随服务端走。想快速加「会放火球、死后爆炸、血量 300」这类怪，它比 Spark Engine 轻得多。

## 四、风险（这条最重要）

- 版本号是 **SNAPSHOT**，下载量不到 1000，单人开发。
- 它管模型和动画，**客户端必须装**，且模型资源要和存档对齐。哪天作者改了数据结构，你现有的 NPC 可能整体失效。
- 服务端跑的东西依赖客户端资源 = 玩家装错版本就看不到 boss。

**建议**：先在一个测试维度里做一只 boss 验证，别直接进主服。同时留一条退路——用 EntityJS 做一版简化的。

## 五、什么情况下值得上

- 你要的是**有独立模型、有动作表现**的 boss（比如主城守卫、副本 boss），并且愿意接受「客户端必须同步」。
- 如果只是想在暮色之外加点有技能的怪，**EntityJS + LootJS** 更稳，纯脚本，改起来快。

## 六、当前状态

**2026-11-02 已安装**（测试阶段先上，双端）。

| 端 | 文件 | 说明 |
|---|---|---|
| 服务端 | `DBE-1.21.1-neoforge-1.0.1044-SNAPSHOT.jar` | 40.2 MB，本体 |
| 客户端 | 同上 | 必须与服务端**同 sha1**，否则网络注册表不匹配直接踢 |
| 客户端 | `ldlib2-neoforge-1.21.1-2.2.44-all.jar` | LDLib2，前置；`mods.toml` 里该依赖 `side=CLIENT`，服务端不需要 |

前置 `kotlinforforge >= 5.10` 整合包本来就有（5.11.0），不用另加。

sha1：

```
1462B8831C98B985694024E885CB2E74FD8842E3  DBE-1.21.1-neoforge-1.0.1044-SNAPSHOT.jar
39D4B7C1FBA4ED56D5680B7ACD0E559690C4E763  ldlib2-neoforge-1.21.1-2.2.44-all.jar
```

桌面同步包：`C:\Users\AkiFish3\Desktop\赤物语-必装MOD-1.21.1\`（含上面两个 + RC Volts）

## 七、刷怪点：KubeJS 定点刷新（已实测）

MythicSpawner 那套「定时 + 上限 + 每点独立判定」，一个 KJS 脚本就够，不需要插件。

需求原型：一张坐标表（p1/p2/p3），每 10 秒检查一次，**每点单独判定**——某点上一只还活着就跳过，死了才补。1、2 号死了补两个，3 号没死就不动。

脚本：`E:/server-1.21.1/kubejs/server_scripts/spawn_points.js.disabled`
去掉 `.disabled` 生效，改完 `/kubejs reload server_scripts`。

### 7.1 核心就一行命令

整个判定压进一条原版命令，让**游戏自己判断**，脚本只负责定时触发：

```
execute in <dim> positioned <x> <y> <z> \
  if entity @a[distance=..64] \
  unless entity @e[tag=sp_<id>] \
  run summon <entity> ~ ~ ~ {Tags:["sp_<id>"],PersistenceRequired:1b,<额外NBT>}
```

三件事一块做完：限定维度坐标、要求附近有玩家、要求世界里没有这个 tag 的活实体。`summon` 的 `~ ~ ~` 继承 `positioned` 的坐标，不用重复写。

KJS 那边只有调度：

```js
if (p._next === undefined) p._next = t + (p.offset || 0)
if (t < p._next) return
p._next = t + interval
```

用「下一次时刻」而不是 `tickCount % interval === 0`：不依赖整除、容忍卡顿跳 tick、reload 后自动重新对齐。

### 7.2 实测记录（2026-11-02，1.21.1 服务端）

| tick | 场景 | 结果 |
|---|---|---|
| 1 | 点位空 | 刷出 1 只 ✓ |
| 101 / 201 | 生物存活 | 不刷，数量保持 1 ✓ |
| kill 之后 301 | 生物已死 | 补刷 1 只 ✓ |

### 7.3 三个坑（都是实测踩出来的）

> **坑一：`runCommandSilent` 返回 void。**
> `MinecraftServerKJS.kjs$runCommandSilent(String)` 签名是 `void`，拿不到命令结果。
> `if (server.runCommandSilent('execute if entity ...') > 0)` 这种写法永远是 `undefined`。
> 解法：把判断写进命令（`unless entity`），别在 JS 里读返回值。

> **坑二：KJS 的 `getEntitiesWithin` 会把已经 kill 掉的实体继续返回。**
> 用 `level.getEntitiesWithin(AABB)` 判定时，`/kill @e[tag=sp_x]` 之后
> `@e[tag=sp_x]` 已经查不到（`Test failed`），但同一个 AABB 里 KJS 还能拿到那只僵尸，
> 于是 `occupied` 永远为 true，永远不补刷。原版选择器和 KJS 实体缓存的结论不一致。
> 这也是最终改用纯命令方案的原因——**判定不要用 KJS 的实体 API**。

> **坑三：区块没加载 = 实体不在选择器里。**
> `@e` 和 `getEntitiesWithin` 都只统计已加载区块。
> 若去掉 `if entity @a[distance=..N]`，玩家跑远后该点实体不被加载 → 判定为已死亡 → 重复生成，回来一堆。
> 两种解法：① 保留 `nearPlayer` 距离（脚本默认 64 格，推荐）；② `forceload add` 把刷怪区块常驻。

### 7.4 为什么 NBT 里必须有 PersistenceRequired

`PersistenceRequired:1b` 关掉原版的距离 despawn。不加的话玩家一走远实体被清，脚本以为死了，回头又是满编。

`Tags:["sp_p1"]` 是身份标识，也是手动清理的抓手：`/kill @e[tag=sp_p1]`。

### 7.5 运维

```
/kill @e[tag=sp_p1]                                   清场，下个周期自动补
/execute as @e[tag=sp_p1] run data get entity @s Pos   看当前这只在哪
```

加点的三种变体：

| 想要 | 怎么改 |
|---|---|
| 不同生物 | 每个点写自己的 `entity` |
| 不同节奏 | 每个点写自己的 `interval` |
| 不想同时刷 | 用 `offset` 错开，0 ~ interval-1 |

### 7.6 已知边界

- 服务器重启后，`_next` 重新计算，第一次刷新对齐到 `tickCount + offset`，可能比预期晚最多一个 interval。
- `/kubejs reload server_scripts` 之后 tick 监听器有时不重新绑定（实测），改完脚本最稳的是重启服务端。
- 生物被玩家引走后，「盒子内还有同类」和「tag 还在」的结论不同：命令方案用 tag，所以引走也不会重复刷——这正是想要的。
