---
title: 测试服 server-test
role: admin
group: 管理员
order: 13
nav: no
---

# 测试服 `E:/server-test`

给 RedtaleProject 验证用的最小服务器。**和正式服完全隔离**：独立目录、独立 world、独立端口、独立内存。

| 项 | 测试服 | 1.21.1 正式服 | 1.20.1 服（在跑） |
|---|---|---|---|
| 版本 | NeoForge **21.1.257** / MC 1.21.1 | 同版（`libraries` 直接复制，177 MB） | Fabric / 1.20.1 |
| 目录 | `E:/server-test` | `E:/server-1.21.1` | `E:/server` |
| 游戏端口 | **25567** | 25566 | 25565 |
| RCON | **25577** | 25576 | 25575 |
| 内存 | `-Xms2G -Xmx4G` | 7G / 12G | 7G / 12G |
| `level-type` | `minecraft:normal` | `wover:normal` | — |
| `online-mode` | `false` | `false` | `false` |
| 启动 | `run-test.bat` | `启动.bat` | `启动.bat` |

三个服的端口是**故意错开**的（同一台机器可能同时开两个）。`PLAN.md` 里写的「正式服 25565 / 25575」指的是 1.20.1 那台，项目真正要对齐的是 1.21.1 的 25566 / 25576。

## 装了哪 12 个

全是**库型前置，没有玩法内容**：

```
architectury 13.0.11      cloth-config 15.0.140    kotlinforforge 5.11.0
resourcefullib 3.0.12     glitchcore 2.1.0.2       curios 9.5.1
geckolib 4.9.3            azurelib 3.1.19          attributefix 21.1.3
bookshelf 21.1.81         prickle 21.1.11          terrablender 4.1.0.8
```

::: note 首次启动的坑
`attributefix` 硬依赖 `bookshelf` + `prickle`，缺任一个直接 FATAL：`requires bookshelf 21.1 / prickle 21.1`。
补齐后 `Done (5.354s)!`，12 mods，RCON 正常，`Preparing spawn area` 通过。
:::

## 用法约定

- **只加不改**：要测某个模组冲突，临时把 jar 丢进 `mods/`，测完移除。**不要把它当正式服副本。**
- 正式服的 `world` / `mods` / `config` 任何东西都**不能从这里同步回去**。
- 测试服的 `world` 可以直接删掉重建（本来就是一次性的）。
- 验证完记得停进程 —— 2G/4G 也是内存，别和正式服抢。

## 为什么用最小模组集

正式服 271 个模组，任何一个报错都会淹没真正的错误。

测试服只留 12 个库型前置，跑自己的 jar，日志里出现异常就能直接定性是不是自己的问题。**先在空服务器上跑通，再进正式服。**
