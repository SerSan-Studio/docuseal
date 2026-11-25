// SerSan: lib/pdf_icons/stamp-logo.png, la scritta in diagonale dietro il campo "timbro" dei PDF firmati.
// Come quella di DocuSeal: 506x340, grigio, sfondo trasparente. Uso: swift sersan/timbro.swift <file.png>
import AppKit

let larghezza = 506, altezza = 340
let uscita = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "stamp-logo.png"

guard let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: larghezza, pixelsHigh: altezza,
                                  bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                                  colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0),
      let contesto = NSGraphicsContext(bitmapImageRep: rep) else { fatalError("niente contesto grafico") }

NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = contesto
let cg = contesto.cgContext
cg.clear(CGRect(x: 0, y: 0, width: larghezza, height: altezza))

let testo = "SerSan" as NSString
let attributi: [NSAttributedString.Key: Any] = [
  .font: NSFont.systemFont(ofSize: 132, weight: .heavy),
  .foregroundColor: NSColor(calibratedWhite: 0.5, alpha: 1.0),
]
let misura = testo.size(withAttributes: attributi)
cg.translateBy(x: CGFloat(larghezza) / 2, y: CGFloat(altezza) / 2)
cg.rotate(by: 34 * .pi / 180)
testo.draw(at: NSPoint(x: -misura.width / 2, y: -misura.height / 2), withAttributes: attributi)
NSGraphicsContext.restoreGraphicsState()

guard let png = rep.representation(using: .png, properties: [:]) else { fatalError("niente PNG") }
try! png.write(to: URL(fileURLWithPath: uscita))
print("scritto \(uscita)")
