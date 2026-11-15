---
title: 物品禁用（Item Banning）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 物品禁用（Item Banning）

<!-- auto:begin -->

::: infobox Item Banning
| Mod ID | `itemblacklist`
| 版本 | 1.21.1-1.1.4
| 端 | 双端
| 作者 | pitbox46
:::

> Allows Blacklisting Items on Servers

**Item Banning**（`itemblacklist`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

服主用来禁物品的开关：被禁的物品无法合成、不能交易、放进容器会被清掉、丢在地上也会消失。有人拿创造模式物品或漏洞道具搞事时，用它比逐个回收省事。

## 在赤物语里

- 玩家侧：通常只会看到「这个物品不能拿」的提示；本服未启用任何禁用条目，正常物品不受影响。
- 服务端侧：`config/itemblacklist.properties.toml`：`[banProperties]` 的 `banContainerChanged` / `banMerchantTrades` / `banCraftingRecipes` / `banItemEntity` 分别控制容器、交易、配方、掉落四个入口是否拦截，`banRate` 是拦截检查概率（调低省性能），`[miscProperties]` 的 `showMessages` 决定非 OP 玩家能否看到提示。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
