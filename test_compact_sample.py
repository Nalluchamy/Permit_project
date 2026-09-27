import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from permit_master_source import generate_pdf
from datetime import datetime

# Create a dummy signature image for testing
from PIL import Image, ImageDraw
sig_path = os.path.join(BASE_DIR, "test_sig.png")
img = Image.new('RGBA', (200, 80), (255, 255, 255, 0))
d_draw = ImageDraw.Draw(img)
d_draw.text((10, 10), "TEST SIGNATURE", fill=(0, 0, 255))
img.save(sig_path)

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
    "quantity": "9",
    "signature_path": sig_path
}

output_path = os.path.join(BASE_DIR, "test_client_perfect.pdf")
print(f"Generating test PDF at: {output_path}")
generate_pdf(test_data, output_path)
print("Done. Verification PNG will be generated next.")
