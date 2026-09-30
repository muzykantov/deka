#!/usr/bin/env python3
import json, os, re, shutil, html, sys

ROOT = "/home/muzykantov/projects/dekasteklo-static"
DIST = os.path.join(ROOT, "dist")
SRC = os.path.join(ROOT, "assets/grit")
sys.path.insert(0, ROOT)
import parts

data = json.load(open(os.path.join(ROOT, "data/catalog.json"), encoding="utf-8"))
cats = {c["id"]: c for c in data["categories"]}
by_cat = {}
for im in data["images"]:
    by_cat.setdefault(im["cat"], []).append(im)

GRIT_CATS = [92, 95, 96, 97, 98, 99, 103, 104, 105, 106, 107, 108, 109, 110, 111,
             112, 113, 114, 115, 116, 117, 137, 138, 139, 140]

def media(p):
    return "/" + re.sub(r"^images/phocagallery/", "media/", p)

def esc(s):
    return html.escape(str(s))

def item(im):
    return {"id": im["id"], "c": im["code"], "t": media(im["thumb"])}

out = os.path.join(DIST, "assets/grit")
os.makedirs(os.path.join(out, "data"), exist_ok=True)
shutil.copy(os.path.join(SRC, "grit.js"), os.path.join(out, "grit.js"))

category_list = []
seen = {}
for cid in GRIT_CATS:
    if cid not in cats:
        continue
    ims = sorted(by_cat.get(cid, []), key=lambda x: x["id"])[:500]
    if not ims:
        continue
    category_list.append({"id": cid, "title": cats[cid]["title"]})
    with open(os.path.join(out, "data", "cat_%d.json" % cid), "w", encoding="utf-8") as f:
        json.dump([item(i) for i in ims], f, ensure_ascii=False)
    for i in ims:
        seen[i["id"]] = item(i)
with open(os.path.join(out, "data", "categories.json"), "w", encoding="utf-8") as f:
    json.dump(category_list, f, ensure_ascii=False)

def room(n):
    return ('<div class="style_doors" data-n="%d">'
            '<img src="/assets/closet/img/ds/st1_0%d.jpg" alt="" class="room_doors_style">'
            '<div class="wrapp_after_line after_line%d"><div class="img_doors_style"></div></div>'
            '</div>') % (n, n, n)

rooms = "".join(room(n) for n in (1, 2, 3, 4))

BODY = """<section class="section"><div class="wrap">
  <span class="eyebrow">Онлайн-примерка</span>
  <h1>Пескоструйные рисунки</h1>
  <p class="muted" style="max-width:62ch">Выберите вид — фасад или шкаф-купе, число дверей и рисунок: он появится на стекле.</p>

  <div class="mode" id="mode" style="margin-top:16px">
    <button data-mode="facade" class="active">Фасад</button>
    <button data-mode="closet">Шкаф-купе</button>
  </div>

  <div class="count" id="count" style="margin:14px 0 0">
    <button data-n="1">1 дверь</button>
    <button data-n="2" class="active">2 двери</button>
    <button data-n="3">3 двери</button>
    <button data-n="4">4 двери</button>
  </div>

  <div id="facade-wrap">
    <div class="facade" id="facade" style="margin-top:22px"></div>
  </div>
  <div id="wardrobe" hidden>%s</div>

  <div style="margin-top:26px">
    <div class="chips" id="chips"></div>
    <div class="list-head" id="list-head" style="margin-top:14px">Загрузка…</div>
    <ul class="ul_load_img_closet" id="imglist" style="margin-top:10px"></ul>
  </div>
</div></section>""" % rooms

os.makedirs(os.path.join(DIST, "grid"), exist_ok=True)
with open(os.path.join(DIST, "grid", "index.html"), "w", encoding="utf-8") as f:
    f.write(parts.page("Пескоструйные рисунки — примерка — ДЕКА",
        "Онлайн-примерка пескоструйных рисунков на стеклянные фасады.",
        BODY, active="gr",
        extra_head='<link rel="stylesheet" href="%s"><script src="%s" defer></script>' % (parts.asset("/assets/ctor.css"), parts.asset("/assets/grit/grit.js"))))
print("grit: categories=%d images=%d" % (len(category_list), len(seen)))
