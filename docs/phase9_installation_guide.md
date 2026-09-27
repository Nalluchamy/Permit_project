# PermitMaster — Production Installation Guide (v1.0.0)

**Document Version:** 1.0.0  
**Target OS:** Microsoft Windows 10 / 11 (64-bit)

---

## 1. Overview & System Requirements

PermitMaster is packaged as a standard Windows installer (`PermitMaster_v1.0.0_Setup.exe`) or standalone executable (`dist\PermitMaster.exe`).

### Prerequisites
- **Operating System:** Windows 10 (Build 1809+) or Windows 11 (64-bit)
- **Privileges:** Windows Administrator privileges (required for Program Files installation)
- **Disk Space:** Minimum 250 MB free disk space
- **Browser:** Microsoft Edge (standard on Windows 10/11) or Google Chrome

---

## 2. Installation Procedures

### Method A: Automated Inno Setup Installer (`PermitMaster_v1.0.0_Setup.exe`)
1. Download or copy `PermitMaster_v1.0.0_Setup.exe` to your target Windows machine.
2. Double-click `PermitMaster_v1.0.0_Setup.exe`.
3. If prompted by Windows User Account Control (UAC), click **Yes** to grant installation permissions.
4. Accept the default destination folder:
   `C:\Program Files\PermitMaster\` (or `C:\Program Files (x86)\PermitMaster\`)
5. Optionally check **Create a desktop shortcut**.
6. Click **Install**. The installer will copy application binaries and automatically initialize the user data directory:
   `%LOCALAPPDATA%\PermitMaster\`
7. Click **Finish** to launch PermitMaster.

### Method B: Standalone Portable Executable (`PermitMaster.exe`)
1. Copy `dist\PermitMaster.exe` to a folder on your Windows computer (e.g. `C:\Tools\PermitMaster\`).
2. Double-click `PermitMaster.exe`.
3. On first run, the executable will automatically create `%LOCALAPPDATA%\PermitMaster\` with sub-folders `logs\`, `backups\`, and `generated_pdfs\`.

---

## 3. Directory Layout & Data Isolation

To comply with Windows security best practices and prevent UAC write restriction errors:
- **Application Executable (Read-Only):** `C:\Program Files\PermitMaster\PermitMaster.exe`
- **Writable Application Data:** `%LOCALAPPDATA%\PermitMaster\`
  - Database: `%LOCALAPPDATA%\PermitMaster\permits.db`
  - Audit Logs: `%LOCALAPPDATA%\PermitMaster\logs\app.log`
  - Automated Backups: `%LOCALAPPDATA%\PermitMaster\backups\`
  - Generated PDFs: `%LOCALAPPDATA%\PermitMaster\generated_pdfs\`

---

## 4. First-Run Admin Initialization

1. Launch `PermitMaster.exe`.
2. Because no users exist on a fresh installation, the **First-Run Admin Setup** screen appears.
3. Enter your desired **Admin Username** (e.g. `admin`) and a strong **Password**.
4. Click **Create Administrator Account**.
5. The password will be salted and hashed using PBKDF2-HMAC-SHA256 (600,000 iterations).
6. Proceed to login using your new Admin credentials.
