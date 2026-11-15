---
title: 暮色战利品（Twilight Lootr）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 暮色战利品（Twilight Lootr）

<!-- auto:begin -->

::: infobox Twilight Lootr
| Mod ID | `twilight_lootr`
| 版本 | 1.21.1-0.0.0.1
| 端 | 双端
| 作者 | Noobanidus
| 链接 | https://minecraft.curseforge.com/projects/twilight-lootr
:::

> Generates a boss chest with instanced loot for everyone who participated in the kill.

**Twilight Lootr**（`twilight_lootr`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

把 Lootr 的「每人一份独立战利品」机制接到暮色森林的 BOSS 上：参与击杀的每个玩家都会拿到自己的宝箱内容，不会出现一个人开完其他人空手的情况。多人服打暮色 BOSS 时基本必备。

## 在赤物语里

- 玩家侧：打完 BOSS 后在你自己的宝箱界面里开箱，看到的是属于你的那份；别人开同一个箱子不影响你。
- 服务端侧：`config/twilight_lootr-common.toml`：`enable_decay`（当前 true，宝箱会过期消失）、`decay_time`（3600 tick = 3 分钟）。怕玩家来不及捡就把 `decay_time` 调大或关掉 decay。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
