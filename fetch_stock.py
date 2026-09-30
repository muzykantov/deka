#!/usr/bin/env python3
import json, os, subprocess, urllib.parse

OUT = "/home/muzykantov/projects/dekasteklo-static/assets/stock"
os.makedirs(OUT, exist_ok=True)
QUERIES = ["minimalist kitchen interior", "modern kitchen interior", "kitchen countertop light",
           "white kitchen cabinets", "glass splashback kitchen", "bathroom glass shower modern"]

def api(q):
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
        {"q": q, "license": "cc0", "page_size": 12, "mature": "false"})
    out = subprocess.check_output(["curl", "-s", "-A", "deka/1.0", url], text=True)
    try:
        return json.loads(out).get("results", [])
    except Exception:
        return []

seen = set()
picked = 0
for q in QUERIES:
    for r in api(q):
        w, h = r.get("width") or 0, r.get("height") or 0
        if w < 1600 or w <= h:
            continue
        url = r.get("url", "")
        if "rawpixel" in url:
            url = url.replace("editor_1024", "editor_2048")
        key = url.split("?")[0]
        if key in seen:
            continue
        seen.add(key)
        picked += 1
        fn = os.path.join(OUT, "s%02d.jpg" % picked)
        subprocess.run(["curl", "-s", "-L", "-o", fn, url])
        sz = os.path.getsize(fn) if os.path.exists(fn) else 0
        print("%02d %s %sx%s %dKB  %s" % (picked, q[:22], w, h, sz // 1024, url[:70]))
        if picked >= 10:
            break
    if picked >= 10:
        break
