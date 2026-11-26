// SerSan: stili per la firma scritta (il nome digitato), come nei servizi di firma più noti. Vedi SERSAN.md.
// Caratteri con licenza OFL in public/sersan-firme/ (licenze accanto). Dancing Script è quello che DocuSeal
// aveva già, in /fonts; non ha il cirillico, quindi per i nomi in russo si usano solo gli altri due.
// I file sono divisi per alfabeto: il browser scarica solo quelli che servono per il nome scritto.

const LATIN = 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'
const LATIN_EXT = 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF'
const CYRILLIC = 'U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116'
const CYRILLIC_EXT = 'U+0460-052F,U+1C80-1C8A,U+20B4,U+2DE0-2DFF,U+A640-A69F,U+FE2E-FE2F'

const SUBSETS = [['latin', LATIN], ['latin-ext', LATIN_EXT], ['cyrillic', CYRILLIC], ['cyrillic-ext', CYRILLIC_EXT]]

export const SIGNATURE_FONTS = [
  { family: 'Great Vibes', file: 'great-vibes', size: 54, style: '', cyrillic: true },
  { family: 'Dancing Script', size: 44, style: 'italic', cyrillic: false },
  { family: 'Caveat', file: 'caveat', size: 52, style: '', cyrillic: true }
]

const CYRILLIC_RE = /[Ѐ-ԯ]/

let registered = false

export function fontsFor (text) {
  return CYRILLIC_RE.test(text || '') ? SIGNATURE_FONTS.filter((f) => f.cyrillic) : SIGNATURE_FONTS
}

export function fontFor (family, text) {
  const fonts = fontsFor(text)

  return fonts.find((f) => f.family === family) || fonts[0]
}

export function fontSpec (font) {
  return `${font.style} ${font.size}px "${font.family}"`.trim()
}

// Registra i caratteri (una volta sola) e scarica quelli che servono per il testo dato.
export function loadSignatureFonts (baseUrl, text) {
  if (!registered) {
    registered = true

    const faces = [new FontFace('Dancing Script', `url(${baseUrl}/fonts/DancingScript-Regular.otf) format("opentype")`)]

    SIGNATURE_FONTS.filter((f) => f.file).forEach((f) => {
      SUBSETS.forEach(([subset, unicodeRange]) => {
        faces.push(new FontFace(f.family, `url(${baseUrl}/sersan-firme/${f.file}-${subset}.woff2) format("woff2")`, { unicodeRange }))
      })
    })

    faces.forEach((face) => document.fonts.add(face))
  }

  const sample = text || 'Firma'

  return Promise.all(fontsFor(text).map((font) => {
    return document.fonts.load(fontSpec(font), sample).catch((error) => {
      console.error('Font loading failed:', error)
    })
  }))
}
