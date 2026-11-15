---
title: 沉浸式乐器（Immersive Melodies）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 沉浸式乐器（Immersive Melodies）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-immersive_melodies-1201|1.20.1（1.20.1 服）]]

::: infobox Immersive Melodies
| Mod ID | `immersive_melodies`
| 版本 | 0.8.0+1.21.1
| 端 | 双端
| 作者 | Luke100000
| 链接 | https://conczin.net/
:::

> Play custom melodies on various instruments and annoy your friends!

**Immersive Melodies**（`immersive_melodies`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

能真正「演奏」的乐器：鲁特琴、长笛、手鼓、小提琴等，可以导入 MIDI 曲谱自己弹，也能几个人合奏。办活动、开酒馆、给建筑配背景音乐时用。

## 在赤物语里

- 玩家侧：手持乐器后按界面选曲目，用键盘按键对应音符实时演奏；多人同时弹不同乐器会自动对齐节拍。
- 服务端侧：`config/immersive_melodies.json`：`maxAudibleDistance` 控制多远能听见（默认 48），`instrumentVolumeFactor` 调整整体音量，`bufferDelay` 是音符同步缓冲（默认 75），`mobInstrumentFactors` 决定哪些怪物也会演奏。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
