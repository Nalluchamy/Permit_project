# PermitMaster — Troubleshooting & Support Guide (v1.0.0)

---

## Common Issues & Solutions

### 1. Error: "The file is currently open in Microsoft Edge..."
- **Symptom:** PDF generation or printing fails with a PermissionError.
- **Cause:** A previously generated PDF with the same filename is currently open in a Microsoft Edge browser tab or PDF viewer, locking the file.
- **Solution:** Close the PDF tab in Microsoft Edge and retry printing.

### 2. Error: "No compatible browser found..."
- **Symptom:** Application reports missing browser when attempting to generate PDF permits.
- **Cause:** Neither Microsoft Edge (`msedge.exe`) nor Google Chrome (`chrome.exe`) is installed or registered in Windows Registry.
- **Solution:** Install Microsoft Edge or Google Chrome. Edge comes pre-installed on standard Windows 10/11 installations.

### 3. QR Code Scanning Difficulties on Printed Copies
- **Symptom:** QR scanner on phone/handheld device does not decode paper permit.
- **Cause:** Low printer toner contrast, low print scaling, or printer paper alignment issues.
- **Solution:** Print PDF at 100% scale (A4 actual size). Ensure printer toner is sufficient. Clean scanner camera lens.

### 4. Application Fails to Start (Database Permission Error)
- **Symptom:** SQLite database error on launch.
- **Cause:** Application binary attempting to write database inside protected `C:\Program Files\` directory instead of user AppData.
- **Solution:** Ensure application is run from the official installer or that `%LOCALAPPDATA%\PermitMaster\` directory exists with write permissions for the current Windows user.
