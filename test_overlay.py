import fitz
from PIL import Image
import os
import sys

def create_overlay():
    # 1. Generate the PDF
    os.system('python test_generate.py')
    
    # 2. Render FORM.pdf
    doc_bg = fitz.open('pdf_generator/FORM.pdf')
    pix_bg = doc_bg[0].get_pixmap(dpi=150)
    bg_img = Image.frombytes("RGB", [pix_bg.width, pix_bg.height], pix_bg.samples)
    
    # 3. Render Generated PDF with transparent background
    doc_fg = fitz.open('Test_Reference_Match.pdf')
    pix_fg = doc_fg[0].get_pixmap(dpi=150, alpha=True)
    fg_img = Image.frombytes("RGBA", [pix_fg.width, pix_fg.height], pix_fg.samples)
    
    # Make white pixels transparent
    data = fg_img.getdata()
    newData = []
    for item in data:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    fg_img.putdata(newData)
    
    # 4. Composite
    # Resize bg_img to match fg_img just in case (should be the same if both A4 at 150dpi)
    if bg_img.size != fg_img.size:
        bg_img = bg_img.resize(fg_img.size)
        
    bg_img.paste(fg_img, (0, 0), fg_img)
    
    from PIL import ImageDraw
    draw = ImageDraw.Draw(bg_img)
    # Draw horizontal lines every 10mm. At 150dpi, 10mm is approx 59 pixels.
    mm_px = 150 / 25.4
    for i in range(0, 300, 10):
        y = int(i * mm_px)
        draw.line([(0, y), (bg_img.width, y)], fill=(255, 0, 0, 128), width=2)
        draw.text((10, y), f"{i}mm", fill=(255, 0, 0, 255))
        draw.text((bg_img.width - 50, y), f"{i}mm", fill=(255, 0, 0, 255))
    
    bg_img.save('overlay_preview.png')
    print("Overlay created at overlay_preview.png")

if __name__ == "__main__":
    create_overlay()
