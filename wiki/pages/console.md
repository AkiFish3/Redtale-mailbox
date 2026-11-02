---
title: 控制台美化
role: admin
group: 管理员
order: 8
---

# 控制台美化

## 做了什么

旧版整行套一个 `%highlightForge{}`，所以**整行一个颜色**，日志级别、来源、正文混在一起分不出来。

现在拆成三段各自上色：时间暗、级别按级别染色、来源品红、正文按 Minecraft 格式码解析。

## 配置在哪

`E:\server-1.21.1\config\log4j2-server.xml`：

```xml
<Console name="Console" target="SYSTEM_OUT">
  <Filters>
    <RegexFilter regex=".*moved (too quickly|wrongly)!.*" onMatch="DENY" onMismatch="NEUTRAL"/>
  </Filters>
  <PatternLayout disableAnsi="false"
    pattern="%style{[%d{HH:mm:ss}]}{dim} %highlight{[%t/%level]} %style{(%logger{1})}{magenta} %minecraftFormatting{%msg{nolookup}}%n%xEx"/>
</Console>
```

同一条规则也加在 `ServerGuiConsole` 上，否则 GUI 窗口里还是老样子。

## 三个必须记住的坑

### 1. `%style` 是两个花括号

正确：`%style{...}{dim}`
错误：`%style{...,dim}` —— 会把 `,dim` 当正文输出。

### 2. `%tEx` 不存在

原 pattern 结尾用了 `%tEx`，实测输出 `mainEx` 这种垃圾。要异常堆栈用 **`%xEx`**。

### 3. FML 会用 loader jar 内嵌的配置覆盖外部文件

这是最容易白干的一步：改完 `config/log4j2-server.xml` 发现没生效，因为 Forge/NeoForge 在正式环境读的是 **loader jar 里的 `log4j2.xml`**。

所以必须跑 `_patch_log4j_jar.py` 把新配置写进 `loader-4.0.45.jar`。`run.bat` 每次启动都会跑这个脚本，是幂等的。

校验：jar 内嵌的 `log4j2.xml` 大小应与 `config/` 里的一致（约 6688 字节）。

## 顺带解决的事

`user_jvm_args.txt` 里 `-Dlog4j2.configurationFile` 原本指向**不存在的 D 盘**，已改 `file:///E:/server-1.21.1/...`。

Windows 下这个属性必须带 `file:///` 前缀，写相对路径读不到。

## 屏蔽「moved too quickly」

原版 1.21.1 **没有** `moved-too-quickly-threshold` 这类配置项（已核 `DedicatedServerProperties` 和整个 jar）。所以要么装 RemoveSpeedDetection 这类 mod，要么在 log4j 层过滤。

选了后者——一条 `RegexFilter` 就够，不动游戏逻辑：

```
".*moved (too quickly|wrongly)!.*"  onMatch="DENY"
```

副作用：这是纯日志过滤，**服务端的移动检测照常运行**，只是不打印。玩家被拉回原地的情况不会消失，只是你在控制台看不到原因了。排障时要记得这一条。

## 想让日志更安静

可以按 logger 名字给特定包降级，比如：

```xml
<Logger name="com.iafenvoy" level="warn"/>
```

比全局改 level 安全，不会漏掉真正重要的报错。
