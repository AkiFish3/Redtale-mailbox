---
title: 实体剔除（EntityCulling）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 实体剔除（EntityCulling）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-entityculling-1201|1.20.1（1.20.1 服）]]

::: infobox EntityCulling
| Mod ID | `entityculling`
| 版本 | 1.11.3
| 端 | 双端
| 作者 | tr7zw
| 链接 | https://modrinth.com/mod/entityculling
:::

> This mod uses async path-tracing to hide Tiles/Entities that are not visible.

**EntityCulling**（`entityculling`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

用异步光线追踪判断哪些方块实体和生物其实被墙挡住看不见，直接跳过它们的渲染。人多、箱子多、刷怪塔多的地方掉帧时，它是最直接的客户端提帧手段之一。

## 在赤物语里

- 玩家侧：纯客户端优化，装上就生效，没有界面也不用设置；看不到的东西不再渲染，视野内的画面不受影响。
- 服务端侧：无配置文件，仅客户端生效。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
