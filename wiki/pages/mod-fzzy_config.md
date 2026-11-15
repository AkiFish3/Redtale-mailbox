---
title: Fzzy Config
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# Fzzy Config

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-fzzy_config-1201|1.20.1（1.20.1 服）]]

::: infobox Fzzy Config
| Mod ID | `fzzy_config`
| 版本 | 0.7.7+1.21+neoforge
| 端 | 双端
| 作者 | fzzyhmstrs
:::

> Configuration engine with automatic GUI generation, client-server syncing, powerful validation and error handling, and much more.

**Fzzy Config**（`fzzy_config`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给模组作者用的配置框架：从代码里的字段自动生成图形设置界面，带客户端/服务端同步、输入校验和出错回退。玩家感受到的是「很多模组的设置界面长得一样、改完立刻生效」，它本身不含玩法。

## 在赤物语里

- 玩家侧：用不到，只在模组列表的「配置」按钮里见到它生成的界面。
- 服务端侧：无独立配置文件；各模组真正的配置值仍写在 `config/` 下对应模组的文件里，这个库只负责界面与同步。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
