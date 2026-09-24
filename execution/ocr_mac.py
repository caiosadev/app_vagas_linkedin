import sys
import subprocess
import fitz

def ocr_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img_path = f".tmp/page_{page.number}.png"
        pix.save(img_path)
        
        swift_script = f"""
import Vision
import AppKit

guard let image = NSImage(contentsOfFile: "{img_path}"),
      let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {{
    print("Error loading image")
    exit(1)
}}

let request = VNRecognizeTextRequest {{ (request, error) in
    guard let observations = request.results as? [VNRecognizedTextObservation] else {{ return }}
    let text = observations.compactMap({{ $0.topCandidates(1).first?.string }}).joined(separator: "\\n")
    print(text)
}}
request.recognitionLevel = .accurate
let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
try? handler.perform([request])
"""
        with open(".tmp/ocr.swift", "w") as f:
            f.write(swift_script)
            
        result = subprocess.run(["swift", ".tmp/ocr.swift"], capture_output=True, text=True)
        text += result.stdout + "\n"
    return text.strip()

print(ocr_pdf(".tmp/resumes/resume_1.pdf")[:500])
