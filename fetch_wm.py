#!/usr/bin/env python3
import json, os, subprocess, urllib.parse

OUT = "/home/muzykantov/projects/dekasteklo-static/assets/stock"
os.makedirs(OUT, exist_ok=True)
UA = "deka/1.0 (contact e24box@mail.ru)"
QUERIES = ["modern kitchen interior", "minimalist kitchen interior", "kitchen marble countertop",
           "kitchen glass wall", "bathroom glass shower modern", "modern dining kitchen",
           "white kitchen minimalist", "dark kitchen interior"]


def wm(q, limit=10):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": "6",
        "gsrsearch": "filetype:bitmap " + q, "gsrlimit": limit,
        "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": "2400"})
    out = subprocess.check_output(["curl", "-s", "-A", UA, url], text=True)
    try:
        return json.loads(out).get("query", {}).get("pages", {})
    except Exception:
        return {}


seen = set()
n = 0
for q in QUERIES:
    for pid, p in wm(q).items():
        ii = (p.get("imageinfo") or [{}])[0]
        w, h = ii.get("width", 0), ii.get("height", 0)
        thumb = ii.get("thumburl", "")
        if not thumb or w < 2400 or w <= h:
            continue
        key = thumb.split("?")[0]
        if key in seen:
            continue
        seen.add(key)
        n += 1
        fn = os.path.join(OUT, "k%02d.jpg" % n)
        subprocess.run(["curl", "-s", "-L", "-A", UA, "-o", fn, thumb])
        print("%02d %sx%s %-30s %s" % (n, w, h, q[:28], p.get("title", "")[:50]))
        if n >= 12:
            break
    if n >= 12:
        break
