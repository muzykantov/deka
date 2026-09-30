#!/usr/bin/env python3
import json, os, re, shutil, html, sys, urllib.parse

ROOT = "/home/muzykantov/projects/dekasteklo-static"
DIST = os.path.join(ROOT, "dist")
MEDIA = os.environ.get("DEKA_MEDIA", "/home/muzykantov/deka-media")


def mpath(p):
    return os.path.join(MEDIA, re.sub(r"^images/phocagallery", "phocagallery", p))
sys.path.insert(0, ROOT)
import parts

SITE_URL = os.environ.get("DEKA_SITE_URL", "https://dekasteklo.ru")

data = json.load(open(os.path.join(ROOT, "data/catalog.json"), encoding="utf-8"))
cats = {c["id"]: c for c in data["categories"]}
images = data["images"]
EXCLUDE_CATS = {126, 127}
EXCLUDE_IDS = set()

by_cat = {}
for im in images:
    by_cat.setdefault(im["cat"], []).append(im)
children = {}
for c in data["categories"]:
    children.setdefault(c["parent_id"], []).append(c["id"])
for k in children:
    children[k].sort(key=lambda i: cats[i]["title"].lower())


def media(p):
    return "/" + re.sub(r"^images/phocagallery/", "media/", p)


def has_thumb(im):
    return os.path.exists(mpath(im["thumb"]))


def jsize(p):
    try:
        with open(mpath(p), "rb") as f:
            d = f.read(160000)
    except Exception:
        return None
    i = 2
    while i + 9 < len(d):
        if d[i] != 0xFF:
            i += 1
            continue
        m = d[i + 1]
        if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            return ((d[i + 7] << 8) | d[i + 8], (d[i + 5] << 8) | d[i + 6])
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        i += 2 + ((d[i + 2] << 8) | d[i + 3])
    return None


_sizes = {}
def size(im):
    if im["id"] not in _sizes:
        _sizes[im["id"]] = jsize(im["thumb"])
    return _sizes[im["id"]]


def is_lowq(im):
    s = size(im)
    return (not s) or max(s) < 420


valid_ids = set()
for im in images:
    if im["id"] in EXCLUDE_IDS or im["cat"] in EXCLUDE_CATS:
        continue
    if has_thumb(im) and not is_lowq(im):
        valid_ids.add(im["id"])

valid_by_cat = {}
for im in images:
    if im["id"] in valid_ids:
        valid_by_cat.setdefault(im["cat"], []).append(im)


def count_cat(cid):
    n = len(valid_by_cat.get(cid, []))
    for ch in children.get(cid, []):
        n += count_cat(ch)
    return n


def cat_valid(cid):
    return count_cat(cid) > 0


def pick_cover(cid):
    pool = []
    for ch in [cid] + children.get(cid, []):
        pool += valid_by_cat.get(ch, [])
    if not pool:
        return "/assets/img/hero.png"

    def fsize(im):
        try:
            return os.path.getsize(mpath(im["thumb"]))
        except Exception:
            return 0

    def score(im):
        s = size(im) or (400, 400)
        w, h = s
        ar = (h / w) if w else 1
        return (0 if 0.72 <= ar <= 1.55 else 1, -fsize(im))

    return media(sorted(pool, key=score)[0]["thumb"])


def cat_tile(cid):
    c = cats[cid]
    return ('<a href="/c/%d/"><span class="im"><img loading="lazy" src="%s" alt="%s"></span>'
            '<b>%s</b><span>%d изображений</span></a>'
            % (cid, pick_cover(cid), parts.esc(c["title"]), parts.esc(c["title"]), count_cat(cid)))


def card(im):
    return ('<a class="card" href="/i/%d/"><span class="ph"><img loading="lazy" src="%s" alt="%s"></span>'
            '<span class="meta"><span class="code">%s</span></span></a>'
            % (im["id"], media(im["thumb"]), parts.esc(im["code"]), parts.esc(im["code"])))


def mcard(im):
    return ('<a class="m" href="/i/%d/"><img loading="lazy" src="%s" alt="%s"><span class="cap">%s</span></a>'
            % (im["id"], media(im["thumb"]), parts.esc(im["code"]), parts.esc(im["code"])))


def breadcrumb(cid, last=None):
    out = []
    cur = cid
    while cur and cur in cats:
        out.append('<a href="/c/%d/">%s</a>' % (cur, parts.esc(cats[cur]["title"])))
        cur = cats[cur]["parent_id"]
    out = list(reversed(out))
    if last is not None:
        out.append("<span>%s</span>" % parts.esc(last))
    return '<div class="crumbs">%s / <a href="/">Каталог</a></div>' % " / ".join(out)


def write(rel, s):
    p = os.path.join(DIST, rel)
    os.makedirs(os.path.dirname(p) or DIST, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


# ---------- copy assets ----------
def copytree(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

for name in ("theme.css", "theme.js", "ctor.css"):
    shutil.copy(os.path.join(ROOT, "assets", name), os.path.join(DIST, "assets", name))
copytree(os.path.join(ROOT, "assets/fonts"), os.path.join(DIST, "assets/fonts"))
copytree(os.path.join(ROOT, "assets/img"), os.path.join(DIST, "assets/img"))

media_dst = os.path.join(DIST, "media")
if os.path.islink(media_dst):
    os.unlink(media_dst)
elif os.path.exists(media_dst):
    shutil.rmtree(media_dst)
os.symlink(os.path.join(MEDIA, "phocagallery"), media_dst)

# ---------- home ----------
top = [c["id"] for c in data["categories"] if c["parent_id"] == 0 and cat_valid(c["id"])]
top_sorted = sorted(top, key=lambda i: -count_cat(i))
n_img = len(valid_ids)
n_cat = sum(1 for c in data["categories"] if cat_valid(c["id"]))

HERO_IMG = "/assets/img/kitchen.webp"

hero = """<section class="hero"><div class="wrap inner">
  <div>
    <span class="eyebrow">Салон декорирования стекла и зеркала</span>
    <h1>Скинали, фрески и пескоструй <span class="script" style="font-weight:700">для кухни</span></h1>
    <p class="lead">%(n)s изображений с номерами. Выберите рисунок, примерьте на кухню — изготовим и установим.</p>
    <div class="cta">
      <a class="btn btn-primary" href="/primerka-skinali/">Примерка на кухню</a>
      <a class="btn btn-ghost" href="#catalog">Каталог</a>
      <a class="btn btn-ghost" href="/raboty/">Наши работы</a>
    </div>
  </div>
  <div class="hero-art"><div class="frame"><img src="%(img)s" alt=""></div></div>
</div></section>""" % {"n": format(n_img, ",d").replace(",", " "), "img": HERO_IMG}

cats_block = """<section class="section" id="catalog"><div class="wrap">
  <div class="section-head"><div><span class="eyebrow">Каталог</span><h2>Категории рисунков</h2></div><a class="more" href="/raboty/">Наши работы →</a></div>
  <div class="catgrid">%s</div>
</div></section>""" % "".join(cat_tile(c) for c in top_sorted)

try_block = """<section class="section" style="background:var(--bg-2);border-block:1px solid var(--border)"><div class="wrap">
  <span class="eyebrow">Примерка</span>
  <h2>Посмотрите рисунок на своей мебели</h2>
  <div class="grid cards3" style="margin-top:24px">
    <a class="try" href="/primerka-skinali/"><span class="im"><img loading="lazy" src="%(sk)s" alt=""></span><span class="body"><b>Фартук для кухни</b><div class="muted">Цвет кухни и рисунок</div></span></a>
    <a class="try" href="/primerka-shkaf/"><span class="im"><img loading="lazy" src="/assets/closet/img/ds/st1_01.jpg" alt=""></span><span class="body"><b>Шкаф-купе</b><div class="muted">Рисунок на двери</div></span></a>
    <a class="try" href="/grid/"><span class="im"><img loading="lazy" src="/assets/grit/img/ds/st1_11.jpg" alt=""></span><span class="body"><b>Пескоструй на стекло</b><div class="muted">Фасад или шкаф, матовое стекло</div></span></a>
  </div>
</div></section>""" % {"sk": "/assets/img/kitchen2.webp"}

newest = sorted(valid_ids, key=lambda i: -i)[:16]
newest_ims = [im for im in images if im["id"] in set(newest)]
newest_ims.sort(key=lambda x: -x["id"])
new_block = """<section class="section"><div class="wrap">
  <div class="section-head"><div><span class="eyebrow">Каталог</span><h2>Новинки</h2></div><a class="more" href="/vse/">Все изображения →</a></div>
  <div class="masonry">%s</div>
</div></section>""" % "".join(mcard(im) for im in newest_ims)

write("index.html", parts.page(
    "ДЕКА — скинали, фрески, фотопечать и пескоструй на стекле",
    "Каталог изображений для скинали, фресок и пескоструйных рисунков. Онлайн-примерка на кухню, шкаф-купе и фасады.",
    hero + cats_block + try_block + new_block, active="cat"))

# ---------- category pages ----------
for cid in cats:
    if not cat_valid(cid):
        continue
    ims = sorted(valid_by_cat.get(cid, []), key=lambda x: x["id"])
    kids = [k for k in children.get(cid, []) if cat_valid(k)]
    kids_html = ""
    if kids:
        kids_html = '<h2 style="margin-top:34px">Подкатегории</h2><div class="catgrid" style="margin-top:16px">%s</div>' % "".join(cat_tile(k) for k in kids)
    gallery = '<div class="masonry" style="margin-top:26px">%s</div>' % "".join(mcard(im) for im in ims) if ims else '<p class="muted" style="margin-top:20px">В этой категории пока нет изображений — смотрите подкатегории выше.</p>'
    body = """<section class="section"><div class="wrap">
      %s
      <div class="section-head"><div><span class="eyebrow">Каталог</span><h1>%s</h1><p class="muted">%d изображений</p></div>
      </div>
      %s
    </div></section>""" % (breadcrumb(cid), parts.esc(cats[cid]["title"]), count_cat(cid), kids_html + gallery)
    write("c/%d/index.html" % cid, parts.page(
        "%s — каталог ДЕКА" % cats[cid]["title"],
        "%s: изображения для скинали и декора стекла, примерка онлайн." % cats[cid]["title"],
        body, active="cat"))

# ---------- image pages ----------
for im in images:
    if im["id"] not in valid_ids:
        continue
    cid = im["cat"]
    rel = [x for x in sorted(valid_by_cat.get(cid, []), key=lambda y: y["id"]) if x["id"] != im["id"]][:8]
    rel_html = ""
    if rel:
        rel_html = '<h2 style="margin-top:40px">Ещё в категории</h2><div class="masonry" style="margin-top:16px">%s</div>' % "".join(mcard(x) for x in rel)
    c = parts.CONTACTS
    qs = "?img=" + urllib.parse.quote(media(im["thumb"]), safe="") + "&code=" + urllib.parse.quote(str(im["code"]), safe="")
    try_links = ('<a class="btn btn-ghost" href="/primerka-skinali/%s">Примерить на кухню</a>'
                 '<a class="btn btn-ghost" href="/primerka-shkaf/%s">Примерить на шкаф</a>'
                 '<a class="btn btn-ghost" href="/grid/%s">Примерить пескоструй</a>') % (qs, qs, qs)
    body = """<section class="section"><div class="wrap">
      %s
      <div class="detail">
        <div class="ph"><img src="%s" alt="%s"></div>
        <div>
          <span class="eyebrow">Рисунок</span>
          <h1 style="margin-top:6px">%s</h1>
          <p class="muted">%s</p>
          <a class="btn btn-primary" href="tel:%s">Заказать: %s</a>
          <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:12px">
            %s
            <a class="btn btn-ghost" href="mailto:%s?subject=Заказ рисунка %s">Написать на почту</a>
          </div>
          <p class="muted" style="margin-top:16px;font-size:13.5px">Скажите нам номер «%s» — подберём размер и изготовим.</p>
        </div>
      </div>
      %s
    </div></section>""" % (
        breadcrumb(cid, im["code"]), media(im["thumb"]), parts.esc(im["code"]),
        parts.esc(im["code"]), parts.esc(cats.get(cid, {}).get("title", "")),
        c["mob_tel"], c["mob_disp"], try_links, c["email"], parts.esc(im["code"]),
        parts.esc(im["code"]), rel_html)
    write("i/%d/index.html" % im["id"], parts.page(
        "%s — %s | ДЕКА" % (im["code"], cats.get(cid, {}).get("title", "")),
        "Рисунок %s для декора стекла. Примерка и заказ." % im["code"], body, active="cat"))

# ---------- all images (paginated) ----------
VSE_PER = 180
all_ims = sorted([im for im in images if im["id"] in valid_ids], key=lambda x: x["id"])
vse_total = len(all_ims)
vse_pages = (vse_total + VSE_PER - 1) // VSE_PER


def vse_url(n):
    return "/vse/" if n == 1 else "/vse/%d/" % n


def vse_pager(n):
    out = ['<span class="dis">← Назад</span>' if n == 1 else '<a href="%s">← Назад</a>' % vse_url(n - 1)]
    nums = sorted(set([1, vse_pages, n - 2, n - 1, n, n + 1, n + 2]))
    nums = [k for k in nums if 1 <= k <= vse_pages]
    prev = 0
    for k in nums:
        if prev and k - prev > 1:
            out.append('<span class="dots">…</span>')
        out.append('<span class="cur">%d</span>' % k if k == n else '<a href="%s">%d</a>' % (vse_url(k), k))
        prev = k
    out.append('<span class="dis">Вперёд →</span>' if n == vse_pages else '<a href="%s">Вперёд →</a>' % vse_url(n + 1))
    return '<nav class="pager">%s</nav>' % "".join(out)


for n in range(1, vse_pages + 1):
    chunk = all_ims[(n - 1) * VSE_PER:n * VSE_PER]
    grid = '<div class="masonry" style="margin-top:26px">%s</div>' % "".join(mcard(im) for im in chunk)
    vse_body = """<section class="section"><div class="wrap">
      <div class="crumbs"><a href="/">Каталог</a> / <span>Все изображения</span></div>
      <div class="section-head"><div><span class="eyebrow">Каталог</span><h1>Все изображения</h1>
      <p class="muted">%d изображений · страница %d из %d</p></div></div>
      %s
      %s
    </div></section>""" % (vse_total, n, vse_pages, grid, vse_pager(n))
    ttl = "Все изображения — ДЕКА" if n == 1 else "Все изображения — страница %d — ДЕКА" % n
    write("vse/index.html" if n == 1 else "vse/%d/index.html" % n, parts.page(
        ttl, "Каталог всех изображений для скинали, фресок и пескоструя.", vse_body, active="cat"))

# ---------- search ----------
# (search by number removed)

# ---------- "Наши работы" ----------
works = sorted(os.listdir(os.path.join(ROOT, "assets/works"))) if os.path.isdir(os.path.join(ROOT, "assets/works")) else []
copytree(os.path.join(ROOT, "assets/works"), os.path.join(DIST, "assets/works"))
if works:
    wgrid = "".join(
        '<button class="work" data-full="/assets/works/%s" aria-label="Открыть работу"><img loading="lazy" src="/assets/works/%s" alt="Наши работы"></button>'
        % (w, w) for w in works)
    works_body = """<section class="section"><div class="wrap">
      <span class="eyebrow">Портфолио</span>
      <h1>Наши работы</h1>
      <p class="muted" style="max-width:54ch">Примеры выполненных работ: скинали, фартуки, шкафы-купе, зеркала. Нажмите на фото, чтобы открыть галерею.</p>
      <div class="works" style="margin-top:24px">%s</div>
    </div></section>
    <div class="lightbox" id="lb" hidden>
      <button class="lb-btn lb-close" id="lb-close" type="button" aria-label="Закрыть">×</button>
      <button class="lb-btn lb-prev" id="lb-prev" type="button" aria-label="Предыдущая">‹</button>
      <img id="lb-img" src="" alt="Наши работы">
      <button class="lb-btn lb-next" id="lb-next" type="button" aria-label="Следующая">›</button>
    </div>
    <script>
    (function(){
      var works = Array.prototype.slice.call(document.querySelectorAll('.work'));
      var lb = document.getElementById('lb'), img = document.getElementById('lb-img'), i = 0;
      if (!works.length || !lb) return;
      function show(k){ if (k < 0) k = works.length - 1; else if (k >= works.length) k = 0; i = k; img.src = works[i].dataset.full; lb.hidden = false; document.body.style.overflow = 'hidden'; }
      function close(){ lb.hidden = true; img.src = ''; document.body.style.overflow = ''; }
      works.forEach(function(el, k){ el.addEventListener('click', function(){ show(k); }); });
      document.getElementById('lb-close').addEventListener('click', close);
      document.getElementById('lb-next').addEventListener('click', function(e){ e.stopPropagation(); show(i + 1); });
      document.getElementById('lb-prev').addEventListener('click', function(e){ e.stopPropagation(); show(i - 1); });
      lb.addEventListener('click', function(e){ if (e.target === lb) close(); });
      document.addEventListener('keydown', function(e){
        if (lb.hidden) return;
        if (e.key === 'Escape') close();
        else if (e.key === 'ArrowRight') show(i + 1);
        else if (e.key === 'ArrowLeft') show(i - 1);
      });
    })();
    </script>""" % wgrid
    write("raboty/index.html", parts.page("Наши работы — ДЕКА", "Примеры выполненных работ салона ДЕКА.",
          works_body, active="wrk"))


# ---------- contacts ----------
c = parts.CONTACTS
contacts_body = """<section class="section"><div class="wrap">
  <span class="eyebrow">Связаться</span>
  <h1>Контакты</h1>
  <p class="muted" style="max-width:52ch">Позвоните или напишите — поможем подобрать рисунок, рассчитаем стоимость и ответим на вопросы.</p>
  <div class="grid cards3" style="margin-top:30px">
    <div class="feature"><h3>Телефоны</h3>
      <p><a href="tel:%(city_tel)s"><b>%(city_disp)s</b></a><br><span class="muted">городской</span></p>
      <p><a href="tel:%(mob_tel)s"><b>%(mob_disp)s</b></a><br><span class="muted">мобильный</span></p>
    </div>
    <div class="feature"><h3>MAX</h3>
      <p><a href="%(max_url)s" style="display:inline-flex;align-items:center;gap:8px"><img src="/assets/img/max.svg" alt="MAX" style="width:22px;height:22px;border-radius:6px;background:#fff;padding:2px"><b>MAX</b></a></p>
      <p class="muted">%(max_disp)s</p>
    </div>
    <div class="feature"><h3>Почта</h3>
      <p><a href="mailto:%(email)s"><b>%(email)s</b></a></p>
      <p class="muted">Пришлите размеры — посчитаем стоимость.</p>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(20px,4vw,50px);margin-top:44px" class="contact-cols">
    <div>
      <h2>Заказать или задать вопрос</h2>
      <form class="lead-form" method="post" action="/api/lead">
        <div class="field"><label>Как вас зовут</label><input name="name" required></div>
        <div class="field"><label>Телефон или e-mail</label><input name="contact" required></div>
        <div class="field"><label>Сообщение</label><textarea name="message" rows="4" placeholder="Например: хочу рисунок 5132 на фартук 2.4 м"></textarea></div>
        <input type="text" name="company" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">
        <div class="field" style="display:flex;gap:10px;align-items:center"><input type="checkbox" name="agree" required style="width:auto"><label style="margin:0">Согласен на обработку персональных данных</label></div>
        <button class="btn btn-primary" type="submit">Отправить</button>
        <p class="muted" style="font-size:13px;margin-top:12px">Форма защищена от спама. Если не отправится — просто позвоните.</p>
      </form>
    </div>
    <div>
      <h2>Как заказать</h2>
      <p class="muted">Сообщите номер рисунка и размеры (или пришлите фото места) — рассчитаем стоимость и сроки. Замер и консультация.</p>
      <p><a class="btn btn-ghost" href="tel:%(mob_tel)s">Позвонить %(mob_disp)s</a></p>
    </div>
  </div>
</div></section>""" % c
write("kontakty/index.html", parts.page("Контакты — ДЕКА", "Телефоны, мессенджеры и почта салона ДЕКА.",
      contacts_body, active="kt"))

# ---------- 404 ----------
notfound_body = """<section class="section"><div class="wrap" style="text-align:center;padding:64px 0">
  <span class="eyebrow">Ошибка 404</span>
  <h1 style="font-size:clamp(40px,9vw,88px);line-height:1.05;margin:10px 0 8px">Страница не найдена</h1>
  <p class="lead" style="max-width:42ch;margin:0 auto 26px">Возможно, ссылка устарела или страница была перемещена. Вернитесь в каталог или напишите нам.</p>
  <p><a class="btn btn-primary" href="/">Перейти в каталог</a> <a class="btn btn-ghost" href="/kontakty/">Связаться</a></p>
</div></section>"""
write("404.html", parts.page("Страница не найдена — ДЕКА", "Страница не найдена.", notfound_body))

# ---------- sitemap ----------
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in ["/", "/raboty/", "/kontakty/", "/primerka-skinali/", "/primerka-shkaf/", "/grid/"]:
    sm.append("<url><loc>%s%s</loc></url>" % (SITE_URL, u))
for n in range(1, vse_pages + 1):
    sm.append("<url><loc>%s%s</loc></url>" % (SITE_URL, vse_url(n)))
for cid in cats:
    if cat_valid(cid):
        sm.append("<url><loc>%s/c/%d/</loc></url>" % (SITE_URL, cid))
for im in images:
    if im["id"] in valid_ids:
        sm.append("<url><loc>%s/i/%d/</loc></url>" % (SITE_URL, im["id"]))
sm.append("</urlset>")
write("sitemap.xml", "\n".join(sm))
write("robots.txt", "User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: "+SITE_URL+"/sitemap.xml\n")

n_files = sum(len(f) for _, _, f in os.walk(DIST))
print("site: images=%d categories=%d files=%d" % (len(valid_ids), n_cat, n_files))
