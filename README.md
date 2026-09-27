# PermitMaster — TN Mining Dispatch Permit Generator

![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)
![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-brightgreen)
![License](https://img.shields.io/badge/license-Proprietary-red)
![Status](https://img.shields.io/badge/status-Production%20Ready-success)

A production-ready Windows desktop application built with Python and CustomTkinter for generating, managing, validating, and tracking **Tamil Nadu Mining Dispatch Permits**.

PermitMaster generates official, pixel-perfect dual-copy A4 PDF dispatch permits (Office Copy & Driver Copy) embedded with dynamic QR codes for instant on-field scannability and web verification.

---

## 🚀 Key Features

- **Pixel-Perfect A4 Permits**: Generates official Tamil Nadu mining dispatch permits matching government layouts, exact column margins, and dual copies (Office & Driver) per page.
- **Dynamic QR Code Verification**: Generates high-density QR codes linking to online permit verification with comprehensive dispatch metadata.
- **Role-Based Access Control (RBAC)**:
  - **Admin**: Full access to permit issuance, record editing, user management, database backups, restore points, and audit trails.
  - **Staff**: Streamlined interface for rapid permit creation, searching, and printing.
- **Enterprise Security**:
  - PBKDF2-HMAC-SHA256 password hashing with 600,000 iterations and per-user cryptographic salts.
  - Constant-time password verification via `secrets.compare_digest`.
  - 100% parameterized SQL queries to prevent SQL injection.
  - Strict HTML escaping for PDF template data to prevent injection attacks.
- **Resilient Data Architecture**:
  - Local SQLite database in WAL (Write-Ahead Logging) mode for high-concurrency safety.
  - Isolated user data stored in `%LOCALAPPDATA%\PermitMaster\`.
- **Automated Backup & Disaster Recovery**:
  - Atomic database backups using SQLite Online Backup API.
  - 9-point integrity checks (`PRAGMA integrity_check`, header magic, table parity, record count validation).
  - Automated 10-backup rotation policy with safe rollback capabilities.
- **Comprehensive Audit Trail**:
  - Logs 24 critical operational events with timestamps, usernames, roles, and action outcomes.
  - Built-in administrative audit log viewer.
- **Automated Verification**: Complete test suite of 81 automated regression, security, data validation, and reliability tests.

---

## 🛠️ Architecture & Tech Stack

| Component | Technology |
|---|---|
| **GUI Framework** | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern Light UI) |
| **Language** | Python 3.11+ / 3.12 (64-bit AMD64) |
| **Database** | SQLite 3 with WAL Mode |
| **PDF Engine** | HTML5 / CSS3 Template injected and rendered via Headless Microsoft Edge / Google Chrome |
| **QR Code Engine** | `qrcode[pil]` with bilinear downscaling |
| **Packager** | PyInstaller 6.x (Single-file executable bundle) |
| **Installer** | Inno Setup 6 (`PermitMaster_Setup.iss`) |

---

## 📁 Repository Structure

```
├── permit_master_source.py     # Main application source (UI, DB, Auth, PDF engine)
├── permit_master_sample.py     # Sample runner and developer sandbox
├── requirements.txt            # Python dependencies
├── PermitMaster.spec           # PyInstaller build specification
├── build_exe.bat               # One-click Windows build batch script
├── permit_icon.ico             # Application window & executable icon
├── ad_dd_signature.png         # Official AD/DD authority signature asset
├── netlify_page.html           # Web verification portal page (Netlify)
│
├── pdf_generator/              # PDF generation subsystem
│   ├── template.html           # Frozen official A4 permit layout template
│   ├── generate.js             # Headless renderer script
│   ├── package.json            # Node.js dependencies
│   └── package-lock.json
│
├── installer/                  # Windows installer packaging
│   └── PermitMaster_Setup.iss  # Inno Setup installation script
│
├── docs/                       # Operational & architectural documentation
│   ├── version.md              # Version specifications and release notes
│   ├── phase9_admin_guide.md   # System administrator guide
│   ├── phase9_user_guide.md    # End-user dispatch operator guide
│   ├── phase9_backup_recovery_guide.md # Backup and DR procedures
│   └── phase10_final_report.md # Production acceptance certification
│
└── test_*.py / verify_*.py     # Comprehensive automated test suites (81 tests)
```

---

## 💻 Getting Started

### Prerequisites

- **Operating System**: Windows 10 (Version 1809+) or Windows 11 (64-bit)
- **Python**: Python 3.11 or 3.12 (64-bit)
- **Browser**: Microsoft Edge (pre-installed on Windows) or Google Chrome

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nalluchamy/Permit_project.git
   cd Permit_project
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python permit_master_source.py
   ```

---

## 🔨 Building Standalone Executable

To build the standalone Windows `.exe` using PyInstaller:

```cmd
build_exe.bat
```

Or manually:

```bash
pyinstaller --noconfirm PermitMaster.spec
```

The compiled binary will be placed at `dist\PermitMaster.exe`.

---

## 🧪 Running Tests

PermitMaster includes an 81-test validation suite covering security, database integrity, backup recovery, and UI operations:

```bash
# Run complete test suite
python run_all_13_tests.py

# Run individual verification suites
python test_phase3_security.py
python test_phase4_data_validation.py
python test_phase5_database_integrity.py
python test_phase6_backup_recovery.py
python test_phase7_audit.py
python test_phase8_reliability.py
python verify_phase10_golive.py
```

---

## 📄 License & Ownership

Developed for Tamil Nadu Mining Dispatch Permit Operations. All rights reserved.
