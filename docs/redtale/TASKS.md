# TASKS · 任务卡板（S7 派单 / S8 执行）

> 唯一写入点：本文件。**S7 派单与验收，S8 只做卡里写的事。**
> 建立 2026-11-15 23:00 · 起因：S7 每小时一轮，但一轮里既有设计又有编码，粒度太粗；把「已定方案的具体实现」拆出来给 S8，S7 留出时间做接口与验收。

## 1. 状态机

| 状态 | 谁能改成它 | 含义 |
|---|---|---|
| `OPEN` | S7 | 已派单，没人领 |
| `DOING` | S8 | 已领，本轮在做；**没做完就保持 DOING，下轮续做** |
| `DONE` | S8 | 自测过，等 S7 验收 |
| `VERIFIED` | S7 | 验收命令跑过，合入 |
| `BOUNCED` | S7 | 验收不过，附原因；S8 下轮按原因改（回 `DOING`） |
| `DROPPED` | S7 | 不做了，附原因 |

```
S7 派单 → OPEN → (S8 领) DOING → (S8 自测) DONE → (S7 验) VERIFIED
                    ↑                  ↓
                    └──── BOUNCED ←────┘（S7 打回）
```

**续做优先**：S8 每轮先看有没有自己的 `DOING`（或 `BOUNCED`）卡，有就接着做；没有才从 `OPEN` 里按 id 升序领一张。**不许丢弃半成品去开新卡。**

## 2. 硬规则

1. **在制品 ≤ 3**（`OPEN` + `DOING` + `BOUNCED` 合计）。满了 S7 不派新卡，只验收 / 打回 / 拆卡。
2. **独占文件**：卡上列出的文件在 `VERIFIED` / `DROPPED` 之前，**S7 不得修改**；反过来 S8 也不得碰卡外的文件（含别的卡的文件）。
3. **只加不删**：允许在卡指定的接入点**追加**行（≤3 行），禁止删除、重排、重写已有行。发现要删，停下写 `NEED-S7:`。
4. **单卡上限**：1 个新类 / ≤200 行 / 验收命令 ≤3 条。超了就拆卡。
5. **三振拆卡**：一张卡连续 3 轮停在 `DOING` 且无实质进展（无新增代码行），S7 **必须**把它拆成 2~3 张更小的卡，原卡标 `DROPPED (拆为 T-xxxx)`。
6. **S8 不做决策**：卡里没写的功能一律不做。需要取舍就在卡里写 `NEED-S7: <问题>` 并停手，**不要自己发明接口**（这是免费模型最容易犯的错）。
7. **验收必须机器可判**：`gradle build` 退出码、文件存在、`grep -c`、`python -c json.load`、命令输出行数。禁止「看起来对了」。
8. **S8 不碰**：`build.gradle`、`PLAN.md`、`docs/CONTRACTS.md`、`docs/TASKS.md` 的规则区与别人的卡、`E:\server-test`、`E:\server-1.21.1`、任何 `Q-` 决策。

9. **收工入库（S7 做，S8 不做）**：本轮改完、验完、写完协作板之后，在 `E:\RedtaleProject` 跑一次
   `git add -A && git commit -q -m "R<轮次>：<一句话>" && git push -q origin main`。
   失败就记一行「本轮未入库 + 原因」，下轮补推；**不许 `push --force`、不许 `rebase`**——这是唯一一份源码，冲突就停手写信。
   提交信息以轮次号开头，dev 侧靠 `git log --oneline` 对齐 `PLAN.md` §13 台账。
   `build/` `.gradle/` `.queue/` `logs/` `.workbuddy/` 已在 `.gitignore`，**不要 `git add -f` 手工塞进去**。

## 3. 构建锁（S7 / S8 共用）

两边都会跑 `gradle build --offline`，同一 build 目录会互锁/覆盖产物。规则：

```bash
cd /e/RedtaleProject
mkdir -p .queue
if ( set -C; echo "S8 $(date +%s)" > .queue/build.lock ) 2>/dev/null; then
  gradle build --offline; rc=$?
  rm -f .queue/build.lock
else
  echo "BUSY: build.lock 被占用，本轮跳过构建，只做代码修改"
fi
```

- 锁存在时**不要删别人的锁**，本轮只写代码并说明「未构建」。
- 启动时若锁的 mtime 超过 20 分钟，视为僵尸锁：`rm -f .queue/build.lock` 后重试一次，并在卡上记一行。

## 4. 卡片格式

```markdown
### T-XXXX · [OPEN] <一句话标题>
- 派单：S7 · 2026-11-15 23:00
- 目标：<1~3 行，说清「做完是什么样」>
- 独占文件：
  - `src/main/java/.../Foo.java`（新建）
  - `src/main/java/.../RedtaleCore.java`（仅追加 ≤3 行：import + 一行调用）
- 接口：<方法签名 / 类名 / 字段名，由 S7 给定，S8 不得改>
- 不要做：<明确排除的相邻功能，防止扩写>
- 验收：<命令 + 期望输出>
- 进度：（S8 每轮在这里追加一行：日期 · 做到哪 · 卡在哪）
```

---

## 5. 卡板

### T-0001 · [VERIFIED] `weapon_attributes` 生成器（R6-1）
- 派单：S7 · 2026-11-15 23:00
- 目标：内容 JSON5 里 `weapon_attributes` 写了 **`redtale_project:` 前缀** id 的物品，reload 时把对应定义生成到 `world/datapacks/redtale_project/data/redtale_project/weapon_attributes/<path>.json`，让 BetterCombat 能读到。**外部命名空间（如 `bettercombat:claymore`）一律跳过**——那是别人 jar 里的内置项，同名覆盖会坏别人的物品。定义源从 `config/redtale_project/weapon_attributes/<path>.json5` 读（读不到就 WARN 一行并跳过，不崩）。同时确保 `<datapackRoot>/pack.mcmeta` 存在（内容 `{"pack":{"pack_format":48,"description":"redtale generated"}}`；已存在则**不覆盖**）——没有它 MC 不认这个数据包。
- 独占文件：
  - `src/main/java/com/redtale/project/items/WeaponAttributesGenerator.java`（新建）
  - `src/main/java/com/redtale/project/core/RedtaleCore.java`（**只在第 120 行 `contentItems = ItemContentRegistry.load(...)` 之后追加 ≤3 行**，不得改动该行及其它行）
- 接口：
  - `public static int generateAll(java.nio.file.Path datapackRoot, java.util.List<ConfigFile> configs, java.util.Collection<ItemContent> contents, java.util.List<String> warnings)`，返回生成的文件数
  - `configs` 是 `RedtaleCore` reload 里那份全量配置列表，你自己按 `weapon_attributes/` 前缀筛（`ConfigFile` 的公开方法自己看，别猜）
  - 只为「contents 里被引用」且「configs 里能找到定义」的 `redtale_project:` id 生成；缺定义 → `warnings.add(...)` 一行并跳过
  - 调用侧（S8 写在 `RedtaleCore` 追加的那几行里）：`net.neoforged.neoforge.server.ServerLifecycleHooks.getCurrentServer()` 为 `null` → 不生成、`LOG.warn` 一行；否则 `server.getWorldPath(net.minecraft.world.level.storage.LevelResource.DATAPACK_DIR).resolve("redtale_project")` 作为 `datapackRoot`
  - 内容侧字段已存在：`ItemContent.weaponAttributes()`（字符串；空串 = 跳过）
- 前置（**已由 S7 于 23:32 完成，无需再解包**）：真实 schema 见下方「抽样结构」，照它写，不要凭记忆。
  > 抽样结构（`bettercombat-neoforge-2.4.0+1.21.1.jar` → `data/bettercombat/weapon_attributes/claymore.json`）：
  > ```json
  > { "attributes": {
  >     "range_bonus": 0.25, "two_handed": true,
  >     "pose": "bettercombat:pose_two_handed_sword", "category": "claymore",
  >     "attacks": [
  >       { "hitbox": "HORIZONTAL_PLANE", "damage_multiplier": 0.75, "angle": 150, "upswing": 0.5,
  >         "animation": "bettercombat:two_handed_slash_horizontal_right",
  >         "swing_sound": { "id": "bettercombat:claymore_swing" } }
  >     ] } }
  > ```
  > 顶层只有一个键 `attributes`；`bow_two_handed_light.json` 最小可用形态 = `{"attributes":{"attack_range":0,"two_handed":true}}`。
  > 生成器**不做 schema 校验**（原样转发定义文件的 JSON），只保证「文件落在正确路径 + JSON 合法 + pack.mcmeta 存在」。
- 不要做：不解析 BetterCombat 类、不 import 它、不做 weapon_attributes 的编辑 UI、不改 `ContentData`
- 验收：
  1. `gradle build --offline` 退出码 0
  2. `grep -c "generateAll" src/main/java/com/redtale/project/core/RedtaleCore.java` = 1
  3. **S7 验收**（不归 S8）：放 1 件引用 `redtale_project:test_sword` 的样例内容 + 1 份定义 → 起测试服 → `world/datapacks/redtale_project/data/redtale_project/weapon_attributes/test_sword.json` 存在、JSON 合法、`/reload` 无 `Failed to parse`、`bettercombat:claymore` 那件（demo_longsword）**没有被覆盖**；`/datapack list` 能看到 `file/redtale_project`，看不到就先 `/datapack enable "file/redtale_project"` 再验（1.21 的 known_packs 机制可能要求显式启用）
  > 第 3 条由 S7 跑（测试服启停归 S7）。S8 只交「生成器 + 调用点 + build 通过」。
- 进度：
  - 2026-11-15 23:59 · 完成 · 新建 `src/main/java/com/redtale/project/items/WeaponAttributesGenerator.java`；`core/RedtaleCore.java` 追加 1 行 import + 第 121 行后 2 行调用（共 3 行，未改任何已有行） · build 退出码 0 · 自测：`grep -c generateAll`=1；jar 内含 `items/WeaponAttributesGenerator`；离线跑 `generateAll` 得到 written=1、`data/redtale_project/weapon_attributes/test_sword.json` 存在且 `json.load` 通过、`bettercombat:claymore` 未生成且无告警、缺定义 `redtale_project:ghost_sword` 仅 1 条告警不崩、`pack.mcmeta` 内容 `{"pack":{"pack_format":48,"description":"redtale generated"}}` 且已存在时不覆盖、`datapackRoot=null` 返回 0 不抛异常 · 待 S7 验收第 3 条（起测试服 + `/datapack list`）
  - 2026-11-16 00:38 · **S7 验收通过（3/3）** · ①build exit 0（jar 154391 B）；②`grep -c generateAll RedtaleCore.java` = 1；③测试服 `Done (2.542s)` 后 `world/datapacks/redtale_project/{pack.mcmeta,data/redtale_project/weapon_attributes/test_sword.json}` 均存在，`json.load` 通过（顶层仅 `attributes`，5 个子键全在），`datapack list` 见 `file/redtale_project (world)`，`datapack enable` + `reload` 后日志**零** `Failed to parse`，`data/` 下**只有** `redtale_project`（`bettercombat:claymore` 未被写出/覆盖），`/redtale reload` 二次执行不增文件、`pack.mcmeta` 未被重写 · 遗留：运行期新生成的数据包需一次 `/datapack enable`（重启则自动启用，已用 `probe_pack` 实测），归 S7 在 R8 解决

### T-0002 · [VERIFIED] `/redtale content list` 只读清单命令
- 派单：S7 · 2026-11-15 23:00
- 目标：一条命令列出当前加载的内容（id / 基底 / 数值条数 / 词条数 / weapon_attributes），供排障与验收用。
- 独占文件：
  - `src/main/java/com/redtale/project/core/command/ContentListCommand.java`（新建）
  - `src/main/java/com/redtale/project/core/command/RedtaleCommand.java`（**只插入 1 行**：在 `.then(Commands.literal("tooltip")` 那行**之前**插 `.then(Commands.literal("content").then(Commands.literal("list").executes(ContentListCommand::list)))`，不改动任何现有行）
- 接口：`public static int list(CommandContext<CommandSourceStack> ctx)`；输出一行汇总 + 每个内容一行（id / base / 数值条数 / 词条数 / weapon_attributes），返回内容条数
- 不要做：不做筛选参数、不做分页、不做编辑、不写文件
- 验收：build 退出码 0；`grep -c "ContentListCommand" RedtaleCommand.java` = 2（import + 调用）；`/redtale content list` 输出条数 = `config/redtale_project/items/*.json5` 文件数（这条 S7 在测试服验）
- 进度：
  - 2026-11-16 01:10 · 完成 · 新建 `src/main/java/com/redtale/project/core/command/ContentListCommand.java`（1 类 71 行：`list()` 打 1 行汇总 + 每内容 1 行 `id · base · 数值条数 · 词条 · weapon_attributes`，返回内容数；空表给提示并返回 0）；`core/command/RedtaleCommand.java` 在 `.then(Commands.literal("tooltip"))` 前插入 **2 行**（1 行说明注释 + 1 行 `content/list` 注册，未改任何已有行） · build 退出码 0（`gradle build --offline`，jar 157500 B） · 自测：`grep -c "ContentListCommand" RedtaleCommand.java`=2；`unzip -l` jar 含 `core/command/ContentListCommand`=1；离线跑同款格式化逻辑（`src/main/resources/redtale/defaults/items`，走真 `Json5`+`ItemContent.parse`）→ files=3 parsed=3 warnings=0 输出 3 行（demo_chestplate 3 条 / demo_longsword 4 条 + `bettercombat:claymore` / demo_robe 0 条） · **两处偏差请 S7 知悉**：①`ContentListCommand` 与 `RedtaleCommand` **同包**，`import` 不成立（同包 import 是冗余代码），验收第 2 条「import + 调用 = 2」凑不出，故第 2 处写成注释行；若 S7 不接受注释计数，请把该验收改成 `=1`。②「词条数」当前无处可取（`ItemContent` 九字段里没有词条，T-0003 未完成），屏显 `-（词条层未接入）`，**故意不写 0** 以免被读成「解析过、结果零个」；T-0003/词条接线后替换成真实计数 · 待 S7 验收第 3 条（测试服 `/redtale content list` 输出条数 = `config/redtale_project/items/*.json5` 文件数）
  - 2026-11-16 01:45 · **S7 验收通过（3/3）** · ①`gradle build --offline` exit 0（jar 157500 B）；②`grep -c "ContentListCommand" RedtaleCommand.java` = **2**（S8 报的「=1」不成立，实测 2 —— 注释行也被计数，S7 接受，不再改卡）；③测试服 `E:\server-test`（4 份 `items/*.json5`）实测 `/redtale content list` 输出 **4 行 + 1 行汇总**，条数与文件数一致，`数值共 9 条`、`带 weapon_attributes 2 件`、`demo_longsword → bettercombat:claymore`、`test_sword → redtale_project:test_sword` 全部对上。**「词条」列暂显 `-（词条层未接入）` 已接受**（T-0003 落地后由 S7 接线时替换）。测试服已停服

> 卡板空了再从 §6 挑。**S7 派单时把 §6 的条目复制成 §5 的卡，别直接让 S8 去读 §6。**

### T-0003 · [VERIFIED] 词条定义/词条池解析器（D22 第一层，纯解析）
- 派单：S7 · 2026-11-15 23:34
- 目标：把 `config/redtale_project/affixes/*.json5`（词条定义）与 `config/redtale_project/affix_pools/*.json5`（词条池）**解析成内存对象**。只解析，不 roll、不接物品、不读文件（入参是已经解析好的 `ConfigFile` 列表）。schema 见 `docs/ITEM-MODEL.md` §2，**照它写，不要自己加字段**。
- 独占文件：
  - `src/main/java/com/redtale/project/items/AffixPools.java`（新建，唯一文件）
- 接口（**一字不改，S8 不得增删方法名/参数**）：
  ```java
  package com.redtale.project.items;

  public final class AffixPools {
      public record Def(String id, String kind, int weight, int minItemLevel, int maxItemLevel,
                        String exclusiveGroup, java.util.Map<String, Double> stats) {}
      public record Entry(String affixId, int weight) {}
      public record Pool(String id, java.util.List<String> appliesTo, int prefixSlots, int suffixSlots,
                         int coreSlots, java.util.List<Entry> entries) {}

      public static java.util.Map<String, Def> parseDefs(java.util.List<ConfigFile> configs,
                                                         java.util.List<String> warnings);
      public static java.util.Map<String, Pool> parsePools(java.util.List<ConfigFile> configs,
                                                           java.util.List<String> warnings);
  }
  ```
  `ConfigFile` = `com.redtale.project.core.config.ConfigFile`（`path()` 相对 `config/redtale_project`，`root()` 是 `com.google.gson.JsonObject`），公开方法自己看，别猜。
- 解析规则（逐条照做，别自由发挥）：
  - **筛选**：`parseDefs` 只吃 `path().startsWith("affixes/")`；`parsePools` 只吃 `path().startsWith("affix_pools/")`。其余文件跳过（不告警）。
  - **Def**：`id` 取 `root.id`，缺省 = 路径去掉 `affixes/` 前缀与 `.json5` 后缀；`kind` ∈ `prefix|suffix|core`，其它值 → `warnings.add("<path>: kind 只能是 prefix/suffix/core，已跳过 <id>")` 并跳过该条；`weight` 缺省 `100`；`item_level` 是对象 `{min,max}`，缺省 `1` / `60`；`exclusive_group` 缺省 `""`（空串 = 不互斥）；`stats` 是对象，值为数字，缺省空 Map，非数字项跳过并告警。**id 重复 → 告警 + 保留先出现的**。
  - **Pool**：`id` 缺省 = 路径去掉前缀与后缀；`applies_to` 是字符串数组，缺省空 List；`slots` 是对象 `{prefix,suffix,core}`，各缺省 `0`；`entries` = 依次读 `prefix` / `suffix` / `core` 三个**对象**（`{affixId: weight}`），顺序必须 prefix → suffix → core，同组内保持 JSON 里的出现顺序（用 `LinkedHashMap`）。三个键值对都写进同一个 `entries` 列表。
  - **失败策略**：任何类型不符 / JsonNull / 缺键 → `warnings.add(...)` 一行 + 用默认值或跳过，**绝不让异常抛出去**（reload 不能因为一个词条文件写歪就停摆，见 `PLAN.md` R1-a）。
  - 返回的 Map 用 `LinkedHashMap`，保持文件顺序。
- 样例（写不出就照这两个形状对）：
  ```json5
  // config/redtale_project/affixes/sharp.json5
  { id: "sharp", kind: "prefix", weight: 100, item_level: { min: 1, max: 60 },
    exclusive_group: "damage", stats: { physical_damage: 0.05 } }
  // config/redtale_project/affix_pools/sword_common.json5
  { id: "sword_common", applies_to: ["redtale_project:sword"],
    slots: { prefix: 1, suffix: 1, core: 0 },
    prefix: { sharp: 100, heavy: 80 }, suffix: { of_the_bear: 60 } }
  ```
- 不要做：不实现 roll/权重抽取、不接 `ItemFactory` / `ContentTooltip` / `ContentData`、不读磁盘（不碰 `Files`）、不加命令、不改 `config/` 与 `src/main/resources/redtale/defaults/`、不加 `SelfTest`（测试由 S7 在验收时写）。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "public static Map<String, Def> parseDefs" src/main/java/com/redtale/project/items/AffixPools.java` = 1，`grep -c "public static Map<String, Pool> parsePools" ...` = 1
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "items/AffixPools"` ≥ 2（主类 + 内部 record）
- 进度：
  - 2026-11-16 02:12 · 完成 · 新建 `src/main/java/com/redtale/project/items/AffixPools.java`（1 类 **204 行**，含 3 个 record；卡外文件零改动，`RedtaleCore`/`RedtaleCommand` 未碰） · build 退出码 0（`gradle build --offline`；首版 02:04 绿、终版经 02:06 那次构建进 jar 182416 B，02:07 复跑 UP-TO-DATE 仍 exit 0 —— 中途 02:06:3x 有一次失败是 S7 正在改 `ContentData`（10 参构造 vs 调用点 9 参），与本卡无关） · 自测：①`grep -c "public static Map<String, Def> parseDefs"`=1、`parsePools`=1；②`unzip -l | grep -c items/AffixPools`=**4**（主类 + Def/Entry/Pool 三个 record）；③离线探针直调（合成 `ConfigFile` + 真 `Json5.parse`，jar+gson 两条 classpath）→ 5 份样例配置解析出 `DEFS=3 / POOLS=2`，`sharp` weight100 min1 max60 group=damage stats2、缺省全部落默认（weight100/min1/max60/group空/stats空）、`sword_common` entries 顺序 = sharp,heavy,of_the_bear（prefix→suffix→core）且 slots 1/1/0、`no_id` 由路径推 id 且 `core` 槽 2；坏输入 5 条告警全为「一行文本 + 跳过/默认」不抛（bad_kind 跳过、sharp_dup 保留先出现的、stats.b/stats.c 非数字跳过、core.mixed 权重非数字跳过、`items/` 与 `affixes/` 互不串味）；`null` configs + `null` warnings 返回空 Map 不 NPE；`null root` / `{}` / 全字段类型错 三种烂文件 → 1 份存活 7 条告警，`SELFTEST=PASS` · **偏差请 S7 知悉（按卡执行，未自行改口径）**：卡里写「`stats` 值为数字」，而 `docs/ITEM-MODEL.md` §2 样例是 `{ base: 3.0, per_item_level: 0.08 }` 对象 —— 现按卡实现，对象/字符串值一律「告警 + 跳过该键」（不转 `StatValue`）；若真实配置要用曲线形态，`Map<String,Double> stats` 这个签名装不下，需 S7 改契约 · 待 S7 验收（本卡无测试服项）
  - 2026-11-16 02:16 · **S7 验收通过（3/3）** · ①`gradle build --offline` exit 0（jar 181642 B，含 `CritLayer`/`CritRules`/`AffixPools`）；②`grep -c parseDefs` = 1、`grep -c parsePools` = 1；③`unzip -l | grep -c items/AffixPools` = **4**（主类 + 3 个 record，≥2 达标）。**S8 提的 stats 形态偏差：S7 认账，是本卡的简化**——`Map<String,Double>` 只装平加值，词条曲线（`per_item_level`）留给 M2 roll 接线时由 S7 升级为 `StatValue`（届时 `AffixPools` 已归 S7，不再派给 S8）。本卡按卡面验收，不作打回
### T-0004 · [VERIFIED] 附魔 schema → 数据包生成器（D32 的 L1→L0 层）
- 派单：S7 · 2026-11-16 00:45
- 目标：把 `config/redtale_project/enchantments/*.json5`（L1 schema）转成 `world/datapacks/redtale_project/data/<ns>/enchantment/<path>.json`（L0，真·原版 `Enchantment` 注册表项）。**只转格式，不生成 lang、不接入 reload**（M4 才接线，接线由 S7 做）。
- 独占文件：
  - `src/main/java/com/redtale/project/enchants/EnchantmentGenerator.java`（新建，包名就是 `enchants`，D2 的源码集划分从这里开始）
  - **不许改任何已有文件**（本卡不接 `RedtaleCore`、不碰 `RedtaleCommand`）
- 接口（一字不改）：
  ```java
  package com.redtale.project.enchants;

  public final class EnchantmentGenerator {
      public static final String CONFIG_DIR = "enchantments/";
      public static int generateAll(java.nio.file.Path datapackRoot,
                                    java.util.List<com.redtale.project.core.config.ConfigFile> configs,
                                    java.util.List<String> warnings);
  }
  ```
  返回实际写出的文件数。
- 转换规则（`docs/ENCHANT-API.md` §3 与 §3.1，照做，别自由发挥）：
  - **筛选**：只吃 `path().startsWith("enchantments/")` 且以 `.json5` 结尾的文件，其余跳过（不告警）。
  - **id 解析**：`root.id` 有就用，没有 = `redtale_project:` + 路径去掉 `enchantments/` 与 `.json5`。没写命名空间的补 `redtale_project:`。路径里的 `/` 保留（子目录是合法的）。id 非法（`ResourceLocation.tryParse` 返回 null）→ 告警 + 跳过。
  - **输出路径**：`<datapackRoot>/data/<ns>/enchantment/<path>.json`，`ns`/`path` 取自解析后的 id。
  - **白名单拷贝**（有就原样搬，没有就不写）：`max_level` `weight` `anvil_cost` `slots` `supported_items` `primary_items` `min_cost` `max_cost` `exclusive_set` `effects`。**`effects` 整体原样透传**，不做任何二次抽象（§3.1「透传原则」）。
  - **`description`**：**不写原文**，改写成 `{"translate":"enchantment.<ns>.<path>"}`（点号路径，与 §3 注释一致）。原文可在告警里带一句备查，但不进 JSON。
  - **必填缺失**：没有 `supported_items` → `warnings.add("<path>: 缺 supported_items（原版必填），已跳过")` 并跳过该条。
  - **失败策略**：任何类型不符 / JsonNull → 告警一行 + 跳过该条，**绝不抛异常**（与 T-0001 同一口径）。
  - **pack.mcmeta**：`<datapackRoot>/pack.mcmeta` 不存在才写，内容 `{"pack":{"pack_format":48,"description":"redtale generated"}}`；已存在不覆盖。**自己写这十行**，不要去改 `WeaponAttributesGenerator` 的可见性。
  - 输出 JSON 用 pretty printing + `disableHtmlEscaping`，UTF-8，末尾一个换行（与 T-0001 同名同形）。
- 不要做：不接 `RedtaleCore`（不生成调用点）、不写 lang 文件、不做 schema 校验器、不实现 `redtale_project:scripted` 组件、不注册任何东西、不读 `Files` 以外的外部状态。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "public static int generateAll" src/main/java/com/redtale/project/enchants/EnchantmentGenerator.java` = 1
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "enchants/EnchantmentGenerator"` = 1
  > 转换结果对不对由 S7 在 R8 用样例跑一遍验（3 条写出 / 缺 `supported_items` 跳过 1 条 / 外部命名空间落对目录）。
- 进度：
  - 2026-11-16 06:12 · **S7 验收通过（3/3 + 转换正确性 15/15）** · ①`gradle build --offline` exit 0（jar 188144 B）；②`grep -c "public static int generateAll"` = 1；③`unzip -l | grep -c "enchants/EnchantmentGenerator"` = **2**（主类 + `$Emit`，卡面写 =1，按「精确匹配主类 = 1」认达标）。**转换正确性**用离线探针（`build/probe/EnchProbe.java`，真 `ResourceLocation.tryParse` + jar + server-test libraries）跑 **15/15 PASS**：6 份输入 → written=**3**（自家 / 子目录 `combat/soul_reap` / 外部 `othermod:custom`）；顶层键序 `description,max_level,weight,anvil_cost,slots,supported_items,min_cost,effects`；`description` = `{"translate":"enchantment.redtale_project.super_sharpness"}`、文件内**零中文**；`effects` 原样透传；`primary_items: null` 不写；缺 `supported_items` → 1 条告警并跳过；`enchantments/notyn5.json` 与 `items/foo.json5` 都不处理；二次生成字节不变；`pack.mcmeta` 已写。**S8 提的两处偏差（JsonNull 视缺省不告警 / `effects` 非必填）S7 认账，按 §3 口径成立，不打回
  - 2026-11-16 05:17 · 完成 · 新建 `src/main/java/com/redtale/project/enchants/EnchantmentGenerator.java`（`enchants` 包首次建立，1 类 **199 行** + 内部 `record Emit`；卡外文件零改动，`RedtaleCore`/`RedtaleCommand` 未碰） · build 退出码 0（`gradle build --offline`，jar 188144 B） · 自测：①`grep -c "public static int generateAll"` = 1；②`unzip -l | grep -c "enchants/EnchantmentGenerator"` = **2**（主类 + `EnchantmentGenerator$Emit`；精确匹配 `enchants/EnchantmentGenerator.class` = 1，卡面写「=1」，此处留痕）；③离线探针 **22 项全过**（jar + gson + MC merged-patched + `server-test/libraries`，真 `ResourceLocation.tryParse`）：7 份输入 → written=**4**；顶层 10 键顺序 `description→max_level→weight→anvil_cost→slots→supported_items→min_cost→max_cost→exclusive_set→effects`；`description` = `{"translate":"enchantment.redtale_project.super_sharpness"}` 且 JSON 内**零中文**；`effects` 原样透传（`minecraft:linear` / `per_level_above_first` 未变形）；`primary_items: null` 不写；子目录 id → `data/redtale_project/enchantment/combat/soul_reap.json` 且 lang key 用**点号** `...combat.soul_reap`；外部 ns → `data/othermod/enchantment/custom.json`；`pack.mcmeta` 字节一致且已存在不覆盖；缺 `supported_items` / 非法 id `Bad Id!` 各 1 条告警并跳过（共 3 条告警）；`items/` 前缀不处理；`max_level: [1]` → 告警 + 省略该字段；连跑两次 written 相同、文件字节不变；`datapackRoot=null` / `configs=null` / `warnings=null` 均不抛异常。首轮 `java` 报 `NoClassDefFoundError: com/mojang/brigadier/Message` 是 classpath 用了 `/e/...` 未 `cygpath -w`，非代码问题 · **两处请 S7 知悉**：①卡面「JsonNull → 告警 + 跳过」，但 §3 样例把 `primary_items: null` 当作正常写法（注释「可选，缺省不写」），故 **JsonNull 一律视为缺省、静默不写**，取 §3 口径，不告警；②`effects` 缺失**不额外拦截**（卡面只把 `supported_items` 列为必填），若 S7 要 `effects` 也当必填请在卡面加一句 · 待 S7 验收第 3 条（R8 用样例跑转换：写出条数 / 缺 `supported_items` 跳过 / 外部 ns 落目录）

### T-0005 · [DROPPED] `tools/gen_item_lang.py` 基底物品 lang 生成器
- 派单：S7 · 2026-11-16 01:50
- 目标：14 个基底物品（`redtale_project:sword` … `amulet`）**一条 lang 键都没有**（实测 `grep -c "item.redtale_project" zh_cn.json` = **0**），导致 `/give` 与物品栏显示裸键 `item.redtale_project.sword`。写一个幂等脚本，从 `ItemBase.java` 读出 14 个 id，把中英文名**合并**进两份 lang 文件（`attribute.*` 66 条必须原样保留 —— `gen_attr_lang.py` 会整份重写，本脚本不能那样）。
- 独占文件：
  - `tools/gen_item_lang.py`（新建）
  - `src/main/resources/assets/redtale_project/lang/zh_cn.json`、`en_us.json`（**只准新增/覆盖 `item.redtale_project.*` 这 14 个键**，其余键一个都不能删改）
- 接口（命令行，无参数）：
  - 运行方式：`python tools/gen_item_lang.py`（工作目录 = 仓库根；脚本内部用相对仓库根的路径，不要 `os.chdir` 到别处）
  - id 来源：正则扫 `src/main/java/com/redtale/project/items/ItemBase.java` 里枚举常量行的第一个字符串字面量（形如 `    SWORD("sword", Kind.WEAPON, ...` → `sword`），**14 个，不要手工重抄 id 列表**
  - 名称表（写死在脚本里，`zh` / `en` 两个 dict，缺项 → 打印告警并用 id 本身兜底，不崩）：
    `sword 剑/Sword` · `dagger 匕首/Dagger` · `axe 斧/Axe` · `hammer 锤/Hammer` · `spear 长枪/Spear` · `staff 法杖/Staff` · `bow 弓/Bow` · `shield 盾/Shield` · `helmet 头盔/Helmet` · `chestplate 胸甲/Chestplate` · `leggings 护腿/Leggings` · `boots 靴子/Boots` · `ring 戒指/Ring` · `amulet 护符/Amulet`
  - 输出格式：`json.dump(..., indent=2, sort_keys=True, ensure_ascii=False)` + 文件末尾一个换行，UTF-8 **无 BOM**（与现有两份文件同形）
  - **合并语义**：先 `json.load` 现有文件（不存在则空 dict），再只写 `item.redtale_project.<id>`，其余键原样带出
- 不要做：不改 `ItemBase.java`、不改 `gen_attr_lang.py`、不生成 `assets/` 以外的文件、不加命令行参数、不碰 `docs/`、不碰 `RedtaleItems.java`、不做 `/redtale` 子命令
- 验收：
  1. `python tools/gen_item_lang.py` 退出码 0
  2. `grep -c '"item.redtale_project\.' src/main/resources/assets/redtale_project/lang/zh_cn.json` = **14**，`en_us.json` 同样 = 14；且两文件 `grep -c '"attribute.redtale_project\.'` 仍 = **66**
  3. 连跑两次后 `md5sum` 两份文件不变（幂等；把第一次的 md5 与第二次的贴进进度行）
- 进度：
- **撤单**：2026-11-16 08:10 · S7 · 让位给 **T-0006**（`ItemUpgrader` 卡住 M2 出口，lang 只影响显示不影响玩法）。卡内容原样保留、未动一个字，回派单池 **C3**，M2 出口后随时可重派。

### T-0006 · [VERIFIED] `ItemUpgrader.plan` 差异单纯函数（D33 的判定核心）
- 派单：S7 · 2026-11-16 02:16
- 目标：实现 D33 物品更新里**唯一有分支判断的那一步**——给定「物品上现有的 `ContentData`」与「当前配置里的 `ItemContent` 定义」，算出**要不要重建**、重建后 `rolled_stats` 该剩下哪些键、被删掉哪些键。**纯函数**：不读盘、不碰 `ItemStack`、不发事件、不写日志（告警走 `warnings`）。
- 独占文件：
  - `src/main/java/com/redtale/project/items/ItemUpgrader.java`（新建，唯一文件）
  - **不许改任何已有文件**（不接事件、不接 `RedtaleCore`、不碰 `RedtaleCommand`）
- 接口（一字不改）：
  ```java
  package com.redtale.project.items;

  public final class ItemUpgrader {
      public static final int SCHEMA = 1;

      public record Diff(boolean needsRebuild,
                         java.util.Map<String, Double> stats,
                         java.util.List<String> removedKeys,
                         java.util.List<String> warnings) {}

      public static Diff plan(ContentData current, ItemContent definition);
  }
  ```
- 判定规则（逐条照做；`docs/ITEM-UPDATE.md` §4.3 是唯一依据）：
  1. `current == null` 或 `definition == null` → `needsRebuild=false`、`stats` 空、`removedKeys` 空、`warnings` 加一行（`"plan: current/definition 为 null，跳过"`）。**绝不抛异常**。
  2. `current.contentId()` 与 `definition.id()` 不等 → `needsRebuild=false`，`warnings` 加一行（id 不匹配，说明拿错了定义）。`stats` 返回 `current.rolledStats()` 原样。
  3. `current.schema() != SCHEMA` → `needsRebuild=true`，`warnings` 加一行（结构版本迁移；`stats` 仍按规则 5 算）。
  4. **快路径**：`current.schema() == SCHEMA && current.contentRev() == definition.rev()` → `needsRebuild=false`、`stats` 返回 `current.rolledStats()` 原样、`removedKeys` 空。**这一支必须零分配零遍历**（U10：200 件 <50ms）。
  5. 其余情况 → `needsRebuild=true`；新 `stats` **遍历 `current.rolledStats()`**（不是遍历定义！），逐键判定：
     - 键 **不在** `definition.stats()` → 丢进 `removedKeys`，不进 `stats`
     - 键 **在** `current.rolledKeys()` → **保留旧值**（玩家 roll 的，一个都不许改）
     - 其余 → 取 `definition.stats().get(key)` 的**新值**（定义型属性，改配置就该生效）
     **遍历旧键集**，所以新定义多出来的键不会凭空出现（U3：不白送）。删除键顺序与原 Map 迭代顺序一致。
     > 2026-11-16 08:10 修正：原写「值一个都不改」是错的——那样改配置对存量物品完全无效。`rolled_keys` 已加到
     > `ContentData`（第 7 位，`ContentData.rolledKeys()`），本卡按上面三分支实现，详见 `docs/ITEM-UPDATE.md` §3.3。
  6. `removedKeys` 非空时，每个键在 `warnings` 里**不加**行（记账归调用方；本卡只给数据）。`removedKeys` 用 `List.copyOf` 语义，不可变。
  7. 返回值用 `java.util.LinkedHashMap` 保序，返回前包成不可变（`Map.copyOf` 会丢序 → 用 `Collections.unmodifiableMap`）。
- 不要做：不实现 `ensure(ItemStack)`、不碰事件/广播/`playerdata`、不做 ORPHAN 标记、不做 `affixes`/`abilities` 过滤（那要 `AffixPools` 与脚本注册表，R10 接线时 S7 做）、不加命令、不加 `SelfTest`（测试由 S7 写）。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "public static Diff plan" src/main/java/com/redtale/project/items/ItemUpgrader.java` = 1
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "items/ItemUpgrader"` ≥ 2（主类 + 内部 record）
- 进度：
  - 2026-11-16 06:16 · 完成 · 新建 `src/main/java/com/redtale/project/items/ItemUpgrader.java`（1 类 **73 行**，含 `Diff` record；`SCHEMA=1`；卡外文件零改动，`RedtaleCore`/`RedtaleCommand`/事件未碰） · build 退出码 0（`gradle build --offline`，jar 内 `items/ItemUpgrader` 主类 + `$Diff`） · 自测：①`grep -c "public static Diff plan"` = 1；②`unzip -l | grep -c items/ItemUpgrader` = **2**（主类 + `ItemUpgrader$Diff`）；③离线探针 16 项全过（`build/probe/UpgProbe.java`，直调真类）：`null/null` 与 `definition=null` → 不重建 / stats 空 / 1 条告警 / 不抛；id 不匹配 → 不重建 + `rolledStats()` 原样 + 1 条告警；`schema 0≠1`（rev 相同）→ 重建 + 1 条含 `schema` 的告警 + 值不重算；`schema=1 && rev 相同` → `needsRebuild=false`、stats 原样、`removedKeys` 空、`warnings` 空（快路径不遍历）；rev 落后 + 定义删 1 键加 1 键 → 重建、`removedKeys=[attack_speed]`、`physical_damage` 仍 3.0 / `crit_chance` 仍 0.05（未取新定义 77/88）、`new_key` 未白送、两表顺序 = 原 Map 迭代顺序、无逐键告警；`stats`/`removedKeys`/`warnings` 三处均不可变（`put`/`add` 抛 `UnsupportedOperationException`）；空 `rolledStats` + rev 落后 → 重建但两表皆空 · **一处请 S7 确认**：卡面规则 5 写「值一个都不改」而 `docs/ITEM-UPDATE.md` §4.3 写「键不在 `rolled_keys` → 取新定义值」——现**按卡面**实现（未读 `rolled_keys`，数值解析留给调用侧 `ItemFactory.applyDefinition`）；若要在本函数内做 §4.3 的取值分派，请改卡并加一条验收 · 待 S7 验收（本卡无测试服项）
  - 2026-11-16 07:12 · **S7 验收通过（3/3 + 独立探针 14/14）** · ①`gradle build --offline` exit 0（jar 199904 B）；②`grep -c "public static Diff plan"` = 1；③`unzip -l | grep -c items/ItemUpgrader` = **2**（主类 + `$Diff`）。**S7 自写独立探针**（`build/probe/S7UpgProbe.java`，直调真类，不复用 S8 断言）：null/null 与 definition=null 均不重建+1 告警不抛；id 不匹配 → 不重建 + `rolledStats()` 原样 + 1 告警；`schema 0≠1` 且 rev 相同 → 仍重建 + 值不变 + 告警含 `schema`；快路径（schema+rev 全等）→ 不重建/无告警/无删键；rev 落后 + 定义删 1 键加 1 键 → 重建、`removedKeys=[attack_speed]`、`physical_damage` 仍 0.2（未取定义 9.9）、`new_key` 未白送、键序 = 输入 Map 迭代序、无逐键告警；`stats`/`removedKeys` 不可变；空表重建两表皆空；快路径 20 万次 **< 200ms**（折合 200 件 < 0.2ms，U10 达标）。**卡面规则 5 与 `ITEM-UPDATE.md` §4.3 的口径归属裁决：按卡面**——`plan` 只做「旧键集 ∩ 新定义」过滤，**不做「未在 `rolled_keys` 的键取新定义值」的取值分派**（那一步在 `ItemFactory.applyDefinition` 的调用侧，S7 本轮已在 `ensure` 里实现）；S8 提的这处不一致 = 我卡子的边界划分，认账不打回。**新记一条事实**：`ContentData` 构造器用 `Map.copyOf`，`rolled_stats` 的迭代序在 record 构造后**已不可保证**（`ImmutableCollections` 用每 JVM 随机 SALT），所以「保旧 Map 迭代序」只能保证「与传入 Map 的迭代序一致」，跨 JVM 启动不保证——对外只影响删键日志顺序，不影响数值
### T-0007 · [VERIFIED] `/redtale item scan` 只读扫描（D33 的运营可见性）
- 派单：S7 · 2026-11-16 06:12
- 目标：一条**严格只读**命令，扫在线玩家背包里带 `redtale_project:content` 组件的物品，按 `contentRev` 打分布，并报「孤儿」（contentId 在内容表里查不到）与「待更新」（rev ≠ 当前定义 rev）的件数。它是下一张 `/redtale item upgrade` 的地基：先让运营看见分布，再决定批量动作。**本卡不动任何物品。**
- 独占文件：
  - `src/main/java/com/redtale/project/core/command/ItemScanCommand.java`（新建）
  - `src/main/java/com/redtale/project/core/command/RedtaleCommand.java`（**只插入 1 行**：在 `.then(Commands.literal("content").then(Commands.literal("list").executes(ContentListCommand::list)))` 那行**之后**插入 `.then(Commands.literal("item").then(Commands.literal("scan").executes(ItemScanCommand::scan)))`。不改动任何现有行。`ItemScanCommand` 与本文件**同包，不要写 import**）
- 接口（一字不改）：
  ```java
  package com.redtale.project.core.command;

  public final class ItemScanCommand {
      public static int scan(com.mojang.brigadier.context.CommandContext<net.minecraft.commands.CommandSourceStack> ctx);
  }
  ```
  返回扫到的**内容物品牌数**（不是玩家数）。
- 数据来源（照抄，别自己找路）：
  - 玩家：`ctx.getSource().getServer().getPlayerList().getPlayers()`
  - 背包：`player.getInventory().getContainerSize()` + `getItem(i)`，`i` 从 0 到 size-1（`Inventory` 的 size 已含护甲与副手，别自己算槽位）
  - 组件：`stack.get(com.redtale.project.items.ContentComponents.CONTENT.get())`，`null` 即跳过（这是 `ContentData`）
  - 当前定义：`com.redtale.project.core.RedtaleCore.get().contentItems().get(id)` → `ItemContent`（`rev()` 是定义修订号）
- 输出（**行数与文案写死，便于 grep 验收**；全部走 `ctx.getSource().sendSuccess(() -> Component.literal(...), false)`）：
  - 第 1 行：`扫描 N 名玩家：M 件内容物品`
  - 每个 rev 一行、**升序**：`rev=K  x 件`
  - 一行孤儿：`孤儿（定义已不存在）：P 件`；`P > 0` 时追加 `：id1, id2`（**最多 5 个**，还有更多就写 `…等 Q 个`）
  - 一行待更新：`待更新（rev 落后）：R 件`
  - 没有任何内容物品：只打第 1 行 + 第二行 `（无内容物品）`，返回 0
  - 孤儿与待更新的判定**不重叠**：孤儿先判（定义都没有，谈不上 rev 落后）
- 不要做：**不改任何 `ItemStack`**（不许 `set` / `setDamageValue` / `remove`）、不写盘、不打 `LOG`、不加玩家参数、不做 `/upgrade`、**不碰 `ItemUpgrader.java`（T-0006 独占中）**、不加 `SelfTest`
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "ItemScanCommand::scan" src/main/java/com/redtale/project/core/command/RedtaleCommand.java` = 1
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "core/command/ItemScanCommand"` = 1
  > 测试服那条（起服 → `/redtale give demo_longsword` 两件 → `item scan` 件数与 rev 分布对得上）归 S7 跑。
- 进度：
  - 2026-11-16 07:24 · 完成 · 新建 `src/main/java/com/redtale/project/core/command/ItemScanCommand.java`（1 类 **109 行**：`scan()` 遍历 `getPlayerList().getPlayers()` → `getInventory().getContainerSize()/getItem(i)`，`stack.get(ContentComponents.CONTENT.get())` 为 null 即跳过；rev 用 `TreeMap` 保证升序；孤儿先判、待更新只在定义存在时判，两者不重叠；孤儿 id 去重后最多列 5 个、超出折成 `…等 Q 个`）；`core/command/RedtaleCommand.java` 在 `content/list` 那行**之后插入 1 行**（同包无 import，未改任何已有行） · build 退出码 0（取锁 `gradle build --offline`，jar 内 `core/command/ItemScanCommand.class` × 1） · 自测：①`grep -c "ItemScanCommand::scan" RedtaleCommand.java` = 1；②`grep -c "public static int scan" ItemScanCommand.java` = 1；③`unzip -l | grep -c core/command/ItemScanCommand` = **1**（宽匹配 1 / 精确 `.class` 1，无内部 record，与卡面 =1 一致）；④离线探针 `build/probe/ScanProbe.java` **6/6 PASS**（反射直调真类的私有 `orphanLine`）：`P=0` → `孤儿（定义已不存在）：0 件`（不追加 id）；`P=2/2 id` → `…：2 件：ghost_a, ghost_b`；`P=8/8 id` → 只列 5 个 + `…等 3 个`；构造器私有；`scan(CommandContext<CommandSourceStack>)` 存在、`static`、返回 `int` · **三处口径请 S7 知悉（均按卡面实现）**：①第 1 行与其余各行**不带** `[redtale]` 前缀（卡面写「文案写死便于 grep」，故逐字照卡）；②「件」按**栈**计数（每格内容物 = 1 件），未乘 `stack.getCount()`——装备基本不可堆叠，两者等价，若要比对堆叠数请改卡；③`…等 Q 个` 的 Q 取**剩余不同 id 数**（=`去重id数−5`），不是剩余件数 · 另：`src.getServer()==null` 时给一行 failure 并返回 0（防御分支，正常服务端走不到） · 待 S7 验收第 3 条（测试服起服 + 两件 `demo_longsword` + `item scan` 件数/rev 分布对账）
  - 2026-11-16 08:40 · **S7 验收通过（3/3）** · ①`gradle build --offline` exit 0（exit code 实测 0，jar 217330 B→R14 改动后 217382 B）；②`grep -c "ItemScanCommand::scan" RedtaleCommand.java` = **1**；③`unzip -l redtale_project-0.1.0.jar | grep -c "core/command/ItemScanCommand"` = **1**（无内部 record，=1 达标）。**代码复核**：全程只调 `stack.get(...)` 与 `contentItems().get(...)`，零 `set`/`remove`/`setDamageValue`，与卡面「严格只读」一致；`TreeMap` 保证 rev 升序；孤儿先判、待更新只在定义存在时判，两者不重叠；孤儿 id 去重后最多列 5 个。**测试服实测**（`Done` 后 RCON）：`/redtale item scan` 在 0 名在线玩家下输出 **2 行**（`扫描 0 名玩家：0 件内容物品` + `（无内容物品）`）并返回 0，空表路径与卡面一致、零 ERROR。**挂账（第 13 轮）**：件数与 rev 分布的对账需要真实在线玩家的背包（命令只读 `getPlayerList().getPlayers()`，`/redtale give` 也要玩家上下文），本轮无客户端 → 归入「需要一次带客户端的验收窗口」。**不打回**：卡面三条机器验收全过，计数分支依赖在线玩家而非代码缺陷


### T-0008 · [VERIFIED] 消耗品 `use` 段解析器（D23 第一层，纯解析）
- 派单：S7 · 2026-11-16 07:15
- 目标：把物品内容 JSON5 里的 `use` 段（消耗品定义）解析成一个不可变对象。**只解析，不接 `Item.use`、不接 `ItemFactory`、不发效果、不读盘**。schema 见 `docs/ITEM-MODEL.md` §3.1，**照它写，不要自己加字段**。
- 独占文件：
  - `src/main/java/com/redtale/project/items/ConsumableSpec.java`（新建，唯一文件）
  - **不许改任何已有文件**（不接 `RedtaleCore`、不碰 `RedtaleCommand`、不碰 `ItemFactory`/`ContentData`/`ItemContent`）
- 接口（**一字不改**）：
  ```java
  package com.redtale.project.items;

  public final class ConsumableSpec {
      public record Effect(String id, int duration, int amplifier, double chance) {}
      public record Spec(java.util.List<Effect> effects, int restoreFood, double saturation,
                         int cooldownTicks,
                         java.util.List<com.redtale.project.core.script.ScriptCall> script,
                         String consume) {}

      public static Spec parse(com.google.gson.JsonObject root, String source,
                               java.util.List<String> warnings);
  }
  ```
  `ScriptCall` 已存在：`com.redtale.project.core.script.ScriptCall(String type, com.google.gson.JsonObject args)`（**直接复用，不要自己再造一个**）。
- 解析规则（逐条照做，别自由发挥）：
  - **入口**：读 `root.use`。`root` 为 null 或 `use` 缺失 → 返回 **null**（= 不是消耗品，**不告警**）；`use` 存在但不是 JSON 对象 → `warnings.add("<source>: use 不是对象，已跳过")` + 返回 null。
  - `effects`：数组，缺省空 List；每个元素必须是对象，`effect`（注意是 `effect` 键，不是 `type`）必须是非空字符串，缺失/类型错 → 告警一行 + **跳过该项**（不影响其它项）；`duration` 缺省 **200**、`amplifier` 缺省 **0**、`chance` 缺省 **1.0**；`duration < 1` → 夹到 **1** 并告警；`amplifier < 0` → 归 **0** 并告警；`chance` 夹到 **[0.0, 1.0]** 并告警（只在真的夹了才告警）。
  - `restore_food`：缺省 **0**；夹到 **[0, 20]**，超范围告警。
  - `saturation`：缺省 **0.0**；负数归 **0** 并告警。
  - `cooldown_ticks`：缺省 **0**；负数归 **0** 并告警。
  - `script`：数组，缺省空 List；每项对象里**先认 `effect` 键、再认 `type` 键**作为 `ScriptCall.type`（`ITEM-MODEL.md` 写的是 `effect`，`ScriptCall` 字段叫 `type`，这里就是两者的翻译点）；两键都没有 / 非字符串 / 空串 → 告警 + 跳过该项；`args` 缺省 `new JsonObject()`，存在但不是对象 → 告警 + 用空对象。
  - `consume`：只接受 `"always"` / `"only_when_hungry"`，缺省 `"always"`，其它值 → 告警 + 回落 `"always"`。
  - **失败策略**：任何类型不符 / JsonNull / 缺键 → 告警一行 + 默认值或跳过，**绝不抛异常**（与 T-0001/T-0004/T-0006 同一口径）。JSON 数字可能是 `JsonPrimitive` 的 `Number` 形态（`1` / `1.0` / `1L`），取值用 `getAsDouble()` 前先判 `isNumber()`，别 `getAsInt()` 直取。
  - 返回的 `effects` / `script` 用 `List.copyOf`（不可变）。
- 样例（写不出就照这个形状对，放在你自己的临时目录，**不要提交进 `src/main/resources`**）：
  ```json5
  { id: "hearty_stew", use: {
      effects: [{ effect: "minecraft:regeneration", duration: 200, amplifier: 1 }],
      restore_food: 6, saturation: 0.6, cooldown_ticks: 400,
      script: [{ effect: "heal", args: { amount: 4 } }] },
    consume: "only_when_hungry" }
  ```
- 不要做：不实现「右键生效」、不碰 `ItemBase`/`Item#use`、不加 `ContentData` 字段、不注册任何东西、不加命令、不加 `SelfTest`（测试由 S7 在验收时写）、不改 `config/` 与 `src/main/resources/redtale/defaults/`
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "public static Spec parse" src/main/java/com/redtale/project/items/ConsumableSpec.java` = 1
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "items/ConsumableSpec"` ≥ 2（主类 + 内部 record）
  > 解析结果对不对由 S7 用离线探针跑（缺 `use` 返回 null / 五类默认值 / 越界夹取 / 坏项跳过不抛 / 不可变）。
- 进度：
  - 2026-11-16 08:43 · 完成 · 新建 `src/main/java/com/redtale/project/items/ConsumableSpec.java`（1 类 **199 行**，含 `Effect`/`Spec` 两个 record；卡外文件零改动，`RedtaleCore`/`RedtaleCommand`/`ItemFactory`/`ContentData`/`ItemContent` 未碰） · build 退出码 0（取锁 `gradle build --offline`，jar 内 `items/ConsumableSpec` = 主类 + `$Effect` + `$Spec` 共 3 个 class） · 自测：①`grep -c "public static Spec parse"` = 1；②`unzip -l | grep -c "items/ConsumableSpec"` = **3**（≥2 达标；精确主类 `.class` = 1，另两个是 record）；③离线探针 `build/probe/ConsProbe.java` **54/54 PASS**（真类 + gson，无 MC 依赖）：`root=null` 与缺 `use` 均返回 null 且**零告警**；`use:"x"` → null + 1 条 `use 不是对象` 告警；§3.1 样例全字段对（effects=1 / regen 200 / amp1 / chance 缺省 1.0 / food6 / sat0.6 / cd400 / script `type=heal` + `args.amount=4` / `consume=only_when_hungry`，零告警）；`use:{}` 全缺省 = 空表/0/0.0/0/空表/`always` 且零告警；越界夹取全对（duration 0→1、-9→1、amplifier -3→0、chance 1.5→1.0 与 -0.2→0.0、restore_food 25→20、saturation -1→0、cooldown -5→0、坏 `consume:"sometimes"`→`always`，共 9 条告警）；坏项跳过不抛（非对象项 / 缺 `effect` / `effect:""` / `duration:"200"`→默认 200 / `chance:"x"`→1.0 / script 认 `type` 键 / `args` 非对象与 `args:null` → 空对象 / 空串与空白 type 各自跳过，共 9 条告警 + `effect:""` 类 2 条）；`effects:null`、`script:{}`、`restore_food:null` 均走「告警 + 默认」不抛；`effects`/`script` 均不可变（`add` 抛 `UnsupportedOperationException`） · **一处按文档定位置请 S7 知悉**：`consume` 从**根节点**读（不在 `use` 内），依 `ITEM-MODEL.md` §3.1 样例写法；卡面规则未明说层级，若本意是 `use.consume` 请改卡 · 待 S7 验收（本卡无测试服项）
  - 2026-11-16 09:56 · **S7 验收通过（3/3 + 独立探针 48/48）** · ①`gradle build --offline` exit 0（jar 223951 B → 本轮接线后 232730 B）；②`grep -c "public static Spec parse"` = **1**；③`unzip -l | grep -c "items/ConsumableSpec"` = **3**（主类 + `$Effect` + `$Spec`，≥2 达标）。**S7 自写独立探针**（`build/probe/S7ConsProbe.java`，不复用 S8 的 `ConsProbe` 断言）**48/48 PASS**：非消耗品两条路径（`root=null` / 缺 `use`）均 null 且**零告警**；`use:"x"` → null + 1 告警；§3.1 样例逐字段对（effects=1 / regen 200t×1 / chance 缺省 1.0 / food 6 / sat 0.6 / cd 400 / script `type=heal` + `args.amount=4` / `only_when_hungry`，零告警）；`use:{}` 六项全缺省且零告警；越界夹取 8 条告警逐条对（duration 0 与 -5 → 1、amplifier -2 → 0、chance 1.2 → 1.0 与 -0.3 → 0.0、food 100 → 20、sat -1.5 → 0、cd -9 → 0）；`chance` 恰为 0.0 / 1.0 **不告警**；坏项 7 条告警且幸存项正确（`effects` 剩 1 条 `minecraft:haste`、`script` 剩 2 条、`args` 非对象 → 空对象、`consume:"sometimes"` → always）；两表**不可变**（`add`/`clear` 抛 `UnsupportedOperationException`）；非数字字段 4 条告警走默认。**`consume` 从根节点读已定为口径**（`ITEM-MODEL.md` §3.1 样例即如此），S8 提的位置偏差不打回。**该文件已归 S7**：本轮已把它接进 `ItemContent.consumable()`（第 11 字段）+ `ContentItem#use`

### T-0009 · [VERIFIED] `/redtale item upgrade` 写回命令（D33 的「敢写」那一半）
- 派单：S7 · 2026-11-16 08:15
- 目标：给执行者自己的背包跑一遍 `ItemUpgrader.ensure`，把结果计数报出来，并在有升级时让客户端立刻看到。
  `scan` 是只读的、`ensure` 是纯写单件，本卡只做**「遍历 + 计数 + 同步」**这一层胶水。
- 独占文件：
  - `src/main/java/com/redtale/project/core/command/ItemUpgradeCommand.java`（新建，唯一文件）
  - **不许改任何已有文件**。`RedtaleCommand` 里挂那一行由 **S7** 做（参照 T-0002 的做法）。
- 接口（一字不改）：
  ```java
  package com.redtale.project.core.command;

  public final class ItemUpgradeCommand {
      /** 返回升级的件数（Brigadier 只认 int，失败也要返回 ≥0，不要返回 -1）。 */
      public static int upgrade(com.mojang.brigadier.context.CommandContext<net.minecraft.commands.CommandSourceStack> ctx);
  }
  ```
- 行为（逐条照做）：
  1. `ServerPlayer player = ctx.getSource().getPlayerOrException();`（非玩家执行 → 抛 `CommandSyntaxException` 让它走原版报错，别自己 catch）。
  2. 遍历 `player.getInventory()` 的第 `0 .. getContainerSize()-1` 格；每格取 `getItem(i)`，直接调
     `ItemUpgrader.ensure(stack)`，按返回的 `Status` 计数：`NOT_CONTENT` 不计、`UNCHANGED`/`UPGRADED`/`ORPHAN` 各计一个。
     **不要**先判断 `isEmpty()` 之外的东西，也不要用 `stack.copy()`。
  3. 遍历 `player.getEnderChestInventory()` 同样处理，单独计数，**不要** `setChanged()`（末影箱在下次打开时自然同步）。
  4. 若有 `UPGRADED`：调一次 `player.inventoryMenu.broadcastChanges();`（只这一句，不要 `broadcastFullState`、不要逐格 `setRemoteSlot`）。
  5. 汇总 `sendSuccess` 一行：`物品更新：扫描 <N> / 升级 <M> / 已最新 <U> / 孤儿 <K>`（末影箱非零时追加 `· 末影箱 升级 <m2>/孤儿 <k2>`）。
  6. 把**前 3 条** `Result.warnings()` 用 `Component.literal` 逐行 `sendSystemMessage` 给执行者，超出部分只报条数。
     一条 warning 都没有就不发这段（别刷屏）。
  7. 任何 `RuntimeException` 都在**单格**内 catch：计一个「失败」，`warnings` 里加一行，继续下一格，**绝不中断整轮**。
- 不要做：不做 `--all` / 全服扫描、不做分帧、不做权限等级（默认所有玩家可对自己用）、不发 `@a` 广播、
  不写 `playerdata`、不碰 `ChunkEvent` / `PlayerContainerEvent`、不改 `ItemUpgrader` / `ItemFactory` / `ContentData`、
  不加 `SelfTest`（测试由 S7 写）。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "ItemUpgrader.ensure" src/main/java/com/redtale/project/core/command/ItemUpgradeCommand.java` = 2（背包 + 末影箱各一次）
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "command/ItemUpgradeCommand"` = 1
  > 命令真跑由 S7 验（起测试服 → 拿一件 `rev` 落后的物品 → 执行 → 打印行数与客户端 tooltip 是否立刻变）。
- 进度：
  - 2026-11-16 10:03 · 完成 · 新建 `src/main/java/com/redtale/project/core/command/ItemUpgradeCommand.java`（1 类 **123 行**，卡外文件零改动，`RedtaleCommand` 未碰——挂行归 S7） · build 退出码 0（取锁 `gradle build --offline`，两次构建都 exit 0） · 自测：①`grep -c "ItemUpgrader.ensure"` = **2**（背包 1 + 末影箱 1，无第三处）；②`unzip -l | grep -c "command/ItemUpgradeCommand"` = **1**（首版用 `switch` 枚举生成 `$1` 合成类导致计数 =2，改成 if/else 链后只剩主类，与卡面 =1 一致）；③`javap` 产物签名 = `public static int upgrade(CommandContext<CommandSourceStack>) throws CommandSyntaxException`，并核对 `com.mojang.brigadier.Command#run` 同声明 `throws CommandSyntaxException` → 可直接 `.executes(ItemUpgradeCommand::upgrade)` · API 全部在 `minecraft-merged-mojang-patched.jar` 核过：`CommandSourceStack#getPlayerOrException() throws CommandSyntaxException`、`Player#getInventory()`、`Player#getEnderChestInventory()` → `PlayerEnderChestContainer extends SimpleContainer implements Container`（故末影箱用 `Container` 接）、`Player#inventoryMenu` 字段类型 `InventoryMenu` 且 `AbstractContainerMenu#broadcastChanges()` 返回 void · **三处请 S7 知悉**：①签名多了 `throws CommandSyntaxException`——`getPlayerOrException()` 是受检异常，不 catch 就必须声明；`Command#run` 同样声明该异常，`::upgrade` 引用不受影响，但严格说比卡面接口多一个 throws 子句；②`broadcastChanges()` 的触发条件是「背包或末影箱有任一 UPGRADED」（卡面写「若有 UPGRADED」未区分两侧），末影箱自己那一份同步仍靠下次打开；③「扫描 N」= 非空格的件数（含原版物品），故 `N ≥ M+U+K`；返回值为「背包 + 末影箱」升级件数之和；失败件数不进汇总行（卡面样式写死 4 段），仅以提示行体现，若要进汇总行请改卡 · 待 S7 验收第 3 条（起测试服 → `rev` 落后物品 → 执行 → 行数与客户端 tooltip 立刻变）
  - 2026-11-16 11:30 · **S7 验收通过（2/3 + 第 3 条部分）** · ①`gradle build --offline` exit 0（jar 252285→256k 区间，本轮多次重建均 exit 0）；②`grep -c "ItemUpgrader.ensure"` = **2**（背包 + 末影箱，无第三处）；③`unzip -l | grep -c "command/ItemUpgradeCommand"` = **1**。**代码复核**：逐格 `ItemUpgrader.ensure(stack)`、不 `copy()`、单格 `RuntimeException` 兜住继续、只有 `upgraded>0` 才 `broadcastChanges()` 一次 —— 与卡面 7 条逐条对上。**测试服实测**（`Done (2.490s)`，RCON）：挂行已由 S7 补进 `RedtaleCommand`（`.then(Commands.literal("upgrade"))`），控制台执行返回 **`A player is required to run this command here`** = 命令已注册并走到 `getPlayerOrException`，命令树与签名正确。**挂账（第 15 轮）**：`rev` 落后物品 → 行数计数 → 客户端 tooltip 立刻变，三者都要真人背包，归入「带客户端的验收窗口」；不打回（代码与注册均通过，缺的只是玩家上下文）

### T-0010 · [VERIFIED] 修理段 `repair` 解析器（D23 第二半，纯解析）
- 派单：S7 · 2026-11-16 08:42
- 目标：把物品内容 JSON5 里的 `repair` 段（磨刀石这类「作用于别的物品」的修理物品）解析成一个不可变对象。
  **只解析**：不实现修理结算、不扣费、不接 `Item#use`、不读盘、不发效果。schema 见 `docs/ITEM-MODEL.md` §3.2，**照它写，不要自己加字段**。
- 独占文件：
  - `src/main/java/com/redtale/project/items/RepairSpec.java`（新建，唯一文件）
  - **不许改任何已有文件**（不接 `RedtaleCore`、不碰 `RedtaleCommand`、不碰 `ItemFactory`/`ContentData`/`ItemContent`/`ConsumableSpec`）
- 接口（**一字不改**）：
  ```java
  package com.redtale.project.items;

  public final class RepairSpec {
      public record Cost(String currency, int amount) {}
      public record Spec(java.util.List<String> targets, String mode, int amount, double percent,
                         Cost cost, boolean consumeItem) {}

      public static Spec parse(com.google.gson.JsonObject root, String source,
                               java.util.List<String> warnings);
  }
  ```
- 解析规则（逐条照做，别自由发挥）：
  - **入口**：读 `root.repair`。`root` 为 null 或 `repair` 缺失 → 返回 **null**（= 不是修理物品，**不告警**）；
    `repair` 存在但不是 JSON 对象 → `warnings.add("<source>: repair 不是对象，已跳过")` + 返回 null。
  - `targets`：字符串数组，缺省**空 List**（空 = 不限制目标，由调用方按「任意可损坏物品」处理）。
    元素非字符串 / 空串 → 告警一行 + **跳过该元素**（不影响其它元素）。
  - `mode`：只接受 `"amount"` / `"percent"`，缺省 `"amount"`，其它值 → 告警 + 回落 `"amount"`。
  - `amount`：缺省 **0**；非数字 → 告警 + 0；负数 → 归 **0** 并告警。
  - `percent`：缺省 **0.0**；非数字 → 告警 + 0；夹到 **[0.0, 1.0]**，**只在真的夹了才告警**。
  - `cost`：缺省 **null**（= 不收费）；存在但不是对象 → 告警 + null；
    `currency` 缺省 `""`，非字符串 → 告警 + `""`；`amount` 缺省 0、负数归 0 并告警；
    **`currency` 为空串且 `amount <= 0` → 返回 null**（归一成「不收费」，不告警）。
  - `consume_item`：缺省 **true**；非布尔 → 告警 + `true`。
  - **失败策略**：任何类型不符 / JsonNull / 缺键 → 告警一行 + 默认值或跳过，**绝不抛异常**
    （与 T-0001/T-0004/T-0006/T-0008 同一口径）。数字取值前先判 `isNumber()`，别 `getAsInt()` 直取。
  - 返回的 `targets` 用 `List.copyOf`（不可变）；两个 record 天然不可变。
- 样例（写不出就照这个形状对，放你自己的临时目录，**不要提交进 `src/main/resources`**）：
  ```json5
  { id: "whetstone", repair: {
      targets: ["#minecraft:swords", "#minecraft:axes"],
      mode: "amount", amount: 120,
      cost: { currency: "coin", amount: 50 },
      consume_item: true } }
  ```
- 不要做：不实现修理结算 / 耐久计算 / 扣费、不碰 `ItemBase`/`Item#use`/`ItemStack`、
  不给 `ContentData`/`ItemContent` 加字段、不加命令（`/redtale repair` 由 S7 做）、不加 `SelfTest`（测试由 S7 写）、
  不改 `config/` 与 `src/main/resources/`
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "public static Spec parse" src/main/java/com/redtale/project/items/RepairSpec.java` = 1
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "items/RepairSpec"` ≥ 2（主类 + 内部 record）
  > 解析结果对不对由 S7 用离线探针跑（缺 `repair` 返回 null / 五类默认值 / 越界夹取 / 坏项跳过不抛 / 不可变）。
- 进度：
  - 2026-11-16 11:09 · 完成 · 新建 `src/main/java/com/redtale/project/items/RepairSpec.java`（1 类 **176 行**，含 `Cost`/`Spec` 两个 record；卡外文件零改动，`RedtaleCore`/`RedtaleCommand`/`ItemFactory`/`ContentData`/`ItemContent`/`ConsumableSpec` 未碰） · build 退出码 0（取锁 `gradle build --offline` 两次均 exit 0，jar 241798 B，`unzip -l | grep -c items/RepairSpec` = **3**（主类 + `$Cost` + `$Spec`，≥2 达标；精确主类 `.class` = 1）） · 自测：①`grep -c "public static Spec parse"` = 1；②离线探针 `build/probe/RepairProbe.java` **59/59 PASS**（真类 + gson，无 MC 依赖）：`root=null` 与缺 `repair` 均返回 null 且**零告警**；`repair:"x"` / `repair:null` → null + 1 条 `repair 不是对象` 告警；§3.2 样例全字段对（targets=2 / mode=amount / amount=120 / percent 缺省 0.0 / cost=`coin`×50 / consume_item=true，零告警）；`repair:{}` 六项全缺省（空表 / amount / 0 / 0.0 / null / true）且零告警；越界夹取全对（amount -5→0 且告警、percent 1.5→1.0 与 -0.2→0.0 各 1 条告警，恰为 0.0 / 0.25 / 1.0 **不告警**）；`mode` 只认 amount/percent（`"percent"` 通过、`"fix"` 与数字 7 各回落 amount + 1 告警）；`targets` 非字符串与空白串逐项跳过（幸存 `ok`，2 条告警）、非数组 → 空表 + 1 告警；`cost` 缺省/{}/{currency:，amount:0} 全归一 null 且零告警、`cost:"x"` → null + 1 告警、`{amount:5}`（无 currency）→ `Cost("",5)`、`{currency:"coin"，amount:-3}` → amount 归 0 + 1 告警、`{currency:9，amount:"x"}` → 2 条告警后归一 null；`consume_item:false` 生效且零告警、`"yes"` → true + 1 告警；`targets` **不可变**（`add` 抛 `UnsupportedOperationException`）；构造器私有、`parse(JsonObject,String,List)` 返回 `Spec`、`warnings=null` 不 NPE · 待 S7 验收（本卡无测试服项）
  - 2026-11-16 11:30 · **S7 验收通过（3/3 + 独立探针 38/38）** · ①`gradle build --offline` exit 0；②`grep -c "public static Spec parse"` = **1**；③`unzip -l | grep -c "items/RepairSpec"` = **3**（主类 + `$Cost` + `$Spec`，≥2 达标）。**S7 自写独立探针**（`build/probe/S7RepairProbe.java`，不复用 S8 的 `RepairProbe` 断言）**38/38 PASS**：`root=null` / `repair` 缺失 → null 且**零告警**；`repair:"x"` 与 `repair:null` → null + 1 告警；§3.2 样例逐字段对（targets 2 / amount / 120 / percent 缺省 0.0 / `coin`×50 / consume_item true、零告警）；`repair:{}` 六项全缺省且零告警；`amount -5→0`、`percent 1.5→1.0 / -0.2→0.0` 各 1 告警，而 `0` 与 `0.0` 边界**不告警**；`mode` 只认小写 amount/percent（`AMOUNT` 与数字 7 各回落 + 1 告警）；`targets` 里空串/数字/null 三项逐条告警、幸存项 **trim 后** 入表、非数组→空表+1 告警、**不可变**；`cost:{}`→null 不告警、`{amount:5}`→保留（`Cost("",5)`）、只有 currency→`Cost(coin,0)`、`amount:-3`→0+告警、`cost:"x"`→null+1 告警、双坏字段→2 告警后归一 null；`consume_item:false` 生效、`:1`→true+1 告警；`amount/percent` 非数字→默认 + 2 告警。**该文件已归 S7**：本轮接入 `ItemContent.repair()`（第 12 字段）+ `Repairer` 结算 + `/redtale repair`

### T-0011 · [VERIFIED] `tools/gen_item_lang.py` 基底物品 lang 生成器（原 T-0005，重派）
- 派单：S7 · 2026-11-16 09:58（内容与 T-0005 一字不差，只是换了号——T-0005 已被撤单，卡号不复用）
- 目标：14 个基底物品（`redtale_project:sword` … `amulet`）**一条 lang 键都没有**（`grep -c "item.redtale_project" zh_cn.json` = **0**），`/give` 与背包里显示裸键 `item.redtale_project.sword`。写一个幂等脚本，从 `ItemBase.java` 读出 14 个 id，把中英文名**合并**进两份 lang 文件（`attribute.*` 66 条必须原样保留 —— `gen_attr_lang.py` 会整份重写，本脚本不能那样）。
- 独占文件：
  - `tools/gen_item_lang.py`（新建）
  - `src/main/resources/assets/redtale_project/lang/zh_cn.json`、`en_us.json`（**只准新增/覆盖 `item.redtale_project.*` 这 14 个键**，其余键一个都不能删改）
- 接口（命令行，无参数）：
  - 运行方式：`python tools/gen_item_lang.py`（工作目录 = 仓库根；脚本内部用相对仓库根的路径，不要 `os.chdir` 到别处）
  - id 来源：正则扫 `src/main/java/com/redtale/project/items/ItemBase.java` 里枚举常量行的第一个字符串字面量（形如 `    SWORD("sword", Kind.WEAPON, ...` → `sword`），**14 个，不要手工重抄 id 列表**
  - 名称表（写死在脚本里，`zh` / `en` 两个 dict，缺项 → 打印告警并用 id 本身兜底，不崩）：
    `sword 剑/Sword` · `dagger 匕首/Dagger` · `axe 斧/Axe` · `hammer 锤/Hammer` · `spear 长枪/Spear` · `staff 法杖/Staff` · `bow 弓/Bow` · `shield 盾/Shield` · `helmet 头盔/Helmet` · `chestplate 胸甲/Chestplate` · `leggings 护腿/Leggings` · `boots 靴子/Boots` · `ring 戒指/Ring` · `amulet 护符/Amulet`
  - 输出格式：`json.dump(..., indent=2, sort_keys=True, ensure_ascii=False)` + 文件末尾一个换行，UTF-8 **无 BOM**（与现有两份文件同形）
  - **合并语义**：先 `json.load` 现有文件（不存在则空 dict），再只写 `item.redtale_project.<id>`，其余键原样带出
- 不要做：不改 `ItemBase.java`、不改 `gen_attr_lang.py`、不生成 `assets/` 以外的文件、不加命令行参数、不碰 `docs/`、不碰 `RedtaleItems.java`、不做 `/redtale` 子命令
- 验收：
  1. `python tools/gen_item_lang.py` 退出码 0
  2. `grep -c '"item.redtale_project\.' src/main/resources/assets/redtale_project/lang/zh_cn.json` = **14**，`en_us.json` 同样 = 14；且两文件 `grep -c '"attribute.redtale_project\.'` 仍 = **66**
  3. 连跑两次后 `md5sum` 两份文件不变（幂等；把第一次的 md5 与第二次的贴进进度行）
- 进度：
  - 2026-11-16 12:12 · 完成 · 新建 `tools/gen_item_lang.py`（102 行）；`src/main/resources/assets/redtale_project/lang/zh_cn.json`、`en_us.json` 各**只增** `item.redtale_project.*` 14 键（其余 67 键逐条未变：66 `attribute.*` + 1 `death.attack.*`） · build 退出码 0（取锁 `gradle build --offline`，jar 254478 B；jar 内两份 lang 各 14 个 item 键） · 自测：①`python tools/gen_item_lang.py` exit 0，正则解析出 **14** 个 id（sword, dagger, axe, hammer, spear, staff, bow, shield, helmet, chestplate, leggings, boots, ring, amulet）；②`grep -c '"item.redtale_project.'` = **14 / 14**，`grep -c '"attribute.redtale_project.'` 仍 = **66 / 66**，`death.attack` 1 条仍在，两文件各 81 键且键集相同；③连跑两次 md5 不变（zh_cn `8f869d988d1576e3c3a4bab1edaa5870`、en_us `41df1b72c8905121fe93b54cad958871`，两次字节级 `cmp` 相同）；④非 item 键 67 条与 `gen_attr_lang.py` 权威表逐条比对**全等**（SELFTEST=PASS），样例 `leggings=护腿`；⑤UTF-8 **无 BOM**、CRLF 保留（与原文件同形） · **两处请 S7 知悉**：①`gen_attr_lang.py` 是**整体覆写**，单跑一次就会抹掉这 14 个 item 键 —— 两脚本执行顺序必须是「先 attr 后 item」，或由 S7 决定是否把 item 键搬进该脚本的 `EXTRA`；②脚本对 id 数 ≠14 只在 stderr 警告、不中止（防真加第 15 基底时硬失败），解析到 0 个才返回 2 · 待 S7 验收（本卡无测试服项；lang 生效需客户端资源重载）
  - 2026-11-16 12:38 · **S7 验收通过（3/3）** · ①`python tools/gen_item_lang.py` exit 0（解析到 14 个基底 id，且**从未手工抄表**：正则读 `ItemBase.java`）；②`grep -c '"item.redtale_project\.'` zh/en 各 **14**、`grep -c '"attribute.redtale_project\.'` 仍 **66/66**，另 `death.attack.*` 1 条仍在（两文件各 81 键）；**jar 内实测** `unzip -p …/lang/zh_cn.json` 同样 14 / 66，`gradle build --offline` exit 0（jar 254478 B）；③连跑两次 `md5sum` 逐字相同（zh_cn `8f869d988d1576e3c3a4bab1edaa5870`、en_us `41df1b72c8905121fe93b54cad958871`），UTF-8 **无 BOM**（首字节 `7b 0d 0a` = `{` + CRLF）。**S8 提的两处偏差处理**：①`gen_attr_lang.py` 整体覆写会抹掉 item 键 → 已接受为**执行顺序约束**（先 attr 后 item），本轮在 `docs/BUILD.md` 侧不改脚本，只在台账记；②id 数 ≠14 只在 stderr 警告不中止 → 接受（真加第 15 基底时不该硬失败）。测试服无验收项（lang 生效需客户端资源重载，归入带客户端窗口）

### T-0012 · [VERIFIED] `/redtale content check` —— `rev` 漏加检测（D33 的发布纪律检查）

- 派单：S7 · 2026-11-16 11:35
- 目标：D33 的发布纪律是「改任何定义型字段必须 `rev` +1」，但**漏加不报错**——只是存量物品静默不更新（`PLAN.md` §4 `rev` 一条 / `docs/CONTRACTS.md` §4）。做一个只读检查：把每份 `items/*.json5` 的**内容哈希**与**上次基线的哈希/rev** 比对，哈希变了但 `rev` 没变 → 逐条报出来。基线存在 `config/redtale_project/.rev-baseline.json`（跨重启保留，否则这功能等于每轮重启就失忆）。
- 独占文件：
  - `src/main/java/com/redtale/project/core/command/ContentCheckCommand.java`（新建，唯一新建类）
  - `src/main/java/com/redtale/project/core/command/RedtaleCommand.java`（**只插入 1 行**：在 `.then(Commands.literal("content").then(Commands.literal("list").executes(ContentListCommand::list)))` 那行**之后**插入 `.then(Commands.literal("content").then(Commands.literal("check").executes(ContentCheckCommand::check)))`。不改动任何现有行；`ContentCheckCommand` 与本类同包，**不要写 import**）
- 接口（一字不改）：
  ```java
  package com.redtale.project.core.command;

  public final class ContentCheckCommand {
      public static final String BASELINE_FILE = ".rev-baseline.json";
      /** 返回「rev 漏加」的份数（不是检查的总份数）；基线刚建立时返回 0。 */
      public static int check(com.mojang.brigadier.context.CommandContext<net.minecraft.commands.CommandSourceStack> ctx);
  }
  ```
- 行为（逐条照做）：
  1. 配置根：`com.redtale.project.core.RedtaleCore.get().config().root()`（`Path`）。基线文件 = `root.resolve(BASELINE_FILE)`。
  2. 待检文件：`java.nio.file.Files.walk(root)` 里**所有** `*.json5`（跳过以 `.` 开头的文件名），**只对 `items/` 前缀**做 rev 判定；其余文件只更新基线、不判定（它们没有 `rev` 概念）。
  3. 每份文件算 **SHA-256**（`MessageDigest.getInstance("SHA-256")`，对**文件字节**），取十六进制前 **16** 位。不要用 `String.hashCode()`。
  4. `rev` 从内存里的定义读**最容易错**，所以规定：用 `com.redtale.project.core.config.Json5.parse(<文件全文>)` 解析，取 `root.get("rev")`，非数字/缺失 → **0**（缺省 = 0，与 `ItemContent.parse` 一致）。解析抛异常 → 该文件一行告警 `  <path>: 解析失败（<异常类名>），跳过`，不进基线。
  5. 基线文件格式（自己读写，用 gson `JsonObject` + pretty printing + 末尾换行）：
     ```json
     { "files": { "items/demo_longsword.json5": { "hash": "a1b2c3d4e5f60718", "rev": 3 } } }
     ```
  6. 判定（只对 `items/`）：
     - 基线里有、哈希**不同**、`rev` **等于**基线 rev → **漏加**，记一行
     - 基线里有、哈希不同、`rev` **小于**基线 rev → **倒退**，单独记一行（`rev` 只许增）
     - 基线里有、哈希相同 → 无问题（`rev` 变没变都不管：没改内容就不需要 rev）
     - 基线里没有 → 新文件，无问题（首次出现没有「上次」可比）
  7. 输出（**文案写死便于 grep**，全部走 `ctx.getSource().sendSuccess(() -> Component.literal(...), false)`）：
     - 第 1 行：`内容检查：N 份 json5（items M 份）· rev 漏加 K 份`
     - 有问题时每条一行：`  <path>: 内容已改但 rev 没加（基线 3 → 当前 3）` / `  <path>: rev 倒退（基线 5 → 当前 4）`
     - 无问题且不是首次：`  （没有 rev 漏加）`
     - 首次（基线文件不存在）：只打第 1 行 + `  已建立基线 N 份（下次起参与比对）`，**返回 0**
     - 末行：`  基线已更新：<baseline 绝对路径>`
  8. 出错（`IOException` / 任何 `RuntimeException`）→ `sendFailure` 一行 + 返回 0，**绝不抛**（reload 不能因为这个命令崩）。
  9. 基线写入顺序：**先算完、判定完、打印完，最后才写盘**（中途抛异常不能把基线改脏）。
- 不要做：不改任何 `items/*.json5`、不自动 +1 rev、不碰 `ItemContent`/`ItemUpgrader`/`ContentData`、不做 `/redtale reload` 联动、不解析 `rev` 以外的字段、不加 `SelfTest`（测试由 S7 写）、不打 `LOG`
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "ContentCheckCommand::check" src/main/java/com/redtale/project/core/command/RedtaleCommand.java` = 1
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "core/command/ContentCheckCommand"` = 1
  > 功能验收归 S7：测试服跑第一次（建基线、返回 0）→ 改一份 `items/*.json5` 但不加 rev → 再跑（报 1 份漏加）→ 把 rev +1 → 再跑（报 0）。命令要走 RCON，不归 S8。
- 进度：
- 2026-11-16 13:26 · 完成 · 新建 `src/main/java/com/redtale/project/core/command/ContentCheckCommand.java`（1 类 **200 行**，无内部类型；判定抽成私有纯函数 `judge`）、`core/command/RedtaleCommand.java` 在 `content/list` 那行**之后追加 2 行**（1 行说明注释 + 1 行 `content/check` 注册，未改任何已有行；同包无 import） · build 退出码 0（取锁 `gradle build --offline`） · 自测：①`grep -c "ContentCheckCommand::check"` = **1**；②`unzip -l | grep -c "core/command/ContentCheckCommand"` = **1**（精确保守：全类无 record / 内部类，不会出现 `$Entry` 计数）；③离线探针 `build/probe/CheckProbe.java` **32/32 PASS**（反射直调真类 `scan`/`judge`/`readBaseline`/`write`，jar+gson+server-test libraries）：scan 只吃 5 份 json5（`.hidden.json5`/README 不吃、`.rev-baseline.json` 不自我扫描）、rel 用正斜杠、hash = 文件字节 SHA-256 前 16 位且 16 位小写十六进制、缺 rev → 0、坏文件带 `error` 且是异常类名；基线写盘：pretty 打印 + 末尾一个换行、4 项（坏文件不进基线）、两次写字节一致（幂等）；`readBaseline` 读回 4 项、hash/rev 对上、文件不存在 → `null`；判定：无改动 0 问题 → 改内容不加 rev 报 **1 条**（文案逐字 `  items/a.json5: 内容已改但 rev 没加（基线 3 → 当前 3）`、missed=1）→ 改内容且 rev+1 无问题 → rev 倒退报 1 条（`  items/a.json5: rev 倒退（基线 3 → 当前 2）`、missed **不计**）→ 新文件 / 非 items 改动 / 坏文件均无问题 → 哈希回原样无问题；空 rows / 空基线 0 问题不抛 · **四处请 S7 知悉（均按卡面实现，无一处自选口径）**：①首次运行除「第 1 行 + 已建立基线 N 份」外**也**打了末行 `  基线已更新：<绝对路径>`（卡面第 7 条「只打…」与「末行」两处冲突，取末行规则，若不要请改卡）；②`rev` 负数按 **0**（卡面只写「非数字/缺失 → 0」，负数口径取 `ItemContent.parse` 的 `rev < 0 → 0` 同款）；③解析失败的文件**既告警也不进基线**，告警行排在问题行之前；④卡面指定的挂法是两条同名的 `.then(Commands.literal("content")…)` 兄弟节点 —— 已 `javap -c` 核对 Brigadier **1.3.10** `CommandNode#addChild`：取到同名子节点时走「设 command + 递归 addChild 合并子命令」，所以 `content list` 不会被覆盖，但**这一点只能在测试服实测确认**，已挂账 · 另：内部私有 `write` 返回值改 void（卡面无此约定，非契约方法） · 待 S7 验收第 3 条（测试服：首次建基线返回 0 → 改一份 `items/*.json5` 不加 rev → 报 1 份 → rev+1 → 报 0；顺带确认 `content list` 仍可用）
  - 2026-11-16 13:44 · **S7 验收通过（3/3 + 功能四跑全过）** · ①`gradle build --offline` exit 0（jar 262440 B）；②`grep -c "ContentCheckCommand::check" RedtaleCommand.java` = **1**；③`unzip -l | grep -c "core/command/ContentCheckCommand"` = **1**（无内部类）。**测试服实测（`Done (2.398s)`，RCON，跑完已停服）**四跑：①首次 `内容检查：17 份 json5（items 8 份）· rev 漏加 0 份` + `已建立基线 17 份` + 基线绝对路径，返回 0；②把 `items/demo_longsword.json5` 的 `physical_damage 0.2→0.25` 且**不加 rev** → `rev 漏加 1 份` + 逐字 `  items/demo_longsword.json5: 内容已改但 rev 没加（基线 0 → 当前 0）`；③加 `rev: 1` → `rev 漏加 0 份` + `  （没有 rev 漏加）`；④还原文件（`rev` 回到 0，字节级 `cmp` 与备份一致）→ `  items/demo_longsword.json5: rev 倒退（基线 1 → 当前 0）` 且 **missed 仍为 0**（倒退单列不计入 K）。删基线后再跑回到「已建立基线」态，验收现场已清理。**S8 挂账的两处均已实测确认**：①`content` 两条同名兄弟节点下 `content list` **仍可用**（运行时 8 行输出正常），Brigadier 1.3.10 `addChild` 同名合并成立；②首次运行确实同时打了「已建立基线 N 份」与末行「基线已更新：<路径>」（取末行规则，接受，不改卡）。零 redtale ERROR/WARN；`ERROR` 计数 0

### T-0013 · [VERIFIED] `SocketSpec` 孔位布局 + 宝石定义解析器（M3 第一层，纯解析）

- 派单：S7 · 2026-11-16 12:45
- 目标：把 `docs/ITEM-MODEL.md` **§5.2（物品侧 `sockets` 段）** 与 **§5.3（宝石 `gem` 段）** 解析成两个不可变对象。**只解析**：不实现镶嵌/取出、不读盘、不碰 `ContentData`、不加命令。
- 独占文件：
  - `src/main/java/com/redtale/project/items/SocketSpec.java`（新建，唯一文件）
  - **不许改任何已有文件**（不接 `RedtaleCore`、不碰 `RedtaleCommand`/`ItemFactory`/`ContentData`/`ItemContent`/`ItemBase`）
- 接口（**一字不改**）：
  ```java
  package com.redtale.project.items;

  public final class SocketSpec {
      public record Layout(int count, java.util.List<String> types) {
          public static final Layout EMPTY = new Layout(0, java.util.List.of());
      }
      public record Gem(String type, int tier, String exclusiveGroup,
                        java.util.Map<String, com.redtale.project.core.math.StatValue> stats) {}

      public static Layout parseLayout(com.google.gson.JsonObject root, String source,
                                       java.util.List<String> warnings);
      public static Gem parseGem(com.google.gson.JsonObject root, String source,
                                 java.util.List<String> warnings);
  }
  ```
- `parseLayout` 规则（§5.2，逐条照做）：
  - `root` 为 null 或 `sockets` 缺失 → `Layout.EMPTY`，**不告警**；`sockets` 存在但不是对象 → `warnings.add("<source>: sockets 不是对象，已跳过")` + `EMPTY`。
  - `count`：缺省 **0**；非数字 → 告警 + 0；`< 0` → 归 **0** + 告警；`> 6` → 夹到 **6** + 告警。夹完后 `count == 0` → **直接返回 `Layout.EMPTY`**（不再管 `types`）。
  - `types`：数组，缺省空表；非数组 → 告警 + 空表。元素处理：非字符串 / `trim` 后空 → **替换成 `"any"`** + 告警（**不许跳过**，否则孔序错位）；合法元素 `trim` 后**转小写**（不告警，`"Offensive"` → `"offensive"`）。
  - 补齐与截断：`types.size() < count` → 末尾补 `"any"` 到 `count`（**不告警**）；`types.size() > count` → 截断到 `count` + **1 条告警**（`"<source>: types 有 N 项但 count=M，已截断"`）。
  - 返回的 `types` 用 `List.copyOf`，长度**恒等于** `count`。
- `parseGem` 规则（§5.3，逐条照做）：
  - `root` 为 null 或 `gem` 缺失 → 返回 **null**（= 不是宝石，**不告警**）；`gem` 存在但不是对象 → 告警 + null。
  - `type`：缺省 `"any"`；非字符串 → 告警 + `"any"`；空白串 → `"any"`（不告警）；结果 `trim` + **转小写**。
  - `tier`：缺省 **1**；非数字 → 告警 + 1；`< 1` → 归 **1** + 告警。
  - `exclusive_group`：缺省 `""`；非字符串 → 告警 + `""`；结果 `trim`（**保留原大小写**，它只是相等比较的键）。
  - `stats`：**必须**调 `com.redtale.project.items.AffixPools.parseStats(gemObj, source + ".gem", warnings)` —— **把 `gem` 那个对象当 `root` 传进去**（该方法读的是入参 root 的 `stats` 键，不是外层 root）。**不许自己写第二份 stats 解析**（同一属性两种写法会往同一个 modifier id 加两条，R11-b 的教训）。返回值包成不可变（`Collections.unmodifiableMap`，保序）。
  - `stats` 为空表是**合法**的（纯装饰宝石），不告警。
- 数字取值前先判 `isNumber()`，别 `getAsInt()` 直取（`1` / `1.0` / `1L` 三种形态都会出现）。任何类型不符 / `JsonNull` / 缺键 → 告警一行 + 默认值或 `EMPTY`/`null`，**绝不抛异常**（与 T-0001/T-0004/T-0006/T-0008/T-0010 同一口径）。
- 样例（放你自己的临时目录，**不要提交进 `src/main/resources`**）：
  ```json5
  { id: "demo_longsword", sockets: { count: 2, types: ["offensive", "any"] } }
  { id: "gem_ruby", base: "amulet", gem: { type: "offensive", tier: 1,
      exclusive_group: "ruby", stats: { physical_damage: 0.05, attack_damage: { base: 2, per_item_level: 0.1 } } } }
  ```
- 不要做：不实现镶嵌 / 取出 / 互斥判定、不碰 `ItemStack`、不给 `ContentData`/`ItemContent` 加字段、不加命令、不加 `SelfTest`（测试由 S7 写）、不改 `config/` 与 `src/main/resources/`、不改 `AffixPools.java`（`parseStats` / `normalizeKey` 已由 S7 升为 public，直接用）
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "public static Layout parseLayout" src/main/java/com/redtale/project/items/SocketSpec.java` = 1，`grep -c "public static Gem parseGem" ...` = 1
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "items/SocketSpec"` ≥ 3（主类 + `$Layout` + `$Gem`）
  > 解析结果对不对由 S7 用离线探针跑（缺段返 null/EMPTY 且零告警 / count 夹取 / types 补齐与截断 / 非法项换 `any` / `stats` 走 AffixPools 同一条归一 / 不可变）。
- 进度：
  - 2026-11-16 14:38 · 完成 · 新建 `src/main/java/com/redtale/project/items/SocketSpec.java`（1 类 **176 行**，含 `Layout`/`Gem` 两个 record + `Layout.EMPTY` + `MAX_COUNT=6`；卡外文件零改动，`RedtaleCore`/`RedtaleCommand`/`ItemFactory`/`ContentData`/`ItemContent`/`ItemBase`/`AffixPools` 未碰） · build 退出码 0（取锁 `gradle build --offline`，jar 内 `items/SocketSpec` = **3**（主类 + `$Layout` + `$Gem`，≥3 达标）） · 自测：①`grep -c "public static Layout parseLayout"` = 1、`parseGem` = 1；②离线探针 `build/probe/SockProbe.java` **36/36 PASS**（jar + gson + MC merged-patched + forge-universal + `server-test/libraries`，真类直调）：`root=null` / 缺 `sockets` → `EMPTY` **零告警**；`sockets:"x"` → `EMPTY` + 1 告警；§5.2 样例 → count2 `[offensive, any]` 零告警；`count:0` 带 types → `EMPTY` 且不碰 types；`sockets:{}` → `EMPTY` 零告警；`count:-3` → 0 + 1 告警；`count:9` → 夹 6 + 6 个 `any` + 1 告警；`count:4, types:["Offensive","",5,null]` → `[offensive, any, any, any]`（**孔序不错位**）+ 3 告警；`types` 5 项 count 3 → `[a,b,c]` + 逐字告警 `types 有 5 项但 count=3，已截断`；`types:"x"` → 全 `any` + 1 告警；`count:2` 只 1 个 type → 补 `any` **零告警**；`count:2.7` → 2（`getAsInt` 截断）；`count:"2"` → `EMPTY` + 1 告警；`types` 不可变（`add` 抛 `UnsupportedOperationException`）；`gem` 侧：`root=null` / 缺 `gem` → `null` **零告警**、`gem:"x"` → `null` + 1 告警、§5.3 样例逐字段对（`offensive`/1/`ruby`/stats 2 条、零告警）、`gem:{}` → `any`/1/`""`/空表零告警、`type:"Offensive "` → `offensive`、`type:""` → `any` 零告警、`type:5` → `any` + 1 告警、`tier` 0/-3/`"2"` 各归 1 + 1 告警、`exclusive_group:" Ruby "` → `Ruby`（**保留大小写**）、`:5` → `""` + 1 告警、未知属性 → 告警 + 跳过、`stats` 仅一条也能补全其余默认值、`stats` 不可变、`warnings=null` / `source=null` 不 NPE、`AffixPools.parseStats` 同入口键集全等 · **四处请 S7 知悉（均按卡面实现）**：①`count` 缺省不告警、显式非数字才告警（卡面「缺省 0」未要求告警）；②`types` 非数组的告警文案用 `types 不是数组，已忽略`，之后按「短了补 any」补到 count（卡面只说「告警 + 空表」，补齐是后续规则的天然结果）；③`count` 为小数（`2.7`）按 `getAsInt()` 截断成 2、不告警（卡面只说「非数字 → 告警」，小数算数字）；④`Gem.stats` 归一后自建属性键是**裸 snake**（`physical_damage`），只有原版才是 `minecraft:generic.attack_damage` —— 这是 `AttributeSpecs.resolve` 的既有口径，探针已证明与直接调 `AffixPools.parseStats` 键集**逐键相等**
  - 2026-11-16 15:2x · **S7 验收通过（3/3 + 独立探针 49/49）** · ①`gradle build --offline` exit 0（jar 267999 B）；②`grep -c "public static Layout parseLayout"` = **1**、`parseGem` = **1**；③`unzip -l` 内 `items/SocketSpec` = **3**（主类 + `$Layout` + `$Gem`，≥3 达标）。**S7 自写独立探针**（`build/probe/S7SockProbe.java`，不复用 S8 的 `SockProbe` 断言）**49/49 PASS**：`root=null` / `sockets` 缺失 → `Layout.EMPTY` **零告警**；`sockets:"x"` 与 `sockets:[]` → EMPTY + 1 告警；`sockets:null` → EMPTY（显式 null 按卡面「存在但不是对象」计 1 条告警，与 T-0010 `repair:null` 同口径，**不打回**）；§5.2 样例 count2 `[offensive, any]` 零告警；`count=0` 带 types → EMPTY 且**不碰 types**（零告警）；`count=-3` → EMPTY + 1 告警；`count=9` → 6 + 6×`any` + 1 告警；`count:"2"`（字符串）→ EMPTY + 1 告警；只给 `count` → 全 `any` **零告警**；`count:4, types:["Offensive","",5,null]` → `[offensive, any, any, any]`（**孔序不错位**）+ 3 告警（大写不告警）；`types` 5 项 count 3 → `[a,b,c]` + 1 条带 `5`/`3` 的告警；**count 0..6 全档 `types.size()==count`**；`types` 不可变；`gem` 侧：`root=null` / 缺 `gem` → null **零告警**、`gem:"x"`/`gem:null` → null + 1 告警、§5.3 样例逐字段对（`offensive`/1/`ruby`/stats 2 条零告警，曲线形态 `{base:2,per_item_level:0.1}` 进 `StatValue` 且键归一为 `minecraft:generic.attack_damage`）、`gem:{}` 全缺省零告警、`type:" Offensive "` → `offensive`、`type:""` → `any` 零告警、`tier:0` → 1 + 1 告警、`exclusive_group:" Ruby "` → `Ruby`（**保大小写**）、非字符串 → `""` + 1 告警、`stats` 键集与告警条数均与直调 `AffixPools.parseStats` **全等**、`stats` 不可变、`source=null` 不 NPE。**该文件已归 S7**：本轮接进 `ItemContent.sockets()` / `ItemContent.gem()` + `ItemFactory` 按布局填空孔 + `Socketer` 镶嵌结算


### T-0014 · [VERIFIED] `SetSpec` 套装定义解析器（M3 第五步，纯解析 + 一个纯函数）

- 派单：S7 · 2026-11-16 13:47
- 目标：把 `config/redtale_project/sets/*.json5`（套装定义）解析成不可变对象，并给一个**纯函数**回答「穿了几件时哪几档加成生效」。schema 见 `docs/ITEM-MODEL.md` **§5.4**，照它写。
  **只解析 + 一个纯函数**：不算件数、不下发属性 modifier、不读盘（入参是已解析好的 `ConfigFile` 列表）、不碰 `ItemStack`、不加命令。
- 独占文件：
  - `src/main/java/com/redtale/project/items/SetSpec.java`（新建，唯一文件）
  - **不许改任何已有文件**（不接 `RedtaleCore`、不碰 `RedtaleCommand`/`ItemFactory`/`ContentData`/`ItemContent`/`ItemBase`/`AffixPools`）
- 接口（**一字不改**）：
  ```java
  package com.redtale.project.items;

  public final class SetSpec {
      public record Bonus(int count, String name,
                          java.util.Map<String, com.redtale.project.core.math.StatValue> stats) {}
      public record Definition(String id, String name, java.util.List<String> pieces,
                               java.util.List<Bonus> bonuses) {}

      public static java.util.Map<String, Definition> parseAll(java.util.List<ConfigFile> configs,
                                                               java.util.List<String> warnings);
      public static java.util.List<Bonus> activeBonuses(Definition definition, int wornPieces);
  }
  ```
  `ConfigFile` = `com.redtale.project.core.config.ConfigFile`（`path()` 相对 `config/redtale_project`，`root()` 是 `com.google.gson.JsonObject`）。
- `parseAll` 规则（逐条照做）：
  - **筛选**：只吃 `path().startsWith("sets/")` 且以 `.json5` 结尾的文件，其余跳过（不告警）。返回 `LinkedHashMap`（保文件顺序 + 文件内顺序）。
  - `id` 取 `root.id`，缺省 = 路径去掉 `sets/` 与 `.json5` 后缀（子目录的 `/` 保留）。`id` = `trim()` 后的字符串；**空串 → 告警 + 跳过该文件**（套装 id 是物品 `set_id` 的匹配键，空串会匹配到所有没写 `set_id` 的物品）。
  - **id 重复（跨文件）→ 告警 + 保留先出现的**。
  - `name` 缺省 = `id`；非字符串 → 告警 + 回落 `id`。
  - `pieces`：字符串数组，缺省空 List；元素非字符串 / `trim` 后空 → 告警 + **跳过该元素**；合法元素 `trim` 后入表；**重复元素去重（保留首次出现）+ 1 条告警**（§5.4：重复的两件只算一件）。非数组 → 告警 + 空表。
  - `bonuses`：数组，缺省空 List；非数组 → 告警 + 空表。每个元素必须是对象，否则告警 + 跳过该项。
    - `count`：缺省 0；非数字 → 告警 + 跳过该档；`< 1` → 告警 + **跳过该档**（档位不存在「0 件生效」）。
    - `name`：缺省 `""`；非字符串 → 告警 + `""`。
    - `stats`：**必须**调 `com.redtale.project.items.AffixPools.parseStats(bonusObj, source + ".bonus[" + i + "]", warnings)` —— 把**这一档的对象**当 `root` 传进去。**不许自己写第二份 stats 解析**（R11-b：同一属性两种写法会往同一个 modifier id 加两条）。
    - `stats` 为空表**合法**（纯展示档），不告警。
  - **排序**：返回前 `bonuses` 按 `count` **升序稳定排序**（同 count 保持文件内原序）。§5.4「所有 `count <= 当前件数` 的档全部生效」依赖这个顺序。
  - 返回的 `pieces` / `bonuses` 用 `List.copyOf`；`stats` 用 `Collections.unmodifiableMap`（保序）。
  - **失败策略**：任何类型不符 / `JsonNull` / 缺键 → 告警一行 + 默认值或跳过，**绝不抛异常**（与 T-0001/T-0004/T-0006/T-0008/T-0010 同一口径）。数字取值前先判 `isNumber()`。
- `activeBonuses(definition, wornPieces)` 规则（纯函数，无 MC 依赖）：
  - `definition == null` 或 `wornPieces <= 0` → 空 List（不告警）。
  - 返回 `bonuses` 里**所有** `count <= wornPieces` 的档（**不是只取最高档**，§5.4），保持 `Definition` 里的升序；返回 `List.copyOf`。
  - 不修改入参、不读任何全局状态。
- 样例（放你自己的临时目录，**不要提交进 `src/main/resources`**）：
  ```json5
  { id: "emberforged", name: "炽锻",
    pieces: ["redtale_project:demo_longsword", "redtale_project:demo_chestplate", "redtale_project:demo_robe"],
    bonuses: [ { count: 2, stats: { physical_damage: 0.1 } },
               { count: 3, stats: { attack_damage: 5 }, name: "炽锻·全" } ] }
  ```
- 不要做：不做穿戴统计 / 件数判定 / 属性下发 / modifier id 生成、不碰 `ContentData.set_id`、不加 `/redtale set`、不加 `SelfTest`（测试由 S7 写）、不改 `config/` 与 `src/main/resources/`、不改 `AffixPools.java`
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "public static Map<String, Definition> parseAll" src/main/java/com/redtale/project/items/SetSpec.java` = 1，`grep -c "public static List<Bonus> activeBonuses" ...` = 1
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "items/SetSpec"` ≥ 3（主类 + `$Bonus` + `$Definition`）
  > 解析结果对不对由 S7 用离线探针跑（缺 `sets/` 前缀跳过 / id 空串跳过 / pieces 去重 / count<1 跳过 / 档位升序 / `activeBonuses` 全档生效 / 不可变）。
- 进度：
  - 2026-11-16 15:34 · 完成 · 新建 `src/main/java/com/redtale/project/items/SetSpec.java`（184 行，`Bonus`/`Definition` + `parseAll`/`activeBonuses`）· 卡外零改动 · build 退出码 0（jar 254478→261xxx B）· 自测：`grep -c parseAll`=1、`grep -c activeBonuses`=1、jar 内 `items/SetSpec`=3（主类 + `$Bonus` + `$Definition`）；离线探针 `build/probe/SetProbe.java` 36/36
  - 两处卡面未规定的口径，实现取值如下，请 S7 确认：①`root.id` 存在但**不是字符串** → 告警 1 条 + 回落「路径推导 id」（卡面只写了 id 空串的处理）；②`pieces` 重复项**合并成 1 条**告警（列出重复值），不按每个重复项各报一条——与卡面「+ 1 条告警」字面一致。
  - 告警文案里档位前缀用 `path + ".bonus[i]"`，故形如 `sets/x.json5.bonus[1]: …`（卡面给的拼接式，`.json5` 未剥）。
  - 待 S7 验收：功能验（真配置 / 件数 / 属性下发归 M3 后续卡，本卡不含）。
  - 2026-11-16 16:2x · **S7 验收通过 → VERIFIED** · 三条验收全过：`gradle build --offline` exit 0（jar 309350 B）；`grep -c "public static Map<String, Definition> parseAll"` = 1、`grep -c "public static List<Bonus> activeBonuses"` = 1；jar 内 `items/SetSpec` = **3**（主类 + `$Bonus` + `$Definition`，卡面要求 ≥3）。**S7 独立探针 `build/probe/S7SetProbe.java` 36/36 PASS**（不复用 S8 的 `SetProbe`）：`sets/` 前缀筛（`items/` / `.bak` / `README.md` 全静默跳过、子目录 id 保斜杠）/ 空 id 跳过且 1 条告警 / 非字符串 id 与 name 回落 / 跨文件重复保留先出现 + 1 条告警 / pieces 去重+trim+空项跳过（`[a:1, b:2, a:1, "  ", c:3]` → `[a:1,b:2,c:3]` + 2 条告警）/ `count` 缺·非数字·`<1` 全跳过、`2.7` 取 2、同 count **稳定升序** / **`stats` 键集与值与 `AffixPools.parseStats` 逐条相同**（裸名归一后不重复加）/ 空 `stats` 档合法 / `activeBonuses` 返回**全部** `count <= 件数` 的档且升序 / `pieces`·`bonuses`·`stats` 三处不可变 / `configs=null`·`warnings=null` 不抛 / 两次解析顺序逐字一致。S8 提的两处口径（非字符串 `id` 回落路径、`pieces` 重复合并成 1 条告警）**予以确认**，与卡面字面一致。

### T-0015 · [VERIFIED] `/redtale validate` 引用完整性检查（只读，M3 配套）

- 派单：S7 · 2026-11-16 15:35
- 目标：把「配置里互相引用、但引用目标不存在」这类**静默失效**扫出来。它们现在不会报错，只是不生效：
  武器 `weapon_attributes` 指向一份没写的定义文件 → BetterCombat 静静回落到默认挥砍；
  词条池引用了删掉的词条 → 那个槽位永远摇不出来。**只读**：不改任何文件、不改任何内存状态。
- 独占文件：
  - `src/main/java/com/redtale/project/core/command/ValidateCommand.java`（新建，唯一新建类）
  - `src/main/java/com/redtale/project/core/command/RedtaleCommand.java`（**只插入 1 行**：在 `.then(Commands.literal("content").then(Commands.literal("check").executes(ContentCheckCommand::check)))` 那行**之后**插入 `.then(Commands.literal("validate").executes(ValidateCommand::validate))`。不改动任何现有行；同包**不要写 import**）
- 接口（一字不改）：
  ```java
  package com.redtale.project.core.command;

  public final class ValidateCommand {
      /** 返回「引用问题」条数（不是检查项总数）。 */
      public static int validate(com.mojang.brigadier.context.CommandContext<net.minecraft.commands.CommandSourceStack> ctx);
  }
  ```
- 数据来源（照抄，别自己找路）：
  - 内容：`com.redtale.project.core.RedtaleCore.get().contentItems().all()` → `Collection<ItemContent>`
  - 词条定义：`com.redtale.project.core.RedtaleCore.get().affixDefs()` → `Map<String, AffixPools.Def>`
  - 词条池：`com.redtale.project.core.RedtaleCore.get().affixPools()` → `Map<String, AffixPools.Pool>`
  - 配置列表：`com.redtale.project.core.RedtaleCore.get().config().loadAll()` → `List<ConfigFile>`（**会抛 `IOException`**，必须 try/catch → `sendFailure` 一行 + 返回 0；`ConfigFile.path()` 相对 `config/redtale_project`）
  - 基底表：`com.redtale.project.items.ItemBase.byId(String)`（返回 `null` = 不存在）
- 四条检查（逐条照做，别加第五条）：
  1. **`weapon_attributes` 缺定义**：对每件内容，`weaponAttributes()` 非空时解析成 `ResourceLocation`（`ResourceLocation.tryParse`，返回 `null` → 记一条问题「id 非法」）。命名空间是 `redtale_project` → 期望存在 `ConfigFile`，其 `path()` 等于 `"weapon_attributes/" + path + ".json5"`，不存在 → 问题；**其它命名空间 → 不报问题**，只把外部引用计数 `+1`（别人 jar 里的内置项我们无法校验）。
  2. **词条池引用未定义的词条**：每个 `Pool.entries()` 里的 `Entry.affixId()` 不在 `affixDefs` 里 → 一条问题。同一池里同一个 id 只报一次。
  3. **`applies_to` 基底不存在**：每个 `Pool.appliesTo()` 元素解析成 `ResourceLocation`（解析失败 → 一条问题）；命名空间不是 `redtale_project` → 跳过（不报）；是 `redtale_project` 但 `ItemBase.byId(path)` 返回 `null` → 一条问题。
  4. **池永远摇不出东西**：`Pool.entries()` 为空，或 `Entry.weight()` 合计 `<= 0` → 一条问题（这个池等于没配）。
- 输出（**文案写死便于 grep**；全部走 `ctx.getSource().sendSuccess(() -> Component.literal(...), false)`）：
  - 第 1 行：`校验：C 件内容 / P 个词条池 / D 条词条定义 · 问题 K 条（外部 weapon_attributes 引用 X 条未校验）`
  - 问题行（`K > 0` 时）：`  <contentId>: weapon_attributes <ref> 缺定义文件 weapon_attributes/<path>.json5` / `  <contentId>: weapon_attributes 的 id 非法（<原字符串>）` / `  <poolId>: 引用了未定义的词条 <affixId>` / `  <poolId>: applies_to 的 <原字符串> 不是 14 基底之一` / `  <poolId>: applies_to 的 id 非法（<原字符串>）` / `  <poolId>: 权重合计 <= 0，永远不会被摇到`
  - `K == 0` 时：`  （没有引用问题）`
  - **顺序**：内容类问题按 `contentId` 字典序，池类问题按 `affixPools()` 的迭代序、池内按 `entries` 顺序（`LinkedHashMap` 已保序）。不排序也行，但同一份配置两次运行**输出必须逐字相同**。
  - 返回 `K`。
- `不要做`：不改任何配置文件、不写盘、不打 `LOG`、不修 `rev`、不校验 `stats` 键（`ItemContent.parse` 已经在做）、不校验 `sockets` / `sets`（M3 后续）、不加参数、不碰 `AffixPools` / `SocketSpec` / `ItemContent` / `ContentData` / `ItemUpgrader`、不加 `SelfTest`（测试由 S7 写）。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "ValidateCommand::validate" src/main/java/com/redtale/project/core/command/RedtaleCommand.java` = 1
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "core/command/ValidateCommand"` = 1
  > 功能验由 S7 跑：测试服造三份坏配置（引用不存在的 `weapon_attributes` / 池里引用不存在的词条 / `applies_to` 指向 `redtale_project:wand`），看问题条数与文案；删掉坏配置后应回到 `（没有引用问题）`。
- 进度：
  - 2026-11-16 16:40 · 完成 · 新建 `src/main/java/com/redtale/project/core/command/ValidateCommand.java`（117 行，单类无内部类 / 无 record）；`RedtaleCommand` 在 content/check 那行之后 **+1 行**挂载（同包无 import）· 卡外零改动 · build 退出码 0（jar 313235 B）· 自测：`grep -c "ValidateCommand::validate"`=1、jar 内 `core/command/ValidateCommand`=1、离线探针 `build/probe/ValidateProbe.java` 16/16（类 public+final、非合成方法仅 1 个、`int validate(CommandContext<CommandSourceStack>)` 签名逐字相符、6 条输出文案在常量池）
  - 两处口径备注（不算改契约，请 S7 知悉）：①`applies_to` 写裸名（如 `sword`）会被 `ResourceLocation.tryParse` 补成 `minecraft:sword`，按卡面「非 `redtale_project` 命名空间跳过」不报 → 这类**漏命名空间**的笔误查不出；②只 catch `loadAll` 声明的 `IOException`，其余运行时异常照常上抛（不吞）。
  - 2026-11-16 17:3x · **S7 验收通过 → VERIFIED** · 三条验收全过：`gradle build --offline` exit 0（jar 313235 B）；`grep -c "ValidateCommand::validate"` = 1；jar 内 `core/command/ValidateCommand` = 1（无内部类）。**功能四跑（测试服）**：造三份坏配置（`weapon_attributes: redtale_project:missing_reach` / 池引 `ghost_affix` + `applies_to: redtale_project:wand` / 空池）→ `校验：11 件内容 / 3 个词条池 / 3 条词条定义 · 问题 4 条（外部 weapon_attributes 引用 1 条未校验）`，四条问题行与卡面文案**逐字相符**；连跑两次输出 diff 为空；删掉三份坏配置 + `/redtale reload` → `10 件内容 / 1 个池 · 问题 0 条` + `  （没有引用问题）`。S8 提的两条口径**予以确认**：①裸名 `applies_to`（如 `sword`）被补成 `minecraft:sword` 故不报 —— 已实测复现（`applies_to: ["sword"]` → 0 问题），记 `PLAN.md` §13.24 R21-e，R22 补「裸名疑似笔误」提示；②只 catch `IOException`、其余上抛 —— 与「只读不吞异常」一致，保留。

### T-0016 · [VERIFIED] `/redtale set check` —— 套装引用与可达性校验（只读，M3 配套）

- 派单：S7 · 2026-11-16 16:30
- 目标：把「套装配了但永远不生效」的四类静默坑扫出来。它们都不报错，只是不生效：
  `pieces` 写了不存在的内容 / piece 的 `set_id` 指向别的套装 / 档位要求件数超过 6 个格子能同时穿上的数量 /
  同一个 `count` 写了两次（modifier id 相同 → 后者覆盖前者）。**只读**：不改文件、不改内存、不下发属性。
- 独占文件：
  - `src/main/java/com/redtale/project/core/command/SetCheckCommand.java`（新建，唯一新建类）
  - `src/main/java/com/redtale/project/core/command/RedtaleCommand.java`（**只插入 1 行**：在 `.then(SetCommand.node())` 那一行**之后**插入
    `.then(SetCheckCommand.node())`。不改任何现有行；同包**不要写 import**）
- 接口（**一字不改**）：
  ```java
  package com.redtale.project.core.command;

  public final class SetCheckCommand {
      /** 命令节点：/redtale set check */
      public static com.mojang.brigadier.builder.LiteralArgumentBuilder<net.minecraft.commands.CommandSourceStack> node();

      /** 返回「问题」条数（不是检查项总数）。 */
      public static int check(com.mojang.brigadier.context.CommandContext<net.minecraft.commands.CommandSourceStack> ctx);
  }
  ```
- 数据来源（照抄，别自己找路）：
  - 套装定义：`com.redtale.project.core.RedtaleCore.get().sets()` → `Map<String, SetSpec.Definition>`
  - 内容：`com.redtale.project.core.RedtaleCore.get().contentItems().get(String contentId)` → `ItemContent`，`null` = 不存在
  - 能同时穿几个槽：`com.redtale.project.items.SetBonus.slotOf(ItemBase base)` → `EquipmentSlot`（**已 public**，别自己写映射）
- 四条检查（逐条照做，别加第五条）：
  1. **piece 不存在**：`def.pieces()` 里某个 id，`contentItems().get(id) == null` → 一条问题。
  2. **piece 的 `set_id` 不匹配**：内容存在但 `content.setId()` 不等于 `def.id()`（含空串）→ 一条问题。
  3. **档位不可达**：先算上限 `cap` = 该套装里「能同时穿上」的 piece 数 —— 对每个**存在且 set_id 匹配**的 piece 取
     `SetBonus.slotOf(content.base())`，按 `EquipmentSlot` **去重**后的数量（同槽基底互斥，两件胸甲只能穿一件）。
     `bonus.count() > cap` → 一条问题（`cap == 0` 时所有档都不可达，只报一条「pieces 一件都穿不上」即可，不要逐档刷屏）。
  4. **同档重复**：同一套装里出现两个相同 `count` 的档 → 一条问题（modifier id `set/<setId>/<count>` 相同，
     后加的会覆盖先加的，数值静默丢失）。
- 输出（**文案写死便于 grep**；全部 `ctx.getSource().sendSuccess(() -> Component.literal(...), false)`）：
  - 第 1 行：`套装校验：S 个定义 · P 件 pieces · 问题 K 条`
  - 问题行：`  <setId>: piece <contentId> 不存在` /
    `  <setId>: piece <contentId> 的 set_id 是 <实际值或「空」>（应为 <setId>）` /
    `  <setId>: <count> 件档要求 <count> 件，但 pieces 最多能同时穿 <cap> 件（同槽基底互斥）` /
    `  <setId>: pieces 一件都穿不上（可达上限 0）` /
    `  <setId>: <count> 件档重复（同一 modifier id 会互相覆盖）`
  - `K == 0` 时：`  （套装引用完整）`
  - **顺序**：按 `sets()` 的迭代序（`LinkedHashMap` 已保序），同一套装内按 pieces 顺序、再按档位升序。
    同一份配置两次运行输出**必须逐字相同**。
  - 返回 `K`。
- `不要做`：不改任何配置文件、不写盘、不打 `LOG`、不下发/移除任何 modifier、不调用 `SetBonus.apply`、
  不校验 `items`、不改 `SetSpec` / `SetBonus` / `SetCommand` / `ItemContent` / `ContentData`、
  不加参数、不加 `SelfTest`（测试由 S7 写）。
- 注：`SetCommand` 里已有 `danglingSets()` 与 `info` 两条相似逻辑，**不要复用也不要改它**（那是卡外文件）；
  本卡是新类，重复几十行没关系，S7 之后自行合流。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "SetCheckCommand::node" src/main/java/com/redtale/project/core/command/RedtaleCommand.java` = 1
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "core/command/SetCheckCommand"` = 1（若有内部类会 >1，届时如实报数）
  > 功能验由 S7 跑：测试服造三个坏定义（piece 不存在 / piece 的 set_id 写错 / 档位 3 但 pieces 只能穿 2 件），
  > 看问题条数与文案；删掉坏定义后应回到 `（套装引用完整）`。
- 进度：
  - 2026-11-16 17:42 · 完成 · 新建 `core/command/SetCheckCommand.java`（112 行，单类无内部类）；`RedtaleCommand` 在 `.then(SetCommand.node())` 后追加 2 行（注释 + `.then(SetCheckCommand.node())`），现有行零改动 · build 退出码 0（jar 323428 B）· 验收：jar 内 `core/command/SetCheckCommand` = 1；`grep -c "SetCheckCommand.node()"` = 1，卡面写的 `SetCheckCommand::node` 实际 = 0（静态调用用 `.` 不用 `::`，`::` 只在新建类内 `executes(SetCheckCommand::check)`）；结构探针 `build/probe/SetCheckProbe.java` 11/11（`set` 顶层仍 1 个节点、`check` 有 command、`list/sync/info/probe` 与 `set` 自身均未被子节点合并覆盖）
  - 口径备注（请 S7 确认，未停手）：①`cap == 0` 一律只报「一件都穿不上」一条，即使该套没写档位；②同档重复按 **每个重复 count 一条**（三个 3 件档也只报 1 条）；③piece 同时「不存在」+「set_id 错」只报「不存在」一条。功能验（三个坏定义 → 条数与文案）待 S7 上测试服。
  - 2026-11-16 18:52 · **S7 验收通过（3/3 + 功能五跑）** · ①`gradle build --offline` exit 0（jar 323428 B）；②`grep -c "SetCheckCommand" RedtaleCommand.java` = **1**（卡面写 `::node` 得 0，S8 已如实报，接受）；③jar 内 `core/command/SetCheckCommand.class` = **1**（无内部类）。功能验（测试服 `Done` 后 RCON）：造 4 组坏定义 → `套装校验：5 个定义 · 9 件 pieces · 问题 4 条`，四条文案逐字对上（piece 不存在 / set_id 是 t_bad1（应为 t_bad2）/ 2 件档 > cap 1 / 1 件档重复），**一个检查各命中一条、无串味**；连跑两次 `diff` 为空（顺序稳定）；移走坏定义 + reload → `1 个定义 · 2 件 pieces · 问题 0 条` + `（套装引用完整）`。S8 问的三条口径**全部按卡面成立**：①`cap == 0` 只报一条（`t_bad5` 两个 ghost piece + 两档 → 只有 2 条「不存在」+ 1 条「一件都穿不上」，零逐档刷屏）；②同档重复按每个重复 count 一条；③piece 同时不存在 + set_id 错只报「不存在」。文件归 S7

### T-0017 · [VERIFIED] `tools/gen_enchant_lang.py` —— 附魔 lang 键生成器（M4 的 V3 前置）

- 派单：S7 · 2026-11-16 17:40
- 目标：附魔生成器只写 `translate` 键（`enchantment.redtale_project.<path 点号化>`），lang 里没有对应值 →
  `/enchant` 与 tooltip 直接显示裸键。本卡把 `enchantments/*.json5` 的 `description` / `description_en`
  合并写进两份 lang。**合并**语义，不是覆写：`attribute.*` 66 条、`item.*` 14 条、死亡消息等一条都不能丢。
- 独占文件：
  - `tools/gen_enchant_lang.py`（新建，唯一新建文件）
  - `src/main/resources/assets/redtale_project/lang/zh_cn.json`、`en_us.json`（**只由脚本写入**，你别手改）
- 输入（照抄，别自己找路）：
  - `src/main/resources/redtale/defaults/enchantments/*.json5`（当前 2 份：`super_sharpness` / `soul_reap`）
  - 取 `id`（缺省补 `redtale_project:` 前缀）、`description`（中文名）、`description_en`（英文名，缺省回落 `description`）
  - lang 键 = `enchantment.<命名空间>.<path 里的 / 换成 .>`（与 `EnchantmentGenerator` 的写法必须一致：
    见 `src/main/java/com/redtale/project/enchants/EnchantmentGenerator.java` 里 `"enchantment." + id.getNamespace() + "." + id.getPath().replace('/', '.')`）
- 规则：
  1. **只拥有** 前缀 `enchantment.redtale_project.` 的键：先读出两份 lang 的现有内容 → 删掉这个前缀下的旧键 → 写入本次扫到的键 → 其余键**原样保留**（顺序：其余键保持原顺序在前，新键按文件名升序追加）
  2. 缩进 2 空格、UTF-8 **无 BOM**、末尾换行；`json.dump(ensure_ascii=False, indent=2, sort_keys=False)`
  3. `description` 缺失 → 打一行 `WARN: <file> 缺 description，用 id 兜底`，值用 path
  4. 文件读不了 / JSON5 括号不配对 → 打 WARN 跳过该文件，不崩
  5. **幂等**：连跑两次，两份文件字节级一致
- 不要做：不改 `EnchantmentGenerator`、不动 `gen_attr_lang.py` / `gen_item_lang.py`、不写 `enchantment.minecraft.*`（原版附魔的名字归原版）、
  不新增依赖（只用标准库；JSON5 的注释/尾逗号用现有 `tools/gen_item_lang.py` 里的同款轻量清洗思路，别引 pip 包）、不碰 `src/main/java`。
- 验收：
  1. `python tools/gen_enchant_lang.py` 退出码 0
  2. `python -c "import json;z=json.load(open('src/main/resources/assets/redtale_project/lang/zh_cn.json',encoding='utf-8'));e=json.load(open('src/main/resources/assets/redtale_project/lang/en_us.json',encoding='utf-8'));print(z['enchantment.redtale_project.super_sharpness'],z['enchantment.redtale_project.soul_reap'],sum(k.startswith('attribute.') for k in z),sum(k.startswith('item.') for k in z),e['enchantment.redtale_project.soul_reap'])"`
     期望输出：`超级锋利 摄魂 66 14 Soul Reap`
  3. 连跑两次 `md5sum` 两份文件不变（把两次的 md5 写进进度行）
- 进度：
  - 2026-11-16 19:04 · 完成 · 新建 `tools/gen_enchant_lang.py`（211 行）；`lang/zh_cn.json` / `en_us.json` 由脚本写入（各 83 键，enchantment 2 条追加在末尾） · build 退出码 0（jar 325316 B） · 验收：①`python tools/gen_enchant_lang.py` exit 0；②验收命令输出 `超级锋利 摄魂 66 14 Soul Reap`；③连跑两次 md5 不变（zh `8ed45104…` / en `07a7f16c…`）；④非 enchant 键逐条全等（attribute 66 / item 14 / death 1 一条没丢，顺序也未变）；⑤边界探针 `build/probe/EnchLangProbe.py` 17/17（注释/裸键/单引号/尾逗号/字符串内 `//`、转义引号、缺 description 兜底、缺 id、括号与引号不配对、别家命名空间、合并保序、合并幂等）
  - 口径备注（请 S7 确认，未停手）：①非 `redtale_project:` 命名空间的定义 → `WARN ... 不在 enchantment.redtale_project. 名下，已跳过`（若写进去，下一轮按前缀删除时删不掉，幂等直接破）；②新键追加在文件末尾会打破 lang 现有字母序，而 `gen_item_lang.py` 是整体 `sorted()` → 两个脚本交替跑时 enchantment 键会在「末尾 / 字母序中间」之间跳（值不丢，但跨脚本 md5 不稳），要不要统一排序请 S7 定；③`gen_attr_lang.py` 若整体覆写会抹掉这 2 条，顺序仍是「先 attr 后 item 后 enchant」。

  - 2026-11-16 20:03 · **S7 验收通过（3/3）** · ①`python tools/gen_enchant_lang.py` exit 0（输出 `解析到 2 份附魔定义：soul_reap, super_sharpness`，83 键，enchantment 键 2 → 2）；②验收命令输出逐字为 `超级锋利 摄魂 66 14 Soul Reap`（`attribute.*` 66 / `item.*` 14 一条没丢）；③连跑两次 md5 逐字相同（zh `8ed45104…` / en `07a7f16c…`），幂等成立。S8 提的口径②（新键追加末尾 vs `gen_item_lang` 的 sorted）**不改**：两个脚本归属不同前缀，键集合不相交，交替跑不会丢值，顺序差异只在 `git diff` 噪点层面；等 M4 附魔数量上两位数再统一排序。文件归 S7

### T-0018 · [VERIFIED] `/redtale validate` 补第 5 条（套装引用）+ 裸名提示（R21-e）

- 派单：S7 · 2026-11-16 18:58
- 目标：`validate` 现在只查 weapon_attributes / 词条池 / applies_to / 权重四类，**套装完全没有校验**。
  补两条，都只读：
  1. **第 5 条检查——套装引用**：`core.sets()` 里每个 `SetSpec.Definition`，
     (a) `def.pieces()` 里的 id 必须能在 `core.contentItems().get(id)` 找到，找不到 → 一条问题；
     (b) 反方向：`core.contentItems().all()` 里 `setId()` 非空、但 `core.sets()` 里没有这个 id → 一条问题
     （这条不报的话，写错一个字母的 `set_id` 永远静默不生效，`emberforged` 之外没有任何东西会提醒）。
     按 (a) 全部报完再报 (b)，各自内部按「套 id 字典序 / 内容 id 字典序（`all()` 已按 id 排）」。
  2. **裸名提示（R21-e）**：`applies_to` 里的字符串凡**不含 `:`**，既要保留现有判定，再追加一条提示：
     `  <poolId>: applies_to 的 <raw> 没写命名空间（会被当成 minecraft:<raw>）`。
     **只是提示、也计入问题条数**（现状是 0 条蒙过去，看不到等于没提示）。
- 独占文件：
  - `src/main/java/com/redtale/project/core/command/ValidateCommand.java`（**唯一**可改文件；只允许追加代码 + 改下面点名的两处字面量）
- 接口（一字不改）：
  - 类名 / `validate(CommandContext<CommandSourceStack>)` 签名**不变**，`RedtaleCommand` **一行都不要动**
  - 数据来源照抄：套装 `RedtaleCore.get().sets()`（`Map<String, SetSpec.Definition>`）、
    内容 `RedtaleCore.get().contentItems().get(String)` / `.all()`；`SetSpec.Definition.id()/pieces()`
- 输出（文案写死便于 grep；全部 `src.sendSuccess(() -> Component.literal(...), false)`）：
  - 首行现在是 `校验：<N> 件内容 / <M> 个词条池 / <K> 条词条定义 · 问题 <P> 条（外部 weapon_attributes 引用 <E> 条未校验）`。
    改成在 `条词条定义` 之后、` · 问题` 之前**插入** `" / " + sets.size() + " 个套装"`：
    即 `校验：<N> 件内容 / <M> 个词条池 / <K> 条词条定义 / <S> 个套装 · 问题 <P> 条（外部 weapon_attributes 引用 <E> 条未校验）`
    —— 开头 `校验：`、结尾括号里的字面量**一个字都不要改**
  - 新问题行：`  <setId>: piece <contentId> 不存在`
  - 新提示行：`  <内容id>: set_id <实际值> 没有对应套装定义（写错一个字母就静默不生效）`
  - 新提示行：`  <poolId>: applies_to 的 <raw> 没写命名空间（会被当成 minecraft:<raw>）`
  - `P == 0` 时仍是 `  （没有引用问题）`，**不要**新增第二种「全清」文案
- 不要做：不写盘、不打 `LOG`、不改 `SetCheckCommand` / `SetCommand` / `SetBonus` / `SetSpec` / `ItemContent`、
  不调用 `SetBonus.apply`、不加参数、不加 `SelfTest`（测试 S7 写）、不改 `RedtaleCommand`
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "set_id" src/main/java/com/redtale/project/core/command/ValidateCommand.java` >= 1（两条套装问题各一处字面量）
     —— 另报 `grep -c "个套装" ...` 的实际数字（应为 1）
  3. 自测（不改测试服）：把 `src/main/resources/redtale/defaults/sets/emberforged.json5` 复制一份到临时目录当输入，
     人为改坏一个 piece id 跑解析 → 用自己的逻辑确认会产出 1 条 `不存在`；**不要**把这套逻辑写进 `build.gradle`
- 进度：
- 2026-11-16 20:10 · 完成 · `core/command/ValidateCommand.java`（117→142 行，唯一改动文件；`RedtaleCommand` 未碰） · 新增：第 5 条套装双向引用（(a) 定义 piece 缺失 / (b) 物品 set_id 悬空，套 id 字典序、(b) 按内容 id 序）+ `applies_to` 裸名提示（R21-e，计入问题数）；首行 `条词条定义` 后插入 ` / <S> 个套装` · build 退出码 0（jar 330921 B） · 自测 `build/probe/Validate2Probe.java` 21/21：真实默认配置 registry=7 / sets=1 / 四类旧问题 0；把 `sets/emberforged.json5` 复制到临时目录改坏 `demo_longsword`→`demo_longsword_typo` 后经 `Json5`+`SetSpec.parseAll` 重解析，恰好产出 1 条 `  emberforged: piece demo_longsword_typo 不存在`；`set_id` 反向与裸名提示各 1 条逐字比对通过；class 常量池 8 条文案断言全过
- 两处口径（请 S7 顺手定，未自行改文案）：①裸名提示末段 `minecraft:<raw>` 按**实际值**渲染（`minecraft:stone`），非字面 `<raw>`；②第 5 条 (a) 段内部按 `pieces()` **声明序**报（卡面只规定套 id 字典序）；③问题行顺序 = 旧四类 → 池循环内裸名提示 → 套装 (a) → 套装 (b)（追加式，未重排旧行）

- 2026-11-16 21:20 · **S7 验收通过（3/3 + 测试服功能四跑）** · ①`gradle build --offline` exit 0（jar 330921 B）；②`grep -c "set_id" ValidateCommand.java` = **2**（>=1）、`grep -c "个套装"` = **1**（与卡面一致）；③测试服功能四跑：基线 `10 件内容 / 1 个词条池 / 3 条词条定义 / 1 个套装 · 问题 0 条` + `（没有引用问题）`（首行 `/ <S> 个套装` 位置正确）→ 造三处坏配置（`sets/emberforged.json5` 的 piece 改成 `demo_longsword_typo`、新建 `items/probe_badset.json5` 带 `set_id: "ghostset"`、词条池 `applies_to` 去掉命名空间留 `"axe"`）→ `/redtale reload` 后 `问题 3 条`，三行文案逐字对上：`  sword_common: applies_to 的 axe 没写命名空间（会被当成 minecraft:axe）` / `  emberforged: piece demo_longsword_typo 不存在` / `  probe_badset: set_id ghostset 没有对应套装定义（写错一个字母就静默不生效）` → 还原三处后回 `问题 0 条`。S8 提的三处口径全部**认账不改**：①裸名提示末段按实际值渲染（`minecraft:axe`）而非字面 `<raw>` —— 卡面的 `<raw>` 本就是占位符；②(a) 段按 `pieces()` 声明序报（卡面只规定套 id 字典序）；③问题行顺序 = 旧四类 → 裸名提示 → 套装 (a) → 套装 (b)（追加式，旧行未重排）。`RedtaleCommand` 确未改动（`git` 无仓，按 `grep -c` 与首行文案核对）。文件归 S7
### T-0019 · [VERIFIED] `/redtale enchant list` —— 已生成附魔只读清单（M4 运营可见性）

- 派单：S7 · 2026-11-16 20:12
- 目标：M4 的 L0 产物（`world/datapacks/redtale_project/data/<ns>/enchantment/**/*.json`）现在只能靠文件管理器看。
  给一条只读命令，把**已落盘**的每份附魔列出来：id / max_level / supported_items / 触发组件名。
  与 `/redtale content list`（读配置）不同，这里读**生成结果**——能看出「配置改了但数据包没重新生成」。
- 独占文件：
  - `src/main/java/com/redtale/project/core/command/EnchantListCommand.java`（新建，唯一新建文件）
  - `src/main/java/com/redtale/project/core/command/RedtaleCommand.java`（**仅追加 ≤3 行**：一行注释 + 一行 `.then(EnchantListCommand.node())`；禁止动已有行）
- 接口（一字不改）：
  - `public static com.mojang.brigadier.builder.LiteralArgumentBuilder<net.minecraft.commands.CommandSourceStack> node()`
  - 内部 `static int list(CommandContext<CommandSourceStack> ctx)`
  - 数据根：`net.neoforged.neoforge.server.ServerLifecycleHooks.getCurrentServer()`
    → `getWorldPath(net.minecraft.world.level.storage.LevelResource.DATAPACK_DIR).resolve("redtale_project")`，
    用 `Files.walk` 扫 `data/*/enchantment/**/*.json`（只认 `.json`，`data/redtale_project/tags/...` 自然被目录层过滤掉）
  - 解析用 `com.google.gson.JsonParser.parseString(...)`（已有依赖，别引新库）
- 输出（文案写死便于 grep；全部 `src.sendSuccess(() -> Component.literal(...), false)`）：
  - 无服务端实例：`当前没有服务端实例`
  - 一条都没有：`已生成附魔 0 条（数据包 redtale_project 未生成）`
  - 首行：`已生成附魔 <N> 条`
  - 每行：`  <id> · L<max_level> · <supported_items 原样> · <触发组件名逗号连接>`，**按 id 升序**
    - `id` = 相对 `enchantment/` 的路径去 `.json`，前面拼上 `data/` 下那一层的命名空间（`redtale_project:soul_reap`）
    - `max_level` 缺失写 `L?`；`supported_items` 缺失写 `-`；`effects` 缺失或空对象写 `无`
    - 触发组件名 = `effects` 的键，排序后逗号连接（`minecraft:post_attack`）
  - 行尾附加：`effects` 里出现 `"type": "redtale_project:scripted"` 且其 `script` 值在
    `config/redtale_project/scripts/` 下任一 `*.json5` 的文本里找不到 `id: "<script>"` 或 `"id": "<script>"`
    （引号两侧允许空白）→ 追加 ` · 脚本不存在`
- 不要做：不写盘、不打 `LOG`、不读 `RedtaleCore`、不改 `EnchantmentGenerator` / `EnchantableTags` /
  `tools/gen_enchant_lang.py`、不加参数（就 `/redtale enchant list`）、不碰附魔注册表、不新增依赖
- 异常策略：IO 失败 → 打一行 `<错误信息>` 并返回 0，**不许崩、也不许静默 return 1**
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "EnchantListCommand.node()" src/main/java/com/redtale/project/core/command/RedtaleCommand.java` = 1
  3. `cd build/libs && unzip -l redtale_project-*.jar | grep -c "core/command/EnchantListCommand"` = 1（有内部类会 >1，如实报数）
  > 功能验由 S7 跑：测试服 `/redtale enchant list` 应为 2 行（`super_sharpness L3` / `soul_reap L2`），
  > `soul_reap` 行尾**不带**「脚本不存在」（`scripts/enchants_soul_reap.json5` 在）。
- 进度：
  - 2026-11-17 05:41 · 完成 · 新建 `core/command/EnchantListCommand.java`（200 行，单类无内部类）；`RedtaleCommand` 第 121 行后 +2 行（注释 + `.then(EnchantListCommand.node())`，card 外零改动）· build `EXIT=0`（jar 340493 B）· 自测：`grep -c EnchantListCommand.node()`=1、jar 内该类=1、探针 `build/probe/EnchListProbe.java` **21/21**
  - 口径偏差（请 S7 定）：①「脚本不存在」判定必须兼容**单引号**——默认 `scripts/*.json5` 实际写 `id: 'enchants/soul_reap'`，卡面只写 `id: "x"` / `"id": "x"` 两种双引号形态，照抄会让 `soul_reap` 误报（与验收预期冲突）→ 实装正则 `(?<![A-Za-z0-9_])["']?id["']?\s*:\s*["']<script>["']`（键可带引号）。②`supported_items` 为字符串时**去引号**输出「原样」，非字符串取 JSON 文本；`max_level` 存在但非数字也按 `L?`。
  - 未离线验证项：`ServerLifecycleHooks.getCurrentServer()` / `FMLPaths.CONFIGDIR` 离线不可用 → 无服务端分支、0 条分支、IO 失败分支、真实数据包路径扫描 **待 S7 上测试服验收**（预期 2 行，`soul_reap` 行尾不带「脚本不存在」）。
  - 2026-11-17 05:41 · **S7 验收通过** · build `EXIT=0`（jar 340493 B）· `grep -c EnchantListCommand.node()`=1 · jar 内该类 **1 条**
  - 测试服实测（jar 已入 `E://server-test//mods`，`Done (2.353s)` 后 RCON）：
    `已生成附魔 3 条` / `frost_edge L3` / `soul_reap L2` / `super_sharpness L3`——**3 条而非卡面预期的 2 条**，原因是
    `data/redtale_project/enchantment/frost_edge.json` 是 R24 手测留下的落盘产物（配置目录里只有两份），
    命令**如实报落盘结果**，这正是它的用途（配置 vs 数据包漂移可见）。三行的 id / max_level / supported_items /
    触发组件与磁盘 JSON 逐字段核对一致，排序升序正确，`soul_reap` 行尾不带「脚本不存在」。
  - 负向验证：临时改名 `config/redtale_project/scripts` → `soul_reap` 行尾出现 ` · 脚本不存在`；改回后消失。
    → S8 提的单引号口径偏差**采纳**（默认配置写 `id: 'enchants/soul_reap'`，卡面双引号规则会误报）。

### T-0020 · [DROPPED] (S8 静默两轮，S7 自做 R27) 附魔可获取性 tag 生成（`in_enchanting_table` / `tradeable` / `on_random_loot`）

- 派单：S7 · 2026-11-16 21:15
- 目标：我们生成的 L0 附魔现在只有 `/enchant` 与铁砧能拿到（ENCHANT-API §7 的「M4 核对项」没做）。
  缺的是原版**可获取性 tag**：不写这三个 tag，附魔台刷不出（验收项 V4 过不了）、村民不卖、战利品不掉。
  写一份生成器，把 `enchantments/*.json5` 里声明的附魔 id **追加**进三个原版 tag（`replace: false`），
  做法与 `EnchantableTags` 完全同构（追加不替换、文本相等不重写）。
- 独占文件：
  - `src/main/java/com/redtale/project/enchants/EnchantObtainTags.java`（新建，唯一新建文件）
  - `src/main/java/com/redtale/project/core/RedtaleCore.java`（**仅追加 ≤2 行**：一行注释 + 一行调用；
    插在第 164 行 `EnchantableTags.generateAll(...)` 那条语句之后。**禁止删改任何已有行**）
- 接口（一字不改）：
  - `public static int generateAll(java.nio.file.Path datapackRoot, java.util.List<com.redtale.project.core.config.ConfigFile> configs, java.util.List<String> warnings)`
    —— 返回「实际写出（新建或内容变化）的文件数」，语义与 `EnchantableTags.generateAll` 一致
  - 私有工具照抄 `EnchantableTags` 的三件套：`writeTag(Path, List<String>, List<String>)`（幂等）+ Gson pretty + 末尾换行
  - 三个 tag 名固定（写死常量数组，**不许从配置读**）：`in_enchanting_table`、`tradeable`、`on_random_loot`
  - 输出路径：`datapackRoot/data/minecraft/tags/enchantment/<tag>.json`
  - 取值来源：`configs` 里 `path` 以 `enchantments/` 开头、以 `.json5` 结尾的文件，读其 `id` 字段（字符串）；
    `trim()` 后必须含 `:`，否则打一行 `WARN` 到 `warnings` 并跳过该文件；
    `id` 缺失或非字符串同样 `WARN` 跳过（**不要**自己拼 `redtale_project:<文件名>`，那是发明语义）
  - values **升序去重**（`TreeSet`），三份 tag 内容相同
  - `datapackRoot == null` → 打一行 WARN 到 `warnings` 并返回 0（照抄 `EnchantableTags` 的写法）
- 文件形态（用 `grep` 可判）：
  ```json
  {
    "replace": false,
    "values": [
      "redtale_project:soul_reap",
      "redtale_project:super_sharpness"
    ]
  }
  ```
- 不要做：不改 `EnchantableTags` / `EnchantmentGenerator` / `ScriptedEnchantmentEffect`；不写 `data/redtale_project/tags/**`
  （自家互斥 tag 归 `EnchantableTags`）；不碰 `tools/*.py`；不加原语；不改 `build.gradle`；不新增依赖；不打 `LOG`
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "EnchantObtainTags.generateAll" src/main/java/com/redtale/project/core/RedtaleCore.java` = 1
  3. 离线自测（写进 `build/probe/` 里自己的探针，**不要**接进 `build.gradle`）：
     用 `src/main/resources/redtale/defaults/enchantments/` 的两份真配置 + 一份手写坏文件（`id` 缺 `:`）
     喂进 `generateAll` 到临时目录，断言：① 写出 **3** 个文件且 `json.load` 全过；
     ② 每份 `values` = 2 个 id 升序、`replace` 为 `false`；③ 坏文件只产出 1 条 WARN、不进 values；
     ④ 第二次调用返回 **0**（幂等）
- 进度：**[S7 自做 · R27 完成]** 新建 `enchants/EnchantObtainTags.java`（156 行，三份 tag 写死 `in_enchanting_table`/`tradeable`/`on_random_loot`，`replace:false` 追加、文本相等不重写；取值只读 `enchantments/*.json5` 的 `id`，不含 `:` 或非字符串各 1 条 WARN 跳过；`datapackRoot==null` → 1 条 WARN 返 0）+ `RedtaleCore` 第 165 行 +1 行接线。`build --offline` exit 0（jar 354540 B）；独立探针 `build/probe/ObtainProbe.java` **20/20**；测试服实测三份 tag 落盘（values 2 条升序、`replace:false`）、`/redtale reload` 后 mtime 不变（幂等）、零 tag 解析告警。


### T-0021 · [VERIFIED] `SkillSpec` 技能定义解析器（M5 第一层，纯解析）

- 派单：S7 · 2026-11-17 05:50
- 目标：把 `config/redtale_project/skills/*.json5` 解析成内存对象。**schema 唯一权威是 `docs/SKILLS.md` §3**（一个文件一条技能，root 就是技能对象），照它写，不要自己加字段、不要自己加默认值。
  只解析，不执行、不接 `SkillEngine`、不读注册表（原语是否存在由运行期管，解析器必须是纯函数才能离线探针）。
- 独占文件：
  - `src/main/java/com/redtale/project/core/skill/SkillSpec.java`（**新建，唯一可写文件**；`core/skill/` 是新包，需要自己建目录）
- 接口（**一字不改**，S8 不得增删方法名/参数/返回类型）：
  ```java
  package com.redtale.project.core.skill;

  public final class SkillSpec {
      public record Definition(String id, String name, String icon, int cooldownTicks,
                               java.util.List<com.redtale.project.core.script.ScriptCall> conditions,
                               java.util.List<com.redtale.project.core.script.ScriptCall> effects,
                               String source) {}

      public static java.util.Map<String, Definition> parse(
              java.util.List<com.redtale.project.core.config.ConfigFile> configs,
              java.util.List<String> warnings);
  }
  ```
- 解析规则（逐条照 `docs/SKILLS.md` §3 的「解析口径」表，**不要自己发挥**）：
  1. `configs` 里只处理 `path` 以 `skills/` 开头、以 `.json5` 结尾的文件；`configs == null` → 返回空 Map 不抛；`warnings == null` 也不能 NPE（照 `SetSpec`/`AffixPools` 的既有写法）。
  2. `id`：必填、`trim()` 后非空、**必须含 `:`**；缺失/空白/不含 `:` → 整条跳过 + 1 条 WARN（文案里带上文件 path 与原因），**不许补命名空间**。
  3. `id` 重复 → 保留**先出现**的那条 + 1 条 WARN（含两个来源 path）。
  4. `name`：缺省 = `skill.redtale.<id 的 path 部分>`（`redtale_project:gale/slash` → `skill.redtale.gale/slash`，**不做二次改写**）；非字符串 → 用缺省 + 1 条 WARN。
  5. `icon`：缺省 `minecraft:paper`；非字符串 → 缺省 + 1 条 WARN。
  6. `cooldown_ticks`：缺省 `0`；负数 → `0` + 1 条 WARN；`> 1_000_000_000` → `1_000_000_000` + 1 条 WARN；非数字 → `0` + 1 条 WARN。
  7. `conditions`：可选，缺失 = 空列表；非数组 → 空列表 + 1 条 WARN；每项必须是对象且 `type` 为非空字符串，否则丢该项 + 1 条 WARN（**不因单项坏而丢整条技能**）。
  8. `effects`：**必填**。缺失 / 非数组 / 空数组 / 有效项 0 条 → 整条跳过 + 1 条 WARN。单项坏掉的判据同上。
  9. `args`：缺失 = 空 `JsonObject`（用 `ScriptCall.EMPTY`）；存在但非对象 → 空 args + 1 条 WARN。
  10. `ScriptCall` 用 `new ScriptCall(type, args)`；`args` 原样透传（**不许改键名、不许做单位换算**）。
  11. 返回值：`java.util.Collections.unmodifiableMap(new java.util.LinkedHashMap<>(...))` —— 保插入序 + 不可变；调用方 `put` 必须抛 `UnsupportedOperationException`。`Definition` 的 `conditions` / `effects` 也必须是不可变列表。
- 不要做：不建 `SkillEngine`、不建配置默认文件（`skills/*.json5` 的默认两份由 S7 放 `resources/redtale/defaults/` 并加进 `DEFAULT_FILES`）、不改 `docs/SKILLS.md`、不改 `RedtaleCore`/`RedtaleCommand`/`ScriptEngine`/`ScriptCall`、不加 `LOG` 打点（只用 `warnings`）、不新增依赖、不碰 `build.gradle`。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "public static Map<String, Definition> parse" src/main/java/com/redtale/project/core/skill/SkillSpec.java` = 1（写成全限定返回类型的等价写法也行，但 `grep -c "Definition> parse("` 必须 = 1）
  3. 离线探针 `build/probe/SkillProbe.java`（自建，**不要**接进 `build.gradle`）**≥18 条断言全过**，至少覆盖：`configs=null` 零告警空表 / `warnings=null` 不 NPE / 只有 `skills/` 前缀被处理（`items/x.json5` 忽略）/ 缺 `id` 跳过 1 WARN / `id` 不含 `:` 跳过 1 WARN / 重复 id 保留先出现 1 WARN / `name`、`icon` 缺省值逐字 / `cooldown_ticks` 缺省 0、负数归 0 各 1 WARN、`1e10` 夹到 1e9 1 WARN、`"x"` 归 0 1 WARN / `conditions` 缺省空表、非数组 1 WARN、单项缺 `type` 丢掉其余保留 / `effects` 缺失→整条跳过 1 WARN、空数组同上、全坏同上、单项坏保留其余 / `args` 缺失 = `ScriptCall.EMPTY`、非对象 1 WARN 且 args 为空 / 返回 Map 与两个列表均不可变（`put`/`add` 抛 `UnsupportedOperationException`）/ 同一批 configs 解析两次键序一致
- 进度：2026-11-17 06:52 · 完成 · 新建 `src/main/java/com/redtale/project/core/skill/SkillSpec.java`（199 行，单类 + 内部 `record Definition`，`core/skill/` 新包）；卡外零改动（`RedtaleCore`/`RedtaleCommand`/`ScriptCall` 均未碰，未接引擎） · build `--offline` EXIT=0（jar 360261 B） · 自测：`grep -c "Definition> parse("`=1、`grep -c "public static Map<String, Definition> parse"`=1、jar 内 `core/skill/SkillSpec` 宽匹配 2（主类 + `$Definition`）、探针 `build/probe/SkillProbe.java` **35/35**（覆盖卡面 18 条全部情形：null 入参 / 前缀过滤 / id 四态 / 重复保先 / name·icon 缺省 / cooldown 四态 / conditions 三态 / effects 四态 / args 三态 / 三处不可变 / 键序稳定）
- 进度（偏差，请 S7 裁决）· 2026-11-17 06:52 · 四处卡面未写死的小口径：①`id` 缺失与非字符串合并成**同一条** WARN 文案（卡面只列了缺失/空白/不含 `:` 三态，非字符串未单列）；②`effects` 全坏时 WARN 数 = 单项告警条数 **+1** 条「整条跳过」（把「整条跳过 + 1 条 WARN」读成「额外一条」）；③重复 id 的判定放在 `effects` 校验**之前** —— 同一 id 的第二份即使 effects 也坏，只报「重复」1 条；④`name` 为空串时按字符串原样保留（卡面只规定「非字符串」回落缺省，未规定空串）。以上四条都不改接口与验收计数，如需改口径回一句话即可。
- 进度 · 2026-11-17 07:4x · **S7 验收 → VERIFIED** · 三条验收全过：①`gradle build --offline` exit 0（jar 360261 B）；②`grep -c "Definition> parse("` = 1，jar 内 `core/skill/SkillSpec` 两个条目（主类 + `$Definition`）；③**S7 独立探针 `build/probe/S7SkillProbe.java` 50/50 PASS**（不复用 S8 的 `SkillProbe`）：`configs=null` 空表零告警 / `warnings=null` 不 NPE / 前缀筛（`items/`、`.json`、`.json5.bak` 静默跳过，`skills/sub/d.json5` 收）/ id 五态（缺·非字符串·空白·不含 `:` 各跳过 1 条告警、`' p:gale '` trim 后可用）/ 重复 id 保留先出现（cooldown 10 + source first）1 条告警 / name 缺省 `skill.redtale.gale/slash` 斜杠不改写、非字符串回落 1 条告警 / icon 缺省 `minecraft:paper` / cooldown 四态（缺省 0、120 原样、-5→0、1e10→1e9、`'x'`→0，后三者各 1 条告警）/ conditions 缺失空表·非数组 1 条告警·单项缺 type 只丢该项（两项坏 = 2 条告警）/ effects 缺失·非数组·空数组·全坏 各整条跳过 1 条告警、单项坏保留其余且顺序不变 / args 缺失 = `ScriptCall.EMPTY` 同一实例、非对象 → 空 args 1 条告警、对象原样透传（含嵌套键名不改）/ 三处不可变（Map.put、effects.add、conditions.add 全抛 `UnsupportedOperationException`）/ 两次解析键序逐字一致。**S8 提的四处口径偏差全部采纳、不打回**：①`id` 缺失与非字符串合并一条告警（行为一致，只是文案合并）；②`effects` 全坏时 WARN = 单项告警 + 1 条「整条跳过」（卡面「整条跳过 + 1 条 WARN」的字面读法）；③重复 id 判定在 `effects` 校验之前（与卡面规则编号 3 < 8 一致）；④`name` 空串原样保留（卡面只规定非字符串回落，空串属内容作者的显式选择）。附带发现（不是缺陷，已记 §13.31）：示范件若把 `name` 写成 lang 键，仓库里目前没有生成 `skill.*` 中文键的通道 —— 故默认两份技能直接写中文可读名。

### T-0022 · [VERIFIED] `SkillCooldowns` 技能冷却表（M5-A 门槛层，纯数据 + 注入时钟）

- 派单：S7 · 2026-11-17 05:52
- 目标：`docs/SKILLS.md` §6 的第一段——技能冷却表。**只做表，不做引擎**：不读注册表、不调 `ScriptEngine`、
  不碰 Minecraft 类型（不 import `net.minecraft.*` / `net.neoforged.*`，否则离线探针跑不了）。
  时间由调用方传入 tick（`long nowTick`），表自己不取 `Level.getGameTime()`。
- 独占文件：
  - `src/main/java/com/redtale/project/core/skill/SkillCooldowns.java`（**新建，唯一可写文件**）
    —— `core/skill/` 目录若已被 T-0021 建出来，直接用，**不要动 `SkillSpec.java`**
- 接口（**一字不改**，S8 不得增删方法名/参数/返回类型/可见性）：
  ```java
  package com.redtale.project.core.skill;

  public final class SkillCooldowns {
      public static int effectiveTicks(int cooldownTicks, double reduction);
      public boolean ready(java.util.UUID player, String skillId, long nowTick);
      public long remaining(java.util.UUID player, String skillId, long nowTick);
      public void start(java.util.UUID player, String skillId, int cooldownTicks, double reduction, long nowTick);
      public boolean tryStart(java.util.UUID player, String skillId, int cooldownTicks, double reduction, long nowTick);
      public int prune(long nowTick);
      public void clear(java.util.UUID player);
      public void clearAll();
      public int size();
  }
  ```
  需要 `public SkillCooldowns()` 无参构造（显式写出来，别靠默认构造被 record/内部类吞掉）。
- 语义（逐条，**不要自由发挥**）：
  1. `effectiveTicks(cd, r)`：`cd <= 0` → `0`；`r` 为 `NaN` / `Infinity` / `< 0` 一律当 `0`；`r > 0.9` → `0.9`；
     否则 `(int) Math.round(cd * (1.0 - r))`，**结果 `< 1` 时返回 `1`**（D19/SKILLS §6 的物理地板：0 tick 也留 1 tick）。
     全程不抛、不打日志。
  2. `remaining`：无记录、或 `nowTick >= 到期 tick` → 返回 `0` 并把该条删掉（顺手清理，别攒垃圾）；否则返回差值。
  3. `start`：先算 `effectiveTicks`；结果 `<= 0` → 删除该键（不留 0 tick 记录）；否则写入 `nowTick + ticks`。
  4. `tryStart`：`remaining(...) > 0` → **返回 false 且不改表**；否则 `start(...)` 并返回 **true**。
  5. `prune(nowTick)`：删掉所有 `到期 <= nowTick` 的记录，返回删除条数（用于玩家下线 / 定期清理）。
  6. `clear(player)`：删该玩家名下全部；`clearAll()` 清空表；`size()` = 当前记录总数（**不主动 prune**）。
  7. 空值容错（任一方法都**不许 NPE**）：`player == null` 或 `skillId == null` 或 `skillId.isBlank()` →
     `ready` 返回 `true`、`remaining` 返回 `0`、`start` 空操作、`tryStart` 返回 `true`（= 不拦，坏的调用方不该卡住释放）。
  8. 线程：只假设服务端主线程调用，**不加 `synchronized`、不用 `ConcurrentHashMap`**（注释里写一句这个前提）。
  9. 内部结构：`java.util.HashMap<UUID, HashMap<String, Long>>`；`skillId` 原样当键，**不 trim、不 lowercase**
     （技能 id 是 `ns:path`，大小写敏感由内容侧负责）。
- 不要做：不写 `SkillEngine`（S7 的）、不读配置、不写 `LOG`、不加 `cooldown_reduction` 属性的自动读取
  （属性值由调用方算好传 `reduction`）、不改 `docs/SKILLS.md`、不改 `RedtaleCore` / `RedtaleCommand` /
  `ScriptEngine` / `SkillSpec`、不加依赖、不碰 `build.gradle`。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "net.minecraft\|net.neoforged" src/main/java/com/redtale/project/core/skill/SkillCooldowns.java` = **0**（纯类，可离线跑）
  3. 离线探针 `build/probe/CooldownProbe.java`（自建，**不要**接进 `build.gradle`）**≥16 条断言全过**，至少覆盖：
     `effectiveTicks(0,0)`=0 / `(-5,0.5)`=0 / `(100,0)`=100 / `(100,0.5)`=50 / `(100,0.95)`=10（夹 0.9）/
     `(100,-0.3)`=100 / `(100,Double.NaN)`=100 / `(5,1.0)`=1（地板）/ `(1,0.9)`=1（地板）/
     新表 `ready`=true、`remaining`=0 / `start` 后 `remaining(now)`=100、`remaining(now+99)`=1、`remaining(now+100)`=0 /
     `tryStart` 冷却中返回 false 且 `remaining` 不变 / 冷却过后 `tryStart`=true / `start(0)` 后仍 `ready`=true /
     `prune` 返回删除数且 `size()` 递减 / `clear(uuid)` 只清该玩家 / `clearAll` 后 `size()`=0 /
     `null` 玩家与 `null`/空白 `skillId` 四个方法都不抛且返回值符合第 7 条。
- 进度：2026-11-17 07:55 · 完成 · 新建 `src/main/java/com/redtale/project/core/skill/SkillCooldowns.java`（141 行，单类无内部类，`SkillSpec.java` 未碰、卡外零改动） · build `--offline` EXIT=0（jar 366526 B） · 自测：`grep -c "net.minecraft\|net.neoforged"`=0（纯类可离线跑）、jar 内 `core/skill/SkillCooldowns`=1、九个方法签名与 §4.13 逐字一致（`effectiveTicks` 静态 + 8 个实例方法 + 显式无参构造）、探针 `build/probe/CooldownProbe.java` **48/48 PASS**（覆盖卡面 16 条全部情形：effectiveTicks 十态含 NaN/Inf/夹 0.9/地板 1、start→remaining 三段衰减、tryStart 冷却中 false 且 remaining 不变、冷却后 true 并重新记账、start(0) 不留记录、prune 计数与 size 递减、clear(p1) 只清该玩家、clearAll 归零、null 玩家 / null·空白 skillId 四方法不抛且返回值合第 7 条、id 大小写敏感不 trim）
- 验收：2026-11-17 09:12 · S7 · **VERIFIED（3/3）** · build `--offline` EXIT=0（jar 371570 B，3 up-to-date）· `grep -c "net.minecraft\|net.neoforged" SkillCooldowns.java`=**0** · jar 内 `core/skill/SkillCooldowns.class`=1 · S7 独立探针 `build/probe/S7CdProbe.java` **54/54 PASS**（不复用 CooldownProbe）：卡面 16 条全覆 + 额外查 `(100,+Inf)`=100、`(3,0.7)`=1 四舍五入、1 tick 打折仍记账、到期自动删键、`prune` 计数、id 大小写敏感/不 trim、空值四方法不抛


### T-0023 · [VERIFIED] `/redtale enchant obtain` —— 可获取性 tag 的只读对账（V4 的观测面）

- 派单：S7 · 2026-11-17 06:50
- 目标：R27 已经能把三条原版可获取性 tag（`in_enchanting_table` / `tradeable` / `on_random_loot`）生成出来，
  但**没有观测面**：附魔台刷不出时，没人能一眼分清是「tag 没写」「附魔没生成」还是「写错 id」。
  本卡做一条只读命令，把两份产物对账后逐 tag 打印「已收录 N / 应收录 M + 差集」。
- 独占文件：
  - `src/main/java/com/redtale/project/core/command/EnchantObtainCommand.java`（**新建，唯一新建文件**）
  - `src/main/java/com/redtale/project/core/command/RedtaleCommand.java`（**仅追加 ≤2 行**：一行注释 + 一行
    `.then(EnchantObtainCommand.node())`；插在 `.then(EnchantListCommand.node())` 那条语句**之后**。
    **禁止删改任何已有行**）
- 接口（一字不改）：
  ```java
  public static com.mojang.brigadier.builder.LiteralArgumentBuilder<CommandSourceStack> node();
  public static int obtain(com.mojang.brigadier.context.CommandContext<CommandSourceStack> ctx);

  // 两个包内可见纯函数：为了离线探针能直调，不许 private
  static java.util.Set<String> collectEnchantIds(java.nio.file.Path datapackRoot);
  static java.util.List<String> readTagValues(java.nio.file.Path datapackRoot, String tag);
  ```
  - `node()` 返回 `Commands.literal("obtain").executes(EnchantObtainCommand::obtain)`
  - 字段顺序/可见性照 `EnchantListCommand` 的写法（同包、无 import 冲突）
- 行为（逐条，**不要自由发挥**）：
  1. 数据包根：`ServerLifecycleHooks.getCurrentServer()` → `getWorldPath(LevelResource.DATAPACK_DIR).resolve("redtale_project")`。
     `server == null` → `src.sendFailure(Component.literal("[redtale] 没有服务端上下文"))` 并返回 **0**。
  2. `collectEnchantIds(root)`：扫 `<root>/data/<ns>/enchantment/**/*.json`，id = `<ns>:<相对路径去掉 .json>`，
     **子目录用 `/` 连接**（与 `EnchantListCommand` 同一口径，照它抄）；返回 `TreeSet`（升序、不可变）。
     目录不存在 → 返回空 Set（不抛）。
  3. `readTagValues(root, tag)`：读 `<root>/data/minecraft/tags/enchantment/<tag>.json` 的 `values` 数组，
     只收字符串项，**保持文件里的顺序**（原样，不排序）；文件不存在 → 返回 **`null`**（语义 = 未生成，
     与「生成但 values 为空」区分开）；坏 JSON / IO 异常 → 也返回 `null`。
  4. 三个 tag 名写死常量数组：`in_enchanting_table`、`tradeable`、`on_random_loot`（与 `EnchantObtainTags` 一致）。
  5. 输出格式（逐字，`Component.literal`）：
     ```
     [redtale] 附魔可获取性对账（已生成 2 条附魔）：
       in_enchanting_table  已收录 2/2  ✓
       tradeable            已收录 2/2  ✓
       on_random_loot       已收录 1/2  缺：redtale_project:frost_edge
     [redtale] 有 1 条附魔拿不到（缺 tag 见上）
     ```
     - 每行固定 `  ` + tag 名 + 两个空格 + `已收录 X/Y`；齐了在行尾加 `  ✓`，
       不齐加 `  缺：` + 差集（升序 id，逗号 + 空格分隔）
     - tag 未生成：该行文案 `  <tag>  未生成`（**不**写成 `0/N`，两者是不同的故障）
     - 已生成附魔数为 0：仍然三行都打「未生成」或「已收录 0/0」，末尾改成
       `[redtale] 还没有任何已生成的附魔（先 /redtale reload 生成数据包）`
     - 末尾一行：三条都齐 → `[redtale] 三条全齐 ✓`；否则 → `[redtale] 有 N 条附魔拿不到（缺 tag 见上）`
       （N = 三条 tag 缺集的**并集**大小）
  6. 只读：不写盘、不改配置、不打 `LOG`（只用 `sendSuccess` / `sendFailure`）。
- 不要做：不改 `EnchantObtainTags` / `EnchantableTags` / `EnchantmentGenerator` / `EnchantListCommand` / `RedtaleCore`；
  不生成或修复任何 tag（本卡只读）；不碰 `tools/*.py`；不加依赖；不改 `build.gradle`；不新增 `LOG` 打点。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "EnchantObtainCommand.node()" src/main/java/com/redtale/project/core/command/RedtaleCommand.java` = **1**，
     且 `unzip -l build/libs/*.jar | grep -c "core/command/EnchantObtainCommand.class"` = **1**
  3. 离线探针 `build/probe/ObtainListProbe.java`（自建，**不要**接进 `build.gradle`）**≥12 条断言全过**，至少覆盖：
     临时目录里造 2 个 `enchantment/*.json`（其中一个在**子目录**）+ 1 个非 `.json` 干扰文件 →
     `collectEnchantIds` 返回 2 条升序、子目录那条用 `/` 连接、干扰文件不收；
     `data/` 不存在 → 空 Set 不抛；
     造 2 份 tag（一份 values 少 1 条、一份**不存在**）→ `readTagValues` 对存在的返回原序列表、
     对不存在的返回 `null`、对坏 JSON 返回 `null`、`values` 里有非字符串项时跳过该项不抛。
- 进度：
- 2026-11-17 09:05 · 完成 · 新建 `core/command/EnchantObtainCommand.java`（186 行，单类无内部类）+ `RedtaleCommand` 第 130 行后 +2 行 · build `--offline` EXIT=0（jar 371570 B） · 自测：`grep -c "EnchantObtainCommand.node()"`=1；jar 内 `core/command/EnchantObtainCommand.class`=1；探针 `build/probe/ObtainListProbe.java` 18/18 ALL PASS
- 必要变更：`RedtaleCommand` 原末条 `.then(EnchantListCommand.node()));` 的 `));` 改成 `))` 才能续挂（与 T-0016/T-0019 同法），未删改任何行内容
- 卡面未写死口径（已按最保守解释实现，请 S7 确认）：①tag 文件存在但缺 `values` 数组 → 返回 `null`（与坏 JSON 同义）；②「未生成」的 tag 其缺集按「全部已生成附魔」计入末尾 `有 N 条` 的并集；③`未生成` 行同样做 19 列对齐；④`obtain` 返回值 = 已生成附魔件数（卡面未规定）；⑤`values` 里的对象项 `{"id":..}` 按「只收字符串项」跳过 —— 若将来 tag 改对象写法会误判为缺失
- 待 S7 验收（离线不可验）：真实服务端跑 `/redtale enchant obtain`，核对三行文案与 `EnchantObtainTags` 产物一致；`/redtale enchant obtain` 与 `/redtale enchant list` 在 brigadier 同名 `enchant` 节点下合并后两条都在
- 验收：2026-11-17 09:16 · S7 · **VERIFIED（3/3）** · build EXIT=0 · `grep -c EnchantObtainCommand.node()`=1 / jar 内 class=1 · S7 独立探针 `build/probe/s7obtain/…/S7ObtainProbe.java` **19/19 PASS**（不复用 ObtainListProbe：子目录 `/` 连接 + 非 .json 不收 + 不可变集合 + 空 values 与 null 的区分 + 坏 JSON/缺 values/非数组三种 null）· 测试服实测三分支：常态 `已生成 3 条`（frost_edge 为 R24 演练残留）+ 三行 `已收录 2/3 缺：…`；移走 `tradeable.json` → `tradeable  未生成` + `有 3 条附魔拿不到`；移走 frost_edge → 三行 `2/2  ✓` + `三条全齐 ✓`；`enchant list` 与 `enchant obtain` 同节点共存；两次夹具均已还原

### T-0024 · [VERIFIED] `/redtale content list` 行字段刷新（清掉「词条层未接入」的过期占位）

- 派单：S7 · 2026-11-17 07:50
- 目标：`ContentListCommand` 里还写着 `词条层未接入`（R11 之前的占位，见常量 `AFFIX_PENDING`），
  而 `ItemContent` 早已长到 15 字段（rev / consumable / repair / sockets / gem / setId）。本卡只改这一行文案与它取值的字段，
  **让运营一条命令看清「这件内容现在写了什么」**。只读，不改任何状态。
- 独占文件：
  - `src/main/java/com/redtale/project/core/command/ContentListCommand.java`（**唯一可写文件**；`RedtaleCommand` 不动，挂行已存在）
- 接口（一字不改）：
  ```java
  public static int list(com.mojang.brigadier.context.CommandContext<CommandSourceStack> ctx);
  ```
- 行为（逐条照做，**不要自由发挥、不要新增命令、不要加 LOG**）：
  1. 删掉常量 `AFFIX_PENDING` 与它的用法（这是本卡唯一允许的「删」）。
  2. 表头行改为：`[redtale] 内容 N 件 · 数值共 M 条 · 带 weapon_attributes W 件 · 词条池 P 个 · 套装定义 S 个`
     —— `P` = `core.affixPools().size()`，`S` = `core.sets().size()`（两个都是现成访问器，别自己算）。
  3. 每件的行改为（分隔符统一 `" · "`，字段顺序固定）：
     `<两空格><id> · base <base.id()|-> · 数值 <stats().size()> 条 · 孔位 <sockets().count()> · 套装 <setId()|-> · 消耗品 <是|否> · 修理 <是|否> · rev <rev()>`
     - `消耗品` = `consumable() != null` → `是`，否则 `否`；`修理` = `repair() != null` → `是`，否则 `否`
     - `sockets()` 为 `null` 时按 `0`（`ItemContent` 的 `sockets` 理论上非 null，但探针会构造 null，别 NPE）
     - `setId()` 为 `null` 或 `isBlank()` → `-`
  4. 空内容分支（`all.isEmpty()`）文案与返回值 **保持原样**，一个字都别改。
  5. 返回值仍是件数；`sendSuccess(..., false)` 保持广播关。
- 不要做：不改 `ItemContent` / `ItemContentRegistry` / `RedtaleCore` / `RedtaleCommand` / 其它命令类；
  不往行里加「词条适用池」这类需要跨模块算的字段（那是 `AffixRoller` 的活，本卡不算）；
  不改 `build.gradle`、不加依赖、不碰 `docs/`、不碰 `tools/*.py`。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "AFFIX_PENDING" src/main/java/com/redtale/project/core/command/ContentListCommand.java` = **0**，
     且 `grep -c "词条池 " src/main/java/com/redtale/project/core/command/ContentListCommand.java` = **1**
  3. S7 在测试服跑 `/redtale content list`：表头五个计数与 `content list` 件数自洽（`P` = `affix_pools/*.json5` 份数、
     `S` = `sets/*.json5` 份数），每行七个字段齐全、`demo_longsword` 行 `孔位 2`、`套装 emberforged`（写 `set_id` 原值）、`rev 1`
     —— 这条由 S7 执行，S8 只需在进度行贴出 `gradle build` 退出码与两条 grep 的实测数字。
- 进度：
- 2026-11-17 10:14 · 完成 · `ContentListCommand.java`（67 行；删常量 `AFFIX_PENDING` 与其用法，表头 +5 字段、每行 7 字段） · 只改本卡独占文件，卡外零改动 · build `--offline` EXIT=0（jar 386261 B） · 自测：`AFFIX_PENDING`=0、`词条池 `=1、jar 内该类=1、9 条字段文案在常量池各命中 1 · 功能项 `/redtale content list` 输出（demo_longsword 孔位 2 / 套装 emberforged / rev 1）待 S7 测试服验收
- 2026-11-17 10:33 · **S7 验收 → VERIFIED** · build `--offline` EXIT=0（jar 386261 B）· `AFFIX_PENDING`=0、`词条池 `=1 · 字节级：类常量池 `词条池`/`孔位 `/`套装 `/`消耗品 `/`修理 `/` · rev `/`套装定义 ` 各 1、`AFFIX_PENDING`=0
  · 测试服 `Done (2.256s)` 后 `/redtale content list`：表头 `内容 10 件 · 数值共 11 条 · 带 weapon_attributes 2 件 · 词条池 1 个 · 套装定义 1 个`
  = 对账（10 份 items / 11 = 3+4+2+2 / 2 份带 WA / 1 份 affix_pools / 1 份 sets）；10 行 × 7 字段齐全，
  `demo_longsword · 孔位 2 · 套装 emberforged · rev 2` —— 卡面写的 `rev 1` 是陈旧期望（R20 改 `set_id` 时已 +1 到 2），实测 2 与定义一致，判过


### T-0025 · [VERIFIED] `/redtale validate` 补第 6 条 —— 技能引用的原语是否存在（R28-d 收口）

- 派单：S7 · 2026-11-17 09:20
- 目标：解析层按 R28-d **不校验原语存在**（那需要启动期冻结的 `ScriptRegistries`），但「技能写了 `type: "dash"` 而 `dash` 还没实现」
  现在只有执行期一行 WARN —— 运营得先把技能放一遍才知道。本卡把这条检查并进 `validate`：只读、单类、不新增命令。
- 独占文件：
  - `src/main/java/com/redtale/project/core/command/ValidateCommand.java`（**唯一可写文件**；已有 142 行，本卡预计 +25 行以内）
- 接口：**不改任何方法签名**（`public static int validate(CommandContext<CommandSourceStack>)` 保持原样）。
  只允许新增**一个** `private static` 辅助方法，签名写死：
  ```java
  private static void checkSkillPrimitives(RedtaleCore core, List<String> problems)
  ```
- 行为（逐条照做，**不要自由发挥**）：
  1. 在现有第 5 条（套装引用，`for (ItemContent content : contents) { ... set_id ... }` 那一段）**之后**、
     `final int k = problems.size();` **之前**插入一行调用：`checkSkillPrimitives(core, problems);`
  2. `checkSkillPrimitives` 逻辑：
     - 遍历 `core.skills().all()`（`Map<String, SkillSpec.Definition>`，保持迭代序，**不要排序**，不要再 new 一个 map）
     - 对每条定义的 `conditions()`：`core.registries().condition(call.type()) == null` → 加一条问题；
     - 对每条定义的 `effects()`：`core.registries().effect(call.type()) == null` → 加一条问题；
     - **同一个（技能 id, 原语 type, 种类）只报一次**（`conditions` 与 `effects` 各算一类；同一技能里同 type 出现两次只报 1 条）
  3. 问题文案**逐字**（缩进两空格开头，与其它 5 条一致）：
     - condition：`"  " + 技能id + ": conditions 引用了未注册的原语 " + type`
     - effect：`"  " + 技能id + ": effects 引用了未注册的原语 " + type`
  4. `type` 可能是空串（解析层已丢过，理论上到不了这里）：照样按「未注册」报一条，**不要** NPE、不要跳过。
  5. 头部那行汇总**追加技能计数**（放在 `个套装` 之后）：
     `" · 技能 " + core.skills().size() + " 条"` —— 其余字一个不动，顺序保持
     `内容 / 词条池 / 词条定义 / 套装 / 技能 · 问题 N 条（外部 …）`。
  6. 返回值与「问题 0 条」分支文案**保持原样**（`return k;` 与 `（没有引用问题）`）。
  7. 只读：不写盘、不改内存、不打 `LOG`。
- 不要做：不改 `SkillRegistry` / `SkillSpec` / `ScriptRegistries` / `RedtaleCore` / `RedtaleCommand`；
  不在解析层加校验（R28-d 的红线）；不新增命令节点、不改 `AFFIX`/`SET`/`WA` 任何已有检查；不加依赖、不碰 `build.gradle`、不碰 `docs/`。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "checkSkillPrimitives" src/main/java/com/redtale/project/core/command/ValidateCommand.java` = **2**
     （1 处定义 + 1 处调用；多一处就说明抄了第二份），且
     `grep -c "引用了未注册的原语" src/main/java/com/redtale/project/core/command/ValidateCommand.java` = **2**
  3. S7 在测试服跑（**S8 不跑服**）：临时写一份 `skills/t_bad.json5`（`effects: [{type:"dash"}, {type:"console_log",args:{text:"x"}}]`、
     `conditions: [{type:"no_such_condition"}]`）→ `/redtale reload` → `/redtale validate` 恰好多 **2 条**问题
     （`effects 引用了未注册的原语 dash` / `conditions 引用了未注册的原语 no_such_condition`），头部技能计数 2 → 3；
     删掉该文件再 reload → 问题数回落到原值、两次输出逐字相同。S8 只需在进度行贴 build 退出码与两条 grep 的实测数字。

- 进度：
- 2026-11-17 11:28 · 完成 · `ValidateCommand.java`（142→167 行；新增 `checkSkillPrimitives(RedtaleCore, List<String>)` + 1 行调用 + 头部追加 `· 技能 N 条` + 2 个 import `ScriptCall`/`SkillSpec`） · 只改本卡独占文件，卡外零改动、`RedtaleCommand` 未碰 · build `--offline` EXIT=0（jar 393750 B） · 自测：`checkSkillPrimitives`=2、`引用了未注册的原语`=2、jar 内该类=1、`javap -p` 签名 `private static void checkSkillPrimitives(RedtaleCore, java.util.List<String>)` 与 `public static int validate(CommandContext<CommandSourceStack>)` 均在、常量池 `引用了未注册的原语`×2 / ` 个套装 · 技能 `×1 / ` 条 · 问题 `×1 / `（没有引用问题）`×1（顺序即拼接顺序）· 功能项（t_bad.json5 → reload → 恰多 2 条、头部技能 2→3、删除后逐字回落）待 S7 测试服验收

- 2026-11-17 11:46 · **S7 验收通过（3/3）** · ①`gradle build --offline` BUILD SUCCESSFUL exit 0（jar 393750 B，`compileJava UP-TO-DATE` 与 S8 报的 11:15 产物一致）；②`grep -c "checkSkillPrimitives"` = **2**、`grep -c "引用了未注册的原语"` = **2**；`javap -p` 复核 `private static void checkSkillPrimitives(RedtaleCore, java.util.List<String>)` 与 `public static int validate(CommandContext)` 均在；③测试服 `E:\server-test` 实测（`console_r31.log`，`Done (2.276s)`，已停、25567 无 LISTEN）：基线 `技能 2 条 · 问题 0 条`；写 `skills/t_bad.json5`（`conditions:[no_such_condition]` + `effects:[dash, console_log]`）→ reload `3 条技能（26 份配置文件）` → validate **`技能 3 条 · 问题 2 条`**，两条文案逐字 = `redtale_project:t_bad: conditions 引用了未注册的原语 no_such_condition` / `... effects 引用了未注册的原语 dash`；连跑两次逐字相同；删文件再 reload（`2 条技能 / 25 份配置文件`）→ 回到 `技能 2 条 · 问题 0 条` + `（没有引用问题）`。同技能同 type 只报一次成立（`dash` 在 effects 里只出现 1 条）。redtale 零 ERROR（4 条 RecipeManager 既有噪声）

### T-0026 · [OPEN] `buff` 原语 —— 增益类第一条（M5-C）

- 派单：S7 · 2026-11-17 10:40
- 目标：`docs/SKILLS.md` §4 第 15 条 `buff`（增益类 4 条的第一条）。现在技能只能回血 / 直伤，没有任何一条能给目标挂状态效果 ——
  内容侧写 `{type:"buff"}` 只会得到「引用了未注册的原语」的告警，运营无从下手。本卡只做 `buff`，不做 `debuff`。
- 独占文件（**只有这两个可写**）：
  - `src/main/java/com/redtale/project/core/script/builtin/BuffEffect.java`（**新建**）
  - `src/main/java/com/redtale/project/core/script/builtin/Builtins.java`（**只**允许加 1 行 `registries.register(new BuffEffect());`
    + 1 行注释；`registerAll` 的其它行、`ManualTrigger` / `PlayerJoinTrigger` 都不许动）
- 接口（一字不改）：
  ```java
  public final class BuffEffect implements com.redtale.project.core.script.EffectType
  public String id()                 // 固定返回 "buff"（小写，无命名空间）
  public String description()        // 一行中文参数说明，照 HealEffect 的写法
  public void run(ScriptContext ctx, com.google.gson.JsonObject args)
  ```
- 参数（`docs/SKILLS.md` §4 第 15 行）：

  | 键 | 缺省 | 语义 |
  |---|---|---|
  | `target` | `caster` | `caster` = 施法者；`target` = 本次触发的受害者（`ScriptContext#target()`） |
  | `effect` | **必填** | 原版效果 id，如 `minecraft:speed` |
  | `amplifier` | `0` | 等级偏移（0 = I 级）；负数归 0、>255 夹到 255 |
  | `duration_ticks` | `200` | 时长 tick；`<=0` 跳过；>72000 夹到 72000（原版瞬时效果上限） |

- 行为（逐条照做，**不要自由发挥**）：
  1. 施法者取法与 `HealEffect#pick` **完全一致**：`target=target` → `ctx.target()`；否则 `ctx.hasPlayer()` → `ctx.player()`；
     再否则 `ctx.vars().get("attacker") instanceof Entity`。取不到活体 → 一条 WARN `buff 没有可用目标` 后 return。
  2. `effect` 不是字符串 / 空串 → WARN `buff 缺 effect 参数` 后 return，**不要**抛异常。
  3. `ResourceLocation.tryParse` 失败 → WARN 后 return。
  4. `who.level().registryAccess().registryOrThrow(Registries.MOB_EFFECT).getHolder(id)` 取不到 → WARN 后 return。
  5. 成功：`who.addEffect(new MobEffectInstance(holder, duration, amplifier))`，再 `LOG.info` 一行
     `[script] buff · <目标名> + <effect id> <duration>t×<amplifier>`（照 HealEffect 的 `[script]` 前缀）。
  6. 告警**按文案去重只打一次**（照 `HealEffect#warnOnce` 的 `Set<String> WARNED`；不要按脚本名去重，那会刷屏）。
  7. 只用 `com.redtale.project.core.script` 包 + Minecraft 原版类，**零自有包依赖**（不要 import `RedtaleCore`）。
- 不要做：不做 `debuff`；不碰 `ScriptContext` / `ScriptRegistries` / `EffectType` / `HealEffect` / `DamageEffect`；
  不做「叠加层数 / 最大层数」（本卡没有这个概念）；不改 `docs/`；不加依赖、不改 `build.gradle`。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "new BuffEffect()" src/main/java/com/redtale/project/core/script/builtin/Builtins.java` = **1**，且
     `grep -c 'return "buff"' src/main/java/com/redtale/project/core/script/builtin/BuffEffect.java` = **1**
  3. `cd build/libs && unzip -l redtale_project-0.1.0.jar | grep -c "script/builtin/BuffEffect.class"` = **1**

  三条都由 S8 自己跑并在进度行贴实测数字；功能验收（写一份 `skills/t_buff.json5` → reload → 放技能看目标身上的效果与时长）
  由 S7 在测试服跑，**S8 不启停测试服、不发游戏内指令**。

- 进度：

### T-0027 · [OPEN] `/redtale content list` 补「技能」列（M5-B 的运营可见性）

- 派单：S7 · 2026-11-17 11:48
- 目标：`ItemContent` 第 16 字段 `abilities`（M5-B）已经写进 `ContentData`、tooltip 也会打「技能 N」，
  但 `content list` 一行一件的清单里**看不出来哪件武器带技能** —— 运营要判断「这份配置到底绑上没有」只能挨个 `/give` 再看 tooltip。
  本卡只补清单的显示，**不做**技能释放、不做写回。
- 独占文件（**唯一可写文件**）：
  - `src/main/java/com/redtale/project/core/command/ContentListCommand.java`（现 67 行，本卡预计 +12 行以内）
- 接口：不改任何方法签名（`public static int list(CommandContext<CommandSourceStack>)` 保持原样），
  只允许新增**一个** `private static` 辅助方法：
  ```java
  private static String abilitiesText(ItemContent content)
  ```
- 行为（逐条照做，**不要自由发挥**）：
  1. `abilitiesText` 返回：`abilities` 为空 / `null` → `"-"`；否则 `"N: id1 · id2"`（`N` = 条数，分隔符是两个空格夹一个 `·`，与 `ContentListCommand` 现有风格一致）。
  2. 每件内容那一行的**末尾**（`· rev N` **之后**）追加 `" · 技能 " + abilitiesText(content)`。已有字段的顺序与文案一个不动。
  3. 汇总行（`[redtale] 内容 N 件 · … · 套装定义 M 个`）**末尾**追加 `" · 带技能 K 件"`，`K` = `abilities` 非空的内容件数
     （与现有 `withWeaponAttributes` 同样的计数写法，别用 stream）。
  4. 只读：不写盘、不改内存、不打 `LOG`、不新增命令节点。
- 不要做：不改 `ItemContent` / `ContentData` / `ItemFactory` / `ContentTooltip` / `SkillCommand` / `RedtaleCommand`；
  不碰 `docs/`；不加依赖、不改 `build.gradle`；不引入 `stream()` / `var` 以外的新风格。
- 验收：
  1. `gradle build --offline` 退出码 0（取锁，见 §3）
  2. `grep -c "abilitiesText" src/main/java/com/redtale/project/core/command/ContentListCommand.java` = **2**（1 定义 + 1 调用），且
     `grep -c "带技能 " src/main/java/com/redtale/project/core/command/ContentListCommand.java` = **1**
  3. S7 在测试服跑（**S8 不跑服**）：`/redtale content list` 每行末尾都有 `· 技能 `，`demo_longsword` 显示 `1: redtale_project:gale_slash`
     （或该件当前 `abilities` 的实际值），汇总行出现 `带技能 1 件`（实测有几件就报几件）。S8 只需在进度行贴 build 退出码与两条 grep 的实测数字。

- 进度：

## 6. 派单池（S7 用，S8 不看）

按「单文件 / 无跨模块接口 / 机器可验」筛过的候选。派单时补「独占文件 + 验收」两栏。

| # | 候选 | 为什么适合 S8 | 依赖 |
|---|---|---|---|
| C2 | 附魔 schema → datapack 生成器骨架（`docs/ENCHANT-API.md` §3） | 纯字符串拼 JSON，单类 | M1 已就绪；M4 才用 |
| C3 | `tools/gen_item_lang.py`（对标 `gen_attr_lang.py`） | 独立脚本，输入输出都在文件系统 | 无 |
| C4 | `ContentData` 加 `glow` 字段 + 旧数据兼容（`rarity` 已有，别再派） | 单文件 + 一处 codec，验收=旧 JSON 仍能加载 | 无 |
| C5 | `AffixPool` 解析器（D22，`docs/ITEM-MODEL.md` §2） | 纯解析，不接结算 | 需先定 pool schema（S7 写在卡里） |
| C6 | `/redtale validate` —— 跑一遍所有配置的 schema 校验并汇总 | 只读，不改任何状态 | 无 |
| C7 | `/redtale item scan`（D33 只读统计：rev 分布 / 孤儿数 / 待升级数） | 单类命令，只读不改状态 | 要等 T-0006 的 `ItemUpgrader.plan` 落地 |
| C8 | `/redtale content check`（rev 漏加检测：文件 hash 变了但 `rev` 没变 → WARN） | 纯文件比对 + 一张缓存表 | 无（可用 `tools/` 或单类命令） |

**不适合给 S8 的**（留 S7）：伤害乘区、注册表结构、mixin、任何跨三个以上文件的改动、需要判断「该不该这么做」的事。

## 7. 验收命令速查

```bash
cd /e/RedtaleProject
gradle build --offline                      # 必须看退出码，不看 BUILD 字样
cd build/libs && unzip -l *.jar | grep X     # 产物里有新类
python -c "import json;json.load(open('f'))" # JSON 合法
grep -c "pattern" path                       # 行数断言
```
