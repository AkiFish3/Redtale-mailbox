---
title: Chunky
role: admin
group: 模组
order: 300
nav: no
auto: mod
---

# Chunky

<!-- auto:begin -->

::: infobox Chunky
| Mod ID | `chunky`
| 版本 | 1.4.23
| 端 | 双端
| 定位 | 服务端工具
| 作者 | pop4959
| 链接 | https://github.com/pop4959/Chunky
| jar | `[优化]Chunky-NeoForge-1.4.23.jar`
| 许可 | GNU GPLv3
:::

> Pre-generates chunks, quickly, efficiently, and safely

**Chunky**（`chunky`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

区块预生成工具：提前把地图生成好，减少玩家跑图时的卡顿与卡区块。开新图、加新维度、扩边界之后必跑一次。

## 在赤物语里

- 玩家侧：玩家用不到，属于管理员维护工具；跑预生成时会有刷屏提示，可以 `/chunky silent` 关掉播报。
- 服务端侧：配置在 `config/chunky/`（`config.json` 管播报与重启续跑），进度存档在 `config/chunky/tasks/<维度>/`。当前存档里主世界是半径 7000 方块方形（中心 0,0），资源维度 `minecraft:ziyuan` 是半径 5000。

## 什么时候该用

- **开新周目 / 换图**：先跑完再开放，否则玩家跑到没生成的区块会卡顿，甚至卡进未生成地形。
- **加了新维度或扩了世界边界**（配合 [[mod-chunkyborder|ChunkyBorder]]）：只对新区域补跑，别整张重跑。
- **跑图卡顿成片出现**：先 `/spark tps` 看是不是区块生成引起的，再决定要不要补生成。
- **不要在有玩家在线时大范围跑**：单核吃满会让 TPS 掉到 10 以下。夜里跑，或者限半径分段跑。

## 命令怎么写

按顺序四步：定中心 → 定形状和半径 → 选维度 → 开跑。

```text
/chunky world minecraft:overworld     # 选维度（不写就是当前所在维度）
/chunky center 0 0                    # 定中心坐标
/chunky shape square                  # 形状：square / circle / diamond / pentagon / hexagon / star
/chunky radius 7000                   # 半径，单位方块
/chunky pattern region                # 生成顺序：region 按区块文件扫，最快
/chunky start                         # 开跑
```

跑起来之后常用：

```text
/chunky progress     # 看进度、预计剩余时间
/chunky pause        # 暂停（服务器重启前先停）
/chunky continue     # 继续
/chunky cancel       # 取消，已生成的区块保留
/chunky silent       # 开关刷屏播报
/chunky trim         # 把边界外的区块裁掉（要再输一次 confirm 才执行，危险）
```

- 半径 7000 的方形 ≈ 77 万区块，实测按天算，不是按小时。
- `continueOnRestart` 在 `config/chunky/config.json` 里，默认 `false`：重启后要手动 `/chunky continue`。
- 任务存档在 `config/chunky/tasks/<维度>/`，一个 `.properties` 就是一次任务，想重置就删掉对应文件再 `/chunky reload`。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
