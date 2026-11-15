---
title: Oh The Trees You'll Grow
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# Oh The Trees You'll Grow

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-ohthetreesyoullgrow-1201|1.20.1（1.20.1 服）]]

::: infobox Oh The Trees You'll Grow
| Mod ID | `ohthetreesyoullgrow`
| 版本 | 5.3.5
| 端 | 双端
| 作者 | Corgi Taco
:::

> A Minecraft library that aims to give users incredible configurability by allowing the creation of trees with Minecraft's structure template `.nbt` files.

**Oh The Trees You'll Grow**（`ohthetreesyoullgrow`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

树木生成库：让模组/数据包用原版结构模板（`.nbt`）来定义树，支持随机旋转、多种变体、按生物群系替换，配置粒度非常细。玩家看到的是「新加的树形态很自然」，它本身不生树。

## 在赤物语里

- 玩家侧：用不到，纯前置；依赖它的群系与装饰模组的树木由它生成。
- 服务端侧：无独立配置文件；树型定义走数据包（`data/<命名空间>/worldgen/configured_feature` 一类），改树要改数据包而不是 config。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
