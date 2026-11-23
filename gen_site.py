# -*- coding: utf-8 -*-
"""Собирает мини-сайт «Караокеры vs рокеры» из markdown и готовых блоков.

Запуск:  python gen_site.py
Правит тексты — PROEKT-27-11.md и RUNBOOK.md рядом в папке проекта.
"""
from pathlib import Path
import re
import shutil
import markdown

BASE = Path(__file__).resolve().parent          # ...\music-party\site
PROJ = BASE.parent                              # ...\music-party
OUT = BASE

NAV = [
    ("index.html", "Обзор"),
    ("tekhproekt.html", "Техпроект"),
    ("ranbook.html", "Ранбук"),
    ("sxema.html", "Схема"),
    ("sxema-interaktiv.html", "Интерактив"),
    ("pult.html", "Пульт"),
    ("kartochki.html", "Карточки"),
    ("uchastnikam.html", "Участникам"),
]

TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Караокеры vs рокеры</title>
<meta name="description" content="Технический проект вечера «Караокеры vs рокеры», лофт ОПЕРА, 27 ноября 2026.">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top"><div class="top-in">
  <div class="brand">КАРАОКЕРЫ <span>vs</span> РОКЕРЫ · 27.11</div>
  <nav class="main">{nav}</nav>
</div></header>
<div class="wrap">
{body}
<footer class="bot">
  Лофт «ОПЕРА», Берсеневский пер. 5 стр. 4 · пятница, 27 ноября 2026 · сбор 18:30, начало 19:00
  <br>Сайт собран из рабочих файлов проекта. Тексты правятся в <code>PROEKT-27-11.md</code> и <code>RUNBOOK.md</code>, затем пересборка: <code>python gen_site.py</code>.
</footer>
</div>
</body>
</html>
"""

def nav_html(current):
    parts = []
    for href, label in NAV:
        cls = ' class="on"' if href == current else ""
        parts.append(f'<a href="{href}"{cls}>{label}</a>')
    return "".join(parts)

def page(name, title, body):
    (OUT / name).write_text(
        TEMPLATE.format(title=title, nav=nav_html(name), body=body), encoding="utf-8")
    print("готово:", name)

MD = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "attr_list", "toc"])

def normalize_lists(text):
    """Markdown требует пустую строку перед списком. Правки руками её часто теряют —
    поэтому достраиваем её перед каждым списком, который идёт сразу за текстом."""
    out = []
    prev = ""
    for line in text.split("\n"):
        is_item = re.match(r"^\s*(?:[-*+]\s|\d+\.\s)", line) is not None
        prev_is_item = re.match(r"^\s*(?:[-*+]\s|\d+\.\s)", prev) is not None
        prev_is_special = prev.lstrip().startswith(("|", "#", ">")) or not prev.strip()
        if is_item and prev.strip() and not prev_is_item and not prev_is_special:
            out.append("")
        out.append(line)
        prev = line
    return "\n".join(out)

def md_to_html(text):
    text = normalize_lists(text)
    MD.reset()
    html = MD.convert(text)
    # чек-листы "- [ ] пункт" -> аккуратные квадратики
    html = re.sub(r'<li>\[ \]\s*(.+?)</li>', r'<li class="task"><span class="box"></span><span>\1</span></li>', html, flags=re.S)
    html = re.sub(r'<li>\[[xх]\]\s*(.+?)</li>', r'<li class="task done"><span class="box"></span><span>\1</span></li>', html, flags=re.S)
    return html

def md_page(src, name, title):
    text = (PROJ / src).read_text(encoding="utf-8")
    body = md_to_html(text)
    page(name, title, f'<article>\n{body}\n</article>')

# ---------- 1. Техпроект и ранбук из markdown ----------
md_page("PROEKT-27-11.md", "tekhproekt.html", "Технический проект")
md_page("RUNBOOK.md", "ranbook.html", "Ранбук вечера")

# ---------- 2. Статическая схема ----------
src_svg = (PROJ / "sxema-signal.html").read_text(encoding="utf-8")
m = re.search(r"<svg\b.*?</svg>", src_svg, re.S)
svg = m.group(0) if m else "<p>Схема не найдена.</p>"
svg = svg.replace('<svg ', '<svg style="width:100%;height:auto;min-width:900px" ', 1)
sxema_body = f"""
<section class="hero" style="padding-bottom:8px">
  <div class="kicker">Схема подключения</div>
  <h1>Что куда втыкается</h1>
  <p class="lead">Источники → пульт FLOW 8 → акустика; отдельно видео-тракт, две линии питания и сеть с VPN.
  Внизу — три главных вывода: каналы, питание, YouTube.</p>
</section>
<div style="border:1px solid var(--line);border-radius:14px;background:#020617;padding:10px;overflow:auto">
{svg}
</div>
<div class="tiles">
  <div class="tile"><h3>Каналы — впритык</h3><p>2 микрофона + 3 гитары + стерео-минус = 7 из 8. Запаса нет: либо минус в моно, либо сабмикшер.</p></div>
  <div class="tile"><h3>Питание и земля</h3><p>0,9–1,4 кВт на аудио-видео. Две линии, три удлинителя 1,5 мм², два пилота. «Щиплет» микрофон — нет земли.</p></div>
  <div class="tile"><h3>YouTube без VPN</h3><p>В каталоге 1954 песни, готовый видео-ID у 12. Основной путь — 60 минусовок офлайн, резерв — свой WireGuard на VPS.</p></div>
</div>
<p style="color:var(--dim);font-size:13.5px">Открыть интерактивную версию: <a href="sxema-interaktiv.html">схема с переключением вариантов</a>.</p>
"""
page("sxema.html", "Схема подключения", sxema_body)

# ---------- 3. Обзор ----------
index_body = """
<section class="hero">
  <div class="kicker">Технический проект · лофт ОПЕРА · пятница</div>
  <h1>Караокеры vs рокеры<br>27 ноября 2026</h1>
  <p class="lead">Всё, что нужно, чтобы вечер не встал из-за кабеля, канала или YouTube: проект,
  тайминг, схема, пульт ведущего и карточки для печати — на одном сайте.</p>
  <div class="facts">
    <div class="fact"><b>18:30</b><span>сбор гостей</span></div>
    <div class="fact"><b>19:00</b><span>начало программы</span></div>
    <div class="fact"><b>02:00</b><span>планируемый финал</span></div>
    <div class="fact"><b>25</b><span>максимум гостей</span></div>
    <div class="fact"><b>7 из 8</b><span>каналов пульта занято</span></div>
  </div>
</section>

<div class="tiles">
  <a class="tile" href="tekhproekt.html"><h3>Технический проект</h3>
    <p>Состав оборудования, канальная карта FLOW 8, электрика, YouTube и VPN, 12 рисков с планами Б.</p></a>
  <a class="tile" href="ranbook.html"><h3>Ранбук вечера</h3>
    <p>Тайминг по часам, роли, чек-листы за неделю / за день / за час и что делать, если что-то сломалось.</p></a>
  <a class="tile" href="sxema.html"><h3>Схема подключения</h3>
    <p>Аудио, видео, питание и сеть на одной картинке — с пометками, где DI-боксы и пилоты.</p></a>
  <a class="tile" href="sxema-interaktiv.html"><h3>Интерактивная схема</h3>
    <p>Переключи вариант — и увидишь, что происходит с каналами, питанием и картинкой на экране.</p></a>
  <a class="tile" href="pult.html"><h3>Пульт ведущего</h3>
    <p>Слайды на проектор: ← → блоки, N — заметки, T — таймер, B — затемнение, P — проекторный режим.</p></a>
  <a class="tile" href="kartochki.html"><h3>Карточки для печати</h3>
    <p>Шесть стопок: язык, настроение, жанр, десятилетие, артисты, «как петь». Ctrl+P на A4.</p></a>
  <a class="tile" href="uchastnikam.html"><h3>Участникам</h3>
    <p>Что взять с собой, что оставить дома, во сколько и куда приходить — короткий список без техники.</p></a>
</div>

<article style="max-width:880px">
  <h2>Три вещи, из-за которых вечер обычно и встаёт</h2>
  <p><strong>1. Каналы.</strong> По документации FLOW 8 — 8 входов: 2 XLR с фантомом, 2 combo, 2 стереоканала,
  Hi-Z на линейных. Два микрофона, три гитары и стерео-минус занимают семь. Восьмой держим под резерв.</p>
  <p><strong>2. YouTube.</strong> В каталоге сайта 1954 песни, и только у 12 есть готовый видео-ID: остальные
  кнопки открывают поиск YouTube. В лофте VPN нет, поэтому основные минусовки — офлайн-файлами, VPN на VPS — резерв.</p>
  <p><strong>3. Питание.</strong> Аудио-видео контур — около 0,9–1,4 кВт. Нужны две независимые линии,
  три удлинителя 1,5 мм² и два пилота. Свет и чайник — не наша линия.</p>

  <h2>Как это править</h2>
  <p>Тексты живут в двух файлах проекта: <code>PROEKT-27-11.md</code> (технический проект) и
  <code>RUNBOOK.md</code> (тайминг и чек-листы). Правишь markdown — я пересобираю сайт одной командой,
  и страницы обновляются. Схема, пульт и карточки — отдельные файлы, их правка тоже не ломает остальное.</p>
</article>
"""
page("index.html", "Технический проект вечера", index_body)

# ---------- 4. Пульт и карточки: копия + ссылка назад ----------
BACK = """
<a href="index.html" style="position:fixed;left:14px;bottom:14px;z-index:60;
   background:rgba(18,22,29,.92);border:1px solid #2b3542;color:#e2b25c;border-radius:999px;
   padding:7px 14px;font:13px/1 'Segoe UI',Roboto,sans-serif;text-decoration:none">← проект</a>
"""
pult = (PROJ / "pult-vedushchego.html").read_text(encoding="utf-8")
if "← проект" not in pult:
    pult = pult.replace("</body>", BACK + "</body>")
(OUT / "pult.html").write_text(pult, encoding="utf-8")
print("готово: pult.html")

cards = (PROJ / "kartochki.html").read_text(encoding="utf-8")
if "site-nav-injected" not in cards:
    nav = ('<div class="site-nav-injected" style="max-width:194mm;margin:6mm auto 0;display:flex;'
           'gap:10px;align-items:center;font:13px/1.4 \'Segoe UI\',Roboto,sans-serif">'
           '<a href="index.html" style="color:#8a6100">← проект</a>'
           '<span style="color:#777">Карточки: печать A4, книжная, масштаб 100%, резать по пунктирным линиям</span>'
           '</div>')
    cards = cards.replace("</head>", "</head>", 1)
    cards = re.sub(r"(<body[^>]*>)", r"\1" + nav.replace("\\", "\\\\"), cards, count=1)
    cards = cards.replace("</style>", "@media print{.site-nav-injected{display:none}}\n</style>", 1)
(OUT / "kartochki.html").write_text(cards, encoding="utf-8")
print("готово: kartochki.html")

# ---------- 4b. Участникам: чек-лист сборов ----------
ITEMS = [
    ("Стас", [
        "Микшерный пульт (FLOW 8)",
        "Удлинитель минимум на 3 розетки — 2 шт.",
        "Пюпитер",
        "Микрофонная стойка",
        "Микрофон",
        "Провода для микрофона",
        "Гитара",
        "Струны (запасной комплект)",
        "Каподастер",
        "Медиаторы",
        "Провод для гитары",
        "Педаль эффектов",
        "Подставка для гитары",
    ]),
    ("Павел", [
        "Ноутбук",
        "HDMI-провод",
        "Провод для зарядки планшета",
        "Планшет",
        "Пюпитер",
        "Микрофонная стойка",
        "Микрофон",
        "Гитара",
        "Струны (запасной комплект)",
        "Каподастер",
        "Медиаторы",
        "Педаль эффектов",
        "Подставка для гитары",
    ]),
]

def items_html():
    out = []
    total = 0
    for person, rows in ITEMS:
        out.append(f"<h3>{person}</h3>")
        out.append('<ul class="pl">')
        for name in rows:
            total += 1
            out.append(f'<li data-k="{person}:{name}"><span class="bx"></span><span class="tx">{name}</span></li>')
        out.append("</ul>")
    return "\n".join(out), total

items_body, items_total = items_html()
uch = f"""
<section class="hero" style="padding-bottom:10px">
  <div class="kicker">Участникам</div>
  <h1>Кто что приносит</h1>
  <p class="lead">Список сборов: отмечай галочкой, что уже в машине. Позиции добавляются по мере диктовки —
  страница обновляется вместе с сайтом, так что ссылку можно держать открытой на телефоне.</p>
</section>

<article style="max-width:820px;padding-top:6px">
  <p class="pl-sum">Всего позиций: <b id="pl-total">{items_total}</b> · отмечено: <b id="pl-done">0</b></p>
  {items_body}
  <p style="color:var(--dim);font-size:13.5px">Галочки хранятся в этом браузере: у каждого своя копия списка.
  Если пункт нужно закрепить за конкретным человеком — скажи, подпишу.</p>
</article>

<script>
const LIST = document.querySelectorAll('.pl li');
const KEY = 'opera-27-11-packing';
const saved = JSON.parse(localStorage.getItem(KEY) || '[]');
function refresh(){{
  const done = document.querySelectorAll('.pl li.done').length;
  document.getElementById('pl-done').textContent = done;
}}
LIST.forEach(li=>{{
  if(saved.includes(li.dataset.k)) li.classList.add('done');
  li.addEventListener('click', ()=>{{
    li.classList.toggle('done');
    const now = [...document.querySelectorAll('.pl li.done')].map(x=>x.dataset.k);
    localStorage.setItem(KEY, JSON.stringify(now));
    refresh();
  }});
}});
refresh();
</script>
"""
page("uchastnikam.html", "Участникам: что взять", uch)

# ---------- 5. Служебное ----------
(OUT / ".nojekyll").write_text("", encoding="utf-8")
print("готово: .nojekyll")
