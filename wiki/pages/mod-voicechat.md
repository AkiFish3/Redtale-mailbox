---
title: 简单语音（Simple Voice Chat）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 简单语音（Simple Voice Chat）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-voicechat-1201|1.20.1（1.20.1 服）]]

::: infobox Simple Voice Chat
| Mod ID | `voicechat`
| 版本 | 1.21.1-2.6.24
| 端 | 双端
| 作者 | Max Henkel
| 链接 | https://modrepo.de/minecraft/voicechat/overview
:::

> A working voice chat in Minecraft!

**Simple Voice Chat**（`voicechat`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

让服务器有真正的近距离语音：说话按距离衰减，附近的人听得到、远了就是杂音或听不见，还支持悄悄话和语音频道。赤物语用它当主要沟通方式，替代第三方语音软件。需要客户端也装同版本模组才能连。

## 在赤物语里

- 玩家侧：第一次进服先在语音设置里选麦克风、调好输入音量再点「连接」；游戏里默认按住 CAPS LOCK 说话（可改键），蹲下靠近自动变耳语，队友可组语音频道。
- 服务端侧：`config/voicechat/voicechat-server.properties`。`port=24455` 是语音专用的 UDP 端口（防火墙要单独放行，别和游戏端口复用，否则可能崩服）；`max_voice_distance`（当前 48）与 `whisper_distance`（当前 24）控制听音半径；改完重启生效。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
