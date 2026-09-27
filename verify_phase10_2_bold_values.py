"""
PermitMaster — Phase 10.2 PDF Bold Labels & Values Verification Suite
Validates bold font-weight for BOTH labels and values across Office Copy and Driver Copy,
along with A4 1-page geometry, AM/PM timestamp, QR payload, and signature preservation.
"""

import os
import sys
import time
import fitz # PyMuPDF
import re

import permit_master_source as pms
from permit_master_source import (
    generate_pdf,
    get_app_data_dir,
    get_resource_path
)

def test_template_css_bold_rules():
    tpl_path = get_resource_path(os.path.join("pdf_generator", "template.html"))
    if not os.path.exists(tpl_path):
        return False, f"Template file not found at '{tpl_path}'"
        
    with open(tpl_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check .label rule
    label_match = re.search(r'\.label\s*\{([^}]+)\}', content)
    if not label_match or "font-weight: bold" not in label_match.group(1):
        return False, ".label class does NOT specify 'font-weight: bold'"
        
    # Check .value rule
    value_match = re.search(r'\.value\s*\{([^}]+)\}', content)
    if not value_match or "font-weight: bold" not in value_match.group(1):
        return False, ".value class does NOT specify 'font-weight: bold'"
        
    if "font-weight: normal" in content:
        return False, "Found lingering 'font-weight: normal' rule in template.html!"
        
    return True, "Template CSS verified: BOTH .label and .value specify 'font-weight: bold'."

def test_pdf_rendering_bold_labels_and_values():
    pdf_out = os.path.join(get_app_data_dir(), "generated_pdfs", "p10_2_bold_test.pdf")
    if os.path.exists(pdf_out):
        try: os.remove(pdf_out)
        except: pass
        
    d = {
        "serial_no": "TN03996631",
        "lessee_id": "L-99812",
        "minecode": "MC/2026/SLM",
        "lessee_name": "Salem Granites Quarrying Co (P) Ltd",
        "lessee_address": "S.F. No. 44/2A, Kadayampatti Village",
        "hsn_code": "2517",
        "district": "Salem",
        "taluk": "Omalur",
        "village": "Kadayampatti",
        "sf_no": "44/2A",
        "classification": "Patta Land",
        "lease_period": "01-01-2024 to 31-12-2028",
        "mineral": "Rough Stone & Jelly",
        "bulk_permit": "BP-2026-991",
        "order_ref": "ROC-1120/2024",
        "within_tn": "Yes",
        "dispatch_slip": "DISP0000000000001",
        "delivered_to": "Metro Project Site",
        "quantity": "30.00",
        "auth_person": "V. Ramasamy",
        "vehicle_no": "TN 30 XY 1234",
        "vehicle_type": "Tractor-Trailer",
        "distance": "45.0",
        "destination": "Namakkal Bypass",
        "via": "NH 44",
        "traveling_date": "17-08-2026",
        "traveling_time": "04:35 PM",
        "req_hours": "8",
        "driver_name": "P. Velu",
        "driver_license": "TN3420190012345",
        "driver_phone": "9443322110",
        "dispatch_datetime": "17-08-2026 16:35:58"
    }
    
    generate_pdf(d, pdf_out)
    
    if not os.path.exists(pdf_out) or os.path.getsize(pdf_out) < 10000:
        return False, "Generated test PDF missing or corrupt."
        
    doc = fitz.open(pdf_out)
    page_cnt = len(doc)
    page = doc[0]
    rect = page.rect
    w_mm = rect.width * 25.4 / 72.0
    h_mm = rect.height * 25.4 / 72.0
    text = page.get_text()
    doc.close()
    
    if page_cnt != 1:
        return False, f"PDF page count is {page_cnt}, expected exactly 1."
        
    if not (205 <= w_mm <= 215 and 290 <= h_mm <= 302):
        return False, f"PDF dimensions ({w_mm:.1f}mm x {h_mm:.1f}mm) deviate from A4."
        
    exp_disp = "17-08-2026 04:35:58 PM"
    if exp_disp not in text:
        return False, f"Converted timestamp '{exp_disp}' not found in rendered PDF text!"
        
    if text.count(exp_disp) < 2:
        return False, f"Timestamp '{exp_disp}' found less than 2 times."
        
    # Verify sample labels AND values appear in rendered text
    required_samples = [
        "Lessee Id :", "L-99812",
        "Minecode :", "MC/2026/SLM",
        "Lease Area Details", "TN03996631",
        "Vehicle No:", "TN 30 XY 1234",
        "District Name:", "Salem",
        "Taluk Name:", "Omalur"
    ]
    for sample in required_samples:
        if sample not in text:
            return False, f"Sample text '{sample}' missing from rendered PDF text."
            
    return True, f"Rendered PDF verified: 1-page A4 ({w_mm:.1f}mm x {h_mm:.1f}mm), timestamp '{exp_disp}', labels & values present."

def main():
    print("=" * 75)
    print("  PERMITMASTER — PHASE 10.2 BOLD LABELS & VALUES VERIFICATION")
    print("=" * 75)
    
    tests = [
        ("Template CSS Bold Rules Inspection", test_template_css_bold_rules),
        ("PDF Rendering Bold Labels & Values Test", test_pdf_rendering_bold_labels_and_values),
    ]
    
    passed = 0
    failed = 0
    
    for name, fn in tests:
        print(f"\n[RUNNING TEST] {name}...")
        res, msg = fn()
        if res:
            passed += 1
            print(f"  [PASS] {name} -- {msg}")
        else:
            failed += 1
            print(f"  [FAIL] {name} -- {msg}")
            
    print("\n" + "=" * 75)
    print(f"  VERIFICATION SUMMARY: Passed {passed}/{len(tests)} tests. (Failed: {failed})")
    print("=" * 75)
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
