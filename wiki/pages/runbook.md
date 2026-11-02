---
title: 启停与端口
role: admin
group: 管理员
order: 2
---

# 启停与端口

## 正常启停

**启动**：`E:\server-1.21.1\run.bat`。它会先跑 `_patch_console.ps1` 补 JLine 的 JNA 依赖，再拉起 java。

**关闭**：**永远用 `stop`，不要直接关窗口。**

```
/stop
```

或者通过 RCON 发。直接杀进程会让世界文件处于未保存状态，虽然回滚备份能救，但没必要。

关闭顺序建议：先 `save-all flush`，确认日志出现 `Saved the game`，再 `stop`。

## 端口表

| 用途 | 旧服 | 新服 |
|---|---|---|
| 游戏 | 25565 | 25566 |
| RCON | 25575 | **25576** |
| Query | 未开 | 未开 |

改端口要同时改 `server.properties` 里的 `rcon.port`，**改完必须重启**（RCON 端口不支持热重载）。

## RCON

`server.properties` 里：

```
enable-rcon=true
rcon.port=25576
rcon.password=<看文件>
```

密码明文存在 `server.properties` 里，**不要把这一页截图外发**。

用 Python 发一条指令（本机测试）：

```python
# 简化版，完整脚本在 temp 目录
import socket, struct
```

日常更推荐直接进服务器控制台敲，RCON 只在脚本化时需要。

## 命令行直启（脚本被拦时）

如果 `run.bat` 因为安全策略起不来，可以绕过 bat 直接拉 java：

```
java @user_jvm_args.txt @libraries/net/neoforged/neoforge/21.1.257/win_args.txt nogui
```

在 `E:\server-1.21.1` 目录下执行。工作目录必须是服务端根目录，否则找不到 `mods`。

## 启动要多久

225 个模组，冷启动约 **8 秒**到 `Done`，但如果触发区块生成会延长到 30 秒以上。日志里看到 `Done (8.062s)!` 就算起来了。

## 排障顺序

起不来的时候按这个顺序看：

1. `logs/latest.log` 最后 50 行，找 `Exception` / `Caused by`
2. `crash-reports/` 最新的一份
3. 最近改过什么（模组？配置？数据包？）——先回滚那一项
4. 模组冲突：二分法，一次移一半

> 别一次改多个东西再启动，出问题无法二分。
