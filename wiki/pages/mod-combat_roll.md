---
title: 战斗翻滚（Combat Roll）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 战斗翻滚（Combat Roll）

<!-- auto:begin -->

::: infobox Combat Roll
| Mod ID | `combat_roll`
| 版本 | 2.0.6+1.21.1
| 端 | 双端
| 作者 | Daedelus
:::

> Adds combat roll ability, with related attributes and enchantments.

**Combat Roll**（`combat_roll`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给玩家加一个翻滚闪避动作，带无敌帧、翻滚距离属性和相关附魔。打 Boss、玩偏动作向的战斗时用来拉开距离。

## 在赤物语里

- 玩家侧：默认按 R 翻滚（可在按键设置里改），消耗少量饥饿度、有冷却；翻滚距离受属性与附魔影响，饿着肚子翻不动。
- 服务端侧：`config/combat_roll/server.json5`：`roll_cooldown` 冷却秒数、`invulnerable_ticks_upon_roll` 无敌帧、`exhaust_on_roll` 每次翻滚的饥饿消耗、`roll_duration` 动作时长、`allow_rolling_while_airborn` 是否允许空中翻滚（开了会破坏距离属性）。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
