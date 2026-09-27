# Phase 8 — Baseline Inventory Document

**System Name**: PermitMaster  
**Date**: 2026-08-17  
**Environment**: Windows Desktop Application (CustomTkinter + SQLite + Headless Edge/Chrome)  

---

## 1. Project Component Inventory

### Core Components
| Component | Path / File | Description / Specifications |
|---|---|---|
| Main Source Application | `permit_master_source.py` | 1,871 lines. Contains UI, DB layer, validation, auth, backup/restore, PDF engine, audit log viewer. |
| SQLite Database | `%LOCALAPPDATA%\PermitMaster\permits.db` | WAL mode, synchronous NORMAL, 3 primary tables (`permits`, `users`, `audit_logs`). |
| PDF Generator Engine | `generate_pdf()` in `permit_master_source.py` | Headless Edge/Chrome process bridge with temp HTML buffer & timeout handling. |
| HTML Permit Template | `pdf_generator/template.html` | 16.8 KB. **FROZEN**. Pixel-perfect twin-block A4 layout with QR and signature. |
| PyInstaller Spec File | `PermitMaster.spec` | PyInstaller bundle spec for standalone Windows executable build. |
| Executable Build Script | `build_exe.bat` | Automated compilation script targeting standalone deployment. |
| Backup Subsystem | `create_backup()`, `verify_backup()`, `rotate_backups()` | 9-point verification check, max 10-backup rotation retention policy. |
| Restore Subsystem | `restore_backup()` | 16-step safe replacement with automatic rollback to pre-restore safety snapshot. |
| Security & Auth | `hash_password()`, `verify_password()`, `LoginFrame` | PBKDF2-HMAC-SHA256 (600,000 iterations), constant-time comparison, RBAC enforcement. |
| Input Validation | `validate_permit_data()` | Centralized input bounds, date (`DD-MM-YYYY`), time, phone, non-negative numbers. |
| Audit Trail Subsystem | `log_audit_event()`, `AuditViewerFrame` | Parameterized audit insertion, zero secret leakage filter, indexed query engine. |

### Existing Phase 1–7 Test Suites
1. `test_phase3_security.py` — PBKDF2 authentication, RBAC, password security.
2. `test_phase4_data_validation.py` — Centralized input bounds and format verification.
3. `test_phase5_database_integrity.py` — Schema constraints, index verification, duplicate handling.
4. `test_phase6_backup_recovery.py` — Backup verification, rotation, restore, rollback.
5. `test_phase7_audit.py` — 24 audit event inventory, zero secret leakage, pagination, query optimization.

---

## 2. Baseline Database Metrics

Prior to running Phase 8 failure, reliability, and stress tests:

| Metric | Count / State | Notes |
|---|---|---|
| `permits` Table Record Count | 47 | Active permit records in production DB |
| `users` Table Record Count | 1 | Admin user account registered |
| `audit_logs` Table Record Count | 50,034 | Audit log entries (includes 50k benchmark load) |
| Database Journal Mode | `WAL` | Write-Ahead Logging active |
| Database Synchronous Mode | `NORMAL` | Optimized write safety |
| Baseline Verified Backup | `permits_2026-08-17_22-46-57_phase8_baseline.db` | Verified 9-point pre-testing backup snapshot |

---

## 3. Standard Application Lifecycle Workflow Baseline

1. **Startup**: `init_db()` checks schema, indexes, duplicates, applies WAL mode.
2. **Authentication**: `LoginFrame` verifies username/password via PBKDF2-HMAC-SHA256.
3. **Permit Operations**:
   - `Create`: Validated by `validate_permit_data()`, written inside single transaction with `PERMIT_CREATED` audit event.
   - `Edit`: Admin-only modification, written with `PERMIT_UPDATED` audit event.
   - `Delete`: Admin-only deletion, written with `PERMIT_DELETED` audit event.
   - `Search`: Real-time query with parameterized `LIKE` matching on serial, vehicle, or dispatch slip.
4. **PDF Generation**: Generates Level M high-density QR code (Netlify URL payload), embeds AD/DD signature image (with fallback), fills dynamic HTML template, invokes headless Edge/Chrome, writes output PDF.
5. **Backup & Restore**: Admin-triggered verified backup generation & 16-step safe restore with auto-rollback.
