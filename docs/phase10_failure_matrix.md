# PermitMaster — Phase 10 Failure & Risk Analysis Matrix

---

## Failure Mode & Mitigation Analysis

| Risk / Failure Scenario | Trigger Condition | Severity | System Behavior & Mitigation | Status |
| :--- | :--- | :---: | :--- | :---: |
| **Corrupted Backup File** | Restoring zero-byte or corrupt SQLite file | High | Restore engine rejects file during 9-point verification; auto-rollback restores pre-restore safety DB | **PASS** |
| **Locked Output PDF** | PDF permit open in Edge tab during regeneration | Medium | Trapped via `PermissionError`; displays user guidance asking user to close Edge tab | **PASS** |
| **Program Files Permission Error** | Standard user launching app | High | Binary isolated in Program Files while all writes occur in `%LOCALAPPDATA%\PermitMaster\` | **PASS** |
| **Duplicate Serial Number** | Staff inserting existing permit serial | Medium | Rejected via partial unique index `idx_permits_serial_unique` with validation dialog | **PASS** |
| **Database Corruption** | Disk failure or power loss | High | SQLite WAL mode protects transactions; verified backup restored via 16-step engine | **PASS** |
