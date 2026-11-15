---
title: Rhino（JavaScript 引擎）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# Rhino（JavaScript 引擎）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-rhino-1201|1.20.1（1.20.1 服）]]

::: infobox Rhino
| Mod ID | `rhino`
| 版本 | 2101.2.8-build.91
| 端 | 双端
| 作者 | latvian.dev, Mozilla
| 链接 | https://kubejs.com
:::

> A fork of Mozilla's Rhino library, modified for use in mods

**Rhino**（`rhino`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

latvian.dev 把 Mozilla 的 Rhino JavaScript 引擎移植进 Minecraft 的版本，专门给 KubeJS 这类「用 JS 脚本改游戏」的模组当底层运行环境。玩家看不到它，但凡是 KubeJS 脚本能跑起来，背后都是它在解释执行。属于「不装就崩」的那类底层依赖。

## 在赤物语里

- 玩家侧：用不到，纯前置；KubeJS 脚本靠它执行，缺失则脚本全部失效。
- 服务端侧：无独立服务端配置文件；脚本本身写在 KubeJS 的 `kubejs/` 目录下，不在这里改。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
