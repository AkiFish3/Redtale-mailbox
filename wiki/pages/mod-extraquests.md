---
title: FTB 任务扩展（ExtraQuests）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# FTB 任务扩展（ExtraQuests）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-extraquests-1201|1.20.1（1.20.1 服）]]

::: infobox ExtraQuests [FTB Quests]
| Mod ID | `extraquests`
| 版本 | 1.7.0
| 端 | 双端
| 作者 | Vecoo
:::

> Addon adds new tasks, rewards and functions.

**ExtraQuests [FTB Quests]**（`extraquests`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给 FTB Quests 补任务类型和奖励类型：多了一些原版没有的判定条件（比如检测物品、进度、统计）和奖励形式（发指令、给经验等）。做任务线时能把「做什么算完成」写得更细。

## 在赤物语里

- 玩家侧：看到的是任务书里多出来的任务条目，操作方式不变；奖励若是指令型，会在完成时自动执行。
- 服务端侧：`config/extraquests/config.yml`：`blacklist-console` 与 `blacklist-console-list` 决定指令奖励能执行哪些命令，默认已把 `op`、`gamemode` 拉黑，避免任务奖励被当成提权后门。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
