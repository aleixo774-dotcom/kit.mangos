"""Gera modelos de uniformes (SVG+PNG) e arte vetorial do logo para silk (SVG+PDF).
Uso: CHROMIUM=<caminho> python3 tools/build_uniformes.py"""
import os, math
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U = f"{R}/assets/uniformes"
PW, PH, LOGO_D = open(f"{R}/tools/fonte/mangos_path.txt").read().split("\n", 1)[0].split() + [open(f"{R}/tools/fonte/mangos_path.txt").read().split("\n", 1)[1]]
PW, PH = int(PW), int(PH)
AZUL, ROSA, VERDE, BRANCO, PRETO = "#010146", "#db0063", "#b7fe00", "#ffffff", "#111111"

# peça -> (hex da peça, cor do silk, nome)
# tecidos permitidos e cores de silk permitidas em cada um (1ª opção = padrão)
PECAS = {"preta": PRETO, "branca": BRANCO, "azul": AZUL}
SILK = {"preta": ["verde", "branco", "rosa"], "branca": ["azul", "rosa"], "azul": ["branco", "verde"]}
SILKHEX = {"verde": VERDE, "rosa": ROSA, "azul": AZUL, "branco": BRANCO}

def shade(hexc, amt):
    h = hexc.lstrip("#"); r, g, b = [int(h[i:i+2], 16) for i in (0, 2, 4)]
    f = lambda c: max(0, min(255, round(c + (255-c)*amt if amt > 0 else c*(1+amt))))
    return "#%02x%02x%02x" % (f(r), f(g), f(b))
def lum(hexc):
    h = hexc.lstrip("#"); r, g, b = [int(h[i:i+2], 16) for i in (0, 2, 4)]; return (.299*r + .587*g + .114*b)/255

# ---------- geometria (viewBox 600 x 620, vista frontal) ----------
BODY = {
 "reta": ("M232,62 L142,92 L60,178 L106,224 L150,194 L150,566 L450,566 L450,194 L494,224 L540,178 L458,92 L368,62",
          "M150,194 Q166,140 142,92", "M450,194 Q434,140 458,92", 548),
 "acintada": ("M240,64 L166,92 L98,166 L136,204 L170,182 C176,270 194,330 186,420 L180,526 L420,526 L414,420 C406,330 424,270 430,182 L464,204 L502,166 L434,92 L360,64",
          "M170,182 Q184,136 166,92", "M430,182 Q416,136 434,92", 508),
}
def tee_neck(kind):
    if kind == "reta": return ("M232,62 Q300,36 368,62 Q300,150 232,62 Z", "M232,62 Q300,152 368,62", None)
    return ("M240,64 Q300,40 360,64 Q300,160 240,64 Z", "M240,64 Q300,162 360,64", None)

def polo_collar(kind, base):
    dark = shade(base, -.10 if lum(base) > .3 else .10)
    x0, x1 = (232, 368) if kind == "reta" else (240, 360)
    # aba esquerda / direita + gola por trás + plaqueta
    back = f'<path d="M{x0},62 Q300,48 {x1},62 L{x1-10},70 Q300,58 {x0+10},70 Z" fill="{dark}"/>'
    L = f'<path d="M{x0},62 L{x0-34},98 L262,140 L300,112 Z" fill="{base}"/>'
    Rr = f'<path d="M{x1},62 L{x1+34},98 L338,140 L300,112 Z" fill="{base}"/>'
    plaq = f'<rect x="286" y="112" width="28" height="118" fill="{base}"/><line x1="300" y1="112" x2="300" y2="230"/>'
    btn = "".join(f'<circle cx="300" cy="{y}" r="5.2" fill="{dark}"/>' for y in (138, 168, 198))
    return back, L + Rr, plaq, btn

def svg_peca(modelo, cor, silk_nome, with_logo=True):
    base, silk = PECAS[cor], SILKHEX[silk_nome]
    kind = "reta" if modelo in ("camiseta-tradicional", "polo-masculina") else "acintada"
    polo = modelo.startswith("polo")
    body, armL, armR, hem = BODY[kind]
    stroke = shade(base, .16 if lum(base) < .35 else -.16)
    inner = shade(base, .10 if lum(base) < .35 else -.12)
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 620" width="1200" height="1240">'
    s += f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".10"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".16"/></linearGradient></defs>'
    s += f'<g stroke="{stroke}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">'
    if not polo:
        back, front, _ = tee_neck(kind)
        s += f'<path d="{body} {front.split(" Q")[0] if False else ""}" fill="{base}"/>'
        # corpo fechado pelo decote
        pts = body + (" Q300,150 232,62 Z" if kind == "reta" else " Q300,160 240,64 Z")
        s += f'<path d="{pts}" fill="{base}"/><path d="{pts}" fill="url(#g)" stroke="none"/>'
        s += f'<path d="{tee_neck(kind)[0]}" fill="{inner}"/>'
        s += f'<path d="{tee_neck(kind)[1]}" fill="none" stroke="{shade(base, .08 if lum(base) < .35 else -.08)}" stroke-width="13" stroke-linecap="butt"/>'
        s += f'<path d="{tee_neck(kind)[1]}" fill="none" stroke="{stroke}" stroke-width="1.5"/>'
    else:
        back, flaps, plaq, btn = polo_collar(kind, base)
        pts = body + " Q300,120 " + body.split(" ")[0][1:].replace(",", ",") + " Z"
        s += f'<path d="{pts}" fill="{base}"/><path d="{pts}" fill="url(#g)" stroke="none"/>'
        s += back + flaps + f'<g fill="{base}">{plaq}</g>' + btn
    # costuras: ombro/cava, barra
    s += f'<path d="{armL}" fill="none"/><path d="{armR}" fill="none"/>'
    hy = hem
    x0, x1 = (150, 450) if kind == "reta" else (181, 419)
    s += f'<path d="M{x0+4},{hy-22} L{x1-4},{hy-22}" stroke-dasharray="2 5" fill="none" stroke-width="2"/>'
    # punho das mangas
    if kind == "reta":
        s += '<path d="M76,166 L117,208" stroke-dasharray="2 5" fill="none" stroke-width="2"/><path d="M524,166 L483,208" stroke-dasharray="2 5" fill="none" stroke-width="2"/>'
    else:
        s += '<path d="M110,156 L142,190" stroke-dasharray="2 5" fill="none" stroke-width="2"/><path d="M490,156 L458,190" stroke-dasharray="2 5" fill="none" stroke-width="2"/>'
    s += '</g>'
    if with_logo:
        cx = 378 if kind == "reta" else 372
        cy = 160 if not polo else 164
        w = 52 if kind == "reta" else 48          # ~8,5 cm / ~8,0 cm (peito ≈ 50 cm = 300 u)
        sc = w / PW
        s += f'<g transform="translate({cx-w/2:.1f},{cy:.1f}) scale({sc:.6f})"><path d="{LOGO_D}" fill="{silk}" fill-rule="evenodd"/></g>'
    return s + "</svg>"

def svg_logo(color, bg=None, pad=0.06):
    w = PW; h = PH; p = int(w*pad)
    bgr = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-p} {-p} {w+2*p} {h+2*p}" width="{w+2*p}" height="{h+2*p}">{bgr}<path d="{LOGO_D}" fill="{color}" fill-rule="evenodd"/></svg>'

MODELOS = ["camiseta-tradicional", "baby-look", "polo-masculina", "polo-feminina"]
files = []
import glob
for old in glob.glob(f"{U}/modelos/*"): os.remove(old)
for m in MODELOS:
    for c in PECAS:
        for sk in SILK[c]:
            p = f"{U}/modelos/{m}-{c}-silk-{sk}.svg"; open(p, "w").write(svg_peca(m, c, sk)); files.append((p, 1200))
LOGOS = {"verde": VERDE, "rosa": ROSA, "azul": AZUL, "branco": BRANCO}
for n, c in LOGOS.items():
    open(f"{U}/arte-silk/mangos-silk-{n}.svg", "w").write(svg_logo(c))
    open(f"{R}/assets/logos/mangos-logo-{n}.svg", "w").write(svg_logo(c))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROMIUM"), args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1200, "height": 1240}, device_scale_factor=1)
    for path, w in files:
        pg.goto("file://" + path); pg.screenshot(path=path[:-4] + ".png", omit_background=True)
    pad = int(PW*0.06); ratio = (PH+2*pad)/(PW+2*pad)
    pg2 = b.new_page(viewport={"width": 3000, "height": 700})
    for n, c in LOGOS.items():
        fix = lambda wcss: svg_logo(c).replace("<svg ", f'<svg style="width:{wcss};height:auto;display:block" ', 1)
        bg = "#010146" if n == "branco" else "transparent"
        pg2.set_content(f'<html><head><style>@page{{margin:0}}html,body{{margin:0;background:{bg}}}</style></head><body>{fix("200mm")}</body></html>')
        pg2.pdf(path=f"{U}/arte-silk/mangos-silk-{n}.pdf", width="200mm", height=f"{200*ratio:.2f}mm", print_background=True)
        pg2.set_content(f'<html><body style="margin:0;background:transparent"><div id="x" style="width:3000px">{fix("3000px")}</div></body></html>')
        pg2.locator("#x").screenshot(path=f"{U}/arte-silk/mangos-silk-{n}-3000.png", omit_background=True)
    b.close()
print("ok", len(files), "modelos")
