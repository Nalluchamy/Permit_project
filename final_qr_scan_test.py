import os
import fitz
import cv2
from permit_master_source import generate_pdf, messagebox

# Patch messagebox to avoid GUI popups
messagebox.showerror = lambda t, m: print('ERR:', t, m)

test_data = {
    'serial_no': 'TN03996631',
    'dispatch_slip': 'DISP000007354833',
    'minecode': 'KKIN0025',
    'traveling_date': '01-04-2026',
    'traveling_time': '06:45 PM',
    'hsn_code': '6290009',
    'lessee_id': 'CHN241557',
    'lessee_name': 'Gautham P M',
    'lessee_address': 'No. 19, 11th Avenue, Ashok nagar, Chennai - 600083',
    'district': 'Kallakurichi',
    'taluk': 'Ulundurpet',
    'village': 'Kallamedu',
    'sf_no': '58/1 (P-1)., / 00002.85.00',
    'mineral': 'Pebbles',
    'bulk_permit': 'KKI260000085',
    'order_ref': 'REF123',
    'classification': 'Porampoke Land',
    'lease_period': '12-07-2024 to 07-11-2028',
    'within_tn': 'Yes',
    'delivered_to': 'MANI',
    'vehicle_no': 'TN56J7212',
    'vehicle_type': 'Taurus 19',
    'distance': '689',
    'destination': 'ARANTHANGI',
    'via': 'THANJAVUR',
    'req_hours': '12',
    'driver_name': 'PARAMASIVAM',
    'driver_license': 'TN31Y20090003199',
    'driver_phone': '9642063599',
    'auth_person': 'Gautham P M',
    'quantity': '9'
}

pdf_path = os.path.abspath('qr_scan_test_final.pdf')
generate_pdf(test_data, pdf_path)
if not os.path.exists(pdf_path):
    print('PDF NOT CREATED')
    exit(1)

print('PDF created:', pdf_path)

# Render page at 300 DPI and crop the QR code region
doc = fitz.open(pdf_path)
page = doc[0]
pix = page.get_pixmap(dpi=300)
pix.save('qr_scan_test_final_300dpi.png')

img = cv2.imread('qr_scan_test_final_300dpi.png')
h, w = img.shape[:2]

# QR is top-right corner (header area)
crop = img[int(h*0.04):int(h*0.22), int(w*0.7):int(w*0.98)]
cv2.imwrite('qr_scan_crop.png', crop)

detector = cv2.QRCodeDetector()

# 1. Direct digital scan
v1, _, _ = detector.detectAndDecode(crop)

# 2. Simulated print scan (150 DPI, Gaussian blur for ink bleed)
sim_print = cv2.resize(crop, (0, 0), fx=0.5, fy=0.5)
sim_print = cv2.GaussianBlur(sim_print, (3, 3), 0.5)
v2, _, _ = detector.detectAndDecode(sim_print)

# 3. Simulated Xerox photocopy scan (contrast loss + threshold)
gray = cv2.cvtColor(sim_print, cv2.COLOR_BGR2GRAY)
xerox = cv2.convertScaleAbs(gray, alpha=0.75, beta=25)
xerox = cv2.GaussianBlur(xerox, (3, 3), 0.7)
_, xerox_th = cv2.threshold(xerox, 140, 255, cv2.THRESH_BINARY)
v3, _, _ = detector.detectAndDecode(cv2.cvtColor(xerox_th, cv2.COLOR_GRAY2BGR))

print()
print('=== QR CODE PRINT SCAN TEST ===')
print('Digital scan  (300 DPI):', 'PASS' if v1 else 'FAIL', v1[:60] if v1 else '')
print('Print scan    (150 DPI):', 'PASS' if v2 else 'FAIL', v2[:60] if v2 else '')
print('Xerox scan    (degraded):', 'PASS' if v3 else 'FAIL', v3[:60] if v3 else '')
