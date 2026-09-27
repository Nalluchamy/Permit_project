import os
import sys
import tempfile
import base64
import subprocess
from datetime import datetime

def generate_pdf_test(d: dict, path: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tpl_path = os.path.join(base_dir, "pdf_generator", "template.html")
    
    with open(tpl_path, 'r', encoding='utf8') as f:
        html = f.read()
    
    d['qr_code_url'] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    d['dispatch_datetime'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    d['signature_img_tag'] = ""
    
    for key, value in d.items():
        html = html.replace(f"{{{{{key}}}}}", str(value) if value is not None else "")
        
    temp_html = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf8')
    temp_html.write(html)
    temp_html.close()
    
    browser_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
    edge_temp_dir = tempfile.mkdtemp()
    file_url = "file:///" + temp_html.name.replace("\\", "/")

    print(f"Running edge for {path}...")
    result = subprocess.run([
        browser_path, 
        "--headless=new", 
        f"--print-to-pdf={path}", 
        "--no-pdf-header-footer",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={edge_temp_dir}",
        file_url
    ], capture_output=True, text=True, startupinfo=startupinfo, timeout=30)
    
    print(f"Code: {result.returncode}")
    print(f"Err: {result.stderr}")
    
    os.unlink(temp_html.name)

if __name__ == "__main__":
    d = {"serial_no": "TEST-USER-CODE"}
    path = os.path.join(tempfile.gettempdir(), "Permit_TN03996631.pdf")
    generate_pdf_test(d, path)
