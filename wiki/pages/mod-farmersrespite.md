---
title: 农夫暇饮（Farmer's Respite）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 农夫暇饮（Farmer's Respite）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-farmersrespite-1201|1.20.1（1.20.1 服）]]

::: infobox Farmer's Respite
| Mod ID | `farmersrespite`
| 版本 | 3.0.1
| 端 | 双端
| 作者 | umpaz, HoboJoe, SoyTutta; port by TylerCross
| 链接 | https://www.curseforge.com/minecraft/mc-mods/farmers-respite-unofficial-port
:::

> An addon for the Farmer's Delight mod centered around brewing tea and coffee in the kettle; ported and upgraded to NeoForge 1.21.1 by TylerCross

**Farmer's Respite**（`farmersrespite`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

农夫乐事的茶饮扩展：加了一只水壶（Kettle），用来煮茶和咖啡，另有茶丛、咖啡丛和一批带增益的饮品。日常补给、开店卖饮料、给建筑摆一套茶席都用得上。

## 在赤物语里

- 玩家侧：做水壶放热源上（可用机械动力的烈焰人加热），投茶叶或咖啡豆煮；喝带「困倦」的饮品后再睡一觉能回血。
- 服务端侧：`config/farmersrespite-common.toml`：`[Kettle]` 的 `blazeBurnersAsSource` / `blazeBurnersNeedFuel` 控制烈焰人能否当热源、是否需要燃料，`drainKettleButton` 控制倒空按钮；`[Crops]` 的 `boneMealTea` / `boneMealCoffee` 控制能否催熟，`coffeeParasitization` 控制咖啡丛是否必须寄生在其他作物旁。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
