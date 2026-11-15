---
title: 服务端核心优化（ServerCore）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 服务端核心优化（ServerCore）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-servercore-1201|1.20.1（1.20.1 服）]]

::: infobox ServerCore
| Mod ID | `servercore`
| 版本 | 1.5.19+1.21.1
| 端 | 双端
| 作者 | Wesley1808
| 链接 | https://github.com/Wesley1808/ServerCore
:::

> A NeoForge mod that aims to optimize the minecraft server.

**ServerCore**（`servercore`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

Wesley1808 的服务端优化与修复模组：针对多人服做了一批性能优化（异步加载、动态调节、村民降频、合并经验/物品等）和防卡顿的小修复，能在不明显改变玩法的同时明显降 MSPT、减少卡顿尖峰。开服必装那一档，但对性能敏感的设置要按机器调。

## 在赤物语里

- 玩家侧：用不到，装上即生效；你只会感觉到进服更稳、高峰不卡，个别优化（如村民降频）会改变 NPC 行为节奏。
- 服务端侧：`config/servercore/config.yml` 管功能开关（如 `prevent-moving-into-unloaded-chunks`、`autosave-interval-seconds`、村民 `lobotomize`）与动态调节；`optimizations.yml` 管可开关的具体优化项（`reduce-sync-loads`、`cache-ticking-chunks` 等，重启生效）。多数设置可用 `/servercore reload` 热重载。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
