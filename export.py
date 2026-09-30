#!/usr/bin/env python3
import json, os, subprocess, sys

COMPOSE_DIR = "/home/muzykantov/projects/dekasteklo"
OUT_DIR = "/home/muzykantov/projects/dekasteklo-static/data"


def query(sql):
    cmd = ["docker", "compose", "exec", "-T", "db", "sh", "-c",
           'mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" dekasteklo -N -B -e "%s"' % sql.replace('"', '\\"')]
    out = subprocess.check_output(cmd, cwd=COMPOSE_DIR, text=True)
    rows = []
    for line in out.splitlines():
        if line == "":
            continue
        rows.append(line.split("\t"))
    return rows


def thumb(filename, size="l"):
    fn = filename.strip()
    d, base = os.path.split(fn)
    t = "thumbs/phoca_thumb_%s_%s" % (size, base)
    return ("images/phocagallery/" + (d + "/" if d else "") + t), "images/phocagallery/" + fn


cat_rows = query(
    "SELECT c.id,c.parent_id,c.title,c.alias,c.published,c.access "
    "FROM stg_phocagallery_categories c ORDER BY c.ordering,c.id")

categories = []
SKIP_CATS = {50, 88, 89, 126, 127}
RENAME_CATS = {90: "Абстракция", 121: "Города ночные", 107: "Морская тематика", 118: "Скинали"}
for r in cat_rows:
    cid, pid, title, alias, pub, access = r[0], r[1], r[2], r[3], r[4], r[5]
    if int(cid) in SKIP_CATS:
        continue
    title = RENAME_CATS.get(int(cid), title).strip()
    alias = (alias or "").strip()
    categories.append({
        "id": int(cid), "parent_id": int(pid), "title": title, "alias": alias,
        "published": int(pub), "access": int(access),
    })

img_rows = query(
    "SELECT i.id,i.catid,i.title,i.filename,i.published "
    "FROM stg_phocagallery i ORDER BY i.ordering,i.id")

images = []
missing = 0
for r in img_rows:
    iid, catid, title, filename, pub = r[0], r[1], r[2], r[3], r[4]
    if not filename.strip():
        continue
    t, orig = thumb(filename, "l")
    images.append({
        "id": int(iid), "cat": int(catid), "code": title, "file": filename,
        "published": int(pub), "access": 1,
        "thumb": t, "orig": orig,
    })

os.makedirs(OUT_DIR, exist_ok=True)
data = {"categories": categories, "images": images}
with open(os.path.join(OUT_DIR, "catalog.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)

pub_img = sum(1 for i in images if i["published"] == 1)
codes = {}
for i in images:
    codes.setdefault(i["code"].strip(), 0)
    codes[i["code"].strip()] += 1
dup = {c: n for c, n in codes.items() if c.strip() != "" and n > 1}
print("categories:", len(categories), "images:", len(images), "published:", pub_img)
print("unique codes:", len(codes), "duplicate codes:", len(dup))
if dup:
    print("sample dup:", list(dup.items())[:5])
