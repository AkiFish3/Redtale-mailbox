---
title: 模组清单
role: admin
group: 管理员
order: 5
---

# 模组清单

## 数量

| 端 | 数量 | 备注 |
|---|---|---|
| 服务端 1.21.1 | 226 | `E:\server-1.21.1\mods` |
| 客户端 1.21.1 | 234 | 服务端 226 + 客户端独有 8 |
| 服务端 1.20.1 | 271 | `E:\server\mods` |

权威表格：`D:\redtale-ops\_srv_MODLIST_1.21.1.xlsx`。

> 2026-11-02 新增：DBE's Spark Engine（双端）、LDLib2 2.2.44（仅客户端）。
> 详见 `mobs.md`。

## 客户端独有的 8 个

| 模组 | 作用 |
|---|---|
| Jade 15.10.6 | 方块/生物信息 |
| REI 16.0.799 | 配方查询 |
| mafglib 0.4.3 | MASA 移植的前置库 |
| Forgematica 0.4.3 | Litematica 的 NeoForge 版 |
| BoccHUD 0.4.1 | MiniHUD 移植 |
| Tweakerge 0.4.3 | Tweakeroo 移植 |
| Rock'n Roller 0.4.0 | ItemScroller 移植 |
| LDLib2 2.2.44 | Spark Engine 前置（`side=CLIENT`，服务端不要） |

> **MASA 全家桶官方只做 Fabric。** Forge/NeoForge 上的这些都是第三方移植，作者用 MaFgLib 系列改名发布。mafglib 0.4.x 起不再需要 ForgedFabricLoaderAPI。

## 客户端为什么必须全量复制

NeoForge 连服靠**注册表与网络通道对齐**。少一个注册了方块/物品/数据包的模组，就会在 configuration 阶段直接断连——不是「看不到」，是**进不去**。

所以规则是：**服务端 mods 整个文件夹复制到客户端，再在上面加客户端专属的。** 不要逐个挑。

例外：`ftbbackups2`、`ftb-ranks` 带 `IGNORE_SERVER_VERSION`，客户端加载无害。

## 世界生成相关的几个

| 模组 | 状态 | 说明 |
|---|---|---|
| Twilight Forest 4.8.3345 | 在用 | 暮色森林主体 |
| Resource World 2.0 | 在用 | 资源世界，**命名空间写死 `resource_world`** |
| Ruins 1.21.1.2NF | 在用 | 模板遗迹，**不走原版结构系统** |
| Recurrent Complex Volts 0.7.3 | 在用 | 结构生成，`/locate structure reccomplex:natural_structure` |
| Lootr 1.11.38 | 在用 | 按玩家独立战利品 |
| twilight_lootr | 在用 | Lootr 的暮色适配 |
| Astruct 0.1.1 | **未装** | 试验性，能精确锁维度 |

## 已知的坑

**mobfilter**（旧服）——jar 因文件锁没删掉，但配置已删，**它从未生效过**（json5 语法错，每次启动都 load 失败）。删它不影响游戏行为。

**AtomSweep**（旧服）——每 10 分钟清一次，白名单 26 项，牛羊猪兔不在里面。真正生效的配置是 `atom/sweep/config.toml`，不是 `config/sweeper-common.toml`（那是死文件）。

**Multiworld**——已从 1.21.1 移除，jar、配置、残留维度都备份在 `D:\redtale-ops\_removed_20261102\`。

## 加模组的流程

1. 服务端 `mods/` 放进去
2. **同一个 jar 复制到客户端** `mods/`
3. 重启服务端，看日志有没有 `Missing or unsupported mandatory dependencies`
4. 客户端进服验证

只做第 1 步，玩家就连不上了。
