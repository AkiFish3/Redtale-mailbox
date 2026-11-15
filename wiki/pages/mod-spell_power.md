---
title: 法术强度属性（Spell Power Attribute）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 法术强度属性（Spell Power Attribute）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-spell_power-1201|1.20.1（1.20.1 服）]]

::: infobox Spell Power Attribute
| Mod ID | `spell_power`
| 版本 | 1.6.0+1.21.1
| 端 | 双端
| 作者 | Daedelus
:::

> Spell Power entity attributes with related status effects and enchantments.

**Spell Power Attribute**（`spell_power`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给实体加一批「法术属性」：法术强度、法术暴击、法术急速、法术穿透等，配套状态效果和附魔，让法术伤害能像近战一样吃装备加成。想堆法术 build、拉暴击或急速时它提供底层数值。

## 在赤物语里

- 玩家侧：穿上带法术属性词条的装备或喝对应药水，面板数值随之提升，法术伤害/暴击率跟着变；具体词条看装备 tooltip，相关魔咒在附魔台可附。
- 服务端侧：`config/spell_power/attributes.json` 定义各属性的默认值、上下限与是否启用；要限法术暴击上限或调整成长曲线改这里。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
