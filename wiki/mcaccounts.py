"""用服务器的游戏账号登录 Wiki。

1.20.1 服装了 EasyAuth（离线服认证插件），账号存在
  <服务端>/EasyAuth/easyauth.db   （SQLite，表 easyauth，密码是 BCrypt）
所以 Wiki 不再自己发密码：直接拿「游戏 ID + 进服密码」去校验。

BCrypt 用 vendor/ 里的 bcrypt 扩展（pip install bcrypt --target vendor）。
没装也能跑，只是无法校验密码，登录页会提示找服主。

只读打开数据库，mode=ro，绝不写回，避免和正在运行的服务器抢锁。
"""

import hashlib
import json
import os
import sqlite3
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
MC_FILE = os.path.join(DATA, "mc.json")
VENDOR = os.path.join(ROOT, "vendor")

if os.path.isdir(VENDOR) and VENDOR not in sys.path:
    sys.path.append(VENDOR)

try:
    import bcrypt
    BCRYPT_OK = True
except Exception:                                    # 没装扩展也能启动网站
    bcrypt = None
    BCRYPT_OK = False

DEFAULT_DB = "E:/server/EasyAuth/easyauth.db"
_CACHE = {"path": None, "mtime": 0, "count": 0, "ts": 0}


# ------------------------------------------------------------------ 配置

def config():
    try:
        with open(MC_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def db_path():
    # WIKI_EASYAUTH_DB 只在自测/临时切库时用，正常读 data/mc.json
    p = os.environ.get("WIKI_EASYAUTH_DB") or config().get("easyauth_db") or DEFAULT_DB
    return p.strip() or DEFAULT_DB


def ok():
    """账号库可用吗（文件在 + 有 bcrypt）"""
    return os.path.isfile(db_path()) and BCRYPT_OK


def admin_ids():
    """服主 ID：这些账号登录后自动是 Wiki 管理员。"""
    ids = config().get("wiki_admins") or []
    if isinstance(ids, str):
        ids = [ids]
    return [str(x).strip().lower() for x in ids if str(x).strip()]


# ------------------------------------------------------------------ 查询

def _connect():
    p = db_path()
    if not os.path.isfile(p):
        raise FileNotFoundError(p)
    uri = "file:///" + p.replace("\\", "/").lstrip("/") + "?mode=ro"
    return sqlite3.connect(uri, uri=True, timeout=2.0)


def find(username):
    """按游戏 ID 查账号（大小写不敏感）。找不到返回 None。"""
    name = (username or "").strip()
    if not name:
        return None
    try:
        with _connect() as c:
            row = c.execute(
                "SELECT username, uuid, data FROM easyauth WHERE username_lower = ? LIMIT 1",
                (name.lower(),)).fetchone()
            if not row:
                row = c.execute(
                    "SELECT username, uuid, data FROM easyauth WHERE username = ? LIMIT 1",
                    (name,)).fetchone()
    except FileNotFoundError:
        return None
    except sqlite3.Error:
        return None
    if not row:
        return None
    try:
        meta = json.loads(row[2] or "{}")
    except ValueError:
        meta = {}
    return {
        "username": row[0],
        "uuid": row[1] or "",
        "hash": meta.get("password") or "",
        "registered": meta.get("registration_date") or "",
        "last_auth": meta.get("last_authenticated_date") or "",
    }


def _check_bcrypt(password, hashed):
    h = hashed.strip()
    if h.startswith("$2y$"):                        # PHP 风格的 2y 当 2b 处理
        h = "$2b$" + h[4:]
    try:
        pw = password.encode("utf-8")
    except Exception:
        return False
    if len(pw) > 72:                                # bcrypt 只吃前 72 字节
        pw = pw[:72]
    try:
        return bool(bcrypt.checkpw(pw, h.encode("utf-8")))
    except (ValueError, TypeError):
        return False


def verify(username, password):
    """校验游戏密码。

    返回 (account|None, reason)，reason: ok / no_user / bad_pw / no_db / no_bcrypt。
    """
    if not BCRYPT_OK:
        return None, "no_bcrypt"
    if not os.path.isfile(db_path()):
        return None, "no_db"
    acct = find(username)
    if not acct:
        return None, "no_user"
    h = acct["hash"]
    if not h:
        return None, "bad_pw"
    if h.startswith("$2"):
        good = _check_bcrypt(password, h)
    else:
        # 极老版本可能存明文 / 十六进制摘要，能认就认，认不出当密码错
        low = h.lower()
        good = (low == hashlib.sha256(password.encode("utf-8")).hexdigest()
                or low == hashlib.md5(password.encode("utf-8")).hexdigest()
                or h == password)
    if not good:
        return None, "bad_pw"
    return acct, "ok"


def summary():
    """给管理员页面显示：账号数、库文件时间、bcrypt 是否可用。"""
    p = db_path()
    info = {"path": p, "exists": os.path.isfile(p), "bcrypt": BCRYPT_OK,
            "count": 0, "mtime": "", "error": ""}
    if not info["exists"]:
        info["error"] = "找不到账号库文件"
        return info
    try:
        st = os.stat(p)
        info["mtime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))
        with _connect() as c:
            info["count"] = c.execute("SELECT COUNT(*) FROM easyauth").fetchone()[0]
    except Exception as e:
        info["error"] = str(e)
    return info
