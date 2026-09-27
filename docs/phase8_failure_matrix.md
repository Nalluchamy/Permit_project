# Phase 8 — System Failure & Recovery Matrix

**System**: PermitMaster  
**Date**: 2026-08-17  
**Scope**: Failure modes, recovery mechanisms, data safety guarantees, and automated verification status.  

---

## Failure Matrix Overview

| Failure Mode / Scenario | Component Affected | Trigger Condition | Expected System Behavior | Observed System Behavior | Recovery Mechanism | Acceptance Status |
|---|---|---|---|---|---|---|
| **Abnormal Process Termination / Power Loss** | SQLite Database Engine | Sudden process exit or power loss during active session | WAL journal recovery on startup; zero database corruption | `PRAGMA integrity_check` returns `ok`; committed records intact | Automatic WAL recovery on `init_db()` startup | **RESOLVED / PASS** |
| **Database Lock Contention** | Database & UI Layer | Concurrent write operations from multiple threads / users | WAL mode concurrency prevents locking crashes; retries executed | 10 concurrent writers inserted without error; write locks managed | WAL mode + 30.0s lock timeout & busy handlers | **RESOLVED / PASS** |
| **Duplicate Serial / Dispatch Write** | Permit Manager | Saving permit with existing serial or non-empty dispatch slip | Rejected by partial unique index constraint; UI shows clear error | `sqlite3.IntegrityError` caught; user alerted; zero duplicate row | UI validation + Database index enforcement | **RESOLVED / PASS** |
| **Transaction Mid-Operation Failure** | Transaction Manager | Exception thrown after DB insert but before audit logging | Complete transactional rollback; zero partial database state | Database state restored; zero orphaned permit rows | Single `with get_db()` connection context block | **RESOLVED / PASS** |
| **Unwritable Backup Destination** | Backup Subsystem | Read-only target directory or invalid filesystem path | Backup operation fails gracefully; active database unaffected | `create_backup()` returns `(False, msg)`; active DB untouched | Pre-write path verification & 9-point audit check | **RESOLVED / PASS** |
| **Corrupted Backup File Restore** | Restore Subsystem | Admin attempts to restore a zero-byte or text file as backup | 9-point verification rejects backup; 16-step rollback triggers | Restore blocked; pre-restore safety backup restores active DB | 16-step restore pipeline with auto-rollback | **RESOLVED / PASS** |
| **Missing Custom Signature File** | PDF Generator | `signature_path` points to missing or unreadable file | Fallback to default AD/DD signature; permit PDF generated | System defaults to bundled `ad_dd_signature.png` | Resource resolver fallback mechanism | **RESOLVED / PASS** |
| **HTML Injection Attack Payload** | Input Validator & PDF Generator | User input contains `<script>` or HTML formatting tags | HTML special characters escaped (`&lt;script&gt;`); PDF safe | Rendered cleanly as literal text; zero script execution | `html.escape()` sanitization in `generate_pdf()` | **RESOLVED / PASS** |
| **Headless Browser Timeout / Output Lock** | PDF Generator | Edge/Chrome process hangs or PDF destination locked | Subprocess timeout (60s); temporary buffer cleaned up | Timeout caught; temp HTML buffer deleted; error reported | Subprocess timeout handling + temp buffer cleanup | **RESOLVED / PASS** |
| **Headless Browser UTF-8 Output Decoding Error** | Subprocess Bridge | Edge/Chrome outputs UTF-8 log messages on Windows `cp1252` | Browser output decoded safely without raising `UnicodeDecodeError` | `encoding="utf-8", errors="replace"` decodes logs safely | Explicit subprocess text encoding parameters | **RESOLVED / PASS** |
| **Rapid Double-Click Save** | UI Event Handler | User rapidly double-clicks "Save Permit" button | First request processes; second request blocked by index | Database unique index rejects second insert cleanly | Backend unique constraints + UI button debouncing | **RESOLVED / PASS** |
| **Attempted Logging of Plaintext Passwords** | Audit Trail Subsystem | Failed authentication or audit event includes user password | Sensitive credentials stripped before database insertion | Passwords, hashes, and bearer tokens replaced with `[REDACTED]` | Centralized secret filter in `log_audit_event()` | **RESOLVED / PASS** |
| **High-Volume Data Load (5,000 Records)** | Database Query Engine | Querying permits table populated with 5,000 records | Instant response using indexed query execution plans | Indexed search latency = 0.50 ms; zero UI freezing | Partial unique & indexed columns (`idx_permits_vehicle`) | **RESOLVED / PASS** |
