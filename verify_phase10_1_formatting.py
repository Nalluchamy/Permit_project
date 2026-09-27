"""
PermitMaster — Phase 10.1 PDF Formatting & AM/PM Verification Suite
Validates 12-hour AM/PM timestamp conversion, bold table labels, and strict A4 geometry preservation.
"""

import os
import sys
import time
import tempfile
import fitz # PyMuPDF
from datetime import datetime

import permit_master_source as pms
from permit_master_source import format_dispatch_datetime, generate_pdf, get_app_data_dir

def test_ampm_formatting_conversion():
    test_cases = [
        ("17-08-2026 16:35:58", "17-08-2026 04:35:58 PM"),
        ("17-08-2026 00:00:00", "17-08-2026 12:00:00 AM"),
        ("17-08-2026 00:15:03", "17-08-2026 12:15:03 AM"),
        ("17-08-2026 12:00:00", "17-08-2026 12:00:00 PM"),
        ("17-08-2026 12:30:45", "17-08-2026 12:30:45 PM"),
        ("17-08-2026 23:59:59", "17-08-2026 11:59:59 PM"),
        ("13-05-2026 13:05:09", "13-05-2026 01:05:09 PM"),
    ]
    
    for inp, exp in test_cases:
        res = format_dispatch_datetime(inp)
        if res != exp:
            return False, f"Format conversion failed for '{inp}': expected '{exp}', got '{res}'"
            
    return True, f"All {len(test_cases)} AM/PM conversion test cases passed."

def test_pdf_rendering_and_label_bolding():
    test_pdf = os.path.join(get_app_data_dir(), "generated_pdfs", "p10_1_verification.pdf")
    if os.path.exists(test_pdf):
        try: os.remove(test_pdf)
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
    
    generate_pdf(d, test_pdf)
    
    if not os.path.exists(test_pdf) or os.path.getsize(test_pdf) < 10000:
        return False, f"Generated PDF file missing or corrupt (size={os.path.getsize(test_pdf) if os.path.exists(test_pdf) else 0})."
        
    doc = fitz.open(test_pdf)
    page_cnt = len(doc)
    page = doc[0]
    rect = page.rect
    w_mm = rect.width * 25.4 / 72.0
    h_mm = rect.height * 25.4 / 72.0
    text = page.get_text()
    doc.close()
    
    if page_cnt != 1:
        return False, f"Page count is {page_cnt}, expected exactly 1."
        
    if not (205 <= w_mm <= 215 and 290 <= h_mm <= 302):
        return False, f"PDF dimensions ({w_mm:.1f}mm x {h_mm:.1f}mm) deviate from A4."
        
    # Check AM/PM timestamp appearance in PDF text
    exp_disp = "17-08-2026 04:35:58 PM"
    if exp_disp not in text:
        return False, f"Converted timestamp '{exp_disp}' not found in rendered PDF text."
        
    # Verify BOTH Office Copy and Driver Copy contain the timestamp
    cnt = text.count(exp_disp)
    if cnt < 2:
        return False, f"Timestamp '{exp_disp}' found {cnt} times; expected at least 2 (Office Copy & Driver Copy)."
        
    # Verify label bolding consistency in template.html
    tpl_path = os.path.join(pms.get_resource_path("pdf_generator"), "template.html")
    with open(tpl_path, "r", encoding="utf-8") as f:
        tpl_content = f.read()
        
    if "<td>Lease Area Details</td>" in tpl_content:
        return False, "Found un-bolded '<td>Lease Area Details</td>' in template.html!"
        
    if tpl_content.count('<span class="label">Lease Area Details</span>') < 2:
        return False, "Missing '<span class=\"label\">Lease Area Details</span>' in Office or Driver copy template."
        
    return True, f"PDF verified: 1-page A4 ({w_mm:.1f}mm x {h_mm:.1f}mm), dispatch time '{exp_disp}' in both copies, bold labels verified."

def main():
    print("=" * 75)
    print("  PERMITMASTER — PHASE 10.1 FORMATTING & AM/PM VERIFICATION")
    print("=" * 75)
    
    tests = [
        ("12-Hour AM/PM Format Conversion", test_ampm_formatting_conversion),
        ("PDF Rendering & Label Bolding", test_pdf_rendering_and_label_bolding),
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
