import fitz
import os

pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]

with open("all_pdfs_inspect.txt", "w", encoding="utf-8") as out:
    for pdf in sorted(pdf_files):
        try:
            doc = fitz.open(pdf)
            out.write(f"\n==================== {pdf} (pages: {len(doc)}) ====================\n")
            page = doc[0]
            for i, b in enumerate(page.get_text("blocks")):
                x0, y0, x1, y1 = [v/2.83465 for v in b[:4]]
                txt = b[4].replace('\n', ' ')
                if "HSN" in txt or "TN0" in txt or "Serial" in txt:
                    out.write(f"  Block {i:2d}: Y={y0:6.2f}mm..{y1:6.2f}mm | {txt[:65]}\n")
            for i, img in enumerate(page.get_image_info()):
                bbox = img["bbox"]
                x0, y0, x1, y1 = [v/2.83465 for v in bbox]
                out.write(f"  Image {i+1}: Y={y0:6.2f}mm..{y1:6.2f}mm\n")
        except Exception as e:
            out.write(f"  Error reading {pdf}: {e}\n")
