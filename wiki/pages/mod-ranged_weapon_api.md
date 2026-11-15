---
title: 远程武器 API（RangedWeaponAPI）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 远程武器 API（RangedWeaponAPI）

<!-- auto:begin -->

::: infobox RangedWeaponAPI
| Mod ID | `ranged_weapon_api`
| 版本 | 3.0.0+1.21.1
| 端 | 双端
| 作者 | Daedelus
:::

> Allows creating bows and crossbows, with just a few line of code

**RangedWeaponAPI**（`ranged_weapon_api`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

Daedelus 给模组作者用的武器框架：用很少的代码就能注册新的弓、弩和对应的弹药、拉弓动画与伤害逻辑。玩家看到的是一批风格统一的远程武器模组（同作者系列），它本身不含可直接用的武器。做弓弩类模组都靠它打底。

## 在赤物语里

- 玩家侧：用不到，纯前置；依赖它的武器模组在它缺失时无法启动。
- 服务端侧：无独立服务端配置文件；武器数值写在依赖它的模组里。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
