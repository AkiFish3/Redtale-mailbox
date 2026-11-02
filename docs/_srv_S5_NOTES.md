# _srv_S5_NOTES.md — S5·地志 执行笔记

> 只追加，不覆盖。每轮一条：日期、处理了什么、留给下一轮的判断。

## 2026-11-02 · 首轮（人工需求优先）

**处理的人工需求（3/4）**

- R1 模组总览按用途分组：改的是**脚本 + 配置**，不是直接改 md（mod-index 由 `index_page()` 全量重写，手改必被覆盖）。
  `s5_config.json` 新增 `categories`（name / intro / mods 三字段）与 `category_rest`；
  `s5_wiki_sync.py` 新增 `category_map()`、`category_order()`，`index_page()` 改为按分类输出 `### 组名（n）` + 表格。
  实际分了 8 组：科技与机械 7 / 建筑与装饰 43 / 冒险与战斗 34 / 农业与生活 37 / 工具与社交 29 / 优化与界面 24 / 前置库与 API 58 / 其他 1。
  「服务端运维」8 个只在 `mod-index-server` 里出现（它们 role=admin，玩家页本来就不列）。
  以后加模组只需往 `categories` 对应数组里塞 modid；没写进去的自动落到「其他」。
- R2 chunky / spark / ftbbackups2 三页各补「## 什么时候该用」「## 命令怎么写」。
  命令与配置项都对着实际文件核过：`config/chunky/`（主世界 r=7000 方形，`minecraft:ziyuan` r=5000）、
  `config/spark/config.json`、`config/ftbbackups2.json`（cron 每天 06:00、留 5 份、落点 D:/mc_backups/server-1.21.1）。
- R3 client.md 加「## 按了键没反应怎么排查」五步（输入法 → 键位冲突标红 → 模组是否装/顶掉 → 需要目标才触发 → 换键验证）。

**留在池子里等 Aki 拍板**

- R4 旧服 1.20.1 内容（`E:\server-2`，395 jar）：归档页 vs 不收录。没动，等决定。
  顺带记录：若选归档，建议与 1.21.1 页面物理分开（`data/pages/legacy-*`），否则两张总览会混版本。

**内容进度**

- 20 个模组补了「中文简介 + 在赤物语里」，全部按 jar 英文描述 + `config/<modid>-common.toml` 的实际键名写，
  没有配置文件的（hearth_and_timber、lilis_pottery、lilis_lucky_lures、alcocraftplus、another_furniture、
  aquamirae、accelerateddecay）明确写了「没有找到独立配置文件」，没编。
- 20 页 frontmatter title 与 H1 改成「中文名（English Name）」，slug 未动。
- 任务池 229 → 204（20 补简介 + spark/ftbbackups2 两页归零，3 条人工需求消失后剩 1 条）。
- 注意：总览页行名取的是 jar 里的 `displayName`（英文），页面标题是中文——点进去会看到中文标题，属预期。

**玩家反馈**

- `E:\server-wiki\data\social.jsonl` 尚不存在（`social.py` 的 STORE 指向该路径），即目前没有任何留言/意见箱记录，本轮无内容可修。

**异常**

- 无。脚本未改动 auto 块以外的写行为；wiki 服务未启停。

## 2026-11-02 · 追加：旧服内容收录（Aki 拍板）

**决定**：旧服 1.20.1 收录，同一模组页内可切版本，默认 1.21.1。

**落地方式**：wiki 渲染器（`app.py` 的 `render()`）不做 raw HTML 透传，`container()` 只有 infobox/tip/note/warn，
真 tab 需要动 app.py + style.css（Aki 自己维护，本次没碰）。改为**页顶切换条 + 独立存档页**：

- 当前版页顶部加一行：`版本：**1.21.1（当前）** ｜ 1.20.1（旧服存档）`，后半是链接。
- 存档页 `mod-<modid>-1201.md`（`auto: mod-legacy`）反向链回当前版；标题继承当前版中文名 + 版本后缀。
- 只有旧版的模组，存档页切换条写「当前版已无此模组」，不产生死链。

**数据**：当前版 241（不变）；旧版扫到 577 个 modid（1.20.1 服务端 391 + 旧客户端包，两者合并不完全重合），
与当前版重合 184，仅旧服 393。新增页面 577，总页数 818（含 21 张手写页）。

**两个判断（自决，可推翻）**

1. 存档页默认 `role: player`。旧版把很多模组判成「仅服务端」只是因为旧客户端包没带，
   不等于运维工具；只有命中 `server_tools` 的才 admin。
2. 存档页**不进**玩家总览，单独出 `mod-index-legacy`（order 288），按同一套分类分组；
   否则玩家在总览里会看到一半是停服版本。

**分类兜底**：`s5_config.json` 新增 `category_rules`（关键词 → 分类），只在 `categories` 没显式登记时生效。
当前版 241 个全部靠显式名单，结果未变；旧版靠关键词从 393 个「其他」降到 96 个，
剩下的 96 个（additionaladditions、bbb、ctov、pasterdream、smc 之类）确实猜不准，留在「其他」，
并在任务池留一条「分类」任务等以后补。

**后续可做**：真 tab 切换（要动 app.py）；96 个旧版模组人工归类；旧版页补简介（先从当前版继承，没继承的写 _待补_）。

