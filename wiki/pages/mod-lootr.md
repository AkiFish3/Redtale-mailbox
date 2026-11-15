---
title: 独立战利品箱（Lootr）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 独立战利品箱（Lootr）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-lootr-1201|1.20.1（1.20.1 服）]]

::: infobox Lootr
| Mod ID | `lootr`
| 版本 | 1.21.1-1.11.38.127
| 端 | 双端
| 作者 | Noobanidus
| 链接 | https://minecraft.curseforge.com/projects/lootr
:::

> Generates unique loot for each player that opens a loot container.

**Lootr**（`lootr`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

把地牢、矿洞、村庄、要塞里的战利品箱变成「每人一份」：每个玩家第一次打开时看到自己的那份，别人开过不影响你，箱子外观会变成已开启的样子。多人服抢箱子、跑图重复刷同一片地牢时，它解决的就是「来晚了啥都没」的问题。

## 在赤物语里

- 玩家侧：看到箱子直接开，属于你的那份一直在；箱子上有玩家头颅贴图表示已被别人开过。破坏箱子只会掉你自己的那份内容，箱子会在一段时间后自动恢复。
- 服务端侧：`config/lootr-common.toml`：`[conversion]` 的 `disable` 关掉整个模组、`max_age` 是箱子恢复时间（默认 18000 tick），`[breaking]` 的 `enable_break` 允许破坏战利品箱、`[decay]` 的 `decay_value` 控制空箱消失时间、`[whitelist]` 用维度/模组 id 白黑名单排除特定箱子。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
