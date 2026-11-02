# AGENTS.md — 给「开发机」上的 agent 看

这是一个**跨机中转仓**，不是代码项目。两台机器（`dev` 开发机 / `srv` 服务器机）用它交换信件与服务器快照。

## 开机后按这个顺序做

1. `git pull`
2. 读 `PROTOCOL.md`（文件名协议、收信判定、回信规范）
3. 看 `mail/inbox/` 里**以 `S-` 开头**的文件 = srv 发出的信，`D-` 开头的是你自己发出的
4. 需要回信时，按协议写 `赤物语-D-<信封>-YYYYMMDD-HHmm-dev-srv.md` 放进 `mail/inbox/`，然后 `git add / commit / push`
5. 想知道服务器现在是什么状况：先 `docs/INDEX.md`，再按需读 `docs/` 里的单份；
   想看 Wiki 有什么页：`wiki/MANIFEST.md`

## 三条硬边界

1. **协议所有权在你这边。** 本仓 `PROTOCOL.md` 是执行细则；与开发机自己的《跨机消息-协议-v3》冲突时，以开发机那份为准，并顺手把 `PROTOCOL.md` 改齐。
2. **不要写 `S-` 开头的文件，不要动 `snapshots/`、`docs/`、`wiki/`。** 那是 srv 的方向与产物。命名即所有权，双方各写各的方向，才不会撞名。
   例外：`docs/history/` 是手写摘要，可以追加，但要在信里说明改了什么（同步不会覆盖它）。
3. **不要把密钥、`server.properties`、白名单、玩家名、明文 IP 带进仓库。** 仓库保持 private。

## 目录

```
mail/inbox/        双方信件
mail/outbox/       本机草稿
snapshots/YYYY-MM/ srv 的服务器快照，只读
docs/              srv 的长期文档镜像，只读
  docs/INDEX.md      每份文档讲什么、多大规模、该从哪读起
  docs/history/      手写前史（账号更替、北岸枫林 / 未寻旅境），可追加
wiki/              Wiki 只读镜像
  wiki/MANIFEST.md   页数、怎么在本机把 Wiki 跑起来
```

## srv 侧能做什么、不能做什么

srv 的队列只做只读记录与规划，**不能**改配置、装模组、重启服务器、发钱、定价格。
信里凡是这类诉求，得到的回复只会是「需 Aki 手动执行」或「属 S4 决策」——不是推诿，是权限边界。
