---
title: 饰品栏（Accessories）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 饰品栏（Accessories）

<!-- auto:begin -->

::: infobox Accessories
| Mod ID | `accessories`
| 版本 | 1.1.0-beta.53+1.21.1
| 端 | 双端
| 作者 | Blodhgarm, chyzman, Dr.Zeal
:::

> A extendable and data-driven Accessory Mod for Minecraft.

**Accessories**（`accessories`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给戒指、项链、护符这类东西提供独立装备槽的框架模组，很多 RPG 与装备模组都靠它。它本身不提供饰品，只提供槽位和渲染管线。

## 在赤物语里

- 玩家侧：背包界面里有饰品按钮，点开是独立的槽位页；把饰品拖进去就生效。默认要蹲下才能换（`equipControl`），战斗中换装不太方便是这个原因。
- 服务端侧：`config/accessories.json5`：`clientOptions.equipControl` 控制换装是否要蹲下，`disableEmptySlotScreenError` 关掉空槽报错提示。服务端主要关心槽位定义与死亡掉落规则。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
