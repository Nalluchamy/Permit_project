"""
Permit Form Generator
Overlays Permit_TN03996631.pdf content onto FORM.pdf template to create a print-ready official permit form PDF.
"""

import os
import fitz

def overlay_permit_to_form(form_path: str, permit_path: str, output_path: str):
    """
    Overlays the permit data from permit_path onto the official FORM template at form_path.
    Saves the final print-ready PDF to output_path.
    """
    if not os.path.exists(form_path):
        raise FileNotFoundError(f"FORM PDF template not found at: {form_path}")
    if not os.path.exists(permit_path):
        raise FileNotFoundError(f"Permit PDF not found at: {permit_path}")

    # Open base form template and permit data PDF
    doc_form = fitz.open(form_path)
    doc_permit = fitz.open(permit_path)

    # Overlay permit page 0 onto form page 0
    page_form = doc_form[0]
    page_form.show_pdf_page(page_form.rect, doc_permit, 0)

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Save output PDF
    doc_form.save(output_path)
    doc_form.close()
    doc_permit.close()

    print(f"✅ Print-ready permit form saved successfully to: {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    form_file = os.path.join(base_dir, "pdf_generator", "FORM.pdf")
    permit_file = os.path.join(base_dir, "pdf_generator", "Permit_TN03996631.pdf")
    out_file = os.path.join(base_dir, "Permit_TN03996631_Form.pdf")
    out_file_sub = os.path.join(base_dir, "pdf_generator", "Permit_TN03996631_Form.pdf")

    overlay_permit_to_form(form_file, permit_file, out_file)
    overlay_permit_to_form(form_file, permit_file, out_file_sub)
