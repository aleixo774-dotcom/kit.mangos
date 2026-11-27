"""Gera favicons, foto de perfil e logos do kit Mangos a partir dos originais em tools/fonte.
Uso: python3 tools/build_assets.py   (requer Pillow)"""
from PIL import Image, ImageDraw, ImageChops
import os, shutil
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = f"{R}/tools/fonte"; A = f"{R}/assets"
AZUL, ROSA, VERDE, BRANCO = (1,1,70), (219,0,99), (183,254,0), (255,255,255)
LANCZOS = Image.LANCZOS

# ---------- 1. glifo "m." limpo a partir do favicon enviado ----------
src = Image.open(f"{F}/favicon-original.webp").convert("RGBA")
rgb = src.convert("RGB")
# alpha do glifo = quão "branco" é o pixel (azul de fundo ~0, branco =1), ignorando cantos transparentes
mask = rgb.split()[0].point(lambda v: max(0, min(255, int((v-3)*255/(255-3)))))
mask = ImageChops.multiply(mask, src.split()[3])
bbox = mask.point(lambda v: 255 if v > 128 else 0).getbbox()
glyph = mask.crop(bbox)  # só o "m."
gw, gh = glyph.size
# separa o ponto (parte direita): última coluna conectada
cols = glyph.point(lambda v: 255 if v > 128 else 0)
px = cols.load(); gap_start = None
inside = False
for x in range(gw):
    has = any(px[x, y] for y in range(0, gh, 2))
    if has and not inside: inside = True
    if (not has) and inside:
        gap_start = x; break
dot_x0 = None
for x in range(gap_start, gw):
    if any(px[x, y] for y in range(0, gh, 2)): dot_x0 = x; break
dot_mask = Image.new("L", glyph.size, 0); dot_mask.paste(glyph.crop((dot_x0, 0, gw, gh)), (dot_x0, 0))
print("glifo", glyph.size, "ponto a partir de x=", dot_x0)

def tint(m, color): 
    im = Image.new("RGBA", m.size, color + (0,)); im.putalpha(m); return im

def mark_on(size, bg, fg=BRANCO, dot=None, scale=0.72, rounded=0.0):
    """quadrado size×size, glifo centralizado ocupando `scale` da largura."""
    S = 4  # supersampling
    N = size * S
    base = Image.new("RGBA", (N, N), bg + (255,))
    w = int(N * scale); h = int(gh * w / gw)
    g = glyph.resize((w, h), LANCZOS); d = dot_mask.resize((w, h), LANCZOS)
    pos = ((N - w)//2, (N - h)//2)
    body = ImageChops.subtract(g, d)
    base.alpha_composite(tint(body, fg), pos)
    base.alpha_composite(tint(d, dot or fg), pos)
    if rounded:
        m = Image.new("L", (N, N), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, N-1, N-1], radius=int(N*rounded), fill=255)
        base.putalpha(m)
    return base.resize((size, size), LANCZOS)

# ---------- 2. favicons ----------
fav = f"{A}/favicon"
for s in (16, 32, 48, 64, 96, 128, 192, 256, 512):
    # glifo maior em tamanhos pequenos para manter legibilidade
    sc = 0.80 if s <= 48 else 0.72
    mark_on(s, AZUL, scale=sc, rounded=0.22).save(f"{fav}/favicon-{s}.png")
# ícones "full-bleed" (o sistema arredonda sozinho)
mark_on(180, AZUL).save(f"{fav}/apple-touch-icon.png")
mark_on(192, AZUL, scale=0.56).save(f"{fav}/android-chrome-192.png")   # maskable: zona segura 80%
mark_on(512, AZUL, scale=0.56).save(f"{fav}/android-chrome-512.png")
mark_on(150, AZUL).save(f"{fav}/mstile-150.png")
ico_imgs = [mark_on(s, AZUL, scale=0.80 if s<=48 else 0.72, rounded=0.22) for s in (16,32,48,64)]
ico_imgs[-1].save(f"{fav}/favicon.ico", sizes=[(16,16),(32,32),(48,48),(64,64)], append_images=ico_imgs[:-1])
# SVG vetorial do favicon (m. com a mesma geometria do raster, via máscara -> não é path; usamos PNG embutido seria ruim) -> omitido
with open(f"{fav}/site.webmanifest", "w") as f:
    f.write('''{
  "name": "Mangos",
  "short_name": "Mangos",
  "description": "Correspondente bancário e corretora de seguros · Batatais/SP",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#010146",
  "theme_color": "#010146",
  "icons": [
    { "src": "android-chrome-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable" },
    { "src": "android-chrome-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ]
}
''')

# ---------- 3. foto de perfil (quadrada, sem cantos: as redes recortam em círculo/quadrado) ----------
pf = f"{A}/perfil"
for s in (1080, 800, 400, 200):
    mark_on(s, AZUL, scale=0.62).save(f"{pf}/perfil-mangos-{s}.png")
VAR = [("azul", AZUL, "verde", VERDE), ("azul", AZUL, "rosa", ROSA), ("rosa", ROSA, "branco", BRANCO),
       ("verde", VERDE, "azul", AZUL), ("branco", BRANCO, "azul", AZUL), ("branco", BRANCO, "rosa", ROSA)]
for fn, fc, mn, mc in VAR:   # m e ponto sempre na mesma cor
    mark_on(1080, fc, fg=mc, scale=0.62).save(f"{pf}/perfil-mangos-fundo-{fn}-marca-{mn}-1080.png")
# prévia em círculo
def circ(im):
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).ellipse([0,0,im.width-1,im.height-1], fill=255)
    o = Image.new("RGBA", im.size, (0,0,0,0)); o.paste(im, (0,0), m); return o
circ(mark_on(400, AZUL, scale=0.62)).save(f"{pf}/previa-circulo-400.png")

# ---------- 4. logos: wordmark sem tagline, 4 cores ----------
big = Image.open(f"{F}/logo-original-rosa.png").convert("RGBA")
a = big.split()[3]
W, H = big.size
# remove a linha "Assessoria Financeira e Seguros" (x<4120, y>1240) preservando o rabinho do g
clear = Image.new("L", (W, H), 0); ImageDraw.Draw(clear).rectangle([0, 1240, 4100, H], fill=255)
a_word = ImageChops.subtract(a, clear)
a_tag = ImageChops.multiply(a, clear)   # só a tagline antiga
bb = a_word.getbbox(); a_word = a_word.crop(bb)
cores = {"rosa": ROSA, "verde": VERDE, "azul": AZUL, "branco": BRANCO}
lg = f"{A}/logos"
for nome, c in cores.items():
    t = tint(a_word, c)
    for w in (2000, 1000, 500):
        t.resize((w, round(t.height*w/t.width)), LANCZOS).save(f"{lg}/mangos-logo-{nome}-{w}.png")
a_word.save(f"{R}/tools/fonte/_wordmark_mask.png")
print("wordmark", a_word.size, "bbox", bb)
