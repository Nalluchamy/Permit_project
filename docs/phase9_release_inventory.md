# PermitMaster — Production Release Inventory (v1.0.0)

**Document Version:** 1.0.0  
**Release Date:** August 18, 2026  
**Target OS:** Microsoft Windows 10 / 11 (64-bit)

---

## 1. Release Inventory Summary

The table below catalogs all required components for building, packaging, running, and maintaining the PermitMaster production release.

| Category | Item Name | File / Directory Path | Purpose / Description | Included in Binary/Installer |
| :--- | :--- | :--- | :--- | :--- |
| **Source Code** | Main Source Code | `permit_master_source.py` | Complete monolithic Python GUI, DB, Auth, RBAC, PDF bridge & Backup source | Executable Compilation |
| **PDF Engine** | Frozen HTML Template | `pdf_generator/template.html` | 100% frozen HTML/CSS template for dual A4 permit PDF generation | Bundled (`pdf_generator/`) |
| **Assets** | Signature Asset | `ad_dd_signature.png` | Default AD/DD authorized signature image | Bundled Asset |
| **Assets** | Application Icon | `permit_icon.ico` | High-resolution application window & desktop icon | Bundled Asset & Executable Icon |
| **Database** | Database Engine | `sqlite3` (Python Standard Library) | Embedded relational database engine (WAL Mode) | Python Runtime |
| **Database** | Schema & Migration Logic | `permit_master_source.py` (`init_db()`) | Automatic schema creation, indexing, and pre-migration backup | Executable Compilation |
| **Database** | Seed Database Template | `permits.db` | Initial database template copied to `%LOCALAPPDATA%\PermitMaster\` on first run | Bundled Asset |
| **Build Configuration** | PyInstaller Spec | `PermitMaster.spec` | Production PyInstaller specification with asset hooks & data bundling | Build System Only |
| **Build Configuration** | Build Script | `build_exe.bat` | One-click Windows build batch script | Build System Only |
| **Build Configuration** | Dependency File | `requirements.txt` | Core Python package requirements (`customtkinter`, `qrcode`, `pillow`) | Build System Only |
| **Installer** | Installer Script | `installer/PermitMaster_Setup.iss` | Inno Setup script for Program Files & Start Menu shortcut deployment | Build System Only |
| **Test Suites** | Security Tests | `test_phase3_security.py` | PBKDF2 hashing, RBAC, input sanitization, and SQL injection tests | Verification Suite |
| **Test Suites** | Validation Tests | `test_phase4_data_validation.py` | Permit field length, date, time, and numeric validation tests | Verification Suite |
| **Test Suites** | DB Integrity Tests | `test_phase5_database_integrity.py` | Transactional integrity, unique constraints, and schema tests | Verification Suite |
| **Test Suites** | Backup & Recovery Tests | `test_phase6_backup_recovery.py` | 9-point backup verification, rotation, and safety rollback tests | Verification Suite |
| **Test Suites** | Audit Logging Tests | `test_phase7_audit.py` | Audit event logging, viewer filtering, and payload stripping tests | Verification Suite |
| **Test Suites** | Stress & Recovery Tests | `test_phase8_reliability.py` | Concurrency, disk full, corrupt database, and crash recovery tests | Verification Suite |
| **Documentation** | Operational Documentation | `docs/` | Phase 8 & Phase 9 operational, installation, user, and admin guides | Release Package / Documentation |

---

## 2. Dynamic Runtime File Paths (%LOCALAPPDATA%\PermitMaster\)

At runtime, PermitMaster stores all user state outside of `C:\Program Files\` under `%LOCALAPPDATA%\PermitMaster\` to prevent permission errors and ensure safe uninstallation:

- **Database File:** `%LOCALAPPDATA%\PermitMaster\permits.db`
- **Application Logs:** `%LOCALAPPDATA%\PermitMaster\logs\app.log`
- **Automated Backups:** `%LOCALAPPDATA%\PermitMaster\backups\`
- **Generated PDFs:** `%LOCALAPPDATA%\PermitMaster\generated_pdfs\`

---

## 3. Exclusion List (Excluded from Installer Package)

To ensure a minimal, secure, and production-ready installer, the following temporary or development-only files are **excluded** from distribution:
- Development source files (`*.py` scripts outside runtime needs)
- Intermediate PyInstaller build directories (`build/`, `__pycache__/`)
- Temporary render/preview images (`*.png` crops, `verif_*.png`)
- Development test logs (`p7_out.txt`, `build_log.txt`, `meipass_debug.txt`)
- Scratch test PDFs (`test_*.pdf`, `bridge_test_output.pdf`)
