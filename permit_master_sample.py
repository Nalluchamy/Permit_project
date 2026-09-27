"""
Permit Master — Scaled Sample Generator
"""
import customtkinter as ctk
from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
import qrcode
import tempfile
import os
from datetime import datetime, timedelta
from urllib.parse import quote

def generate_qr_img(data: str) -> str:
    qr = qrcode.QRCode(version=None, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name)
    return tmp.name

def build_permit_block(c, d, y_top_anchor, page_w):
    L, R = 66.77, 595.28 - 62.14
    W, serial = R - L, d.get("serial_no", "TN03996631")
    
    lbl_s = ParagraphStyle('lbl', fontName='Helvetica', fontSize=5.0, leading=5.5)
    val_s = ParagraphStyle('val', fontName='Helvetica-Bold', fontSize=5.0, leading=5.5)
    
    def mk_lb(txt): return Paragraph(str(txt) if txt else "", lbl_s)
    def mk_vl(txt): return Paragraph(f'<b>{txt}</b>', val_s)
    def mk_lv(l, v): return Paragraph(f"{l} <b>{v if v else ''}</b>", lbl_s)

    # QR and Serial
    qr_path = generate_qr_img("https://test.com/verify?s=" + serial)
    qr_sz = 14 * 0.3527 * 72/25.4 # approx 14mm in pts
    try:
        c.drawImage(qr_path, R - 40, y_top_anchor + 10, 40, 40)
    finally: os.unlink(qr_path)
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor('#A9A9A9'))
    c.drawRightString(R - 45, y_top_anchor + 20, serial)
    c.setFillColor(colors.black)

    req_v = "12hrs (18-04-2026 06:45 AM)"
    rows = [
        [mk_lv("HSN Code:", "6290009"), "", "", mk_lv("Date:", "17-04-2026 12:45:00")],
        [mk_lv("Lessee Id :", "CHN241557"), mk_lv("Minecode :", "KKIN00225"), mk_lb("Lease Area Details"), mk_lv("Serial No:", serial)],
        [mk_lb("Lessee Name and Address:"), mk_vl("Gautham P M"), mk_lb("District Name:"), mk_vl("Kallakurichi")],
        [mk_vl("No. 19, 11th Avenue, Ashok nagar, Chennai - 600083"), "", mk_lb("Taluk Name:"), mk_vl("Ulundurpet")],
        ["", "", mk_lb("Village:"), mk_vl("Kallamedu")],
        ["", "", mk_lb("SF.No / Extent:"), mk_vl("58/1 (P-1)., / 00002.85.00")],
        [mk_lv("Mineral Name:", "Pebbles"), mk_lv("Bulk Permit No:", "KKI260000085"), mk_lb("Classification:"), mk_vl("Porampoke Land")],
        [mk_lb("Order Ref:"), mk_vl("REF123"), mk_lb("Lease Period:"), mk_vl("12-07-2024 to 07-11-2028")],
        [mk_lb("Dispatch Slip No:"), mk_vl("DISP000007354833"), mk_lb("Within Tamil Nadu:"), mk_vl("Yes")],
        [mk_lb("Delivered To:"), mk_vl("MANI"), mk_lb("Destination Address:"), ""],
        [mk_lb("Vehicle No:"), mk_vl("TN56J7212"), mk_vl("ARANTHANGI"), ""],
        [mk_lb("Vehicle Type:"), mk_vl("Taurus 19"), "", ""],
        [mk_lb("Total Distance In (Kms):"), mk_vl("689"), "", ""],
        [mk_lb("Traveling Date:"), mk_vl("01-04-2026 06:45 PM"), mk_lb("Driver Name:"), mk_vl("PARAMASIVAM")],
        [mk_lb("Required Time:"), mk_vl(req_v), mk_lb("Via:"), mk_vl("THANJAVUR")],
        [mk_lb("Driver License No:"), mk_vl("TN31Y20090003199"), mk_lb("Lease / Authorized Person Name:"), mk_vl("Gautham P M")],
        [mk_lb("Driver Signature:"), "", mk_lb("Signature of AD / DD:"), ""]
    ]

    col_ws = [114.83, 115.78, 117.52, 118.23]
    orig_row_hs = [13.82, 46.80, 14.40, 19.18, 14.41, 14.41, 13.47, 14.29, 14.29, 53.37, 13.68, 13.68, 13.68, 13.67, 13.68, 13.68, 30.47]
    row_hs = [h * 0.7745 for h in orig_row_hs]
    
    tbl = Table(rows, colWidths=col_ws, rowHeights=row_hs)
    tbl.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('SPAN', (0,3), (1,5)),
        ('SPAN', (2,10), (3,10)),
        ('SPAN', (2,11), (3,13)),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('FONTSIZE', (0,0), (-1,-1), 5),
    ]))
    
    tbl.wrapOn(c, W, 800)
    tbl_y = y_top_anchor - sum(row_hs)
    tbl.drawOn(c, L, tbl_y)

def generate_pdf(path):
    c = rl_canvas.Canvas(path, pagesize=(595.28, 841.89))
    data = {"serial_no": "TN03996631"}
    
    # Coordinates from spec
    y1 = 841.89 - 142.19
    y2 = 841.89 - 499.94
    
    build_permit_block(c, data, y1, 595.28)
    build_permit_block(c, data, y2, 595.28)
    c.save()

if __name__ == "__main__":
    generate_pdf("scaled_sample_test.pdf")
