import os
import sys
import unittest
import fitz # PyMuPDF
import permit_master_source as pm

class TestDeliveredToColspan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template_path = pm.get_resource_path(os.path.join("pdf_generator", "template.html"))
        with open(cls.template_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

        cls.test_data = {
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
        cls.pdf_path = os.path.join(pm.APP_DATA_DIR, "generated_pdfs", "Delivered_To_Colspan_Test.pdf")
        pm.generate_pdf(cls.test_data, cls.pdf_path)

    def test_01_template_html_structure(self):
        """1. Verify HTML template contains colspan='3' for Delivered To in both Office & Driver copy tables."""
        print("\n--- 1. HTML TEMPLATE COLSPAN VERIFICATION ---")
        expected_fragment = '<td class="value" colspan="3">{{delivered_to}}</td>'
        count = self.html_content.count(expected_fragment)
        self.assertEqual(count, 2, f"Expected 2 occurrences of '{expected_fragment}' (1 for Office Copy, 1 for Driver Copy), found {count}")
        print(f"  [PASS] HTML structure verified: Delivered To uses colspan='3' in both tables ({count}/2 found)")

    def test_02_delivered_to_label_first_column(self):
        """2. Verify Delivered To label remains in the first column."""
        print("\n--- 2. DELIVERED TO LABEL COLUMN VERIFICATION ---")
        expected_label = '<td class="label">Delivered To:</td>'
        count = self.html_content.count(expected_label)
        self.assertEqual(count, 2, "Delivered To label must exist in column 1 of both tables")
        print("  [PASS] Delivered To label verified in column 1 for both copies")

    def test_03_no_empty_td_dividers(self):
        """3. Verify no extra empty <td> cells remain in the Delivered To row."""
        print("\n--- 3. NO EXTRA DIVIDERS VERIFICATION ---")
        # Ensure old empty <td></td> after delivered_to is gone
        lines = self.html_content.splitlines()
        for i, line in enumerate(lines):
            if "Delivered To:" in line:
                # Check next 3 lines
                block = "\n".join(lines[i:i+4])
                self.assertNotIn("<td></td>", block, "Delivered To row must not contain empty <td></td> divider cells")
        print("  [PASS] Extra vertical dividers removed from Delivered To row")

    def test_04_pdf_page_count_and_a4_geometry(self):
        """4. Verify PDF output remains exactly 1 A4 page."""
        print("\n--- 4. SINGLE PAGE A4 GEOMETRY VERIFICATION ---")
        doc = fitz.open(self.pdf_path)
        self.assertEqual(len(doc), 1, f"PDF page count must be exactly 1, got {len(doc)}")
        page = doc[0]
        rect = page.rect
        # A4 size in points: 595.276 x 841.89
        self.assertAlmostEqual(rect.width, 595.276, delta=1.0, msg="Page width must match A4 (210mm / 595.27pt)")
        self.assertAlmostEqual(rect.height, 841.89, delta=1.0, msg="Page height must match A4 (297mm / 841.89pt)")
        doc.close()
        print("  [PASS] PDF remains exactly 1 A4 page (595.28 x 841.89 pt)")

    def test_05_qr_and_signature_positions(self):
        """5. Verify QR code and Signature positions/styling remain unchanged."""
        print("\n--- 5. QR CODE & SIGNATURE GEOMETRY VERIFICATION ---")
        self.assertIn('.qr-code {\n            width: 18.5mm;\n            height: 18.5mm;', self.html_content)
        self.assertIn('.sig-img {\n            max-height: 8.5mm;\n            max-width: 38mm;', self.html_content)
        print("  [PASS] QR code (18.5mm) and Signature (8.5mm max height) specifications intact")

    def test_06_text_content_and_formatting(self):
        """6. Verify text extraction from generated PDF includes Delivered To value 'MANI'."""
        print("\n--- 6. PDF TEXT CONTENT VERIFICATION ---")
        doc = fitz.open(self.pdf_path)
        text = doc[0].get_text()
        doc.close()
        self.assertIn("Delivered To:", text)
        self.assertIn("MANI", text)
        print("  [PASS] Delivered To: MANI rendered correctly in output PDF")

if __name__ == "__main__":
    print("===========================================================================")
    print("  VERIFYING DELIVERED TO ROW COLSPAN FIX")
    print("===========================================================================")
    unittest.main()
