---
title: 紧凑帮助（Compact Help Command）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 紧凑帮助（Compact Help Command）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-compacthelpcommand-1201|1.20.1（1.20.1 服）]]

::: infobox Compact Help Command
| Mod ID | `compacthelpcommand`
| 版本 | 3.0
| 端 | 双端
| 作者 | Serilum
| 链接 | https://serilum.com/mod/compact-help-command
:::

> Modifies the standard /help command to be colourful and have multiple pages.

**Compact Help Command**（`compacthelpcommand`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

重写 `/help`：彩色、可悬停看说明、按页翻。服务器指令一多，原版 `/help` 刷一屏根本看不完，用它。

## 在赤物语里

- 玩家侧：直接 `/help` 看分页列表，鼠标悬停在指令上看子指令说明，翻页用页码参数。
- 服务端侧：`config/compacthelpcommand.json5`：`amountCommandsPerPage` 每页条数、`commandColour` / `subcommandColour` 配色编号（0–15 对应原版颜色）。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
