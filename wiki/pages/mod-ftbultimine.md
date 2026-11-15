---
title: 连锁挖掘（FTB Ultimine）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 连锁挖掘（FTB Ultimine）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-ftbultimine-1201|1.20.1（1.20.1 服）]]

::: infobox FTB Ultimine
| Mod ID | `ftbultimine`
| 版本 | 2101.1.15
| 端 | 双端
| 作者 | FTB Team
:::

> Allows you to break multiple blocks at once

**FTB Ultimine**（`ftbultimine`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

按住一个键再挖方块，会沿同种方块一次性挖掉一整片（默认上限 64 格），挖矿脉、清石头、收大片作物全靠它。是生存服里手感提升最明显的工具类模组之一。

## 在赤物语里

- 玩家侧：默认按住 `~`（反引号）再左键挖方块，会按当前工具和朝向连挖；挖不同形状可以在按键设置里换模式（平面、隧道、阶梯等）。
- 服务端侧：`config/ftbultimine-server.snbt` 的 `costs_limits`：`max_blocks` 是单次上限（默认 64），`exhaustion_per_block` 是每格额外饥饿消耗（默认 20.0，挖一片会明显掉饥饿），`require_tool` 要求必须手持可损坏工具，`ultimine_cooldown` 是冷却；装了 FTB Ranks 时这些值能被权限节点覆盖。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
