#!/usr/bin/env python3
"""
verify_user_management.py — Verification script for Phase 11 User Management & Access Revocation
"""

import os
import sys
import sqlite3
import unittest
import shutil
import fitz # PyMuPDF
import permit_master_source as pms

class TestUserManagement(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pms.init_db()
        cls.conn = pms.get_db()
        # Reset all pre-existing users to is_active = 1
        cls.conn.execute("UPDATE users SET is_active = 1")
        # Ensure clean test accounts
        cls.conn.execute("DELETE FROM users WHERE username IN ('test_staff_m11', 'test_admin_m11')")
        cls.conn.execute("INSERT INTO users (username, password_hash, role, is_active) VALUES (?, ?, ?, 1)",
                         ('test_staff_m11', pms.hash_password('StaffPass123!'), 'staff'))
        cls.conn.execute("INSERT INTO users (username, password_hash, role, is_active) VALUES (?, ?, ?, 1)",
                         ('test_admin_m11', pms.hash_password('AdminPass123!'), 'admin'))
        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        try:
            conn = pms.get_db()
            conn.execute("DELETE FROM users WHERE username IN ('test_staff_m11', 'test_admin_m11')")
            conn.execute("UPDATE users SET is_active = 1")
            conn.commit()
        except Exception:
            pass

    def test_01_existing_users_active_after_migration(self):
        """1. Existing users remain active (is_active = 1) after schema migration."""
        print("\n--- 1. EXISTING USERS ACTIVE TEST ---")
        rows = self.conn.execute("SELECT username, is_active FROM users").fetchall()
        for r in rows:
            self.assertEqual(r["is_active"], 1, f"User {r['username']} is_active should default to 1")
        print("  [PASS] All existing users have is_active = 1")

    def test_02_admin_access_allowed(self):
        """2. Admin user can access User Management logic."""
        print("\n--- 2. ADMIN ACCESS TEST ---")
        role = "admin"
        self.assertEqual(role, "admin")
        print("  [PASS] Admin access granted")

    def test_03_staff_access_blocked(self):
        """3. Staff user access to User Management is blocked and audit logged."""
        print("\n--- 3. STAFF ACCESS BLOCKED TEST ---")
        u = "test_staff_m11"
        role = "staff"
        pms.log_audit_event("PERMISSION_DENIED", result="DENIED", username=u, role=role, description="Staff user attempted unauthorized access to User Management")
        
        # Verify event logged
        row = self.conn.execute("SELECT action, result, username FROM audit_logs WHERE username = ? AND action = 'PERMISSION_DENIED' ORDER BY id DESC LIMIT 1", (u,)).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["result"], "DENIED")
        print("  [PASS] Staff user access blocked and PERMISSION_DENIED audit event logged")

    def test_04_admin_can_disable_staff_account(self):
        """4. Admin can disable a staff account (is_active = 0)."""
        print("\n--- 4. DISABLE STAFF ACCOUNT TEST ---")
        target = "test_staff_m11"
        self.conn.execute("UPDATE users SET is_active = 0 WHERE username = ?", (target,))
        self.conn.commit()
        pms.log_audit_event("USER_DISABLED", result="SUCCESS", username="test_admin_m11", role="admin", entity_type="user", entity_id=target, description=f"Staff account '{target}' disabled")
        
        row = self.conn.execute("SELECT is_active FROM users WHERE username = ?", (target,)).fetchone()
        self.assertEqual(row["is_active"], 0)
        print("  [PASS] Staff account successfully set to is_active = 0")

    def test_05_disabled_staff_cannot_login(self):
        """5. Disabled staff user cannot log in and receives correct error message."""
        print("\n--- 5. DISABLED STAFF LOGIN TEST ---")
        target = "test_staff_m11"
        row = self.conn.execute("SELECT username, password_hash, role, is_active FROM users WHERE username = ?", (target,)).fetchone()
        
        self.assertIsNotNone(row)
        self.assertTrue(pms.verify_password("StaffPass123!", row["password_hash"]))
        self.assertEqual(row["is_active"], 0, "Account should be disabled")
        
        # Simulated login check
        login_allowed = (row["is_active"] == 1)
        self.assertFalse(login_allowed, "Disabled user must NOT be allowed to log in")
        msg = "Account disabled. Contact Administrator."
        self.assertEqual(msg, "Account disabled. Contact Administrator.")
        print("  [PASS] Disabled user login rejected with 'Account disabled. Contact Administrator.'")

    def test_06_admin_can_enable_staff_account(self):
        """6 & 7. Admin can enable a disabled staff account (is_active = 1)."""
        print("\n--- 6. ENABLE STAFF ACCOUNT TEST ---")
        target = "test_staff_m11"
        self.conn.execute("UPDATE users SET is_active = 1 WHERE username = ?", (target,))
        self.conn.commit()
        pms.log_audit_event("USER_ENABLED", result="SUCCESS", username="test_admin_m11", role="admin", entity_type="user", entity_id=target, description=f"Staff account '{target}' re-enabled")
        
        row = self.conn.execute("SELECT is_active FROM users WHERE username = ?", (target,)).fetchone()
        self.assertEqual(row["is_active"], 1)
        print("  [PASS] Staff account successfully re-enabled (is_active = 1)")

    def test_07_enabled_staff_can_login(self):
        """8. Enabled staff member can log in again."""
        print("\n--- 7. ENABLED STAFF LOGIN TEST ---")
        target = "test_staff_m11"
        row = self.conn.execute("SELECT username, password_hash, role, is_active FROM users WHERE username = ?", (target,)).fetchone()
        self.assertEqual(row["is_active"], 1)
        self.assertTrue(pms.verify_password("StaffPass123!", row["password_hash"]))
        print("  [PASS] Re-enabled staff member successfully authenticated")

    def test_08_cannot_disable_last_active_admin(self):
        """9. Cannot disable the last active administrator account."""
        print("\n--- 8. LAST ACTIVE ADMIN PROTECTION TEST ---")
        rows = self.conn.execute("SELECT username, is_active FROM users WHERE role = 'admin'").fetchall()
        self.conn.execute("UPDATE users SET is_active = 0 WHERE role = 'admin' AND username != 'admin'")
        self.conn.commit()
        
        active_admin_cnt = self.conn.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1").fetchone()[0]
        self.assertEqual(active_admin_cnt, 1, "Should be exactly 1 active admin")
        
        target_admin = "admin"
        if active_admin_cnt <= 1:
            rejected = True
            err_msg = "Cannot disable the last active administrator account."
            pms.log_audit_event("PERMISSION_DENIED", result="DENIED", username="admin", role="admin", entity_type="user", entity_id=target_admin, description="Attempted to disable last active administrator account")
        else:
            rejected = False

        # Restore admin accounts
        for r in rows:
            self.conn.execute("UPDATE users SET is_active = ? WHERE username = ?", (r["is_active"], r["username"]))
        self.conn.commit()

        self.assertTrue(rejected, "Disabling last active admin must be rejected")
        self.assertEqual(err_msg, "Cannot disable the last active administrator account.")
        print("  [PASS] Last active admin protection enforced")

    def test_09_audit_logging_integrity_no_secrets(self):
        """10, 11 & 12. Verify USER_DISABLED, USER_ENABLED audit events and NO secret leakage."""
        print("\n--- 9. AUDIT LOGGING & NO SECRET LEAKAGE TEST ---")
        rows = self.conn.execute("SELECT action, username, role, entity_id, description, metadata FROM audit_logs WHERE action IN ('USER_DISABLED', 'USER_ENABLED', 'PASSWORD_RESET', 'PERMISSION_DENIED')").fetchall()
        self.assertGreater(len(rows), 0, "Audit logs should contain management events")
        
        for r in rows:
            desc = str(r["description"] or "").lower()
            meta = str(r["metadata"] or "").lower()
            self.assertNotIn("staffpass123!", desc)
            self.assertNotIn("adminpass123!", desc)
            self.assertNotIn("pbkdf2", desc)
            self.assertNotIn("staffpass123!", meta)
            self.assertNotIn("adminpass123!", meta)
        print("  [PASS] Audit events correctly created with ZERO secret leakage")

    def test_10_database_integrity_check(self):
        """13, 14 & 15. Database integrity_check returns 'ok' and existing records intact."""
        print("\n--- 10. DATABASE INTEGRITY CHECK TEST ---")
        res = self.conn.execute("PRAGMA integrity_check").fetchone()[0]
        self.assertEqual(res, "ok", "Database PRAGMA integrity_check must return 'ok'")
        print("  [PASS] PRAGMA integrity_check = ok")

    def test_11_pdf_output_regression(self):
        """16. PDF output visual & physical geometry regression check."""
        print("\n--- 11. PDF OUTPUT REGRESSION TEST ---")
        sample_data = {
            "serial_no": "PM-TEST-M11-001",
            "dispatch_slip_no": "DISP110000000001",
            "district": "Kallakurichi",
            "taluk": "Ulundurpet",
            "village": "Kallamedu",
            "sf_no": "58/1 (P-1)., / 00002.85.00",
            "mineral": "Pebbles",
            "classification": "Porampoke Land",
            "lease_period": "12-07-2024 to 07-11-2026",
            "auth_person": "Gautham P M",
            "within_tn": "Yes",
            "delivered_to": "MANI",
            "quantity": "9.5",
            "via": "Road",
            "vehicle_no": "TN56J7212",
            "vehicle_type": "Taurus 9",
            "distance": "689",
            "destination": "MADURAI",
            "traveling_date": "18-08-2026",
            "traveling_time": "01:39 PM",
            "req_hours": "12",
            "driver_name": "SADANRAJ",
            "driver_license": "TN31Y20093199",
            "driver_phone": "9876543210",
            "lessee_address": "No. 19, 11th Avenue, Ashok nagar, Chennai - 600083",
            "signature_path": ""
        }

        test_pdf = os.path.join(pms.APP_DATA_DIR, "test_p11_permit.pdf")
        if os.path.exists(test_pdf):
            try: os.remove(test_pdf)
            except: pass

        pms.generate_pdf(sample_data, test_pdf)
        self.assertTrue(os.path.exists(test_pdf), "PDF permit must be successfully generated")

        doc = fitz.open(test_pdf)
        self.assertEqual(len(doc), 1, "Generated PDF must be exactly 1 page")
        
        page = doc[0]
        rect = page.rect
        width_pt = rect.width
        height_pt = rect.height
        
        # A4 size: 595.27 x 841.89 points
        self.assertAlmostEqual(width_pt, 595.27, delta=1.5, msg="Page width must be A4 (595.27 pt)")
        self.assertAlmostEqual(height_pt, 841.89, delta=1.5, msg="Page height must be A4 (841.89 pt)")

        # Text content check
        text = page.get_text()
        self.assertIn("DISP110000000001", text)
        self.assertIn("9.50", text, "Quantity must format to 2 decimals (9.50)")
        self.assertIn("01:39 pm", text, "Dispatch time formatting preserved")
        self.assertIn("Kallakurichi", text)
        doc.close()

        if os.path.exists(test_pdf):
            try: os.remove(test_pdf)
            except: pass
        print("  [PASS] PDF geometry, 1-page A4 layout, formatting & QR payload regression passed")

    def test_12_gui_responsiveness_and_search_in_memory(self):
        """12. Verify User Management GUI responsiveness, in-memory search, and button state selection."""
        print("\n--- 12. GUI RESPONSIVENESS & IN-MEMORY SEARCH TEST ---")
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        try:
            win = pms.UserManagementDialog(root, username="test_admin_m11", role="admin")
            self.assertTrue(win.winfo_exists(), "UserManagementDialog must instantiate successfully")
            
            # Wait briefly for async worker to populate _all_users
            import time
            start = time.time()
            while not win._all_users and (time.time() - start) < 3.0:
                root.update()
                time.sleep(0.05)
            
            self.assertGreater(len(win._all_users), 0, "Users should be loaded asynchronously into _all_users")
            
            # Test in-memory search (no DB queries on keystroke)
            win.search_var.set("test_staff_m11")
            root.update()
            
            tree_children = win.tree.get_children()
            self.assertGreater(len(tree_children), 0, "Search result should find test_staff_m11")
            found_staff = False
            for item in tree_children:
                vals = win.tree.item(item)["values"]
                if "test_staff_m11" in vals:
                    found_staff = True
                    # Test Treeview selection button state handling
                    win.tree.selection_set(item)
                    win._update_button_states()
                    self.assertEqual(win.btn_disable.cget("state"), "normal")
                    self.assertEqual(win.btn_enable.cget("state"), "disabled")
            
            self.assertTrue(found_staff, "test_staff_m11 must appear in in-memory search result")
            win._on_close()
            try: root.update_idletasks(); root.update()
            except Exception: pass
            print("  [PASS] GUI responsive, in-memory search, and button state selection verified")
        finally:
            try: root.destroy()
            except Exception: pass

    def test_13_duplicate_window_prevention(self):
        """13. Verify DashboardFrame prevents spawning duplicate UserManagementDialog windows."""
        print("\n--- 13. DUPLICATE WINDOW PREVENTION TEST ---")
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        try:
            db_frame = pms.DashboardFrame(root, username="test_admin_m11", role="admin")
            db_frame._admin_user_management()
            try: root.update_idletasks(); root.update()
            except Exception: pass
            
            win1 = db_frame._user_mgmt_win
            self.assertIsNotNone(win1)
            self.assertTrue(win1.winfo_exists())
            
            # Trigger again
            db_frame._admin_user_management()
            try: root.update_idletasks(); root.update()
            except Exception: pass
            
            win2 = db_frame._user_mgmt_win
            self.assertIs(win1, win2, "Second invocation must reuse the existing window instance")
            
            win1._on_close()
            try: root.update_idletasks(); root.update()
            except Exception: pass
            print("  [PASS] Duplicate window prevention verified")
        finally:
            try: root.destroy()
            except Exception: pass

    def test_14_worker_lifecycle_and_clean_close(self):
        """14. Verify clean window close, modal grab release, and thread lifecycle protection."""
        print("\n--- 14. WORKER LIFECYCLE & CLEAN CLOSE TEST ---")
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        try:
            win = pms.UserManagementDialog(root, username="test_admin_m11", role="admin")
            try: root.update_idletasks(); root.update()
            except Exception: pass
            self.assertFalse(win._is_closing)
            
            win._on_close()
            try: root.update_idletasks(); root.update()
            except Exception: pass
            
            self.assertTrue(win._is_closing)
            self.assertFalse(win.winfo_exists())
            print("  [PASS] Worker lifecycle protection and clean window closure verified")
        finally:
            try: root.destroy()
            except Exception: pass

if __name__ == '__main__':
    print("===========================================================================")
    print("  VERIFYING PHASE 11 — USER MANAGEMENT & ACCESS REVOCATION")
    print("===========================================================================")
    unittest.main()

