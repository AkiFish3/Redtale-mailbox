---
title: 传送石碑（Waystones）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 传送石碑（Waystones）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-waystones-1201|1.20.1（1.20.1 服）]]

::: infobox Waystones
| Mod ID | `waystones`
| 版本 | 21.1.46
| 端 | 双端
| 作者 | BlayTheNinth
| 链接 | https://mods.twelveiterations.com/minecraft/waystones
:::

> Teleport back to activated waystones. For Survival, Adventure or Servers.

**Waystones**（`waystones`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

生存向传送系统：在世界里生成/自建石碑，激活后可以在已激活的石碑之间互相传送，支持私人石碑、村庄石碑、传送卷轴与传送石板。跑图远了懒得走、或者想让队友快速集合时用。

## 在赤物语里

- 玩家侧：第一次靠近野生石碑右键激活并记住；之后在任意已激活石碑右键打开列表选目的地。传送要花经验（按距离计，跨维度固定价），带宠物默认不行，拴绳牵着可以。
- 服务端侧：`config/waystones-common.toml`：`[teleports]` 的 `enableCosts`（当前 true）、`warpRequirements`（经验花费公式：按距离 0.01/格、跨维度 +27、上限 27）、`transportPets`（当前 DISABLED）；`[general]` 的 `restrictedWaystones` 与 `defaultVisibility` 管谁能看到/管理石碑。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
