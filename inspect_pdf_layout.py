import fitz

with open("inspect_out.txt", "w", encoding="utf-8") as out:
    doc = fitz.open("final_rebuild_verification.pdf")
    out.write(f"Page count: {len(doc)}\n")
    page = doc[0]




    out.write(f"Page rect: {page.rect}\n")

    out.write("\n--- ALL TEXT BLOCKS ---\n")
    for i, b in enumerate(page.get_text("blocks")):
        x0, y0, x1, y1 = [v/2.83465 for v in b[:4]]
        txt = b[4].replace('\n', ' ')
        out.write(f"Block {i:2d}: Y={y0:6.2f}mm..{y1:6.2f}mm, X={x0:6.2f}mm..{x1:6.2f}mm | {txt[:70]}\n")

    out.write("\n--- ALL IMAGES ---\n")
    for i, img in enumerate(page.get_image_info()):
        bbox = img["bbox"]
        x0, y0, x1, y1 = [v/2.83465 for v in bbox]
        out.write(f"Image {i+1}: Y={y0:6.2f}mm..{y1:6.2f}mm, X={x0:6.2f}mm..{x1:6.2f}mm\n")

    out.write("\n--- TABLES (Horizontal Lines) ---\n")
    drawings = page.get_drawings()
    h_lines = []
    for d in drawings:
        for item in d["items"]:
            if item[0] == "l":
                p1, p2 = item[1], item[2]
                if abs(p1.y - p2.y) < 0.5 and abs(p2.x - p1.x) > 100:
                    h_lines.append(round(p1.y / 2.83465, 2))
    h_lines = sorted(list(set(h_lines)))
    out.write(f"Horizontal lines Y coords (mm): {h_lines}\n")

