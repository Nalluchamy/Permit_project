import fitz
from PIL import Image
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(base_dir, "test_client_perfect.pdf")
out_path = os.path.join(base_dir, "sample_output.png")

if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(dpi=150)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.save(out_path)
    print(f"Sample generated at {out_path}")
else:
    print("PDF not found")
