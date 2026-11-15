---
title: Architectury
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# Architectury

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-architectury-1201|1.20.1（1.20.1 服）]]

::: infobox Architectury
| Mod ID | `architectury`
| 版本 | 13.0.11
| 端 | 双端
| 作者 | shedaniel
:::

> A intermediary api aimed to ease developing multiplatform mods.

**Architectury**（`architectury`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给模组作者用的中间层 API，让同一份代码同时编译成 Fabric 与 NeoForge 两个版本。玩家不会直接看到它，它只是别的模组的前置。

## 在赤物语里

- 玩家侧：用不到；注意它是前置依赖，删掉会连带一批模组加载失败。
- 服务端侧：无独立配置文件，版本要和各模组声明的兼容范围对得上。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
