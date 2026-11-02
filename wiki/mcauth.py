"""Minecraft 玩家身份绑定。

原理：离线服没有密码，能证明「我是这个 ID」的唯一方式是在游戏内说话。
玩家在 Wiki 上填游戏 ID → 拿到 4 位验证码 → 在游戏聊天里发 `wiki 1234`
→ Wiki 扫服务端日志确认这句话确实由该 ID 发出 → 绑定成功。

不依赖任何服务端插件，不改 server.properties，也不需要重启服务器。
"""

import json
import os
import re
import secrets
import socket
import struct
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
BIND_FILE = os.path.join(DATA, "bind.json")

# 服务端（可在 data/mc.json 覆盖）
DEFAULT_MC = {
    "log": r"E:\server-1.21.1\logs\latest.log",
    "rcon_host": "127.0.0.1",
    "rcon_port": 25576,
    "rcon_password": "***",
}

CODE_TTL = 300          # 验证码有效期（秒）
SCAN_TAIL = 512 * 1024  # 只读日志尾部，避免大文件全量扫描

CHAT_RE = re.compile(r"<([^<>\n]{2,32})>\s*wiki\s+(\d{4,8})\b", re.I)
JOIN_RE = re.compile(r"([A-Za-z0-9_]{2,32}) joined the game")


def mc_config():
    cfg = dict(DEFAULT_MC)
    try:
        with open(os.path.join(DATA, "mc.json"), "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    return cfg


# ------------------------------------------------------------------ 日志扫描

def _tail_text(path, limit=SCAN_TAIL):
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            if size > limit:
                f.seek(size - limit)
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


def server_online_players():
    """通过 RCON 取在线玩家；服务器没开或 RCON 不通时返回 None。"""
    cfg = mc_config()
    try:
        s = socket.create_connection((cfg["rcon_host"], cfg["rcon_port"]), timeout=3)
    except OSError:
        return None
    try:
        s.sendall(_rcon_pack(1, 3, cfg["rcon_password"]))
        rid, _ = _rcon_read(s)
        if rid == -1:
            return None
        s.sendall(_rcon_pack(2, 2, "list"))
        _, body = _rcon_read(s)
        if not body:
            return []
        names = body.split(":", 1)[-1].strip()
        return [n.strip() for n in names.split(",") if n.strip()] if names else []
    except Exception:
        return None
    finally:
        try:
            s.close()
        except Exception:
            pass


def _rcon_pack(rid, ptype, body):
    payload = struct.pack("<ii", rid, ptype) + body.encode("utf-8") + b"\x00\x00"
    return struct.pack("<i", len(payload)) + payload


def _rcon_read(sock):
    head = b""
    while len(head) < 4:
        chunk = sock.recv(4 - len(head))
        if not chunk:
            return None, ""
        head += chunk
    length = struct.unpack("<i", head)[0]
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            break
        data += chunk
    if len(data) < 8:
        return None, ""
    rid = struct.unpack("<i", data[:4])[0]
    return rid, data[8:-2].decode("utf-8", "replace")


def find_code(code, mc_id=None):
    """在日志尾部找 `<ID> wiki 1234`。返回玩家名或 None。"""
    text = _tail_text(mc_config()["log"])
    if not text:
        return None
    for line in reversed(text.splitlines()):
        if "INFO" not in line:
            continue
        m = CHAT_RE.search(line)
        if not m:
            continue
        if m.group(2) != code:
            continue
        name = m.group(1).strip()
        if mc_id and name.lower() != mc_id.lower():
            continue
        return name
    return None


def recent_joins(limit=20):
    """日志里最近进服的人，用于绑定页给个提示。"""
    text = _tail_text(mc_config()["log"], 256 * 1024)
    out = []
    for m in JOIN_RE.finditer(text):
        n = m.group(1)
        if n not in out:
            out.append(n)
    return out[-limit:][::-1]


# ------------------------------------------------------------------ 绑定码

def _load_binds():
    try:
        with open(BIND_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_binds(d):
    now = time.time()
    d = {k: v for k, v in d.items() if v.get("exp", 0) > now}
    os.makedirs(DATA, exist_ok=True)
    tmp = BIND_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    os.replace(tmp, BIND_FILE)


def new_bind(mc_id):
    d = _load_binds()
    code = None
    used = {v["code"] for v in d.values()}
    for _ in range(200):
        c = "%04d" % secrets.randbelow(10000)
        if c not in used:
            code = c
            break
    if not code:
        code = "%04d" % secrets.randbelow(10000)
    token = secrets.token_urlsafe(16)
    d[token] = {"mc": mc_id, "code": code,
                "exp": time.time() + CODE_TTL, "created": time.time()}
    _save_binds(d)
    return token, code


def get_bind(token):
    d = _load_binds()
    b = d.get(token)
    if not b or b["exp"] < time.time():
        return None
    return b


def drop_bind(token):
    d = _load_binds()
    d.pop(token, None)
    _save_binds(d)


def bind_status(token):
    """返回 (状态, 玩家名)。状态：pending / ok / expired / none"""
    b = get_bind(token)
    if not b:
        return "none", None
    who = find_code(b["code"], b["mc"])
    if who:
        d = _load_binds()
        if token in d:
            d[token]["exp"] = time.time() + 900
            _save_binds(d)
        return "ok", who
    return "pending", b["mc"]


def reset():
    """管理员重建绑定文件时用。"""
    _save_binds({})
