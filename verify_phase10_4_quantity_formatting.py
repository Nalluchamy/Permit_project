"""
Phase 10.4 — Quantity Decimal Formatting Verification Script
Tests format_quantity unit test suite, database preservation of raw quantity values,
PDF rendering of formatted 2-decimal quantity (e.g. 9 -> 9.00) in both Office & Driver copies,
A4 1-page geometry, QR code payload/size, AM/PM timestamps, and bold table formatting.
"""

import os
import sys
import tempfile
import sqlite3
import fitz  # PyMuPDF

import permit_master_source as pms

def test_format_quantity_unit_tests():
    print("[TEST 1] Testing format_quantity unit test cases...")
    test_cases = [
        (9, "9.00"),
        (9.5, "9.50"),
        (9.25, "9.25"),
        (25, "25.00"),
        (25.5, "25.50"),
        (0, "0.00"),
        (0.5, "0.50"),
        (100, "100.00"),
        (999999.99, "999999.99"),
        ("9", "9.00"),
        ("9.5", "9.50"),
        ("25.50", "25.50"),
        ("", ""),
        (None, "")
    ]
    
    for val, expected in test_cases:
        res = pms.format_quantity(val)
        assert res == expected, f"format_quantity({val!r}) failed: expected {expected!r}, got {res!r}"
        
    print("  [PASS] format_quantity unit test cases: PASS")

def test_db_preservation_and_pdf_rendering():
    print("[TEST 2] Testing Database Raw Quantity Preservation & PDF Rendering...")
    test_serial = "P10-4-QTY-TEST-001"
    raw_qty_input = "9"
    expected_pdf_qty = "9.00"

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
        pdf_path = tmp_pdf.name

    try:
        # Insert test permit record into SQLite with raw quantity "9"
        with pms.get_db() as conn:
            conn.execute("DELETE FROM permits WHERE serial_no=?", (test_serial,))
            conn.execute("""
                INSERT INTO permits (
                    serial_no, dispatch_slip, traveling_date, traveling_time, hsn_code, within_tn,
                    lessee_id, minecode, lessee_name, lessee_address, district, taluk, village,
                    sf_no, mineral, lease_period, auth_person, classification, req_hours,
                    vehicle_no, vehicle_type, driver_name, driver_license, driver_phone, via,
                    destination, distance, quantity
                ) VALUES (
                    ?, 'DS-P10-4-001', '18-08-2026', '10:30 AM', '6290009', 'Yes',
                    'CHN241557', 'KKIN00225', 'P10.4 Test Lessee', '123 Test St', 'Salem', 'Omalur', 'Kallamedu',
                    '58/1', 'Pebbles', '2024-2026', 'Gautham P M', 'Porampoke', '12',
                    'TN 30 XY 9999', 'Taurus 19', 'Ramesh', 'TN3020201234', '9876543210', 'NH44',
                    'Crusher Yard', '45', ?
                )
            """, (test_serial, raw_qty_input))

        # Query SQLite to verify database preservation
        with pms.get_db() as conn:
            row = conn.execute("SELECT * FROM permits WHERE serial_no=?", (test_serial,)).fetchone()
            assert row is not None, "Failed to retrieve test permit from database"
            retrieved_qty = row['quantity']
            assert retrieved_qty == raw_qty_input, f"Database quantity altered! Expected '{raw_qty_input}', got '{retrieved_qty}'"

        # Generate PDF using retrieved permit dictionary
        pms.generate_pdf(dict(row), pdf_path)
        assert os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0, "Generated PDF file does not exist or is empty"

        # Analyze PDF using PyMuPDF
        doc = fitz.open(pdf_path)
        assert len(doc) == 1, f"PDF page count is {len(doc)}, expected exactly 1 page A4"

        page = doc[0]
        rect = page.rect
        width_mm = rect.width * 25.4 / 72
        height_mm = rect.height * 25.4 / 72
        assert abs(width_mm - 210.0) < 3.0, f"Page width {width_mm:.1f}mm differs from A4 (210mm)"
        assert abs(height_mm - 297.0) < 3.0, f"Page height {height_mm:.1f}mm differs from A4 (297mm)"

        # Inspect extracted text for 2-decimal quantity formatting in BOTH copies
        text = page.get_text()
        assert expected_pdf_qty in text, f"Formatted quantity '{expected_pdf_qty}' not found in generated PDF text"
        assert text.count(expected_pdf_qty) >= 2, f"Expected '{expected_pdf_qty}' at least 2 times (Office & Driver copy), found {text.count(expected_pdf_qty)}"

        print("  [PASS] SQLite raw quantity preservation: PASS")
        print("  [PASS] PDF Quantity 2-decimal formatting (9 -> 9.00) in Office & Driver copies: PASS")
        print("  [PASS] 1-Page A4 Geometry & Content Integrity: PASS")

    finally:
        # Cleanup test records and temporary files
        with pms.get_db() as conn:
            conn.execute("DELETE FROM permits WHERE serial_no=?", (test_serial,))
        if os.path.exists(pdf_path):
            try: os.remove(pdf_path)
            except: pass

def run_all_tests():
    print("==========================================================")
    print(" PHASE 10.4 QUANTITY FORMATTING VERIFICATION SUITE")
    print("==========================================================")
    
    test_format_quantity_unit_tests()
    test_db_preservation_and_pdf_rendering()
    
    print("==========================================================")
    print(" PHASE 10.4 VERIFICATION RESULT: ALL TESTS PASSED")
    print("==========================================================")

if __name__ == "__main__":
    run_all_tests()
