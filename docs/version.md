# PermitMaster Release Metadata & Version Specification

**Application Name:** PermitMaster (TN Mining Dispatch Permit Generator)  
**Version:** v1.0.0 (Production Release Candidate)  
**Release Date:** August 18, 2026  
**Build System:** PyInstaller 6.x / Python 3.12 (64-bit)  
**Database Schema Version:** 1.2 (Partial Unique Indexes on `serial_no` & `dispatch_slip`)  
**Minimum Operating System:** Microsoft Windows 10 (Version 1809+) / Windows 11 (64-bit)

---

## 1. Version Availability

The application version `PermitMaster v1.0.0` is accessible via:
1. **GUI Window Title:** Displays `Permit Master v1.0.0 — TN Mining Dispatch System`
2. **About / Metadata Dialog:** Accessible via Help/About menu
3. **Installer Metadata:** Inno Setup version identifier `v1.0.0`
4. **Release Metadata File:** `docs/version.md`

> [!NOTE]
> Per system guidelines, the version string is strictly omitted from `pdf_generator/template.html` to guarantee 100% frozen PDF template compliance.

---

## 2. Release Highlights & Features

- **Phase 1–2 Baseline Parity:** Pixel-perfect A4 permit PDF generation matching Tamil Nadu Mining Dispatch standards.
- **Phase 3 Security & RBAC:** PBKDF2-HMAC-SHA256 password hashing (600,000 iterations), role-based access control (Admin / Staff), input sanitization, and SQL parameterization.
- **Phase 4 Validation:** Strict client-side and server-side validation for dates (DD-MM-YYYY), times, non-negative numerical quantities, and phone numbers.
- **Phase 5 Database Integrity:** SQLite WAL mode with partial unique indexes (`idx_permits_serial_unique`, `idx_permits_dispatch_unique`), preventing duplicate permit creation.
- **Phase 6 Backup & Recovery Engine:** Automated, verified SQLite backup generation with 10-file rotation, 9-point integrity checking, and atomic 16-step rollback recovery.
- **Phase 7 Comprehensive Audit Trail:** Parameterized logging of 24 critical operational events with sensitive token stripping and Admin Log Viewer.
- **Phase 8 Failure Recovery & Stress Resilience:** Concurrency safety under high load, corrupted database auto-isolation, and disk-full failure protection.
- **Phase 9 Production Installer & Local AppData Isolation:** Standalone Windows execution with `%LOCALAPPDATA%\PermitMaster\` directory separation.

---

## 3. System Requirements

- **Operating System:** Windows 10 / Windows 11 (64-bit)
- **Processor:** 1.6 GHz dual-core or faster x86-64 processor
- **Memory (RAM):** 2 GB minimum (4 GB recommended)
- **Disk Space:** 250 MB free space (Application binaries + local SQLite database storage)
- **PDF Renderer Support:** Built-in Microsoft Edge (or Google Chrome) installed on Windows

---

## 4. Known Operational Limitations

1. **Headless Browser Requirement:** PDF permit generation utilizes Microsoft Edge (`msedge.exe`) or Google Chrome in headless mode. Microsoft Edge is pre-installed on all Windows 10/11 installations.
2. **File Locking during Edge Preview:** If a generated PDF is currently open in Microsoft Edge or an external viewer, regeneration of the same file path requires closing the open tab first.
3. **Physical Hardware Scannability:** QR code scannability depends on printer toner contrast and physical scanner focal depth. Plain-text CSV payload URL structure ensures maximum scannability even on low-resolution prints.
