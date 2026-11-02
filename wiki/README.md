# 赤物语服务器 Wiki

本地知识库，双击 `启动.bat` 即可。打开 <http://127.0.0.1:8080>。

**`启动.bat` 必须是 GBK 编码**（Windows cmd 默认代码页 936）。用编辑器改完记得存成 ANSI/GBK；
存成 UTF-8 会让中文全部变成乱码，cmd 逐行解析时就报一堆「'cho' 不是内部或外部命令」。
嫌麻烦就改 `_make_bat.py` 再跑一次，它会重新生成一份 GBK 的 `启动.bat`。

`启动.bat` 自己找解释器：内置解释器 → PATH 里的 `python` → `py -3`，每个候选都真跑一次 `-c "import sys"` 才算数。
所以微软商店那个占位 `python.exe`（执行只会提示 Python was not found）不会被误选。

版式仿 Minecraft Wiki（MediaWiki / Vector）：左栏导航 + 顶部页签 + 白底正文框 + wikitable 表格 + 右侧信息框 + 自动目录。

改动前的旧版留了两份备份：`app.py.bak_20261102`、`static\style.css.bak_20261102`。

## 浏览不需要登录

任何人打开网址就能看：所有 `role: player` 的页面（含 240 多页模组页）、搜索、页面讨论区、意见箱都能翻。
游客唯一不能做的是**发言**（页面留言、意见箱），也看不到 `role: login`、特定组页面和管理后台。

点右上角「登录」；如果是在留言时被拦下，登录完会自动回到原来那一页。

## 账号与登录（用游戏的账号密码）

1.20.1 服装了 EasyAuth，Wiki 直接拿它的账号库校验，**不再自己发密码**：

- 账号 = 游戏 ID（大小写随意）
- 密码 = 进服密码
- 账号库：`E:\server\EasyAuth\easyauth.db`（SQLite，**只读**打开，不会写坏）
- 密码是 BCrypt（`$2a$12$…`），由 `vendor\bcrypt` 校验；Wiki 自己不存密码

配置在 `data\mc.json`：

```json
{ "easyauth_db": "E:/server/EasyAuth/easyauth.db",
  "wiki_admins": ["AkiFish3"] }
```

`wiki_admins` 里的 ID 登录后自动是 Wiki 管理员（服主号不用每次手动提权）。
第一次登录会在 `data\users.json` 自动建一条账号，只存称号和权限组；之后在 `/users` 改称号、加组，不影响游戏。

### 备用通道：没有游戏密码的号

登录页第二个页签「没有密码？用验证码」，给不在 EasyAuth 里的号（1.21 服玩家、测试号）用：
网页拿 4 位码 → 游戏聊天框发 `wiki 1234` → 网页通过 → 自己设 Wiki 密码。

实现上不装插件、不改 `server.properties`、不用重启服务器：`mcauth.py` 用 RCON 问 `list` 看谁在线，
再扫 `logs\latest.log` 尾部 512KB 找那一行聊天。验证码 5 分钟有效（通过后延长到 15 分钟）。
日志路径和 RCON 端口同样写在 `data\mc.json` 的 `log` / `rcon_*` 里。

### 称号

`data\users.json` 里每个账号可以有一个 `title`（如「服主」「建筑师」），登录后显示在右上角，
也会跟在留言署名后面。在 `/users` 页面直接改，不用手编 JSON。

## 权限怎么分的

页面头部有一段元信息：

```
---
title: 世界与维度
role: player      ← 可见组
group: 玩家指南
order: 2
nav: no           ← 可选，写 no 就不出现在左栏
---
```

- `role: player` —— 所有人可看，包括没登录的游客
- `role: login` —— 登录后才可见，游客访问 403、搜索也搜不到
- `role: admin` —— 只有管理员能看，其他人访问返回 403，左栏也不出现
- `role: <自定义组>` —— 只有该组成员和管理员能看
- **可以写多个组**，逗号隔开：`role: builder,staff` —— 属于其中任一组就能看，
  页面上会显示「仅建筑师、运维可见」

组表在 `data\groups.json`，目前有 玩家 / 登录玩家 / 建筑师 / 运维 / 管理员。
`player`、`login`、`admin` 是内置语义，不能删。
**不用手改文件**：管理员左栏「工具 → 权限组」可以增删改组，每个组会显示有几个成员、几个页面在用。
加组只要在这个文件里加一行，再给 `data\users.json` 里对应账号的 `groups` 数组加上组 id：

```json
{ "id": "builder", "label": "建筑师", "desc": "参与主城建设的成员" }
```

账号的 `groups` 长这样（不写就按 role 推：admin → `["admin","player"]`，player → `["player"]`）：

```json
"admin": { "salt": "...", "hash": "...", "role": "admin", "display": "服主",
           "groups": ["admin", "player"] }
```

管理员账号能看到全部页面，包括玩家页。

## 账号管理（`/users`）

管理员左栏「工具 → 账号与称号」。一表看全部账号，每行可改：

| 列 | 能改什么 |
|---|---|
| 显示名 | 站内显示的名字，默认等于游戏 ID |
| 称号 | 「服主」「建筑师」这种小标签，显示在右上角和留言署名旁 |
| 权限组 | 勾选框，属于哪些组（决定能看哪些页面） |
| 身份 | 普通 / 管理员 |

操作列有「保存 / 删除」。EasyAuth 账号还会显示「游戏」标签和「密码随游戏」——
这类账号的密码以游戏为准，Wiki 里改不了；只有备用通道开的号才有「重置密码」。
删除会保留这个人已发的留言（署名还在），只是不能再登录。
不能删自己，也不能取消自己的管理员权限（防止把自己锁在门外）。

顶上「新增账号」是给还没绑定游戏的成员（比如内部测试号）开号用的，
玩家自己绑定后会出现在表里，不用手动建。

## 留言与意见箱

### 每个页面都有讨论区
正文页顶部页签「讨论」，页签上带未读条数角标；正文页脚也有一条「去讨论区」的提示。
登录账号都能留言，支持 `**粗体**`、`` `代码` ``、裸链接自动识别、换行。
管理员在每条留言右侧有「隐藏 / 恢复」（软删除，记录还在文件里）。

### 全站意见箱（`/feedback`）
左栏「互动 → 意见箱」，红色数字是待处理条数。玩家提的任何建议都在这里，
管理员可以「回复」（会在条目下方显示绿框回复）和「标记已处理」。

### 存在哪
`data\social.jsonl`，一行一条 JSON（`kind` 是 `comment` 或 `feedback`）。没上数据库是故意的：
备份直接拷 `data\` 目录就行，出问题用文本编辑器就能看。

## 页面管理（`/pages`）

管理员登录后，左栏「工具 → 页面管理」是一张全站清单：标题、文件名、分组、**可见组下拉框**、最后修订时间。

下拉框改完立刻生效，不用重启服务。标「自动」的是 S5 队列脚本生成的页面（模组页等），
这类页面**重新生成时只改 `<!-- auto:begin/end -->` 之间那段**，手写的「中文简介」「在赤物语里」不会被覆盖。

## 目录

```
E:\server-wiki\
├── 启动.bat               双击启动（GBK 编码，别存成 UTF-8）
├── _make_bat.py           重新生成 启动.bat（改脚本内容时用）
├── app.py                 服务本体（路由 / 渲染 / 权限判断）
├── mcaccounts.py          读 EasyAuth 账号库，校验游戏密码
├── social.py              留言与意见箱（data\social.jsonl 的读写）
├── mcauth.py              备用绑定通道（扫日志 + RCON 查在线）
├── vendor\bcrypt\         校验 BCrypt 密码用的扩展，别删
├── data\
│   ├── users.json         账号（只存称号 / 权限组；备用号的 sha256+salt 也在这）
│   ├── groups.json        可见组表（player / login / builder / staff / admin）
│   ├── social.jsonl       留言 + 意见（一行一条，可直接文本编辑）
│   ├── bind.json          绑定中的验证码（5 分钟过期，可整个删）
│   ├── mc.json            EasyAuth 账号库路径、服主 ID、日志与 RCON
│   └── pages\*.md         内容，一篇一个文件（mod-*.md 由 S5 生成）
└── static\style.css       样式
```

## 搜索

顶部搜索框输入关键词回车 → 全文搜索标题 + 正文，结果按相关度排序，命中词高亮，带分类标签。
清空关键词直接访问 `/search` 就是**全部页面清单**。

搜索结果只包含你**能看的**页面：游客搜不到 `role: login`、各组和 `role: admin` 的页面，
不是点了才 403，而是根本不出现在结果里。

## 加页面

**网页里新建（推荐）**：管理员登录后，左栏「工具 → 新建页面」，填标题、文件名、分组、排序、权限，
点「创建并开始编辑」→ 自动跳到编辑器写正文。文件名不可重复，只能用 `a-z 0-9 _ -`。

**手动建**：在 `data\pages\` 下新建 `任意名字.md`，写好头部元信息即可，刷新就出现。

文件名只能用 `a-z 0-9 _ -`。`order` 越小越靠前，`group` 相同会归到同一栏。

## 改页面

两个办法：

1. **网页里改** —— 管理员登录后，页面底部有「编辑本页」，改完点保存，立刻生效。
2. **直接改文件** —— 用任意文本编辑器打开 `data\pages\xxx.md`，保存即生效。

网页编辑器只给管理员开，玩家看不到入口。`role` 那一行也可以在编辑器里直接改。

## 页面写法（Markdown 扩展）

普通 Markdown 都支持（标题、列表、表格、引用、代码块、原始 HTML 行）。另外加了四种维基常见写法：

**1. 站内链接** —— 目标页面不存在时自动显示红链：

```
见 [[worlds]] 或 [[worlds|世界与维度]]
```

**2. 右侧信息框**（第一个 `:::` 后面写标题，`|` 分键值）：

```
::: infobox 末影龙
| 生命值 | 200
| 类型 | Boss
:::
```

**3. 提示框** —— `tip` 绿 / `note` 蓝 / `warn` 橙：

```
::: tip 小提示
正文
:::
```

**4. 目录自动生成** —— 一页里有 3 个及以上 `##` 标题时，正文开头自动插入「目录」框，标题带锚点。

页面正文第一行的 `# 标题` 会被当成文章大标题（和页面标题不同时以正文为准），不用重复写。

## 改密码

玩家的密码在游戏里改（EasyAuth 的改密命令，看服务端配置），Wiki 不用动，下次登录自动生效。

只有「备用通道」开的号（以及早期手动建的账号）密码存在 Wiki 里：

1. 生成新哈希：

```bash
python -c "import hashlib,secrets;s=secrets.token_hex(8);print(s, hashlib.sha256((s+'新密码').encode()).hexdigest())"
```

2. 把输出的两个值填进 `data\users.json` 对应账号的 `salt` 和 `hash`。
3. 重启服务（已登录的会话会失效）。

EasyAuth 账号在 `users.json` 里没有 `salt`/`hash`，**别手动加**——加了也不生效，
登录永远以游戏密码为准（`do_login` 先查 EasyAuth）。

## 让局域网的人访问

服务默认监听 `0.0.0.0:8080`，同一局域网直接访问 `http://<你的内网IP>:8080` 即可。

首次启动 Windows 会弹防火墙提示，选**允许专用网络**。如果没有弹或者被拒了：

```
netsh advfirewall firewall add rule name="RedtaleWiki" dir=in action=allow protocol=TCP localport=8080
```

**不要**把这个端口映射到公网——它只做了最基础的登录，没有 HTTPS，没有防爆破。

## 换端口

```
python app.py 9000
```

## 停止

双击 `停止.bat`（停 wiki + 看门狗 + 公网隧道）。只想停某一个：任务管理器结束对应的 `pythonw.exe` / `cloudflared.exe`。

## 常驻（为什么它不会再"用着用着就没了"）

| 文件 | 作用 |
|---|---|
| `wiki_service.pyw` | 看门狗：`app.py` 退出 4 秒后自动拉起；连续 6 次秒退才放弃并写日志 |
| `logs\service.log` | 启停记录 |
| 启动文件夹 `RedtaleWiki.vbs` | 登录 Windows 自动拉起（无窗口） |
| `启动.bat` | 手动启动（自带同样的守护循环），排障用 |

关键：**不要在对话里 `python app.py 8080`**。那种进程挂在会话的作业对象下，会话一结束就被回收 —— 这正是以前"过一会儿就断"的原因。现在进程由 explorer/登录项拉起，和对话无关。

## 待拍板（S1–S5 队列的统一出口）

页面 `decisions.md`（侧栏：管理员 → 待拍板），结构固定两节：`## 待处理` / `## 已定`。

- 写入口：`POST /api/inbox`，头 `X-Inbox-Token`，令牌在 `data/inbox_token`
- 动作：`add`（追加）、`resolve`（挪到已定并写死结论）
- 客户端：`D:\redtale-ops\wiki_inbox.py`，文档 `D:\redtale-ops\_srv_INBOX.md`
- 服务端持 `LOCK` 串行写、`os.replace` 原子替换、按 `<!-- inbox:key=… -->` 去重
- 只改这两个小节，页面其余内容一个字不碰；小节标题被删掉会返回 `SKIP 缺少小节`

## 公网访问

`app.py` 绑 `0.0.0.0:8080`，局域网直接 `http://<内网IP>:8080`。
外网用 Cloudflare 隧道：`tools\cloudflared.exe`（2026.10.7，走 ghfast.top 镜像下的，官方 GitHub 在这台机器上不通）。

```
双击 公网访问.bat        → 地址写进 data\tunnel_url.txt
或  explorer tunnel_hidden.vbs   （无窗口版，脚本里用）
```

- 快速隧道**不需要账号**，但域名每次重启都变；要固定域名得用命名隧道（Cloudflare 账号 + 域名，`cloudflared tunnel login / create / route dns`）
- 实测：`/login` 200、`/p/index` 200、`/p/decisions` 403（未登录）、`/api/inbox` 403（缺令牌）
- **公网前置条件**：登录只走 EasyAuth（游戏 ID + 进服密码）。建站时的演示号 `admin`/`redtale-admin`、`player`/`redtale` 已在 2026-11-02 删除，别再造固定口令的本地号


## 账号模型（2026-11-02 起）

| 来源 | 存在哪 | 怎么用 |
|---|---|---|
| EasyAuth 游戏账号 | `E:\server\EasyAuth\easyauth.db`（只读） | 用户名 = 游戏 ID，密码 = 进服密码。首次登录自动在 `users.json` 建档 |
| 验证码通道（`/login?tab=bind`） | `users.json` 的 `salt`/`hash` | 适用于不在 EasyAuth 里的号；在游戏里发 `wiki <4位码>` 证明身份后自设密码 |
| 管理员手动建号 | 同上 | 站内「用户管理」页 |

- 服主 ID 名单在 `data\mc.json` 的 `wiki_admins`（当前 `AkiFish3`），这些 ID 无论走哪条通道登录都是管理员。
- `app.py` 的 `do_login()` **先 EasyAuth、失败回落本地密码**。所以 `users.json` 里放一个 EasyAuth 中不存在的 ID + 固定口令，就是一个绕开游戏账号的后门——不要再这么干。
- 本地密码机制不能整块删：验证码通道和管理员建的号都靠它。



## 模组页（S5 自动维护）

`mod-*.md` 一共 241 页，由 `D:\redtale-ops\_srv_artifacts\s5_wiki_sync.py` 生成，**不要手动新建同名文件**。

- 每页文件名 `mod-<Mod ID>`，分组「模组」，`nav: no`（不进左栏，从「模组总览」点进去）
- 双端 / 仅客户端模组 → `role: player`；仅服务端与服务端工具（chunky、spark 等）→ `role: admin`
- 两张总览页：`mod-index`（玩家可见，233 条）、`mod-index-server`（管理员，8 条服务端工具）
- 页面里 `<!-- auto:begin --> … <!-- auto:end -->` 之间是脚本区，**只改这里**；
  其余段落（中文简介、在赤物语里）是手写区，脚本永不覆盖
- 模组增删、版本变化 → 下次跑脚本自动同步，并把「还缺什么」写进 `D:\redtale-ops\_srv_S5_WIKI.md` 的任务池

改了配置（扫哪个目录、哪些算服务端工具、强制某页权限）→ 改 `s5_config.json` 再跑脚本。

## 已知限制

- 会话存在内存里，**重启服务要重新登录**。
- 登录密码 = 游戏密码，所以 Wiki 的登录安全等价于游戏账号；同一 IP 连错 10 次会锁 10 分钟。**对外开放前先确认管理员口令够强**（快速隧道一旦跑起来，全世界可访问 `/login`）。
- 依赖 `vendor\bcrypt`（Windows 版 wheel）。换机器/删了 vendor，网站还能开，但游戏密码登录会提示找服主。
- EasyAuth 账号库只读打开；服务器正在跑的时候登录也没问题。
- 没有页面历史 / 版本回退。重要内容自己留一份，或者靠 D 盘的备份。
- 没有上传图片功能。要放图就把图片放进 `static\`，页面里写 `<img src="/static/xxx.png">`（Markdown 渲染器支持原始 HTML 行）。
