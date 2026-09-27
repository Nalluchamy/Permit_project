import fitz
from PIL import Image

def create_comparison(client_pdf, my_pdf, out_path):
    # Convert client PDF page 1 to image
    doc1 = fitz.open(client_pdf)
    pix1 = doc1[0].get_pixmap(dpi=150)
    img1 = Image.frombytes("RGB", [pix1.width, pix1.height], pix1.samples)
    
    # Convert my PDF page 1 to image
    doc2 = fitz.open(my_pdf)
    pix2 = doc2[0].get_pixmap(dpi=150)
    img2 = Image.frombytes("RGB", [pix2.width, pix2.height], pix2.samples)
    
    # Create combined image
    w = img1.width + img2.width + 20
    h = max(img1.height, img2.height)
    combined = Image.new('RGB', (w, h), (255, 255, 255))
    combined.paste(img1, (0, 0))
    combined.paste(img2, (img1.width + 20, 0))
    combined.save(out_path)

if __name__ == "__main__":
    import sys
    create_comparison(sys.argv[1], sys.argv[2], sys.argv[3])
