# RedtaleProject 进展（srv 侧）

> 自动生成：2026-11-27 06:23 · `D:\redtale-ops\gen_progress.py`
> 源：`docs/TASKS.md`（卡板）· `PLAN.md` §13（轮次台账）· `_srv_QUEUE_BOARD.md`（队列动态）
> 对端：`PROGRESS-dev.md` 由 dev 自己写，本文件不覆盖它。

## 1. 当前里程碑

**未知**（依据：最近一条提到里程碑的台账标题「」）

## 2. 进行中（在制品上限 3 张）

| 卡 | 状态 | 标题 |
|---|---|---|
| T-0130 | OPEN | `tools/check_weapon_attr_ref.py` —— `weapon_attributes` 外部引用 ↔ BetterCombat 内置动作对账（引用型，对账网第五十六例） |
| T-0131 | OPEN | 护甲三件套内容：`demo_helmet` / `demo_greaves` / `demo_boots` + 套装 `ashen_vow`（D1 装备线 / M3 套装线，内容面卡） |

已验完 **127** 张 / 共 **131** 张。

## 3. 最近五轮（PLAN §13 台账）

| 轮 | 日期 | 一句话 |
|---|---|---|
| R86 | 2026-11-21 | **验收 T-0081（`check_skill_args.py`）+ 接线 `check_all` 29→30 + 派 |
| R87 | 2026-11-21 | **验收 T-0082（`check_script_args.py`）+ 接线 `check_all` 30→31 +  |
| R88 | 2026-11-21 | **验收 T-0083（`check_effect_target.py`）+ 接线 `check_all` 31→32  |
| R89 | 2026-11-21 | **验收 T-0084（`check_mob_equipment.py`）+ 接线 `check_all` 32→33  |
| R90 | 2026-11-21 | **验收 T-0085（`check_use_script.py`）+ 接线 `check_all` 33→34 + 派 |

## 4. 卡住的（真实缺口，不是产能问题）

- 最新一处：挂账第 **40 轮**（`PLAN.md` 里最早见第 6 轮）。多为「需客户端窗口」的 GUI 验收

## 5. 队列动态（协作板最近 5 条）

- `2026-11-16 18:05` S7 · 验收 **T-0015 → VERIFIED**（3/3 + 功能四跑：三份坏配置 → `问题 4 条`，四条文案逐字对上；删掉后 `（没有引用问题）`；两次连跑 diff 空）；**派 T-0017
- `2026-11-16 21:25` S7 · 验收 **T-0018 → VERIFIED**（3/3 + 测试服四跑：基线 0 条 → 三处坏配置（套装 piece 写错 / `set_id` 悬空 / `applies_to` 裸名）→ `问
- `2026-11-17 06:10` S7 · **代码仓上线**：`github.com/AkiFish3/RedtaleProject`（private），已推 2 个提交（`5794d69` 初始 / `847d232` 规则），160 文件
- `2026-11-17 06:35` S7 · **REQ-N08 结案**：dev 报 8 条文档矛盾，逐条核代码后判 **7 成立 / 1 过度**（#2 说「迁移会丢孔位宝石」→ 读 `ItemUpgrader.ensure:179-184`
- `2026-11-21 02:05` S6 · **签到「总是失败」定位并修复**：根因三条叠加 —— ①`checkin-cred.json` 的 cookie 11-15 落盘、服务端 401 判定 session 过期（寿命约 4 天，无自动

---

## 6. dev 侧要写的：`PROGRESS-dev.md`

同一目录下建一个同名不同后缀的文件，固定四段，每段一行一条：

```markdown
## 进行中    <REQ 号或任务名> · 做到哪步 · 预计还差什么
## 已完成    <REQ 号> · 交付物路径
## 卡住的    卡在哪 · 需要 srv 提供什么（写具体文件或字段名）
## 下一步    下一轮打算做的一件具体的事
```

只追加，不改历史。srv 侧只读，永不覆盖。
