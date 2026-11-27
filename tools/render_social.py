"""Renderiza assinaturas (logo + descritor) e capas de redes sociais com Montserrat via Chromium.
Uso: python3 tools/build_assets.py && python3 tools/render_social.py"""
from playwright.sync_api import sync_playwright
import os, base64
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = f"{R}/assets"
COR = {"rosa": "#db0063", "verde": "#b7fe00", "azul": "#010146", "branco": "#ffffff"}
FONT = '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;800&display=swap" rel="stylesheet">'
def b64(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()

DESC = {"assessoria-financeira-e-seguros": "Assessoria Financeira e Seguros", "corretora-de-seguros": "Corretora de Seguros", "assessoria-financeira": "Assessoria Financeira"}

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

import math
def ring(cx, cy, d, color, op, dashed=False, bw=2, dot=None):
    """anel centrado em (cx,cy) com diâmetro d; dot=(ângulo°, cor, diâmetro) adiciona o pontinho em órbita."""
    st = "dashed" if dashed else "solid"
    h = f'<div style="position:absolute;left:{cx-d/2:.0f}px;top:{cy-d/2:.0f}px;width:{d:.0f}px;height:{d:.0f}px;border-radius:50%;border:{bw}px {st} {color};opacity:{op}"></div>'
    if dot:
        ang, c, dd = dot
        x = cx + d/2*math.cos(math.radians(ang)); y = cy + d/2*math.sin(math.radians(ang))
        h += f'<div style="position:absolute;left:{x-dd/2:.0f}px;top:{y-dd/2:.0f}px;width:{dd}px;height:{dd}px;border-radius:50%;background:{c};box-shadow:0 0 0 {dd*.35:.0f}px {c}33"></div>'
    return h

def rings(W, H):
    u = H; bw = max(2, round(H/260))
    W_, P, L = "#ffffff", "#db0063", "#b7fe00"
    o = ""
    # grupo direito (onde ficava o brilho rosa): anéis concêntricos + órbita tracejada com ponto rosa
    cx, cy = W*0.90, H*0.58
    for d, op in ((0.9, .10), (1.35, .08), (1.85, .06)): o += ring(cx, cy, d*u, W_, op, bw=bw)
    o += ring(cx, cy, 1.12*u, P, .55, True, bw, dot=(-50, P, max(10, u*.035)))
    # grupo esquerdo inferior: anéis parciais + ponto verde
    cx, cy = W*0.04, H*0.98
    for d, op in ((0.8, .09), (1.3, .07)): o += ring(cx, cy, d*u, W_, op, bw=bw)
    o += ring(cx, cy, 1.05*u, L, .35, True, bw, dot=(-35, L, max(8, u*.026)))
    # grupo superior central: anel rosa fino + marca d'água branca
    cx, cy = W*0.40, H*0.02
    o += ring(cx, cy, 0.7*u, P, .30, bw=bw)
    o += ring(cx, cy, 1.1*u, W_, .06, bw=bw)
    # círculo pequeno solto (como os do hero do site)
    o += ring(W*0.78, H*0.16, 0.22*u, W_, .12, bw=bw)
    o += ring(W*0.66, H*0.88, 0.30*u, P, .25, True, bw)
    return o

CAPA = """<html><head>{font}<style>
*{{margin:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:#010146;font-family:Montserrat;color:#fff;position:relative;overflow:hidden}}
.c{{position:absolute;left:{cx}px;top:50%;transform:translateY(-50%);z-index:2}}
.c img{{height:{lh}px;display:block;margin-bottom:{gap}px}}
h1{{font-size:{fs}px;font-weight:800;line-height:1.08;letter-spacing:-.03em}}
h1 b{{color:#b7fe00;font-weight:800}}
.s{{margin-top:{gap}px;font-size:{ss}px;font-weight:600;color:rgba(255,255,255,.75);display:flex;align-items:center;gap:{dg}px}}
.s i{{width:{dd}px;height:{dd}px;border-radius:50%;background:#db0063;display:inline-block}}
.bar{{position:absolute;left:0;right:0;top:0;height:{bar}px;background:linear-gradient(90deg,#db0063,#ff6b35 25%,#ffbe00 50%,#b7fe00 75%,#010146);z-index:3}}
</style></head><body><div class="bar"></div>{rings}
<div class="c"><img src="{logo}"><h1>Você acredita,<br><b>a gente realiza!</b></h1>
<div class="s"><i></i>Correspondente bancário e corretora de seguros · Batatais/SP</div></div></body></html>"""

def capa(W, H, cx, lh, fs, ss, name, one_line=False):
    s = W/1584
    return CAPA.format(font=FONT, W=W, H=H, cx=cx, lh=lh, gap=int(lh*.5), fs=fs, ss=ss, dg=int(ss*.6), dd=int(ss*.55),
                       bar=max(4,int(6*s)), logo=b64(f"{A}/logos/mangos-logo-branco-1000.png"), rings=rings(W, H))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROMIUM", None), args=["--no-sandbox"]); 
    # --- assinaturas ---
    pg = b.new_page(device_scale_factor=1)
    for nome in COR:
        for w in (2000, 1000):
            pg.set_viewport_size({"width": w, "height": round(w*1526/8000)})
            for slug, txt in DESC.items():
                pg.set_content(lockup_html(nome, txt, w)); pg.wait_for_function("document.body.dataset.ok")
                pg.screenshot(path=f"{A}/logos/mangos-assinatura-{slug}-{nome}-{w}.png", omit_background=True)
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
