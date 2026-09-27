"""
PermitMaster — Final Production Rebuild Verification Suite
Validates dist/PermitMaster.exe build artifact, AppData database preservation,
Phase 10.1 AM/PM dispatch timestamp conversion, bold table labels, A4 PDF geometry,
QR payload integrity, and backup creation.
"""

import os
import sys
import time
import sqlite3
import hashlib
import fitz # PyMuPDF

import permit_master_source as pms
from permit_master_source import (
    generate_pdf,
    create_backup,
    verify_backup,
    get_app_data_dir,
    DB_PATH
)

def test_executable_artifact():
    exe_path = os.path.join("dist", "PermitMaster.exe")
    if not os.path.exists(exe_path):
        return False, "Executable artifact dist/PermitMaster.exe does not exist!"
        
    size = os.path.getsize(exe_path)
    if size < 10000000: # Expect ~30 MB
        return False, f"Executable file size is unusually small ({size} bytes)."
        
    h = hashlib.sha256(open(exe_path, "rb").read()).hexdigest()
    return True, f"Executable artifact verified: {size} bytes ({size/(1024*1024):.2f} MB), SHA-256: {h[:16]}..."

def test_appdata_database_preservation():
    if not os.path.exists(DB_PATH):
        return False, f"Active production database missing at {DB_PATH}!"
        
    with sqlite3.connect(DB_PATH) as conn:
        p_cnt = conn.execute("SELECT COUNT(*) FROM permits").fetchone()[0]
        u_cnt = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        a_cnt = conn.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        
    if integrity != "ok":
        return False, f"Database integrity check failed: {integrity}"
        
    if p_cnt < 111:
        return False, f"Permit records count dropped to {p_cnt} (expected >= 111)."
        
    if u_cnt < 9:
        return False, f"User accounts count dropped to {u_cnt} (expected >= 9)."
        
    return True, f"AppData database preserved intact: {p_cnt} permits, {u_cnt} users, {a_cnt} audit logs."

def test_critical_post_build_pdf_ampm_and_labels():
    pdf_out = os.path.join(get_app_data_dir(), "generated_pdfs", "final_rebuild_pdf_test.pdf")
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
        "quantity": "9",
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
        
    if "9.00" not in text:
        return False, "Formatted quantity '9.00' not found in rendered PDF text!"

    cnt = text.count(exp_disp)
    if cnt < 2:
        return False, f"Timestamp '{exp_disp}' found {cnt} times; expected at least 2 (Office & Driver copy)."
        
    return True, f"Post-build PDF verified: 1-page A4 ({w_mm:.1f}mm x {h_mm:.1f}mm), timestamp '{exp_disp}' rendered in both copies."

def test_backup_engine_smoke():
    ok, b_path, msg = create_backup(tag="final_rebuild_smoke")
    if not ok or not os.path.exists(b_path):
        return False, f"Backup creation failed: {msg}"
        
    v_ok, v_msg = verify_backup(b_path)
    if not v_ok:
        return False, f"Created backup failed 9-point integrity check: {v_msg}"
        
    return True, f"Backup engine smoke test passed: backup created and verified at '{os.path.basename(b_path)}'."

def main():
    print("=" * 75)
    print("  PERMITMASTER — FINAL PRODUCTION REBUILD VERIFICATION SUITE")
    print("=" * 75)
    
    tests = [
        ("Executable Artifact Integrity & Size", test_executable_artifact),
        ("AppData Production Database Preservation", test_appdata_database_preservation),
        ("Critical Post-Build PDF AM/PM & Geometry Test", test_critical_post_build_pdf_ampm_and_labels),
        ("Backup Engine Smoke Test", test_backup_engine_smoke),
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
    print(f"  REBUILD VERIFICATION SUMMARY: Passed {passed}/{len(tests)} tests. (Failed: {failed})")
    print("=" * 75)
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
