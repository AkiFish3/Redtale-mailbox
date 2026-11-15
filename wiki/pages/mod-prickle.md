---
title: Prickle（JSON 配置库）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# Prickle（JSON 配置库）

<!-- auto:begin -->

::: infobox PrickleMC
| Mod ID | `prickle`
| 版本 | 21.1.11
| 端 | 双端
| 作者 | Darkhax
| 链接 | https://www.curseforge.com/minecraft/mc-mods/prickle
:::

> Bringing Prickle, the JSON based configuration file format to Minecraft.

**PrickleMC**（`prickle`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

Darkhax 做的配置库，把模组的配置文件格式改成基于 JSON、带注释和自动重载的方案，让依赖它的模组能用更省心的方式读写设置。玩家看不到它，只作为底层依赖存在。装了 Darkhax 系模组时它才会出现。

## 在赤物语里

- 玩家侧：用不到，纯前置；依赖它的模组的设置文件由它管理。
- 服务端侧：无独立服务端配置文件；它的配置是给下游模组用的，各自写在自己的 config 里。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
