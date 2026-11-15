---
title: 区块边界（ChunkyBorder）
role: admin
group: 模组
order: 300
nav: no
auto: mod
---

# 区块边界（ChunkyBorder）

<!-- auto:begin -->

::: infobox ChunkyBorder
| Mod ID | `chunkyborder`
| 版本 | 1.2.18
| 端 | 双端
| 定位 | 服务端工具
| 作者 | pop4959
| 链接 | https://github.com/pop4959/ChunkyBorder
| jar | `ChunkyBorder-1.2.18.jar`
| 许可 | GNU GPLv3
:::

> Add a world border to your Chunky world

**ChunkyBorder**（`chunkyborder`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

给 Chunky 预生成的世界套一圈真正的边界，玩家越界会被弹回。想限制探索范围、控制存档体积时用。

## 在赤物语里

- 玩家侧：走到边界会被弹回并看到提示文字；地图插件（BlueMap、squaremap 等）上会画出边界线。
- 服务端侧：`config/chunkyborder/config.json` 的 `borderOptions`：`message` 越界提示文案、`preventMobSpawns` 边界外是否禁刷怪、`preventEnderpearl` / `preventChorusFruit` 是否禁末影珍珠与紫颂果穿越。边界本身用 `/chunkyborder` 命令设置。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
