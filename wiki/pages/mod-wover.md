---
title: WorldWeaver
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# WorldWeaver

<!-- auto:begin -->

::: infobox WorldWeaver
| Mod ID | `wover`
| 版本 | 21.0.26
| 端 | 双端
| 作者 | Quiqueck
| 链接 | https://github.com/quiqueck/WorldWeaver
:::

> Unleash your world-building potential with WorldWeaver, a Minecraft utility mod for NeoForge, simplifying tasks and enhancing the possibilities of data-driven world generation.

**WorldWeaver**（`wover`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

WorldWeaver：面向数据驱动世界生成的工具库，把群系、地形、结构、特征这些原本要写一堆 JSON 的东西用统一的 API 组织起来，作者改世界生成时不用重复造轮子。玩家侧不直接感知，但用了它的模组（Quiqueck 系的群系/地形模组）缺了它会崩。

## 在赤物语里

- 玩家侧：用不到，纯前置；依赖它的模组提供的新地形/群系靠它生成。
- 服务端侧：`config/wover/main.json` 是全局配置，`cached.json` 是生成缓存（可删，下次启动重建）；一般不需要改。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
