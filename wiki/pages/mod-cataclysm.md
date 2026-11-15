---
title: 灾厄之心（L_Ender's Cataclysm）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 灾厄之心（L_Ender's Cataclysm）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-cataclysm-1201|1.20.1（1.20.1 服）]]

::: infobox L_Ender's Cataclysm 1.21.1
| Mod ID | `cataclysm`
| 版本 | 3.33
| 端 | 双端
| 作者 | L_Ender
:::

> https://www.curseforge.com/minecraft/texture-packs/cataclysmic-tunes

**L_Ender's Cataclysm 1.21.1**（`cataclysm`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

大型 Boss 模组：往世界各处塞了十几个独立 Boss（末影守卫、下界合金巨兽、Ignis、远古残骸一类），每个都有专属地牢结构、召唤流程、多阶段战斗和掉落装备。想打有机制的高难 Boss、凑一套终局装备时，就是它。

## 在赤物语里

- 玩家侧：按各 Boss 的召唤物在对应结构里召唤（如末地城的末影守卫、下界的下界合金巨兽），打死后掉落专属材料，能做一整套带主动技能的武器与护甲，主动技能有独立冷却。
- 服务端侧：`config/cataclysm-common.toml` 按 `[mobs.<boss>]` 分节，每节下 `combat_config` 调攻击力/护甲/韧性，`cap_config` 是血量上限，`respawner_config` 管能否重复挑战；`[tools_and_abilities.<装备>]` 里是每件装备的 `attack_damage`、冷却（如 `incinerator_cooldown`）与符文伤害。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
