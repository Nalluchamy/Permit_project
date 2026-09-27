# PermitMaster — Admin User Management Guide

## 1. Overview
The Admin User Management feature provides system administrators with full control over user accounts and access lifecycle in PermitMaster. Administrators can create new accounts, manage staff account statuses (Active / Disabled), and perform secure password resets directly from the graphical user interface.

## 2. Access Requirements
* **Role Requirement**: Administrator (`admin`)
* **Access Point**: Main Admin Dashboard -> `👥 User Management` button
* **RBAC Enforcement**: If a Non-Admin (Staff) user attempts to access User Management via hotkey or script, the request is blocked and logged as a `PERMISSION_DENIED` security audit event.

## 3. Account Actions & Features

### 3.1 Viewing Users
* Displays real-time list of all system accounts with columns: `ID`, `Username`, `Role`, `Status` (`Active` / `Disabled`), and `Created At`.
* Real-time search filter allows quick lookup by username.

### 3.2 Creating New Accounts
1. Click `➕ Add New User`.
2. Enter the new `Username`.
3. Select `Role` (`staff` or `admin`).
4. Enter `Password` and `Confirm Password`.
5. Passwords are salted using `os.urandom(16)` and hashed using PBKDF2-HMAC-SHA256 (100,000 iterations). Plaintext passwords are never stored or logged.

### 3.3 Disabling / Enabling Accounts (Staff Resignation Handling)
1. Select a user row from the table.
2. Click `🚫 Disable Account` to revoke access immediately upon staff resignation or role change.
3. Click `✅ Enable Account` to reactivate an account if needed.
4. **Safety Rule**: The system protects against administrative lockout. The last active Administrator account cannot be disabled.

### 3.4 Resetting Passwords
1. Select a user row from the table.
2. Click `🔑 Reset Password`.
3. Enter and confirm the new password.
4. The system updates the hashed password in `users` and logs a `PASSWORD_RESET` audit event without recording sensitive data.

## 4. Audit Logging Integration
All User Management actions generate tamper-resistant audit trail entries in SQLite with transaction safety:
* `USER_CREATED`: Created new user account
* `USER_DISABLED`: Disabled staff account
* `USER_ENABLED`: Re-enabled staff account
* `PASSWORD_RESET`: Administrative password reset
* `PERMISSION_DENIED`: Unauthorized attempt by non-admin user
