---
title: 惊悚之门（Spooky Doors）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 惊悚之门（Spooky Doors）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-spookydoors-1201|1.20.1（1.20.1 服）]]

::: infobox Spooky Doors
| Mod ID | `spookydoors`
| 版本 | 21.1.14
| 端 | 双端
| 作者 | BlayTheNinth
| 链接 | https://mods.twelveiterations.com/minecraft/spooky-doors
:::

> Doors, but they're scary like in Horror Games

**Spooky Doors**（`spookydoors`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

让门变得「不老实」：靠近会自己缓缓打开、镜头被门带着转、开关时带恐怖片式的顿挫，还能用蜂蜜块之类「驱邪」把门恢复正常。做鬼屋、恐怖地图或万圣节活动时很好用。

## 在赤物语里

- 玩家侧：默认模式下普通门就有概率闹鬼（自开、镜头跟着偏）；拿蜂蜜块右键可驱邪、拿恶魂之泪右键可反向让门闹鬼；若服主设成强制模式，这两种道具都无效。
- 服务端侧：`config/spookydoors-common.toml`：`spookyDoorActivation` 三档 `OPTIONAL`（默认不闹，需指令开启）/`DEFAULT`（默认闹，可关）/`FORCED`（全部强制闹）；`allowItemToExorciseDoors`、`allowItemToHauntDoors` 开关驱邪与闹鬼道具；`moveCameraWithDoor` 管镜头跟随。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
