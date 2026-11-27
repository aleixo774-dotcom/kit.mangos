# Kit de Marca Mangos 2026

Página: `index.html` (GitHub Pages, publicado a partir da `main`).

- `assets/` logos, favicons, foto de perfil e capas (PNG)
- `assets/uniformes/` modelos de camiseta/polo (SVG+PNG) e arte vetorial do logo para silk (SVG+PDF)
- `downloads/` pacotes .zip
- `tools/` scripts que geram tudo a partir dos originais em `tools/fonte/`

Regerar: `python3 tools/build_assets.py && CHROMIUM=<caminho> python3 tools/render_social.py && CHROMIUM=<caminho> python3 tools/build_uniformes.py && python3 tools/build_zips.py`
(requer Pillow, Playwright e potracer).
