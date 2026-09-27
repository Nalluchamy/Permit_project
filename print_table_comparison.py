import fitz

ref_doc = fitz.open(r'pdf_generator/Tamil_GOWTHAM _TN02638368(1)-1.pdf')
gen_doc = fitz.open('test_generated_output.pdf')

def get_stats(doc):
    page = doc[0]
    drawings = page.get_drawings()
    lines = sorted([(r.y0/2.83465, r.x0/2.83465, r.width/2.83465) for d in drawings for r in [d['rect']] if r.width > 350], key=lambda x: x[0])
    unique_y = []
    for y, x, w in lines:
        if not unique_y or abs(y - unique_y[-1][0]) > 0.5:
            unique_y.append((y, x, w))
    top_b = [item for item in unique_y if item[0] < 150]
    bot_b = [item for item in unique_y if item[0] >= 150]
    imgs = [(img['bbox'][0]/2.83465, img['bbox'][1]/2.83465, (img['bbox'][2]-img['bbox'][0])/2.83465, (img['bbox'][3]-img['bbox'][1])/2.83465) for img in page.get_image_info()]
    return top_b, bot_b, imgs

r_top, r_bot, r_imgs = get_stats(ref_doc)
g_top, g_bot, g_imgs = get_stats(gen_doc)

print("=== REFERENCE PDF TABLES ===")
print("Top table count lines:", len(r_top))
if r_top:
    print(f"Top Table: Top={r_top[0][0]:.2f}mm, Bottom={r_top[-1][0]:.2f}mm, Height={r_top[-1][0]-r_top[0][0]:.2f}mm, Left={r_top[0][1]:.2f}mm, Width={r_top[0][2]:.2f}mm")
print("Bottom table count lines:", len(r_bot))
if r_bot:
    print(f"Bottom Table: Top={r_bot[0][0]:.2f}mm, Bottom={r_bot[-1][0]:.2f}mm, Height={r_bot[-1][0]-r_bot[0][0]:.2f}mm, Left={r_bot[0][1]:.2f}mm, Width={r_bot[0][2]:.2f}mm")

print("\n=== GENERATED PDF TABLES (OUR FIX) ===")
print("Top table count lines:", len(g_top))
if g_top:
    print(f"Top Table: Top={g_top[0][0]:.2f}mm, Bottom={g_top[-1][0]:.2f}mm, Height={g_top[-1][0]-g_top[0][0]:.2f}mm, Left={g_top[0][1]:.2f}mm, Width={g_top[0][2]:.2f}mm")
print("Bottom table count lines:", len(g_bot))
if g_bot:
    print(f"Bottom Table: Top={g_bot[0][0]:.2f}mm, Bottom={g_bot[-1][0]:.2f}mm, Height={g_bot[-1][0]-g_bot[0][0]:.2f}mm, Left={g_bot[0][1]:.2f}mm, Width={g_bot[0][2]:.2f}mm")
