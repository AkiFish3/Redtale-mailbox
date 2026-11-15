---
title: 右键收割（Harvest with Ease）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 右键收割（Harvest with Ease）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-harvest_with_ease-1201|1.20.1（1.20.1 服）]]

::: infobox Harvest with ease
| Mod ID | `harvest_with_ease`
| 版本 | 9.4.0
| 端 | 双端
| 作者 | Crystal Spider, Moonstone Webber, Noir
| 链接 | https://github.com/crystal-nest/harvest-with-ease/tree/1.21
:::

> Don't break crops, right click them!

**Harvest with ease**（`harvest_with_ease`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

作物成熟后右键就能收割并自动补种，不用再左键打掉再手动种回去。大农场、自动补种、连收整排作物时省下大量点击，也避免误踩踏耕地。

## 在赤物语里

- 玩家侧：对着成熟作物右键即收割并原地补种，掉落物可选自动飞向玩家；按住 Shift 可以只收不种。
- 服务端侧：`config/harvest_with_ease-common.toml`：`[balancing]` 的 `require hoe` 要求手持锄头、`damage on harvest` 每次消耗锄头耐久、`exhaustion multiplier` 控制收割疲劳度（默认 1.0，大致等同正常破坏方块）、`gather drops` 让掉落物聚到脚下、`exp on harvest` 给经验；`[compatibility]` 的 `crops` 补其他模组的作物 id，`blacklist` 排除不该右键收的。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
