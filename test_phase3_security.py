import os
import sys
import tempfile
import sqlite3
import shutil

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from permit_master_source import (
    hash_password, verify_password, validate_permit_data,
    init_db, get_db, DB_PATH, LOG_FILE, APP_DATA_DIR, generate_pdf
)

def test_password_hashing():
    print("--- 1. TESTING PBKDF2 PASSWORD HASHING ---")
    raw_pass = "SecureAdmin2026!#"
    hash_str = hash_password(raw_pass)
    print(f"Generated Hash String: {hash_str[:40]}...")
    
    assert hash_str.startswith("pbkdf2:sha256:600000$"), "Hash string must contain algorithm and 600,000 iterations!"
    assert verify_password(raw_pass, hash_str) is True, "Password verification failed for valid password!"
    assert verify_password("WrongPassword123", hash_str) is False, "Password verification passed for invalid password!"
    assert verify_password("", hash_str) is False, "Empty password verification must fail!"
    assert verify_password(raw_pass, "invalid_hash_format") is False, "Malformed hash string must return False!"
    print("[OK] Password Hashing & PBKDF2 Verification Passed!")

def test_input_validation():
    print("\n--- 2. TESTING CENTRALIZED INPUT VALIDATION ---")
    valid_data = {
        "serial_no": "TEST-2026-001",
        "vehicle_no": "TN15AB1234",
        "quantity": "25.5",
        "distance": "120",
        "req_hours": "12",
        "traveling_date": "17-08-2026",
        "traveling_time": "06:45 PM",
        "driver_phone": "9876543210"
    }
    
    # Test valid permit data
    ok, msg = validate_permit_data(valid_data)
    assert ok is True, f"Valid permit data rejected: {msg}"
    
    # Test missing serial_no
    invalid_data = valid_data.copy()
    invalid_data["serial_no"] = ""
    ok, msg = validate_permit_data(invalid_data)
    assert ok is False and "Serial Number is required" in msg, f"Missing serial_no check failed: {msg}"
    
    # Test negative quantity
    invalid_data = valid_data.copy()
    invalid_data["quantity"] = "-10"
    ok, msg = validate_permit_data(invalid_data)
    assert ok is False and "cannot be a negative value" in msg, f"Negative quantity check failed: {msg}"
    
    # Test malformed date
    invalid_data = valid_data.copy()
    invalid_data["traveling_date"] = "2026/08/17"
    ok, msg = validate_permit_data(invalid_data)
    assert ok is False and "DD-MM-YYYY format" in msg, f"Malformed date check failed: {msg}"

    # Test malformed time
    invalid_data = valid_data.copy()
    invalid_data["traveling_time"] = "invalid_time"
    ok, msg = validate_permit_data(invalid_data)
    assert ok is False and "valid time string" in msg, f"Malformed time check failed: {msg}"

    print("[OK] Centralized Input Validation Passed!")

def test_database_and_user_seeding():
    print("\n--- 3. TESTING DATABASE USER SEEDING & LOCATION ---")
    assert os.path.exists(APP_DATA_DIR), "%LOCALAPPDATA%\\PermitMaster directory must exist!"
    assert DB_PATH.endswith("permits.db"), "Database must be stored at permits.db in user app data!"
    
    init_db()
    with get_db() as conn:
        users = conn.execute("SELECT * FROM users").fetchall()
        print(f"Current User Accounts in DB: {len(users)}")
    print("[OK] Database Initialization & User Table Passed!")

def test_pdf_generation_regression():
    print("\n--- 4. TESTING PDF GENERATION REGRESSION ---")
    test_record = {
        "id": 9999,
        "serial_no": "SEC-TEST-999",
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
        "bulk_permit": "BP-2026-99",
        "order_ref": "REF-9999",
        "within_tn": "Yes",
        "dispatch_slip": "DISP9999",
        "delivered_to": "Kallakurichi Site",
        "quantity": "25.00",
        "auth_person": "Gautham P M",
        "vehicle_no": "TN15XY9999",
        "vehicle_type": "Tippler Heavy",
        "distance": "45.0",
        "destination": "Ulundurpet Construction Site",
        "via": "NH45 Highway",
        "traveling_date": "17-08-2026",
        "traveling_time": "06:45 PM",
        "req_hours": "12",
        "driver_name": "R. Vignesh",
        "driver_license": "TN-15-2020-009988",
        "driver_phone": "9876543210",
        "signature_path": ""
    }
    
    output_pdf = os.path.join(tempfile.gettempdir(), "test_phase3_output.pdf")
    if os.path.exists(output_pdf):
        os.remove(output_pdf)

    try:
        generate_pdf(test_record, output_pdf)
        assert os.path.exists(output_pdf), "PDF file was not created!"
        assert os.path.getsize(output_pdf) > 1000, f"Generated PDF size is too small: {os.path.getsize(output_pdf)} bytes"
        print(f"[OK] PDF generated successfully ({os.path.getsize(output_pdf):,} bytes) at {output_pdf}")
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        raise e

if __name__ == "__main__":
    print("==================================================")
    print("  PERMIT MASTER — PHASE 3 SECURITY SUITE TESTS   ")
    print("==================================================")
    test_password_hashing()
    test_input_validation()
    test_database_and_user_seeding()
    test_pdf_generation_regression()
    print("\n==================================================")
    print("  ALL PHASE 3 AUTOMATED TESTS PASSED SUCCESSFULLY! ")
    print("==================================================")
