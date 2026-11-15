---
title: 魔女的扫帚（Majo's Broom）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 魔女的扫帚（Majo's Broom）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-majobroom-1201|1.20.1（1.20.1 服）]]

::: infobox Majo's Broom Dl909
| Mod ID | `majobroom`
| 版本 | 2.3.0
| 端 | 双端
| 作者 | DL909
:::

> A mod featuring Elaina's broom from Majo no Tabitabi, inspired by Marisa's broom from Touhou Maid Mod.

**Majo's Broom Dl909**（`majobroom`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

一把能骑的飞行扫帚，造型取自《魔女之旅》伊蕾娜的扫帚：手持即飞、可悬停、能载人，飞行手感偏轻盈而不是创造模式那种直上直下。跑图、跨地形、拍风景时比走路舒服，也更符合魔法系建筑的调性。

## 在赤物语里

- 玩家侧：合成扫帚后右键骑上，W/A/S/D 控制方向、空格上升、Shift 下降；落地会自动减速，长时间飞行不掉饥饿。
- 服务端侧：`config/majobroom-server.toml` 的 `[flight]`：`maxSpeed` 水平最大速度（默认 `0.9`）、`acceleration` 水平加速度、`maxVerticalSpeed` 垂直速度上限（默认 `0.5`）、`momentum` 惯性（默认 `0.92`，越大越难停）。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
