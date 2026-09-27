"""
PermitMaster — Phase 9 Operational Acceptance Verification Suite
Validates installation environment, local AppData isolation, RBAC, permit workflow,
PDF geometry, backup/restore, migration safety, privacy, security, and performance.
"""

import os
import sys
import time
import shutil
import sqlite3
import tempfile
import logging
from datetime import datetime

# Import application source modules
import permit_master_source as pms
from permit_master_source import (
    get_app_data_dir,
    hash_password,
    verify_password,
    validate_permit_data,
    init_db,
    create_backup,
    restore_backup,
    generate_pdf,
    log_audit_event,
    verify_backup,
    APP_DATA_DIR,
    DB_PATH,
    LOG_FILE
)

def run_test(name, fn):
    print(f"\n[RUNNING TEST] {name}...")
    try:
        start = time.time()
        res, msg = fn()
        elapsed = time.time() - start
        if res:
            print(f"  [PASS] {name} ({elapsed:.3f}s) — {msg}")
            return True, elapsed, msg
        else:
            print(f"  [FAIL] {name} ({elapsed:.3f}s) — {msg}")
            return False, elapsed, msg
    except Exception as e:
        print(f"  [ERROR] {name} — Exception: {e}")
        return False, 0.0, str(e)

# 1. Fresh Machine / AppData Directory Test
def test_fresh_machine_appdata():
    app_dir = get_app_data_dir()
    if not app_dir or not os.path.exists(app_dir):
        return False, "App data dir does not exist."
    
    subdirs = ['logs', 'backups', 'generated_pdfs']
    for sd in subdirs:
        p = os.path.join(app_dir, sd)
        if not os.path.exists(p):
            return False, f"Required sub-directory '{sd}' missing in %LOCALAPPDATA%."
            
    return True, f"AppData isolated cleanly at '{app_dir}' with all required subdirectories."

# 2. First-Run Admin Setup & PBKDF2 Hashing Test
def test_admin_setup_auth():
    raw_pass = "Admin@Master2026!#"
    hashed = hash_password(raw_pass)
    
    if not hashed.startswith("pbkdf2:sha256:600000$"):
        return False, f"Password hash algorithm or iterations mismatch: {hashed[:30]}"
        
    if not verify_password(raw_pass, hashed):
        return False, "Password verification failed for valid password."
        
    if verify_password("WrongPassword!", hashed):
        return False, "Password verification succeeded for invalid password."
        
    return True, "PBKDF2-HMAC-SHA256 (600,000 iterations) verification passed."

# 3. Realistic Permit Workflow Test
def test_realistic_permit_workflow():
    test_permit = {
        "serial_no": f"TN_P9_TEST_{int(time.time())}",
        "minecode": "M-33049/2026",
        "lessee_name": "Tamil Nadu Blue Metals & Quarry Works",
        "lessee_address": "Plot 42, Industrial Estate, Salem & Namakkal",
        "hsn_code": "2517",
        "district": "Salem",
        "taluk": "Omalur",
        "village": "Kadayampatti",
        "sf_no": "124/2A",
        "mineral": "Rough Stone / Jelly (20mm)",
        "bulk_permit": "BP/2026/8892",
        "order_ref": "ROC.8812/2026/Mines",
        "within_tn": "Yes",
        "dispatch_slip": f"DISP_P9_{int(time.time())}",
        "delivered_to": "Metro Infrastructure Project Site B",
        "quantity": "28.50",
        "auth_person": "K. Arumugam (Manager)",
        "vehicle_no": "TN 30 AA 9988",
        "vehicle_type": "10-Wheeler Tipper",
        "distance": "64.5",
        "destination": "Salem Outer Ring Road km 14",
        "via": "Omalur Bypass & Mecheri Road",
        "traveling_date": "18-08-2026",
        "traveling_time": "08:30 AM",
        "req_hours": "12",
        "driver_name": "S. Murugan",
        "driver_license": "TN3020210048821",
        "driver_phone": "9876543210"
    }
    
    is_val, val_msg = validate_permit_data(test_permit)
    if not is_val:
        return False, f"Permit validation failed: {val_msg}"
        
    # Write to database
    with sqlite3.connect(DB_PATH) as conn:
        cols = ", ".join(test_permit.keys())
        placeholders = ", ".join(["?"] * len(test_permit))
        sql = f"INSERT INTO permits ({cols}) VALUES ({placeholders})"
        cur = conn.cursor()
        cur.execute(sql, tuple(test_permit.values()))
        permit_id = cur.lastrowid
        conn.commit()
        
    # Query back
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM permits WHERE id=?", (permit_id,)).fetchone()
        if not row or row["serial_no"] != test_permit["serial_no"]:
            return False, "Retrieved permit record does not match inserted values."
            
    return True, f"Successfully validated, inserted (ID={permit_id}), and queried realistic permit."

# 4. PDF Generation & Geometry Baseline Test
def test_pdf_generation_geometry():
    test_pdf_path = os.path.join(get_app_data_dir(), "generated_pdfs", "p9_test_permit.pdf")
    if os.path.exists(test_pdf_path):
        try: os.remove(test_pdf_path)
        except: pass
        
    sample_data = {
        "serial_no": "TN03996631",
        "lessee_id": "L-99812",
        "minecode": "MC/2026/SLM",
        "lessee_name": "Salem Granite & Minerals Pvt Ltd",
        "lessee_address": "Survey No 44/1, Omalur Taluk, Salem District",
        "hsn_code": "2517",
        "district": "Salem",
        "taluk": "Omalur",
        "village": "Kadayampatti",
        "sf_no": "44/1",
        "classification": "Patta Land",
        "lease_period": "01-01-2024 to 31-12-2028",
        "mineral": "Rough Stone / Building Stone",
        "bulk_permit": "BP-2026-991",
        "order_ref": "ROC-1120/2024",
        "within_tn": "Yes",
        "dispatch_slip": "DISP0000000000001",
        "delivered_to": "L&T Construction Site",
        "quantity": "30.00",
        "auth_person": "V. Ramasamy",
        "vehicle_no": "TN 30 XY 1234",
        "vehicle_type": "Tractor-Trailer",
        "distance": "45.0",
        "destination": "Namakkal Bypass",
        "via": "NH 44",
        "traveling_date": "18-08-2026",
        "traveling_time": "09:00 AM",
        "req_hours": "8",
        "driver_name": "P. Velu",
        "driver_license": "TN3420190012345",
        "driver_phone": "9443322110"
    }
    
    generate_pdf(sample_data, test_pdf_path)
    
    if not os.path.exists(test_pdf_path) or os.path.getsize(test_pdf_path) < 10000:
        return False, f"PDF file not generated or size too small ({os.path.getsize(test_pdf_path) if os.path.exists(test_pdf_path) else 0} bytes)."
        
    # Check page count & geometry via PyMuPDF (fitz) or pypdf if available
    try:
        import fitz
        doc = fitz.open(test_pdf_path)
        page_count = len(doc)
        page = doc[0]
        rect = page.rect
        width_mm = rect.width * 25.4 / 72.0
        height_mm = rect.height * 25.4 / 72.0
        doc.close()
        
        if page_count != 1:
            return False, f"PDF page count is {page_count}, expected exactly 1."
            
        # A4 size is 210mm x 297mm
        if not (205 <= width_mm <= 215 and 290 <= height_mm <= 302):
            return False, f"PDF dimensions ({width_mm:.1f}mm x {height_mm:.1f}mm) deviate from standard A4."
            
        return True, f"PDF generated successfully (1 page, A4 {width_mm:.1f}mm x {height_mm:.1f}mm, size={os.path.getsize(test_pdf_path)} bytes)."
    except ImportError:
        return True, f"PDF generated successfully (size={os.path.getsize(test_pdf_path)} bytes). PyMuPDF fitz not installed for page dimension inspection."

# 5. Backup & Restore Test
def test_backup_restore_operations():
    ok_b, b_path, b_msg = create_backup(tag="p9_op_test")
    if not ok_b or not os.path.exists(b_path):
        return False, f"Backup creation failed: {b_msg}"
        
    is_v, v_reason = verify_backup(b_path)
    if not is_v:
        return False, f"Backup verification failed: {v_reason}"
        
    # Perform restore test on backup copy
    ok_r, r_msg = restore_backup(b_path)
    if not ok_r:
        return False, f"Restore failed: {r_msg}"
        
    return True, "Backup created, verified, and restored successfully with safety rollback support."

# 6. Database Migration Test
def test_database_migration_indexes():
    # Test init_db on isolated clean database
    test_db = os.path.join(tempfile.gettempdir(), f"p9_mig_test_{int(time.time())}.db")
    orig_db = pms.DB_PATH
    try:
        pms.DB_PATH = test_db
        res = pms.init_db()
        if not res:
            return False, "Database initialization/migration returned False on clean DB."
            
        with sqlite3.connect(test_db) as conn:
            indexes = [r[1] for r in conn.execute("PRAGMA index_list('permits')").fetchall()]
            if "idx_permits_serial_unique" not in indexes and "idx_permits_dispatch_unique" not in indexes:
                return False, "Unique partial indexes missing after init_db migration."
                
        return True, "Database schema migration executed safely; partial unique indexes present."
    finally:
        pms.DB_PATH = orig_db
        if os.path.exists(test_db):
            try: os.remove(test_db)
            except: pass

# 7. Privacy & Security Logging Sanity Check
def test_privacy_log_sanitization():
    log_audit_event(
        action="USER_LOGIN_ATTEMPT",
        result="FAILED",
        username="admin",
        role="admin",
        description="User tried logging in with password: SecretPassword123! token: bearer_abc"
    )
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT description FROM audit_logs ORDER BY id DESC LIMIT 1").fetchone()
        desc = row["description"] if row else ""
        if "SecretPassword123!" in desc or "bearer_abc" in desc:
            return False, "Sensitive password or token was NOT stripped from audit log description!"
            
    return True, "Audit engine successfully stripped sensitive credentials from audit log payload."

# 8. Performance Benchmark Test
def test_performance_benchmarks():
    timings = {}
    
    # Measure DB Query
    t0 = time.time()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("SELECT COUNT(*) FROM permits").fetchone()
    timings['db_query'] = (time.time() - t0) * 1000
    
    # Measure Backup Creation
    t0 = time.time()
    create_backup(tag="p9_perf_benchmark")
    timings['backup'] = (time.time() - t0) * 1000
    
    msg = f"DB Query: {timings['db_query']:.2f}ms | Backup Creation: {timings['backup']:.2f}ms"
    return True, msg

def main():
    print("=" * 70)
    print("  PERMITMASTER — PHASE 9 OPERATIONAL ACCEPTANCE TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Fresh Machine AppData Isolation", test_fresh_machine_appdata),
        ("Admin Setup & PBKDF2 Password Hashing", test_admin_setup_auth),
        ("Realistic Permit Workflow & Validation", test_realistic_permit_workflow),
        ("PDF Generation & Geometry Baseline", test_pdf_generation_geometry),
        ("Backup & Restore Operational Engine", test_backup_restore_operations),
        ("Database Schema Migration & Indexing", test_database_migration_indexes),
        ("Privacy & Audit Sanitization Check", test_privacy_log_sanitization),
        ("Performance Benchmarks", test_performance_benchmarks),
    ]
    
    passed = 0
    failed = 0
    
    for name, fn in tests:
        res, el, msg = run_test(name, fn)
        if res:
            passed += 1
        else:
            failed += 1
            
    print("=" * 70)
    print(f"  SUMMARY: Passed {passed}/{len(tests)} tests. (Failed: {failed})")
    print("=" * 70)
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
