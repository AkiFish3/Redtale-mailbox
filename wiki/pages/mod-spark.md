---
title: spark
role: admin
group: 模组
order: 300
nav: no
auto: mod
---

# spark

<!-- auto:begin -->

::: infobox spark
| Mod ID | `spark`
| 版本 | 1.10.124
| 端 | 双端
| 定位 | 服务端工具
| jar | `spark-1.10.124-neoforge.jar`
| 许可 | GPLv3
:::

> spark is a performance profiling plugin/mod for Minecraft clients, servers and proxies.

**spark**（`spark`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

性能诊断工具：采样 TPS、各线程耗时、内存与堆，把报告生成一个网页链接。服务器卡但说不清卡在哪时，第一个该用的就是它。

## 在赤物语里

- 玩家侧：玩家用不到；`/spark tps` 任何人都能看，卡的时候可以自己先确认是服务器整体卡还是自己网络卡。
- 服务端侧：配置在 `config/spark/config.json`（`backgroundProfiler: true` 表示常驻后台采样，出问题可以直接导出）。命令要 op（权限等级 4）。

## 什么时候该用

- **玩家集体喊卡**：先 `/spark tps` 确认是 TPS 低（服务端算不过来）还是 TPS 正常（那就是网络/客户端问题）。
- **TPS 低但看不出原因**：跑 30 秒 profiler，看哪个模组/实体/区块加载占大头。
- **内存缓慢上涨**：`/spark heapsummary` 看对象占用，排除实体或区块泄漏。
- **单次卡顿尖峰**：`/spark tickmonitor` 挂着，超过阈值的 tick 会打日志，能定位到具体时刻。

## 命令怎么写

```text
/spark tps                                  # 当前 TPS / MSPT 概览，最轻量
/spark profiler start --timeout 30          # 采样 30 秒后自动停，给出网页链接
/spark profiler start --timeout 60 --only-ticks-over 100   # 只抓超过 100ms 的慢 tick
/spark profiler stop                        # 手动停（不带 --timeout 时用）
/spark health                               # 整体健康报告：CPU、内存、磁盘
/spark heapsummary                          # 堆内存摘要
/spark tickmonitor --threshold 100          # 监控慢 tick，超过 100% 才记录
/spark tickmonitor --threshold 0            # 关闭监控
/spark ping                                 # 看自己到服务器的延迟
```

- 报告会打印形如 `https://spark.lucko.me/xxxxx` 的链接，直接发给人看，不用截图。
- 采样期间有额外开销，别在人多的时候长时间跑；30–60 秒足够。
- `/spark gc` 会触发一次完整 GC，**只在确认内存异常时用**，会造成一次明显卡顿。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
