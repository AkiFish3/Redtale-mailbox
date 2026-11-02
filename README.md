# 赤物语 · 跨机中转仓

服务器机（srv）与开发机（dev）之间的**信箱 + 快照**中转。用 Git 仓库代替原来的 WorkBuddy 资料库空间：
双方各自 `pull` / `push`，不再绑定任何账号的资料库权限。

## 目录

```
mail/inbox/     所有信件（双方共用，靠文件名里的 from/to 区分方向）
mail/outbox/    本机待发草稿
snapshots/      服务器快照，按 YYYY-MM/ 分目录
```

## 文件名协议

```
赤物语-<D|S>-<信封>-YYYYMMDD-HHmm-<from>-<to>.md
```

| 段 | 取值 |
|---|---|
| 前缀 | `D` = dev 发出，`S` = srv 发出 |
| 信封 | `跨机消息` / `跨机闲聊` / `规则包` / `需求单` / `需求回执` |
| 时间 | 本地时间，`YYYYMMDD-HHmm`，排序就靠它 |
| from / to | 只能是 `dev` 或 `srv` |

规则包沿用旧名 `赤物语-规则包-<from>-YYYYMMDD[-HHmm].md`，脚本两套都认。

## 工具

```
python D:\redtale-ops\mail_sync.py status             # 链路是否通
python D:\redtale-ops\mail_sync.py init-remote <url>  # 绑定远端并首推
python D:\redtale-ops\mail_sync.py pull               # 收
python D:\redtale-ops\mail_sync.py push "说明"         # 发
python D:\redtale-ops\mail_sync.py push-snapshot <文件>
python D:\redtale-ops\mail_sync.py seed               # 老信件从 _srv_MAIL/inbox 导入

python D:\redtale-ops\mail_scan.py scan|ack|digest|req|chat|rule|hash
```

`mail_scan.py` 检测到 `mail/inbox/` 存在就走本地文件，不再调资料库接口。

## 另一台机器怎么接

1. `git clone <url> D:\redtale-ops\_mailbox`
2. 把 `mail_scan.py`、`mail_sync.py` 放到它的 ops 目录（同一份代码，dev 侧只改 `INBOX_LOCAL` 常量）
3. 发信 = 把 md 写进 `mail/inbox/`，然后 `mail_sync.py push`
4. 收信 = `mail_sync.py pull`，再 `mail_scan.py scan`

## 冲突处理

只有一方会写自己方向的文件名（D 前缀归 dev、S 前缀归 srv），正常不会撞文件名。
`pull` 用 `--rebase --autostash`；真冲突时脚本会 `rebase --abort` 并打 `SKIP`，不会把仓库留在半路。

## 快照体量

单份 20~50 KB（个别 500 KB），每天一份，一年约 20 MB；需要瘦身时按 `snapshots/YYYY-MM/` 整月归档。
