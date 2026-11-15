---
title: 开放领地与队伍（Open Parties and Claims）
role: player
group: 模组
order: 300
nav: no
auto: mod
---

# 开放领地与队伍（Open Parties and Claims）

<!-- auto:begin -->

**版本**：**1.21.1（当前）** ｜ [[mod-openpartiesandclaims-1201|1.20.1（1.20.1 服）]]

::: infobox Open Parties and Claims
| Mod ID | `openpartiesandclaims`
| 版本 | 0.26.3
| 端 | 双端
| 作者 | Xaero96 and other contributors
| 链接 | https://www.curseforge.com/minecraft/mc-mods/open-parties-and-claims
:::

> This mod adds the ability to claim and to forceload world chunks, as well as create and manage player parties. It also gives server owners powerful controls over their players' usage of the mod's features. The mod's API allows other mods or plugins to easily interact with the parties and the chunk claims, both on the server and the client side. Xaero's Minimap mod and World Map mods are recommende

**Open Parties and Claims**（`openpartiesandclaims`）是**双端**模组，服务端与客户端整合包都带它。

<!-- auto:end -->

## 中文简介

玩家自助领地系统：圈地保护方块与实体、给区块设强制加载、组队共享权限，服务器端还能限制每人可圈多少块、哪些维度不能圈。多人服想让大家自己管地盘、又不想装重型保护插件时用它。

## 在赤物语里

- 玩家侧：按 `P`（或配置的快捷键）打开界面，选两个角点圈地，可给队友或全服玩家单独开建造/交互/容器权限；队伍面板能邀请、踢人和共享领地，强制加载的区块在下线后仍保持加载。
- 服务端侧：`config/openpartiesandclaims-server.toml` 的 `[serverConfig]`：`defaultLanguage`（无模组玩家的服务端提示语言）、`[claims]` 下 `maxPlayerClaims` / `maxPlayerClaimForceloads` 限制数量（可用权限节点覆盖）、`[general]` 的 `claimableDimensions` 控制哪些维度可圈；玩家默认值在 `openpartiesandclaims-server.toml` 旁边的 `default-player-config` 里。

## 相关页面

- [[mod-index|模组总览]]
- [[modlist|模组清单（运维）]]
