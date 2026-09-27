import cv2
import numpy as np
import fitz
import os
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
from permit_master_source import generate_pdf, generate_qr_base64

def generate_svg_qr_base64(data: str) -> str:
    """Generates a high-clarity Vector SVG QR code with Level H error correction and 4-module quiet zone."""
    factory = qrcode.image.svg.SvgPathImage
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction (30% recovery)
        box_size=10,
        border=4,  # Standard 4-module quiet zone
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(image_factory=factory)
    stream = BytesIO()
    img.save(stream)
    svg_b64 = base64.b64encode(stream.getvalue()).decode('utf-8')
    return f"data:image/svg+xml;base64,{svg_b64}"

def test_rendering_and_scanning():
    data = {
        'serial_no': 'TN03996631',
        'lessee_id': 'CHN241557',
        'minecode': 'KKIN0025',
        'lessee_name': 'Gautham P M',
        'lessee_address': 'No. 19, 1 1th Avenue, Ashok nagar, Chennai - 600083',
        'hsn_code': '5390009',
        'district': 'Kallakurichi',
        'taluk': 'Ulundurpet',
        'village': 'Kallamedu',
        'sf_no': '58/1 (P-1)., / 00002.85.00',
        'classification': 'Porampoke Land',
        'lease_period': '12-07-2024 to 07-11-2026',
        'mineral': 'Pebbles',
        'bulk_permit': 'KKI250000399',
        'order_ref': '',
        'within_tn': 'Yes',
        'dispatch_slip': 'DISP0000052993368',
        'delivered_to': 'SARAVANAN',
        'quantity': '9',
        'auth_person': 'Gautham P M',
        'vehicle_no': 'TN46 M6499',
        'vehicle_type': 'Tipper',
        'distance': '320',
        'destination': 'ARANTHANGI',
        'via': 'PERAMBALUR',
        'traveling_date': '03-04-2026',
        'traveling_time': '07:40 PM',
        'req_hours': '12',
        'driver_name': 'SATHISH R',
        'driver_license': 'TN91Y20180001610',
        'driver_phone': '-',
    }

    output_pdf = os.path.abspath("test_qr_update.pdf")
    generate_pdf(data, output_pdf)

    # Render PDF page to high-res image (300 DPI) for scanning test
    doc = fitz.open(output_pdf)
    page = doc[0]
    pix = page.get_pixmap(dpi=300)
    img_path = "test_qr_page_300dpi.png"
    pix.save(img_path)

    # Load image with OpenCV
    img = cv2.imread(img_path)
    detector = cv2.QRCodeDetector()

    # 1. Digital PDF scanning test
    val, points, _ = detector.detectAndDecode(img)
    print("\n=== DIGITAL PDF SCAN TEST ===")
    print("Detected Payload:", val)
    print("Digital PDF Scan Pass:", bool(val))

    # 2. Print Simulation (DPI reduction + subtle blur)
    h, w = img.shape[:2]
    print_sim = cv2.resize(img, (w // 2, h // 2)) # simulate 150 DPI print
    print_sim = cv2.GaussianBlur(print_sim, (3, 3), 0)
    val_print, _, _ = detector.detectAndDecode(print_sim)
    print("\n=== PRINT SIMULATION SCAN TEST ===")
    print("Detected Payload:", val_print)
    print("Printed PDF Scan Pass:", bool(val_print))

    # 3. Xerox / Photocopy Simulation
    gray = cv2.cvtColor(print_sim, cv2.COLOR_BGR2GRAY)
    xerox_sim = cv2.convertScaleAbs(gray, alpha=0.85, beta=15)
    xerox_sim = cv2.GaussianBlur(xerox_sim, (3, 3), 0.5)
    _, xerox_thresh = cv2.threshold(xerox_sim, 140, 255, cv2.THRESH_BINARY)
    xerox_bgr = cv2.cvtColor(xerox_thresh, cv2.COLOR_GRAY2BGR)
    val_xerox, _, _ = detector.detectAndDecode(xerox_bgr)
    print("\n=== XEROX PHOTOCOPY SIMULATION SCAN TEST ===")
    print("Detected Payload:", val_xerox)
    print("Xerox Copy Scan Pass:", bool(val_xerox))

if __name__ == "__main__":
    test_rendering_and_scanning()
