import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from permit_master_source import generate_pdf
from datetime import datetime

test_data = {
    "serial_no": "TEST12345",
    "dispatch_slip": "DISP0000000000001",
    "minecode": "MINE999",
    "traveling_date": datetime.now().strftime("%d-%m-%Y"),
    "traveling_time": datetime.now().strftime("%I:%M %p"),
    "hsn_code": "HSN123",
    "lessee_id": "L123",
    "lessee_name": "Test Lessee",
    "lessee_address": "Test Address",
    "district": "Test District",
    "taluk": "Test Taluk",
    "village": "Test Village",
    "sf_no": "SF123",
    "mineral": "Test Mineral",
    "bulk_permit": "BULK123",
    "order_ref": "REF123",
    "within_tn": "Yes",
    "delivered_to": "Test Destination",
    "vehicle_no": "TN01AB1234",
    "vehicle_type": "Truck",
    "distance": "100",
    "destination": "Test Destination",
    "via": "Road",
    "req_hours": "12",
    "driver_name": "Test Driver",
    "driver_license": "DL123",
    "driver_phone": "1234567890",
    "auth_person": "Authorized Person"
}

output_path = os.path.join(BASE_DIR, "test_qr_update.pdf")
print(f"Generating test PDF at: {output_path}")
generate_pdf(test_data, output_path)
print("Done. Please verify the QR code in the PDF.")
