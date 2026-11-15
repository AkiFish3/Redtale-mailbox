---
title: 万花筒玩偶（Kaleidoscope Doll）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 万花筒玩偶（Kaleidoscope Doll）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-kaleidoscope_doll-1201|1.20.1（1.20.1 服）]]

::: infobox Kaleidoscope Doll
| Mod ID | `kaleidoscope_doll`
| 版本 | 1.4.2-neoforge+mc1.21.1
| 端 | 双端
| 作者 | ysbbbbbb
:::

_（模组 jar 里没有写简介）_

**Kaleidoscope Doll**（`kaleidoscope_doll`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

能摆能丢的装饰玩偶：把各种角色做成小布偶，可以摆在方块上、挂在幻翼身上，也能拿在手里丢出去互相打闹。装点房间、做展台、给据点加一点生气时用得上，跟万花筒烹饪是同一个作者的周边向模组。

## 在赤物语里

- 玩家侧：合成玩偶后右键摆在地上或桌上，空手右键取回；手持玩偶右键可以丢出去，砸到生物会有一点击退。幻翼有小概率带着玩偶生成，打下来能捡。
- 服务端侧：`config/kaleidoscope_doll-common.toml` 的 `[doll]`：`EnableSponsoredDoll` 控制赞助玩偶是否出现，`DollCanBeThrown` / `DollCanKnockbackEntities` 管丢出与击退，`EnablePhantomDollSpawn` 与 `PhantomDollSpawnChance`（默认 `0.03`）控制幻翼带玩偶的概率。自定义玩偶图放 `config/kaleidoscope_doll/custom/`。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
