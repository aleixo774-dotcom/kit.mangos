import zipfile, os, glob
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = f"{R}/assets"; D = f"{R}/downloads"
os.makedirs(D, exist_ok=True)
def zipit(name, files, strip):
    with zipfile.ZipFile(f"{D}/{name}", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(files): z.write(f, os.path.relpath(f, strip))
fav = glob.glob(f"{A}/favicon/*")
perfil = [f for f in glob.glob(f"{A}/perfil/*")]
logos = glob.glob(f"{A}/logos/*")
capas = [f for f in glob.glob(f"{A}/social/*") if "og-" not in f]
uni = glob.glob(f"{A}/uniformes/*/*")
zipit("mangos-uniformes.zip", uni, f"{A}/uniformes")
simb = glob.glob(f"{A}/simbolo/*")
zipit("mangos-simbolo.zip", simb, f"{A}/simbolo")
zipit("mangos-favicons.zip", fav, f"{A}/favicon")
zipit("mangos-foto-de-perfil.zip", perfil, f"{A}/perfil")
zipit("mangos-logos.zip", logos, f"{A}/logos")
zipit("mangos-capas-redes.zip", capas, f"{A}/social")
zipit("mangos-kit-completo.zip", fav+perfil+logos+capas+uni+simb, A)
for f in sorted(glob.glob(f"{D}/*")): print(os.path.basename(f), os.path.getsize(f)//1024, "KB")
