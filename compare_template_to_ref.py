import fitz
import os
import sys

from permit_master_source import generate_pdf

test_data = {
    "serial_no": "TN02638368",
    "dispatch_slip": "DISP0000052993368",
    "minecode": "KKIN0025",
    "traveling_date": "03-04-2026",
    "traveling_time": "07:40 PM",
    "hsn_code": "5390009",
    "lessee_id": "CHN241557",
    "lessee_name": "Gautham P M",
    "lessee_address": "No. 19, 1 1th Avenue, Ashok nagar, Chennai - 600083",
    "district": "Kallakurichi",
    "taluk": "Ulundurpet",
    "village": "Kallamedu",
    "sf_no": "58/1 (P-1)., / 00002.85.00",
    "mineral": "Pebbles",
    "bulk_permit": "KKI250000399",
    "order_ref": "",
    "lease_period": "12-07-2024 to 07-11-2026",
    "classification": "Porampoke Land",
    "within_tn": "Yes",
    "delivered_to": "SARAVANAN",
    "vehicle_no": "TN46 M6499",
    "vehicle_type": "Tipper",
    "distance": "320",
    "destination": "ARANTHANGI",
    "via": "PERAMBALUR",
    "req_hours": "12",
    "driver_name": "SATHISH R",
    "driver_license": "TN91Y20180001610",
    "driver_phone": "-",
    "auth_person": "Gautham P M"
}

gen_pdf_path = os.path.abspath("test_generated_output.pdf")
generate_pdf(test_data, gen_pdf_path)

out = []

def analyze_pdf(pdf_path, title):
    doc = fitz.open(pdf_path)
    page = doc[0]
    drawings = page.get_drawings()
    
    lines = []
    for d in drawings:
        r = d['rect']
        if r.width > 350:
            lines.append((r.y0 / 2.83465, r.x0 / 2.83465, r.width / 2.83465))
            
    lines.sort(key=lambda x: x[0])
    unique_y = []
    for y, x, w in lines:
        if not unique_y or abs(y - unique_y[-1][0]) > 0.5:
            unique_y.append((y, x, w))
            
    top_block = [item for item in unique_y if item[0] < 150]
    bottom_block = [item for item in unique_y if item[0] >= 150]
    
    images = []
    for img_info in page.get_image_info():
        x0, y0, x1, y1 = img_info['bbox']
        images.append((x0/2.83465, y0/2.83465, (x1-x0)/2.83465, (y1-y0)/2.83465))
        
    out.append(f"\n================ {title} ================")
    if top_block:
        left_m = top_block[0][1]
        width = top_block[0][2]
        top = top_block[0][0]
        bottom = top_block[-1][0]
        height = bottom - top
        out.append(f"Top Table: Left Margin={left_m:.2f}mm, Right Margin={210-left_m-width:.2f}mm, Width={width:.2f}mm")
        out.append(f"Top Table: Top={top:.2f}mm, Bottom={bottom:.2f}mm, Height={height:.2f}mm")
        
    if bottom_block:
        top_b = bottom_block[0][0]
        bottom_b = bottom_block[-1][0]
        height_b = bottom_b - top_b
        out.append(f"Bottom Table: Top={top_b:.2f}mm, Bottom={bottom_b:.2f}mm, Height={height_b:.2f}mm")
        if top_block:
            out.append(f"Gap between Top Table Bottom and Bottom Table Top: {top_b - bottom:.2f}mm")
            
    if images:
        out.append(f"QR Code(s) found: {len(images)}")
        for idx, (x, y, w, h) in enumerate(images):
            out.append(f"  QR #{idx+1}: Top={y:.2f}mm, Left={x:.2f}mm, Size={w:.2f}x{h:.2f}mm")

analyze_pdf(r"pdf_generator/Tamil_GOWTHAM _TN02638368(1)-1.pdf", "REFERENCE PDF (SAMPLE)")
analyze_pdf(gen_pdf_path, "OUR GENERATED PDF (CURRENT)")

with open("comparison_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
