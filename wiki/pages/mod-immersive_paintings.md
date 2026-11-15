---
title: 沉浸式画作（Immersive Paintings）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 沉浸式画作（Immersive Paintings）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-immersive_paintings-1201|1.20.1（1.20.1 服）]]

::: infobox Immersive Paintings
| Mod ID | `immersive_paintings`
| 版本 | 0.7.9
| 端 | 双端
| 作者 | Luke100000
| 链接 | https://conczin.net/
:::

> Use your own paintings!

**Immersive Paintings**（`immersive_paintings`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

把任意图片变成游戏里的画挂到墙上，支持任意尺寸、透明通道和自定义画框。装修展厅、还原现实照片、给自己基地挂张地图都行。

## 在赤物语里

- 玩家侧：用画布和染料合成空白画，手持后在界面上传图片并选尺寸，贴到墙上即可；别人的画默认也能看到。
- 服务端侧：`config/immersive_paintings/common_config.toml`：`maxUserImages` 限制每人上传张数（默认 1000），`maxUserImageWidth` / `maxUserImageHeight` 限制图片像素（默认 4096），`uploadPermissionLevel` 是上传所需权限等级（`0` 表示所有人都能传），`enableBundledPaintings` 控制是否带内置画作。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
