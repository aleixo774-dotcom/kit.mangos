"""Renderiza assinaturas (logo + descritor) e capas de redes sociais com Montserrat via Chromium.
Uso: python3 tools/build_assets.py && python3 tools/render_social.py"""
from playwright.sync_api import sync_playwright
import os, base64
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = f"{R}/assets"
COR = {"rosa": "#db0063", "verde": "#b7fe00", "azul": "#010146", "branco": "#ffffff"}
FONT = '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;800&display=swap" rel="stylesheet">'
def b64(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()

def lockup_html(nome, texto, w):
    c = COR[nome]; img = b64(f"{A}/logos/mangos-logo-{nome}-2000.png")
    # a imagem tem proporção 8000:1526
    h = round(w * 1526 / 8000)
    return f"""<html><head>{FONT}<style>
    html,body{{margin:0;background:transparent}}
    .l{{position:relative;width:{w}px;height:{h}px}}
    .l img{{position:absolute;inset:0;width:100%;height:100%}}
    .t{{position:absolute;left:0;top:{h*0.89:.0f}px;transform:translateY(-50%);font:300 20px Montserrat;color:{c};white-space:nowrap;line-height:1}}
    </style></head><body><div class="l"><img src="{img}"><span class="t" id="t">{texto}</span></div>
    <script>document.fonts.ready.then(()=>{{const t=document.getElementById('t');const real=t.textContent;t.textContent='Assessoria Financeira e Seguros';const target={w}*0.49;const fs=20*target/t.getBoundingClientRect().width;t.textContent=real;t.style.fontSize=fs+'px';document.body.dataset.ok=1}})</script>
    </body></html>"""

CAPA = """<html><head>{font}<style>
*{{margin:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:#010146;font-family:Montserrat;color:#fff;position:relative;overflow:hidden}}
.g1{{position:absolute;right:-{r1}px;bottom:-{r1}px;width:{r1x}px;height:{r1x}px;border-radius:50%;background:radial-gradient(circle,rgba(219,0,99,.22),transparent 65%)}}
.g2{{position:absolute;left:{g2x}px;top:-{r2}px;width:{r2x}px;height:{r2x}px;border-radius:50%;background:radial-gradient(circle,rgba(183,254,0,.10),transparent 65%)}}
.c{{position:absolute;left:{cx}px;top:50%;transform:translateY(-50%)}}
.c img{{height:{lh}px;display:block;margin-bottom:{gap}px}}
h1{{font-size:{fs}px;font-weight:800;line-height:1.08;letter-spacing:-.03em}}
h1 b{{color:#b7fe00;font-weight:800}}
.s{{margin-top:{gap}px;font-size:{ss}px;font-weight:600;color:rgba(255,255,255,.75);display:flex;align-items:center;gap:{dg}px}}
.s i{{width:{dd}px;height:{dd}px;border-radius:50%;background:#db0063;display:inline-block}}
.bar{{position:absolute;left:0;right:0;top:0;height:{bar}px;background:linear-gradient(90deg,#db0063,#ff6b35 25%,#ffbe00 50%,#b7fe00 75%,#010146)}}
</style></head><body><div class="bar"></div><div class="g1"></div><div class="g2"></div>
<div class="c"><img src="{logo}"><h1>Você acredita,<br><b>a gente realiza!</b></h1>
<div class="s"><i></i>Correspondente bancário e corretora de seguros · Batatais/SP</div></div></body></html>"""

def capa(W, H, cx, lh, fs, ss, name, one_line=False):
    s = W/1584
    h = CAPA.format(font=FONT, W=W, H=H, r1=int(120*s), r1x=int(520*s), g2x=int(520*s), r2=int(100*s), r2x=int(380*s), cx=cx,
                    lh=lh, gap=int(lh*.5), fs=fs, ss=ss, dg=int(ss*.6), dd=int(ss*.55), bar=max(4,int(6*s)), logo=b64(f"{A}/logos/mangos-logo-branco-1000.png"))
    return h

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROMIUM", None), args=["--no-sandbox"]); 
    # --- assinaturas ---
    pg = b.new_page(device_scale_factor=1)
    for nome in COR:
        for w in (2000, 1000):
            pg.set_viewport_size({"width": w, "height": round(w*1526/8000)})
            pg.set_content(lockup_html(nome, "Corretora de Seguros", w)); pg.wait_for_function("document.body.dataset.ok")
            pg.screenshot(path=f"{A}/logos/mangos-assinatura-{nome}-{w}.png", omit_background=True)
    # --- capas ---
    jobs = [("capa-linkedin-1584x396", 1584, 396, 560, 46, 50, 17),
            ("capa-facebook-1640x624", 1640, 624, 410, 56, 70, 20),
            ("capa-youtube-2560x1440", 2560, 1440, 760, 70, 150, 38),
            ("og-kit-1200x630", 1200, 630, 90, 56, 64, 20)]
    for name, W, H, cx, lh, fs, ss in jobs:
        pg.set_viewport_size({"width": W, "height": H})
        pg.set_content(capa(W, H, cx, lh, fs, ss, name)); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(800)
        pg.screenshot(path=f"{A}/social/{name}.png")
    b.close()
