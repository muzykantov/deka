# Shared page chrome for the DEKA static site.
import html, os

ROOT = os.path.dirname(os.path.abspath(__file__))


def asset(p):
    fp = os.path.join(ROOT, p.lstrip("/"))
    try:
        v = int(os.path.getmtime(fp))
    except OSError:
        v = 0
    return "%s?v=%d" % (p, v)

CONTACTS = {
    "city_disp": "+7 (3822) 250-310",
    "city_tel": "+73822250310",
    "mob_disp": "+7 906 949-70-71",
    "mob_tel": "+79069497071",
    "max_disp": "+7 906 949-70-91",
    "max_url": "https://max.ru/",
    "email": "e24box@mail.ru",
}

NAV = [
    ("Каталог", "/", "cat"),
    ("Работы", "/raboty/", "wrk"),
    ("Фартук", "/primerka-skinali/", "sk"),
    ("Шкаф-купе", "/primerka-shkaf/", "sh"),
    ("Пескоструй", "/grid/", "gr"),
    ("Контакты", "/kontakty/", "kt"),
]


def esc(s):
    return html.escape(str(s))


def header(active=""):
    nav = "".join(
        '<a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if key == active else "", esc(label))
        for label, href, key in NAV
    )
    return """<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="/">
      <img class="mark" src="/assets/img/logo-mark.png" alt="ДЕКА">
      <span><span class="word">ДЕКА</span><span class="tag">Салон декорирования стекла и зеркала</span></span>
    </a>
    <nav class="nav">%s</nav>
    <button class="icon-btn" data-theme-toggle aria-label="Тема"></button>
    <button class="icon-btn burger" aria-label="Меню"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button>
  </div>
</header>""" % nav


def footer():
    c = CONTACTS
    return """<footer class="site-footer">
  <div class="wrap foot">
    <div>
      <img class="logo only-light" src="/assets/img/logo.png" alt="ДЕКА — салон декорирования стекла и зеркала">
      <img class="logo only-dark" src="/assets/img/logo-white.png" alt="ДЕКА — салон декорирования стекла и зеркала">
      <p class="muted" style="max-width:34ch">Скинали, фрески, фотопечать и пескоструйные рисунки на стекле. Каталог изображений и онлайн-примерка.</p>
      <p class="script" style="font-size:22px;margin:0">Arte, labore et scientia</p>
    </div>
    <div>
      <h4>Разделы</h4>
      <a href="/">Каталог</a>
      <a href="/vse/">Все изображения</a>
      <a href="/raboty/">Наши работы</a>
      <a href="/primerka-skinali/">Примерка фартука</a>
      <a href="/primerka-shkaf/">Примерка шкафа</a>
      <a href="/grid/">Пескоструй</a>
    </div>
    <div>
      <h4>Контакты</h4>
      <a href="tel:%(city_tel)s">%(city_disp)s</a>
      <a href="tel:%(mob_tel)s">%(mob_disp)s</a>
      <a href="%(max_url)s" class="with-max"><img class="maxi" src="/assets/img/max.svg" alt="MAX"> MAX · %(max_disp)s</a>
      <a href="mailto:%(email)s">%(email)s</a>
    </div>
  </div>
  <div class="wrap legal">
    <span>© %(year)s Салон декорирования стекла и зеркала «ДЕКА»</span>
  </div>
</footer>""" % dict(c, year="2026")


def page(title, desc, body, active="", extra_head="", body_class=""):
    return """<!doctype html><html lang="ru" data-theme="light"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="icon" href="/assets/img/logo-mark.png">
<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="%s">
<link rel="stylesheet" href="%s">
<script src="%s"></script>
%s</head>
<body%s>
%s
%s
%s</body></html>""" % (
        esc(title), esc(desc),
        asset("/assets/fonts/manrope-cyrillic.woff2"), asset("/assets/fonts/fonts.css"),
        asset("/assets/theme.css"), asset("/assets/theme.js"),
        extra_head, body_class, header(active), body, footer())
