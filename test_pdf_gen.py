"""Quick test of PDF generation"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

# Minimal import to avoid UI loading
from permit_master_source import generate_pdf

test_data = {
    'serial_no': 'TN03996631',
    'lessee_id': 'CHN241557',
    'minecode': 'KKIN00225',
    'lessee_name': 'Gautham P M',
    'lessee_address': 'No. 19, 11th Avenue, Ashok nagar, Chennai - 600083',
    'hsn_code': '6290009',
    'district': 'Kallakurichi',
    'taluk': 'Ulundurpet',
    'village': 'Kallamedu',
    'sf_no': '58/1 (P 1), / 00002.85.00',
    'classification': 'Porampoke Land',
    'lease_period': '12-07-2024 to 07-11-2026',
    'mineral': 'Pebbles',
    'bulk_permit': '',
    'order_ref': '',
    'within_tn': 'Yes',
    'dispatch_slip': 'DISP0000000000010',
    'delivered_to': '',
    'quantity': '10',
    'auth_person': 'Gautham P M',
    'vehicle_no': 'TN01AB1234',
    'vehicle_type': 'Lorry',
    'distance': '50',
    'destination': 'Chennai',
    'via': 'Villupuram',
    'traveling_date': '22-04-2026',
    'traveling_time': '12:00 PM',
    'req_hours': '12',
    'driver_name': 'Test Driver',
    'driver_license': 'TN1234567890',
    'driver_phone': '9876543210',
}

out_path = os.path.join(os.path.dirname(__file__), 'test_output_verify.pdf')
print(f"Generating PDF to: {out_path}")
try:
    generate_pdf(test_data, out_path)
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"SUCCESS! PDF generated: {size} bytes")
    else:
        print("FAIL: PDF file was not created")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
