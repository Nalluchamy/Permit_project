# Phase 8 — Operational Recovery Procedures & Administration Guide

**System**: PermitMaster  
**Target Audience**: System Administrators, Operators, Support Engineers  
**Date**: 2026-08-17  

---

## Standard Operating Procedures (SOP)

### SOP-01: Application Restart & Crash Recovery
1. **Symptom**: Application closes unexpectedly due to power failure or process termination.
2. **Action**: Re-launch `PermitMaster.exe` or `python permit_master_source.py`.
3. **Internal Mechanics**:
   - `init_db()` automatically opens the SQLite database at `%LOCALAPPDATA%\PermitMaster\permits.db`.
   - SQLite Write-Ahead Logging (WAL) automatically replays committed transactions from `permits.db-wal` and discards uncommitted partial transactions.
   - Application verifies tables and partial unique indexes (`idx_permits_serial_no`, `idx_permits_dispatch_slip`).
4. **Verification**: Check application log at `%LOCALAPPDATA%\PermitMaster\app.log` for `Application initialized successfully`.

---

### SOP-02: Creating a Verified Manual Database Backup
1. **Symptom**: Admin requires an on-demand database backup before performing batch modifications or system maintenance.
2. **Action**:
   - Log into PermitMaster with `admin` credentials.
   - Open Admin Dashboard -> Backup System -> Click **"Create Backup Now"**.
3. **Internal Mechanics**:
   - System invokes `create_backup(tag="manual")`.
   - Performs `PRAGMA wal_checkpoint(TRUNCATE)` to flush WAL pages to the main file.
   - Copies database using SQLite Online Backup API.
   - Executes 9-point verification check on backup file.
   - Rotates backups, retaining the 10 newest verified snapshots in `%LOCALAPPDATA%\PermitMaster\backups`.
   - Logs `DATABASE_BACKUP` audit event.

---

### SOP-03: Restoring Database from a Verified Backup Snapshot
1. **Symptom**: Database corruption or invalid operator entry requires reverting to a previous known-good backup state.
2. **Action**:
   - Log in as `admin`.
   - Navigate to Admin Dashboard -> Restore System.
   - Select the target backup snapshot file (e.g., `permits_2026-08-17_22-46-57_phase8_baseline.db`).
   - Click **"Restore Selected Backup"** and confirm prompt.
3. **Internal Mechanics**:
   - System verifies selected backup against 9 criteria via `verify_backup()`.
   - Creates a safety backup of active database (`permits_..._safety_before_restore.db`).
   - Replaces active database contents using SQLite Online Backup API.
   - Verifies restored database state post-restore.
   - **Automatic Rollback**: If post-restore verification fails, system automatically restores the pre-restore safety backup, preserving 100% of operational data.
   - Logs `DATABASE_RESTORE` audit event.

---

### SOP-04: Resolving PDF Generator & Headless Browser Errors
1. **Symptom**: Permit PDF fails to render or headless Edge/Chrome returns error.
2. **Diagnosis & Action**:
   - Verify Edge or Chrome is installed on host system (`msedge.exe` or `chrome.exe`).
   - Ensure target PDF directory (e.g. `Desktop` or `Downloads`) is writable and not locked by an external PDF viewer.
   - Check `%LOCALAPPDATA%\PermitMaster\app.log` for timeout or path errors.
   - System automatically falls back from `--headless=new` to legacy `--headless` mode.
   - Verify `pdf_generator/template.html` has not been altered or deleted.

---

### SOP-05: Emergency Manual Database Restoration (Headless / Recovery)
If the GUI is inaccessible and an emergency database restore is required:
1. Close all running `PermitMaster` processes.
2. Open PowerShell or Command Prompt.
3. Run emergency restore command:
   ```cmd
   python -c "import permit_master_source as pm; ok, msg = pm.restore_backup('C:\\Users\\<USER>\\AppData\\Local\\PermitMaster\\backups\\<TARGET_BACKUP>.db'); print(ok, msg)"
   ```
4. Verify output returns `True Database restored successfully.`
5. Start PermitMaster application normally.
