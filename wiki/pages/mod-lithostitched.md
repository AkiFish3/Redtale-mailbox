---
title: Lithostitched
role: admin
group: 模组
order: 300
nav: no
auto: mod
---

# Lithostitched

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-lithostitched-1201|1.20.1（1.20.1 服）]]

::: infobox Lithostitched
| Mod ID | `lithostitched`
| 版本 | 1.8.1
| 端 | 仅服务端
| 作者 | Apollo
| jar | `lithostitched-1.8.1-neoforge-21.1.jar`
| 许可 | MIT
:::

> A library mod with new configurability and compatibility enhancements for worldgen

**Lithostitched**（`lithostitched`）是**仅装在服务端**，玩家客户端里没有它，所以页面只记录它在做什么、改哪个配置。

<!-- auto:end -->

## 中文简介

Lithostitched 是世界生成（worldgen）的底层库，自己不产方块、生物或地形，只把原版 worldgen 的配置项做得更细，并修补不同地形/结构模组之间的兼容问题。玩家在游戏里看不到它，但装了地形类模组（如 Tectonic）或加了自定义结构数据包时，靠它才能正常叠加而不互相打架。

## 在赤物语里

- 玩家侧：无直接入口，不产生任何方块或物品；进游戏感觉不到它。
- 服务端侧：`config` 下没有独立配置目录，它通过其他模组/数据包提供的 worldgen JSON 生效，改地形请改对应地形模组的配置，不要找 lithostitched 的文件。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
