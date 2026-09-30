#!/usr/bin/env python3
"""Minimal spam-protected lead endpoint for the DEKA static site (stdlib only)."""
import json, os, time, html, urllib.request, urllib.parse, socketserver
from http.server import BaseHTTPRequestHandler

PORT = int(os.environ.get("DEKA_FORM_PORT", "8099"))
LEADS = os.environ.get("DEKA_LEADS", "/home/muzykantov/backup/dekasteklo/leads.jsonl")
TG_TOKEN = os.environ.get("DEKA_TG_TOKEN", "")
TG_CHAT = os.environ.get("DEKA_TG_CHAT", "")
TURNSTILE_SECRET = os.environ.get("DEKA_TURNSTILE_SECRET", "")
WINDOW, LIMIT = 600, 5
_hits = {}


def rate_ok(ip):
    now = time.time()
    arr = [t for t in _hits.get(ip, []) if now - t < WINDOW]
    _hits[ip] = arr + [now]
    return len(arr) < LIMIT


def turnstile_ok(token, ip):
    if not TURNSTILE_SECRET:
        return True
    data = urllib.parse.urlencode({"secret": TURNSTILE_SECRET, "response": token, "remoteip": ip}).encode()
    try:
        with urllib.request.urlopen("https://challenges.cloudflare.com/turnstile/v0/siteverify", data, timeout=8) as r:
            return json.loads(r.read().decode()).get("success") is True
    except Exception:
        return False


def notify(text):
    os.makedirs(os.path.dirname(LEADS), exist_ok=True)
    with open(LEADS, "a", encoding="utf-8") as f:
        f.write(json.dumps({"t": time.strftime("%F %T"), "text": text}, ensure_ascii=False) + "\n")
    if TG_TOKEN and TG_CHAT:
        try:
            body = urllib.parse.urlencode({"chat_id": TG_CHAT, "text": text}).encode()
            urllib.request.urlopen("https://api.telegram.org/bot%s/sendMessage" % TG_TOKEN, body, timeout=8).read()
        except Exception:
            pass


THANKS = """<!doctype html><html lang="ru" data-theme="light"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Заявка отправлена — ДЕКА</title>
<link rel="icon" href="/assets/img/logo-mark.png"><link rel="stylesheet" href="/assets/fonts/fonts.css">
<link rel="stylesheet" href="/assets/theme.css"></head><body>
<header class="site-header"><div class="wrap bar"><a class="brand" href="/"><img class="mark" src="/assets/img/logo-mark.png" alt="ДЕКА"><span><span class="word">ДЕКА</span></span></a></div></header>
<section class="section"><div class="wrap" style="max-width:640px">
<div class="eyebrow">Заявка</div><h1>Спасибо! Мы свяжемся с вами</h1>
<p class="muted">Сообщение получено. Если вопрос срочный — позвоните: <a href="tel:+79069497071">+7 906 949-70-71</a>.</p>
<p><a class="btn btn-primary" href="/">Вернуться в каталог</a></p>
</div></section></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        b = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        if self.path.rstrip("/") != "/api/lead":
            return self._send(404, "Not found", "text/plain")
        ip = self.headers.get("X-Real-IP") or self.client_address[0]
        if not rate_ok(ip):
            return self._send(429, "Слишком много заявок, попробуйте позже.", "text/plain")
        try:
            n = int(self.headers.get("Content-Length", "0"))
            form = urllib.parse.parse_qs(self.rfile.read(min(n, 65536)).decode("utf-8", "replace"))
        except Exception:
            return self._send(400, "Bad request", "text/plain")
        g = lambda k: (form.get(k, [""])[0] or "").strip()
        if g("company"):  # honeypot
            return self._send(200, THANKS)
        if not g("name") or not g("contact"):
            return self._send(400, "Заполните имя и контакт.", "text/plain")
        if not turnstile_ok(g("cf-turnstile-response"), ip):
            return self._send(403, "Проверка не пройдена.", "text/plain")
        text = "Заявка с сайта ДЕКА\nИмя: %s\nКонтакт: %s\nСообщение: %s" % (
            g("name"), g("contact"), g("message") or "—")
        notify(text)
        return self._send(200, THANKS)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    print("deka form on 127.0.0.1:%d" % PORT, flush=True)
    Server(("127.0.0.1", PORT), H).serve_forever()
