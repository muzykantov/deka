#!/usr/bin/env python3
import json, os, re, shutil, html, sys

ROOT = "/home/muzykantov/projects/dekasteklo-static"
DIST = os.path.join(ROOT, "dist")
SRC = os.path.join(ROOT, "assets/closet")
sys.path.insert(0, ROOT)
import parts

data = json.load(open(os.path.join(ROOT, "data/catalog.json"), encoding="utf-8"))
cats = {c["id"]: c for c in data["categories"]}
by_cat = {}
for im in data["images"]:
    by_cat.setdefault(im["cat"], []).append(im)

CLOSET_CATS = [49, 84, 85, 86, 87, 90, 94, 119, 120, 121, 122, 123, 124, 126, 127]

def media(p):
    return "/" + re.sub(r"^images/phocagallery/", "media/", p)

def esc(s):
    return html.escape(str(s))

def item(im):
    return {"id": im["id"], "c": im["code"], "t": media(im["thumb"])}

out = os.path.join(DIST, "assets/closet")
os.makedirs(os.path.join(out, "data"), exist_ok=True)
for d in ("css", "img"):
    src = os.path.join(SRC, d)
    dst = os.path.join(out, d)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
shutil.copy(os.path.join(SRC, "closet.js"), os.path.join(out, "closet.js"))

category_list = []
search_seen = {}
for cid in CLOSET_CATS:
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


def room(style, variant):
    if variant in ("01", "02"):
        line = "after_line" + ("1" if variant == "01" else "2")
        inner = "img_doors" if variant == "01" else "img_doors2"
        ruler = ""
    else:
        line = "after_line" + ("3" if variant == "03" else "4")
        inner = "img_doors" + ("3" if variant == "03" else "4")
        ruler = '<div class="wrapp_ruler3"></div>' if variant == "03" else '<div class="wrapp_ruler4"></div>'
    return ('<li><div class="style_doors">'
            '<img src="/assets/closet/img/ds/st%d_%s.jpg" alt="" class="room_doors_style">'
            '%s<div class="wrapp_after_line %s"><div class="%s img_doors_style"></div></div>'
            '</div></li>') % (style, variant, ruler, line, inner)

rooms12 = "".join(room(s, "02") for s in range(1, 7))
rooms34 = "".join(room(s, v) for s in range(1, 7) for v in ("03", "04"))

EXTRA = """
body{margin:0;background:#fafafa;font:15px/1.45 system-ui,"Segoe UI",Roboto,Arial,sans-serif;color:#222}
.cl-top{background:#3a2f2b;color:#fff;padding:12px 20px}.cl-top a{color:#fff;text-decoration:none;font-weight:700}
.cl{max-width:1100px;margin:0 auto;padding:20px}
.cl h1{font-size:22px;margin:0 0 6px}.cl .hint{color:#777;margin:0 0 16px}
.closet_block{width:auto !important;max-width:1100px;margin:0 auto !important}
#tabs_closet > ul{list-style:none;display:flex;gap:8px;padding:0;margin:0 0 10px}
#tabs_closet > ul a{display:block;padding:8px 18px;background:#efe9e3;border-radius:8px;text-decoration:none;color:#6b5b4d;font-weight:600}
#tabs_closet > ul a.active{background:#c98a3c;color:#fff}
.choose_closet{display:none}.choose_closet.active{display:block}
.fit{overflow:hidden;margin:0 auto;max-width:1050px}
.wrapp_doors_12,.wrapp_doors_34{margin:0 !important}
#carousel_closet,#carousel_closet2{list-style:none;display:flex;gap:10px;overflow-x:auto;padding:4px;margin:0}
#carousel_closet > li,#carousel_closet2 > li{flex:0 0 auto}
.wrapp_img_4doors{display:flex;gap:18px;flex-wrap:wrap;margin-top:16px !important}
.left_part_wi4d{flex:0 0 230px}.right_part_wi4d{flex:1 1 300px;min-width:260px}
.list_all_cat{list-style:none;margin:0;padding:0}
.list_all_cat a{display:block;padding:5px 8px;text-decoration:none;color:#555;border-radius:6px}
.list_all_cat a.active_cat{background:#c98a3c;color:#fff}
.ul_load_img_closet{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px;max-height:430px;overflow:auto;background:#fff;border:1px solid #e2e2e2;border-radius:8px;padding:8px}
.ul_load_img_closet li{text-align:center;cursor:pointer}
.ul_load_img_closet img.big_i{display:block;height:88px;width:auto;border:2px solid transparent;border-radius:6px}
.ul_load_img_closet li.this_closet_active img.big_i,.ul_load_img_closet img.big_i.this_closet_active{border-color:#c98a3c}
.ul_load_img_closet .id_closet{font-size:11px;color:#666;display:block;max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ul_load_img_closet .empty{color:#999}
.search_img_closet{margin-top:10px}
"""

HTML = """<section class="section"><div class="wrap">
<span class="eyebrow">Онлайн-примерка</span>
<h1>Примерка шкаф-купе</h1>
<p class="muted" style="max-width:62ch">Выберите рисунок — он наложится на двери. Количество дверей: 2 или 3-4.</p>
<div class="closet_block">
  <div class="wrapp_count_doors" id="tabs_closet">
    <ul><li><a href="#tabs-1" class="active">2 двери</a></li><li><a href="#tabs-2">3-4 двери</a></li></ul>
    <div class="fit">
      <div id="tabs-1" class="choose_closet active"><div class="wrapp_doors_12">
        <ul id="carousel_closet" class="jcarousel-skin-tango">%s</ul>
      </div></div>
      <div id="tabs-2" class="choose_closet"><div class="wrapp_doors_34">
        <ul id="carousel_closet2" class="jcarousel-skin-tango">%s</ul>
      </div></div>
    </div>
  </div>
  <div class="wrapp_cat_block" style="margin-top:16px"><div class="chips" id="chips"></div></div>
  <div class="wrapp_list_id_closet" style="margin-top:12px"><div class="show_this_cat_closet"><ul class="ul_load_img_closet" id="imglist"></ul></div></div>
</div>
</div></section>"""

os.makedirs(os.path.join(DIST, "primerka-shkaf"), exist_ok=True)
with open(os.path.join(DIST, "primerka-shkaf", "index.html"), "w", encoding="utf-8") as f:
    f.write(parts.page("Примерка шкаф-купе — ДЕКА",
        "Онлайн-примерка рисунков на двери шкафа-купе: выберите рисунок и количество дверей.",
        HTML % (rooms12, rooms34), active="sh",
        extra_head='<link rel="stylesheet" href="%s"><link rel="stylesheet" href="%s"><style>%s</style><script src="%s" defer></script>' % (parts.asset("/assets/closet/css/styles.css"), parts.asset("/assets/ctor.css"), EXTRA, parts.asset("/assets/closet/closet.js"))))
print("closet: categories=%d images=%d rooms=%d" % (len(category_list), len(search_seen), 24))
