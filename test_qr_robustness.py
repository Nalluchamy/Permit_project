import cv2
import numpy as np
import fitz
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
import os

def test_qr():
    # 1. Payload inspection
    old_payload = "https://cheery-sherbet-91f7c4.netlify.app/?serial=TN03996631&slip=DISP0000052993368&minecode=KKIN0025&date=03-04-2026%2019%3A40&vehicle=TN46%20M6499&mineral=Pebbles%289MT%29&distance=320&reqtime=12&dest=ARANTHANGI"
    compact_url_payload = "https://cheery-sherbet-91f7c4.netlify.app/?serial=TN03996631"
    compact_id_payload = "TN03996631"

    print("=== TASK 1: PAYLOAD INSPECTION ===")
    print(f"Old Payload Length: {len(old_payload)} chars")
    print(f"Compact URL Payload Length: {len(compact_url_payload)} chars")
    print(f"Compact ID Payload Length: {len(compact_id_payload)} chars")

    # Inspect module matrix size for old vs compact
    qr_old = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr_old.add_data(old_payload)
    qr_old.make(fit=True)
    
    qr_compact_h = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr_compact_h.add_data(compact_url_payload)
    qr_compact_h.make(fit=True)

    print(f"\nOld QR Version: Version {qr_old.version} ({len(qr_old.modules)}x{len(qr_old.modules)} modules)")
    print(f"Compact Level H QR Version: Version {qr_compact_h.version} ({len(qr_compact_h.modules)}x{len(qr_compact_h.modules)} modules)")

    # 2. Generator function (SVG Vector QR)
    def gen_svg_qr(payload):
        factory = qrcode.image.svg.SvgPathImage
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(image_factory=factory)
        stream = BytesIO()
        img.save(stream)
        svg_b64 = base64.b64encode(stream.getvalue()).decode('utf-8')
        return f"data:image/svg+xml;base64,{svg_b64}"

    svg_data_url = gen_svg_qr(compact_url_payload)
    print("\n=== TASK 2: VECTOR SVG QR GENERATION ===")
    print(f"Generated Vector SVG Data URL length: {len(svg_data_url)} chars")

if __name__ == "__main__":
    test_qr()
