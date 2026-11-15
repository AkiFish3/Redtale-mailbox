---
title: 法术引擎（Spell Engine）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 法术引擎（Spell Engine）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-spell_engine-1201|1.20.1（1.20.1 服）]]

::: infobox Spell Engine
| Mod ID | `spell_engine`
| 版本 | 1.10.9
| 端 | 双端
| 作者 | Daedelus
:::

> Data driven magic library.

**Spell Engine**（`spell_engine`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

数据驱动的法术框架：法术的伤害、范围、冷却、施法动作都由 JSON 定义，作者不写代码就能加新法术；玩家侧统一了施法手感、法术书和冷却显示。赤物语里的法术书、法杖类内容都跑在它上面。

## 在赤物语里

- 玩家侧：法术靠法术书/法杖施放，看快捷栏上方的冷却图标；施法时移速会变慢，法术消耗法力或经验，具体看所用法术书。
- 服务端侧：`config/spell_engine/server.json5` 是全局规则：`movement_multiplier_speed_while_casting`（施法移速倍率）、`bypass_iframes`（高频法术是否穿无敌帧）、`spell_target_range_tolerance`（服务端判定容差）、`spell_cost_*` 系列管消耗与耐久；`elemental_weaknesses.json` 管元素克制，`weapon_fallback.json` 管无法术武器时的兜底。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
