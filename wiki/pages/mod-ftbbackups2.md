---
title: FTB Backups 2
role: admin
group: 模组
order: 300
nav: no
auto: mod
---

# FTB Backups 2

<!-- auto:begin -->

::: infobox FTB Backups 2
| Mod ID | `ftbbackups2`
| 版本 | 1.0.28
| 端 | 双端
| 定位 | 服务端工具
| 作者 | CreeperHost
| jar | `[辅助]ftbbackups2-neoforge-1.21-1.0.28.jar`
| 许可 | All Rights Reserved
:::

> Backup all the things!

**FTB Backups 2**（`ftbbackups2`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

定时整包备份：把世界目录、配置和模组列表压成 zip 丢到指定目录，按 cron 自动跑。改配置、清地形、装删模组之前先手动备份一次，出事了能整包回滚。它是「出事了」和「没出事」之间唯一的那层保险。

## 在赤物语里

- 玩家侧：完全感知不到。备份提示只发给 op（`notify_op_only: true`），也不占带宽。
- 服务端侧：配置在 `config/ftbbackups2.json`。当前值：每天 06:00 自动备份（`backup_cron`）、保留最近 5 份（`max_backups`）、ZIP 格式、落点 `D:/mc_backups/server-1.21.1`、剩余空间不足 20 GB 就放弃本次。

## 什么时候该用

- **改配置 / 装删模组 / 清区块之前**：先 `/backup` 手动来一份，把当前状态钉死。
- **出问题要回档**：去 `D:/mc_backups/server-1.21.1` 按时间戳挑，选问题发生之前的那份。
- **磁盘告警**：先查这个目录，5 份整包几十 GB 很常见，再考虑调小 `max_backups`。
- **别和预生成撞车**：跑 [[mod-chunky|Chunky]] 时世界文件正在写，这时候压包可能压出不一致的数据。

## 命令怎么写

只有一条命令，其余全靠配置：

```text
/backup      # 立刻手动备份一次（command_permission_level = 3，即 op）
```

关键配置项（`config/ftbbackups2.json`）：

| 键 | 当前值 | 说明 |
|---|---|---|
| `enabled` | `true` | 关掉 = 完全不做自动备份 |
| `backup_cron` | `0 0 6 1/1 * ? *` | Quartz cron，现在是每天 06:00 |
| `max_backups` | `5` | 只留最近 5 份，超出自动删 |
| `backup_location` | `D:/mc_backups/server-1.21.1` | 落点，别放系统盘 |
| `backup_format` | `ZIP` | 改 `DIRECTORY` 则不压缩，快但占空间 |
| `minimum_free_space` | `20000` | 剩不到 20 GB 就放弃本次 |
| `only_if_players_been_online` | `false` | 改 `true` 可跳过没人玩的空转备份 |
| `excluded` | `[]` | 排除项，例如 `logs/`、`crash-reports/` |

- 改配置无需重启，下一次触发时读取。
- 恢复流程：停服 → 先把当前 `world/` 改名留底 → 解压备份覆盖 → 起服。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
