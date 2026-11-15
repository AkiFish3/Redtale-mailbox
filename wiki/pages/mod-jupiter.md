---
title: Jupiter
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# Jupiter

<!-- auto:begin -->

::: infobox Jupiter
| Mod ID | `jupiter`
| 版本 | 2.3.7
| 端 | 双端
| 作者 | IAFEnvoy
:::

> A powerful, auto sync config library.

**Jupiter**（`jupiter`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

自动同步的配置库：服务端改了配置，客户端连进来会自动拉到同一份值，避免「单机和联机设置不一致」的怪问题。是若干模组的前置依赖，本身没有内容。

## 在赤物语里

- 玩家侧：用不到，连服时会自动同步配置。
- 服务端侧：无独立配置文件；`config/jupiter.json` 只有 `general` 几个开关（是否加载 Forge/Cloth 配置、配置按钮的替换方式），一般不用改。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
