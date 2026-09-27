import os
import json
import base64
from io import BytesIO
import qrcode

def generate_qr_base64(data: str) -> str:
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"

def create_preview_html():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    tpl_path = os.path.join(current_dir, "pdf_generator", "template.html")
    
    with open(tpl_path, 'r', encoding='utf8') as f:
        html = f.read()
    
    data = {
        "serial_no": "PREVIEW-2026",
        "lessee_id": "C-12345",
        "minecode": "MC-999",
        "lessee_name": "Premium Mining Corp",
        "district": "Salem",
        "lessee_address": "No 1. Industrial Zone, Salem - 636001",
        "taluk": "Salem West",
        "village": "Omalur",
        "sf_no": "SF 101 / 5.00 HA",
        "mineral": "Granite",
        "bulk_permit": "BP-2026-001",
        "classification": "Non-Captive",
        "lease_period": "2024 - 2044",
        "dispatch_slip": "SLIP-8888",
        "within_tn": "Yes",
        "delivered_to": "Gautham Construction Ltd",
        "vehicle_no": "TN 30 AB 1234",
        "vehicle_type": "10-Wheeler",
        "destination": "Bangalore Junction Site, Plot 42",
        "distance": "120",
        "traveling_date": "22-04-2026",
        "req_hours": "6",
        "quantity": "25.5",
        "driver_name": "S. Kumar",
        "driver_license": "DL-909090",
        "via": "Krishnagiri",
        "driver_phone": "9876543210",
        "auth_person": "Managing Director",
        "hsn_code": "2515",
        "dispatch_datetime": "22-04-2026 13:40:00",
        "qr_code_url": generate_qr_base64("https://verify.example.com/PREVIEW"),
        "signature_img_tag": '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAAAbCAYAAABv6m80AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAABMSURBVHgB7dKxCQAgEATBf9p/YmUBC9A7mD8Z8mByyY0V6LidB8Y5T8V8t/OAYY5TkN/uPDCY4xLktzsPDGaMMeZfGGPMeWCMMeb8C2OMOf/CGGPOvzDGmPMvjDHm/AtjjDn/whhjzr8wxgzMP701E78hK604AAAAAElFTkSuQmCC" class="sig-img" alt="Sig">'
    }
    
    for k, v in data.items():
        html = html.replace(f"{{{{{k}}}}}", str(v))
        
    output_path = os.path.join(current_dir, "final_full_preview.html")
    with open(output_path, 'w', encoding='utf8') as f:
        f.write(html)
    return output_path

if __name__ == "__main__":
    print(create_preview_html())
