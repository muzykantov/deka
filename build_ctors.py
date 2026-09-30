#!/usr/bin/env python3
import json, os, re, shutil, html, sys

ROOT = "/home/muzykantov/projects/dekasteklo-static"
DIST = os.path.join(ROOT, "dist")
SRC = os.path.join(ROOT, "assets/skinali")
sys.path.insert(0, ROOT)
import parts

data = json.load(open(os.path.join(ROOT, "data/catalog.json"), encoding="utf-8"))
cats = {c["id"]: c for c in data["categories"]}
images = data["images"]
by_cat = {}
for im in images:
    by_cat.setdefault(im["cat"], []).append(im)

SKINALI_CATS = [69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,91,125,128,129,130,
                131,132,133,134,135,136,143,144,145,146,147,148,149,150]

def media(p):
    return "/" + re.sub(r"^images/phocagallery/", "media/", p)

def esc(s):
    return html.escape(str(s))

def item(im):
    return {"id": im["id"], "c": im["code"], "t": media(im["thumb"])}

out = os.path.join(DIST, "assets/skinali")
os.makedirs(os.path.join(out, "data"), exist_ok=True)
shutil.copy(os.path.join(SRC, "skinali.css"), os.path.join(out, "skinali.css"))
shutil.copy(os.path.join(SRC, "skinali.js"), os.path.join(out, "skinali.js"))
if os.path.exists(os.path.join(out, "img")):
    shutil.rmtree(os.path.join(out, "img"))
shutil.copytree(os.path.join(SRC, "img"), os.path.join(out, "img"))

category_list = []
search_seen = {}
for cid in SKINALI_CATS:
    if cid not in cats:
        continue
    ims = sorted(by_cat.get(cid, []), key=lambda x: x["id"])[:500]
    if not ims:
        continue
    category_list.append({"id": cid, "title": cats[cid]["title"]})
    with open(os.path.join(out, "data", "cat_%d.json" % cid), "w", encoding="utf-8") as f:
        json.dump([item(i) for i in ims], f, ensure_ascii=False)
    for i in ims:
        search_seen[i["id"]] = item(i)

with open(os.path.join(out, "data", "categories.json"), "w", encoding="utf-8") as f:
    json.dump(category_list, f, ensure_ascii=False)
with open(os.path.join(out, "data", "search.json"), "w", encoding="utf-8") as f:
    json.dump(sorted(search_seen.values(), key=lambda x: x["id"]), f, ensure_ascii=False)

HTML = """<section class="section"><div class="wrap">
<span class="eyebrow">Онлайн-примерка</span>
<h1>Примерка скинали на кухню</h1>
<p class="muted" style="max-width:62ch">Выберите цвет кухни и рисунок фартука — результат сразу в макете.</p>
<div class="sk" style="padding:0;margin-top:18px">
<div class="sk-stage"><div id="skinali">
  <div class="sk-pickers">
    <div class="grp"><p>Цвет верхних ящиков</p><div id="sw-top" class="swatches"></div></div>
    <div class="grp"><p>Цвет столешницы</p><div id="sw-compt" class="swatches"></div></div>
    <div class="grp"><p>Цвет нижних ящиков</p><div id="sw-bottom" class="swatches"></div></div>
  </div>
  <div class="sk-light"><label><input type="checkbox" id="light"> Включить подсветку</label></div>
  <div class="preview-fit">
  <div class="main-image">
    <div class="light"><img src="/assets/skinali/img/light.png" alt=""></div>
    <div class="top"><img src="/assets/skinali/img/parts/top01.png" alt=""></div>
    <div class="compt"><img src="/assets/skinali/img/parts/compt01.png" alt=""></div>
    <div class="bottom"><img src="/assets/skinali/img/parts/bottom01.png" alt=""></div>
    <div class="fartuk"><img src="/assets/skinali/img/fart/solid04.png" alt=""></div>
  </div>
  </div>
  <div class="sk-tabs">
    <div class="sk-tabs__cap">
      <button class="active" data-tab="#tab-photo">С фотопечатью</button>
      <button data-tab="#tab-solid">Цветной скинали</button>
    </div>
    <div class="sk-tab active" id="tab-photo">
      <div class="chips" id="chips"></div>
      <div class="list-head" id="list-head">Загрузка…</div>
      <div class="list" id="list"></div>
    </div>
    <div class="sk-tab" id="tab-solid">
      <p class="hint">Однотонный фартук:</p>
      <div id="sw-solid" class="swatches"></div>
    </div>
  </div>
  <div class="sk-price">
    <div class="row">
      <div><label>Ширина фартука, мм</label><input type="number" id="pw" value="2000" min="200" step="50"></div>
      <div><label>Высота, мм</label><input type="number" id="ph" value="600" min="150" step="50"></div>
      <label style="display:inline-flex;gap:7px;align-items:center;font-size:14px"><input type="checkbox" id="pback"> подсветка</label>
      <label style="display:inline-flex;gap:7px;align-items:center;font-size:14px"><input type="checkbox" id="pinst"> монтаж</label>
      <div><label>Ориентировочная цена</label><div class="out" id="price">—</div></div>
    </div>
    <div class="note">Расчёт по площади и опциям. Точную стоимость и замер подтвердит менеджер.</div>
  </div>
</div></div></div></div></section>"""

os.makedirs(os.path.join(DIST, "primerka-skinali"), exist_ok=True)
with open(os.path.join(DIST, "primerka-skinali", "index.html"), "w", encoding="utf-8") as f:
    f.write(parts.page("Примерка скинали на кухню — ДЕКА",
        "Онлайн-примерка скинали: подберите цвет кухни и рисунок фартука, введите номер рисунка.",
        HTML, active="sk", extra_head='<link rel="stylesheet" href="%s"><script src="%s" defer></script>' % (parts.asset("/assets/skinali/skinali.css"), parts.asset("/assets/skinali/skinali.js"))))
print("skinali: categories=%d images=%d" % (len(category_list), len(search_seen)))
