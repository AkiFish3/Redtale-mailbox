---
title: 配方并行加速（Fast Suite）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 配方并行加速（Fast Suite）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-fastsuite-1201|1.20.1（1.20.1 服）]]

::: infobox Fast Suite
| Mod ID | `fastsuite`
| 版本 | 6.0.7
| 端 | 双端
| 作者 | Shadows_of_Fire
:::

> Introduces multithreading to the json recipe system.

**Fast Suite**（`fastsuite`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

把 JSON 配方的匹配过程改成多线程，合成、查看配方、自动化机器找配方时 CPU 占用更均匀，卡顿更少。模组多、配方量大的整合包收益最明显。

## 在赤物语里

- 玩家侧：无感知，只是合成和翻配方书更顺。
- 服务端侧：`config/fastsuite.cfg`：`Unsafe Mode` 允许不加校验地全量并行（有崩服风险，默认关），`Max Recipe Lookup Time` 设单次查找超时，出问题时把可疑配方类型加进 `Single Threaded Recipe Types` 回退成单线程。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
