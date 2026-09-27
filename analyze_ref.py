import fitz

doc = fitz.open(r'pdf_generator/Tamil_GOWTHAM _TN02638368(1)-1.pdf')
page = doc[0]

# Images (QR Code)
print('=== IMAGES IN REFERENCE PDF ===')
for img_info in page.get_image_info():
    bbox = img_info['bbox']
    x0, y0, x1, y1 = bbox
    print(f'Image: x0={x0/2.83465:.2f}mm, y0={y0/2.83465:.2f}mm, width={(x1-x0)/2.83465:.2f}mm, height={(y1-y0)/2.83465:.2f}mm')

# Key Text Elements
print('\n=== KEY TEXT BLOCKS IN REFERENCE PDF ===')
blocks = page.get_text('blocks')
for b in blocks:
    text = b[4].strip()
    if any(k in text for k in ['TN02638', 'HSN Code', 'Date & Time', 'DISP']):
        x0, y0, x1, y1 = b[:4]
        print(f'Text: "{text[:40]}" at x0={x0/2.83465:.2f}mm, y0={y0/2.83465:.2f}mm, width={(x1-x0)/2.83465:.2f}mm, height={(y1-y0)/2.83465:.2f}mm')
