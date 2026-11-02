#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赤物语服务器 Wiki —— 单文件本地知识库

浏览不需要登录：游客能看所有 player 级页面、能搜索，只是不能留言。
登录用的是 1.20.1 服 EasyAuth 的游戏密码（见 mcaccounts.py）。

依赖: Python 3 标准库 + vendor/bcrypt（只用于校验游戏密码）。

目录结构:
  app.py            本文件
  mcaccounts.py     读 EasyAuth 账号库校验游戏密码
  data/users.json   账号（Wiki 自己的称号 / 权限组；EasyAuth 账号登录时自动建档）
  data/pages/*.md   内容页面，frontmatter 控制标题与权限
  static/style.css  样式（MediaWiki / Minecraft Wiki 风格）

Markdown 扩展:
  [[slug]] / [[slug|文字]]    站内链接（目标不存在时显示为红链）
  ::: infobox 标题 / | 键 | 值 / :::     右侧信息框
  ::: tip|note|warn 标题 ... :::         提示框（ambox）
"""

import hashlib
import html
import json
import os
import re
import secrets
import socket
import sys
import threading
import time
import urllib.parse
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import mcauth
import mcaccounts
import social

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE_DIR = os.path.join(ROOT, "data", "pages")
USER_FILE = os.path.join(ROOT, "data", "users.json")
GROUP_FILE = os.path.join(ROOT, "data", "groups.json")
CSS_FILE = os.path.join(ROOT, "static", "style.css")

SESSIONS = {}
LOCK = threading.Lock()
SESSION_TTL = 60 * 60 * 12

# 未登录访客也当成一种「用户」传下去，模板里就不用到处判 None
GUEST = {"name": "", "role": "guest", "display": "游客", "groups": ["guest", "player"],
         "title": "", "guest": True}

LOGIN_FAIL = {}          # ip -> [失败时间戳]，防爆破
FAIL_WINDOW = 10 * 60
FAIL_MAX = 10


def is_guest(user):
    return not user or bool(user.get("guest")) or user.get("role") == "guest"


# ---------------------------------------------------------------- 账号 / 会话

def load_users():
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["users"]


def hash_pw(password, salt):
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def user_groups(u):
    """账号所属的可见组。老账号没写 groups 时按 role 推。"""
    g = u.get("groups")
    if g:
        return list(g)
    return ["admin", "player"] if u.get("role") == "admin" else ["player"]


def find_user(username):
    """先精确匹配，再忽略大小写（MC ID 大小写玩家常记错）。"""
    users = load_users()
    if username in users:
        return username, users[username]
    low = username.lower()
    for k, v in users.items():
        if k.lower() == low:
            return k, v
    return None, None


def user_dict(name, u):
    return {"name": name, "role": u.get("role", "player"),
            "display": u.get("display") or name,
            "groups": user_groups(u), "title": u.get("title", "")}


def check_login(username, password):
    """Wiki 自己的密码：管理员手动开的号，或早期用验证码绑定过的号。"""
    name, u = find_user(username)
    if not u or not u.get("hash") or not u.get("salt"):
        return None
    if secrets.compare_digest(hash_pw(password, u["salt"]), u["hash"]):
        return user_dict(name, u)
    return None


def ensure_wiki_account(acct):
    """EasyAuth 校验通过后，确保 Wiki 里有对应账号（没有就按玩家建）。

    Wiki 只存称号和权限组，密码永远以 EasyAuth 为准，不往这里写。
    """
    users = load_users()
    name, u = find_user(acct["username"])
    want_admin = acct["username"].lower() in mcaccounts.admin_ids()
    now = time.strftime("%Y-%m-%d %H:%M")
    if u is None:
        groups = ["admin", "player"] if want_admin else ["player"]
        u = {"role": "admin" if want_admin else "player",
             "display": acct["username"], "title": "", "groups": groups,
             "uuid": acct["uuid"], "source": "easyauth", "created": now,
             "last_login": now}
        users[acct["username"]] = u
        save_users(users)
        return user_dict(acct["username"], u)

    changed = False
    if acct["uuid"] and u.get("uuid") != acct["uuid"]:
        u["uuid"] = acct["uuid"]
        changed = True
    if u.get("source") != "easyauth":
        u["source"] = "easyauth"
        changed = True
    if want_admin and u.get("role") != "admin":
        u["role"] = "admin"
        u["groups"] = ["admin", "player"] + [g for g in user_groups(u)
                                             if g not in ("admin", "player")]
        changed = True
    u["last_login"] = now
    if changed:
        users[name] = u
        save_users(users)
    return user_dict(name, u)


def do_login(username, password):
    """返回 (user, err)。先查游戏账号库，再退回 Wiki 本地密码。"""
    username = (username or "").strip()
    if not username or not password:
        return None, "游戏 ID 和密码都要填。"
    acct, why = mcaccounts.verify(username, password)
    if acct:
        return ensure_wiki_account(acct), ""
    local = check_login(username, password)
    if local:
        return local, ""
    if why == "no_bcrypt":
        return None, "Wiki 缺少 bcrypt 组件（vendor 目录不见了），暂时无法校验游戏密码，找服主。"
    if why == "no_db":
        return None, "读不到服务器账号库（EasyAuth），找服主确认 data/mc.json 里的路径。"
    if why == "no_user":
        return None, "服务器账号库里没有「%s」这个 ID。第一次进服要先在游戏里注册。" % username
    return None, "密码不对。Wiki 用的是你进服时的那个密码。"


def fail_blocked(ip):
    now = time.time()
    with LOCK:
        arr = [t for t in LOGIN_FAIL.get(ip, []) if now - t < FAIL_WINDOW]
        LOGIN_FAIL[ip] = arr
        return len(arr) >= FAIL_MAX


def note_fail(ip):
    with LOCK:
        LOGIN_FAIL.setdefault(ip, []).append(time.time())
        if len(LOGIN_FAIL[ip]) > FAIL_MAX * 2:
            LOGIN_FAIL[ip] = LOGIN_FAIL[ip][-FAIL_MAX:]


def load_groups():
    """可见组表：id -> 显示名。文件缺失时退回内置两组。"""
    try:
        with open(GROUP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {g["id"]: g.get("label", g["id"]) for g in data["groups"]}
    except Exception:
        return {"player": "玩家", "admin": "管理员"}


def group_label(gid):
    return load_groups().get(gid, gid)


def page_groups(page):
    """frontmatter 的 role 支持逗号分隔多个组：role: builder,staff"""
    return [g for g in re.split(r"[,;\s]+", (page.get("role") or "player")) if g]


def can_view(user, page):
    """可见性：

    player  —— 所有人，包括没登录的游客
    login   —— 登录后才可见（游客看不到）
    admin   —— 管理员全见；其他人看组是否匹配
    """
    need = page_groups(page)
    if "player" in need:
        return True
    if is_guest(user):
        return False
    if "login" in need:
        return True
    if user.get("role") == "admin":
        return True
    return bool(set(user.get("groups") or []) & set(need))


def role_label(role):
    """role 可能是多组，标签也拼起来。"""
    return "、".join(group_label(g) for g in re.split(r"[,;\s]+", role or "player") if g)


def new_session(user):
    token = secrets.token_urlsafe(24)
    with LOCK:
        SESSIONS[token] = {"user": user, "ts": time.time()}
    return token


def get_session(handler):
    cookie = SimpleCookie()
    raw = handler.headers.get("Cookie")
    if not raw:
        return None
    try:
        cookie.load(raw)
    except Exception:
        return None
    morsel = cookie.get("sid")
    if not morsel:
        return None
    token = morsel.value
    with LOCK:
        sess = SESSIONS.get(token)
        if not sess:
            return None
        if time.time() - sess["ts"] > SESSION_TTL:
            SESSIONS.pop(token, None)
            return None
        sess["ts"] = time.time()
        return sess["user"]


# ---------------------------------------------------------------- 页面数据

FRONT_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def parse_page(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    meta, body = {}, raw
    m = FRONT_RE.match(raw)
    if m:
        for line in m.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = raw[m.end():]
    meta.setdefault("title", os.path.splitext(os.path.basename(path))[0])
    meta.setdefault("role", "player")
    meta.setdefault("group", "玩家指南")
    meta.setdefault("order", "99")
    try:
        meta["order"] = int(meta["order"])
    except ValueError:
        meta["order"] = 99
    meta["slug"] = os.path.splitext(os.path.basename(path))[0]
    meta["raw"] = raw
    meta["body"] = body
    meta["mtime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(path)))
    _lt = time.localtime(os.path.getmtime(path))
    _wd = "一二三四五六日"[_lt.tm_wday]
    meta["mtime_human"] = time.strftime("%Y年%m月%d日", _lt) + " (星期%s) " % _wd + time.strftime("%H:%M", _lt)
    return meta


def load_all():
    pages = []
    if not os.path.isdir(PAGE_DIR):
        return pages
    for name in sorted(os.listdir(PAGE_DIR)):
        if name.endswith(".md"):
            try:
                pages.append(parse_page(os.path.join(PAGE_DIR, name)))
            except Exception:
                pass
    pages.sort(key=lambda p: (p["group"], p["order"], p["title"]))
    return pages


# ---------------------------------------------------------------- 待拍板收件箱
# 自动队列把「必须由服主本人决定」的事写进 decisions 页面，服主在 wiki 编辑器里
# 直接改「拍板：」那一行；队列下一轮读到就照办。写入口只有这一条，且只动
# 「## 待处理 / ## 已定」两个小节，页面其它内容一个字都不碰。

DECISION_SLUG = "decisions"
INBOX_TOKEN_FILE = os.path.join(ROOT, "data", "inbox_token")
INBOX_KEY_RE = re.compile(r"<!--\s*inbox:key=([^\s>]+)\s*-->")
PENDING_HEAD = "\n## 待处理"
DONE_HEAD = "\n## 已定"
EMPTY_MARK = "（暂无）"


def _inbox_path():
    return os.path.join(PAGE_DIR, DECISION_SLUG + ".md")


def _inbox_token():
    try:
        with open(INBOX_TOKEN_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def _inbox_sections(raw):
    """切出 (页面前置, 待处理区, 已定区到文件尾)。结构不符返回 None。"""
    i1 = raw.find(PENDING_HEAD)
    i2 = raw.find(DONE_HEAD)
    if i1 < 0 or i2 < 0 or i2 < i1:
        return None
    return raw[:i1], raw[i1:i2], raw[i2:]


def _drop_empty_mark(section):
    return re.sub(r"(?m)^" + EMPTY_MARK + r"[ \t]*\n?", "", section)


def _inbox_write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def inbox_items():
    """读出两个小节里的所有条目，给 /api/inbox 列表和人工排查用。"""
    path = _inbox_path()
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError:
        return []
    parts = _inbox_sections(raw)
    if not parts:
        return []
    items = []
    for section, status in ((parts[1], "open"), (parts[2], "done")):
        for chunk in re.split(r"(?m)^### ", section)[1:]:
            chunk = chunk.rstrip()
            if not chunk:
                continue
            lines = chunk.split("\n")
            fields = {}
            for ln in lines[1:]:
                m = re.match(r"-\s*([^：:]{1,6})[：:]\s*(.*)$", ln)
                if m:
                    fields[m.group(1).strip()] = m.group(2).strip()
            km = INBOX_KEY_RE.search(chunk)
            items.append({
                "status": status,
                "title": lines[0].strip(),
                "key": km.group(1) if km else "",
                "queue": fields.get("队列", ""),
                "time": fields.get("时间", ""),
                "question": fields.get("问题", ""),
                "options": fields.get("选项", ""),
                "default": fields.get("默认", ""),
                "decision": fields.get("拍板", ""),
                "archived": fields.get("归档", ""),
            })
    return items


def inbox_add(item):
    """追加一条待拍板。返回 (ok, msg, key)。"""
    path = _inbox_path()
    if not os.path.isfile(path):
        return False, "缺少 decisions 页面：" + path, ""
    title = str(item.get("title") or "").strip()
    if not title:
        return False, "title 不能为空", ""
    queue = str(item.get("queue") or "").strip() or "未知队列"
    key = str(item.get("key") or "").strip()
    if not key:
        tag = re.sub(r"[^A-Za-z0-9]+", "", queue.split("·")[0]) or "Q"
        key = "%s-%s" % (tag, time.strftime("%Y%m%d-%H%M%S"))
    with LOCK:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        if key in INBOX_KEY_RE.findall(raw):
            return True, "已存在，跳过", key
        parts = _inbox_sections(raw)
        if not parts:
            return False, "decisions 页面缺少「## 待处理 / ## 已定」小节", ""
        pre, pending, done = parts
        def _one(v):
            return [v] if isinstance(v, str) else list(v or [])
        lines = ["", "### %s · %s" % (key, title),
                 "- 队列：%s" % queue,
                 "- 时间：%s" % time.strftime("%Y-%m-%d %H:%M")]
        q = str(item.get("question") or "").strip()
        if q:
            lines.append("- 问题：" + q.replace("\n", " "))
        opts = [str(o).replace("\n", " ").strip() for o in _one(item.get("options")) if str(o).strip()]
        if opts:
            lines.append("- 选项：" + " ／ ".join(opts))
        lines.append("- 默认：%s" % (str(item.get("default") or "").strip() or "不拍板就什么都不做"))
        links = [str(l).strip() for l in _one(item.get("links")) if str(l).strip()]
        if links:
            lines.append("- 相关：" + " ".join("[[%s]]" % l for l in links))
        lines.append("- 拍板：_待填_")
        lines.append("<!-- inbox:key=%s -->" % key)
        pending = _drop_empty_mark(pending).rstrip("\n") + "\n" + "\n".join(lines) + "\n"
        _inbox_write(path, pre + pending + "\n" + done.lstrip("\n"))
    return True, "已写入", key


def inbox_resolve(key, note, by=""):
    """把某条从「待处理」挪到「已定」，并写死结论。返回 (ok, msg, key)。"""
    path = _inbox_path()
    if not os.path.isfile(path):
        return False, "缺少 decisions 页面", ""
    note = (note or "").strip() or "（未写结论）"
    with LOCK:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        pat = (r"(?ms)^### [^\n]*\n(?:(?!^### |^## ).*\n)*?"
               + re.escape("<!-- inbox:key=%s -->" % key) + r"[^\n]*\n")
        m = re.search(pat, raw)
        if not m:
            return False, "没有这条待拍板", ""
        block = m.group(0)
        raw = raw[:m.start()] + raw[m.end():]
        if "- 拍板：_待填_" in block:
            block = block.replace("- 拍板：_待填_", "- 拍板：" + note, 1)
        else:
            block = block.rstrip("\n") + "\n- 拍板：" + note + "\n"
        arch = "- 归档：%s%s\n" % (time.strftime("%Y-%m-%d %H:%M"),
                                  (" · " + by) if by else "")
        block = block.rstrip("\n") + "\n"
        i = block.find("<!-- inbox:key=")
        block = (block[:i] + arch + block[i:]) if i >= 0 else (block + arch)
        parts = _inbox_sections(raw)
        if not parts:
            return False, "decisions 页面结构被破坏", ""
        pre, pending, done = parts
        raw2 = (pre + pending.rstrip("\n") + "\n\n"
                + _drop_empty_mark(done).rstrip("\n") + "\n\n" + block)
        _inbox_write(path, raw2)
    return True, "已归档", key


# ---------------------------------------------------------------- Markdown

class MD:
    """极简 Markdown 渲染器（MediaWiki 风格输出）。"""

    def __init__(self, titles=None, slug=None, can_edit=False):
        self.titles = titles or {}
        self.slug = slug
        self.can_edit = can_edit
        self.headings = []       # [(level, anchor, text)]
        self._used = {}

    # ---------- 行内 ----------
    def inline(self, s):
        s = html.escape(s)

        def wl(m):
            target = m.group(1).strip()
            label = (m.group(2) or target).strip()
            title = self.titles.get(target)
            if title is None:
                return '<a class="new" href="/p/%s" title="该页面尚未创建">%s</a>' % (
                    urllib.parse.quote(target), label)
            return '<a href="/p/%s" title="%s">%s</a>' % (
                urllib.parse.quote(target), html.escape(title), label)

        s = re.sub(r"\[\[([^\]|\n]+?)(?:\|([^\]\n]+?))?\]\]", wl, s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)

        def ml(m):
            text, url = m.group(1), m.group(2)
            if url.startswith("http"):
                return '<a class="extlink" href="%s" target="_blank" rel="noopener">%s</a>' % (url, text)
            return '<a href="%s">%s</a>' % (url, text)

        s = re.sub(r"\[([^\]\n]+)\]\(([^)\s]+)\)", ml, s)
        return s

    # ---------- 锚点 ----------
    def anchor(self, text):
        base = re.sub(r"<[^>]+>", "", text)
        base = re.sub(r"\s+", "-", base.strip())
        base = re.sub(r"[^\w\-.]+", "", base) or "section"
        n = self._used.get(base, 0) + 1
        self._used[base] = n
        return base if n == 1 else "%s-%d" % (base, n)

    # ---------- 列表 ----------
    def render_list(self, items):
        out, stack = [], []
        for indent, ordered, text in items:
            tag = "ol" if ordered else "ul"
            while stack and indent < stack[-1][0]:
                out.append("</li></%s>" % stack.pop()[1])
            if not stack or indent > stack[-1][0]:
                out.append("<%s>" % tag)
                stack.append((indent, tag))
                out.append("<li>" + self.inline(text))
            else:
                out.append("</li><li>" + self.inline(text))
        while stack:
            out.append("</li></%s>" % stack.pop()[1])
        return "".join(out)

    # ---------- 块 ----------
    def heading(self, level, text):
        inner = self.inline(text)
        aid = self.anchor(text)
        self.headings.append((level, aid, re.sub(r"<[^>]+>", "", inner)))
        edit = ""
        if self.can_edit and self.slug and level <= 3:
            edit = ' <span class="editsection">[<a href="/edit/%s" title="编辑本页">编辑</a>]</span>' % self.slug
        return '<h%d id="%s">%s%s</h%d>' % (level, aid, inner, edit, level)

    def container(self, kw, arg, body_lines):
        if kw == "infobox":
            rows = []
            for ln in body_lines:
                ln = ln.strip()
                if not ln.startswith("|"):
                    continue
                cells = [c.strip() for c in ln.strip("|").split("|")]
                k = cells[0] if cells else ""
                v = cells[1] if len(cells) > 1 else ""
                rows.append(
                    '<tr><th class="ib-key">%s</th><td class="ib-val">%s</td></tr>'
                    % (self.inline(k), self.inline(v)))
            title = ('<tr><td colspan="2" class="ib-title">%s</td></tr>'
                     % self.inline(arg)) if arg else ""
            return '<table class="infobox">%s%s</table>' % (
                title if title else "", "".join(rows))

        cls = kw if kw in ("tip", "note", "warn") else "note"
        head = ('<span class="ab-title">%s</span>' % self.inline(arg)) if arg else ""
        body = "".join("<p>%s</p>" % self.inline(ln.strip())
                       for ln in body_lines if ln.strip())
        return '<div class="ambox %s">%s%s</div>' % (cls, head, body)

    def render(self, md):
        # 注释标记（S5 自动生成的页面用 <!-- auto:begin/end --> 圈定范围）不进正文
        md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
        lines = md.split("\n")
        out, i = [], 0
        while i < len(lines):
            line = lines[i]

            # 代码块
            if line.startswith("```"):
                i += 1
                buf = []
                while i < len(lines) and not lines[i].startswith("```"):
                    buf.append(lines[i])
                    i += 1
                i += 1
                out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(buf)))
                continue

            # ::: 容器
            if line.startswith(":::"):
                head = line[3:].strip()
                parts = head.split(None, 1)
                kw = parts[0] if parts else ""
                arg = parts[1] if len(parts) > 1 else ""
                i += 1
                buf = []
                while i < len(lines) and not lines[i].startswith(":::"):
                    buf.append(lines[i])
                    i += 1
                i += 1
                out.append(self.container(kw, arg, buf))
                continue

            # 表格
            if line.startswith("|") and i + 1 < len(lines) and re.match(
                    r"^\|[\s:|-]+\|?\s*$", lines[i + 1].strip()):
                header = [c.strip() for c in line.strip().strip("|").split("|")]
                i += 2
                rows = []
                while i < len(lines) and lines[i].startswith("|"):
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                    i += 1
                t = ['<div class="tablewrap"><table class="wikitable"><thead><tr>']
                t += ["<th>%s</th>" % self.inline(c) for c in header]
                t.append("</tr></thead><tbody>")
                for r in rows:
                    t.append("<tr>" + "".join("<td>%s</td>" % self.inline(c) for c in r) + "</tr>")
                t.append("</tbody></table></div>")
                out.append("".join(t))
                continue

            # 标题
            m = re.match(r"^(#{1,6})\s+(.*)$", line)
            if m:
                out.append(self.heading(len(m.group(1)), m.group(2)))
                i += 1
                continue

            # 列表
            if re.match(r"^\s*([-*]|\d+\.)\s+", line):
                items = []
                while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                    mm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                    items.append((len(mm.group(1)), mm.group(2)[0].isdigit(), mm.group(3)))
                    i += 1
                out.append(self.render_list(items))
                continue

            # 分隔线
            if line.strip() in ("---", "***", "___"):
                out.append("<hr>")
                i += 1
                continue

            # 原始 HTML
            if line.lstrip().startswith("<"):
                buf = []
                while i < len(lines) and lines[i].strip():
                    buf.append(lines[i])
                    i += 1
                out.append("\n".join(buf))
                continue

            # 引用
            if line.startswith(">"):
                buf = []
                while i < len(lines) and lines[i].startswith(">"):
                    buf.append(lines[i].lstrip(">").strip())
                    i += 1
                out.append("<blockquote><p>%s</p></blockquote>" % self.inline(" ".join(buf)))
                continue

            if line.strip() == "":
                i += 1
                continue

            # 段落
            buf = []
            while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#{1,6}\s|```|:::|\||>|\s*[-*]\s|\s*\d+\.\s|---$)", lines[i]
            ):
                buf.append(lines[i].strip())
                i += 1
            out.append("<p>%s</p>" % self.inline(" ".join(buf)))

        return "\n".join(out)


def render_toc(heads):
    """把标题列表渲染成 MediaWiki 风格的目录框。"""
    heads = [h for h in heads if h[0] <= 3]
    if len(heads) < 3:
        return ""
    res = ['<div class="toc"><div class="toc-title">目录</div><ol>']
    li_open = sub_open = False
    for lv, aid, text in heads:
        if lv <= 2:
            if sub_open:
                res.append("</ol></li>")
                sub_open = False
            if li_open:
                res.append("</li>")
            res.append('<li><a href="#%s">%s</a>' % (aid, text))
            li_open = True
        else:
            if not sub_open:
                res.append('<ol class="toc-sub">')
                sub_open = True
            res.append('<li><a href="#%s">%s</a></li>' % (aid, text))
    if sub_open:
        res.append("</ol></li>")
    elif li_open:
        res.append("</li>")
    res.append("</ol></div>")
    return "".join(res)


# ---------------------------------------------------------------- 页面模板

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='3' fill='%233c7a2e'/%3E"
           "%3Crect x='4' y='4' width='24' height='24' fill='none' stroke='%23245a1b' stroke-width='2'/%3E"
           "%3C/svg%3E")


def shell(user, title, body, pages, slug=None, group=None, mtime=None, tabs=True, heading=None,
          query="", tool="", tab_active="page"):
    nav = []
    groups = {}
    for p in pages:
        if str(p.get("nav", "")).lower() in ("no", "false", "0"):
            continue
        if not can_view(user, p):
            continue
        groups.setdefault(p["group"], []).append(p)

    for gname in groups:
        nav.append('<div class="side-head">%s</div>' % html.escape(gname))
        for p in groups[gname]:
            lock = ""
            _pg = set(page_groups(p))
            _lb = role_label(p["role"]) if not (_pg & {"player", "login"}) else ""
            if _lb:
                lock = '<span class="lock" title="仅%s可见">%s</span>' % (
                    html.escape(_lb), html.escape(_lb[:1]))
            active = " active" if p["slug"] == slug else ""
            nav.append(
                '<a class="side-link%s" href="/p/%s">%s%s</a>'
                % (active, p["slug"], html.escape(p["title"]), lock)
            )

    nav.append('<div class="side-head">互动</div>')
    nav.append('<a class="side-link%s" href="/feedback">意见箱<span class="side-n">%d</span></a>'
               % (" active" if tool == "feedback" else "", social.open_feedback_count()))

    nav.append('<div class="side-head">工具</div>')
    nav.append('<a class="side-link%s" href="/search">搜索页面</a>'
               % (" active" if tool == "search" else ""))
    if user and user["role"] == "admin":
        nav.append('<a class="side-link%s" href="/new">新建页面</a>'
                   % (" active" if tool == "new" else ""))
        nav.append('<a class="side-link%s" href="/pages">页面管理</a>'
                   % (" active" if tool == "pages" else ""))
        nav.append('<a class="side-link%s" href="/users">账号与称号</a>'
                   % (" active" if tool == "users" else ""))
        nav.append('<a class="side-link%s" href="/groups">权限组</a>'
                   % (" active" if tool == "groups" else ""))

    if is_guest(user):
        nav.append('<div class="side-head">账号</div>')
        nav.append('<a class="side-link" href="/login">登录后可以留言</a>')
        who = ('<span class="who-guest">未登录访客</span>'
               '<a class="btn" href="/login">登录</a>')
    else:
        _t = user.get("title") or ""
        _badge = ('<span class="who-title">%s</span>' % html.escape(_t)) if _t else ""
        who = ('<span class="who">%s<b>%s</b> · %s</span>'
               '<a class="btn" href="/logout">退出</a>') % (
            _badge, html.escape(user["display"]),
            "管理员" if user["role"] == "admin" else "玩家")

    # 标签栏
    tab_bar = ""
    if tabs:
        edit_tab = ""
        if user and user["role"] == "admin" and slug:
            edit_tab = '<a class="tab" href="/edit/%s">编辑</a>' % slug
        if slug:
            n_cm = social.page_comment_count(slug)
            cm_n = '<span class="tab-n">%d</span>' % n_cm if n_cm else ""
            read_cls = " active" if tab_active == "page" else ""
            talk_cls = " active" if tab_active == "discuss" else ""
            tab_bar = """<div class="tabs">
  <div class="set">
    <a class="tab%s" href="/p/%s">页面</a>
    <a class="tab%s" href="/discuss/%s">讨论%s</a>
  </div>
  <div class="set">
    <a class="tab%s" href="/p/%s">阅读</a>
    %s
    <span class="tab disabled">历史</span>
  </div>
</div>""" % (read_cls, slug, talk_cls, slug, cm_n, read_cls, slug, edit_tab)
        else:
            tab_bar = """<div class="tabs">
  <div class="set"><a class="tab active" href="#">页面</a><span class="tab disabled">讨论</span></div>
</div>"""

    foot = ""
    if slug:
        foot = '<div class="page-footer">本页面最后修订于 %s。' % html.escape(mtime or "")
        if user and user["role"] == "admin":
            foot += ' <a href="/edit/%s">编辑本页</a> ·' % slug
        foot += " 除非另有说明，本站内容采用 CC BY-NC-SA 4.0 协议授权。</div>"
        _n = social.page_comment_count(slug)
        foot += ('<div class="talk-note">对本页有疑问或补充？'
                 '<a href="/discuss/%s">去讨论区</a>%s</div>'
                 % (slug, "（已有 %d 条留言）" % _n if _n else ""))
        if group:
            foot += '<div class="catlinks">分类：<a href="/p/index">%s</a></div>' % html.escape(group)

    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s - 赤物语 Wiki</title>
<link rel="icon" href="%(favicon)s">
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header class="site-header">
  <a class="brand" href="/p/index">
    <span class="logo">赤</span>
    <span class="brand-text"><b>赤物语</b><small>WIKI</small></span>
  </a>
  <form class="search-wrap" method="get" action="/search">
    <input id="q" name="q" placeholder="搜索赤物语Wiki" autocomplete="off" value="%(query)s">
  </form>
  <div class="userbox">%(who)s</div>
</header>
<div class="wrap">
  <aside class="sidebar">
    %(nav)s
  </aside>
  <div class="content-col">
    %(tabs)s
    <article class="article%(artcls)s">
      <div class="site-sub">出自 赤物语 Wiki</div>
      <h1>%(heading)s</h1>
      %(body)s
      %(foot)s
    </article>
  </div>
</div>

</body>
</html>""" % {
        "title": html.escape(title),
        "heading": html.escape(heading or title),
        "favicon": FAVICON,
        "who": who,
        "nav": "\n    ".join(nav),
        "tabs": tab_bar,
        "artcls": "" if tabs else " notabs",
        "query": html.escape(query),
        "body": body,
        "foot": foot,
    }


def _lg_shell(inner, tab="pw"):
    """登录 / 绑定共用的卡片外壳。"""
    t_pw = " active" if tab == "pw" else ""
    t_bind = " active" if tab == "bind" else ""
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>登录 - 赤物语 Wiki</title>
<link rel="icon" href="{fav}">
<link rel="stylesheet" href="/static/style.css"></head>
<body class="login-body">
<div class="login">
  <div class="lg-head">
    <span class="logo">赤</span>
    <div><h1>赤物语 Wiki</h1><p class="sub">服务器内部知识库</p></div>
  </div>
  <div class="lg-tabs">
    <a class="lg-tab{t_pw}" href="/login">游戏密码登录</a>
    <a class="lg-tab{t_bind}" href="/login?tab=bind">没有密码？用验证码</a>
  </div>
  <div class="lg-body">{inner}</div>
</div>
</body></html>""".format(fav=FAVICON, t_pw=t_pw, t_bind=t_bind, inner=inner)


def login_page(err="", tab="pw", u="", nxt=""):
    e = '<p class="err">%s</p>' % html.escape(err) if err else ""
    form = """{e}
<form class="lg-form" method="post" action="/login">
  <input type="hidden" name="next" value="{nxt}">
  <label>游戏 ID<input name="u" value="{u}" autofocus autocomplete="username"
    placeholder="就是你在服务器里的 ID"></label>
  <label>密码<input name="p" type="password" autocomplete="current-password"
    placeholder="进服务器时用的密码"></label>
  <button type="submit">登录</button>
</form>
<p class="lg-dim">密码和进服密码是同一个（1.20.1 服的 EasyAuth 账号），
Wiki 不另存密码。没登录也能随便翻页面、搜索，只是不能留言。</p>
<div class="lg-foot">没有游戏密码？点上面的「没有密码？用验证码」，在游戏里发一句话就能开号。</div>""".format(
        e=e, u=html.escape(u), nxt=html.escape(nxt or ""))
    return _lg_shell(form, "pw")


def bind_page(err="", mc="", hint=""):
    online = mcauth.server_online_players()
    if online is None:
        status = '<b class="off">服务器当前没有运行</b>，等服务器开了再来绑定。'
    elif online:
        status = "现在在线：<b>%s</b>" % "、".join(html.escape(x) for x in online[:12])
    else:
        status = "服务器开着，但没人在线。"
    recent = mcauth.recent_joins(8)
    if recent:
        status += '<span class="lg-dim">（最近进服：%s）</span>' % "、".join(
            html.escape(x) for x in recent[:6])
    e = '<p class="err">%s</p>' % html.escape(err) if err else ""
    h = '<p class="lg-help">%s</p>' % hint if hint else ""
    form = """{e}
<form class="lg-form" method="post" action="/bind">
  <label>你的游戏 ID<input name="mc" value="{mc}" autofocus maxlength="32"
    placeholder="和进服时的名字完全一致"></label>
  <button type="submit">获取验证码</button>
</form>
<p class="lg-status">{status}</p>
<div class="lg-steps">
  <b>怎么验证</b>
  <ol>
    <li>填好游戏 ID，点「获取验证码」</li>
    <li>得到一个 4 位数字，比如 <code>0417</code></li>
    <li>回到游戏，在聊天框里发 <code>wiki 0417</code></li>
    <li>网页会自动通过，然后让你设一个 Wiki 密码</li>
  </ol>
  <p class="lg-dim">这条是备用通道：适用于还没在 EasyAuth 注册、或忘了游戏密码的号。
  有游戏密码的话，直接用「游戏密码登录」更省事。</p>
</div>{h}""".format(e=e, mc=html.escape(mc), status=status, h=h)
    return _lg_shell(form, "bind")


def bind_wait_page(token, code, mc):
    inner = """<div class="bind-wait">
  <p class="lg-dim">这是给 <b>{mc}</b> 的验证码</p>
  <div class="bind-code">{code}</div>
  <p>回到游戏，在聊天框里发送：</p>
  <div class="bind-cmd">wiki {code}</div>
  <p class="lg-status" id="st">正在等待你在游戏里发言…</p>
  <p class="lg-dim">剩余 <span id="left">300</span> 秒。发完不用刷新，页面会自动跳转。</p>
</div>
<script>
var t = "{token}", left = 300;
function tick() {{
  fetch("/bind/check?t=" + encodeURIComponent(t)).then(function(r){{return r.json();}}).then(function(d){{
    if (d.state === "ok") {{
      document.getElementById("st").textContent = "验证通过，正在跳转…";
      location.href = "/bind/pw?t=" + encodeURIComponent(t);
      return;
    }}
    if (d.state === "used") {{ location.href = "/bind/pw?t=" + encodeURIComponent(t); return; }}
    if (d.state === "none") {{ document.getElementById("st").textContent = "验证码已过期，请重新获取。"; return; }}
    left -= 2;
    document.getElementById("left").textContent = left > 0 ? left : 0;
    if (left > 0) setTimeout(tick, 2000);
  }}).catch(function(){{ setTimeout(tick, 4000); }});
}}
tick();
</script>""".format(mc=html.escape(mc), code=code, token=html.escape(token))
    return _lg_shell(inner, "bind")


def bind_pw_page(token, mc, err=""):
    e = '<p class="err">%s</p>' % html.escape(err) if err else ""
    inner = """{e}
<p class="lg-help">验证通过：<b>{mc}</b>。给你的 Wiki 账号设一个密码（只用于这个网站）。</p>
<form class="lg-form" method="post" action="/bind/pw">
  <input type="hidden" name="t" value="{token}">
  <label>设置密码<input name="p1" type="password" autofocus minlength="6" autocomplete="new-password"></label>
  <label>再输一次<input name="p2" type="password" minlength="6" autocomplete="new-password"></label>
  <label>显示名（可不填）<input name="display" placeholder="默认用你的游戏 ID" maxlength="24"></label>
  <button type="submit">完成，进入 Wiki</button>
</form>
<p class="lg-dim">以后用「游戏 ID + 这个密码」登录。忘了密码找服主重置。</p>""".format(
        e=e, mc=html.escape(mc), token=html.escape(token))
    return _lg_shell(inner, "pw")


def token_status(token):
    return mcauth.bind_status(token)


# ---------------------------------------------------------------- 搜索 / 新建

def visible_pages(pages, user):
    return [p for p in pages if can_view(user, p)]


def plain_text(md):
    t = re.sub(r"^:::.*$", " ", md, flags=re.M)
    t = re.sub(r"[#>*`|\[\]()]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def snippet(md, q, width=60):
    text = plain_text(md)
    i = text.lower().find(q.lower())
    if i < 0:
        return html.escape(text[:width * 2]) + ("…" if len(text) > width * 2 else "")
    a, b = max(0, i - width), min(len(text), i + len(q) + width)
    frag = html.escape(text[a:b])
    eq = html.escape(q)
    frag = re.sub("(" + re.escape(eq) + ")", r"<mark>\1</mark>", frag, flags=re.I)
    return ("…" if a > 0 else "") + frag + ("…" if b < len(text) else "")


def search_body(user, pages, q):
    vis = visible_pages(pages, user)
    q = q.strip()
    if not q:
        rows = "".join(
            '<li><div class="rs-title"><a href="/p/%s">%s</a>'
            '<span class="rs-group">%s</span></div></li>'
            % (p["slug"], html.escape(p["title"]), html.escape(p["group"]))
            for p in vis)
        return ('<p class="hint">共 <b>%d</b> 个页面。在顶部输入关键词后回车，'
                '会搜索标题与全文。</p><ul class="results">%s</ul>' % (len(vis), rows))

    hits = []
    for p in vis:
        score = p["body"].lower().count(q.lower())
        if q.lower() in p["title"].lower():
            score += 20
        if score:
            hits.append((score, p))
    hits.sort(key=lambda x: (-x[0], x[1]["title"]))

    if not hits:
        return ('<p class="hint">没有找到包含 <b>%s</b> 的页面。换个词试试，'
                '或到 <a href="/search">全部页面</a> 里翻。</p>' % html.escape(q))

    rows = "".join(
        '<li><div class="rs-title"><a href="/p/%s">%s</a>'
        '<span class="rs-group">%s</span></div>'
        '<div class="rs-snip">%s</div></li>'
        % (p["slug"], html.escape(p["title"]), html.escape(p["group"]),
           snippet(p["body"], q))
        for score, p in hits)
    return ('<p class="hint">找到 <b>%d</b> 个页面（按相关度排序）。</p>'
            '<ul class="results">%s</ul>' % (len(hits), rows))


def new_page_body(user, pages, form=None, err=""):
    form = form or {}
    groups = sorted({p["group"] for p in pages})
    opts = "".join('<option value="%s">' % html.escape(g) for g in groups)
    e = '<p class="err">%s</p>' % html.escape(err) if err else ""
    cur = form.get("role", "player")
    ropts = "".join(
        '<option value="%s"%s>%s（%s）</option>'
        % (html.escape(gid), " selected" if gid == cur else "", html.escape(label), html.escape(gid))
        for gid, label in load_groups().items())
    return """%s
<form class="wikiform" method="post" action="/new">
  <table class="formtable">
    <tr><th>页面标题 *</th><td><input name="title" value="%s" autofocus>
      <div class="fhint">显示在左栏和文章大标题上，可以写中文。</div></td></tr>
    <tr><th>文件名（URL）*</th><td><input name="slug" value="%s" placeholder="例如 resource-world">
      <div class="fhint">只允许小写字母、数字、<code>-</code>、<code>_</code>，会变成 <code>/p/文件名</code>。</div></td></tr>
    <tr><th>分组</th><td><input name="group" value="%s" list="glist" placeholder="玩家指南">
      <datalist id="glist">%s</datalist>
      <div class="fhint">同名分组在左栏合并成一栏；写新名字就是新建一栏。</div></td></tr>
    <tr><th>排序</th><td><input name="order" type="number" value="%s" min="0" max="999" style="width:90px">
      <div class="fhint">同组内数字越小越靠前。</div></td></tr>
    <tr><th>可见权限</th><td>
      <select name="role">%s</select>
      <div class="fhint"><code>player</code> = 任何登录账号可见；其余是权限组，只有该组成员与管理员能看。
      组表在 <code>data/groups.json</code>，改完刷新即生效。</div></td></tr>
  </table>
  <div class="actions"><button type="submit">创建并开始编辑</button>
  <a class="btn" href="/search">取消</a></div>
</form>
<p class="hint">创建后会跳到编辑器，正文留空由你写。文件名不可重复。</p>""" % (
        e,
        html.escape(form.get("title", "")),
        html.escape(form.get("slug", "")),
        html.escape(form.get("group", "玩家指南")),
        opts,
        html.escape(str(form.get("order", "50"))),
        ropts,
    )


def pages_body(user, pages):
    """页面管理：一表看全部页面的可见组，就地改。"""
    gs = load_groups()
    counts = {}
    for p in pages:
        counts[p["role"]] = counts.get(p["role"], 0) + 1
    summary = " · ".join('%s <b>%d</b>' % (html.escape(gs.get(k, k)), v)
                         for k, v in sorted(counts.items()))
    cm = social.comments_count()
    rows = []
    for p in pages:
        opts = "".join(
            '<option value="%s"%s>%s</option>'
            % (html.escape(gid), " selected" if gid == p["role"] else "", html.escape(label))
            for gid, label in gs.items())
        auto = ' <span class="rs-group">自动</span>' if str(p.get("auto", "")) else ""
        rows.append(
            '<tr><td><a href="/p/%s">%s</a>%s</td><td><code>%s</code></td><td>%s</td>'
            '<td><form method="post" action="/setrole">'
            '<input type="hidden" name="slug" value="%s">'
            '<select name="role" onchange="this.form.submit()">%s</select></form></td>'
            '<td class="nowrap">%d</td><td class="nowrap">%s</td></tr>'
            % (p["slug"], html.escape(p["title"]), auto, html.escape(p["slug"]),
               html.escape(p["group"]), html.escape(p["slug"]), opts,
               cm.get(p["slug"], 0), html.escape(p["mtime"])))
    return """
<p class="hint">共 <b>%d</b> 个页面。%s。改动即时生效，不用重启服务。
标「自动」的是脚本生成的页面（模组页等），重新生成时会保留正文里手写的段落。</p>
<div class="tablewrap"><table class="wikitable"><thead><tr>
<th>标题</th><th>文件名</th><th>分组</th><th>可见组</th><th>留言</th><th>最后修订</th>
</tr></thead><tbody>%s</tbody></table></div>
<p class="hint">可见组改 <code>player</code> 就对所有登录账号开放；改 <code>admin</code> 只有管理员能看。
要加新组，编辑 <code>data/groups.json</code>。</p>""" % (len(pages), summary, "".join(rows))


# ---------------------------------------------------------------- 账号 / 权限组管理

def save_users(users):
    tmp = USER_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"users": users}, f, ensure_ascii=False, indent=2)
    os.replace(tmp, USER_FILE)


def users_body(user, msg="", err=""):
    users = load_users()
    gs = load_groups()
    notice = ""
    if msg:
        notice += '<p class="ok">%s</p>' % html.escape(msg)
    if err:
        notice += '<p class="err">%s</p>' % html.escape(err)

    gchk = "".join(
        '<label class="cbx"><input type="checkbox" form="{f}" name="groups" value="{g}">{l}</label>'
        for g, l in gs.items())

    rows = []
    for name, u in sorted(users.items(), key=lambda kv: (kv[1].get("role") != "admin", kv[0])):
        f = "f_" + re.sub(r"[^A-Za-z0-9_]", "_", name)
        mine = user_groups(u)
        boxes = "".join(
            '<label class="cbx"><input type="checkbox" form="%s" name="groups" value="%s"%s>%s</label>'
            % (f, html.escape(g), " checked" if g in mine else "", html.escape(l))
            for g, l in gs.items())
        role_sel = "".join(
            '<option value="%s"%s>%s</option>'
            % (r, " selected" if u.get("role") == r else "", lbl)
            for r, lbl in (("player", "普通"), ("admin", "管理员")))
        self_note = ' <span class="rs-group">自己</span>' if name == user["name"] else ""
        src_note = (' <span class="rs-group" title="密码跟随游戏账号">游戏</span>'
                    if u.get("source") == "easyauth" else "")
        if u.get("source") == "easyauth":
            pw_link = '<span class="lg-dim" title="密码以 EasyAuth 为准，改 Wiki 这边的没用">密码随游戏</span>'
        else:
            pw_link = '<a class="mini-link" href="#" data-pw="%s">重置密码</a>' % html.escape(name)
        rows.append(
            '<tr><td><code>%s</code>%s%s</td>'
            '<td><input form="%s" name="display" value="%s" maxlength="24"></td>'
            '<td><input form="%s" name="title" value="%s" maxlength="16" placeholder="如 服主 / 建筑师"></td>'
            '<td class="gs-cell">%s</td>'
            '<td><select form="%s" name="role">%s</select></td>'
            '<td class="nowrap"><button form="%s" type="submit" class="mini">保存</button>'
            '%s'
            '<a class="mini-link danger" href="#" data-deluser="%s">删除</a></td></tr>'
            % (html.escape(name), self_note, src_note, f, html.escape(u.get("display", name)),
               f, html.escape(u.get("title", "")), boxes, f, role_sel, f, pw_link,
               html.escape(name)))

    forms = "".join('<form id="f_%s" method="post" action="/setuser">'
                    '<input type="hidden" name="name" value="%s"></form>'
                    % (re.sub(r"[^A-Za-z0-9_]", "_", n), html.escape(n)) for n in users)

    add_opts = "".join(
        '<label class="cbx"><input type="checkbox" name="groups" value="%s"%s>%s</label>'
        % (html.escape(g), " checked" if g == "player" else "", html.escape(l))
        for g, l in gs.items())

    ea = mcaccounts.summary()
    if ea["exists"] and ea["bcrypt"]:
        src_note = ('<p class="ok">已接入 1.20.1 服 EasyAuth（%d 个账号）：'
                    '玩家用<b>进服密码</b>登录，第一次登录会自动出现在下表。'
                    '称号、权限组在这里改，不影响游戏。</p>' % ea["count"])
    elif not ea["exists"]:
        src_note = ('<p class="err">找不到 EasyAuth 账号库：<code>%s</code>，'
                    '游戏密码登录暂时不可用。</p>' % html.escape(ea["path"]))
    else:
        src_note = ('<p class="err">缺少 bcrypt 组件（<code>vendor</code> 目录），'
                    '游戏密码登录暂时不可用。</p>')

    return """%s%s
<p class="hint">这里改的是<b>账号本身</b>：显示名、称号、属于哪些权限组、是否管理员。
页面能不能被某组看到，在 <a href="/pages">页面管理</a> 里逐页设置。</p>
<form class="wikiform" method="post" action="/newuser">
  <table class="formtable">
    <tr><th>新增账号</th><td>
      <input name="name" placeholder="游戏 ID（大小写随意，登录不区分）" style="max-width:220px">
      <input name="display" placeholder="显示名" style="max-width:140px">
      <input name="title" placeholder="称号，如 建筑师" style="max-width:140px">
      <input name="pw" placeholder="初始密码，至少 6 位" style="max-width:160px">
      <div class="fhint">给不在 EasyAuth 里的号（比如 1.21 服玩家）手动开 Wiki 账号用。1.20.1 的玩家不用在这里建，登录一次会自动出现。</div>
    </td></tr>
    <tr><th>权限组</th><td>%s</td></tr>
  </table>
  <div class="actions"><button type="submit">创建账号</button></div>
</form>
<div class="tablewrap"><table class="wikitable users-table"><thead><tr>
<th>账号</th><th>显示名</th><th>称号</th><th>权限组</th><th>身份</th><th>操作</th>
</tr></thead><tbody>%s</tbody></table></div>
%s
<script>
document.addEventListener('click', function(e){
  var a = e.target.closest('[data-pw]') || e.target.closest('[data-deluser]');
  if(!a) return;
  e.preventDefault();
  var post = function(action, keys, vals){
    var f = document.createElement('form');
    f.method='post'; f.action=action;
    keys.forEach(function(k,i){
      var el=document.createElement('input'); el.type='hidden'; el.name=k; el.value=vals[i]; f.appendChild(el);});
    document.body.appendChild(f); f.submit();
  };
  if(a.hasAttribute('data-pw')){
    var n = a.getAttribute('data-pw');
    var p = prompt('给 ' + n + ' 设置新密码（至少 6 位）：');
    if(!p) return;
    post('/resetpw', ['name','pw'], [n, p]);
  } else {
    var n2 = a.getAttribute('data-deluser');
    if(!confirm('删除账号 ' + n2 + '？这个人的留言会保留，但不能再登录。')) return;
    post('/deluser', ['name'], [n2]);
  }
});
</script>""" % (notice, src_note, add_opts, forms + "".join(rows), "")


def groups_body(msg="", err=""):
    pages = load_all()
    users = load_users()
    rows = []
    for gid, label in load_groups().items():
        members = [n for n, u in users.items() if gid in user_groups(u)]
        npages = sum(1 for p in pages if gid in page_groups(p))
        builtin = gid in ("player", "login", "admin")
        act = ('<span class="lg-dim">内置</span>' if builtin else
               '<a class="mini-link danger" href="/delgroup?id=%s">删除</a>' % html.escape(gid))
        rows.append('<tr><td><code>%s</code></td><td>%s</td><td>%d</td><td>%d</td><td>%s</td></tr>'
                    % (html.escape(gid), html.escape(label), len(members), npages, act))
    notice = ""
    if msg:
        notice = '<p class="ok">%s</p>' % html.escape(msg)
    if err:
        notice = '<p class="err">%s</p>' % html.escape(err)
    return """%s
<p class="hint">权限组决定「谁能看哪些页面」。页面头部 <code>role:</code> 填组 id，
可以填多个，用逗号隔开：<code>role: builder,staff</code>。
<code>player</code>（所有人，含游客）、<code>login</code>（登录后才可见）、
<code>admin</code> 是内置语义，不能删。</p>
<div class="tablewrap"><table class="wikitable"><thead><tr>
<th>组 id</th><th>名称</th><th>成员</th><th>页面</th><th>操作</th>
</tr></thead><tbody>%s</tbody></table></div>
<form class="wikiform" method="post" action="/savegroup">
  <table class="formtable">
    <tr><th>新增 / 改组</th><td>
      <input name="id" placeholder="组 id，小写字母，如 builder" style="max-width:200px">
      <input name="label" placeholder="显示名，如 建筑师" style="max-width:200px">
      <div class="fhint">id 已存在就是改显示名。改完可以去「账号与称号」把人加进这个组。</div>
    </td></tr>
  </table>
  <div class="actions"><button type="submit">保存</button></div>
</form>""" % (notice, "".join(rows))


def old_group_rows():
    """读原始 groups.json，保住每组的 desc（save_groups_table 只写 id 和 label）。"""
    try:
        with open(GROUP_FILE, "r", encoding="utf-8") as f:
            return {g["id"]: g for g in json.load(f)["groups"]}
    except Exception:
        return {}


def save_groups_table(groups):
    old = old_group_rows()
    for g in groups:
        if not g.get("desc"):
            g["desc"] = old.get(g["id"], {}).get("desc", "")
    tmp = GROUP_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"_readme": "可见组表。id 用于页面 frontmatter 的 role: 字段；label 显示在表单和锁标上。",
                   "groups": groups}, f, ensure_ascii=False, indent=2)
    os.replace(tmp, GROUP_FILE)


# ---------------------------------------------------------------- HTTP
class Handler(BaseHTTPRequestHandler):
    server_version = "RedtaleWiki/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s  %s\n" % (time.strftime("%H:%M:%S"), fmt % args))

    def send_html(self, code, text):
        data = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def redirect(self, to, token=None):
        self.send_response(302)
        self.send_header("Location", to)
        if token:
            self.send_header("Set-Cookie", "sid=%s; Path=/; HttpOnly; SameSite=Lax" % token)
        self.end_headers()

    @staticmethod
    def safe_next(v):
        """只允许站内路径，避免被拿去做开放跳转。"""
        v = (v or "").strip()
        if v.startswith("/") and not v.startswith("//") and "\r" not in v and "\n" not in v:
            return v
        return ""

    def need_admin(self, user, pages, msg):
        """管理员页面：游客送去登录，普通玩家给 403。"""
        if user.get("role") == "admin":
            return True
        if is_guest(user):
            path = urllib.parse.urlparse(self.path).path
            self.redirect("/login?next=" + urllib.parse.quote(path))
        else:
            self.send_html(403, shell(user, "无权访问",
                                      "<p>%s</p>" % html.escape(msg), pages, tabs=False))
        return False

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        user = get_session(self) or GUEST
        pages = load_all()
        titles = {p["slug"]: p["title"] for p in pages}

        if path == "/api/inbox":
            exp = _inbox_token()
            if not exp or not secrets.compare_digest(self.headers.get("X-Inbox-Token") or "", exp):
                self.send_json({"ok": False, "err": "bad token"}, 403)
                return
            items = inbox_items()
            self.send_json({
                "ok": True,
                "open": [i for i in items if i["status"] == "open"],
                "done": [i for i in items if i["status"] == "done"],
            })
            return

        if path == "/static/style.css":
            try:
                with open(CSS_FILE, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/css; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except FileNotFoundError:
                self.send_html(404, "no css")
            return

        if path == "/login":
            if not is_guest(user):
                self.redirect("/p/index")
                return
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            tab = (q.get("tab") or ["pw"])[0]
            nxt = (q.get("next") or [""])[0]
            self.send_html(200, bind_page() if tab == "bind" else login_page(nxt=nxt))
            return

        if path == "/logout":
            cookie = SimpleCookie()
            raw = self.headers.get("Cookie")
            if raw:
                try:
                    cookie.load(raw)
                    tok = cookie.get("sid")
                    if tok:
                        with LOCK:
                            SESSIONS.pop(tok.value, None)
                except Exception:
                    pass
            self.send_response(302)
            self.send_header("Location", "/login")
            self.send_header("Set-Cookie", "sid=; Path=/; Max-Age=0")
            self.end_headers()
            return

        if path == "/bind":
            self.send_html(200, bind_page())
            return

        if path == "/bind/check":
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            token = (q.get("t") or [""])[0]
            state, mc = mcauth.bind_status(token)
            self.send_json({"state": state, "mc": mc or ""})
            return

        if path in ("/bind/wait", "/bind/pw"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            token = (q.get("t") or [""])[0]
            b = mcauth.get_bind(token)
            if not b:
                self.send_html(200, bind_page("验证码已过期，重新来一次。"))
                return
            if path == "/bind/wait":
                self.send_html(200, bind_wait_page(token, b["code"], b["mc"]))
            else:
                if mcauth.bind_status(token)[0] != "ok":
                    self.send_html(200, bind_wait_page(token, b["code"], b["mc"]))
                    return
                self.send_html(200, bind_pw_page(token, b["mc"]))
            return

        if path == "/":
            self.redirect("/p/index")
            return

        if path == "/search":
            q = (urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("q") or [""])[0]
            title = ("搜索：" + q) if q.strip() else "所有页面"
            self.send_html(200, shell(user, title, search_body(user, pages, q), pages,
                                      tabs=False, heading=title, query=q, tool="search"))
            return

        if path == "/new":
            if not self.need_admin(user, pages, "只有管理员能新建页面。"):
                return
            self.send_html(200, shell(user, "新建页面", new_page_body(user, pages), pages,
                                      tabs=False, heading="新建页面", tool="new"))
            return

        if path == "/pages":
            if not self.need_admin(user, pages, "只有管理员能管理页面。"):
                return
            self.send_html(200, shell(user, "页面管理", pages_body(user, pages), pages,
                                      tabs=False, heading="页面管理", tool="pages"))
            return

        if path == "/users":
            if not self.need_admin(user, pages, "只有管理员能管理账号。"):
                return
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            self.send_html(200, shell(user, "账号与称号",
                                      users_body(user, (q.get("ok") or [""])[0],
                                                 (q.get("err") or [""])[0]), pages,
                                      tabs=False, heading="账号与称号", tool="users"))
            return

        if path == "/groups":
            if not self.need_admin(user, pages, "只有管理员能改权限组。"):
                return
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            self.send_html(200, shell(user, "权限组",
                                      groups_body((q.get("ok") or [""])[0],
                                                  (q.get("err") or [""])[0]), pages,
                                      tabs=False, heading="权限组", tool="groups"))
            return

        if path == "/delgroup":
            if user["role"] != "admin":
                self.send_html(403, "forbidden")
                return
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            gid = (q.get("id") or [""])[0]
            if gid in ("player", "login", "admin"):
                self.redirect("/groups?err=" + urllib.parse.quote("内置组不能删"))
                return
            used = [p["slug"] for p in pages if gid in page_groups(p)]
            members = [n for n, u in load_users().items() if gid in user_groups(u)]
            if used or members:
                self.redirect("/groups?err=" + urllib.parse.quote(
                    "还有 %d 个页面、%d 个成员在用这个组，先清空再删" % (len(used), len(members))))
                return
            rows = [r for r in [{"id": k, "label": v} for k, v in load_groups().items()]
                    if r["id"] != gid]
            save_groups_table(rows)
            self.redirect("/groups?ok=" + urllib.parse.quote("已删除组 %s" % gid))
            return

        if path == "/feedback":
            self.send_html(200, shell(user, "意见箱",
                                      social.feedback_body(None if is_guest(user) else user,
                                                           user["role"] == "admin"),
                                      pages, tabs=False, heading="意见箱", tool="feedback"))
            return

        if path == "/fbclose":
            if user["role"] != "admin":
                self.send_html(403, "forbidden")
                return
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            rid = (q.get("id") or [""])[0]
            row = next((r for r in social.feedback() if r["id"] == rid), None)
            if row:
                social.reopen(rid) if row.get("status") == "done" else social.reply(rid, "已处理", user)
            self.redirect("/feedback")
            return

        if path.startswith("/discuss/"):
            slug = path[9:]
            page = next((p for p in pages if p["slug"] == slug), None)
            if not page:
                self.send_html(404, shell(user, "页面不存在", "<p>没有这个页面。</p>", pages))
                return
            if not can_view(user, page):
                self.send_html(403, shell(user, "无权访问",
                                          "<p>这个页面仅限「%s」查看。</p>"
                                          % html.escape(role_label(page["role"])), pages))
                return
            self.send_html(200, shell(user, "讨论：" + page["title"],
                                      social.discuss_page(slug, page["title"],
                                                          None if is_guest(user) else user,
                                                          user["role"] == "admin"),
                                      pages, slug=slug, group=page["group"],
                                      mtime=page["mtime_human"],
                                      heading="讨论：" + page["title"],
                                      tab_active="discuss"))
            return

        if path.startswith("/edit/"):
            if not self.need_admin(user, pages, "这个页面只有管理员能编辑。"):
                return
            slug = path[6:]
            page = next((p for p in pages if p["slug"] == slug), None)
            if not page:
                self.send_html(404, shell(user, "页面不存在", "<p>没有这个页面。</p>", pages))
                return
            body = (
                '<p class="edithint">直接编辑下方 Markdown 全文（含头部 <code>---</code> 元信息）。'
                "role 填可见组（player=所有人含游客，login=登录可见，admin=仅管理员，或自定义组；"
                "可用逗号写多个：role: builder,staff），order 越小越靠前。"
                "支持 <code>[[页面]]</code> 站内链接、<code>::: tip</code> 提示框、"
                "<code>::: infobox</code> 信息框。</p>"
                '<form method="post" action="/save/%s"><textarea name="content" spellcheck="false">%s</textarea>'
                '<div class="actions"><button type="submit">保存页面</button>'
                '<a class="btn" href="/p/%s">取消</a></div></form>'
                % (slug, html.escape(page["raw"]), slug)
            )
            self.send_html(200, shell(user, "编辑：" + page["title"], body, pages,
                                      slug=slug, group=page["group"], mtime=page["mtime_human"]))
            return

        if path.startswith("/p/"):
            slug = path[3:]
            page = next((p for p in pages if p["slug"] == slug), None)
            if not page:
                self.send_html(404, shell(user, "页面不存在", "<p>没有找到这个页面。</p>", pages))
                return
            if not can_view(user, page):
                self.send_html(403, shell(user, "无权访问",
                                          "<p>这个页面仅限「%s」查看。</p>"
                                          % html.escape(role_label(page["role"])), pages))
                return
            # 正文首行的 # 标题升为页面标题，避免与模板 h1 重复
            src, heading = page["body"], page["title"]
            m = re.match(r"\s*#\s+([^\n#][^\n]*)\n+", src)
            if m:
                heading = m.group(1).strip()
                src = src[m.end():]

            md = MD(titles, slug, user["role"] == "admin")
            body = md.render(src)
            toc = render_toc(md.headings)
            if toc:
                cut = body.find("<h2")
                body = (body[:cut] + toc + body[cut:]) if cut >= 0 else (toc + body)
            self.send_html(200, shell(user, page["title"], body, pages,
                                      slug=slug, group=page["group"],
                                      mtime=page["mtime_human"], heading=heading))
            return

        self.send_html(404, shell(user, "页面不存在", "<p>路径无效。</p>", pages, tabs=False))

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8")
        form = urllib.parse.parse_qs(body)

        if path == "/api/inbox":
            exp = _inbox_token()
            if not exp or not secrets.compare_digest(self.headers.get("X-Inbox-Token") or "", exp):
                self.send_json({"ok": False, "err": "bad token"}, 403)
                return
            try:
                item = json.loads(body or "{}")
            except ValueError:
                self.send_json({"ok": False, "err": "bad json"}, 400)
                return
            action = str(item.get("action") or "add").strip()
            if action == "add":
                ok, msg, key = inbox_add(item)
            elif action == "resolve":
                ok, msg, key = inbox_resolve(str(item.get("key") or ""),
                                             item.get("note") or "", str(item.get("by") or ""))
            else:
                ok, msg, key = False, "action 只能是 add / resolve", ""
            self.send_json({"ok": ok, "msg": msg, "key": key}, 200 if ok else 400)
            return

        if path == "/login":
            u = (form.get("u") or [""])[0].strip()
            p = (form.get("p") or [""])[0]
            nxt = self.safe_next((form.get("next") or [""])[0])
            ip = (self.client_address or ("?",))[0]
            if fail_blocked(ip):
                self.send_html(429, login_page("密码错太多次了，过十分钟再试。", u=u, nxt=nxt))
                return
            user, err = do_login(u, p)
            if not user:
                note_fail(ip)
                time.sleep(0.6)
                self.send_html(200, login_page(err, u=u, nxt=nxt))
                return
            with LOCK:
                LOGIN_FAIL.pop(ip, None)
            self.redirect(nxt or "/p/index", new_session(user))
            return

        if path == "/bind":
            mc = (form.get("mc") or [""])[0].strip()
            if not re.match(r"^[A-Za-z0-9_]{2,32}$", mc):
                self.send_html(400, bind_page("游戏 ID 只能是字母、数字和下划线，2-32 位。", mc))
                return
            _, exist = find_user(mc)
            if exist:
                self.send_html(400, bind_page("「%s」已经绑定过了，直接用密码登录。忘了密码找服主重置。" % mc, mc))
                return
            token, code = mcauth.new_bind(mc)
            self.redirect("/bind/wait?t=" + urllib.parse.quote(token))
            return

        if path == "/bind/pw":
            token = (form.get("t") or [""])[0]
            p1 = (form.get("p1") or [""])[0]
            p2 = (form.get("p2") or [""])[0]
            display = (form.get("display") or [""])[0].strip()
            b = mcauth.get_bind(token)
            if not b:
                self.send_html(400, bind_page("验证码已过期，重新来一次。"))
                return
            state, who = mcauth.bind_status(token)
            if state != "ok":
                self.send_html(200, bind_wait_page(token, b["code"], b["mc"]))
                return
            mc = who or b["mc"]
            if len(p1) < 6:
                self.send_html(400, bind_pw_page(token, mc, "密码至少 6 位。"))
                return
            if p1 != p2:
                self.send_html(400, bind_pw_page(token, mc, "两次输入的密码不一致。"))
                return
            users = load_users()
            if mc in users:
                self.send_html(400, bind_page("这个 ID 已经有 Wiki 账号了，直接用密码登录。", mc))
                return
            salt = secrets.token_hex(8)
            # 验证码通道已经证明了「这个人真的在游戏里控制这个 ID」，
            # 所以服主 ID 走这条路也应当拿到管理员，否则忘了游戏密码就没有恢复入口。
            want_admin = mc.lower() in mcaccounts.admin_ids()
            grp = ["admin", "player"] if want_admin else ["player"]
            users[mc] = {"salt": salt, "hash": hash_pw(p1, salt),
                         "role": "admin" if want_admin else "player",
                         "display": display or mc, "title": "", "groups": grp,
                         "bound_at": time.strftime("%Y-%m-%d %H:%M")}
            save_users(users)
            mcauth.drop_bind(token)
            user = {"name": mc, "role": "admin" if want_admin else "player",
                    "display": display or mc, "groups": grp, "title": ""}
            self.redirect("/p/index", new_session(user))
            return

        user = get_session(self)
        if is_guest(user):
            slug = (form.get("slug") or [""])[0]
            back = "/p/index"
            if path == "/comment" and re.match(r"^[a-z0-9_-]+$", slug):
                back = "/discuss/" + slug
            self.redirect("/login?next=" + urllib.parse.quote(back))
            return

        if path == "/comment":
            slug = (form.get("slug") or [""])[0]
            pages = load_all()
            page = next((p for p in pages if p["slug"] == slug), None)
            if not page or not can_view(user, page):
                self.send_html(404, "not found")
                return
            social.add("comment", user, (form.get("text") or [""])[0], page=slug)
            self.redirect("/discuss/" + slug)
            return

        if path == "/delcomment":
            if user["role"] != "admin":
                self.send_html(403, "forbidden")
                return
            social.delete((form.get("id") or [""])[0])
            back = self.headers.get("Referer") or "/p/index"
            self.redirect(back)
            return

        if path == "/feedback":
            social.add("feedback", user, (form.get("text") or [""])[0])
            self.redirect("/feedback")
            return

        if path == "/fbreply":
            if user["role"] != "admin":
                self.send_html(403, "forbidden")
                return
            social.reply((form.get("id") or [""])[0], (form.get("text") or [""])[0], user)
            self.redirect("/feedback")
            return

        # ---- 账号管理
        if path == "/setuser":
            if user["role"] != "admin":
                self.send_html(403, "forbidden")
                return
            name = (form.get("name") or [""])[0]
            users = load_users()
            if name not in users:
                self.redirect("/users?err=" + urllib.parse.quote("账号不存在"))
                return
            u = users[name]
            role = (form.get("role") or [u.get("role", "player")])[0]
            if name == user["name"] and role != "admin":
                self.redirect("/users?err=" + urllib.parse.quote("不能取消自己的管理员权限"))
                return
            gs = load_groups()
            picked = [g for g in form.get("groups", []) if g in gs]
            u["display"] = (form.get("display") or [name])[0].strip() or name
            u["title"] = (form.get("title") or [""])[0].strip()
            u["role"] = role if role in ("player", "admin") else "player"
            u["groups"] = picked or ["player"]
            save_users(users)
            self.redirect("/users?ok=" + urllib.parse.quote("已保存 %s" % name))
            return

        if path == "/newuser":
            if user["role"] != "admin":
                self.send_html(403, "forbidden")
                return
            name = (form.get("name") or [""])[0].strip()
            pw = (form.get("pw") or [""])[0]
            if not re.match(r"^[A-Za-z0-9_]{2,32}$", name):
                self.redirect("/users?err=" + urllib.parse.quote("账号只能字母数字下划线，2-32 位"))
                return
            users = load_users()
            if any(k.lower() == name.lower() for k in users):
                self.redirect("/users?err=" + urllib.parse.quote("账号已存在"))
                return
            if len(pw) < 6:
                self.redirect("/users?err=" + urllib.parse.quote("初始密码至少 6 位"))
                return
            gs = load_groups()
            picked = [g for g in form.get("groups", []) if g in gs] or ["player"]
            salt = secrets.token_hex(8)
            users[name] = {"salt": salt, "hash": hash_pw(pw, salt), "role": "player",
                           "display": (form.get("display") or [name])[0].strip() or name,
                           "title": (form.get("title") or [""])[0].strip(),
                           "groups": picked}
            save_users(users)
            self.redirect("/users?ok=" + urllib.parse.quote("已创建 %s" % name))
            return

        if path == "/deluser":
            if user["role"] != "admin":
                self.send_html(403, "forbidden")
                return
            name = (form.get("name") or [""])[0]
            if name == user["name"]:
                self.redirect("/users?err=" + urllib.parse.quote("不能删自己"))
                return
            users = load_users()
            users.pop(name, None)
            save_users(users)
            self.redirect("/users?ok=" + urllib.parse.quote("已删除 %s" % name))
            return

        if path == "/resetpw":
            if user["role"] != "admin":
                self.send_html(403, "forbidden")
                return
            name = (form.get("name") or [""])[0]
            pw = (form.get("pw") or [""])[0]
            if len(pw) < 6:
                self.redirect("/users?err=" + urllib.parse.quote("密码至少 6 位"))
                return
            users = load_users()
            if name in users:
                if users[name].get("source") == "easyauth":
                    self.redirect("/users?err=" + urllib.parse.quote(
                        "「%s」的密码以游戏账号为准，请让本人进服后改密码" % name))
                    return
                salt = secrets.token_hex(8)
                users[name]["salt"] = salt
                users[name]["hash"] = hash_pw(pw, salt)
                save_users(users)
            self.redirect("/users?ok=" + urllib.parse.quote("已重置 %s 的密码" % name))
            return

        if path == "/savegroup":
            if user["role"] != "admin":
                self.send_html(403, "forbidden")
                return
            gid = (form.get("id") or [""])[0].strip().lower()
            label = (form.get("label") or [""])[0].strip()
            if not re.match(r"^[a-z][a-z0-9_]{1,15}$", gid):
                self.redirect("/groups?err=" + urllib.parse.quote("组 id 用小写字母开头，2-16 位"))
                return
            if not label:
                label = gid
            rows = [{"id": k, "label": v} for k, v in load_groups().items()]
            for r in rows:
                if r["id"] == gid:
                    r["label"] = label
                    break
            else:
                rows.append({"id": gid, "label": label, "desc": ""})
            save_groups_table(rows)
            self.redirect("/groups?ok=" + urllib.parse.quote("已保存组 %s" % gid))
            return

        if path == "/new":
            if user["role"] != "admin":
                self.send_html(403, "forbidden")
                return
            pages = load_all()
            title = (form.get("title") or [""])[0].strip()
            slug = (form.get("slug") or [""])[0].strip().lower()
            group = (form.get("group") or ["玩家指南"])[0].strip() or "玩家指南"
            order = (form.get("order") or ["50"])[0].strip() or "50"
            role = (form.get("role") or ["player"])[0].strip() or "player"
            if role not in load_groups():
                role = "player"
            data = {"title": title, "slug": slug, "group": group, "order": order}

            err = ""
            if not title:
                err = "标题不能为空。"
            elif not re.match(r"^[a-z0-9_-]{1,48}$", slug):
                err = "文件名只能用小写字母、数字、- 和 _，长度 1–48。"
            elif any(p["slug"] == slug for p in pages):
                err = "文件名 %s 已存在，换一个。" % slug
            if err:
                self.send_html(400, shell(user, "新建页面",
                                          new_page_body(user, pages, data, err), pages,
                                          tabs=False, heading="新建页面", tool="new"))
                return

            content = "---\ntitle: %s\nrole: %s\ngroup: %s\norder: %s\n---\n\n# %s\n\n" % (
                title, role, group, order, title)
            with open(os.path.join(PAGE_DIR, slug + ".md"), "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            self.redirect("/edit/" + slug)
            return

        if path == "/setrole":
            if user["role"] != "admin":
                self.send_html(403, "forbidden")
                return
            slug = (form.get("slug") or [""])[0].strip()
            role = (form.get("role") or [""])[0].strip()
            target = os.path.join(PAGE_DIR, slug + ".md")
            if not re.match(r"^[a-z0-9_-]+$", slug) or not os.path.isfile(target):
                self.send_html(400, "bad slug")
                return
            if role not in load_groups():
                self.send_html(400, "bad role")
                return
            with open(target, "r", encoding="utf-8") as f:
                raw = f.read()
            if re.search(r"(?m)^role:", raw):
                raw = re.sub(r"(?m)^role:.*$", "role: " + role, raw, count=1)
            else:
                self.send_html(400, "该页面头部没有 role 字段，请在编辑器里手动加")
                return
            with open(target, "w", encoding="utf-8", newline="\n") as f:
                f.write(raw)
            self.redirect("/pages")
            return

        if path.startswith("/save/"):
            if user["role"] != "admin":
                self.send_html(403, "forbidden")
                return
            slug = path[6:]
            if not re.match(r"^[a-z0-9_-]+$", slug):
                self.send_html(400, "bad slug")
                return
            content = (form.get("content") or [""])[0]
            target = os.path.join(PAGE_DIR, slug + ".md")
            with open(target, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            self.redirect("/p/" + slug)
            return

        self.send_html(404, "not found")


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    if not os.path.isdir(PAGE_DIR):
        print("找不到内容目录:", PAGE_DIR)
        sys.exit(1)
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print("=" * 52)
    print("  赤物语 Wiki 已启动")
    print("  本机   http://127.0.0.1:%d" % port)
    print("  局域网 http://%s:%d" % (lan_ip(), port))
    print("  关闭   Ctrl+C")
    print("=" * 52)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
