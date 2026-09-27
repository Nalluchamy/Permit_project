# PermitMaster — Application Upgrade & Migration Guide (v1.0.0)

---

## 1. Upgrading PermitMaster (Simulated v1.0 $\rightarrow$ v1.1)

PermitMaster is designed for seamless in-place updates. Upgrading the application **never deletes** the user's database or configuration.

### Upgrade Procedure
1. Obtain the new version installer (`PermitMaster_v1.1.0_Setup.exe`) or executable (`PermitMaster.exe`).
2. Close any running instances of `PermitMaster.exe`.
3. Run the installer or replace `C:\Program Files\PermitMaster\PermitMaster.exe`.
4. Launch the updated application.

---

## 2. Dynamic Schema Migration Mechanics

When the updated application launches:
1. It connects to existing database at `%LOCALAPPDATA%\PermitMaster\permits.db`.
2. It executes `init_db()`.
3. `init_db()` checks for existing non-empty duplicate `serial_no` or `dispatch_slip` records.
4. It automatically creates a **Pre-Migration Verified Backup** in `%LOCALAPPDATA%\PermitMaster\backups\` (tagged `pre_migration`).
5. It applies new table columns or indexes (such as `idx_permits_serial_unique` and `idx_permits_dispatch_unique`).
6. All existing permits, users, password hashes, and audit logs remain intact.
