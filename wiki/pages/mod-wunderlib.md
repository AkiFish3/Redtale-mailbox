---
title: WunderLib
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# WunderLib

<!-- auto:begin -->

::: infobox WunderLib
| Mod ID | `wunderlib`
| 版本 | 21.0.10
| 端 | 双端
| 作者 | Quiqueck
| 链接 | https://github.com/quiqueck/WunderLib
:::

> A UI, Math and Networking Library

**WunderLib**（`wunderlib`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

WunderLib：UI、数学与网络三合一的前置库，给模组作者提供界面控件、向量/噪声运算和自定义封包通道。单独装没有任何内容，但 Quiqueck 系模组（WorldWeaver 等）依赖它，缺了会在启动时报 NoClassDefFound。

## 在赤物语里

- 玩家侧：用不到，纯前置；不要手动删，删了依赖它的模组会启动失败。
- 服务端侧：无独立服务端配置文件；网络与 UI 参数由依赖它的模组决定。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
