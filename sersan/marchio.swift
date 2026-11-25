// SerSan: il marchio SerSan in PNG, dalle stesse forme di sersan.io (le due metà dell'esagono, 162.38 x 200).
// Uso: swift sersan/marchio.swift <lato> <uscita.png> [sfondo|none] [colore alto] [colore basso] [margine]
// Colori in esadecimale senza #. Margine: frazione del lato lasciata vuota attorno al marchio (0.06 = 6%).
import AppKit

let a = CommandLine.arguments
guard a.count >= 3, let lato = Int(a[1]) else { fatalError("uso: marchio.swift <lato> <uscita.png> [sfondo] [alto] [basso] [margine]") }
let uscita = a[2]
let sfondo = a.count > 3 ? a[3] : "none"
let alto = a.count > 4 ? a[4] : "132741"   // navy del marchio
let basso = a.count > 5 ? a[5] : "2280DC"  // blu del marchio
let margine = a.count > 6 ? Double(a[6]) ?? 0.06 : 0.06

func colore(_ hex: String) -> CGColor {
  let v = UInt32(hex, radix: 16) ?? 0
  return CGColor(srgbRed: CGFloat((v >> 16) & 0xff) / 255, green: CGFloat((v >> 8) & 0xff) / 255,
                 blue: CGFloat(v & 0xff) / 255, alpha: 1)
}

let su: [(Double, Double)] = [(81.19, 0), (162.38, 46.88), (127.3, 67.13), (81.19, 40.51), (39.64, 64.49),
                              (39.64, 90.03), (80.11, 113.4), (40.6, 136.21), (0, 112.78), (0, 46.88)]
let giu: [(Double, Double)] = [(81.19, 200), (0, 153.13), (35.08, 132.87), (81.19, 159.49), (122.73, 135.51),
                               (122.73, 109.97), (82.27, 86.6), (121.78, 63.79), (162.38, 87.22), (162.38, 153.13)]

guard let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: lato, pixelsHigh: lato, bitsPerSample: 8,
                                 samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
                                 bytesPerRow: 0, bitsPerPixel: 0),
      let contesto = NSGraphicsContext(bitmapImageRep: rep) else { fatalError("niente contesto grafico") }

NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = contesto
let cg = contesto.cgContext
let l = Double(lato)
cg.clear(CGRect(x: 0, y: 0, width: l, height: l))
if sfondo != "none" {
  cg.setFillColor(colore(sfondo))
  cg.fill(CGRect(x: 0, y: 0, width: l, height: l))
}
cg.setShouldAntialias(true)

let scala = l * (1 - 2 * margine) / 200
let ox = (l - 162.38 * scala) / 2, oy = (l - 200 * scala) / 2
func disegna(_ punti: [(Double, Double)], _ c: CGColor) {
  let p = CGMutablePath()
  for (i, (x, y)) in punti.enumerated() {
    let q = CGPoint(x: ox + x * scala, y: l - (oy + y * scala))  // l'SVG ha la y verso il basso
    if i == 0 { p.move(to: q) } else { p.addLine(to: q) }
  }
  p.closeSubpath()
  cg.addPath(p)
  cg.setFillColor(c)
  cg.fillPath()
}
disegna(su, colore(alto))
disegna(giu, colore(basso))
NSGraphicsContext.restoreGraphicsState()

guard let png = rep.representation(using: .png, properties: [:]) else { fatalError("niente PNG") }
try! png.write(to: URL(fileURLWithPath: uscita))
