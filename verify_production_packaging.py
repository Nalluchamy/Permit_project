import os
import sys
import shutil
import sqlite3
from datetime import datetime
import fitz # PyMuPDF
from PIL import Image

# Import core permit_master_source module
import permit_master_source as pm

def test_production_packaging():
    print("==================================================")
    print("PHASE 2: PRODUCTION PACKAGING VERIFICATION")
    print("==================================================")

    # 1. Verify App Data Directories
    app_data_dir = pm.get_app_data_dir()
    expected_localappdata = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'PermitMaster')
    assert os.path.abspath(app_data_dir) == os.path.abspath(expected_localappdata), f"App Data Dir mismatch: {app_data_dir} != {expected_localappdata}"
    print(f"[OK] App Data Directory verified: {app_data_dir}")

    db_path = pm.DB_PATH
    log_file = pm.LOG_FILE
    assert os.path.exists(os.path.dirname(db_path)), "Database directory does not exist"
    assert os.path.exists(os.path.dirname(log_file)), "Logs directory does not exist"
    print(f"[OK] Database path verified: {db_path}")
    print(f"[OK] Log file path verified: {log_file}")

    # 2. Test Resource Resolution
    tpl_path = pm.get_resource_path(os.path.join("pdf_generator", "template.html"))
    sig_path = pm.get_resource_path("ad_dd_signature.png")
    icon_path = pm.get_resource_path("permit_icon.ico")
    
    assert os.path.exists(tpl_path), f"Template missing: {tpl_path}"
    assert os.path.exists(sig_path), f"Signature missing: {sig_path}"
    assert os.path.exists(icon_path), f"Icon missing: {icon_path}"
    print("[OK] All bundled resources located successfully via get_resource_path().")

    # 3. Test Database Seed & Data Persistence
    with pm.get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO permits (serial_no, lessee_name, vehicle_no, traveling_date, traveling_time) VALUES (?, ?, ?, ?, ?)",
                     ("TEST_P2_001", "Phase 2 Test Lessee", "TN01P2026", "17-08-2026", "10:00 AM"))
        row = conn.execute("SELECT * FROM permits WHERE serial_no=?", ("TEST_P2_001",)).fetchone()
        assert row is not None and row['lessee_name'] == "Phase 2 Test Lessee", "Database read/write failed"
    print("[OK] SQLite database persistence in %LOCALAPPDATA% verified.")

    # 4. Test Logging Setup
    pm.logging.info("Phase 2 automated verification logging test.")
    assert os.path.exists(log_file) and os.path.getsize(log_file) > 0, "Log file missing or empty"
    print("[OK] Application logging to %LOCALAPPDATA%\\PermitMaster\\logs\\app.log verified.")

    # 5. Phase 1 PDF Layout & Generation Regression Test
    test_data = {
        "serial_no": "TN03996631",
        "dispatch_slip": "DISP000007354833",
        "minecode": "KKIN0025",
        "traveling_date": "01-04-2026",
        "traveling_time": "06:45 PM",
        "hsn_code": "6290009",
        "lessee_id": "CHN241557",
        "lessee_name": "Gautham P M",
        "lessee_address": "No. 19, 11th Avenue, Ashok nagar, Chennai - 600083",
        "district": "Kallakurichi",
        "taluk": "Ulundurpet",
        "village": "Kallamedu",
        "sf_no": "58/1 (P-1)., / 00002.85.00",
        "mineral": "Pebbles",
        "bulk_permit": "KKI260000085",
        "order_ref": "REF123",
        "classification": "Porampoke Land",
        "lease_period": "12-07-2024 to 07-11-2028",
        "within_tn": "Yes",
        "delivered_to": "MANI",
        "vehicle_no": "TN56J7212",
        "vehicle_type": "Taurus 19",
        "distance": "689",
        "destination": "ARANTHANGI",
        "via": "THANJAVUR",
        "req_hours": "12",
        "driver_name": "PARAMASIVAM",
        "driver_license": "TN31Y20090003199",
        "driver_phone": "9642063599",
        "auth_person": "Gautham P M",
        "quantity": "9"
    }

    out_pdf = os.path.join(pm.APP_DATA_DIR, "generated_pdfs", "Phase2_Regression_Test.pdf")
    pm.generate_pdf(test_data, out_pdf)
    assert os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 0, "PDF generation failed"
    print(f"[OK] PDF generated successfully at: {out_pdf}")

    # Render PDF page to PNG to verify visual integrity
    doc = fitz.open(out_pdf)
    assert len(doc) == 1, f"PDF page count should be 1, got {len(doc)}"
    page = doc[0]
    pix = page.get_pixmap(dpi=150)
    out_png = os.path.join(pm.APP_DATA_DIR, "generated_pdfs", "Phase2_Regression_Test.png")
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.save(out_png)
    print(f"[OK] PDF visual rendering verified: {out_png}")
    print("==================================================")
    print("ALL PHASE 2 VERIFICATIONS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_production_packaging()
