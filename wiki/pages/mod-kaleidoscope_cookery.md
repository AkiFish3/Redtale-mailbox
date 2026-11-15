---
title: 万花筒烹饪（Kaleidoscope Cookery）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 万花筒烹饪（Kaleidoscope Cookery）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-kaleidoscope_cookery-1201|1.20.1（1.20.1 服）]]

::: infobox Kaleidoscope Cookery
| Mod ID | `kaleidoscope_cookery`
| 版本 | 1.6.0-neoforge+mc1.21.1
| 端 | 双端
| 作者 | ysbbbbbb, tartaric_acid, Azumic
:::

> A Minecraft mod that adds immersive cooking systems and delicious recipes to enhance your culinary adventure.

**Kaleidoscope Cookery**（`kaleidoscope_cookery`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

中式家常菜方向的烹饪模组：炒锅、蒸笼、灶台、案板一整套厨具，几十道菜和对应的buff，还有「饱食护盾」——吃饱状态下受伤会先扣饥饿而不是血。想认真做饭、开餐馆、给食物加玩法深度时用它。

## 在赤物语里

- 玩家侧：先做灶台和炒锅，放上食材按流程翻炒；成品菜有各自效果，吃满饱食度后会获得护盾，被打时先消耗饥饿值抵消伤害。
- 服务端侧：`config/kaleidoscope_cookery-common.toml` 的 `[cookery]`：`SatiatedShieldAbsorbEnabled` 开关饱食护盾，`SATIATED_SHIELD_MIN_FOOD_LEVEL` 是触发所需最低饥饿值（默认 4），`SATIATED_SHIELD_DAMAGE_REDUCTION_PERCENT` / `SATIATED_SHIELD_MAX_DAMAGE_REDUCTION` 控制减伤比例与上限，`SATIATED_SHIELD_ADDITIONAL_EXHAUSTION_PER_DAMAGE` 是每次受伤额外消耗的疲劳度。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
