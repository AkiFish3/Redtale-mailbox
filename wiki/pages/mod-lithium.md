---
title: 锂优化（Lithium）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 锂优化（Lithium）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-lithium-1201|1.20.1（1.20.1 服）]]

::: infobox Lithium
| Mod ID | `lithium`
| 版本 | 0.15.4+mc1.21.1
| 端 | 双端
| 作者 | 2No2Name, JellySquid
:::

> Lithium is a free and open-source optimization mod for Minecraft which makes a wide range of performance improvements to the game.

**Lithium**（`lithium`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

服务端与客户端的通用性能优化模组：重写实体 AI、区块刻、方块刻、流体、碰撞、刷怪等原版逻辑里最耗 CPU 的部分，行为尽量与原版一致但快很多。人多了卡顿、TPS 掉、生物一多就掉帧时，先加它。

## 在赤物语里

- 玩家侧：用不到，装上即生效，没有界面也没有命令。
- 服务端侧：`config/lithium.properties` 默认是空文件，作者明确写了「仅为调试存在，平时不要配」；真要关某一项才在里面加 `mixin.<类别>=false`，改前先备份存档。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
