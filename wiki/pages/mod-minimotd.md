---
title: MiniMOTD（服务器列表标语）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# MiniMOTD（服务器列表标语）

<!-- auto:begin -->

::: infobox MiniMOTD
| Mod ID | `minimotd`
| 版本 | 2.1.3
| 端 | 双端
| 作者 | jmp
| 链接 | https://github.com/jpenilla/MiniMOTD
:::

> Use MiniMessage text formatting in the server list MOTD.

**MiniMOTD**（`minimotd`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

改多人游戏列表里那两行服务器描述和右侧图标：支持用 MiniMessage 写渐变色、粗体、悬停提示，还能按时间段随机轮换多条 MOTD、伪装在线人数。想让服务器列表第一眼有点样子、或者做活动公告时用。

## 在赤物语里

- 玩家侧：不用做什么，刷新多人游戏列表就能看到效果；鼠标悬停能看到配置里写的额外提示文字。
- 服务端侧：`config/MiniMOTD/main.conf`：`motds=[...]` 里每条含 `line1`/`line2`/`icon`，`motd-enabled`、`icon-enabled` 总开关；`max-players` 与 `max-players-enabled` 控制列表显示的人数（当前写死 `69`），图标 PNG 放 `config/MiniMOTD/icons/`。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
