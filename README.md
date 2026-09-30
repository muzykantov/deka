# ДЕКА — сайт салона декорирования стекла и зеркала

Статический сайт каталога скинали/фресок/пескоструйных рисунков с онлайн‑примерками.
Живёт на `https://dekasteklo.ru` (и `https://deka.su`). Картинки каталога хранятся на
сервере (`/media/...`) и в репозиторий не входят.

## Что внутри

- `export.py` — экспорт каталога из базы (Phoca Gallery) в `data/catalog.json`.
- `build_site.py` — генерация каталога: главная, категории, страницы картинок, «Наши работы», sitemap.
- `build_ctors.py` / `build_closet.py` / `build_grit.py` — примерки (фартук, шкаф‑купе, пескоструй).
- `parts.py` — общий каркас страниц (шапка/подвал/контакты).
- `fetch_fonts.py` — загрузка и self-host шрифтов (Manrope, Unbounded, Caveat).
- `form/server.py` — эндпоинт формы заявок (honeypot, rate-limit, опц. Turnstile/Telegram).
- `assets/` — тема (светлая/тёмная), шрифты, логотип, ассеты и данные примерок.
- `data/catalog.json` — выгрузка каталога (категории + картинки).

## Сборка

```bash
python3 fetch_fonts.py      # один раз: шрифты в assets/fonts
python3 export.py           # data/catalog.json из БД (нужен доступ к базе)
python3 build_site.py
python3 build_ctors.py
python3 build_closet.py
python3 build_grit.py
# результат в dist/ (в репозиторий не коммитится)
```

Абсолютный адрес сайта для sitemap задаётся переменной `DEKA_SITE_URL`
(по умолчанию `https://dekasteklo.ru`).

## Заметки

- Медиа (изображения каталога) обслуживает сервер: `https://dekasteklo.ru/media/...`.
- Форма заявок проксируется на `form/server.py` через nginx (`/api/lead`).
- Для деплоя на GitHub Pages нужен отдельный билд с абсолютным медиа‑хостом.
