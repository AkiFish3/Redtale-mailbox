---
title: TerraBlender
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# TerraBlender

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-terrablender-1201|1.20.1（1.20.1 服）]]

::: infobox TerraBlender
| Mod ID | `terrablender`
| 版本 | 1-4.1.0.8
| 端 | 双端
| 作者 | Adubbz
| 链接 | https://www.curseforge.com/minecraft/mc-mods/terrablender
:::

> A library mod for adding biomes in a simple and compatible manner with Minecraft's new biome/terrain system.

**TerraBlender**（`terrablender`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给模组作者用的群系注册 API，让多个模组往主世界/下界/末地塞自己群系时不会互相打架，也决定各家群系在地图上占多大地盘。玩家一般看不到它，但暮色森林以外的群系类模组（地理类、生物群系扩展）几乎都靠它落地；缺了会直接崩在启动阶段。

## 在赤物语里

- 玩家侧：用不到，纯前置；依赖它的模组提供的新群系能不能正常出现，取决于这里的区域设置。
- 服务端侧：`config/terrablender.toml`：`overworld_region_size`（当前 3）控制主世界群系区域块的大小，`nether_region_size`（2）同理；`vanilla_overworld_region_weight`（10）越高越偏原版群系。改大区域=各模组群系成片出现，改小=更细碎交错。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
