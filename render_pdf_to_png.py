import fitz

doc = fitz.open("test_output_verify.pdf")
page = doc[0]
pix = page.get_pixmap(dpi=150)
pix.save("test_pdf_page.png")
print("Saved test_pdf_page.png (150 dpi)")
