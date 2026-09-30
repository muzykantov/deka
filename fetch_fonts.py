#!/usr/bin/env python3
import os, re, subprocess, sys

ROOT = "/home/muzykantov/projects/dekasteklo-static"
OUT = os.path.join(ROOT, "assets/fonts")
os.makedirs(OUT, exist_ok=True)

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
FAMILIES = [
    ("Manrope", "Manrope:wght@200..800"),
    ("Unbounded", "Unbounded:wght@200..900"),
    ("Caveat", "Caveat:wght@400..700"),
]
KEEP = ("latin", "latin-ext", "cyrillic", "cyrillic-ext")

css_parts = []
for name, query in FAMILIES:
    url = "https://fonts.googleapis.com/css2?family=%s&display=swap" % query
    out = subprocess.check_output(["curl", "-s", "-A", UA, url], text=True)
    # split into blocks preceded by /* subset */ comments
    blocks = re.split(r"/\*\s*([a-z\-]+)\s*\*/", out)
    # blocks: [pre, subset, block, subset, block, ...]
    i = 1
    while i + 1 < len(blocks) + 1 and i < len(blocks):
        subset = blocks[i]
        block = blocks[i + 1] if i + 1 < len(blocks) else ""
        i += 2
        if subset not in KEEP:
            continue
        m = re.search(r"src:\s*url\((https://[^)]+\.woff2)\)", block)
        if not m:
            continue
        src = m.group(1)
        fname = "%s-%s.woff2" % (name.lower(), subset)
        dst = os.path.join(OUT, fname)
        if not os.path.exists(dst):
            subprocess.check_call(["curl", "-s", "-o", dst, src])
        block = block.replace(src, "/assets/fonts/" + fname)
        css_parts.append(block.strip())

with open(os.path.join(OUT, "fonts.css"), "w", encoding="utf-8") as f:
    f.write("\n".join(css_parts))
print("fonts:", len(os.listdir(OUT)) - 1, "files")
for fn in sorted(os.listdir(OUT)):
    print("  ", fn, os.path.getsize(os.path.join(OUT, fn)))
