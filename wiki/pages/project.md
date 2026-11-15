---
title: RedtaleProject · 项目主页
role: admin
group: 管理员
order: 2
---

# RedtaleProject

把 Bukkit 系 RPG 套件（MMOItems / MMOCore / MMOInventory / EcoEnchants / MythicMobs）的能力，在 **Minecraft 1.21.1 + NeoForge** 上自研重做成一个模组。不做兼容层、不跑 Hybrid。

| 项 | 值 |
|---|---|
| **Mod ID** | `redtale_project` —— 已定，上线后基本改不动（物品/方块/属性/附魔 ID 全带它） |
| **源码** | `E:/RedtaleProject` |
| **jar 与反编译缓存** | `D:/redtale-work` |
| **测试服** | `E:/server-test`（25567 / RCON 25577），与正式服完全隔离 |
| **队列** | S7，每天 10:00，工作目录 `E:/RedtaleProject` |
| **规划原文** | `E:/RedtaleProject/PLAN.md`（v2，2026-11-15），本页是给人读的摘要 |

## 要做什么

| 源码集 | 职责 |
|---|---|
| `core` | 属性注册表、`StatValue{base,scale,spread,maxSpread}`、伤害管线、脚本层（effect/trigger/condition）、配置热载、GUI 基座 |
| `items` | 物品类型、武器、宝石与孔、套装、技能绑定、掉落表 |
| `inventory` | Curios 槽位映射、4 类限制（职业/等级/Lore/权限）、装备面板 |
| `enchants` | 附魔 schema → 生成内置 datapack → 真实 `Enchantment` 注册表项 |
| `mobs` | 模板实体、属性/等级缩放、技能原语、刷怪规则 |
| `progression` | 等级、经验源、职业、属性点（对应 MMOCore） |

现在**打成一个单体 jar**，内部按上面拆源码集；将来要拆系列模组时直接搬目录，不用重写。

## 做到哪了

| 项 | 状态 |
|---|---|
| 规划 | ✅ v2 定稿（14 条决策 D1~D14） |
| 上游盘点 | ✅ 六个插件 jar 的证据级盘点（`docs/UPSTREAM-1-Inventory.md`） |
| 数值管线 | ✅ 设计文档完成（`docs/DAMAGE-PIPELINE.md`，328 行） |
| 测试服 | ✅ 已建成并成功引导（`Done (5.354s)!`，12 前置） |
| 源码 | ⬜ `src/` 尚空，Gradle 工程未建 |
| 当前阶段 | **M0 准备中** |

| 阶段 | 内容 | 出口条件 |
|---|---|---|
| **M0** 地基 | Gradle(JDK21 / ModDevGradle) + 配置热载 + 脚本层骨架 | `/redtale reload` 生效，一条配置能触发一个 effect |
| M1 属性 | 属性注册表 + `StatValue` 四段式 + 伤害管线 | 3 个自定义属性能算出伤害并显示在 Lore |
| M2 武器 | 物品类型 + 等级门槛 + Lore 生成 + 掉落表 | 一把自定义剑打出自定义伤害/暴击 |
| M3 宝石/套装 | 孔位、镶嵌/取出、套装件数加成 | 3 件套触发加成，Lore 正确 |
| M4 附魔 | 附魔 schema → datapack 生成 → 2 个示例 | 示例附魔书可附魔、铁砧合并、砂轮去除 |
| M5 技能 | 技能原语 + 绑定 + 冷却/消耗 | 右键释放技能，冷却消耗正确 |
| M6 怪物 | 模板实体 + 技能/掉落/刷怪/等级缩放 | 配置出来的怪能放技能并掉落 |
| M7 进度 | 等级、经验源、职业、属性点 | 打怪给经验，升级加属性点 |

## 三条不能破的规矩

**一、只吃「库型」前置。** 白名单：GeckoLib / AzureLib / PlayerAnimator / Architectury / Cloth Config / Curios / Resourceful Lib / AttributeFix / KotlinForge。`spell_power`、`spell_engine`、Iron's Spells 这类**玩法型** mod 明确排除，连属性都不复用 —— 属性全部自建，零 mod 依赖。

**二、不覆盖式改写伤害。** 绝不 `setAmount(我们算的)`，否则会把前面所有 mod 的加成一并抹掉。先加后乘，超限走递减曲线，tooltip 与结算共用一个 `settle()`。

**三、「注册表项」必须一次预制够。** 新 `EntityType`、新 `Attribute`、新 effect 原语、新 DataComponent 类型都是启动期冻结的，**不能热加**；装备/宝石/套装/附魔/怪物配置/经验曲线全是数据，写 JSON5 + `/redtale reload` 即可。

详见 [[project-design|架构与数值]]。

## 还空着的四个问题

| # | 问题 | 倾向 | 卡在哪 |
|---|---|---|---|
| 1 | 属性预制多少条 | **64 条**（近战 12 / 防御 18 / 法术 18 / 采集移动 10 / 通用 6） | 等反编译 MythicLib 按它的表补齐后定 |
| 2 | 技能原语第一批做几个 | 24 个（直伤/范围/投射物/位移/增益/减益/召唤/治疗） | 未定稿 |
| 3 | 套装首批做几套 | 先 2 套示范，数据可热加，不阻塞 | 非阻塞 |
| 4 | 职业是否照 MMOCore 分类 | 倾向按赤物语世界观自定（战士/游侠/法师…） | 等 M7 |

::: warn 需要 Aki 点头的两件
第 1 条（属性 64 条）和第 4 条（职业分类）会写进注册表或影响世界观，定下来就不好回头。其余两项队列可自行推进。
:::

## 队列进度（S7 自动维护）

下面这段由 S7 每轮覆写（每天 10:00）。标记之外的文字队列不碰，可以放心手改。

<!-- s7:begin -->

_尚未同步。S7 下一次运行会写入本轮进度：当前里程碑、做了什么、下一步、卡点。_

<!-- s7:end -->

## 子页

- [[project-decisions|决策台账]] —— D1~D14、改名成本、上游真面目与许可证
- [[project-design|架构与数值]] —— 脚本层、实体模板、热更新边界、伤害管线、附魔三档
- [[project-testserver|测试服]] —— 端口、12 个前置、用法约定
