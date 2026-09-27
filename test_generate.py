"""Quick test script to generate a sample PDF with the updated layout."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from permit_master_source import generate_pdf, init_db

init_db()

# Sample data matching the reference
test_data = {
    "serial_no": "TN033886031",
    "lessee_id": "CHN241557",
    "minecode": "KKIN00225",
    "lessee_name": "Gautham P M",
    "lessee_address": "No. 19, 11th Avenue, Ashok nagar, Chennai - 600083",
    "hsn_code": "6100090",
    "district": "Kallakurichi",
    "taluk": "Ulundurpet",
    "village": "Kallamedu",
    "sf_no": "58/1 (P-1)., / 00002.85.00",
    "classification": "Porampoke Land",
    "lease_period": "12-07-2024 to 07-11-2026",
    "mineral": "Pebbles",
    "bulk_permit": "K420000146",
    "order_ref": "",
    "within_tn": "Yes",
    "dispatch_slip": "DISP0013003P011",
    "delivered_to": "KVMR",
    "quantity": "5",
    "auth_person": "Gautham P M",
    "vehicle_no": "TN62 OP 12",
    "vehicle_type": "Lorry/Tipper",
    "distance": "130",
    "destination": "SKAV TRADERS",
    "via": "TN.KALLAKUR",
    "traveling_date": "01-04-2026",
    "traveling_time": "01:06 AM",
    "req_hours": "12",
    "driver_name": "V.K.MANI RAJA",
    "driver_license": "TN02119510991",
    "driver_phone": "8420891196",
}

out_path = os.path.join(os.path.dirname(__file__), "Test_Reference_Match.pdf")
generate_pdf(test_data, out_path)
print(f"PDF generated: {out_path}")
