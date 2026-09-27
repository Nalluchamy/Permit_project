import os
import fitz
import cv2
import qrcode
import base64
from io import BytesIO
from permit_master_source import generate_pdf, APP_DATA_DIR, get_resource_path

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

def run_test(label, size_css, ecc_val, is_png=False, compact_payload=False):
    tpl_path = get_resource_path(os.path.join('pdf_generator', 'template.html'))
    with open(tpl_path, 'r', encoding='utf-8') as f:
        orig_html = f.read()
    
    patched_html = orig_html.replace('width: 14mm;', f'width: {size_css};').replace('height: 14mm;', f'height: {size_css};')
    patched_html = patched_html.replace('top: 21.06mm;', 'top: 17.5mm;')
    with open(tpl_path, 'w', encoding='utf-8') as f:
        f.write(patched_html)

    import permit_master_source
    def custom_qr(data_str):
        if compact_payload:
            base_url = "https://cheery-sherbet-91f7c4.netlify.app/"
            params = "s=TN03996631&sl=DISP000007354833&m=KKIN0025&d=01-04-2026+18%3A45&v=TN56J7212&mn=Pebbles(9MT)&dt=689&r=12&ds=ARANTHANGI"
            data_str = f"{base_url}?{params}"
            
        qr_obj = qrcode.QRCode(version=None, error_correction=ecc_val, box_size=12, border=4)
        qr_obj.add_data(data_str)
        qr_obj.make(fit=True)
        if is_png:
            import qrcode.image.pil
            img = qr_obj.make_image(image_factory=qrcode.image.pil.PilImage)
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
    permit_master_source.generate_qr_base64 = custom_qr

    pdf_out = os.path.abspath(f'test_{label}.pdf')
    try:
        generate_pdf(test_data, pdf_out)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        permit_master_source.generate_qr_base64 = old_gen
        with open(tpl_path, 'w', encoding='utf-8') as f:
            f.write(orig_html)

    doc = fitz.open(pdf_out)
    page = doc[0]
    pix = page.get_pixmap(dpi=300)
    png_path = f'test_{label}_300dpi.png'
    pix.save(png_path)

    img = cv2.imread(png_path)
    h, w = img.shape[:2]
    crop = img[int(h*0.04):int(h*0.22), int(w*0.7):int(w*0.98)]
    
    detector = cv2.QRCodeDetector()

    # 1. Direct scan
    v1, _, _ = detector.detectAndDecode(crop)

    # 2. Simulated Print Blur (150 DPI blur + ink bleed simulation)
    sim_print = cv2.resize(crop, (0,0), fx=0.6, fy=0.6)
    sim_print = cv2.GaussianBlur(sim_print, (3,3), 0.4)
    v2, _, _ = detector.detectAndDecode(sim_print)

    # 3. Simulated Xerox Photo (downscale + contrast loss + noise)
    gray = cv2.cvtColor(sim_print, cv2.COLOR_BGR2GRAY)
    xerox = cv2.convertScaleAbs(gray, alpha=0.8, beta=20)
    xerox = cv2.GaussianBlur(xerox, (3,3), 0.5)
    _, xerox_th = cv2.threshold(xerox, 140, 255, cv2.THRESH_BINARY)
    v3, _, _ = detector.detectAndDecode(cv2.cvtColor(xerox_th, cv2.COLOR_GRAY2BGR))

    print(f'=== TEST [{label}] ===')
    print(f'Direct scan: {"PASS" if v1 else "FAIL"}')
    print(f'Print scan:  {"PASS" if v2 else "FAIL"}')
    print(f'Xerox scan:  {"PASS" if v3 else "FAIL"}')
    print()

if __name__ == '__main__':
    run_test('18.5mm_LevelM_PNG', '18.5mm', qrcode.constants.ERROR_CORRECT_M, True, False)
    run_test('18.5mm_LevelM_SVG', '18.5mm', qrcode.constants.ERROR_CORRECT_M, False, False)
    run_test('19mm_LevelM_PNG', '19mm', qrcode.constants.ERROR_CORRECT_M, True, False)
    run_test('18.5mm_LevelM_PNG_Compact', '18.5mm', qrcode.constants.ERROR_CORRECT_M, True, True)
