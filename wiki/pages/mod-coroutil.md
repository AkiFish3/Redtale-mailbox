---
title: CoroUtil
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# CoroUtil

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-coroutil-1201|1.20.1（1.20.1 服）]]

::: infobox CoroUtil
| Mod ID | `coroutil`
| 版本 | 1.21.0-1.3.8
| 端 | 双端
| 作者 | Corosus
:::

> It utils

**CoroUtil**（`coroutil`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

CoroUtil 是 Corosus 系列模组（Weather2、Zombie Awareness 等）的公共工具库，提供实体寻路、配置文件框架、网络同步等底层内容。玩家侧无感知。

## 在赤物语里

- 玩家侧：用不到，纯前置依赖。
- 服务端侧：`config/CoroUtil/General.toml`：`[general]` 下的 `useLoggingLog` / `useLoggingDebug` / `useLoggingError` 控制日志级别，排查问题时临时开 debug。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
