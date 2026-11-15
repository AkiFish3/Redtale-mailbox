---
title: YetAnotherConfigLib
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# YetAnotherConfigLib

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-yet_another_config_lib_v3-1201|1.20.1（1.20.1 服）]]

::: infobox YetAnotherConfigLib
| Mod ID | `yet_another_config_lib_v3`
| 版本 | 3.8.2+1.21.1-neoforge
| 端 | 双端
| 作者 | isXander
:::

> YetAnotherConfigLib (yacl) is just that. A builder-based configuration library for Minecraft.

**YetAnotherConfigLib**（`yet_another_config_lib_v3`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

配置界面库（YACL）：给模组作者提供一套现成的图形化设置界面框架——分类页签、滑杆、颜色选择器、按键绑定、搜索框都由它渲染。玩家侧体现为「很多模组的设置界面长得一样、能直接在游戏里改」，改完即时生效不用翻配置文件；单独装没有任何内容，缺了会让依赖它的模组（FTB 系列、大量 NeoForge 模组）打不开设置页甚至启动失败。

## 在赤物语里

- 玩家侧：在装了它的模组里按快捷键或从模组列表打开的设置界面，就是 YACL 画的；带搜索框的可以直接搜选项名。所有改动存在对应模组自己的配置文件里，YACL 本身不存设置。
- 服务端侧：`config/yacl.json5`：`showColorPickerIndicator`（当前 true，第一次用颜色选择器时闪提示，用过一次自动关）、`preloadComplexImageFormats`（当前 false，改成 true 会在资源重载时预加载 webp/gif，启动略慢但进游戏后不卡图）。纯客户端渲染相关，服务端改不改无所谓。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
