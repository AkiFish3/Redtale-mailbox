---
title: 属性上限修复（AttributeFix）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 属性上限修复（AttributeFix）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-attributefix-1201|1.20.1（1.20.1 服）]]

::: infobox AttributeFix
| Mod ID | `attributefix`
| 版本 | 21.1.3
| 端 | 双端
| 作者 | Darkhax
| 链接 | https://www.curseforge.com/minecraft/mc-mods/attributefix
:::

> Extends the maximum attribute ranges to allow for higher values.

**AttributeFix**（`attributefix`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

原版给属性留了上限（护甲 30、生命 1024、攻击伤害 2048 等），超出的部分会被直接截断。它把上限抬到百万级，整合包堆属性才不失真。

## 在赤物语里

- 玩家侧：装备和药水给的高数值属性会真正生效、也显示得出来，不再被原版上限压回去。
- 服务端侧：`config/attributefix/<命名空间>/<属性>.json` 逐项改 `max`，例如 `minecraft/generic.max_health.json`；只改确实需要的那几项，别全放开。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
