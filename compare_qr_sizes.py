import cv2
import fitz
import os
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
from permit_master_source import generate_pdf

def test_qr_size(qr_size_mm, output_pdf_name):
    # Temporarily update template.html CSS for test
    tpl_path = os.path.abspath("pdf_generator/template.html")
    with open(tpl_path, "r", encoding="utf-8") as f:
        original_css = f.read()

    # Replace width: 14mm; height: 14mm; with target size
    test_css = original_css.replace(
        "width: 14mm;\n            height: 14mm;",
        f"width: {qr_size_mm}mm;\n            height: {qr_size_mm}mm;"
    )

    with open(tpl_path, "w", encoding="utf-8") as f:
        f.write(test_css)

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

    try:
        generate_pdf(data, output_pdf_name)
    finally:
        # Restore original template.html
        with open(tpl_path, "w", encoding="utf-8") as f:
            f.write(original_css)

    # Render PDF page to image
    doc = fitz.open(output_pdf_name)
    page = doc[0]
    pix = page.get_pixmap(dpi=300)
    img_path = f"test_qr_{qr_size_mm}mm.png"
    pix.save(img_path)

    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    # Crop QR region
    qr_crop = img[0:int(h*0.25), int(w*0.65):w]

    detector = cv2.QRCodeDetector()

    # 1. Digital PDF
    val_digital, _, _ = detector.detectAndDecode(qr_crop)

    # 2. Print Simulation (150 DPI blur)
    print_sim = cv2.resize(qr_crop, (int(qr_crop.shape[1] * 0.7), int(qr_crop.shape[0] * 0.7)))
    print_sim = cv2.GaussianBlur(print_sim, (3, 3), 0.3)
    val_print, _, _ = detector.detectAndDecode(print_sim)

    # 3. Xerox Simulation (contrast drop + blur + threshold)
    gray = cv2.cvtColor(print_sim, cv2.COLOR_BGR2GRAY)
    xerox = cv2.convertScaleAbs(gray, alpha=0.85, beta=15)
    xerox = cv2.GaussianBlur(xerox, (3, 3), 0.5)
    _, xerox_thresh = cv2.threshold(xerox, 140, 255, cv2.THRESH_BINARY)
    xerox_bgr = cv2.cvtColor(xerox_thresh, cv2.COLOR_GRAY2BGR)
    val_xerox, _, _ = detector.detectAndDecode(xerox_bgr)

    print(f"\n==========================================")
    print(f"=== TESTING {qr_size_mm}mm QR CODE ===")
    print(f"==========================================")
    print(f"Digital PDF Scan:  {'PASS' if val_digital else 'FAIL'}")
    print(f"  -> Payload: {val_digital}")
    print(f"Print Simulation:  {'PASS' if val_print else 'FAIL'}")
    print(f"  -> Payload: {val_print}")
    print(f"Xerox Simulation:  {'PASS' if val_xerox else 'FAIL'}")
    print(f"  -> Payload: {val_xerox}")
    
    # Measure QR Y-span in mm from PyMuPDF drawings / images
    imgs = page.get_image_info()
    drawings = page.get_drawings()
    print(f"Images count: {len(imgs)}")
    if imgs:
        qr_bbox = [v/2.83465 for v in imgs[0]['bbox']]
        print(f"QR 1 BBox: Y={qr_bbox[1]:.2f}..{qr_bbox[3]:.2f}mm, Size: {qr_bbox[2]-qr_bbox[0]:.2f}mm x {qr_bbox[3]-qr_bbox[1]:.2f}mm")

if __name__ == "__main__":
    test_qr_size(14, "test_qr_14mm.pdf")
    test_qr_size(18, "test_qr_18mm.pdf")
