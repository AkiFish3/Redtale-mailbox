---
title: 末影乐事（Ender's Delight）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 末影乐事（Ender's Delight）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-endersdelight-1201|1.20.1（1.20.1 服）]]

::: infobox Ender's Delight
| Mod ID | `endersdelight`
| 版本 | 1.3.1
| 端 | 双端
| 作者 | Axedgaming, Furti Two
:::

> An addon for Farmer's Delight based around adding culinary content to the end!

**Ender's Delight**（`endersdelight`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

另一套末地主题的农夫乐事附属，主打「末影相位」状态和虚空辣椒：吃了带相位的食物后受击会短距瞬移，虚空辣椒会自己蔓延生长。想玩末地风味的偏门食材和效果时用。

## 在赤物语里

- 玩家侧：做带末影相位的料理吃下，被打时会随机瞬移躲避；虚空辣椒种在末地石一类方块上会自行扩散，注意别让它长满基地。
- 服务端侧：`config/endersdelight-common.toml`：`[ender_phasing]` 的 `doesPhasingTeleportPlayer` 开关受击瞬移、`cooldownBetweenPhasingTeleports` 调冷却、`doesWaterHurtPlayerWithPhasingEffect` 决定相位期间碰水是否掉血；`[void_pepper]` 的 `spreadRadius` / `spreadChance` 控蔓延速度。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
