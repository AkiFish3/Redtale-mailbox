---
title: BCLib
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# BCLib

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-bclib-1201|1.20.1（1.20.1 服）]]

::: infobox BCLib
| Mod ID | `bclib`
| 版本 | 21.0.26
| 端 | 双端
| 作者 | Quiqueck, paulevs, Bulldog83, Raijin
| 链接 | https://modrinth.com/mod/bclib
:::

> A library for BetterX team mods

**BCLib**（`bclib`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

BetterEnd / BetterNether 团队的世界生成基础库：管生物群系源、维度补丁和地形拼装。玩家不直接接触，但它决定新群系能不能正常生成。

## 在赤物语里

- 玩家侧：用不到；它出问题时表现是新维度/新群系不生成或地形错乱。
- 服务端侧：`config/bclib/main.json` 控补丁应用（`apply_patches`、`repairBiomesOnLoad`），另有 `generator.json`、`server.json` 管生成与服务端行为。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
