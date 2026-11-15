---
title: Collective
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# Collective

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-collective-1201|1.20.1（1.20.1 服）]]

::: infobox Collective
| Mod ID | `collective`
| 版本 | 8.46
| 端 | 双端
| 作者 | Serilum
| 链接 | https://serilum.com/mod/collective
:::

> Collective is a shared library with common code for all of Serilum's mods.

**Collective**（`collective`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

Serilum 全家桶（几十个小模组）共用的代码库，负责实体替换、掉落生成等公共逻辑。属于前置库。

## 在赤物语里

- 玩家侧：不用操作；装了 Serilum 的模组就少不了它。
- 服务端侧：`config/collective.json5`：`enableUpdateChecker` 是否在控制台提示依赖模组更新、`transferItemsBetweenReplacedEntities` 实体被替换时是否转移身上物品、`loopsAmountUsedToGetAllEntityDrops` 掉落生成循环次数（调低可加快加载）。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
