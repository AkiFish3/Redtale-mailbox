---
title: 现代修复（ModernFix）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 现代修复（ModernFix）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-modernfix-1201|1.20.1（1.20.1 服）]]

::: infobox ModernFix
| Mod ID | `modernfix`
| 版本 | 5.27.26+mc1.21.1
| 端 | 双端
| 作者 | embeddedt
| 链接 | https://modrinth.com/mod/modernfix
:::

> Egregious, yet effective performance improvements for modern Minecraft

**ModernFix**（`modernfix`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

针对 1.16+ 版本的启动与运行性能补丁集：缩短启动时间、降低内存占用、加速资源加载与动态注册表构建，顺带修掉一批原版与常见模组的卡顿源。整合包模组多、启动慢、内存吃紧时，它是收益最直接的那一档。

## 在赤物语里

- 玩家侧：用不到，装上即生效；个别优化会改变内部实现，遇到偶发 bug 时先看是不是它引起的。
- 服务端侧：`config/modernfix-common.toml`（如 `blacklist_async_jei_plugins` 把不兼容的 JEI 插件拉回主线程）与 `config/modernfix-mixins.properties`，后者用 `mixins.<名字>=false` 单独关某项优化，默认建议保持全开。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
