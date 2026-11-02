"""页面留言 + 全站意见箱。

存储：data/social.jsonl，一行一条，kind = comment | feedback。
不做数据库，是因为 wiki 的其他数据也全是文件，备份直接拷目录即可。
"""

import html
import json
import os
import re
import secrets
import threading
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
STORE = os.path.join(DATA, "social.jsonl")
LOCK = threading.Lock()

MAX_LEN = 1000


# ------------------------------------------------------------------ 存取

def _read():
    out = []
    if not os.path.isfile(STORE):
        return out
    with open(STORE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def _write_all(rows):
    os.makedirs(DATA, exist_ok=True)
    tmp = STORE + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, STORE)


def _append(row):
    os.makedirs(DATA, exist_ok=True)
    with open(STORE, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def add(kind, user, text, page=""):
    text = (text or "").strip()
    if not text:
        return None, "内容不能为空。"
    if len(text) > MAX_LEN:
        return None, "内容太长了（上限 %d 字）。" % MAX_LEN
    row = {
        "id": secrets.token_hex(6),
        "kind": kind,
        "page": page,
        "ts": time.time(),
        "user": user["name"],
        "name": user.get("display") or user["name"],
        "title": user.get("title") or "",
        "groups": user.get("groups") or [],
        "text": text,
        "deleted": False,
        "reply": "",
        "reply_by": "",
        "reply_ts": 0,
        "status": "open",
    }
    with LOCK:
        _append(row)
    return row["id"], ""


def page_comments(slug, include_deleted=False):
    rows = [r for r in _read()
            if r["kind"] == "comment" and r.get("page") == slug]
    if not include_deleted:
        rows = [r for r in rows if not r.get("deleted")]
    return rows


def page_comment_count(slug):
    n = 0
    for r in _read():
        if r["kind"] == "comment" and r.get("page") == slug and not r.get("deleted"):
            n += 1
    return n


def open_feedback_count():
    return sum(1 for r in _read()
               if r["kind"] == "feedback" and not r.get("deleted") and r.get("status") != "done")


def comments_count():
    c = {}
    for r in _read():
        if r["kind"] == "comment" and not r.get("deleted"):
            c[r.get("page", "")] = c.get(r.get("page", ""), 0) + 1
    return c


def feedback(only_open=False):
    rows = [r for r in _read() if r["kind"] == "feedback" and not r.get("deleted")]
    if only_open:
        rows = [r for r in rows if r.get("status") != "done"]
    return sorted(rows, key=lambda r: (r.get("status") == "done", -r["ts"]))


def delete(rid):
    with LOCK:
        rows = _read()
        for r in rows:
            if r["id"] == rid:
                r["deleted"] = True
        _write_all(rows)


def hard_delete(rid):
    with LOCK:
        rows = [r for r in _read() if r["id"] != rid]
        _write_all(rows)


def reply(rid, text, user):
    text = (text or "").strip()
    if not text:
        return "回复不能为空。"
    if len(text) > MAX_LEN:
        return "回复太长了。"
    with LOCK:
        rows = _read()
        for r in rows:
            if r["id"] == rid:
                r["reply"] = text
                r["reply_by"] = user.get("display") or user["name"]
                r["reply_ts"] = time.time()
                r["status"] = "done"
        _write_all(rows)
    return ""


def reopen(rid):
    with LOCK:
        rows = _read()
        for r in rows:
            if r["id"] == rid:
                r["status"] = "open"
                r["reply"] = ""
                r["reply_by"] = ""
                r["reply_ts"] = 0
        _write_all(rows)


# ------------------------------------------------------------------ 渲染

def _when(ts):
    t = time.localtime(ts)
    now = time.time()
    if now - ts < 86400 and time.localtime().tm_yday == t.tm_yday:
        return time.strftime("%H:%M", t)
    return time.strftime("%Y-%m-%d %H:%M", t)


def _md_min(text):
    """极简：只处理换行、**粗体**、行内代码和裸链接，够用且不会被注入 HTML。"""
    t = html.escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"(https?://[^\s<]+)", r'<a href="\1" rel="nofollow">\1</a>', t)
    return t.replace("\n", "<br>")


def _avatar(name):
    ch = (name or "?")[0].upper()
    n = sum(ord(c) for c in (name or "?"))
    colors = ["#546e7a", "#5d4037", "#455a64", "#6a1b9a", "#00695c",
              "#c62828", "#283593", "#00838f"]
    return ('<span class="cm-av" style="background:%s">%s</span>'
            % (colors[n % len(colors)], html.escape(ch)))


def comment_list(slug, user, is_admin=False):
    rows = page_comments(slug, include_deleted=is_admin)
    if not rows:
        return ('<div class="cm-empty">还没有人留言。'
                "对这条内容有疑问、发现写错了，直接写在下面。</div>")
    out = ['<ul class="cm-list">']
    for r in rows:
        cls = " cm-deleted" if r.get("deleted") else ""
        ops = ""
        if is_admin:
            ops = ('<span class="cm-ops">'
                   '<a href="#" data-del="%s">%s</a></span>'
                   % (r["id"], "恢复" if r.get("deleted") else "隐藏"))
        badge = ('<span class="cm-title">%s</span>' % html.escape(r["title"])
                 if r.get("title") else "")
        out.append('<li class="cm-item%s" id="c-%s">%s<div class="cm-main">'
                   '<div class="cm-head"><b>%s</b>%s'
                   '<span class="cm-time">%s</span>%s</div>'
                   '<div class="cm-text">%s</div></div></li>'
                   % (cls, r["id"], _avatar(r.get("name")),
                      html.escape(r.get("name") or r["user"]), badge,
                      _when(r["ts"]), ops, _md_min(r["text"])))
    out.append("</ul>")
    return "".join(out)


def comment_box(slug, user):
    if not user:
        return ('<p class="hint">登录后才能留言（用游戏 ID + 进服密码）。'
                '<a href="/login">去登录</a></p>')
    return """<form class="cm-form" method="post" action="/comment">
  <input type="hidden" name="slug" value="%s">
  <textarea name="text" rows="3" maxlength="1000" placeholder="写下你的疑问或补充。换行直接回车，支持 **粗体**、`代码`。"></textarea>
  <div class="cm-form-foot"><span class="fhint">以 %s 的身份发表</span>
  <button type="submit">发表留言</button></div>
</form>""" % (html.escape(slug), html.escape(user.get("display") or user["name"]))


def discuss_page(slug, title, user, is_admin):
    rows = page_comments(slug, include_deleted=is_admin)
    body = ['<p class="hint">这一页的讨论区，共 %d 条留言。'
            '回到 <a href="/p/%s">正文</a>。</p>' % (len(rows), slug)]
    body.append(comment_list(slug, user, is_admin))
    body.append(comment_box(slug, user))
    body.append("""<script>
document.addEventListener('click', function(e){
  var a = e.target.closest('[data-del]');
  if(!a) return;
  e.preventDefault();
  var f = document.createElement('form');
  f.method='post'; f.action='/delcomment';
  var i = document.createElement('input');
  i.type='hidden'; i.name='id'; i.value=a.getAttribute('data-del');
  f.appendChild(i); document.body.appendChild(f); f.submit();
});
</script>""")
    return "\n".join(body)


def feedback_body(user, is_admin):
    rows = feedback()
    out = ['<p class="hint">对服务器或这个 Wiki 有什么想说的都写在这里，'
           '服主会看到。要私下说就写在页面留言里 @ 管理员。</p>']
    if user:
        out.append("""<form class="cm-form" method="post" action="/feedback">
  <textarea name="text" rows="3" maxlength="1000" placeholder="比如：建议加一个可以查询在线玩家的页面 / 规则第 7 条能不能放宽到 200 格以内"></textarea>
  <div class="cm-form-foot"><span class="fhint">署名：%s</span>
  <button type="submit">提交意见</button></div>
</form>""" % html.escape(user.get("display") or user["name"]))
    else:
        out.append('<p class="hint">登录后才能提意见（用游戏 ID + 进服密码）。'
                   '<a href="/login">去登录</a></p>')

    open_n = sum(1 for r in rows if r.get("status") != "done")
    out.append('<h2>全部意见<span class="h2-note">%d 条，其中 %d 条待处理</span></h2>'
               % (len(rows), open_n))
    if not rows:
        out.append('<div class="cm-empty">还没有意见。</div>')
        return "".join(out)

    out.append('<ul class="cm-list fb-list">')
    for r in rows:
        done = r.get("status") == "done"
        badge = ('<span class="cm-title">已处理</span>' if done
                 else '<span class="cm-badge-open">待处理</span>')
        page = ""
        if r.get("page"):
            page = '<a class="cm-page" href="/p/%s">来自页面 %s</a>' % (
                html.escape(r["page"]), html.escape(r["page"]))
        ops = ""
        if is_admin:
            ops = ('<span class="cm-ops">'
                   '<a href="#" data-reply="%s">回复</a>'
                   '<a href="/fbclose?id=%s">%s</a></span>'
                   % (r["id"], r["id"], "重开" if done else "标记已处理"))
        reply = ""
        if r.get("reply"):
            reply = ('<div class="cm-reply"><b>%s</b> 回复：%s</div>'
                     % (html.escape(r.get("reply_by") or "管理员"),
                        _md_min(r["reply"])))
        out.append('<li class="cm-item%s" id="f-%s">%s<div class="cm-main">'
                   '<div class="cm-head"><b>%s</b>%s<span class="cm-time">%s</span>%s</div>'
                   '<div class="cm-text">%s</div>%s%s</div></li>'
                   % (" cm-done" if done else "", r["id"], _avatar(r.get("name")),
                      html.escape(r.get("name") or r["user"]), badge,
                      _when(r["ts"]), ops, _md_min(r["text"]), page, reply))
    out.append("</ul>")
    if is_admin:
        out.append("""<script>
document.addEventListener('click', function(e){
  var a = e.target.closest('[data-reply]');
  if(!a) return;
  e.preventDefault();
  var id = a.getAttribute('data-reply');
  var t = prompt('回复内容：');
  if(!t) return;
  var f = document.createElement('form');
  f.method='post'; f.action='/fbreply';
  [['id',id],['text',t]].forEach(function(p){
    var i=document.createElement('input'); i.type='hidden'; i.name=p[0]; i.value=p[1]; f.appendChild(i);});
  document.body.appendChild(f); f.submit();
});
</script>""")
    return "".join(out)
