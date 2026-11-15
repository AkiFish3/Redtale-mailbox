---
title: 玩家动画（Player Animator）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 玩家动画（Player Animator）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-playeranimator-1201|1.20.1（1.20.1 服）]]

::: infobox Player Animator
| Mod ID | `playeranimator`
| 版本 | 2.0.4+1.21.1
| 端 | 双端
| 作者 | KosmX
| 链接 | https://github.com/KosmX/minecraftPlayerAnimator
:::

> A lightweight library to easily animate the player

**Player Animator**（`playeranimator`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

KosmX 做的轻量库，让模组作者能像放动画一样驱动玩家和实体的动作——走路、攻击、施法都走动画文件，而不是死板的原版姿势。装了依赖它的内容/战斗模组才能看到效果，它本身不加任何玩法。想知道为什么某些模组的动作很顺，就是它在背后干活。

## 在赤物语里

- 玩家侧：用不到，纯前置；依赖它的模组（大量动画/战斗类）在它缺失时直接崩，进游戏后角色会按这些动画做动作。
- 服务端侧：无独立服务端配置文件；纯库，动作与数值定义在依赖它的模组里。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
