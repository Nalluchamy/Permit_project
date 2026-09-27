import os
import fitz
import cv2
import qrcode
import base64
from io import BytesIO
from permit_master_source import generate_pdf

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

def test_rendering(label, size_css, ecc_val, is_png=False):
    tpl_path = os.path.abspath('pdf_generator/template.html')
    with open(tpl_path, 'r', encoding='utf-8') as f:
        orig_html = f.read()
    
    patched_html = orig_html.replace('width: 14mm;', f'width: {size_css};').replace('height: 14mm;', f'height: {size_css};')
    with open(tpl_path, 'w', encoding='utf-8') as f:
        f.write(patched_html)

    import permit_master_source
    def custom_qr_gen(data_str):
        qr_obj = qrcode.QRCode(version=None, error_correction=ecc_val, box_size=12, border=4)
        qr_obj.add_data(data_str)
        qr_obj.make(fit=True)
        if is_png:
            img = qr_obj.make_image(fill_color='black', back_color='white')
            stream = BytesIO()
            img.save(stream, format='PNG')
            b64 = base64.b64encode(stream.getvalue()).decode('utf-8')
            return f'data:image/png;base64,{b64}'
        else:
            import qrcode.image.svg
            factory = qrcode.image.svg.SvgPathImage
            img = qr_obj.make_image(image_factory=factory)
            stream = BytesIO()
            img.save(stream)
            b64 = base64.b64encode(stream.getvalue()).decode('utf-8')
            return f'data:image/svg+xml;base64,{b64}'
    
    old_gen = permit_master_source.generate_qr_base64
    permit_master_source.generate_qr_base64 = custom_qr_gen

    pdf_out = os.path.abspath(f'test_qr_{label}.pdf')
    try:
        generate_pdf(test_data, pdf_out)
    finally:
        permit_master_source.generate_qr_base64 = old_gen
        with open(tpl_path, 'w', encoding='utf-8') as f:
            f.write(orig_html)

    doc = fitz.open(pdf_out)
    page = doc[0]
    pix = page.get_pixmap(dpi=300)
    png_path = f'test_qr_{label}.png'
    pix.save(png_path)

    img = cv2.imread(png_path)
    detector = cv2.QRCodeDetector()
    
    h, w = img.shape[:2]
    qr_crop = img[0:int(h*0.3), int(w*0.6):w]
    val_digital, _, _ = detector.detectAndDecode(qr_crop)
    
    sim_print = cv2.resize(qr_crop, (0,0), fx=0.6, fy=0.6)
    sim_print = cv2.GaussianBlur(sim_print, (3,3), 0.4)
    val_print, _, _ = detector.detectAndDecode(sim_print)

    gray = cv2.cvtColor(sim_print, cv2.COLOR_BGR2GRAY)
    xerox = cv2.convertScaleAbs(gray, alpha=0.8, beta=20)
    xerox = cv2.GaussianBlur(xerox, (3,3), 0.6)
    _, xerox_th = cv2.threshold(xerox, 140, 255, cv2.THRESH_BINARY)
    val_xerox, _, _ = detector.detectAndDecode(cv2.cvtColor(xerox_th, cv2.COLOR_GRAY2BGR))

    print(f'=== TEST [{label}] ===')
    print(f'Digital scan: {"PASS" if val_digital else "FAIL"} ({val_digital[:30] if val_digital else ""})')
    print(f'Print scan:   {"PASS" if val_print else "FAIL"} ({val_print[:30] if val_print else ""})')
    print(f'Xerox scan:   {"PASS" if val_xerox else "FAIL"} ({val_xerox[:30] if val_xerox else ""})')
    print()

if __name__ == "__main__":
    test_rendering('current_14mm_H', '14mm', qrcode.constants.ERROR_CORRECT_H, False)
    test_rendering('opt1_18.5mm_M_SVG', '18.5mm', qrcode.constants.ERROR_CORRECT_M, False)
    test_rendering('opt2_18.5mm_M_PNG', '18.5mm', qrcode.constants.ERROR_CORRECT_M, True)
    test_rendering('opt3_19mm_Q_PNG', '19mm', qrcode.constants.ERROR_CORRECT_Q, True)
