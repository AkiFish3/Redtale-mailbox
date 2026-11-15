---
title: 野生动物（Naturalist）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 野生动物（Naturalist）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-naturalist-1201|1.20.1（1.20.1 服）]]

::: infobox Naturalist
| Mod ID | `naturalist`
| 版本 | 2.0.5
| 端 | 双端
| 作者 | crispytwig, Starfish Studios
:::

> Enhances the overworld by adding new wildlife with unique behavior!

**Naturalist**（`naturalist`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给主世界补一整套有独立行为的野生动物：熊会冬眠和护崽、蜗牛会留黏液、蝴蝶会停在花上、还有鳄鱼、猫头鹰、萤火虫等。想让人迹稀少的地方有生气、或者做生态观察/动物园时加它。

## 在赤物语里

- 玩家侧：新生物按群系自然生成，多数可以喂食驯服或用对应食物引诱；部分会主动攻击（熊、鳄鱼），夜里注意萤火虫与猫头鹰的活动时间。
- 服务端侧：`config/naturalist-server.toml`：`[disable_mobs]` 下按类别（`aquatic_mobs`、`land_mobs` 等）用 `xxx_removed = true` 逐个关掉不想出现的生物，`remove_all_bugs = true` 一次性禁掉所有虫类；`[behavior]` 调行为参数。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
