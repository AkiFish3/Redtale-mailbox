---
title: 聊天样式（Styled Chat）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 聊天样式（Styled Chat）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-styledchat-1201|1.20.1（1.20.1 服）]]

::: infobox Styled Chat
| Mod ID | `styledchat`
| 版本 | 2.6.0-1.21-neo
| 端 | 双端
| 作者 | Patbox, LostPattern
:::

> Change look of yours server chat!

**Styled Chat**（`styledchat`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

服务端侧美化聊天：给聊天加颜色、粗体、悬停提示和点击事件，支持 Markdown、链接识别、@提及和表情，还能按权限给不同组不同格式。嫌服务器聊天是原版白字时用它。

## 在赤物语里

- 玩家侧：正常打字即可，可用 `*斜体*`、`**粗体**`、`~~删除线~~` 和直接贴链接（能否用取决于服主开的开关）；点聊天里的名字可能有动作（传送/私聊），看服务器配置。
- 服务端侧：`config/styled-chat.json`：`text_formatting` 段管 Markdown、链接解析、提及开关；`auto_completion` 段管标签/表情补全；各组具体格式在 `styles`/`formats` 段按权限配。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
