---
title: 地形生成优化（Noisium）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 地形生成优化（Noisium）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-noisium-1201|1.20.1（1.20.1 服）]]

::: infobox Noisium
| Mod ID | `noisium`
| 版本 | 2.3.0+mc1.21-1.21.1
| 端 | 双端
| 作者 | Steveplays28
| 链接 | https://github.com/Steveplays28/noisium
:::

> Optimises worldgen performance for a better gameplay experience.

**Noisium**（`noisium`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

只优化世界生成阶段的性能：重写噪声采样与生物群系查找里开销最大的部分，让新区块生成更快、开新图或跑远路时的卡顿更少。行为与原版一致，不改地形长相。

## 在赤物语里

- 玩家侧：用不到，装上即生效；只在服务器生成区块时起作用，已经生成过的区域没有变化。
- 服务端侧：无服务端配置文件；如需临时关闭，从模组列表里禁用即可。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
