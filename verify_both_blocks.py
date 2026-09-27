import fitz

doc = fitz.open("test_generated_output.pdf")
print("Total pages:", len(doc))
page = doc[0]
rect = page.rect
print(f"Page dimensions: {rect.width/2.83465:.2f} mm x {rect.height/2.83465:.2f} mm")

# Extract all text blocks with coordinates
blocks = page.get_text("blocks")

hsn_blocks = []
for b in blocks:
    txt = b[4].strip()
    if "HSN Code" in txt or "Date & Time Of Dispatch" in txt:
        y0_mm = b[1] / 2.83465
        y1_mm = b[3] / 2.83465
        print(f"Text: '{txt[:35]}...' @ Y: {y0_mm:.2f}mm -> {y1_mm:.2f}mm")
        hsn_blocks.append((y0_mm, y1_mm))

# Extract tables / drawings
drawings = page.get_drawings()
horizontal_lines = []
for d in drawings:
    for item in d["items"]:
        if item[0] == "l": # line
            p1, p2 = item[1], item[2]
            if abs(p1.y - p2.y) < 0.5 and (p2.x - p1.x) > 100: # wide horizontal line
                horizontal_lines.append(p1.y / 2.83465)

horizontal_lines = sorted(list(set([round(y, 1) for y in horizontal_lines])))

top_table_top = horizontal_lines[0]
top_table_bot = horizontal_lines[18]
bot_table_top = horizontal_lines[19]
bot_table_bot = horizontal_lines[-1]

print(f"\nTop Table Bounds: {top_table_top:.2f}mm to {top_table_bot:.2f}mm")
print(f"Bottom Table Bounds: {bot_table_top:.2f}mm to {bot_table_bot:.2f}mm")

print("\n--- Overlap Verification ---")
if len(hsn_blocks) >= 2:
    hsn2_top, hsn2_bot = hsn_blocks[-1]
    if hsn2_bot < bot_table_top:
        print(f"PASS: Bottom HSN Line (Y={hsn2_bot:.2f}mm) is ABOVE Bottom Table Top (Y={bot_table_top:.2f}mm). Gap = {bot_table_top - hsn2_bot:.2f}mm")
    else:
        print(f"FAIL: Bottom HSN Line overlaps Bottom Table!")

# Check QR code positions
imgs = page.get_image_info()
print("\n--- Image / QR Positions ---")
for i, img in enumerate(imgs):
    bbox = img["bbox"]
    x0, y0, x1, y1 = [v/2.83465 for v in bbox]
    print(f"Image {i+1}: X={x0:.2f}mm..{x1:.2f}mm, Y={y0:.2f}mm..{y1:.2f}mm")
    if i >= 1: # Second permit images
        if y1 < bot_table_top and y0 > top_table_bot:
            print(f"PASS: Bottom QR Code (Y={y0:.2f}mm..{y1:.2f}mm) is ABOVE Bottom Table Top (Y={bot_table_top:.2f}mm). Gap = {bot_table_top - y1:.2f}mm")
