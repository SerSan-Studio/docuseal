#!/usr/bin/env bash
# SerSan: icone e immagini del marchio, da sersan/marchio-512.png (l'esagono SerSan, sfondo trasparente).
# Gira su un Mac (sips, ffmpeg, swift). Uso, dalla cartella del repository: sersan/genera-icone.sh
# Scrive in public/ e in lib/pdf_icons/ gli stessi nomi di file di DocuSeal, più public/sersan-logo.png.
set -euo pipefail
S=sersan/marchio-512.png
SCURO=0x1d1340   # sfondo delle icone che non reggono la trasparenza (iOS, anteprima dei link)
t=$(mktemp -d); trap 'rm -rf "$t"' EXIT

px() { sips -z "$1" "$1" "$S" --out "$2" >/dev/null; }
su_sfondo() {  # lato, lato del marchio, uscita
  px "$2" "$t/m.png"
  ffmpeg -loglevel error -y -f lavfi -i "color=c=$SCURO:s=$1x$1" -i "$t/m.png" \
    -filter_complex "overlay=(W-w)/2:(H-h)/2" -frames:v 1 "$3"
}

px 192 public/sersan-logo.png                 # logo dell'interfaccia (shared/_logo, logo.vue)
px 16 public/favicon-16x16.png
px 32 public/favicon-32x32.png
px 96 public/favicon-96x96.png
su_sfondo 180 150 public/apple-icon-180x180.png
cp public/apple-icon-180x180.png public/apple-touch-icon.png
cp public/apple-icon-180x180.png public/apple-touch-icon-precomposed.png
su_sfondo 800 560 public/preview.png          # anteprima dei link (og:image)
px 300 lib/pdf_icons/logo.png                 # registro di firma (audit trail) nei PDF
swift sersan/timbro.swift lib/pdf_icons/stamp-logo.png >/dev/null

# favicon.svg e logo.svg: l'immagine PNG dentro un SVG (DocuSeal li usa come SVG)
svg() {  # lato del PNG, uscita
  px "$1" "$t/s.png"
  printf '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s"><image width="%s" height="%s" href="data:image/png;base64,%s"/></svg>\n' \
    "$1" "$1" "$1" "$1" "$(base64 < "$t/s.png" | tr -d '\n')" > "$2"
}
svg 96 public/favicon.svg
svg 192 public/logo.svg

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
ls -la public/sersan-logo.png public/favicon* public/apple* public/preview.png public/logo.svg lib/pdf_icons/logo.png lib/pdf_icons/stamp-logo.png | awk '{print $5, $9}'
