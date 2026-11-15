---
title: 循环结构（Recurrent Complex）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 循环结构（Recurrent Complex）

<!-- auto:begin -->

::: infobox Recurrent Complex Volts
| Mod ID | `reccomplex`
| 版本 | 0.7.3.0
| 端 | 双端
| 作者 | Akiak, Ivorius
:::

> Adds structures to worldgen, handles exporting and importing structures, and provides build tools. This 1.21.1 NeoForge port keeps the legacy Recurrent Complex structure ecosystem as a compatibility target.

**Recurrent Complex Volts**（`reccomplex`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

老牌结构生成模组（原版移植到 NeoForge 1.21.1）：往世界里随机撒各种建筑、地牢、遗迹模板，还能在游戏里导出/导入结构、用作者的「建造工具」摆东西。想让世界生成更丰富、或者自己批量布置建筑群时用它。赤物语里作为兼容目标保留了旧版 RC 结构生态。

## 在赤物语里

- 玩家侧：跑图时会自然遇到它生成的各种结构和地牢，里面常带战利品；创作者模式下可用内置工具导出/导入 `.nbt` 结构模板。
- 服务端侧：结构模板与数据放在 `config/reccomplex/` 下（`structures`、`schematics`、`reports` 等子目录）；要增删生成的结构、调生成权重，把模板放进来或改这里的配置，重载生效。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
