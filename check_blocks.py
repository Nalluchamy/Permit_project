import fitz
import sys

doc = fitz.open("test_generated_output.pdf")
page = doc[0]

lines = []
lines.append(f"Page: {page.rect.width/2.83465:.2f} x {page.rect.height/2.83465:.2f} mm")

lines.append("\n=== KEY TEXT BLOCKS ===")
for b in sorted(page.get_text("blocks"), key=lambda x: x[1]):
    txt = b[4].strip().replace("\n", " ")
    y0 = b[1] / 2.83465
    y1 = b[3] / 2.83465
    if "HSN" in txt or "TN0" in txt:
        lines.append(f"  Y={y0:7.2f} -> {y1:7.2f} | {txt[:60]}")

lines.append("\n=== QR IMAGES ===")
for i, img in enumerate(page.get_image_info()):
    bbox = img["bbox"]
    x0 = bbox[0] / 2.83465
    y0 = bbox[1] / 2.83465
    x1 = bbox[2] / 2.83465
    y1 = bbox[3] / 2.83465
    lines.append(f"  QR{i+1}: X={x0:.2f}..{x1:.2f}, Y={y0:.2f}..{y1:.2f}")

lines.append("\n=== TABLE BORDERS ===")
drawings = page.get_drawings()
rect_y_vals = []
for d in drawings:
    for item in d["items"]:
        if item[0] == "re":
            r = item[1]
            if r.width > 100 and r.height < 2:
                rect_y_vals.append(round(r.y0 / 2.83465, 2))
rect_y_vals = sorted(set(rect_y_vals))
lines.append(f"  Count: {len(rect_y_vals)}")

if rect_y_vals:
    gaps = [(rect_y_vals[i+1] - rect_y_vals[i], i) for i in range(len(rect_y_vals)-1)]
    biggest_gap = max(gaps, key=lambda x: x[0])
    split = biggest_gap[1]
    table1 = rect_y_vals[:split+1]
    table2 = rect_y_vals[split+1:]
    lines.append(f"  TOP TABLE: {table1[0]:.2f} -> {table1[-1]:.2f}")
    lines.append(f"  BOT TABLE: {table2[0]:.2f} -> {table2[-1]:.2f}")
    lines.append(f"  Top table offset from page top: {table1[0]:.2f}")
    first_block_h = 126.38
    lines.append(f"  Bot table offset from block2 top ({first_block_h}): {table2[0] - first_block_h:.2f}")

for line in lines:
    sys.stdout.write(line + "\n")
    sys.stdout.flush()
