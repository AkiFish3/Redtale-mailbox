---
title: 队伍系统（FTB Teams）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 队伍系统（FTB Teams）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-ftbteams-1201|1.20.1（1.20.1 服）]]

::: infobox FTB Teams
| Mod ID | `ftbteams`
| 版本 | 2101.1.10
| 端 | 双端
| 作者 | FTB Team
:::

> FTB Teams adds ability to create your own teams that can be used for quests etc.

**FTB Teams**（`ftbteams`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给服务器加一层「队伍」概念：玩家自己建队、拉人、设队长和队员，队伍关系会被 FTB 全家桶共用。FTB 任务的进度共享、FTB Chunks 的区块共同认领，都靠它判断「谁和谁是一伙的」。

## 在赤物语里

- 玩家侧：按默认按键打开队伍界面（FTB Library 的侧栏）建队并邀请队友；建队后任务进度可以选「队伍共享」，认领的区块队友也能用。
- 服务端侧：`config/ftbteams-server.snbt`：`limited_lives` 是队伍共享生命数，默认 `0` 表示关闭；设成正数后队员死亡会扣队伍命，命耗尽时死亡的人被踢出队伍、队长死亡会顺位转让。改 `world/serverconfig/` 下的同名文件才不会被整合包更新覆盖。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
