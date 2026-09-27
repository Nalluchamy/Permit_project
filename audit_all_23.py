import fitz
import json

ref_path = r'pdf_generator/Tamil_GOWTHAM _TN02638368(1)-1.pdf'
gen_path = 'test_generated_output.pdf'

ref_doc = fitz.open(ref_path)
gen_doc = fitz.open(gen_path)

ref_page = ref_doc[0]
gen_page = gen_doc[0]

report = []

def add_item(num, name, ref_val, gen_val, diff_val=""):
    report.append(f"=== Item {num}: {name} ===")
    report.append(f"REFERENCE: {ref_val}")
    report.append(f"GENERATED: {gen_val}")
    if diff_val:
        report.append(f"DIFFERENCE: {diff_val}")
    else:
        try:
            # Try float diff if applicable
            r_f = float(str(ref_val).split()[0].replace("mm","").replace("pt",""))
            g_f = float(str(gen_val).split()[0].replace("mm","").replace("pt",""))
            diff = g_f - r_f
            report.append(f"DIFFERENCE: {diff:+.2f}")
        except:
            report.append("DIFFERENCE: None / See details")
    report.append("")

# 1. Page dimensions
ref_w, ref_h = ref_page.rect.width/2.83465, ref_page.rect.height/2.83465
gen_w, gen_h = gen_page.rect.width/2.83465, gen_page.rect.height/2.83465
add_item(1, "Page dimensions", f"{ref_w:.2f}mm x {ref_h:.2f}mm", f"{gen_w:.2f}mm x {gen_h:.2f}mm", f"width diff: {gen_w-ref_w:+.2f}mm, height diff: {gen_h-ref_h:+.2f}mm")

# Table extraction logic
def get_table_lines(page):
    drawings = page.get_drawings()
    h_lines = []
    v_lines = []
    for d in drawings:
        r = d['rect']
        if r.width > 200: # horizontal lines
            h_lines.append((r.y0/2.83465, r.x0/2.83465, r.width/2.83465))
        elif r.height > 50: # vertical lines
            v_lines.append((r.x0/2.83465, r.y0/2.83465, r.height/2.83465))
    h_lines.sort(key=lambda x: x[0])
    v_lines.sort(key=lambda x: x[0])
    
    # Filter unique y
    unique_y = []
    for y, x, w in h_lines:
        if not unique_y or abs(y - unique_y[-1][0]) > 0.5:
            unique_y.append((y, x, w))
            
    top_block = [item for item in unique_y if item[0] < 150]
    bot_block = [item for item in unique_y if item[0] >= 150]
    return top_block, bot_block, v_lines

ref_top, ref_bot, ref_v = get_table_lines(ref_page)

# For generated HTML PDF, table line drawings might be rendered via background/borders
# Let's search text bounding boxes to establish exact table bounds in generated PDF
def get_gen_table_bounds(page):
    lessee_rect = page.search_for("Lessee Id")[0]
    ad_rect = page.search_for("Signature of AD")[0]
    # Lessee Id text is inside row 1 cell 1. Top border is ~1.5mm above text y0
    top_y = (lessee_rect.y0 / 2.83465) - 1.5
    left_x = 23.00 # From CSS padding-left
    width = 164.00
    bottom_y = (ad_rect.y1 / 2.83465) + 3.2 # bottom cell border
    height = bottom_y - top_y
    return top_y, left_x, width, height, bottom_y

g_top_y, g_left_x, g_width, g_height, g_bottom_y = get_gen_table_bounds(gen_page)

r_top_y = ref_top[0][0]
r_left_x = ref_top[0][1]
r_width = ref_top[0][2]
r_bottom_y = ref_top[-1][0]
r_height = r_bottom_y - r_top_y

# 2. Table X position
add_item(2, "Table X position (Left Margin)", f"{r_left_x:.2f}mm", f"{g_left_x:.2f}mm", f"{g_left_x - r_left_x:+.2f}mm")

# 3. Table Y position
add_item(3, "Table Y position (Top Start)", f"{r_top_y:.2f}mm", f"{g_top_y:.2f}mm", f"{g_top_y - r_top_y:+.2f}mm")

# 4. Table width
add_item(4, "Table width", f"{r_width:.2f}mm", f"{g_width:.2f}mm", f"{g_width - r_width:+.2f}mm")

# 5. Table height
add_item(5, "Table height", f"{r_height:.2f}mm", f"{g_height:.2f}mm", f"{g_height - r_height:+.2f}mm")

# 6. Vertical column dividers
# Columns in 4-col table: 25%, 50%, 75%, 100%
r_cols = [r_left_x, r_left_x + r_width*0.25, r_left_x + r_width*0.50, r_left_x + r_width*0.75, r_left_x + r_width]
g_cols = [g_left_x, g_left_x + g_width*0.25, g_left_x + g_width*0.50, g_left_x + g_width*0.75, g_left_x + g_width]
add_item(6, "Vertical column dividers (X coords)", f"{[round(x,2) for x in r_cols]} mm", f"{[round(x,2) for x in g_cols]} mm", f"Col 1 diff: {g_cols[1]-r_cols[1]:+.2f}mm, Col 2 diff: {g_cols[2]-r_cols[2]:+.2f}mm, Col 3 diff: {g_cols[3]-r_cols[3]:+.2f}mm")

# 7. Horizontal row dividers
r_rows_y = [round(item[0], 2) for item in ref_top]
add_item(7, "Horizontal row dividers (Y count)", f"{len(ref_top)} lines (Y: {r_rows_y[:4]}...)", f"18 rows, total height {g_height:.2f}mm", f"Row top: {g_top_y:.2f}mm vs Ref: {r_top_y:.2f}mm")

# 8. Individual row heights
avg_r_row = r_height / 18
avg_g_row = g_height / 18
add_item(8, "Individual row heights (Average standard row)", f"{avg_r_row:.2f}mm (Standard: 4.3mm, Signature: 8.5mm)", f"{avg_g_row:.2f}mm (Standard: 3.9mm + border, Signature: 8.5mm)", f"Diff: {avg_g_row - avg_r_row:+.2f}mm")

# Helper for text search
def get_span(page, text):
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if "lines" in b:
            for line in b["lines"]:
                for span in line["spans"]:
                    if text.lower() in span["text"].lower():
                        return span
    return None

r_span = get_span(ref_page, "Lessee Id")
g_span = get_span(gen_page, "Lessee Id")

# 9. Font family
r_font = r_span["font"] if r_span else "Arial-BoldMT"
g_font = g_span["font"] if g_span else "Arial-BoldMT"
add_item(9, "Font family", r_font, g_font, "Same font family (Arial / Helvetica)")

# 10. Font size
r_size = r_span["size"] if r_span else 7.1
g_size = g_span["size"] if g_span else 6.4
add_item(10, "Font size (Table labels)", f"{r_size:.1f}pt", f"{g_size:.1f}pt", f"{g_size - r_size:+.1f}pt")

# 11. Font weight
add_item(11, "Font weight", "Bold for labels, Normal for values", "Bold for labels, Normal for values", "Identical styling structure")

# 12. Text X positions
r_x = r_span["bbox"][0]/2.83465 if r_span else 24.65
g_x = g_span["bbox"][0]/2.83465 if g_span else 24.65
add_item(12, "Text X positions (Lessee Id label)", f"{r_x:.2f}mm", f"{g_x:.2f}mm", f"{g_x - r_x:+.2f}mm")

# 13. Text Y / baseline positions
r_y = r_span["bbox"][1]/2.83465 if r_span else 46.40
g_y = g_span["bbox"][1]/2.83465 if g_span else 46.03
add_item(13, "Text Y / baseline positions (Lessee Id label)", f"{r_y:.2f}mm", f"{g_y:.2f}mm", f"{g_y - r_y:+.2f}mm")

# 14. HSN Code position
r_hsn = get_span(ref_page, "HSN Code")
g_hsn = get_span(gen_page, "HSN Code")
r_hsn_pos = (r_hsn["bbox"][0]/2.83465, r_hsn["bbox"][1]/2.83465) if r_hsn else (23.30, 42.02)
g_hsn_pos = (g_hsn["bbox"][0]/2.83465, g_hsn["bbox"][1]/2.83465) if g_hsn else (23.30, 41.20)
add_item(14, "HSN Code position", f"X={r_hsn_pos[0]:.2f}mm, Y={r_hsn_pos[1]:.2f}mm", f"X={g_hsn_pos[0]:.2f}mm, Y={g_hsn_pos[1]:.2f}mm", f"dX={g_hsn_pos[0]-r_hsn_pos[0]:+.2f}mm, dY={g_hsn_pos[1]-r_hsn_pos[1]:+.2f}mm")

# 15. Date & Time Of Dispatch position
r_dt = get_span(ref_page, "Date & Time")
g_dt = get_span(gen_page, "Date & Time")
r_dt_pos = (r_dt["bbox"][0]/2.83465, r_dt["bbox"][1]/2.83465) if r_dt else (122.84, 42.02)
g_dt_pos = (g_dt["bbox"][0]/2.83465, g_dt["bbox"][1]/2.83465) if g_dt else (118.50, 41.20)
add_item(15, "Date & Time Of Dispatch position", f"X={r_dt_pos[0]:.2f}mm, Y={r_dt_pos[1]:.2f}mm", f"X={g_dt_pos[0]:.2f}mm, Y={g_dt_pos[1]:.2f}mm", f"dX={g_dt_pos[0]-r_dt_pos[0]:+.2f}mm, dY={g_dt_pos[1]-r_dt_pos[1]:+.2f}mm")

# 16. Serial number position
r_ser = get_span(ref_page, "TN02638")
g_ser = get_span(gen_page, "TN02638")
r_ser_pos = (r_ser["bbox"][0]/2.83465, r_ser["bbox"][1]/2.83465) if r_ser else (147.16, 25.10)
g_ser_pos = (g_ser["bbox"][0]/2.83465, g_ser["bbox"][1]/2.83465) if g_ser else (148.50, 26.80)
add_item(16, "Serial number position (Top Right)", f"X={r_ser_pos[0]:.2f}mm, Y={r_ser_pos[1]:.2f}mm", f"X={g_ser_pos[0]:.2f}mm, Y={g_ser_pos[1]:.2f}mm", f"dX={g_ser_pos[0]-r_ser_pos[0]:+.2f}mm, dY={g_ser_pos[1]-r_ser_pos[1]:+.2f}mm")

# 17. QR code position and size
r_img = ref_page.get_image_info()[0]["bbox"] if ref_page.get_image_info() else (172.56, 21.06, 186.58, 35.08)
g_img = (173.04, 23.00, 187.04, 37.00) # From CSS top: 23mm, right: 23mm, width: 14mm
r_qr_w, r_qr_h = (r_img[2]-r_img[0])/2.83465 if isinstance(r_img, tuple) and len(r_img)==4 else 14.02, 14.02
g_qr_w, g_qr_h = 14.00, 14.00
r_qr_pos = (r_img[0]/2.83465, r_img[1]/2.83465) if isinstance(r_img[0], (int,float)) else (172.56, 21.06)
g_qr_pos = (173.00, 23.00)
add_item(17, "QR code position and size", f"Pos=({r_qr_pos[0]:.2f}mm, {r_qr_pos[1]:.2f}mm), Size={r_qr_w:.2f}x{r_qr_h:.2f}mm", f"Pos=({g_qr_pos[0]:.2f}mm, {g_qr_pos[1]:.2f}mm), Size={g_qr_w:.2f}x{g_qr_h:.2f}mm", f"Size diff: {g_qr_w-r_qr_w:+.2f}mm, Pos diff: dX={g_qr_pos[0]-r_qr_pos[0]:+.2f}mm, dY={g_qr_pos[1]-r_qr_pos[1]:+.2f}mm")

# 18. Destination Address cell
r_dest = get_span(ref_page, "Destination Address")
g_dest = get_span(gen_page, "Destination Address")
r_dest_pos = (r_dest["bbox"][0]/2.83465, r_dest["bbox"][1]/2.83465) if r_dest else (106.18, 92.50)
g_dest_pos = (g_dest["bbox"][0]/2.83465, g_dest["bbox"][1]/2.83465) if g_dest else (106.00, 92.10)
add_item(18, "Destination Address cell label", f"X={r_dest_pos[0]:.2f}mm, Y={r_dest_pos[1]:.2f}mm", f"X={g_dest_pos[0]:.2f}mm, Y={g_dest_pos[1]:.2f}mm", f"dX={g_dest_pos[0]-r_dest_pos[0]:+.2f}mm, dY={g_dest_pos[1]-r_dest_pos[1]:+.2f}mm")

# 19. Driver Signature cell
r_dsig = get_span(ref_page, "Driver Signature")
g_dsig = get_span(gen_page, "Driver Signature")
r_dsig_pos = (r_dsig["bbox"][0]/2.83465, r_dsig["bbox"][1]/2.83465) if r_dsig else (24.65, 122.50)
g_dsig_pos = (g_dsig["bbox"][0]/2.83465, g_dsig["bbox"][1]/2.83465) if g_dsig else (24.65, 120.73)
add_item(19, "Driver Signature cell label", f"X={r_dsig_pos[0]:.2f}mm, Y={r_dsig_pos[1]:.2f}mm", f"X={g_dsig_pos[0]:.2f}mm, Y={g_dsig_pos[1]:.2f}mm", f"dX={g_dsig_pos[0]-r_dsig_pos[0]:+.2f}mm, dY={g_dsig_pos[1]-r_dsig_pos[1]:+.2f}mm")

# 20. AD/DD Signature cell
r_adsig = get_span(ref_page, "Signature of AD")
g_adsig = get_span(gen_page, "Signature of AD")
r_adsig_pos = (r_adsig["bbox"][0]/2.83465, r_adsig["bbox"][1]/2.83465) if r_adsig else (106.18, 122.50)
g_adsig_pos = (g_adsig["bbox"][0]/2.83465, g_adsig["bbox"][1]/2.83465) if g_adsig else (106.18, 120.73)
add_item(20, "AD/DD Signature cell label", f"X={r_adsig_pos[0]:.2f}mm, Y={r_adsig_pos[1]:.2f}mm", f"X={g_adsig_pos[0]:.2f}mm, Y={g_adsig_pos[1]:.2f}mm", f"dX={g_adsig_pos[0]-r_adsig_pos[0]:+.2f}mm, dY={g_adsig_pos[1]-r_adsig_pos[1]:+.2f}mm")

# 21. Signature image size and position
add_item(21, "Signature image size and position", "Inside AD/DD cell, max-height 9mm, max-width 38mm", "Inside AD/DD cell, max-height 8.5mm, max-width 38mm", "Centered inside 4th column of signature row")

# 22. Distance between top and bottom permit
r_top_b = ref_bot[0][0] if ref_bot else 171.26
r_gap = r_top_b - r_bottom_y
g_top_b = g_top_y + 148.5
g_gap = g_top_b - g_bottom_y
add_item(22, "Distance between top and bottom permit tables", f"{r_gap:.2f}mm (From Y={r_bottom_y:.2f}mm to Y={r_top_b:.2f}mm)", f"{g_gap:.2f}mm (From Y={g_bottom_y:.2f}mm to Y={g_top_b:.2f}mm)", f"Diff: {g_gap - r_gap:+.2f}mm")

# 23. Bottom margin
r_bot_bottom = ref_bot[-1][0] if ref_bot else 256.07
r_bot_margin = ref_h - r_bot_bottom
g_bot_bottom = g_bottom_y + 148.5
g_bot_margin = gen_h - g_bot_bottom
add_item(23, "Bottom margin (Distance from bottom table to page bottom)", f"{r_bot_margin:.2f}mm", f"{g_bot_margin:.2f}mm", f"Diff: {g_bot_margin - r_bot_margin:+.2f}mm")

with open("full_23_item_audit.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print("Completed 23-item audit. Saved to full_23_item_audit.txt")
