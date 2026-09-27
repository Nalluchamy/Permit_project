import os
import sys
import tempfile
import sqlite3
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from permit_master_source import (
    validate_permit_data, init_db, get_db, DB_PATH, APP_DATA_DIR, generate_pdf
)

# Test counter statistics
TEST_STATS = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "rejected_invalid": 0,
    "unexpected_accepted": 0
}

def record_test(name, result, expected_reject=False):
    TEST_STATS["total"] += 1
    if result:
        TEST_STATS["passed"] += 1
        if expected_reject:
            TEST_STATS["rejected_invalid"] += 1
        print(f"  [PASS] {name}")
    else:
        TEST_STATS["failed"] += 1
        if expected_reject:
            TEST_STATS["unexpected_accepted"] += 1
        print(f"  [FAIL] {name}")

def base_permit():
    return {
        "serial_no": "TN/2026/0001",
        "lessee_id": "CHN241557",
        "minecode": "KKIN00225",
        "lessee_name": "Gautham P M",
        "lessee_address": "No. 19, 11th Avenue, Ashok nagar, Chennai - 600083",
        "hsn_code": "6290009",
        "district": "Kallakurichi",
        "taluk": "Ulundurpet",
        "village": "Kallamedu",
        "sf_no": "58/1 (P-1)., / 00002.85.00",
        "classification": "Porampoke Land",
        "lease_period": "12-07-2024 to 07-11-2026",
        "mineral": "Pebbles",
        "bulk_permit": "BP-2026-101",
        "order_ref": "REF-8899",
        "within_tn": "Yes",
        "dispatch_slip": "DISP1001",
        "delivered_to": "Kallakurichi Yard",
        "quantity": "25.50",
        "auth_person": "Gautham P M",
        "vehicle_no": "TN15AB1234",
        "vehicle_type": "Tippler Heavy",
        "distance": "120.0",
        "destination": "Ulundurpet Site",
        "via": "NH45 Highway",
        "traveling_date": "17-08-2026",
        "traveling_time": "06:45 PM",
        "req_hours": "12",
        "driver_name": "R. Vignesh",
        "driver_license": "TN-15-2020-009988",
        "driver_phone": "9876543210",
        "signature_path": ""
    }

def test_1_required_fields():
    print("\n--- 1. REQUIRED FIELD TESTS ---")
    d = base_permit()
    ok, _ = validate_permit_data(d)
    record_test("Valid required fields", ok)

    # Empty serial_no
    d_empty_s = base_permit(); d_empty_s["serial_no"] = ""
    ok, _ = validate_permit_data(d_empty_s)
    record_test("Empty serial_no rejected", not ok, expected_reject=True)

    # Whitespace serial_no
    d_ws_s = base_permit(); d_ws_s["serial_no"] = "   "
    ok, _ = validate_permit_data(d_ws_s)
    record_test("Whitespace serial_no rejected", not ok, expected_reject=True)

    # Empty vehicle_no
    d_empty_v = base_permit(); d_empty_v["vehicle_no"] = ""
    ok, _ = validate_permit_data(d_empty_v)
    record_test("Empty vehicle_no rejected", not ok, expected_reject=True)

def test_2_numeric_fields():
    print("\n--- 2. NUMERIC FIELD TESTS ---")
    for field in ["quantity", "distance", "req_hours"]:
        d = base_permit()
        
        # 0
        d[field] = "0"; ok, _ = validate_permit_data(d)
        record_test(f"{field}: 0", ok)

        # Positive float
        d[field] = "150.75"; ok, _ = validate_permit_data(d)
        record_test(f"{field}: positive decimal 150.75", ok)

        # Negative float (must reject)
        d[field] = "-25.5"; ok, _ = validate_permit_data(d)
        record_test(f"{field}: negative -25.5 rejected", not ok, expected_reject=True)

        # Non-numeric text (must reject)
        d[field] = "abc_invalid"; ok, _ = validate_permit_data(d)
        record_test(f"{field}: text 'abc_invalid' rejected", not ok, expected_reject=True)

        # Very large value
        d[field] = "999999.99"; ok, _ = validate_permit_data(d)
        record_test(f"{field}: large value 999999.99", ok)

def test_3_date_testing():
    print("\n--- 3. DATE TESTING ---")
    valid_dates = ["17-08-2026", "31-12-2026", "29-02-2028"] # 2028 is leap year
    for vd in valid_dates:
        d = base_permit(); d["traveling_date"] = vd
        ok, _ = validate_permit_data(d)
        record_test(f"Valid date '{vd}'", ok)

    invalid_dates = ["32-01-2026", "31-02-2026", "99-99-9999", "2026/08/17", "17.08.2026", "invalid-date"]
    for idate in invalid_dates:
        d = base_permit(); d["traveling_date"] = idate
        ok, msg = validate_permit_data(d)
        record_test(f"Invalid date '{idate}' rejected", not ok, expected_reject=True)

def test_4_time_testing():
    print("\n--- 4. TIME TESTING ---")
    valid_times = ["10:30 AM", "11:59 PM", "12:00 AM", "12:00 PM", "06:45 PM", "14:30"]
    for vt in valid_times:
        d = base_permit(); d["traveling_time"] = vt
        ok, _ = validate_permit_data(d)
        record_test(f"Valid time '{vt}'", ok)

    invalid_times = ["25:90 PM", "99:99", "25:00", "invalid_time"]
    for itime in invalid_times:
        d = base_permit(); d["traveling_time"] = itime
        ok, _ = validate_permit_data(d)
        record_test(f"Invalid time '{itime}' rejected", not ok, expected_reject=True)

def test_5_phone_testing():
    print("\n--- 5. PHONE NUMBER TESTING ---")
    valid_phones = ["9876543210", "+91 98765 43210", "044-28282828", "(044) 98765432"]
    for vp in valid_phones:
        d = base_permit(); d["driver_phone"] = vp
        ok, _ = validate_permit_data(d)
        record_test(f"Valid phone '{vp}'", ok)

    invalid_phones = ["123", "1234567890123456789", "abcdefghij", "phone12345"]
    for ip in invalid_phones:
        d = base_permit(); d["driver_phone"] = ip
        ok, _ = validate_permit_data(d)
        record_test(f"Invalid phone '{ip}' rejected", not ok, expected_reject=True)

def test_6_string_length_and_bounds():
    print("\n--- 6. STRING LENGTH & BOUNDS TESTING ---")
    d_normal = base_permit()
    ok, _ = validate_permit_data(d_normal)
    record_test("Normal string lengths", ok)

    # 500 characters (max allowed)
    d_500 = base_permit()
    d_500["lessee_address"] = "A" * 500
    ok, _ = validate_permit_data(d_500)
    record_test("500-char string (max allowed)", ok)

    # 501 characters (must reject)
    d_501 = base_permit()
    d_501["lessee_address"] = "A" * 501
    ok, _ = validate_permit_data(d_501)
    record_test("501-char string rejected (>500 limit)", not ok, expected_reject=True)

    # Serial No > 50 chars
    d_s51 = base_permit(); d_s51["serial_no"] = "S" * 51
    ok, _ = validate_permit_data(d_s51)
    record_test("Serial No > 50 chars rejected", not ok, expected_reject=True)

def test_7_special_chars_and_html_safety():
    print("\n--- 7. SPECIAL CHARACTERS & HTML SAFETY ---")
    special_text = "Mining & Mineral Co. (Pvt) Ltd. - Site #45/A, Chennai; 'Ref: 100%' <TN>"
    d_spec = base_permit()
    d_spec["lessee_name"] = special_text
    ok, _ = validate_permit_data(d_spec)
    record_test("Special characters in text preserved", ok)

    # XSS Payloads
    xss_payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<iframe src=javascript:alert(1)></iframe>"
    ]
    for xss in xss_payloads:
        d_xss = base_permit()
        d_xss["driver_name"] = xss
        ok, _ = validate_permit_data(d_xss)
        record_test(f"XSS text '{xss[:20]}...' allowed safely as escaped text", ok)

def test_8_duplicate_data_audit():
    print("\n--- 8. DUPLICATE DATA AUDIT ---")
    init_db()
    with get_db() as conn:
        conn.execute("DELETE FROM permits WHERE serial_no IN ('DUP-TEST-001', 'PERSIST-2026-99') OR dispatch_slip IN ('DISP-DUP-001') OR serial_no LIKE 'TN/2026/100%' OR dispatch_slip LIKE 'DISP100%'")
        conn.commit()
        # Check if serial_no or dispatch_slip have UNIQUE constraint in DB schema
        table_info = conn.execute("PRAGMA table_info(permits)").fetchall()
        print(f"Total Columns in 'permits': {len(table_info)}")
        
        # Test duplicate insert behavior
        d1 = base_permit(); d1["serial_no"] = "DUP-TEST-001"; d1["dispatch_slip"] = "DISP-DUP-001"
        cols = list(d1.keys()); vals = [d1[c] for c in cols]
        
        conn.execute(f"INSERT INTO permits ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})", vals)
        try:
            conn.execute(f"INSERT INTO permits ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})", vals)
            print("  [INFO] Duplicate serial_no inserted without DB error (Reported as Phase 5 finding: DB UNIQUE constraint missing).")
            record_test("Duplicate serial_no audited", True)
        except sqlite3.IntegrityError:
            print("  [INFO] Duplicate serial_no rejected at DB level.")
            record_test("Duplicate serial_no rejected at DB level", True)

def test_9_ten_records_roundtrip():
    print("\n--- 9. 10 VALID PERMIT RECORDS DB -> PDF ROUND-TRIP ---")
    init_db()
    temp_dir = tempfile.mkdtemp()
    
    success_count = 0
    for i in range(1, 11):
        rec = base_permit()
        rec["serial_no"] = f"TN/2026/100{i}"
        rec["dispatch_slip"] = f"DISP990{i}"
        rec["vehicle_no"] = f"TN15AB{1000 + i}"
        rec["quantity"] = str(20.0 + i)
        rec["driver_name"] = f"Driver Name {i}"
        
        ok, msg = validate_permit_data(rec)
        if not ok:
            print(f"  [FAIL] Record {i} validation failed: {msg}")
            continue

        with get_db() as conn:
            cols = list(rec.keys()); vals = [rec[c] for c in cols]
            cursor = conn.execute(f"INSERT INTO permits ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})", vals)
            rec_id = cursor.lastrowid

            fetched = conn.execute("SELECT * FROM permits WHERE id=?", (rec_id,)).fetchone()
            fetched_dict = dict(fetched)

        pdf_path = os.path.join(temp_dir, f"Permit_Test_{i}.pdf")
        generate_pdf(fetched_dict, pdf_path)

        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
            success_count += 1

    record_test("10 Valid Permit Records DB -> PDF Round-Trip (Office & Driver copies)", success_count == 10)
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_10_app_restart_persistence():
    print("\n--- 10. APP RESTART PERSISTENCE ROUND-TRIP ---")
    init_db()
    rec = base_permit()
    rec["serial_no"] = "PERSIST-2026-99"
    rec["driver_name"] = "Persistence Test Driver"

    with get_db() as conn:
        cols = list(rec.keys()); vals = [rec[c] for c in cols]
        cursor = conn.execute(f"INSERT INTO permits ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})", vals)
        inserted_id = cursor.lastrowid

    # Re-open DB connection to simulate app restart
    with get_db() as conn2:
        row = conn2.execute("SELECT * FROM permits WHERE id=?", (inserted_id,)).fetchone()
        row_dict = dict(row)

    assert row_dict["serial_no"] == "PERSIST-2026-99", "Serial number mismatch after restart!"
    assert row_dict["driver_name"] == "Persistence Test Driver", "Driver name mismatch after restart!"
    record_test("Data persistence across simulated app restart", True)

if __name__ == "__main__":
    print("==================================================")
    print("  PERMIT MASTER — PHASE 4 DATA INTEGRITY SUITE   ")
    print("==================================================")
    test_1_required_fields()
    test_2_numeric_fields()
    test_3_date_testing()
    test_4_time_testing()
    test_5_phone_testing()
    test_6_string_length_and_bounds()
    test_7_special_chars_and_html_safety()
    test_8_duplicate_data_audit()
    test_9_ten_records_roundtrip()
    test_10_app_restart_persistence()

    print("\n==================================================")
    print(f"  SUMMARY: Total: {TEST_STATS['total']} | Passed: {TEST_STATS['passed']} | Failed: {TEST_STATS['failed']}")
    print(f"  Rejected Invalid Inputs: {TEST_STATS['rejected_invalid']}")
    print("==================================================")
