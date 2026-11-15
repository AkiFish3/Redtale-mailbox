---
title: 世界编辑（WorldEdit）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 世界编辑（WorldEdit）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-worldedit-1201|1.20.1（1.20.1 服）]]

::: infobox WorldEdit
| Mod ID | `worldedit`
| 版本 | 7.3.8+6939-7d32b45
| 端 | 双端
| 作者 | EngineHub
| 链接 | https://enginehub.org/worldedit/
:::

> WorldEdit is an easy-to-use in-game world editor for Minecraft, supporting both single- and multi-player.

**WorldEdit**（`worldedit`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

运维/建筑用的世界编辑工具：选区、批量填充、复制粘贴、地形生成、替换方块，一条命令改一片区域。修地形、铺平台、清理熊孩子现场、批量换方块时用它，普通玩家一般用不上（权限受限）。

## 在赤物语里

- 玩家侧：需要 OP 权限才能用；常用 `//wand` 拿选区工具，`//set`、`//replace`、`//copy`、`//paste`、`//undo`。误操作先 `//undo`，别急着继续改。
- 服务端侧：`config/worldedit/worldedit.properties`：`cheat-mode=false`（不在创造也允许编辑相关命令）、`command-block-support=false`、`calculation-timeout=100`；`config/worldedit/sessions/` 存选区历史，`schematics/` 存原理图。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
