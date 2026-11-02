# Wiki 镜像说明

> 本目录是 `E:\server-wiki` 的**只读镜像**，由 `D:\redtale-ops\mail_sync_docs.py` 生成。
> 要改内容请改服务器上那份（或在 Wiki 网页里改），不要改这里——下一轮同步会整体覆盖。

同步时间：2026-11-02 12:29

## 体量

| 项 | 数量 |
|---|---|
| 手写页面 | 18 |
| 模组页面（自动生成） | 821 |
| 合计 | 839 |

## 手写页面

- `admin`
- `backlog`
- `changelog`
- `client`
- `console`
- `decisions`
- `faq`
- `gameplay`
- `index`
- `loot`
- `mobs`
- `modlist`
- `plan`
- `rules`
- `runbook`
- `start`
- `worldgen`
- `worlds`

## 模组页面

`pages/mod-*.md` 由 S5 队列从模组 jar 自动生成（含 `mod-<id>-1201.md` 这类旧服存档页），
内容稳定、不带你我手写的判断，所以整棵一起镜像、不做二次整理。

## 未镜像的内容

| 路径 | 原因 |
|---|---|
| `data/mc.json` | 含 RCON 口令与账号库路径 |
| `data/users.json` | 含玩家名与 UUID |
| `data/inbox_token` | 收件箱写入口令 |
| `data/tunnel_url.txt` | 临时公网地址，每次重启都变 |
| `tools/cloudflared.exe` | 53 MB 二进制 |
| `vendor/` | bcrypt 轮子，可用 pip 重装 |

## 怎么在本机跑起来

1. 装 Python 3.9+，`pip install bcrypt`（或把 `vendor\bcrypt` 拷回去）
2. 在 `data\` 里补 `mc.json`（`easyauth_db` 指向 EasyAuth 的 SQLite）
3. `python app.py`，浏览器开 <http://127.0.0.1:8080>

登录靠 EasyAuth 账号库；没有那一份库就只能是游客视图（可读、不能留言）。
