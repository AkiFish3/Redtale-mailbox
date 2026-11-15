---
title: 暮色森林（The Twilight Forest）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 暮色森林（The Twilight Forest）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-twilightforest-1201|1.20.1（1.20.1 服）]]

::: infobox The Twilight Forest
| Mod ID | `twilightforest`
| 版本 | 4.8.3345
| 端 | 双端
| 作者 | Benimatic, AtomicBlom, Drullkus, Killer_Demon, quadraxis, Tamaized, williewillus, Andromander, GizmoTheMoonPig, jodlodi, SleepyHorse
| 链接 | https://www.curseforge.com/minecraft/mc-mods/the-twilight-forest
:::

> An enchanted forest dimension.

**The Twilight Forest**（`twilightforest`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

经典的大型冒险维度：一片永远黄昏的森林，按「迷宫—BOSS—解锁下一层」的进度推进，十来个主题迷宫（树篱、沼泽、雪原、暗黑塔、巨魔洞）各有专属 BOSS 和战利品。想玩有明确目标线的 PvE 内容、而不是散落地牢时，这是主菜。

## 在赤物语里

- 玩家侧：用钻石丢进 2×2 水坑中心的花上（周围铺一圈植物）开传送门进入；进度按 BOSS 顺序解锁，跳级会卡住。BOSS 掉落进宝箱而不是直接掉地上，多人一起打会按人数加掉落。
- 服务端侧：`config/twilightforest-common.toml`：`bossesSpawnDropChests`（当前 true，掉落进出生点宝箱）、`casketUUIDLocking`（死亡棺材是否只给本人开）、多玩家 BOSS 难度模式（`NONE`/`MORE_LOOT`/`MORE_HEALTH`）、`cloudBlockPrecipitationDistance`（降到 32 以下可缓解云层卡顿）。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
