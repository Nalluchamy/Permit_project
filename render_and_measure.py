import fitz

ref_doc = fitz.open(r'pdf_generator/Tamil_GOWTHAM _TN02638368(1)-1.pdf')
gen_doc = fitz.open('test_generated_output.pdf')

ref_page = ref_doc[0]
gen_page = gen_doc[0]

ref_pix = ref_page.get_pixmap(dpi=300)
gen_pix = gen_page.get_pixmap(dpi=300)

ref_pix.save('ref_300dpi.png')
gen_pix.save('gen_300dpi.png')

print("Saved ref_300dpi.png and gen_300dpi.png")

# Extract text block positions for top table start ("Lessee Id") and bottom table end ("Signature of AD")
def find_text_bbox(page, search_str):
    rects = page.search_for(search_str)
    if rects:
        r = rects[0]
        return r.x0 / 2.83465, r.y0 / 2.83465, r.x1 / 2.83465, r.y1 / 2.83465
    return None

print("\n=== REFERENCE PDF TEXT POSITIONS ===")
print("Lessee Id (Top Table Top):", find_text_bbox(ref_page, "Lessee Id"))
print("Signature of AD (Top Table Bottom):", find_text_bbox(ref_page, "Signature of AD"))

print("\n=== GENERATED PDF TEXT POSITIONS ===")
print("Lessee Id (Top Table Top):", find_text_bbox(gen_page, "Lessee Id"))
print("Signature of AD (Top Table Bottom):", find_text_bbox(gen_page, "Signature of AD"))
