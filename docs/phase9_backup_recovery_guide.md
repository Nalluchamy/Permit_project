# PermitMaster — Backup & Disaster Recovery Guide (v1.0.0)

---

## 1. Automated 9-Point Verification System

Every backup created by PermitMaster undergoes 9 automated integrity checks before being accepted into `%LOCALAPPDATA%\PermitMaster\backups\`:

1. **File Existence Check:** Confirms backup file exists on disk.
2. **Non-Zero Size Check:** Rejects 0-byte or truncated files.
3. **SQLite Header Verification:** Validates `SQLite format 3\0` magic header bytes.
4. **Pragma Integrity Check:** Runs `PRAGMA integrity_check` returning `ok`.
5. **Permits Table Check:** Confirms presence of `permits` table.
6. **Users Table Check:** Confirms presence of `users` table.
7. **Permits Column Schema Check:** Validates `serial_no`, `vehicle_no`, `dispatch_slip` columns.
8. **Users Column Schema Check:** Validates `username`, `password_hash`, `role` columns.
9. **Record Count Parity Check:** Ensures permit record count in backup matches active database count.

---

## 2. Backup Rotation Policy

- **Location:** `%LOCALAPPDATA%\PermitMaster\backups\`
- **Retention Limit:** 10 verified backups.
- **Rotation Rule:** When an 11th verified backup is generated, the oldest verified backup is automatically purged. The active database and the most recent backup are **never deleted**.

---

## 3. Disaster Recovery & 16-Step Atomic Restore

If database corruption occurs or data must be restored to a previous state:

1. Log in as an **Admin**.
2. Open **Database Management** $\rightarrow$ **Restore Backup**.
3. Select the desired `.db` file from `%LOCALAPPDATA%\PermitMaster\backups\`.
4. Click **Restore**.
5. **Execution Sequence:**
   - **Step 1:** Verify selected backup file against 9-point criteria.
   - **Step 2:** Create safety backup of active database (`permits_safety_before_restore.db`).
   - **Step 3:** Use SQLite Backup API to copy backup into active `permits.db`.
   - **Step 4:** Execute post-restore integrity check on `permits.db`.
   - **Step 5 (Rollback Protection):** If post-restore check fails, the engine automatically rolls back to the pre-restore safety backup, preserving system operational state.
