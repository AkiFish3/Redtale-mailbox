---
title: 封包修复（PacketFixer）
role: admin
group: 模组
order: 300
nav: no
auto: mod
---

# 封包修复（PacketFixer）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-packetfixer-1201|1.20.1（1.20.1 服）]]

::: infobox PacketFixer
| Mod ID | `packetfixer`
| 版本 | 3.3.1
| 端 | 双端
| 定位 | 服务端工具
| 作者 | TonimatasDEV
| jar | `[优化]packetfixer-3.3.1-1.20.5-1.21.X-merged.jar`
| 许可 | MIT
:::

> A simple mod to solve various problems with packets.

**PacketFixer**（`packetfixer`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

放宽网络包与原版 NBT/字符串的大小上限，解决「发包过大」导致的踢出、区块加载失败、大箱子/大机械的 NBT 传不过去这类问题。装了大量内容模组、机器或容器一多就有人掉线时，先试它。

## 在赤物语里

- 玩家侧：用不到，装上即生效；如果之前因为「Packet too large」被踢，装完一般直接恢复。
- 服务端侧：`config/packetfixer.properties`：`packetSize`、`decoderSize`、`nbtMaxSize`、`stringSize`、`varInt21` 等上限，当前 `allSizesUnlimited=true` 走无限制档；要保守一点就设成 `false` 再单独调大 `nbtMaxSize`。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
