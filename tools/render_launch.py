"""Render Heth Spices launch-week Instagram assets (HTML -> Chrome -> JPEG)."""
import os, base64, math, json
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path('/home/claude/hs')
FONTS = ROOT / 'fonts/node_modules/@fontsource'
OUT = ROOT / 'launch'
HTML = ROOT / 'launch_html'
OUT.mkdir(exist_ok=True); HTML.mkdir(exist_ok=True)

def uri(p, mime=None):
    p = Path(p)
    mime = mime or {'.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2'}[p.suffix.lower()]
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"

def face(family, path, weight, style='normal'):
    return f"@font-face{{font-family:'{family}';src:url('{uri(path)}') format('woff2');font-weight:{weight};font-style:{style};font-display:block}}"

FONT_CSS = '\n'.join([
    *[face('Playfair', FONTS / f'playfair-display/files/playfair-display-latin-{w}-normal.woff2', w) for w in (600, 700, 800)],
    *[face('Playfair', FONTS / f'playfair-display/files/playfair-display-latin-{w}-italic.woff2', w, 'italic') for w in (500, 700)],
    *[face('Hind', FONTS / f'hind-vadodara/files/hind-vadodara-latin-{w}-normal.woff2', w) for w in (400, 500, 600, 700)],
    *[face('Hind', FONTS / f'hind-vadodara/files/hind-vadodara-gujarati-{w}-normal.woff2', w) for w in (400, 600, 700)],
    *[face('Caveat', FONTS / f'caveat/files/caveat-latin-{w}-normal.woff2', w) for w in (600, 700)],
])

LOGO = uri(ROOT / 'brand/logo-circle.png')
LABELS = ROOT / 'labels'
def label(name):
    return uri(LABELS / name)

PAPER = "data:image/svg+xml;base64," + base64.b64encode(b"""<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .45  0 0 0 0 .28  0 0 0 0 .12  0 0 0 .07 0'/></filter><rect width='100%' height='100%' filter='url(#n)'/></svg>""").decode()

BASE_CSS = f"""
{FONT_CSS}
:root{{--maroon:#882C0D;--deep:#5A1B08;--cream:#FBF4E6;--paper:#F6EAD3;--turmeric:#D99A2E;--chilli:#B83A1C;--leaf:#3F6B34;--ink:#2E1A10;--muted:#7A5A45}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:var(--w);height:var(--h);overflow:hidden}}
body{{font-family:'Hind',sans-serif;color:var(--ink);background:var(--cream);-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}}
.f{{position:relative;width:var(--w);height:var(--h);overflow:hidden}}
.paper{{background:var(--cream) url('{PAPER}');}}
.dark{{background:radial-gradient(120% 90% at 50% 30%,#93330F 0%,var(--maroon) 40%,var(--deep) 100%);color:var(--cream)}}
.dark::after{{content:'';position:absolute;inset:0;background:url('{PAPER}');opacity:.55;mix-blend-mode:multiply;pointer-events:none}}
.frame{{position:absolute;inset:34px;border:2.5px solid currentColor;border-radius:26px;opacity:.9;pointer-events:none}}
.frame::after{{content:'';position:absolute;inset:9px;border:1px solid currentColor;border-radius:19px;opacity:.55}}
.paper .frame{{color:var(--maroon)}}
.dark .frame{{color:var(--turmeric)}}
.eyebrow{{font-family:'Hind';font-weight:600;font-size:25px;letter-spacing:.24em;text-transform:uppercase}}
.disp{{font-family:'Playfair',serif;font-weight:800;line-height:1.04;letter-spacing:-.01em;text-wrap:balance}}
.ital{{font-family:'Playfair',serif;font-style:italic;font-weight:500}}
.hand{{font-family:'Caveat',cursive;font-weight:700}}
.body{{font-size:34px;line-height:1.42;font-weight:400}}
.content{{position:absolute;inset:0;z-index:2;display:flex;flex-direction:column}}
.logo{{width:var(--ls);height:var(--ls);border-radius:50%;background:url('{LOGO}') center/cover;box-shadow:0 10px 30px rgba(40,10,0,.28)}}
.tag{{display:inline-flex;align-items:center;gap:12px;font-weight:600;font-size:26px;letter-spacing:.06em;padding:10px 20px 8px;border-radius:999px}}
.vegdot{{width:26px;height:26px;border:2.5px solid var(--leaf);display:inline-grid;place-items:center;border-radius:4px;background:#fff}}
.vegdot i{{width:12px;height:12px;border-radius:50%;background:var(--leaf)}}
.swipe{{font-family:'Hind';font-weight:600;font-size:24px;letter-spacing:.2em;text-transform:uppercase;opacity:.85}}
.labelimg{{display:block;width:100%;height:auto;filter:drop-shadow(0 14px 22px rgba(60,20,0,.22))}}
.num{{font-family:'Playfair';font-style:italic;font-weight:700;color:var(--turmeric);line-height:.9}}
.rule{{height:2px;background:linear-gradient(90deg,transparent,currentColor 15%,currentColor 85%,transparent);opacity:.35}}
"""

def diya(size=260, glow=True):
    g = f"<div style='position:absolute;left:50%;top:38%;width:{size*1.9}px;height:{size*1.9}px;transform:translate(-50%,-50%);background:radial-gradient(circle,rgba(255,196,90,.55) 0%,rgba(255,170,60,.18) 38%,transparent 66%);'></div>" if glow else ''
    return f"""<div style='position:relative;width:{size}px;height:{size}px;margin:0 auto'>{g}
<svg viewBox='0 0 200 200' width='{size}' height='{size}' style='position:relative'>
<defs><radialGradient id='fl' cx='50%' cy='70%' r='60%'><stop offset='0' stop-color='#FFF6D6'/><stop offset='.45' stop-color='#FFC94D'/><stop offset='1' stop-color='#E8731C'/></radialGradient>
<linearGradient id='bw' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#E2A23A'/><stop offset='1' stop-color='#9A4A12'/></linearGradient></defs>
<path d='M100 28 C112 52 122 66 120 84 C118 100 108 108 100 108 C92 108 82 100 80 84 C78 66 88 52 100 28 Z' fill='url(#fl)'/>
<path d='M100 62 C105 74 108 82 107 90 C106 98 103 101 100 101 C97 101 94 98 93 90 C92 82 95 74 100 62 Z' fill='#FFF8E4' opacity='.9'/>
<path d='M28 112 Q100 104 172 112 Q166 160 100 166 Q34 160 28 112 Z' fill='url(#bw)'/>
<path d='M28 112 Q100 120 172 112' stroke='#F6D27A' stroke-width='4' fill='none'/>
<g fill='#F6D27A'><circle cx='62' cy='138' r='4'/><circle cx='82' cy='145' r='4'/><circle cx='100' cy='147' r='4'/><circle cx='118' cy='145' r='4'/><circle cx='138' cy='138' r='4'/></g>
</svg></div>"""

def rangoli(size=900, color='#D99A2E', opacity=.22):
    parts = []
    c = size / 2
    for ring, (n, r, rad) in enumerate([(12, .18, 9), (24, .27, 7), (36, .36, 6), (48, .45, 5)]):
        for k in range(n):
            a = 2 * math.pi * k / n + ring * .13
            x, y = c + math.cos(a) * r * size, c + math.sin(a) * r * size
            parts.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{rad}'/>")
    for k in range(12):
        a = 2 * math.pi * k / 12
        x, y = c + math.cos(a) * .1 * size, c + math.sin(a) * .1 * size
        parts.append(f"<ellipse cx='{x:.1f}' cy='{y:.1f}' rx='{.05*size:.0f}' ry='{.018*size:.0f}' transform='rotate({math.degrees(a):.1f} {x:.1f} {y:.1f})'/>")
    return f"<svg viewBox='0 0 {size} {size}' width='{size}' height='{size}' fill='{color}' opacity='{opacity}'>{''.join(parts)}</svg>"

def icon(kind, stroke='#FBF4E6', w=10):
    s = f"fill='none' stroke='{stroke}' stroke-width='{w}' stroke-linecap='round' stroke-linejoin='round'"
    d = {
        'menu': f"<rect x='60' y='40' width='120' height='160' rx='14' {s}/><path d='M88 82h64M88 116h64M88 150h40' {s}/>",
        'order': f"<path d='M50 70a20 20 0 0 1 20-20h100a20 20 0 0 1 20 20v62a20 20 0 0 1-20 20h-58l-38 32v-32h-4a20 20 0 0 1-20-20z' {s}/><path d='M86 102h68' {s}/>",
        'jain': f"<path d='M120 196c0-60 0-90 0-110' {s}/><path d='M120 120c-46-4-66-34-62-78 44 2 66 30 62 78z' {s}/><path d='M120 150c40-4 58-30 54-66-38 2-58 26-54 66z' {s}/>",
        'reviews': f"<path d='M120 196s-70-42-70-96c0-28 20-46 42-46 14 0 24 8 28 18 4-10 14-18 28-18 22 0 42 18 42 46 0 54-70 96-70 96z' {s}/>",
        'recipes': f"<path d='M44 112h152' {s}/><path d='M56 112c0 44 26 70 64 70s64-26 64-70' {s}/><path d='M96 92c-8-12 8-20 0-34M124 92c-8-12 8-20 0-34M152 92c-8-12 8-20 0-34' {s}/>",
        'small': f"<circle cx='120' cy='120' r='70' {s}/><path d='M120 50v-14M120 204v-14M50 120H36M204 120h-14' {s}/><circle cx='120' cy='120' r='22' {s}/>",
        'fresh': f"<path d='M70 170l100-100' {s}/><path d='M150 60c26-6 40 8 34 34l-34-34z' {s}/><circle cx='86' cy='166' r='26' {s}/>",
        'nopres': f"<circle cx='120' cy='120' r='72' {s}/><path d='M70 170L170 70' {s}/><path d='M100 92h40v60h-40z' {s}/>",
    }[kind]
    return f"<svg viewBox='0 0 240 240' width='100%' height='100%'>{d}</svg>"

def page(name, w, h, inner, cls='paper'):
    html = f"<!doctype html><html><head><meta charset='utf-8'><style>{BASE_CSS}</style></head><body style='--w:{w}px;--h:{h}px'><div class='f {cls}'>{inner}</div></body></html>"
    (HTML / f'{name}.html').write_text(html)
    return name, w, h

FRAMES = []
F = lambda *a, **k: FRAMES.append(page(*a, **k))
W, H = 1080, 1350
SW, SH = 1080, 1920

# ---------- POST 1: Meet Heth Spices ----------
F('p1-1', W, H, f"""<div class='frame'></div><div class='content' style='align-items:center;justify-content:center;text-align:center;padding:120px 110px'>
<div class='logo' style='--ls:250px;margin-bottom:56px'></div>
<div class='eyebrow' style='color:var(--turmeric);margin-bottom:34px'>Homemade Indian Spices · Mumbai</div>
<div class='disp' style='font-size:92px;color:var(--cream)'>Masalas ground the week you order them.</div>
<div class='hand' style='font-size:64px;color:var(--turmeric);margin-top:40px'>from Hetal's kitchen to yours</div>
<div class='swipe' style='position:absolute;bottom:92px;left:0;right:0;color:var(--cream)'>Swipe to meet us &rarr;</div></div>""", cls='dark')

rows = [('small', 'Small batches', "Made at home, in small batches, the way it's done in your own kitchen."),
        ('fresh', 'Freshly ground', 'Your pack is ground the week you order it.'),
        ('nopres', 'No added preservatives', 'Not in any of our masalas. Ever.')]
rows_html = ''.join(f"""<div style='display:flex;gap:40px;align-items:center'>
<div style='flex:0 0 150px;height:150px;border-radius:50%;background:var(--maroon);padding:30px'>{icon(k)}</div>
<div style='min-width:0'><div class='disp' style='font-size:56px;color:var(--maroon);margin-bottom:8px'>{t}</div><div class='body' style='color:var(--ink)'>{b}</div></div></div>""" for k, t, b in rows)
F('p1-2', W, H, f"""<div class='frame'></div><div class='content' style='padding:130px 120px 120px'>
<div class='eyebrow' style='color:var(--chilli);margin-bottom:22px'>What makes it Heth</div>
<div class='disp' style='font-size:76px;color:var(--ink);margin-bottom:70px'>Homemade, the way your kitchen would do it.</div>
<div style='flex:1;display:flex;flex-direction:column;justify-content:space-evenly'>{rows_html}</div>
<div class='hand' style='font-size:52px;color:var(--maroon);text-align:center'>made with tradition, made for you</div></div>""")

F('p1-3', W, H, f"""<div class='frame'></div><div class='content' style='padding:120px 110px 150px'>
<div class='eyebrow' style='color:var(--chilli);margin-bottom:22px'>Jain &amp; Non-Jain</div>
<div class='disp' style='font-size:72px;color:var(--ink);margin-bottom:22px'>Every pack is clearly marked.</div>
<div class='body' style='color:var(--muted);margin-bottom:46px;max-width:780px'>Look for <b style="color:var(--maroon)">J</b> or <b style="color:var(--maroon)">N.J</b> on the label, so you always know what's going into your kitchen.</div>
<div style='display:flex;flex-direction:column;gap:34px;align-items:center'>
<div style='width:660px;transform:rotate(-2deg)'><img class='labelimg' src='{label("Garam Masala.png")}'></div>
<div style='width:660px;transform:rotate(1.5deg)'><img class='labelimg' src='{label("Peri Peri Masala.png")}'></div></div>
<div style='margin-top:auto;display:flex;gap:18px;justify-content:center'>
<span class='tag' style='background:var(--maroon);color:var(--cream)'>J · 19 masalas</span>
<span class='tag' style='background:var(--paper);color:var(--maroon);border:2px solid var(--maroon)'>N.J · 3 masalas</span>
<span class='tag' style='background:var(--paper);color:var(--maroon);border:2px solid var(--maroon)'>50g · 100g · 250g</span></div></div>""")

steps = [('Open our menu', 'Tap the link in our bio.'),
         ('Pick your masalas', 'Choose a pack size: 50g, 100g or 250g.'),
         ('Send it on WhatsApp', 'Your order goes straight to Hetal, who confirms pickup or delivery.')]
steps_html = ''.join(f"""<div style='display:flex;gap:36px;align-items:flex-start'><div class='num' style='font-size:150px;flex:0 0 110px;text-align:center'>{i+1}</div>
<div style='padding-top:22px;min-width:0'><div class='disp' style='font-size:58px;color:var(--maroon);margin-bottom:6px'>{t}</div><div class='body'>{b}</div></div></div>""" for i, (t, b) in enumerate(steps))
F('p1-4', W, H, f"""<div class='frame'></div><div class='content' style='padding:130px 120px 120px'>
<div class='eyebrow' style='color:var(--chilli);margin-bottom:22px'>How to order</div>
<div class='disp' style='font-size:78px;margin-bottom:64px'>Three taps. That's it.</div>
<div style='flex:1;display:flex;flex-direction:column;justify-content:space-evenly'>{steps_html}</div>
<div class='hand' style='margin-top:auto;font-size:52px;color:var(--maroon)'>Ground fresh, packed for you.</div></div>""")

F('p1-5', W, H, f"""<div class='frame'></div><div class='content' style='align-items:center;justify-content:center;text-align:center;padding:120px 120px'>
<div class='logo' style='--ls:200px;margin-bottom:60px'></div>
<div class='disp' style='font-size:78px;color:var(--cream);margin-bottom:34px'>Follow for recipes, masala tips &amp; what's fresh this week.</div>
<div class='rule' style='width:420px;color:var(--turmeric);margin:26px 0 40px'></div>
<div class='eyebrow' style='color:var(--turmeric);margin-bottom:14px'>Order on WhatsApp</div>
<div style='font-family:Playfair;font-weight:700;font-size:64px;color:var(--cream);font-variant-numeric:tabular-nums'>+91 98204 41116</div>
<div style='font-size:36px;font-weight:500;color:var(--cream);opacity:.85;margin-top:22px'>@hethspices</div></div>""", cls='dark')

# ---------- POST 2: Menu ----------
JAIN = [('Biryani Masala', 130, 250, 615), ('Pav Bhaji Masala', 120, 230, 565), ('Chole Masala', 125, 240, 585),
        ('Sambar Masala', 99, 190, 468), ('Chaat Masala', 90, 175, 424), ('Tea Masala', 155, 300, 730),
        ('Sambhariyo', 110, 215, 517), ('Garam Masala', 120, 230, 565), ('Pani Puri Masala', 90, 175, 424),
        ('Chaas Masala', 99, 190, 468), ('Sandwich Masala', 99, 190, 468), ('Frankie Masala', 110, 215, 517),
        ('Misal Masala', 95, 185, 450), ('Peri Peri Masala', 95, 185, 450), ('Magic Masala', 95, 185, 450),
        ('Hakka Noodles Masala', 95, 185, 450), ('Kitchen King Masala', 110, 215, 517), ('Paneer Masala', 90, 175, 424),
        ('Molgapodi', 65, 125, 305)]
NONJAIN = [('Peri Peri Masala', 99, 190, 468), ('Magic Masala', 99, 190, 468), ('Hakka Noodles Masala', 99, 190, 468)]
YEARLY = [('Dhana Jeera Powder', 650), ('Dhana Jeera Powder (with Garam Masala)', 1120), ('Home Dried Haldi Powder', 750), ('Chilli Powder', 1550)]

def table(rows, title, chip, rowh=74, fs=36):
    head = f"""<div style='display:grid;grid-template-columns:1fr 130px 130px 130px;align-items:end;padding:0 8px 14px;border-bottom:3px solid var(--maroon)'>
<div class='disp' style='font-size:50px;color:var(--maroon)'>{title} <span class='tag' style='font-size:22px;vertical-align:middle;background:var(--maroon);color:var(--cream);padding:6px 14px 4px'>{chip}</span></div>
{''.join(f"<div style='text-align:right;font-weight:600;font-size:24px;letter-spacing:.12em;color:var(--muted)'>{s}</div>" for s in ('50G','100G','250G'))}</div>"""
    body = ''.join(f"""<div style='display:grid;grid-template-columns:1fr 130px 130px 130px;align-items:center;height:{rowh}px;padding:0 8px;border-bottom:1.5px dashed rgba(136,44,13,.28)'>
<div style='font-size:{fs}px;font-weight:500;white-space:nowrap'>{n}</div>
{''.join(f"<div style='text-align:right;font-size:{fs}px;font-weight:600;font-variant-numeric:tabular-nums;color:var(--ink)'>₹{p}</div>" for p in (a, b, c))}</div>""" for n, a, b, c in rows)
    return head + body

F('p2-1', W, H, f"""<div class='frame'></div><div class='content' style='align-items:center;justify-content:center;text-align:center;padding:120px'>
<div class='logo' style='--ls:210px;margin-bottom:54px'></div>
<div class='eyebrow' style='color:var(--turmeric);margin-bottom:30px'>Save this for your next order</div>
<div class='disp' style='font-size:118px;color:var(--cream)'>The Heth Spices Menu</div>
<div class='rule' style='width:460px;color:var(--turmeric);margin:46px 0'></div>
<div style='font-size:40px;font-weight:500;color:var(--cream)'>19 masalas · Jain &amp; Non-Jain</div>
<div style='font-size:40px;font-weight:500;color:var(--cream);opacity:.85'>50g · 100g · 250g · yearly stock in 1 kg</div>
<div class='swipe' style='position:absolute;bottom:92px;left:0;right:0;color:var(--cream)'>Swipe for prices &rarr;</div></div>""", cls='dark')

F('p2-2', W, H, f"""<div class='frame'></div><div class='content' style='padding:118px 100px 100px'>
{table(JAIN[:10], 'Jain Masalas', 'J', rowh=98, fs=40)}
<div style='margin-top:auto;font-size:26px;color:var(--muted);text-align:center'>Swipe for more Jain masalas &rarr;</div></div>""")

F('p2-3', W, H, f"""<div class='frame'></div><div class='content' style='padding:118px 100px 100px'>
{table(JAIN[10:], 'Jain Masalas', 'J', rowh=98, fs=40)}
<div style='margin-top:auto;font-size:26px;color:var(--muted);text-align:center'>Prices as of November 2026</div></div>""")

yearly_html = ''.join(f"""<div style='display:grid;grid-template-columns:1fr 160px;align-items:center;min-height:72px;padding:0 8px;border-bottom:1.5px dashed rgba(136,44,13,.28)'>
<div style='font-size:34px;font-weight:500'>{n}</div><div style='text-align:right;font-size:34px;font-weight:600;font-variant-numeric:tabular-nums'>₹{p:,}</div></div>""" for n, p in YEARLY)
F('p2-4', W, H, f"""<div class='frame'></div><div class='content' style='padding:118px 100px 96px'>
{table(NONJAIN, 'Non-Jain', 'N.J', rowh=80, fs=36)}
<div style='margin-top:56px;display:flex;align-items:baseline;justify-content:space-between;border-bottom:3px solid var(--maroon);padding:0 8px 14px'>
<div class='disp' style='font-size:50px;color:var(--maroon)'>Yearly Stock</div><div style='font-weight:600;font-size:24px;letter-spacing:.12em;color:var(--muted)'>1 KG</div></div>
<div style='font-family:Hind;font-weight:600;font-size:30px;color:var(--chilli);padding:12px 8px 4px'>બારે માસ ભરવા લાયક મસાલા</div>
{yearly_html}
<div style='margin-top:auto;background:var(--maroon);color:var(--cream);border-radius:22px;padding:26px 34px;display:flex;justify-content:space-between;align-items:center'>
<div style='font-size:30px;font-weight:600'>Order on WhatsApp<br><span style='font-weight:400;opacity:.85;font-size:26px'>or tap the menu link in our bio</span></div>
<div style='font-family:Playfair;font-weight:700;font-size:44px;font-variant-numeric:tabular-nums'>+91 98204 41116</div></div></div>""")

# ---------- POST 3: Dhanteras / Diwali stock-up ----------
F('p3-1', W, H, f"""<div class='frame'></div><div class='content' style='align-items:center;text-align:center;padding:120px 110px'>
<div class='hand' style='font-size:64px;color:var(--turmeric);margin-top:30px'>Happy Dhanteras ✨</div>
<div style='margin:36px 0 10px'>{diya(300)}</div>
<div class='disp' style='font-size:94px;color:var(--cream)'>Diwali guests are on their way.</div>
<div class='ital' style='font-size:56px;color:var(--turmeric);margin-top:28px'>Is your masala dabba ready?</div>
<div class='swipe' style='position:absolute;bottom:92px;left:0;right:0;color:var(--cream)'>Swipe &rarr;</div></div>""", cls='dark')

F('p3-2', W, H, f"""<div class='frame'></div><div class='content' style='padding:130px 110px 110px'>
<div class='eyebrow' style='color:var(--chilli);margin-bottom:22px'>For the doorbell that won't stop</div>
<div class='disp' style='font-size:92px;margin-bottom:30px'>Chai for every guest.</div>
<div class='body' style='max-width:800px;margin-bottom:60px'>Add a pinch of Tea Masala while the tea leaves boil. That's the cup they'll ask about.</div>
<div style='flex:1;display:grid;place-items:center'><div style='width:900px;transform:rotate(-2deg)'><img class='labelimg' src='{label("Tea Masala.png")}'></div></div>
<div class='hand' style='font-size:50px;color:var(--maroon);text-align:right'>refills guaranteed</div></div>""")

F('p3-3', W, H, f"""<div class='frame'></div><div class='content' style='padding:130px 110px 110px'>
<div class='eyebrow' style='color:var(--chilli);margin-bottom:22px'>Diwali nasta plates</div>
<div class='disp' style='font-size:88px;margin-bottom:30px'>A sprinkle makes the plate.</div>
<div class='body' style='max-width:820px;margin-bottom:46px'>Chaat Masala over chevdo, fruit and chaat. Pani Puri Masala for the pani everyone comes back for.</div>
<div style='display:flex;flex-direction:column;gap:30px;align-items:center'>
<div style='width:640px;transform:rotate(-2deg)'><img class='labelimg' src='{label("Chaat Masala.png")}'></div>
<div style='width:640px;transform:rotate(1.5deg)'><img class='labelimg' src='{label("Pani Puri Masala.png")}'></div></div></div>""")

F('p3-4', W, H, f"""<div class='frame'></div><div class='content' style='align-items:center;justify-content:center;text-align:center;padding:120px'>
<div style='position:absolute;inset:0;display:grid;place-items:center;z-index:-1'>{rangoli(980)}</div>
<div class='eyebrow' style='color:var(--turmeric);margin-bottom:30px'>Before the guests arrive</div>
<div class='disp' style='font-size:104px;color:var(--cream)'>Stock up for Diwali.</div>
<div class='body' style='color:var(--cream);margin-top:34px;max-width:760px'>Every pack is ground fresh for your order, so order early and we'll have it ready.</div>
<div class='rule' style='width:420px;color:var(--turmeric);margin:46px 0'></div>
<div class='eyebrow' style='color:var(--turmeric);margin-bottom:14px'>Order on WhatsApp</div>
<div style='font-family:Playfair;font-weight:700;font-size:64px;color:var(--cream)'>+91 98204 41116</div>
<div style='font-size:32px;color:var(--cream);opacity:.85;margin-top:16px'>or tap the menu link in our bio</div></div>""", cls='dark')

# ---------- POST 4: Happy Diwali ----------
diwali_inner = lambda h: f"""<div class='frame'></div><div style='position:absolute;inset:0;display:grid;place-items:center'>{rangoli(1060, opacity=.2)}</div>
<div class='content' style='align-items:center;justify-content:center;text-align:center;padding:120px 110px'>
{diya(330)}
<div class='disp ital' style='font-size:{150 if h==H else 168}px;font-weight:700;color:var(--cream);margin-top:24px;font-style:italic'>Happy Diwali</div>
<div class='body' style='color:var(--cream);margin-top:30px;max-width:760px;font-size:38px'>May your home be full of light, family and good food.</div>
<div class='hand' style='font-size:56px;color:var(--turmeric);margin-top:44px'>Hetal &amp; the Heth Spices kitchen</div></div>"""
F('p4-1', W, H, diwali_inner(H), cls='dark')

# ---------- POST 5: Customer love (needs customer's OK) ----------
cust = uri(ROOT / 'out/feed/IMG_7134_garam-masala-gavar-bhaji_feed.jpg')
F('p5-1', W, H, f"""<div style='position:absolute;inset:0 0 430px 0;background:url("{cust}") center 38%/cover'></div>
<div style='position:absolute;left:0;right:0;bottom:0;height:450px;background:var(--cream) url("{PAPER}");border-top:6px solid var(--turmeric)'></div>
<div class='content' style='justify-content:flex-end;padding:0 96px 78px'>
<div class='tag' style='align-self:flex-start;background:var(--maroon);color:var(--cream);margin-bottom:30px'>From your kitchens</div>
<div class='disp ital' style='font-size:66px;font-style:italic;font-weight:700;color:var(--maroon)'>“The masala was super delicious 😋”</div>
<div style='font-size:30px;color:var(--muted);margin-top:18px'>A Heth Spices customer, on their Garam Masala bhaji</div>
<div class='hand' style='font-size:44px;color:var(--chilli);margin-top:22px'>Cooked with Heth? Tag @hethspices</div></div>""")

# ---------- STORIES ----------
SAFE = "padding:260px 100px 360px"
F('s1', SW, SH, f"""<div class='content' style='align-items:center;justify-content:center;text-align:center;{SAFE}'>
<div class='logo' style='--ls:300px;margin-bottom:70px'></div>
<div class='disp' style='font-size:108px;color:var(--cream)'>New look. Same homemade masalas.</div>
<div class='hand' style='font-size:66px;color:var(--turmeric);margin-top:50px'>Tap our profile to see what's new</div></div>""", cls='dark')

top6 = ['Pav Bhaji Masala', 'Garam Masala', 'Chaas Masala', 'Tea Masala', 'Biryani Masala', 'Sambhariyo']
F('s2', SW, SH, f"""<div class='content' style='{SAFE}'>
<div class='eyebrow' style='color:var(--chilli);margin-bottom:24px'>Just posted</div>
<div class='disp' style='font-size:110px;margin-bottom:50px'>Our full menu is up.</div>
{''.join(f"<div style='font-size:46px;font-weight:500;padding:20px 0;border-bottom:2px dashed rgba(136,44,13,.3);display:flex;justify-content:space-between'><span>{n}</span><span class='tag' style='font-size:24px;padding:6px 16px 4px;background:var(--maroon);color:var(--cream)'>J</span></div>" for n in top6)}
<div style='font-size:40px;color:var(--muted);margin-top:30px'>+ 13 more, Jain &amp; Non-Jain</div>
<div style='margin-top:auto;background:var(--maroon);color:var(--cream);border-radius:28px;padding:34px 40px;font-size:42px;font-weight:600;text-align:center'>Order: link in our bio</div></div>""")

F('s3', SW, SH, f"""<div class='content' style='align-items:center;text-align:center;{SAFE}'>
<div class='hand' style='font-size:76px;color:var(--turmeric)'>Happy Dhanteras ✨</div>
<div style='margin:40px 0 30px'>{diya(300)}</div>
<div class='eyebrow' style='color:var(--turmeric);margin-bottom:24px'>Quick question</div>
<div class='disp' style='font-size:96px;color:var(--cream)'>Which masala runs out first in your kitchen?</div>
<div style='flex:1'></div></div>""", cls='dark')

F('s4', SW, SH, f"""<div class='content' style='{SAFE}'>
<div class='tag' style='align-self:flex-start;background:var(--maroon);color:var(--cream);margin-bottom:36px'>Masala tip</div>
<div class='disp' style='font-size:104px;margin-bottom:40px'>The guest-worthy masala chai.</div>
<div class='body' style='font-size:44px;margin-bottom:70px'>Add a pinch of Tea Masala while the water and tea leaves boil. Then add milk and let it come up once more.</div>
<div style='width:880px;align-self:center;transform:rotate(-2deg)'><img class='labelimg' src='{label("Tea Masala.png")}'></div>
<div class='hand' style='margin-top:auto;font-size:60px;color:var(--maroon);text-align:center'>Ask anyone who's had a second cup</div></div>""")

F('s5', SW, SH, diwali_inner(SH).replace("padding:120px 110px", SAFE).replace("<div class='frame'></div>", ''), cls='dark')

F('s6', SW, SH, f"""<div style='position:absolute;inset:0;display:grid;place-items:center'>{rangoli(1060, color='#882C0D', opacity=.14)}</div>
<div class='content' style='align-items:center;justify-content:center;text-align:center;{SAFE}'>
<div class='logo' style='--ls:220px;margin-bottom:70px'></div>
<div style='font-family:Hind;font-weight:700;font-size:112px;color:var(--maroon);line-height:1.2'>નૂતન વર્ષાભિનંદન</div>
<div class='ital' style='font-size:84px;color:var(--chilli);margin-top:20px'>Saal Mubarak!</div>
<div class='body' style='font-size:44px;margin-top:50px;max-width:820px'>Wishing your family a year of good health and good food.</div>
<div class='hand' style='font-size:58px;color:var(--maroon);margin-top:50px'>Hetal &amp; the Heth Spices kitchen</div></div>""")

cust_story = uri(ROOT / 'out/feed/IMG_7134_garam-masala-gavar-bhaji_feed.jpg')
F('s7', SW, SH, f"""<div class='content' style='align-items:center;{SAFE}'>
<div class='tag' style='background:var(--maroon);color:var(--cream);margin-bottom:40px'>From your kitchens</div>
<div style='width:820px;aspect-ratio:4/5;background:url("{cust_story}") center/cover;border-radius:28px;border:10px solid #fff;box-shadow:0 24px 50px rgba(60,20,0,.25);transform:rotate(-1.5deg)'></div>
<div class='disp ital' style='font-size:76px;font-style:italic;font-weight:700;color:var(--maroon);text-align:center;margin-top:60px'>“The masala was super delicious 😋”</div>
<div class='hand' style='font-size:56px;color:var(--chilli);margin-top:34px'>Cooked with Heth? Tag @hethspices</div></div>""")

# ---------- PROFILE KIT ----------
F('profile-pic', 1080, 1080, f"""<div class='content' style='align-items:center;justify-content:center'><div class='logo' style='--ls:1000px;box-shadow:none'></div></div>""", cls='paper')
for key, lbl in [('menu', 'Menu'), ('order', 'Order'), ('jain', 'Jain'), ('reviews', 'Reviews'), ('recipes', 'Recipes')]:
    F(f'hl-{key}', SW, SH, f"""<div class='content' style='align-items:center;justify-content:center'>
<div style='width:520px;height:520px;border-radius:50%;border:6px solid var(--turmeric);display:grid;place-items:center'>
<div style='width:300px;height:300px'>{icon(key, '#FBF4E6', 9)}</div></div></div>""", cls='dark')

# ---------- RENDER ----------
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for name, w, h in FRAMES:
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
        pg.goto((HTML / f'{name}.html').as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(150)
        png = OUT / f'{name}.png'
        pg.screenshot(path=str(png), full_page=False)
        Image.open(png).convert('RGB').save(OUT / f'{name}.jpg', quality=92, optimize=True)
        png.unlink(); pg.close()
    b.close()
print(len(FRAMES), 'frames rendered')
