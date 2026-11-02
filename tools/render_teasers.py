"""Render pre-launch teaser stories, reusing the launch design system."""
from pathlib import Path
src = Path('/home/claude/hs/scripts/render_launch.py').read_text()
exec(src.split('# ---------- POST 1')[0])  # fonts, tokens, helpers, page()

TEASE = []
T = lambda *a, **k: TEASE.append(page(*a, **k))
SW, SH = 1080, 1920
SAFE = "padding:260px 100px 360px"

# T1 — Mon 2 Nov evening
T('t1', SW, SH, f"""<div style='position:absolute;inset:0;display:grid;place-items:center'>{rangoli(1060, opacity=.16)}</div>
<div class='content' style='align-items:center;justify-content:center;text-align:center;{SAFE}'>
<div class='logo' style='--ls:260px;margin-bottom:70px'></div>
<div class='eyebrow' style='color:var(--turmeric);margin-bottom:34px'>Coming this Wednesday</div>
<div class='disp' style='font-size:112px;color:var(--cream)'>Something fresh is grinding in Hetal's kitchen.</div>
<div class='rule' style='width:420px;color:var(--turmeric);margin:60px 0 44px'></div>
<div style='font-family:Playfair;font-weight:700;font-size:60px;color:var(--cream)'>Wed, 4 Nov · 10 am</div>
<div class='hand' style='font-size:58px;color:var(--turmeric);margin-top:40px'>follow so you don't miss it</div></div>""", cls='dark')

# T2 — Tue 3 Nov morning: blurred sneak peek of the menu
menu = uri(ROOT / 'launch/p2-2.jpg')
T('t2', SW, SH, f"""<div style='position:absolute;inset:0;background:url("{menu}") center/cover;filter:blur(20px) saturate(1.1);transform:scale(1.15)'></div>
<div style='position:absolute;inset:0;background:linear-gradient(180deg,rgba(90,27,8,.25),rgba(90,27,8,.55))'></div>
<div class='content' style='align-items:center;justify-content:center;text-align:center;{SAFE}'>
<div style='background:var(--cream);border-radius:36px;padding:70px 64px;box-shadow:0 30px 60px rgba(40,10,0,.35)'>
<div class='tag' style='background:var(--maroon);color:var(--cream);margin-bottom:34px'>Sneak peek 👀</div>
<div class='disp' style='font-size:96px;color:var(--ink)'>Our full menu, prices and all.</div>
<div class='body' style='font-size:42px;margin-top:30px'>19 homemade masalas, Jain &amp; Non-Jain, in one place.</div>
<div class='rule' style='width:360px;color:var(--maroon);margin:44px auto'></div>
<div style='font-family:Playfair;font-weight:700;font-size:56px;color:var(--maroon)'>Landing Thursday</div></div></div>""")

# T3 — Tue 3 Nov evening: three-clue riddle (reply to answer)
clues = ['It goes into a glass, not a pan.', 'Best after a heavy lunch.', 'Every Gujarati home keeps a jug of its drink in summer.']
clue_html = ''.join(f"""<div style='display:flex;gap:30px;align-items:flex-start;text-align:left'>
<div class='num' style='font-size:120px;flex:0 0 80px;text-align:center'>{i+1}</div>
<div class='body' style='font-size:50px;color:var(--cream);padding-top:24px'>{c}</div></div>""" for i, c in enumerate(clues))
T('t3', SW, SH, f"""<div class='content' style='{SAFE}'>
<div class='eyebrow' style='color:var(--turmeric);margin-bottom:28px;text-align:center'>Guess the masala</div>
<div class='disp' style='font-size:104px;color:var(--cream);text-align:center;margin-bottom:70px'>Three clues. One masala.</div>
<div style='display:flex;flex-direction:column;gap:46px'>{clue_html}</div>
<div style='margin-top:auto;border:3px dashed var(--turmeric);border-radius:30px;padding:34px 30px;text-align:center'>
<div class='hand' style='font-size:62px;color:var(--turmeric)'>Reply with your guess 👇</div>
<div style='font-size:36px;color:var(--cream);opacity:.85;margin-top:8px'>Answer on Wednesday</div></div></div>""", cls='dark')

# T4 — Wed 4 Nov noon: reveal
chaas = uri(ROOT / 'out/feed/IMG_7139_chaas-with-pack_feed.jpg')
T('t4', SW, SH, f"""<div class='content' style='align-items:center;text-align:center;{SAFE}'>
<div class='eyebrow' style='color:var(--chilli);margin-bottom:26px'>Yesterday's riddle</div>
<div class='disp' style='font-size:104px;color:var(--ink)'>It was Chaas Masala!</div>
<div style='width:800px;aspect-ratio:1/1;max-width:100%;background:url("{chaas}") center/cover;border-radius:30px;border:12px solid #fff;box-shadow:0 26px 54px rgba(60,20,0,.25);transform:rotate(-1.5deg);margin:60px 0'></div>
<div class='body' style='font-size:44px'>Stir it into chilled chaas after a heavy Diwali meal.</div>
<div class='hand' style='font-size:58px;color:var(--maroon);margin-top:36px'>Did you get it right?</div></div>""")

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for name, w, h in TEASE:
        pg = b.new_page(viewport={'width': w, 'height': h})
        pg.goto((HTML / f'{name}.html').as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(150)
        png = OUT / f'{name}.png'; pg.screenshot(path=str(png))
        Image.open(png).convert('RGB').save(OUT / f'{name}.jpg', quality=92, optimize=True); png.unlink(); pg.close()
    b.close()
print(len(TEASE), 'teasers rendered')
