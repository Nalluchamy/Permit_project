# Standard Operating Procedure: User Access Revocation (Staff Resignation)

## 1. Objective
To establish a secure, standardized process for revoking access to PermitMaster when a staff member resigns, terminates employment, or changes roles, ensuring zero unauthorized access while preserving complete historical audit trails and permit records.

## 2. Policy & Principles
* **Account Disabling vs. Deletion**: Accounts must NEVER be deleted from the database. Deleting accounts corrupts audit trails and historic record links. Disabling an account (`is_active = 0`) blocks authentication immediately while preserving full audit integrity.
* **Administrator-Only Action**: Access revocation must be executed by an active system Administrator.
* **Audit Trail Accountability**: Every status change is logged automatically to `audit_logs` with timestamp, acting administrator username, target user ID, and action description.

## 3. Step-by-Step Revocation Procedure

### Step 1: Access User Management Panel
1. Log in to PermitMaster with Administrator credentials.
2. Click the `👥 User Management` button on the Admin Dashboard toolbar.

### Step 2: Locate Staff Account
1. Use the search field to filter by the staff member's username.
2. Verify the target account row (ensure correct username and `staff` role).

### Step 3: Disable Account
1. Click to highlight the user row.
2. Click `🚫 Disable Account`.
3. Confirm the confirmation prompt (`Are you sure you want to disable account 'username'?`).
4. The account status indicator immediately updates to `Disabled`.

### Step 4: Verification
1. Attempt to log in with the disabled staff member's credentials.
2. Confirm the system denies access with the exact message: `"Account disabled. Contact Administrator."`.
3. Open `🛡 Audit Trail` to verify the `USER_DISABLED` audit record has been recorded.

## 4. Emergency Lockout Prevention
* The system enforces an automated check preventing the last active Administrator account from being disabled.
* If an Administrator attempts to disable the final active admin account, the operation is blocked with: `"Cannot disable the last active administrator account."`.
