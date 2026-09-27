import fitz
import os

ref_path = r'pdf_generator/Tamil_GOWTHAM _TN02638368(1)-1.pdf'
gen_path = 'test_generated_output.pdf'

ref_doc = fitz.open(ref_path)
gen_doc = fitz.open(gen_path)

ref_page = ref_doc[0]
gen_page = gen_doc[0]

# 1. Page Dimensions
print("=== 1. PAGE DIMENSIONS ===")
ref_rect = ref_page.rect
gen_rect = gen_page.rect
print(f"Ref Page: {ref_rect.width/2.83465:.2f}mm x {ref_rect.height/2.83465:.2f}mm")
print(f"Gen Page: {gen_rect.width/2.83465:.2f}mm x {gen_rect.height/2.83465:.2f}mm")

# Helper for text search with font details
def get_text_details(page, search_text):
    text_instances = []
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if "lines" in b:
            for line in b["lines"]:
                for span in line["spans"]:
                    if search_text.lower() in span["text"].lower():
                        bbox = span["bbox"]
                        # x0, y0, x1, y1 in mm
                        x0, y0, x1, y1 = bbox[0]/2.83465, bbox[1]/2.83465, bbox[2]/2.83465, bbox[3]/2.83465
                        text_instances.append({
                            "text": span["text"],
                            "bbox": (x0, y0, x1, y1),
                            "font": span["font"],
                            "size": span["size"],
                            "flags": span["flags"],
                            "color": span["color"]
                        })
    return text_instances

print("\n=== KEY TEXT ELEMENTS AUDIT ===")
key_items = [
    "HSN Code",
    "Date & Time Of Dispatch",
    "TN02638368",
    "Lessee Id",
    "Minecode",
    "Lessee Name and Address",
    "District Name",
    "Taluk Name",
    "Village",
    "SF.No",
    "Mineral Name",
    "Bulk Permit No",
    "Classification",
    "Order Ref",
    "Lease Period",
    "Dispatch Slip No",
    "Within Tamil Nadu",
    "Delivered To",
    "Vehicle No",
    "Destination Address",
    "Vehicle Type",
    "Total Distance In",
    "Traveling Date",
    "Required Time",
    "Quantity (in MT)",
    "Driver Name",
    "Driver License No",
    "Via",
    "Driver Phone No",
    "Lease / Authorized Person Name",
    "Driver Signature",
    "Signature of AD / DD"
]

report_lines = []

for item in key_items:
    ref_matches = get_text_details(ref_page, item)
    gen_matches = get_text_details(gen_page, item)
    
    ref_first = ref_matches[0] if ref_matches else None
    gen_first = gen_matches[0] if gen_matches else None
    
    report_lines.append(f"--- {item} ---")
    if ref_first:
        r_x0, r_y0, r_x1, r_y1 = ref_first["bbox"]
        report_lines.append(f"  REF: Pos=({r_x0:.2f}mm, {r_y0:.2f}mm), Size={ref_first['size']:.1f}pt, Font={ref_first['font']}")
    else:
        report_lines.append("  REF: Not found")
        
    if gen_first:
        g_x0, g_y0, g_x1, g_y1 = gen_first["bbox"]
        report_lines.append(f"  GEN: Pos=({g_x0:.2f}mm, {g_y0:.2f}mm), Size={gen_first['size']:.1f}pt, Font={gen_first['font']}")
    else:
        report_lines.append("  GEN: Not found")
        
    if ref_first and gen_first:
        dx = g_x0 - r_x0
        dy = g_y0 - r_y0
        dsize = gen_first['size'] - ref_first['size']
        report_lines.append(f"  DIFF: dX={dx:+.2f}mm, dY={dy:+.2f}mm, dSize={dsize:+.1f}pt")

with open("text_audit_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print("Text audit saved to text_audit_report.txt")
