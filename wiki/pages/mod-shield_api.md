---
title: 盾牌 API（ShieldAPI）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 盾牌 API（ShieldAPI）

<!-- auto:begin -->

::: infobox ShieldAPI
| Mod ID | `shield_api`
| 版本 | 2.2.0
| 端 | 双端
| 作者 | TheRedBrain
:::

> Creating shields with custom models was never easier!

**ShieldAPI**（`shield_api`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给模组作者用的盾牌框架，让自定义盾牌能挂上自己的模型、贴图和格挡判定，不用再挤在原版那一张盾牌图上。玩家侧平时看不到它，但依赖它的模组（带特殊盾牌的战斗/装备包）在它缺失时会显示成紫黑块或直接崩。

## 在赤物语里

- 玩家侧：用不到，纯前置；依赖它的模组提供的盾牌靠它渲染，缺了会缺模型。
- 服务端侧：无独立服务端配置文件；盾牌定义与模型写在依赖它的模组里。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
