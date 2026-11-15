---
title: FTB 基础指令（FTB Essentials）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# FTB 基础指令（FTB Essentials）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-ftbessentials-1201|1.20.1（1.20.1 服）]]

::: infobox FTB Essentials
| Mod ID | `ftbessentials`
| 版本 | 2101.1.10
| 端 | 双端
| 作者 | FTB Team
:::

> Adds many essential utility commands for servers

**FTB Essentials**（`ftbessentials`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给服务器补一整套日常指令：家（/home）、传送请求（/tpa）、随机传送（/rtp）、回死亡点（/back）、传送点（/warp）、昵称、禁言等，逐条可开关。生存服的基础设施基本靠它。

## 在赤物语里

- 玩家侧：用 `/sethome` 设家、`/home` 回家，`/tpa 玩家名` 发传送请求，`/rtp` 随机传送去探险；具体哪些能用取决于服里开了哪些。
- 服务端侧：`config/ftbessentials.snbt`：按 `admin` / `teleport` / `chat` 等分节，每条指令一个 `enabled` 开关；改完 `/reload` 或重启生效。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
