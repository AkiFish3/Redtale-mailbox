---
title: 附魔禁用（Enchantment Disabler）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 附魔禁用（Enchantment Disabler）

<!-- auto:begin -->

::: infobox Enchantment Disabler
| Mod ID | `enchantmentdisabler`
| 版本 | 3.4.9
| 端 | 双端
| 作者 | pajic
| 链接 | https://modrinth.com/mod/enchantment-disabler
:::

> Disable enchantments and nerf enchanting in multiple ways with an extensive configuration

**Enchantment Disabler**（`enchantmentdisabler`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给服主一套开关，用来整块禁用某些附魔、压低附魔上限、限制村民书商交易等级，或者改附魔台的青金石与经验消耗。普通整合包里玩家的直观感受是「某些附魔怎么都刷不出来」。

## 在赤物语里

- 玩家侧：本服当前是默认状态（禁用列表为空、上限未改），附魔玩法和原版一致；哪天服里想压一压附魔强度，才会开始起作用。
- 服务端侧：`config/enchantmentdisabler/config.toml`：`[disabler]` 的 `disabledEnchantmentsV2` 填要禁的附魔 id，`[maxLevel]` 的 `globalMaxLevel` 压全局等级上限，`[enchantingTable]` 的 `modifyLapisCost` / `modifyXpCost` 改附魔台消耗公式。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
