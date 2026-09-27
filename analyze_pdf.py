import fitz
import sys

def convert(path, out):
    doc = fitz.open(path)
    page = doc[0]
    pix = page.get_pixmap()
    pix.save(out)

if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
