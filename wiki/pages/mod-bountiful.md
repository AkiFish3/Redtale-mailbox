---
title: 悬赏板（Bountiful）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 悬赏板（Bountiful）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-bountiful-1201|1.20.1（1.20.1 服）]]

::: infobox Bountiful
| Mod ID | `bountiful`
| 版本 | 8.0.0-beta.2
| 端 | 双端
| 作者 | Ejektaflex
:::

> Bountiful adds bounty boards to the world.

**Bountiful**（`bountiful`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

在村庄里生成悬赏板，玩家右键接取每日委托（交物品、清怪、跑腿），完成后拿奖励货币与声望。想让玩家有稳定的日常目标、同时给经济系统一个产出与回收口时用它。

## 在赤物语里

- 玩家侧：右键村里的悬赏板接任务，做完回同一块板上交领奖；列表默认 45 秒刷新一次，超时的委托会过期。
- 服务端侧：`config/bountiful/bountiful.json`：`board.updateFrequencySecs` 刷新间隔、`bounty.shouldHaveTimersAndExpire` 是否限时过期、`bounty.fillerCurrencyPool` 指定奖励货币池（接经济模组时用）。任务内容写在 `bounty_pools/`、`bounty_decrees/` 下的 json。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
