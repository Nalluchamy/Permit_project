# PermitMaster — Final Production Readiness Checklist (v1.0.0)

---

## 1. Clean Build & Release Packaging
- [x] PyInstaller build succeeds with zero errors (`dist\PermitMaster.exe`).
- [x] Executable size verified (~30.03 MB).
- [x] `pdf_generator/template.html` bundled and frozen.
- [x] `ad_dd_signature.png` bundled and intact.
- [x] `permit_icon.ico` set for binary and desktop icon.
- [x] No developer-specific hardcoded absolute paths present in source code.
- [x] Inno Setup script `installer/PermitMaster_Setup.iss` created.

## 2. Windows Environment & Isolation
- [x] Application data stored under `%LOCALAPPDATA%\PermitMaster\`.
- [x] Database file (`permits.db`) stored under user AppData, avoiding Program Files write errors.
- [x] Application logs (`app.log`) isolated under `%LOCALAPPDATA%\PermitMaster\logs\`.
- [x] Automated backups stored under `%LOCALAPPDATA%\PermitMaster\backups\`.
- [x] Generated PDFs stored under `%LOCALAPPDATA%\PermitMaster\generated_pdfs\`.
- [x] Uninstaller removes application binaries while strictly preserving user data.

## 3. Security & Compliance
- [x] Default password hashing uses PBKDF2-HMAC-SHA256 (600,000 iterations).
- [x] Role-Based Access Control (Admin / Staff) strictly enforced.
- [x] HTML escaping enabled to prevent XSS injection in generated PDFs.
- [x] SQL queries parameterized to prevent SQL injection.
- [x] Zero passwords, hashes, salts, or bearer tokens logged in audit files.

## 4. Operational & PDF Parity
- [x] PDF template layout 100% frozen (A4, 1-page, 2 permit blocks).
- [x] High-clarity QR code generation verified (plain-text payload for verification).
- [x] 9-point backup verification and 10-backup rotation operational.
- [x] 16-step atomic restore with safety rollback operational.
- [x] Phase 1–8 regression test suite 100% PASSing.
