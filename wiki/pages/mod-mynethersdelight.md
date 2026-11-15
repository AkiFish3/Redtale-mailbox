---
title: 下界乐事（My Nether's Delight）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 下界乐事（My Nether's Delight）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-mynethersdelight-1201|1.20.1（1.20.1 服）]]

::: infobox My Nether's Delight
| Mod ID | `mynethersdelight`
| 版本 | 1.10.4.1
| 端 | 双端
| 作者 | SoyTutta
| 链接 | https://github.com/SoyTutta/MyNethersDelight
:::

> A new Nether expansion for Farmer's Delight!!

**My Nether's Delight**（`mynethersdelight`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

农夫乐事的下界扩展：加了绯红/诡异菌柄类食材、岩浆蛋糕、炽足兽与猪灵相关料理，还有「复苏土壤」这种能把下界荒地养出作物的耕地。在下界长期驻扎、想在下界也有一套完整厨房时用它。

## 在赤物语里

- 玩家侧：用刀具处理菌柄、菌光体、炽足兽肉等下界食材，砧板加工后下锅；复苏土壤铺在岩浆旁的耕地上会缓慢蔓延并催熟作物，岩浆蛋糕可以喂青蛙。
- 服务端侧：`config/mynethersdelight-common.toml`：`[settings]` 的 `enablePiglinFoodTrades` / `piglinFoodTradeChance`（默认 `0.25`）管猪灵以物易物换本模组食物，`enableFrogMagmaCakeBehavior` 管青蛙追岩浆蛋糕；`[farming]` 的 `resurgentSoilTickMultiplier` 与 `resurgentSoilPropagation` 控制复苏土壤的蔓延速度。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
