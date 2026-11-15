---
title: 酿造与奶酪（Brewin' And Chewin'）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 酿造与奶酪（Brewin' And Chewin'）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-brewinandchewin-1201|1.20.1（1.20.1 服）]]

::: infobox Brewin' And Chewin'
| Mod ID | `brewinandchewin`
| 版本 | 4.5.0
| 端 | 双端
| 作者 | Probleyes, Umpaz, MerchantCalico
:::

> Fermenting addon for Farmer's Delight.

**Brewin' And Chewin'**（`brewinandchewin`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

Farmer's Delight 的发酵扩展：发酵桶、酒类与奶酪，发酵结果受温度和维度影响。想做酒窖、开间酒馆、或者聚餐时有点喝的时用。

## 在赤物语里

- 玩家侧：做发酵桶，把原料放进去按所处生物群系/维度的温度发酵；冷、凉、温、热四档出不同产物，成品大多带短时效果。
- 服务端侧：`config/brewinandchewin-common.toml` 的 `[keg]` 段：`kegCapacity` 容量、`kegCold` / `kegChilly` / `kegWarm` / `kegHot` 各温度档的发酵倍率、`kegBiomeTemp` 与 `kegDimTemp` 决定是否按群系/维度判温度。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
