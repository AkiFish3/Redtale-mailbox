---
title: 变更记录
role: admin
group: 管理员
order: 10
---

# 变更记录

新在上。只记「改了什么、为什么」，不记过程。

## 2026-11-02

**资源世界建成**
创建 `resource_world:overworld` 与 `resource_world:twilight_forest`，均验证为真实生成（暮色侧 `hedge_maze` 814 格、`final_castle` 679 格）。资源暮色的 `tfEnforcedProgression` 已单独关掉。
命名空间被模组写死为 `resource_world`，无法改成 `redtale:xxx`。

**移除 Multiworld（1.21.1）**
jar、配置、`world/dimensions/{myid,redtale}`、chunky 任务全备份到 `D:\redtale-ops\_removed_20261102\`。
连带影响：FTB Quests 章节里「进入资源世界」那条维度目标被删掉，任务从 4 个维度目标变 3 个。资源世界重建后可加回。

**装 Recurrent Complex Volts 0.7.3**
双端。服务端 224→225，客户端 231→232。内置结构按需求保持开启。
实测：`/locate structure reccomplex:natural_structure` 可用，启动后自动生成 8 个 decoration 结构。
**结论：它的箱子 Lootr 接管不了**，且默认不在暮色/资源世界生成。

**控制台美化 + 过滤 moved too quickly**
重写 log4j pattern，三段分色；`RegexFilter` 屏蔽速度检测刷屏；配置同步进 loader jar。

## 2026-10-31

**服务端搬家**
`D:\server*` → `E:\server*`（新装的 NVMe）。今后查服务端一律看 E 盘。

**备份路径改造**
`backup_location` 指向 `D:\mc_backups\server-1.20.1` / `server-1.21.1`（另一块盘）。
`minimum_free_space` 提到 20000 MB，防止写满 NVMe。
备份时间错开：旧服 05:00，新服 06:00（旧服单次约 40 分钟）。

**备份「不生成」的真正原因**
`only_if_players_been_online: true` —— 没人在线就跳过。已改 false。

**RCON 端口分离**
原本两服都是 25575，双开抢端口导致指令发错服。确定为：**新服 25576，旧服 25575**。

**旧服 Ledger 权限修复**
FTB Ranks 的 `admin` 组一条命令节点都没定义，OP 只能继承 `member` 的 `lg i` / `pg`。已补全 45 个 `command.ledger.*` 节点。

## 2026-10-29 ~ 10-30

**发展规划进入只读核查模式**
六个关键决策连续十余轮零答复、87 条行动零落地，按预设停机条件切换。

## 2026-10-28

**客户端整合包补齐**
`mods` 原本是空目录，全量复制服务端 223 个 jar + 7 个客户端 mod。

## 2026-10-25

**MOTD 与图标**
改在 MiniMOTD 层（`config/MiniMOTD/main.conf`），`server.properties` 的 `motd=` 已失效被覆盖。
双行渐变 + 两个随机变体，第 2 行之一为「治愈系 · Food / Adventure / Quest」。

---

## 记变更的规矩

1. **只写结论和原因**，不写探索过程。
2. 涉及不可逆操作的，写清楚**备份在哪**。
3. 连带影响要写——比如删一个模组导致任务书少一个目标，这种不写将来没人查得出来。
