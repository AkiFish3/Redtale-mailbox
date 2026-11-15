---
title: 铁氧体内存优化（Ferrite Core）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 铁氧体内存优化（Ferrite Core）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-ferritecore-1201|1.20.1（1.20.1 服）]]

::: infobox Ferrite Core
| Mod ID | `ferritecore`
| 版本 | 7.0.3
| 端 | 双端
| 作者 | malte0811
:::

> Reduces memory usage.

**Ferrite Core**（`ferritecore`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

压缩方块状态、模型、顶点数据这些占内存的大头，服务端和客户端都能省下可观的堆内存。模组多、跑久了容易 OOM 的服基本必装。

## 在赤物语里

- 玩家侧：无感知，不改变任何画面与玩法，只是内存占用更低、GC 卡顿更少。
- 服务端侧：`config/ferritecore-mixin.toml`：`compactFastMap` 换更紧凑但略慢的方块状态表示，`useSmallThreadingDetector` 是已知会有极罕见崩溃的风险项（默认关），模型与方块状态的去重开关也都在这份文件里。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
