# _srv_S5_WIKI.md — 赤物语 · Wiki 自动更新（S5·地志）

> 队列身份：服务器侧第 5 条队列，2026-11-02 由 Aki 指示新建。
> 执行器：`_srv_artifacts\s5_wiki_sync.py`（本文件由脚本重写，**不要手改**；要留笔记写 `_srv_S5_NOTES.md`）
> 频率：每天 05:10 ｜ 职责：给每个模组生成 wiki 页面、维护总览页、把「还缺什么」变成任务池
> 权限：仅服务端模组默认 `role: admin`（玩家看不到），双端/仅客户端默认 `role: player`
> （`player` = 所有人含未登录游客可看；不想公开就改 `role: login` 或 admin）；
> 覆盖写在 `s5_config.json` 的 `role_override`。

## 本轮状态

| 项 | 值 |
|---|---|
| 最近运行 | 2026-11-02 12:06 |
| 当前版模组（1.21.1） | **241**（双端 228 / 仅客户端 13 / 仅服务端 0） |
| 页面可见性 | player 233 ｜ admin 8 |
| 新建 / 更新 / 未变 / 手建跳过 | 0 / 0 / 241 / 0 |
| 旧版模组（1.20.1） | **577** 页（与当前版重合 184 / 仅旧服 393）｜新建 0 更新 0 未变 577 跳过 0 |
| 旧版总览 | 576 行（`mod-index-legacy`） |
| 待办任务 | **204**（补简介 **203** · 分类 **1**） |

## 任务池

| # | 类型 | 对象 | 说明 |
|---|---|---|---|
| W1 | 补简介 | Archers (RPG Series) | 「中文简介」还没写（`archers`，双端）；标题也只有英文名，可顺手加中文 |
| W2 | 补简介 | Architectury | 「中文简介」还没写（`architectury`，双端）；标题也只有英文名，可顺手加中文 |
| W3 | 补简介 | Armor Model API | 「中文简介」还没写（`armor_model_api`，双端）；标题也只有英文名，可顺手加中文 |
| W4 | 补简介 | Armourer's Workshop | 「中文简介」还没写（`armourers_workshop`，双端）；标题也只有英文名，可顺手加中文 |
| W5 | 补简介 | Arts & Crafts | 「中文简介」还没写（`arts_and_crafts`，双端）；标题也只有英文名，可顺手加中文 |
| W6 | 补简介 | Athena | 「中文简介」还没写（`athena`，双端）；标题也只有英文名，可顺手加中文 |
| W7 | 补简介 | AttributeFix | 「中文简介」还没写（`attributefix`，双端）；标题也只有英文名，可顺手加中文 |
| W8 | 补简介 | Automobility | 「中文简介」还没写（`automobility`，双端）；标题也只有英文名，可顺手加中文 |
| W9 | 补简介 | AzureLib | 「中文简介」还没写（`azurelib`，双端）；标题也只有英文名，可顺手加中文 |
| W10 | 补简介 | Balm | 「中文简介」还没写（`balm`，双端）；标题也只有英文名，可顺手加中文 |
| W11 | 补简介 | Barbeque's Delight | 「中文简介」还没写（`barbequesdelight`，双端）；标题也只有英文名，可顺手加中文 |
| W12 | 补简介 | BCLib | 「中文简介」还没写（`bclib`，双端）；标题也只有英文名，可顺手加中文 |
| W13 | 补简介 | Beautify | 「中文简介」还没写（`beautify`，双端）；标题也只有英文名，可顺手加中文 |
| W14 | 补简介 | Better Advanced Tooltips | 「中文简介」还没写（`betteradvancedtooltips`，双端）；标题也只有英文名，可顺手加中文 |
| W15 | 补简介 | Better End | 「中文简介」还没写（`betterend`，双端）；标题也只有英文名，可顺手加中文 |
| W16 | 补简介 | Better McDonald's Mod | 「中文简介」还没写（`better_mcdonalds_mod`，双端）；标题也只有英文名，可顺手加中文 |
| W17 | 补简介 | Better Nether | 「中文简介」还没写（`betternether`，双端）；标题也只有英文名，可顺手加中文 |
| W18 | 补简介 | Biolith | 「中文简介」还没写（`biolith`，双端）；标题也只有英文名，可顺手加中文 |
| W19 | 补简介 | BoccHUD | 「中文简介」还没写（`bocchud`，仅客户端）；标题也只有英文名，可顺手加中文 |
| W20 | 补简介 | Bookshelf | 「中文简介」还没写（`bookshelf`，双端）；标题也只有英文名，可顺手加中文 |
| W21 | 补简介 | Bosses of Mass Destruction | 「中文简介」还没写（`bosses_of_mass_destruction`，双端）；标题也只有英文名，可顺手加中文 |
| W22 | 补简介 | Bountiful | 「中文简介」还没写（`bountiful`，双端）；标题也只有英文名，可顺手加中文 |
| W23 | 补简介 | Bountiful Fares | 「中文简介」还没写（`bountifulfares`，双端）；标题也只有英文名，可顺手加中文 |
| W24 | 补简介 | Brewin' And Chewin' | 「中文简介」还没写（`brewinandchewin`，双端）；标题也只有英文名，可顺手加中文 |
| W25 | 补简介 | BundleAPI | 「中文简介」还没写（`bundleapi`，双端）；标题也只有英文名，可顺手加中文 |
| W26 | 补简介 | Caelus API | 「中文简介」还没写（`caelus`，双端）；标题也只有英文名，可顺手加中文 |
| W27 | 补简介 | Camping | 「中文简介」还没写（`camping`，双端）；标题也只有英文名，可顺手加中文 |
| W28 | 补简介 | CasualnessDelight | 「中文简介」还没写（`casualnessdelight`，双端）；标题也只有英文名，可顺手加中文 |
| W29 | 补简介 | Cerbons API | 「中文简介」还没写（`cerbons_api`，双端）；标题也只有英文名，可顺手加中文 |
| W30 | 补简介 | Chimes | 「中文简介」还没写（`chimes`，双端）；标题也只有英文名，可顺手加中文 |
| W31 | 补简介 | Chipped | 「中文简介」还没写（`chipped`，双端）；标题也只有英文名，可顺手加中文 |
| W32 | 补简介 | ChunkyBorder | 「中文简介」还没写（`chunkyborder`，双端）；标题也只有英文名，可顺手加中文 |
| W33 | 补简介 | Cloth Config v15 API | 「中文简介」还没写（`cloth_config`，双端）；标题也只有英文名，可顺手加中文 |
| W34 | 补简介 | Clumps | 「中文简介」还没写（`clumps`，双端）；标题也只有英文名，可顺手加中文 |
| W35 | 补简介 | Cluttered | 「中文简介」还没写（`cluttered`，双端）；标题也只有英文名，可顺手加中文 |
| W36 | 补简介 | Cobweb | 「中文简介」还没写（`cobweb`，双端）；标题也只有英文名，可顺手加中文 |
| W37 | 补简介 | Collective | 「中文简介」还没写（`collective`，双端）；标题也只有英文名，可顺手加中文 |
| W38 | 补简介 | Combat Roll | 「中文简介」还没写（`combat_roll`，双端）；标题也只有英文名，可顺手加中文 |
| W39 | 补简介 | Compact Help Command | 「中文简介」还没写（`compacthelpcommand`，双端）；标题也只有英文名，可顺手加中文 |
| W40 | 补简介 | Contact | 「中文简介」还没写（`contact`，双端）；标题也只有英文名，可顺手加中文 |

_还有 164 条没列出来。完整清单在 `_srv_artifacts\s5_state.json`，或跑 `python s5_wiki_sync.py --json` 取。_

## 任务池怎么来的

任务不是人工录入的，每轮从事实里重新推导，所以会自动长出新任务，也会自动消失：

| 类型 | 触发条件 | 消失条件 |
|---|---|---|
| 补简介 | 页面「中文简介」不足 15 个汉字 | 写够字数 |
| 版本更新 | 与上一轮记录的版本号不同 | 处理完在 `s5_state.json` 记新版本（脚本每轮自动记） |
| 端归属变化 | 双端/单端判定变了 | 同上 |
| 模组已移除 | 上次有、这次 jar 没了 | 处理完人工确认后从 `s5_state.json` 的 `mods` 里删掉 |

标题只有英文名的模组，会在「补简介」任务里附带一句提醒，不单独占一条。

## 生成规则

- 文件名 `mod-<modid>.md`，分组「模组」，`nav: no`（不进左栏，从总览页进）
- 自动块用 `<!-- auto:begin --> … <!-- auto:end -->` 包住，脚本只改这一段
- 「中文简介」「在赤物语里」等段落**脚本永不覆盖**，手写内容安全
- 页面已存在但没有自动块的（纯手写页）→ 跳过不动，计入「手建跳过」

## 为什么「仅服务端」是 0

客户端的整合包按「服务端有的客户端必须有」的规矩打包，所以服务端 226 个 jar 全都在客户端里，
脚本判不出「仅服务端」。真正的运维类工具用 `s5_config.json` 的 `server_tools` 名单单独处理：
命中名单的页面强制 `role: admin`，并在信息框里标「定位：服务端工具」。

## 旧版（1.20.1）怎么收的

- 旧版目录写在 `s5_config.json` 的 `legacy_mods` / `legacy_client_mods`，合并逻辑和当前版一样（双端/仅客户端/仅服务端）。
- 文件名 `mod-<modid>-1201.md`，`auto: mod-legacy`，`role` 跟当前版一致，**不进左栏**。
- 两版都有的模组：当前版页面顶部有「版本：1.21.1（当前）｜1.20.1（旧服存档）」切换条，旧版页反向链回来。
- 只有旧版才有的模组：只建存档页，不产生「补简介」任务——先把当前版补完，旧版简介从当前版继承。
- 旧版总览是 `mod-index-legacy`，玩家可见；当前版总览 `mod-index` 只列现行模组，避免混淆。
- 想让旧版重新公开/隐藏，改 `s5_config.json` 的 `role_override` 或直接调 `legacy_mods` 目录。
