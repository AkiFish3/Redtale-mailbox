---
title: 服务端国际化 API（Server I18n API）
role: admin
group: 模组
order: 300
nav: no
auto: mod
---

# 服务端国际化 API（Server I18n API）

<!-- auto:begin -->

::: infobox Server I18n API
| Mod ID | `server_i18n_api`
| 版本 | 1.5
| 端 | 双端
| 定位 | 服务端工具
| 作者 | IAFEnvoy
| jar | `server_i18n_api-1.5.2-1.21.3-neoforge.jar`
| 许可 | LGPL-3.0
:::

> Server side standalone i18n system, for server side only mods.

**Server I18n API**（`server_i18n_api`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

IAFEnvoy 出品的服务端专用国际化（i18n）库：给「只跑在服务端」的模组提供一套独立的多语言文案系统，让这些模组也能按玩家语言发提示、报错，而不依赖客户端的语言文件。玩家看不到它，只作为服务端模组的底层依赖。定位是服务端工具。

## 在赤物语里

- 玩家侧：用不到，纯服务端前置；它只决定服务端模组的提示文字用哪种语言发给你。
- 服务端侧：无独立服务端配置文件（多语言行为由依赖它的服务端模组控制）；作为依赖库，服务端装同版本即可。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
