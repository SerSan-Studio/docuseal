#!/usr/bin/env bash
# SerSan: logo, icone e immagini del marchio, dalle forme del marchio di sersan.io (sersan/marchio.swift).
# Gira su un Mac (swift, python3). Uso, dalla cartella del repository: sersan/genera-icone.sh
# Scrive in public/ e in lib/pdf_icons/ gli stessi nomi di file di DocuSeal, più public/sersan-logo.{svg,png}.
set -euo pipefail

NAVY=132741    # metà alta del marchio, su fondo chiaro
BLU=2280DC     # metà bassa, su fondo chiaro
INK=F4F6FA     # metà alta, su fondo scuro
BLU_SCURO=4FA3F7
FONDO=0B1523   # il blu notte di sersan.io, per le icone che non reggono la trasparenza (iOS, anteprima dei link)

swiftc -O -o "${TMPDIR:-/tmp}/sersan-marchio" sersan/marchio.swift
m() { "${TMPDIR:-/tmp}/sersan-marchio" "$@"; }

SU='M 81.19 0 L 162.38 46.88 L 127.3 67.13 L 81.19 40.51 L 39.64 64.49 L 39.64 90.03 L 80.11 113.4 L 40.6 136.21 L 0 112.78 L 0 46.88 Z'
GIU='M 81.19 200 L 0 153.13 L 35.08 132.87 L 81.19 159.49 L 122.73 135.51 L 122.73 109.97 L 82.27 86.6 L 121.78 63.79 L 162.38 87.22 L 162.38 153.13 Z'

# Logo dell'interfaccia (shared/_logo, logo.vue) e logo.svg di DocuSeal: vettoriale, colori per fondo chiaro.
for f in public/sersan-logo.svg public/logo.svg; do
  printf '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 162.38 200" role="img" aria-label="SerSan"><path fill="#%s" d="%s"/><path fill="#%s" d="%s"/></svg>\n' \
    "$NAVY" "$SU" "$BLU" "$GIU" > "$f"
done

# favicon.svg: come quella di sersan.io, con la metà scura che diventa chiara se il browser è scuro.
cat > public/favicon.svg <<SVG
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" role="img" aria-label="SerSan">
  <style>
    .su { fill: #$NAVY; }
    .giu { fill: #$BLU; }
    @media (prefers-color-scheme: dark) {
      .su { fill: #$INK; }
      .giu { fill: #$BLU_SCURO; }
    }
  </style>
  <g transform="translate(28.55 12) scale(0.88)">
    <path class="su" d="$SU"/>
    <path class="giu" d="$GIU"/>
  </g>
</svg>
SVG

m 192 public/sersan-logo.png none $NAVY $BLU 0.04
m 16 public/favicon-16x16.png none $NAVY $BLU 0
m 32 public/favicon-32x32.png none $NAVY $BLU 0.02
m 96 public/favicon-96x96.png none $NAVY $BLU 0.04
m 180 public/apple-icon-180x180.png $FONDO $INK $BLU_SCURO 0.2
cp public/apple-icon-180x180.png public/apple-touch-icon.png
cp public/apple-icon-180x180.png public/apple-touch-icon-precomposed.png
m 800 public/preview.png $FONDO $INK $BLU_SCURO 0.26          # anteprima dei link (og:image)
m 300 lib/pdf_icons/logo.png none $NAVY $BLU 0.02              # registro di firma (audit trail) nei PDF
swift sersan/timbro.swift lib/pdf_icons/stamp-logo.png >/dev/null

# favicon.ico con dentro i PNG da 16 e 32 (formato ICO con PNG, va bene a tutti i browser)
python3 - public/favicon.ico public/favicon-16x16.png public/favicon-32x32.png <<'PY'
import struct, sys
out, *pngs = sys.argv[1:]
dati = [open(p, "rb").read() for p in pngs]
lati = [struct.unpack(">I", d[16:20])[0] for d in dati]
testa = struct.pack("<HHH", 0, 1, len(dati))
pos = 6 + 16 * len(dati); voci = b""
for d, l in zip(dati, lati):
    voci += struct.pack("<BBBBHHII", l % 256, l % 256, 0, 0, 1, 32, len(d), pos); pos += len(d)
open(out, "wb").write(testa + voci + b"".join(dati))
PY
echo "icone fatte"
ls -la public/sersan-logo.* public/favicon* public/apple* public/preview.png public/logo.svg lib/pdf_icons/logo.png lib/pdf_icons/stamp-logo.png | awk '{print $5, $9}'
