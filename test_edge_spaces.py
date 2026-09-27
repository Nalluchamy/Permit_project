import subprocess, os, tempfile

browser_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(browser_path):
    browser_path = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

test_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8')
test_html.write('<h1>Test PDF Generation</h1>')
test_html.close()

target_pdf_with_space = os.path.abspath('Test PDF With Spaces.pdf')
if os.path.exists(target_pdf_with_space):
    os.remove(target_pdf_with_space)

edge_temp_dir = tempfile.mkdtemp()
file_url = 'file:///' + test_html.name.replace('\\', '/')

print("Testing Edge PDF output path:", target_pdf_with_space)

cmd = [
    browser_path,
    '--headless=new',
    f'--print-to-pdf={target_pdf_with_space}',
    '--no-pdf-header-footer',
    '--disable-gpu',
    '--no-sandbox',
    f'--user-data-dir={edge_temp_dir}',
    file_url
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("Returncode:", res.returncode)
print("Stderr:", res.stderr)
print("Target file exists?:", os.path.exists(target_pdf_with_space))
