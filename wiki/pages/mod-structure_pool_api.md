---
title: 结构池 API（Structure Pool API）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 结构池 API（Structure Pool API）

<!-- auto:begin -->

::: infobox Structure Pool API
| Mod ID | `structure_pool_api`
| 版本 | 1.2.1+1.21.1
| 端 | 双端
| 作者 | Daedelus
:::

> Allows injecting structures into structure pools.

**Structure Pool API**（`structure_pool_api`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给模组/数据包作者用的接口，能把自定义结构注入已有的结构池（比如往村庄、前哨的生成池里加自己的建筑），不用整包替换原版结构集。玩家侧感受到的是「村庄多了几种房子」。

## 在赤物语里

- 玩家侧：用不到，纯前置/数据包接口；装了依赖它的结构模组后，跑图会遇到被注入的新建筑。
- 服务端侧：无独立服务端配置文件；注入规则写在依赖它的模组或数据包的 JSON 里。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
