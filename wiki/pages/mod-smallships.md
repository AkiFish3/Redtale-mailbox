---
title: 小船（Small Ships）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 小船（Small Ships）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-smallships-1201|1.20.1（1.20.1 服）]]

::: infobox Small Ships
| Mod ID | `smallships`
| 版本 | 2.0.0-b2.1
| 端 | 双端
| 作者 | talhanation, metroite
:::

> This mod adds vanilla friendly ships into Minecraft!

**Small Ships**（`smallships`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

把「船」升级成能真正航行的载具：有帆、能调帆速、可加货箱、船上还能放东西，风格贴原版不突兀。想沿河道跑商、跨海赶路或者单纯玩帆船时用它。

## 在赤物语里

- 玩家侧：用对应木材造船，放下后右键上船，前进/后退键调帆的升降档（换档有冷却），船撞到生物会造成伤害；船被打坏会掉出船物品，记得捡。
- 服务端侧：`config/smallships-common.toml`：`[Ship.General]` 下 `shipGeneralSailCooldown`（换档冷却，当前 30）、`shipGeneralCollisionDamage`（撞击伤害，当前 7.5）、`shipGeneralDoItemDrop`（沉船是否掉物品）；各船型速度在后面的 speed 段。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
