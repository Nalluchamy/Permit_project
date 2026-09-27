# PermitMaster — Administrator Guide (v1.0.0)

**Target Audience:** System Administrators & IT Support  
**System:** PermitMaster TN Mining Dispatch System

---

## 1. Role-Based Access Control (RBAC) Overview

PermitMaster enforces strict dual-role authorization:

| Action / Feature | Admin Role | Staff Role |
| :--- | :---: | :---: |
| Create / Search / View Permits | Yes | Yes |
| Generate & Print PDFs | Yes | Yes |
| User Management (Create/Edit/Delete Users) | **Yes** | No (Blocked) |
| Database Backup Generation | **Yes** | No (Blocked) |
| Database Restore Execution | **Yes** | No (Blocked) |
| Audit Log Viewer & Export | **Yes** | No (Blocked) |
| Signature File Configuration | **Yes** | No (Blocked) |

---

## 2. User Management

1. Log in with an **Admin** account.
2. Navigate to the **User Management** tab.
3. **Create Staff User:**
   - Click **Add User**.
   - Enter Username, Password, and select Role = `staff`.
   - Click **Save**. The password will be hashed with PBKDF2 (600,000 iterations).
4. **Reset User Password:**
   - Select user from list, enter new password, click **Update Password**.
5. **Delete User:**
   - Select user from list and click **Delete User**. (The system prevents deleting the last remaining Admin account).

---

## 3. Database Backup & Maintenance

1. Go to **Database Management** tab.
2. Click **Create Verified Backup**.
3. The system generates an immutable, timestamped backup file in `%LOCALAPPDATA%\PermitMaster\backups\` (e.g. `permits_2026-08-18_10-00-00.db`).
4. The system executes automatic **9-Point Verification** on the backup.
5. Up to 10 verified backups are retained automatically (older backups rotate out).

---

## 4. Viewing Audit Logs

1. Go to **Audit Log Viewer** tab.
2. Filter logs by Action (e.g. `PERMIT_CREATE`, `USER_LOGIN_FAILED`, `DATABASE_RESTORE`), Username, or Date Range.
3. All audit descriptions automatically strip sensitive tokens and passwords.
4. Export audit logs to CSV for official compliance reporting.
