# -*- coding: utf-8 -*-
"""wiki_service.pyw —— 让 wiki 常驻，不依赖任何对话窗口。

为什么要有这个文件：
    以前的做法是在会话里 `python app.py 8080`，会话一结束进程就被回收，
    表现就是「wiki 用着用着就没了」。这里改成独立服务：进程被关掉 4 秒后自动拉起，
    由计划任务在登录时启动，和对话彻底解耦。

用法：
    直接双击没反应（.pyw 无控制台）属于正常，去看 http://127.0.0.1:8080。
    手动停止：任务管理器结束 pythonw.exe，或运行 停止.bat。
"""
import os
import socket
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = "8080"
LOG = os.path.join(ROOT, "logs", "service.log")


def port_busy():
    try:
        s = socket.create_connection(("127.0.0.1", int(PORT)), timeout=1.0)
        s.close()
        return True
    except OSError:
        return False


def note(msg):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg))
    except OSError:
        pass


def main():
    if port_busy():
        note("8080 已被占用，本守护进程退出（说明已有实例在跑）")
        return
    py = sys.executable
    if py.lower().endswith("pythonw.exe"):
        py = os.path.join(os.path.dirname(py), "python.exe")
    note("守护启动 pid=%s" % os.getpid())
    fails = 0
    while True:
        t0 = time.time()
        try:
            p = subprocess.Popen([py, "app.py", PORT], cwd=ROOT)
            p.wait()
        except Exception as e:                      # noqa: BLE001
            note("启动失败: %s" % e)
        alive = time.time() - t0
        note("app.py 退出，存活 %.0f 秒" % alive)
        # 秒退说明是端口冲突/依赖缺失这类硬错，别无限刷
        fails = fails + 1 if alive < 15 else 0
        if fails >= 6:
            note("连续 %d 次秒退，守护停止。手动修好后重新运行本文件。" % fails)
            return
        time.sleep(4)


if __name__ == "__main__":
    main()
