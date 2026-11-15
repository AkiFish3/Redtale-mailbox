---
title: Moonlight Lib
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# Moonlight Lib

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-moonlight-1201|1.20.1（1.20.1 服）]]

::: infobox Moonlight Lib
| Mod ID | `moonlight`
| 版本 | 1.21.1-3.0.16
| 端 | 双端
| 作者 | MehVahdJukaar
:::

> A small library with many cool unique features, from dynamic asset generation to dynamic villager schedules, data driven trades and Map Markers, simple multi loader utilities and more

**Moonlight Lib**（`moonlight`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

覆盖面很广的前置库（Moonlight Lib）：给模组作者提供动态资源与模型生成、动态村民日程、数据驱动交易、地图标记、多方块与通用工具类。玩家感知到的是「装了很多内容模组但不打架」，它本身不加玩法。

## 在赤物语里

- 玩家侧：用不到，纯前置；依赖它的模组（大量装饰、生物、村庄扩展类）在它缺失时会直接崩。
- 服务端侧：`config/moonlight-common.toml` 的 `[general]`：`multi_threaded_generation` 开动态资源多线程生成（机器核多时可提速）、`faster_cache_search` 用树结构加速缓存查询（多吃一点内存）、`global_datapacks_folder` 指定全局数据包目录（默认 `moonlight-global-datapacks`）。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
