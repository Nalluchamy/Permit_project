"""
Permit Master — TN Mining Dispatch Permit Generator
Professional Light UI + Login System
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
from datetime import datetime, timedelta
import sqlite3
import os
import sys
import tempfile
import shutil
import secrets
import base64
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import quote, urlencode, unquote

# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import mm
# from reportlab.pdfgen import canvas as rl_canvas
# from reportlab.platypus import Table, TableStyle, Paragraph
# from reportlab.lib.styles import ParagraphStyle
import qrcode
import subprocess
import json

# ══════════════════════════════════════════════════════════════════════════════
#  APPEARANCE & THEME
# ══════════════════════════════════════════════════════════════════════════════

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Light Theme Tokens (Dashboard)
BG_MAIN       = "#F8FAFC"
CARD_BG       = "#FFFFFF"
CARD_BORDER   = "#E2E8F0"
HEADER_BG     = "#1E293B"
HEADER_FG     = "#FFFFFF"
ACCENT        = "#2563EB"
ACCENT_HOVER  = "#1D4ED8"
TEXT_PRIMARY   = "#1E293B"
TEXT_SECONDARY = "#64748B"
TEXT_MUTED     = "#94A3B8"
INPUT_BG      = "#FFFFFF"
INPUT_BORDER  = "#CBD5E1"
SUCCESS       = "#16A34A"
DANGER        = "#DC2626"
WARNING       = "#D97706"
INFO          = "#0284C7"
TABLE_ROW_1   = "#FFFFFF"
TABLE_ROW_2   = "#F1F5F9"
TABLE_SELECT  = "#DBEAFE"

LAST_SIGNATURE_PATH = ""

# Light Theme Tokens (Login)
LOGIN_BG        = "#F1F5F9" # Light gray
LOGIN_CARD      = "#FFFFFF" # Pure white
LOGIN_ACCENT    = "#F97316" # Vibrant Orange
LOGIN_HOVER     = "#EA580C" # Darker Orange
LOGIN_TEXT      = "#0F172A" # Slate 900
LOGIN_SUBTEXT   = "#64748B" # Slate 500
LOGIN_BORDER    = "#E2E8F0" # Slate 200
LOGIN_INPUT_BG  = "#F8FAFC" # Slate 50

import logging
import hashlib
import secrets
import re

# ══════════════════════════════════════════════════════════════════════════════
#  SECURE PASSWORD HASHING (PBKDF2-HMAC-SHA256)
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_HASH_ITERATIONS = 600000

def hash_password(password: str, salt: str = None, iterations: int = DEFAULT_HASH_ITERATIONS) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with salt and configurable iterations.
    Stored Format: pbkdf2:sha256:<iterations>$<salt_hex>$<hash_hex>
    """
    if not salt:
        salt = secrets.token_hex(16)
    hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
    return f"pbkdf2:sha256:{iterations}${salt}${hash_bytes.hex()}"

def verify_password(password: str, stored_hash_str: str) -> bool:
    """Verifies a plaintext password against a stored PBKDF2 hash string using constant-time comparison."""
    if not stored_hash_str or not stored_hash_str.startswith("pbkdf2:sha256:"):
        return False
    try:
        parts = stored_hash_str.split("$")
        if len(parts) != 3:
            return False
        prefix, salt, expected_hash = parts
        iterations = int(prefix.split(":")[-1])
        computed_hash_str = hash_password(password, salt=salt, iterations=iterations)
        computed_hash = computed_hash_str.split("$")[-1]
        return secrets.compare_digest(computed_hash, expected_hash)
    except Exception as e:
        logging.error("Password verification error", exc_info=True)
        return False

# ══════════════════════════════════════════════════════════════════════════════
#  DATABASE & RESOURCE PATHS
# ══════════════════════════════════════════════════════════════════════════════

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def get_app_data_dir():
    """Get writable user application data directory under %LOCALAPPDATA%\\PermitMaster."""
    base_data_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    app_dir = os.path.join(base_data_dir, 'PermitMaster')
    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(os.path.join(app_dir, 'logs'), exist_ok=True)
    os.makedirs(os.path.join(app_dir, 'backups'), exist_ok=True)
    os.makedirs(os.path.join(app_dir, 'generated_pdfs'), exist_ok=True)
    return app_dir

APP_DATA_DIR = get_app_data_dir()
DB_PATH = os.path.join(APP_DATA_DIR, "permits.db")
LOG_FILE = os.path.join(APP_DATA_DIR, "logs", "app.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# If local dev/bundled permits.db exists and APP_DATA_DIR permits.db does not exist, copy it over
dev_db = get_resource_path("permits.db")
if not os.path.exists(DB_PATH) and os.path.exists(dev_db):
    try:
        import shutil
        shutil.copyfile(dev_db, DB_PATH)
        logging.info("Copied initial database template to application data directory.")
    except Exception as e:
        logging.warning(f"Could not copy initial database template: {e}")


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def verify_backup(backup_path: str, expected_record_count: int = None) -> tuple:
    """
    Rigorously verifies a SQLite database backup file against 9 criteria.
    Returns (is_valid: bool, reason: str).
    """
    if not backup_path or not os.path.exists(backup_path):
        return False, "Backup file does not exist."
    if os.path.getsize(backup_path) == 0:
        return False, "Backup file is empty (0 bytes)."
    
    # Check SQLite header signature ("SQLite format 3\0")
    try:
        with open(backup_path, "rb") as f:
            header = f.read(16)
            if not header.startswith(b"SQLite format 3"):
                return False, "File is not a valid SQLite database (invalid header)."
    except Exception as e:
        return False, f"Failed to read backup file header: {e}"

    try:
        with sqlite3.connect(backup_path) as conn:
            conn.row_factory = sqlite3.Row
            # Integrity check
            res = conn.execute("PRAGMA integrity_check").fetchone()
            if not res or res[0].lower() != "ok":
                return False, f"PRAGMA integrity_check failed: {res[0] if res else 'Unknown'}"

            # Expected tables check
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            if "permits" not in tables:
                return False, "Backup missing required 'permits' table."
            if "users" not in tables:
                return False, "Backup missing required 'users' table."

            # Expected schema columns in permits table
            p_cols = [r[1] for r in conn.execute("PRAGMA table_info(permits)").fetchall()]
            req_p_cols = ["serial_no", "vehicle_no", "dispatch_slip"]
            for col in req_p_cols:
                if col not in p_cols:
                    return False, f"Backup 'permits' table missing required column '{col}'."

            # Expected schema columns in users table
            u_cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
            req_u_cols = ["username", "password_hash", "role"]
            for col in req_u_cols:
                if col not in u_cols:
                    return False, f"Backup 'users' table missing required column '{col}'."

            # Record count check
            cnt = conn.execute("SELECT COUNT(*) FROM permits").fetchone()[0]
            if expected_record_count is not None and cnt != expected_record_count:
                return False, f"Record count mismatch: expected {expected_record_count}, found {cnt}."

            return True, f"Verified valid backup ({cnt} permit records)."
    except sqlite3.DatabaseError as de:
        return False, f"Database error during backup verification: {de}"
    except Exception as e:
        return False, f"Unexpected error during backup verification: {e}"

def rotate_backups(max_retention: int = 10):
    """
    Retains up to max_retention verified backups in APP_DATA_DIR/backups.
    Safely removes older verified backups. Never deletes active DB or newest backup.
    """
    backup_dir = os.path.join(APP_DATA_DIR, "backups")
    if not os.path.exists(backup_dir):
        return

    try:
        files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith(".db")]
        verified_backups = []
        for f in files:
            is_valid, _ = verify_backup(f)
            if is_valid:
                verified_backups.append(f)

        verified_backups.sort(key=lambda x: os.path.getmtime(x))

        if len(verified_backups) > max_retention:
            to_remove = verified_backups[:-max_retention]
            for f in to_remove:
                if f != verified_backups[-1] and os.path.abspath(f) != os.path.abspath(DB_PATH):
                    try:
                        os.remove(f)
                        logging.info(f"Backup rotation removed old backup: {f}")
                    except Exception as e:
                        logging.warning(f"Could not remove old backup {f}: {e}")
    except Exception as e:
        logging.error(f"Backup rotation failed: {e}")

def create_backup(tag: str = "") -> tuple:
    """
    Creates an immutable, timestamped database backup in APP_DATA_DIR/backups using SQLite backup API.
    Returns (success: bool, backup_path: str, msg: str).
    """
    if not os.path.exists(DB_PATH):
        return False, "", "Active database file does not exist."

    backup_dir = os.path.join(APP_DATA_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    suffix = f"_{tag}" if tag else ""
    filename = f"permits_{timestamp}{suffix}.db"
    backup_path = os.path.join(backup_dir, filename)

    if os.path.exists(backup_path):
        filename = f"permits_{timestamp}_{secrets.token_hex(2)}{suffix}.db"
        backup_path = os.path.join(backup_dir, filename)

    try:
        with sqlite3.connect(DB_PATH, timeout=30.0) as src_conn:
            src_conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            src_count = src_conn.execute("SELECT COUNT(*) FROM permits").fetchone()[0]
            with sqlite3.connect(backup_path) as dst_conn:
                src_conn.backup(dst_conn)

        is_valid, reason = verify_backup(backup_path, expected_record_count=src_count)
        if is_valid:
            rotate_backups(max_retention=10)
            logging.info(f"Verified backup created successfully: {backup_path}")
            log_audit_event(
                action="DATABASE_BACKUP",
                result="SUCCESS",
                description=f"Backup created & verified: {os.path.basename(backup_path)}"
            )
            return True, backup_path, "Backup created successfully."
        else:
            logging.error(f"Backup verification failed for {backup_path}: {reason}")
            if os.path.exists(backup_path):
                os.remove(backup_path)
            log_audit_event(
                action="DATABASE_BACKUP",
                result="FAILED",
                description=f"Backup verification failed: {reason}"
            )
            return False, "", f"Backup verification failed: {reason}"
    except Exception as e:
        logging.error(f"Backup creation failed: {e}")
        log_audit_event(
            action="DATABASE_BACKUP",
            result="FAILED",
            description=f"Backup creation error: {e}"
        )
        return False, "", f"Backup creation failed: {e}"


def create_pre_migration_backup() -> str:
    """Helper alias for pre-migration backups, returning backup path on success."""
    ok, path, msg = create_backup(tag="pre_migration")
    return path if ok else ""

def restore_backup(backup_path: str) -> tuple:
    """
    Performs 16-step safe restore of a database backup with automatic rollback using SQLite backup API.
    Returns (success: bool, msg: str).
    """
    is_valid, reason = verify_backup(backup_path)
    if not is_valid:
        log_audit_event(
            action="DATABASE_RESTORE_FAILED",
            result="FAILED",
            description=f"Cannot restore invalid backup file: {reason}"
        )
        return False, f"Cannot restore: Invalid backup file ({reason})."

    ok_safety, safety_path, safety_msg = create_backup(tag="safety_before_restore")
    if not ok_safety:
        log_audit_event(
            action="DATABASE_RESTORE_FAILED",
            result="FAILED",
            description=f"Failed to create pre-restore safety backup: {safety_msg}"
        )
        return False, f"Cannot restore: Failed to create safety backup of active database ({safety_msg})."

    try:
        with sqlite3.connect(backup_path, timeout=30.0) as src_conn:
            src_conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            with sqlite3.connect(DB_PATH, timeout=30.0) as dst_conn:
                src_conn.backup(dst_conn)
                dst_conn.execute("PRAGMA journal_mode=WAL;")
    except Exception as e:
        log_audit_event(
            action="DATABASE_RESTORE_FAILED",
            result="FAILED",
            description=f"Overwrite active database error: {e}"
        )
        return False, f"Failed to overwrite active database file during restore: {e}"

    post_valid, post_reason = verify_backup(DB_PATH)
    if post_valid:
        logging.info(f"Database restored successfully from {backup_path}.")
        log_audit_event(
            action="DATABASE_RESTORE",
            result="SUCCESS",
            description=f"Restored from backup: {os.path.basename(backup_path)}"
        )
        return True, "Database restored successfully."
    else:
        logging.error(f"Post-restore verification failed ({post_reason}). Rolling back to safety backup...")
        try:
            with sqlite3.connect(safety_path, timeout=30.0) as src_conn:
                with sqlite3.connect(DB_PATH, timeout=30.0) as dst_conn:
                    src_conn.backup(dst_conn)
            roll_valid, roll_reason = verify_backup(DB_PATH)
            if roll_valid:
                logging.info(f"Automatic rollback to safety backup ({safety_path}) succeeded.")
                log_audit_event(
                    action="DATABASE_RESTORE_FAILED",
                    result="FAILED",
                    description=f"Restore failed ({post_reason}); rolled back to safety backup."
                )
                return False, f"Restore failed ({post_reason}). Automatically rolled back to previous database state."
            else:
                logging.critical("CRITICAL: Automatic rollback failed verification!")
                log_audit_event(
                    action="DATABASE_RESTORE_FAILED",
                    result="FAILED",
                    description="CRITICAL: Restore failed and rollback verification failed."
                )
                return False, "Restore failed and rollback verification failed. Critical database state."
        except Exception as rollback_err:
            logging.critical(f"CRITICAL: Failed to execute automatic rollback: {rollback_err}")
            log_audit_event(
                action="DATABASE_RESTORE_FAILED",
                result="FAILED",
                description=f"Restore failed & rollback error: {rollback_err}"
            )
            return False, f"Restore failed and automatic rollback encountered error: {rollback_err}"

def check_existing_duplicates(conn) -> tuple:
    """Queries for existing non-empty duplicate serial numbers or dispatch slips."""
    dup_serials = conn.execute("""
        SELECT serial_no, COUNT(*) as cnt
        FROM permits
        WHERE serial_no IS NOT NULL AND TRIM(serial_no) != ''
        GROUP BY serial_no
        HAVING cnt > 1
    """).fetchall()
    
    dup_dispatches = conn.execute("""
        SELECT dispatch_slip, COUNT(*) as cnt
        FROM permits
        WHERE dispatch_slip IS NOT NULL AND TRIM(dispatch_slip) != ''
        GROUP BY dispatch_slip
        HAVING cnt > 1
    """).fetchall()

    return [dict(r) for r in dup_serials], [dict(r) for r in dup_dispatches]

def log_audit_event(
    action: str,
    result: str = "SUCCESS",
    username: str = None,
    role: str = None,
    entity_type: str = None,
    entity_id: str = None,
    description: str = None,
    metadata: str = None,
    conn = None,
    is_critical: bool = False
):
    """
    Logs an audit event cleanly using parameterized SQL.
    Ensures zero passwords, hashes, salts, or tokens are logged.
    If conn is provided, executes within the active database transaction.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_desc = description[:500] if description else None
    
    if safe_desc and any(sec in safe_desc.lower() for sec in ["password", "hash", "salt", "token", "secret", "bearer"]):
        safe_desc = "[SENSITIVE DATA STRIPPED BY AUDIT ENGINE]"

    sql = """
        INSERT INTO audit_logs (timestamp, username, role, action, entity_type, entity_id, result, description, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (ts, username, role, action, entity_type, str(entity_id) if entity_id else None, result, safe_desc, metadata)

    try:
        if conn is not None:
            conn.execute(sql, params)
        else:
            with get_db() as c:
                c.execute(sql, params)
    except Exception as e:
        logging.error(f"Audit log insertion failed for action '{action}': {e}")
        if is_critical:
            raise RuntimeError(f"Critical audit event logging failed: {e}")

def init_db():
    try:
        with get_db() as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("""
            CREATE TABLE IF NOT EXISTS permits (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                serial_no       TEXT,
                lessee_id       TEXT,
                minecode        TEXT,
                lessee_name     TEXT,
                lessee_address  TEXT,
                hsn_code        TEXT,
                district        TEXT,
                taluk           TEXT,
                village         TEXT,
                sf_no           TEXT,
                classification  TEXT,
                lease_period    TEXT,
                mineral         TEXT,
                bulk_permit     TEXT,
                order_ref       TEXT,
                within_tn       TEXT,
                dispatch_slip   TEXT,
                delivered_to    TEXT,
                quantity        TEXT,
                auth_person     TEXT,
                vehicle_no      TEXT,
                vehicle_type    TEXT,
                distance        TEXT,
                destination     TEXT,
                via             TEXT,
                traveling_date  TEXT,
                traveling_time  TEXT,
                req_hours       TEXT,
                driver_name     TEXT,
                driver_license  TEXT,
                driver_phone    TEXT,
                created_at      TEXT DEFAULT (datetime('now','localtime'))
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                username        TEXT UNIQUE NOT NULL,
                password_hash   TEXT NOT NULL,
                role            TEXT NOT NULL DEFAULT 'staff',
                is_active       INTEGER NOT NULL DEFAULT 1,
                created_at      TEXT DEFAULT (datetime('now','localtime'))
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                username        TEXT,
                role            TEXT,
                action          TEXT NOT NULL,
                entity_type     TEXT,
                entity_id       TEXT,
                result          TEXT NOT NULL,
                description     TEXT,
                metadata        TEXT
            )
            """)
            try: conn.execute("ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")
            except: pass
            
            try: conn.execute("ALTER TABLE permits ADD COLUMN signature_path TEXT")
            except: pass
            
            try: conn.execute("CREATE INDEX IF NOT EXISTS idx_permits_vehicle ON permits(vehicle_no)")
            except: pass

            try:
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_username ON audit_logs(username)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id)")
            except: pass

            # Audit existing duplicates before applying unique partial indexes
            dup_s, dup_d = check_existing_duplicates(conn)
            if dup_s or dup_d:
                msg = f"MIGRATION BLOCKED — EXISTING DUPLICATE DATA REQUIRES BUSINESS RESOLUTION. Duplicate Serials: {len(dup_s)}, Duplicate Dispatches: {len(dup_d)}"
                logging.warning(msg)
                print(f"[WARNING] {msg}")
                log_audit_event(
                    action="DATABASE_MIGRATION",
                    result="BLOCKED",
                    description="Migration blocked because duplicate business identifiers require resolution.",
                    conn=conn
                )
                return False

            # Create Verified Pre-Migration Backup before applying schema indexes
            create_backup(tag="pre_migration")

            # Apply SQLite partial unique indexes
            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_permits_serial_unique
                ON permits(serial_no)
                WHERE serial_no IS NOT NULL AND serial_no != '';
            """)
            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_permits_dispatch_unique
                ON permits(dispatch_slip)
                WHERE dispatch_slip IS NOT NULL AND dispatch_slip != '';
            """)
            log_audit_event(
                action="DATABASE_MIGRATION",
                result="SUCCESS",
                description="Database migration completed successfully with unique partial indexes.",
                conn=conn
            )
            return True
    except sqlite3.DatabaseError as de:
        logging.error("Database connection/open error during init_db", exc_info=True)
        return False

def has_registered_users() -> bool:
    """Returns True if at least one user account exists in the database."""
    try:
        with get_db() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()
            return row and row["count"] > 0
    except Exception as e:
        logging.error("Failed to check registered users", exc_info=True)
        return False

# ══════════════════════════════════════════════════════════════════════════════
#  CENTRALIZED INPUT VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

def validate_permit_data(d: dict) -> tuple:
    """Validates permit data prior to database writes. Returns (is_valid, error_message)."""
    serial = d.get("serial_no", "").strip()
    vehicle = d.get("vehicle_no", "").strip()

    if not serial:
        return False, "Serial Number is required."
    if not vehicle:
        return False, "Vehicle Number is required."

    if len(serial) > 50:
        return False, "Serial Number cannot exceed 50 characters."
    if len(vehicle) > 30:
        return False, "Vehicle Number cannot exceed 30 characters."

    # Validate numeric fields (quantity, distance, req_hours) are non-negative
    numeric_checks = [
        ("quantity", "Quantity (MT)"),
        ("distance", "Total Distance (Kms)"),
        ("req_hours", "Required Time (hrs)")
    ]
    for key, label in numeric_checks:
        val = d.get(key, "").strip()
        if val:
            try:
                num = float(val)
                if num < 0:
                    return False, f"{label} cannot be a negative value."
            except ValueError:
                return False, f"{label} must be a valid numeric number."

    # Validate Traveling Date format (DD-MM-YYYY)
    t_date = d.get("traveling_date", "").strip()
    if t_date:
        try:
            datetime.strptime(t_date, "%d-%m-%Y")
        except ValueError:
            return False, "Traveling Date must be in DD-MM-YYYY format (e.g. 17-08-2026)."

    # Validate Traveling Time format
    t_time = d.get("traveling_time", "").strip()
    if t_time:
        valid_t = False
        for fmt in ("%I:%M %p", "%H:%M", "%I:%M%p"):
            try:
                datetime.strptime(t_time, fmt)
                valid_t = True
                break
            except ValueError:
                pass
        if not valid_t:
            return False, "Traveling Time must be a valid time string (e.g. 06:45 PM)."

    # Validate phone number
    phone = d.get("driver_phone", "").strip()
    if phone:
        digits_only = re.sub(r'[\s\-+()]', '', phone)
        if not digits_only.isdigit() or len(digits_only) < 7 or len(digits_only) > 15:
            return False, "Driver Phone Number must contain between 7 and 15 digits."

    # Max length sanity bounds for all text fields
    for field_name, field_val in d.items():
        if isinstance(field_val, str) and len(field_val) > 500:
            return False, f"Field '{field_name}' exceeds maximum length limit of 500 characters."

    return True, ""

def next_dispatch_slip():
    with get_db() as conn:
        row = conn.execute(
            "SELECT dispatch_slip FROM permits ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if row and row["dispatch_slip"]:
        try:
            num = int(row["dispatch_slip"].replace("DISP", ""))
            return f"DISP{num + 1:013d}"
        except (ValueError, TypeError): pass
    return "DISP0000000000001"

def next_serial_no():
    with get_db() as conn:
        row = conn.execute(
            "SELECT serial_no FROM permits ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if row and row["serial_no"]:
        try:
            import re
            m = re.search(r"(\d+)$", row["serial_no"])
            if m:
                prefix = row["serial_no"][:m.start()]
                num_str = m.group(1)
                num = int(num_str)
                return f"{prefix}{num + 1:0{len(num_str)}d}"
        except: pass
    return "TN03996631"

def generate_qr_base64(data: str) -> str:
    """Generates a high-clarity raster PNG QR code for the Netlify verification URL.

    Uses ERROR_CORRECT_M (15% data-recovery) to keep the QR version lower (fewer
    modules per side), making modules larger and easier to scan on paper.
    box_size=30 produces a high-density image for crisp rendering in the PDF.
    """
    from io import BytesIO
    import base64
    import qrcode.image.pil  # Pillow-backed raster factory

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Level M: optimal module size for URLs
        box_size=30,   # High resolution raster → sharp downscale in PDF
        border=4,      # Standard 4-module quiet zone
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.pil.PilImage)
    stream = BytesIO()
    img.save(stream, format='PNG')
    png_b64 = base64.b64encode(stream.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{png_b64}"

def format_dispatch_datetime(val) -> str:
    """
    Formats a dispatch timestamp into 12-hour AM/PM format: DD-MM-YYYY hh:mm:ss AM/PM.
    Converts 24-hour timestamps (e.g. 17-08-2026 16:35:58 -> 17-08-2026 04:35:58 PM).
    Safely handles missing values, datetime objects, and various string date formats.
    """
    if not val:
        return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
        
    if isinstance(val, datetime):
        return val.strftime("%d-%m-%Y %I:%M:%S %p")
        
    val_str = str(val).strip()
    if not val_str:
        return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
        
    formats = [
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %I:%M:%S %p",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y"
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(val_str, fmt)
            return dt.strftime("%d-%m-%Y %I:%M:%S %p")
        except ValueError:
            pass
            
    return val_str

def image_to_data_uri(path) -> str:
    """
    Safely converts a local image file path or file:// URL to a base64 data URI string.
    Handles Windows path syntax, leading/trailing quotes, file:// URLs, URL encoding,
    and missing or corrupt files.
    """
    if not path:
        return ""
    try:
        clean_path = str(path).strip().strip('"\'')
        if clean_path.lower().startswith("file:"):
            clean_path = clean_path[5:]
            while clean_path.startswith("/"):
                if len(clean_path) >= 3 and clean_path[1:3] in [":/", ":\\"]:
                    break
                clean_path = clean_path[1:]
            clean_path = unquote(clean_path)

        clean_path = os.path.normpath(clean_path)
        p = Path(clean_path)
        if not p.exists() or not p.is_file():
            return ""
        data = base64.b64encode(p.read_bytes()).decode("ascii")
        ext = p.suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
            ".gif": "image/gif",
            ".svg": "image/svg+xml"
        }
        mime_type = mime_map.get(ext, "image/png")
        return f"data:{mime_type};base64,{data}"
    except Exception as e:
        logging.warning(f"Failed to read image at '{path}': {e}")
        return ""

def format_quantity(val) -> str:
    """
    Formats a quantity value to exactly 2 decimal places (e.g., 9 -> '9.00', 9.5 -> '9.50').
    Preserves empty/None values as empty strings. Safely handles int, float, str, Decimal.
    """
    if val is None:
        return ""
    val_str = str(val).strip()
    if not val_str:
        return ""
    try:
        dec = Decimal(val_str)
        return f"{dec:.2f}"
    except (InvalidOperation, ValueError, TypeError):
        return val_str

# ══════════════════════════════════════════════════════════════════════════════
#  PDF GENERATION (ROBUST HEADLESS BROWSER BRIDGE)
# ══════════════════════════════════════════════════════════════════════════════

def generate_pdf(d: dict, path: str):
    """Zero-dependency high-fidelity PDF rendering via built-in browser CLI."""
    # 1. Resolve & normalize paths
    path = os.path.normpath(os.path.abspath(path))

    # Check if target file is currently locked/open in Edge or another application
    if os.path.exists(path):
        try:
            with open(path, "r+b") as f:
                pass
        except PermissionError:
            raise PermissionError(
                f"The file '{os.path.basename(path)}' is currently open in Microsoft Edge (or another viewer).\n\n"
                "Please close the open PDF tab in Edge and try printing again."
            )

    tpl_path = get_resource_path(os.path.join("pdf_generator", "template.html"))
    
    if not os.path.exists(tpl_path):
        err_msg = f"Template file not found at: {tpl_path}"
        logging.error(err_msg)
        messagebox.showerror("Error", err_msg)
        return

    # 2. Prepare Data & Inject into HTML
    d = d.copy()
    if 'dispatch_slip' not in d and 'dispatch_slip_no' in d:
        d['dispatch_slip'] = d['dispatch_slip_no']

    try:
        with open(tpl_path, 'r', encoding='utf8') as f:
            html = f.read()
        
        # Generate High-Robustness QR — plain-text CSV payload, no internet required
        try:
            t24 = datetime.strptime(d.get('traveling_time',''), "%I:%M %p").strftime("%H:%M")
        except:
            t24 = d.get('traveling_time','')
            
        # Format Traveling Date & Time for display: "1-04-2026 07:48 pm"
        traveling_dt_str = d.get('traveling_date', '') + ' ' + d.get('traveling_time', '')
        
        # Calculate expiry time: "12hrs (02-04-2026 07:48 am)"
        try:
            req_h = float(d.get('req_hours', '0'))
            start_dt = datetime.strptime(traveling_dt_str, "%d-%m-%Y %I:%M %p")
            end_dt = start_dt + timedelta(hours=req_h)
            expiry_str = f"{int(req_h)}hrs ({end_dt.strftime('%d-%m-%Y %I:%M %p').lower()})"
        except Exception as e:
            expiry_str = d.get('req_hours', '')
            
        d['traveling_date_full'] = traveling_dt_str.lower()
        d['req_hours_full'] = expiry_str
        
        # ── QR PAYLOAD: Netlify Verification URL with all parameters ───────────
        base_url = "https://cheery-sherbet-91f7c4.netlify.app/"
        date_param = f"{d.get('traveling_date', '')} {t24}".strip()
        mineral_val = d.get('mineral', '')
        qty_val = d.get('quantity', '')
        if qty_val and not str(mineral_val).endswith(f"({qty_val}MT)"):
            mineral_param = f"{mineral_val}({qty_val}MT)"
        else:
            mineral_param = mineral_val

        qr_params = {
            'serial': d.get('serial_no', ''),
            'slip': d.get('dispatch_slip', ''),
            'minecode': d.get('minecode', ''),
            'date': date_param,
            'vehicle': d.get('vehicle_no', ''),
            'mineral': mineral_param,
            'distance': d.get('distance', ''),
            'reqtime': d.get('req_hours', ''),
            'dest': d.get('destination', '')
        }
        
        qr_payload = f"{base_url}?{urlencode(qr_params)}"

        # Inject custom fields
        d['qr_code_url'] = generate_qr_base64(qr_payload)
        raw_disp = d.get('dispatch_datetime', None)
        if raw_disp:
            d['dispatch_datetime'] = format_dispatch_datetime(raw_disp)
        else:
            d['dispatch_datetime'] = format_dispatch_datetime(datetime.now())

        # Format Quantity to 2 decimal places for PDF display (Phase 10.4)
        if 'quantity' in d:
            d['quantity'] = format_quantity(d.get('quantity', ''))

        # Handle AD/DD Signature Image (Phase 10.3)
        # CASE A: User-selected custom signature path
        custom_sig = d.get('signature_path', '')
        sig_data_uri = ""
        
        if custom_sig:
            sig_data_uri = image_to_data_uri(custom_sig)
            if not sig_data_uri:
                logging.warning(f"Custom signature path '{custom_sig}' invalid/unreadable; falling back to default signature.")

        # CASE B, C, D: Fallback to bundled ad_dd_signature.png if custom_sig missing or unreadable
        if not sig_data_uri:
            bundled_sig = get_resource_path("ad_dd_signature.png")
            sig_data_uri = image_to_data_uri(bundled_sig)

        if sig_data_uri:
            sig_tag = f'<img src="{sig_data_uri}" class="sig-img" alt="Signature">'
        else:
            logging.warning("No signature image available (bundled fallback missing); using text placeholder.")
            sig_tag = '<div class="sig-placeholder">Signature of AD / DD</div>'

        d['signature_img_tag'] = sig_tag

        import html as html_module

        # Perform replacement for all keys safely with HTML escaping
        for key, value in d.items():
            if key in ['qr_code_url', 'signature_img_tag']:
                val_str = str(value) if value is not None else ""
            else:
                val_str = html_module.escape(str(value)) if value is not None else ""
            html = html.replace(f"{{{{{key}}}}}", val_str)

        # Save to temp HTML
        temp_html = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf8')
        temp_html.write(html)
        temp_html.close()
        
        # 3. Locate Browser (Edge or Chrome)
        import winreg
        browser_path = None
        
        # Strategy A: Registry Lookup
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe')
            browser_path = winreg.QueryValue(key, None)
        except:
            # Strategy B: Standard Paths
            paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            ]
            for p in paths:
                if os.path.exists(p):
                    browser_path = p
                    break
        
        if not browser_path:
            messagebox.showerror("Error", "No compatible browser found. Please install Microsoft Edge or Google Chrome.")
            return

        # 4. Execute Headless Printing via Temporary Buffer
        import uuid
        import shutil
        import time
        
        temp_pdf = os.path.join(tempfile.gettempdir(), f"pm_print_{uuid.uuid4().hex}.pdf")
        if os.path.exists(temp_pdf):
            try: os.remove(temp_pdf)
            except: pass

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        edge_temp_dir = tempfile.mkdtemp()
        
        # Use file:// URL for reliable path resolution in Edge
        abs_path = os.path.abspath(temp_html.name)
        file_url = "file:///" + abs_path.replace("\\", "/")

        cmd = [
            browser_path, 
            "--headless=new", 
            f"--print-to-pdf={temp_pdf}", 
            "--no-pdf-header-footer",
            "--disable-gpu",
            "--no-sandbox",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-extensions",
            "--disable-software-rasterizer",
            f"--user-data-dir={edge_temp_dir}",
            file_url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", startupinfo=startupinfo, timeout=60)
        
        # Wait up to 3 seconds for file flush to disk
        pdf_created = False
        for _ in range(30):
            if os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 0:
                pdf_created = True
                break
            time.sleep(0.1)

        # Fallback to legacy headless mode if --headless=new didn't write to disk
        if not pdf_created:
            cmd_legacy = [
                browser_path, 
                "--headless", 
                f"--print-to-pdf={temp_pdf}", 
                "--no-pdf-header-footer",
                "--disable-gpu",
                "--no-sandbox",
                f"--user-data-dir={edge_temp_dir}",
                file_url
            ]
            subprocess.run(cmd_legacy, capture_output=True, text=True, encoding="utf-8", errors="replace", startupinfo=startupinfo, timeout=60)
            for _ in range(30):
                if os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 0:
                    pdf_created = True
                    break
                time.sleep(0.1)
        
        if not pdf_created:
            raise Exception("PDF file was not written to disk despite browser returning success.")

        # Copy temporary rendered PDF to target path
        shutil.copyfile(temp_pdf, path)

    except subprocess.TimeoutExpired:
        messagebox.showerror("Error", "PDF generation timed out. Please close any open Edge/Chrome windows and try again.")
        return
    except Exception as e:
        messagebox.showerror("Error", f"PDF file was not created:\n{str(e)}")
        return
    finally:
        # Clean up temp html file, temp pdf, and temp user data dir
        if 'temp_html' in locals() and temp_html and os.path.exists(temp_html.name):
            try: os.unlink(temp_html.name)
            except: pass
        if 'temp_pdf' in locals() and temp_pdf and os.path.exists(temp_pdf):
            try: os.unlink(temp_pdf)
            except: pass
        try:
            shutil.rmtree(edge_temp_dir, ignore_errors=True)
        except:
            pass


# ══════════════════════════════════════════════════════════════════════════════
#  UI COMPONENTS (Light Theme)
# ══════════════════════════════════════════════════════════════════════════════

class ModernTreeview(tk.Frame):
    COLS = ("sl", "serial", "dispatch_slip", "destination", "vehicle", "driver", "phone", "date", "qty")
    HDRS = ("Sl#", "Serial Number", "Dispatch Slip No", "Destination", "Vehicle No", "Driver", "Phone", "Date", "Qty(MT)")
    WIDTHS = (40, 120, 160, 130, 110, 110, 100, 120, 60)

    def __init__(self, parent, cols=None, hdrs=None, widths=None, on_double_click=None, **kw):
        super().__init__(parent, bg=CARD_BG, **kw)
        if cols: self.COLS = cols
        if hdrs: self.HDRS = hdrs
        if widths: self.WIDTHS = widths
        self._setup_style()
        self._build(on_double_click)

    def _setup_style(self):
        try:
            style = tk.ttk.Style()
            # style.theme_use("clam") # Some systems fail on this
            style.configure("Light.Treeview", background=TABLE_ROW_1, fieldbackground=TABLE_ROW_1, foreground=TEXT_PRIMARY, rowheight=32, font=("Segoe UI", 9), borderwidth=0)
            style.configure("Light.Treeview.Heading", background="#F1F5F9", foreground=ACCENT, font=("Segoe UI", 9, "bold"), relief="flat")
            style.map("Light.Treeview", background=[("selected", TABLE_SELECT)], foreground=[("selected", TEXT_PRIMARY)])
        except Exception:
            pass

    def _build(self, on_dbl):
        import tkinter.ttk as ttk
        vsb, hsb = ttk.Scrollbar(self, orient="vertical"), ttk.Scrollbar(self, orient="horizontal")
        self.tree = ttk.Treeview(self, columns=self.COLS, show="headings", style="Light.Treeview", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        for c, h, w in zip(self.COLS, self.HDRS, self.WIDTHS):
            self.tree.heading(c, text=h, command=lambda _c=c: self._sort(_c))
            self.tree.column(c, width=w, minwidth=40, anchor="w")
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        if on_dbl: self.tree.bind("<Double-1>", on_dbl)

    def _sort(self, col):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        items.sort()
        for idx, (_, k) in enumerate(items): self.tree.move(k, "", idx)

    def clear(self):
        for item in self.tree.get_children(): self.tree.delete(item)

    def insert_row(self, iid, values, tag):
        self.tree.insert("", "end", iid=iid, values=values)

    def selected(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

# ══════════════════════════════════════════════════════════════════════════════
#  FIRST-RUN SETUP SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class FirstRunSetupFrame(ctk.CTkFrame):
    def __init__(self, parent, on_setup_complete):
        super().__init__(parent, fg_color=LOGIN_BG, corner_radius=0)
        self.on_complete = on_setup_complete
        self._build()

    def _build(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        right = ctk.CTkFrame(container, fg_color=LOGIN_CARD, width=480, height=560, corner_radius=24, border_width=0)
        right.pack()
        right.pack_propagate(False)

        inner = ctk.CTkFrame(right, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=40, pady=30)

        ctk.CTkLabel(inner, text="First-Run Admin Setup", font=("Segoe UI", 26, "bold"), text_color=LOGIN_TEXT).pack(anchor="w")
        ctk.CTkLabel(inner, text="Establish administrator credentials for Permit Master", font=("Segoe UI", 12), text_color=LOGIN_SUBTEXT).pack(anchor="w", pady=(5, 20))

        self.user_var = ctk.StringVar(value="admin")
        self.pass_var = ctk.StringVar()
        self.confirm_var = ctk.StringVar()

        self._input(inner, "ADMIN USERNAME", self.user_var)
        self._input(inner, "ADMIN PASSWORD", self.pass_var, show="*")
        self._input(inner, "CONFIRM PASSWORD", self.confirm_var, show="*")

        btn = ctk.CTkButton(inner, text="Initialize Administrator Account", command=self._do_setup, fg_color=LOGIN_ACCENT, hover_color=LOGIN_HOVER, text_color="white", height=45, corner_radius=12, font=("Segoe UI", 14, "bold"))
        btn.pack(fill="x", pady=(25, 10))

    def _input(self, parent, label, var, show=""):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", pady=8)
        ctk.CTkLabel(f, text=label, font=("Segoe UI", 10, "bold"), text_color=LOGIN_SUBTEXT).pack(anchor="w", padx=2, pady=(0, 4))
        e = ctk.CTkEntry(f, textvariable=var, show=show, height=40, corner_radius=10, fg_color=LOGIN_INPUT_BG, border_color=LOGIN_BORDER, border_width=1, text_color=LOGIN_TEXT, font=("Segoe UI", 13))
        e.pack(fill="x")

    def _do_setup(self):
        u = self.user_var.get().strip()
        p = self.pass_var.get().strip()
        c = self.confirm_var.get().strip()

        if not u or not p or not c:
            messagebox.showwarning("Setup Warning", "All fields are required.")
            return
        if len(p) < 6:
            messagebox.showwarning("Setup Warning", "Password must be at least 6 characters long.")
            return
        if p != c:
            messagebox.showwarning("Setup Warning", "Passwords do not match.")
            return

        try:
            pwd_hash = hash_password(p)
            with get_db() as conn:
                conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (u, pwd_hash, "admin"))
                log_audit_event("USER_CREATED", result="SUCCESS", username=u, role="admin", entity_type="user", entity_id=u, description=f"Admin user '{u}' created during setup", conn=conn, is_critical=True)
                
                # Seed standard staff user
                staff_hash = hash_password("StaffPass123!")
                conn.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)", ("staff", staff_hash, "staff"))
                log_audit_event("USER_CREATED", result="SUCCESS", username="staff", role="staff", entity_type="user", entity_id="staff", description="Staff user 'staff' seeded", conn=conn, is_critical=True)
            
            logging.info(f"First-run setup completed successfully. Admin account '{u}' created.")
            messagebox.showinfo("Setup Complete", f"Administrator account '{u}' created successfully!\n\nPlease log in with your credentials.")
            self.on_complete()
        except Exception as e:
            logging.error("First-run setup error", exc_info=True)
            messagebox.showerror("Setup Error", f"Could not create account: {e}")

# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=LOGIN_BG, corner_radius=0)
        self.on_success = on_login_success
        self._build()

    def _build(self):
        # Master Container with split layout
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # ── LEFT PANEL (Branding / Gradient Backdrop) ──
        left_wrapper = ctk.CTkFrame(container, fg_color="transparent", width=420, height=520)
        left_wrapper.pack(side="left", padx=(0, 20))
        left_wrapper.pack_propagate(False)

        left = ctk.CTkFrame(left_wrapper, fg_color=LOGIN_BG, width=420, height=520, corner_radius=24)
        left.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Dynamic Gradient Circle Simulation
        c1 = ctk.CTkFrame(left, fg_color=LOGIN_ACCENT, width=320, height=320, corner_radius=160)
        c1.place(relx=1.1, rely=0.2, anchor="center")
        
        c2 = ctk.CTkFrame(left, fg_color="#FDBA74", width=250, height=250, corner_radius=125)
        c2.place(relx=-0.1, rely=0.8, anchor="center")

        # Branding content
        ctk.CTkLabel(left, text="⛏", font=("Segoe UI", 90), text_color=LOGIN_TEXT).pack(pady=(120, 20))
        ctk.CTkLabel(left, text="PERMIT\nMASTER", font=("Segoe UI", 42, "bold"), text_color=LOGIN_TEXT, justify="center").pack()
        ctk.CTkLabel(left, text="Mining Dispatch Excellence", font=("Segoe UI", 15), text_color=LOGIN_SUBTEXT).pack(pady=20)
        
        # ── RIGHT PANEL (Clean Form) ──
        right = ctk.CTkFrame(container, fg_color=LOGIN_CARD, width=420, height=520, corner_radius=24, border_width=0)
        right.pack(side="left")
        right.pack_propagate(False)

        inner = ctk.CTkFrame(right, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(inner, text="Welcome Back", font=("Segoe UI", 32, "bold"), text_color=LOGIN_TEXT).pack(anchor="w")
        ctk.CTkLabel(inner, text="Please sign in to access your dashboard", font=("Segoe UI", 13), text_color=LOGIN_SUBTEXT).pack(anchor="w", pady=(5, 30))

        # Inputs
        self.user_var = ctk.StringVar()
        self.pass_var = ctk.StringVar()

        self._input(inner, "USERNAME", self.user_var)
        self._input(inner, "PASSWORD", self.pass_var, show="*")

        # Action Button
        btn = ctk.CTkButton(inner, text="Sign In", command=self._do_login, fg_color=LOGIN_ACCENT, hover_color=LOGIN_HOVER, text_color="white", height=50, corner_radius=14, font=("Segoe UI", 16, "bold"))
        btn.pack(fill="x", pady=(30, 20))

        ctk.CTkLabel(inner, text="Need help accessing your account?", font=("Segoe UI", 12), text_color=LOGIN_SUBTEXT, cursor="hand2").pack()

        # Footer
        ctk.CTkLabel(right, text="SECURE ACCESS PORTAL", font=("Segoe UI", 10, "bold"), text_color=LOGIN_BORDER).pack(side="bottom", pady=30)

    def _input(self, parent, label, var, show=""):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", pady=12)
        ctk.CTkLabel(f, text=label, font=("Segoe UI", 10, "bold"), text_color=LOGIN_SUBTEXT).pack(anchor="w", padx=2, pady=(0, 5))
        e = ctk.CTkEntry(f, textvariable=var, show=show, height=45, corner_radius=10, fg_color=LOGIN_INPUT_BG, border_color=LOGIN_BORDER, border_width=1, text_color=LOGIN_TEXT, font=("Segoe UI", 13))
        e.pack(fill="x")

    def _do_login(self):
        u = self.user_var.get().strip()
        p = self.pass_var.get().strip()
        if not u or not p:
            log_audit_event("VALIDATION_FAILED", result="FAILED", username=u or "unknown", description="Login validation failed: username or password empty")
            messagebox.showerror("Login Failed", "Invalid username or password.")
            return

        try:
            with get_db() as conn:
                row = conn.execute("SELECT username, password_hash, role, is_active FROM users WHERE username = ?", (u,)).fetchone()
            if row and verify_password(p, row["password_hash"]):
                is_act = row["is_active"] if "is_active" in row.keys() else 1
                if is_act == 0:
                    logging.warning(f"Login attempt by disabled user '{u}'.")
                    log_audit_event("LOGIN_FAILED", result="FAILED", username=u, role=row["role"], description="Login attempt by disabled account")
                    messagebox.showerror("Account Disabled", "Account disabled. Contact Administrator.")
                    return

                logging.info(f"User '{u}' (role: {row['role']}) logged in successfully.")
                log_audit_event("LOGIN_SUCCESS", result="SUCCESS", username=u, role=row["role"], description="User authenticated successfully")
                self.on_success({"username": row["username"], "role": row["role"]})
            else:
                logging.warning(f"Failed login attempt for user '{u}'.")
                log_audit_event("LOGIN_FAILED", result="FAILED", username=u, description="Invalid credentials supplied")
                messagebox.showerror("Login Failed", "Invalid username or password.")
        except Exception as e:
            logging.error("Login verification error", exc_info=True)
            log_audit_event("DATABASE_ERROR", result="FAILED", username=u, description=f"Authentication database error: {e}")
            messagebox.showerror("Login Error", "An error occurred during authentication.")

# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN AUDIT LOG VIEWER
# ══════════════════════════════════════════════════════════════════════════════

class AuditViewerFrame(ctk.CTkFrame):
    def __init__(self, parent, username, role="admin", on_close=None):
        super().__init__(parent, fg_color=BG_MAIN, corner_radius=0)
        self.username = username
        self.role = role
        self.on_close = on_close
        self.current_page = 1
        self.page_size = 50
        self.total_records = 0
        self.total_pages = 1
        self._build()

    def _build(self):
        # Top Header Bar
        hdr = ctk.CTkFrame(self, fg_color="#1E293B", height=60, corner_radius=0)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="🛡  Application Audit Trail", font=("Segoe UI", 18, "bold"), text_color="white").pack(side="left", padx=20)
        
        if self.on_close:
            ctk.CTkButton(hdr, text="✖ Close Audit Viewer", width=140, height=32, command=self.on_close, fg_color="#64748B", hover_color="#475569", font=("Segoe UI", 11, "bold")).pack(side="right", padx=20)

        # Filter Bar
        fbar = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER)
        fbar.pack(fill="x", padx=20, pady=(15, 10))

        inner = ctk.CTkFrame(fbar, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=10)

        # Search box (Username / Entity ID)
        ctk.CTkLabel(inner, text="🔍 Search:", font=("Segoe UI", 11, "bold"), text_color=TEXT_PRIMARY).pack(side="left", padx=(0, 5))
        self.search_var = ctk.StringVar()
        s_ent = ctk.CTkEntry(inner, textvariable=self.search_var, width=180, placeholder_text="Username / Entity ID...", height=32)
        s_ent.pack(side="left", padx=(0, 15))
        s_ent.bind("<Return>", lambda _: self._load_table())

        # Action Filter
        ctk.CTkLabel(inner, text="Action:", font=("Segoe UI", 11, "bold"), text_color=TEXT_PRIMARY).pack(side="left", padx=(0, 5))
        self.action_var = ctk.StringVar(value="All")
        a_combo = ctk.CTkOptionMenu(
            inner,
            variable=self.action_var,
            values=["All", "LOGIN_SUCCESS", "LOGIN_FAILED", "LOGOUT", "PERMIT_CREATED", "PERMIT_UPDATED", "PERMIT_DELETED", "PERMIT_VIEWED", "PERMIT_SEARCHED", "PDF_GENERATED", "PDF_EXPORT_BATCH", "USER_CREATED", "USER_UPDATED", "USER_DELETED", "ROLE_CHANGED", "DATABASE_BACKUP", "DATABASE_RESTORE", "DATABASE_RESTORE_FAILED", "DATABASE_MIGRATION", "DATABASE_ERROR", "PERMISSION_DENIED", "VALIDATION_FAILED", "APPLICATION_START", "APPLICATION_EXIT"],
            width=180,
            command=lambda _: self._load_table()
        )
        a_combo.pack(side="left", padx=(0, 15))

        # Result Filter
        ctk.CTkLabel(inner, text="Result:", font=("Segoe UI", 11, "bold"), text_color=TEXT_PRIMARY).pack(side="left", padx=(0, 5))
        self.result_var = ctk.StringVar(value="All")
        r_combo = ctk.CTkOptionMenu(
            inner,
            variable=self.result_var,
            values=["All", "SUCCESS", "FAILED", "DENIED", "BLOCKED"],
            width=120,
            command=lambda _: self._load_table()
        )
        r_combo.pack(side="left", padx=(0, 15))

        ctk.CTkButton(inner, text="Filter", width=70, height=32, command=self._load_table, fg_color=ACCENT).pack(side="left", padx=5)

        # Pagination & Stats Bar
        pbar = ctk.CTkFrame(self, fg_color="transparent")
        pbar.pack(fill="x", padx=20, pady=(0, 5))

        self.page_lbl = ctk.CTkLabel(pbar, text="Page 1 of 1 | Total: 0 records", font=("Segoe UI", 11), text_color=TEXT_SECONDARY)
        self.page_lbl.pack(side="right", padx=10)

        self.btn_prev = ctk.CTkButton(pbar, text="◀ Prev", width=70, height=28, command=self._prev_page, fg_color="#64748B")
        self.btn_prev.pack(side="left", padx=5)
        self.btn_next = ctk.CTkButton(pbar, text="Next ▶", width=70, height=28, command=self._next_page, fg_color="#64748B")
        self.btn_next.pack(side="left", padx=5)

        # Table Display
        COLS = ("id", "timestamp", "username", "role", "action", "entity", "result", "description")
        HDRS = ("ID", "Timestamp", "Username", "Role", "Action", "Entity", "Result", "Description")
        WIDTHS = (50, 140, 100, 80, 150, 90, 80, 260)

        t_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER)
        t_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.table = ModernTreeview(t_frame, cols=COLS, hdrs=HDRS, widths=WIDTHS)
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        self._load_table()

    def _load_table(self, reset_page=True):
        if reset_page:
            self.current_page = 1
        q = self.search_var.get().strip()
        act = self.action_var.get()
        res = self.result_var.get()

        where_clauses = []
        params = []

        if q:
            where_clauses.append("(username LIKE ? OR entity_id LIKE ? OR description LIKE ?)")
            params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
        if act != "All":
            where_clauses.append("action = ?")
            params.append(act)
        if res != "All":
            where_clauses.append("result = ?")
            params.append(res)

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        with get_db() as conn:
            cnt_sql = f"SELECT COUNT(*) FROM audit_logs {where_sql}"
            self.total_records = conn.execute(cnt_sql, params).fetchone()[0]

            import math
            self.total_pages = max(1, math.ceil(self.total_records / self.page_size))
            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
            offset = (self.current_page - 1) * self.page_size

            data_sql = f"SELECT * FROM audit_logs {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?"
            rows = conn.execute(data_sql, params + [self.page_size, offset]).fetchall()

        self.page_lbl.configure(text=f"Page {self.current_page} of {self.total_pages}  |  Total: {self.total_records:,} audit logs")
        self.btn_prev.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < self.total_pages else "disabled")

        self.table.clear()
        for r in rows:
            ent_str = f"{r['entity_type']}:{r['entity_id']}" if r['entity_type'] and r['entity_id'] else (r['entity_type'] or r['entity_id'] or "")
            self.table.insert_row(
                r["id"],
                (r["id"], r["timestamp"], r["username"] or "", r["role"] or "", r["action"], ent_str, r["result"], r["description"] or ""),
                ""
            )

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._load_table(reset_page=False)

    def _next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_table(reset_page=False)


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN USER MANAGEMENT DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class UserManagementDialog(ctk.CTkToplevel):
    def __init__(self, parent, username, role="admin"):
        super().__init__(parent)
        self.username = username
        self.role = role
        self.title("PermitMaster — User Access & Account Management")
        self.geometry("850x550")
        self.minsize(750, 450)
        self._all_users = []
        self._is_closing = False
        self._is_mutating = False

        if self.role != "admin":
            log_audit_event(action="PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, description="Staff user attempted unauthorized access to User Management")
            messagebox.showerror("Permission Denied", "Permission Denied: Administrator privileges required.")
            self.destroy()
            return

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()
        self._load_users_async()
        try:
            self.grab_set()
        except Exception:
            pass

    def _on_close(self):
        self._is_closing = True
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

    def _build_ui(self):
        top_bar = ctk.CTkFrame(self, fg_color=CARD_BG, height=50)
        top_bar.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(top_bar, text="👥 User Account Management", font=("Segoe UI", 16, "bold"), text_color="#1E293B").pack(side="left", padx=15, pady=10)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._on_search_changed())
        
        search_entry = ctk.CTkEntry(top_bar, textvariable=self.search_var, placeholder_text="🔍 Search username...", width=200, height=32)
        search_entry.pack(side="right", padx=15, pady=10)
        
        self.add_btn = ctk.CTkButton(top_bar, text="➕ Add User", command=self._add_user_dialog, fg_color="#10B981", height=32, corner_radius=6)
        self.add_btn.pack(side="right", padx=(0, 10), pady=10)

        tbl_frame = ctk.CTkFrame(self, fg_color=CARD_BG)
        tbl_frame.pack(fill="both", expand=True, padx=15, pady=5)

        COLS = ("id", "username", "role", "status", "created_at")
        HDRS = ("ID", "Username", "Role", "Account Status", "Created At")
        WIDTHS = (50, 180, 120, 120, 180)

        self.table = ModernTreeview(tbl_frame, cols=COLS, hdrs=HDRS, widths=WIDTHS)
        self.table.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree = self.table.tree

        self.tree.tag_configure("active", foreground="#166534")
        self.tree.tag_configure("disabled", foreground="#991B1B")

        self.tree.bind("<<TreeviewSelect>>", lambda e: self._update_button_states())

        act_bar = ctk.CTkFrame(self, fg_color="transparent")
        act_bar.pack(fill="x", padx=15, pady=(5, 15))

        self.btn_disable = ctk.CTkButton(act_bar, text="🚫 Disable Account", command=self._disable_user, fg_color="#EF4444", height=36, corner_radius=6, state="disabled")
        self.btn_disable.pack(side="left", padx=5)

        self.btn_enable = ctk.CTkButton(act_bar, text="✅ Enable Account", command=self._enable_user, fg_color="#10B981", height=36, corner_radius=6, state="disabled")
        self.btn_enable.pack(side="left", padx=5)

        self.btn_reset = ctk.CTkButton(act_bar, text="🔑 Reset Password", command=self._reset_password_dialog, fg_color="#3B82F6", height=36, corner_radius=6, state="disabled")
        self.btn_reset.pack(side="left", padx=5)

        ctk.CTkButton(act_bar, text="Close", command=self._on_close, fg_color=TEXT_MUTED, height=36, corner_radius=6).pack(side="right", padx=5)

    def _set_controls_state(self, state):
        if self._is_closing or not self.winfo_exists():
            return
        self.add_btn.configure(state=state)
        if state == "disabled":
            self.btn_disable.configure(state="disabled")
            self.btn_enable.configure(state="disabled")
            self.btn_reset.configure(state="disabled")
        else:
            self._update_button_states()

    def _update_button_states(self):
        if self._is_closing or not self.winfo_exists() or self._is_mutating:
            return
        sel = self.tree.selection()
        if not sel:
            self.btn_disable.configure(state="disabled")
            self.btn_enable.configure(state="disabled")
            self.btn_reset.configure(state="disabled")
            return

        item_vals = self.tree.item(sel[0])["values"]
        if not item_vals or len(item_vals) < 4:
            self.btn_disable.configure(state="disabled")
            self.btn_enable.configure(state="disabled")
            self.btn_reset.configure(state="disabled")
            return

        target_id, target_user, target_role, current_status, _ = item_vals
        self.btn_reset.configure(state="normal")
        if current_status == "Active":
            self.btn_disable.configure(state="normal")
            self.btn_enable.configure(state="disabled")
        else:
            self.btn_disable.configure(state="disabled")
            self.btn_enable.configure(state="normal")

    def _on_search_changed(self):
        self._populate_tree()

    def _load_users_async(self):
        import queue, threading
        q = queue.Queue()
        def worker():
            try:
                with get_db() as conn:
                    rows = conn.execute("SELECT id, username, role, is_active, created_at FROM users ORDER BY id ASC").fetchall()
                    users_data = [
                        {
                            "id": r["id"],
                            "username": r["username"],
                            "role": r["role"],
                            "is_active": r["is_active"] if "is_active" in r.keys() else 1,
                            "created_at": r["created_at"]
                        } for r in rows
                    ]
                q.put((users_data, None))
            except sqlite3.OperationalError as oe:
                logging.error("Database operational error during user fetch", exc_info=True)
                err = "Database is temporarily busy. Please try again." if "lock" in str(oe).lower() or "busy" in str(oe).lower() else "Unable to load user accounts. Please try again."
                q.put((None, err))
            except Exception as ex:
                logging.error("Failed to load user management list", exc_info=True)
                q.put((None, "Unable to load user accounts. Please try again."))

        def poll():
            if getattr(self, "_is_closing", False) or not self.winfo_exists():
                return
            try:
                users_data, err_msg = q.get_nowait()
                self._on_users_loaded(users_data, err_msg)
            except queue.Empty:
                if not getattr(self, "_is_closing", False) and self.winfo_exists():
                    self.after(20, poll)

        threading.Thread(target=worker, daemon=True).start()
        self.after(20, poll)

    def _on_users_loaded(self, users_data, err_msg):
        if self._is_closing or not self.winfo_exists():
            return
        if err_msg:
            messagebox.showerror("Error", err_msg, parent=self)
            return
        self._all_users = users_data or []
        self._populate_tree()

    def _populate_tree(self):
        if self._is_closing or not self.winfo_exists():
            return
        sel_ids = self.tree.selection()
        selected_iid = sel_ids[0] if sel_ids else None

        self.table.clear()
        query = self.search_var.get().strip().lower()
        for r in self._all_users:
            u_name = r["username"]
            if query and query not in u_name.lower():
                continue
            is_act = r["is_active"]
            status_str = "Active" if is_act == 1 else "Disabled"
            tag = "active" if is_act == 1 else "disabled"
            iid = str(r["id"])
            self.tree.insert("", "end", iid=iid, values=(r["id"], r["username"], r["role"], status_str, r["created_at"]), tags=(tag,))

        if selected_iid and self.tree.exists(selected_iid):
            self.tree.selection_set(selected_iid)
        self._update_button_states()

    def _disable_user(self):
        if self._is_mutating:
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a user account from the table.", parent=self)
            return
        item_vals = self.tree.item(sel[0])["values"]
        target_id, target_user, target_role, current_status, _ = item_vals

        if self.role != "admin":
            log_audit_event("PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, description="Non-admin attempted to disable user account")
            messagebox.showerror("Permission Denied", "Permission Denied: Administrator privileges required.", parent=self)
            return

        if target_role == "admin":
            try:
                with get_db() as conn:
                    cnt = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND (is_active = 1 OR is_active IS NULL)").fetchone()[0]
                if cnt <= 1:
                    log_audit_event("PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, entity_type="user", entity_id=str(target_user), description="Attempted to disable last active administrator account")
                    messagebox.showerror("Action Denied", "Cannot disable the last active administrator account.", parent=self)
                    return
            except sqlite3.OperationalError as oe:
                err = "Database is temporarily busy. Please try again." if "lock" in str(oe).lower() or "busy" in str(oe).lower() else "Unable to verify administrator count. Please try again."
                messagebox.showerror("Error", err, parent=self)
                return
            except Exception as e:
                logging.error("Error checking active admin count", exc_info=True)
                messagebox.showerror("Error", "Unable to verify administrator count. Please try again.", parent=self)
                return

        if current_status == "Disabled":
            messagebox.showinfo("Already Disabled", f"Account '{target_user}' is already disabled.", parent=self)
            return

        confirm = messagebox.askyesno("Confirm Disable", f"Are you sure you want to disable staff account '{target_user}'?", parent=self)
        if not confirm:
            return

        self._is_mutating = True
        self._set_controls_state("disabled")

        import queue, threading
        q = queue.Queue()
        def worker():
            try:
                with get_db() as conn:
                    conn.execute("UPDATE users SET is_active = 0 WHERE username = ?", (target_user,))
                    log_audit_event("USER_DISABLED", result="SUCCESS", username=self.username, role=self.role, entity_type="user", entity_id=str(target_user), description=f"Staff account '{target_user}' disabled by Admin '{self.username}'", conn=conn)
                q.put((True, f"User account '{target_user}' has been disabled."))
            except sqlite3.OperationalError as oe:
                logging.error(f"Failed to disable user '{target_user}' due to lock", exc_info=True)
                err = "Database is temporarily busy. Please try again." if "lock" in str(oe).lower() or "busy" in str(oe).lower() else "Unable to update user account. Please try again."
                q.put((False, err))
            except Exception as e:
                logging.error(f"Failed to disable user '{target_user}'", exc_info=True)
                q.put((False, "Unable to update user account. Please try again."))

        def poll():
            if getattr(self, "_is_closing", False) or not self.winfo_exists():
                return
            try:
                success, msg = q.get_nowait()
                if success:
                    self._on_action_complete(msg)
                else:
                    self._on_action_error(msg)
            except queue.Empty:
                if not getattr(self, "_is_closing", False) and self.winfo_exists():
                    self.after(20, poll)

        threading.Thread(target=worker, daemon=True).start()
        self.after(20, poll)

    def _enable_user(self):
        if self._is_mutating:
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a user account from the table.", parent=self)
            return
        item_vals = self.tree.item(sel[0])["values"]
        target_id, target_user, target_role, current_status, _ = item_vals

        if self.role != "admin":
            log_audit_event("PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, description="Non-admin attempted to enable user account")
            messagebox.showerror("Permission Denied", "Permission Denied: Administrator privileges required.", parent=self)
            return

        if current_status == "Active":
            messagebox.showinfo("Already Active", f"Account '{target_user}' is already active.", parent=self)
            return

        self._is_mutating = True
        self._set_controls_state("disabled")

        import queue, threading
        q = queue.Queue()
        def worker():
            try:
                with get_db() as conn:
                    conn.execute("UPDATE users SET is_active = 1 WHERE username = ?", (target_user,))
                    log_audit_event("USER_ENABLED", result="SUCCESS", username=self.username, role=self.role, entity_type="user", entity_id=str(target_user), description=f"User account '{target_user}' re-enabled by Admin '{self.username}'", conn=conn)
                q.put((True, f"User account '{target_user}' has been enabled."))
            except sqlite3.OperationalError as oe:
                logging.error(f"Failed to enable user '{target_user}' due to lock", exc_info=True)
                err = "Database is temporarily busy. Please try again." if "lock" in str(oe).lower() or "busy" in str(oe).lower() else "Unable to update user account. Please try again."
                q.put((False, err))
            except Exception as e:
                logging.error(f"Failed to enable user '{target_user}'", exc_info=True)
                q.put((False, "Unable to update user account. Please try again."))

        def poll():
            if getattr(self, "_is_closing", False) or not self.winfo_exists():
                return
            try:
                success, msg = q.get_nowait()
                if success:
                    self._on_action_complete(msg)
                else:
                    self._on_action_error(msg)
            except queue.Empty:
                if not getattr(self, "_is_closing", False) and self.winfo_exists():
                    self.after(20, poll)

        threading.Thread(target=worker, daemon=True).start()
        self.after(20, poll)

    def _on_action_complete(self, msg):
        self._is_mutating = False
        if self._is_closing or not self.winfo_exists():
            return
        messagebox.showinfo("Success", msg, parent=self)
        self._set_controls_state("normal")
        self._load_users_async()

    def _on_action_error(self, err_msg):
        self._is_mutating = False
        if self._is_closing or not self.winfo_exists():
            return
        messagebox.showerror("Error", err_msg, parent=self)
        self._set_controls_state("normal")

    def _add_user_dialog(self):
        if self._is_mutating:
            return
        if self.role != "admin":
            log_audit_event("PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, description="Non-admin attempted to add user")
            messagebox.showerror("Permission Denied", "Permission Denied: Administrator privileges required.", parent=self)
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New User")
        dialog.geometry("400x320")
        try:
            dialog.grab_set()
        except Exception:
            pass

        u_var = ctk.StringVar()
        p_var = ctk.StringVar()
        r_var = ctk.StringVar(value="staff")

        ctk.CTkLabel(dialog, text="Add New User Account", font=("Segoe UI", 14, "bold")).pack(pady=(15, 10))

        ctk.CTkLabel(dialog, text="Username").pack(anchor="w", padx=20)
        ctk.CTkEntry(dialog, textvariable=u_var).pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(dialog, text="Role").pack(anchor="w", padx=20)
        ctk.CTkOptionMenu(dialog, variable=r_var, values=["staff", "admin"]).pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(dialog, text="Password").pack(anchor="w", padx=20)
        ctk.CTkEntry(dialog, textvariable=p_var, show="*").pack(fill="x", padx=20, pady=(0, 15))

        create_btn = ctk.CTkButton(dialog, text="Create User", fg_color="#10B981")
        create_btn.pack(pady=10)

        def save_user():
            u = u_var.get().strip()
            p = p_var.get().strip()
            r = r_var.get().strip()
            if not u or not p:
                messagebox.showerror("Validation Error", "Username and password cannot be empty.", parent=dialog)
                return
            
            create_btn.configure(state="disabled")
            p_hash = hash_password(p)

            import queue, threading
            q = queue.Queue()
            def worker():
                try:
                    with get_db() as conn:
                        conn.execute("INSERT INTO users (username, password_hash, role, is_active) VALUES (?, ?, ?, 1)", (u, p_hash, r))
                        log_audit_event("USER_CREATED", result="SUCCESS", username=self.username, role=self.role, entity_type="user", entity_id=u, description=f"Created user '{u}' with role '{r}'", conn=conn)
                    q.put((True, f"User '{u}' created successfully."))
                except sqlite3.IntegrityError:
                    q.put((False, f"Username '{u}' already exists."))
                except sqlite3.OperationalError as oe:
                    logging.error(f"Failed to create user '{u}' due to lock", exc_info=True)
                    err = "Database is temporarily busy. Please try again." if "lock" in str(oe).lower() or "busy" in str(oe).lower() else "Unable to create user. Please try again."
                    q.put((False, err))
                except Exception as ex:
                    logging.error(f"Failed to create user '{u}'", exc_info=True)
                    q.put((False, "Unable to create user. Please try again."))

            def poll():
                if not dialog.winfo_exists():
                    return
                try:
                    success, msg = q.get_nowait()
                    if success:
                        self._on_user_created_success(dialog, msg)
                    else:
                        create_btn.configure(state="normal")
                        messagebox.showerror("Error", msg, parent=dialog)
                except queue.Empty:
                    if dialog.winfo_exists():
                        dialog.after(20, poll)

            threading.Thread(target=worker, daemon=True).start()
            dialog.after(20, poll)

        create_btn.configure(command=save_user)

    def _on_user_created_success(self, dialog, msg):
        if dialog.winfo_exists():
            messagebox.showinfo("Success", msg, parent=dialog)
            dialog.destroy()
        if self.winfo_exists() and not self._is_closing:
            self._load_users_async()

    def _reset_password_dialog(self):
        if self._is_mutating:
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a user account from the table.", parent=self)
            return
        item_vals = self.tree.item(sel[0])["values"]
        target_id, target_user, target_role, _, _ = item_vals

        if self.role != "admin":
            log_audit_event("PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, description="Non-admin attempted password reset")
            messagebox.showerror("Permission Denied", "Permission Denied: Administrator privileges required.", parent=self)
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Reset Password - {target_user}")
        dialog.geometry("380x220")
        try:
            dialog.grab_set()
        except Exception:
            pass

        p_var = ctk.StringVar()
        ctk.CTkLabel(dialog, text=f"Reset Password for '{target_user}'", font=("Segoe UI", 13, "bold")).pack(pady=(15, 10))
        ctk.CTkLabel(dialog, text="New Password").pack(anchor="w", padx=20)
        ctk.CTkEntry(dialog, textvariable=p_var, show="*").pack(fill="x", padx=20, pady=(0, 15))

        reset_btn = ctk.CTkButton(dialog, text="Reset Password", fg_color="#3B82F6")
        reset_btn.pack(pady=10)

        def save_pw():
            p = p_var.get().strip()
            if not p:
                messagebox.showerror("Validation Error", "Password cannot be empty.", parent=dialog)
                return
            reset_btn.configure(state="disabled")
            p_hash = hash_password(p)

            import queue, threading
            q = queue.Queue()
            def worker():
                try:
                    with get_db() as conn:
                        conn.execute("UPDATE users SET password_hash = ? WHERE username = ?", (p_hash, target_user))
                        log_audit_event("PASSWORD_RESET", result="SUCCESS", username=self.username, role=self.role, entity_type="user", entity_id=str(target_user), description=f"Password reset for user '{target_user}' by Admin '{self.username}'", conn=conn)
                    q.put((True, f"Password for user '{target_user}' reset successfully."))
                except sqlite3.OperationalError as oe:
                    logging.error(f"Failed to reset password for '{target_user}' due to lock", exc_info=True)
                    err = "Database is temporarily busy. Please try again." if "lock" in str(oe).lower() or "busy" in str(oe).lower() else "Unable to reset password. Please try again."
                    q.put((False, err))
                except Exception as ex:
                    logging.error(f"Failed to reset password for user '{target_user}'", exc_info=True)
                    q.put((False, "Unable to reset password. Please try again."))

            def poll():
                if not dialog.winfo_exists():
                    return
                try:
                    success, msg = q.get_nowait()
                    if success:
                        self._on_password_reset_success(dialog, msg)
                    else:
                        reset_btn.configure(state="normal")
                        messagebox.showerror("Error", msg, parent=dialog)
                except queue.Empty:
                    if dialog.winfo_exists():
                        dialog.after(20, poll)

            threading.Thread(target=worker, daemon=True).start()
            dialog.after(20, poll)

        reset_btn.configure(command=save_pw)

    def _on_password_reset_success(self, dialog, msg):
        if dialog.winfo_exists():
            messagebox.showinfo("Success", msg, parent=dialog)
            dialog.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, username, role="admin", on_logout=None):
        super().__init__(parent, fg_color=BG_MAIN, corner_radius=0)
        self.username = username
        self.role = role
        self.on_logout = on_logout
        self._editing_id = None
        self._vars = {}
        self.current_page = 1
        self.page_size = 50
        self.total_records = 0
        self.total_pages = 1
        init_db()
        self._build_ui()
        self._clear_form()
        self._load_table()
        self.update()

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=HEADER_BG, height=64, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="⛏  Permit Master Dashboard", font=("Segoe UI", 18, "bold"), text_color="white").pack(side="left", padx=20)
        
        user_info = ctk.CTkFrame(hdr, fg_color="#334155", corner_radius=20, height=32)
        user_info.pack(side="right", padx=(10, 20))
        ctk.CTkLabel(user_info, text=f"👤  {self.username} ({self.role.upper()})", font=("Segoe UI", 11), text_color="white", padx=15).pack()

        if self.on_logout:
            ctk.CTkButton(hdr, text="Logout", width=80, height=32, corner_radius=16, fg_color="#EF4444", hover_color="#DC2626", font=("Segoe UI", 11, "bold"), text_color="white", command=self.on_logout).pack(side="right")

        # Content
        sc = ctk.CTkScrollableFrame(self, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=20, pady=10)

        # ── FORM CARD ──
        fcard = ctk.CTkFrame(sc, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER)
        fcard.pack(fill="x", pady=(0, 15))
        self._form_title = ctk.CTkLabel(fcard, text="✚  Create New Permit", font=("Segoe UI", 14, "bold"), text_color=ACCENT)
        self._form_title.pack(anchor="w", padx=20, pady=(12, 4))
        
        body = ctk.CTkFrame(fcard, fg_color="transparent")
        body.pack(fill="x", padx=15, pady=10)
        self._build_fields(body)
        
        btn_bar = ctk.CTkFrame(fcard, fg_color="#F8FAFC", height=60, corner_radius=12)
        btn_bar.pack(fill="x", padx=1, pady=(10, 1))
        self._build_btns(btn_bar)

        # ── TABLE CARD ──
        tcard = ctk.CTkFrame(sc, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER)
        tcard.pack(fill="both", expand=True)
        thdr = ctk.CTkFrame(tcard, fg_color="transparent", height=50)
        thdr.pack(fill="x")
        ctk.CTkLabel(thdr, text="📋  Permit Registry", font=("Segoe UI", 14, "bold"), text_color=TEXT_PRIMARY).pack(side="left", padx=20)
        
        # Add Delete Button to Registry Header
        ctk.CTkButton(thdr, text="🗑 Delete", command=self._delete_selected, fg_color="#EF4444", hover_color="#DC2626", width=80, height=32, corner_radius=8, font=("Segoe UI", 11, "bold")).pack(side="left", padx=5)

        # Add Batch Export Button
        ctk.CTkButton(thdr, text="📦 Batch Export PDFs", command=self._bulk_export_pdfs, fg_color=INFO, hover_color="#0369A1", width=140, height=32, corner_radius=8, font=("Segoe UI", 11, "bold")).pack(side="left", padx=5)

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *_: self._load_table(reset_page=True))
        ctk.CTkEntry(thdr, placeholder_text="Search permits...", textvariable=self.search_var, width=200, height=32, corner_radius=8).pack(side="right", padx=20)

        # Pagination Bar
        pbar = ctk.CTkFrame(tcard, fg_color="#F8FAFC", height=36, corner_radius=6)
        pbar.pack(fill="x", padx=15, pady=(0, 10))
        
        self.btn_prev = ctk.CTkButton(pbar, text="◀ Prev", width=70, height=26, command=self._prev_page, fg_color="#64748B", hover_color="#475569", font=("Segoe UI", 10, "bold"))
        self.btn_prev.pack(side="left", padx=10, pady=5)
        
        self.page_label = ctk.CTkLabel(pbar, text="Page 1 of 1 (Total: 0)", font=("Segoe UI", 11, "bold"), text_color=TEXT_PRIMARY)
        self.page_label.pack(side="left", padx=10)
        
        self.btn_next = ctk.CTkButton(pbar, text="Next ▶", width=70, height=26, command=self._next_page, fg_color="#64748B", hover_color="#475569", font=("Segoe UI", 10, "bold"))
        self.btn_next.pack(side="left", padx=10, pady=5)

        self._table = ModernTreeview(tcard, on_double_click=lambda _: self._edit_selected())
        self._table.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        # Bind Delete key
        self._table.tree.bind("<Delete>", lambda _: self._delete_selected())

    def _field(self, p, label, key, row, col, req=False, state="normal"):
        f = ctk.CTkFrame(p, fg_color="transparent")
        f.grid(row=row, column=col, sticky="ew", padx=8, pady=6)
        txt = f"{label}*" if req else label
        ctk.CTkLabel(f, text=txt, font=("Segoe UI", 10), text_color=TEXT_SECONDARY).pack(anchor="w")
        v = ctk.StringVar(); self._vars[key] = v
        ctk.CTkEntry(f, textvariable=v, height=32, corner_radius=6, border_width=1, state=state).pack(fill="x")

    def _build_fields(self, p):
        for i in range(4): p.columnconfigure(i, weight=1)
        
        # Determine state based on role
        is_admin = (self.role == "admin")
        adm_s = "normal" if is_admin else "disabled"
        
        # Row 1 — General
        self._field(p, "Serial No", "serial_no", 0, 0, True)
        self._field(p, "Minecode", "minecode", 0, 1, state=adm_s)
        self._field(p, "Dispatch Slip", "dispatch_slip", 0, 2)
        self._field(p, "HSN Code", "hsn_code", 0, 3, state=adm_s)

        # Row 2 — Lessee & Permit
        self._field(p, "Lessee ID", "lessee_id", 1, 0, state=adm_s)
        self._field(p, "Lessee Name", "lessee_name", 1, 1, state=adm_s)
        self._field(p, "Bulk Permit No", "bulk_permit", 1, 2, state=adm_s)
        self._field(p, "Order Ref", "order_ref", 1, 3)

        # Row 3 — Location
        self._field(p, "District", "district", 2, 0, state=adm_s)
        self._field(p, "Taluk", "taluk", 2, 1, state=adm_s)
        self._field(p, "Village", "village", 2, 2, state=adm_s)
        self._field(p, "SF.No / Extent", "sf_no", 2, 3, state=adm_s)

        # Row 4 — Mineral & Status
        self._field(p, "Mineral", "mineral", 3, 0)
        self._field(p, "Classification", "classification", 3, 1, state=adm_s)
        self._field(p, "Lease Period", "lease_period", 3, 2, state=adm_s)
        self._field(p, "Auth Person", "auth_person", 3, 3, state=adm_s)

        # Row 5 — Delivery
        self._field(p, "Within Tamil Nadu", "within_tn", 4, 0, state=adm_s)
        self._field(p, "Delivered To", "delivered_to", 4, 1)
        self._field(p, "Quantity (MT)", "quantity", 4, 2)
        self._field(p, "Via", "via", 4, 3)

        # Row 6 — Vehicle
        self._field(p, "Vehicle No", "vehicle_no", 5, 0, True)
        self._field(p, "Vehicle Type", "vehicle_type", 5, 1)
        self._field(p, "Distance (Km)", "distance", 5, 2)
        self._field(p, "Destination", "destination", 5, 3)

        # Row 7 — Journey & Driver
        self._field(p, "Traveling Date", "traveling_date", 6, 0)
        self._field(p, "Traveling Time", "traveling_time", 6, 1)
        self._field(p, "Req. Time (hrs)", "req_hours", 6, 2)
        self._field(p, "Driver Name", "driver_name", 6, 3)

        # Row 8 — More Driver Info
        self._field(p, "Driver License", "driver_license", 7, 0)
        self._field(p, "Driver Phone", "driver_phone", 7, 1)

        # Row 9: Lessee Address (Full Width)
        ax = ctk.CTkFrame(p, fg_color="transparent")
        ax.grid(row=8, column=0, columnspan=4, sticky="ew", padx=8, pady=5)
        ctk.CTkLabel(ax, text="Lessee Address", font=("Segoe UI", 10), text_color=TEXT_SECONDARY).pack(anchor="w")
        v = ctk.StringVar(); self._vars["lessee_address"] = v
        ctk.CTkEntry(ax, textvariable=v, height=32, corner_radius=6, state=adm_s).pack(fill="x")

        # Row 10: Signature Path (Full Width - Available for Admin & Staff)
        sx = ctk.CTkFrame(p, fg_color="transparent")
        sx.grid(row=9, column=0, columnspan=4, sticky="ew", padx=8, pady=5)
        ctk.CTkLabel(sx, text="Signature Image Path (PNG)", font=("Segoe UI", 10, "bold"), text_color=ACCENT).pack(anchor="w")
        
        row = ctk.CTkFrame(sx, fg_color="transparent")
        row.pack(fill="x")
        
        sv = ctk.StringVar(); self._vars["signature_path"] = sv
        ctk.CTkEntry(row, textvariable=sv, height=32, corner_radius=6).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        def browse_sig():
            path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
            if path: sv.set(path)
        
        ctk.CTkButton(row, text="📁 Browse", command=browse_sig, width=100, height=32, corner_radius=6).pack(side="right")

    def _build_btns(self, p):
        inner = ctk.CTkFrame(p, fg_color="transparent")
        inner.pack(expand=True)
        ctk.CTkButton(inner, text="💾 Save Permit", command=self._save, fg_color=SUCCESS, height=36, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(inner, text="📋 Duplicate", command=self._dup, fg_color=WARNING, height=36, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(inner, text="🗑 Clear", command=self._clear_form, fg_color=TEXT_MUTED, height=36, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(inner, text="🖨 Print PDF", command=self._print, fg_color=INFO, height=36, corner_radius=8).pack(side="left", padx=5)
        if self.role == "admin":
            ctk.CTkButton(inner, text="📦 Backup DB", command=self._admin_backup, fg_color="#6366F1", height=36, corner_radius=8).pack(side="left", padx=5)
            ctk.CTkButton(inner, text="🔄 Restore DB", command=self._admin_restore, fg_color="#8B5CF6", height=36, corner_radius=8).pack(side="left", padx=5)
            ctk.CTkButton(inner, text="🛡 Audit Trail", command=self._admin_audit_viewer, fg_color="#0EA5E9", height=36, corner_radius=8).pack(side="left", padx=5)
            ctk.CTkButton(inner, text="👥 User Management", command=self._admin_user_management, fg_color="#10B981", height=36, corner_radius=8).pack(side="left", padx=5)

    def _admin_backup(self):
        if self.role != "admin":
            log_audit_event(action="PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, description="Staff user attempted unauthorized backup")
            messagebox.showwarning("Permission Denied", "Backup operations require Administrator privileges.")
            logging.warning(f"User '{self.username}' (role: {self.role}) attempted unauthorized backup.")
            return
        ok, path, msg = create_backup(tag="manual")
        if ok:
            messagebox.showinfo("Backup Success", f"Backup created successfully.\n\nPath: {os.path.basename(path)}")
        else:
            messagebox.showerror("Backup Error", f"Backup verification failed.\n\nReason: {msg}")

    def _admin_restore(self):
        if self.role != "admin":
            log_audit_event(action="PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, description="Staff user attempted unauthorized restore")
            messagebox.showwarning("Permission Denied", "Database Restore operations require Administrator privileges.")
            logging.warning(f"User '{self.username}' (role: {self.role}) attempted unauthorized restore.")
            return
        file_path = filedialog.askopenfilename(
            title="Select Database Backup File to Restore",
            filetypes=[("SQLite Database Files", "*.db"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        ok, msg = restore_backup(file_path)
        if ok:
            self._load_table()
            messagebox.showinfo("Restore Success", "Database restored successfully.")
        else:
            messagebox.showerror("Restore Error", f"Restore operation failed.\n\nDetails: {msg}")

    def _admin_audit_viewer(self):
        if self.role != "admin":
            log_audit_event(action="PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, description="Staff user attempted unauthorized audit trail access")
            messagebox.showwarning("Permission Denied", "Audit Log Viewer requires Administrator privileges.")
            return
        win = ctk.CTkToplevel(self)
        win.title("PermitMaster — Audit Log Viewer")
        win.geometry("1100x650")
        win.grab_set()
        win.focus_force()
        viewer = AuditViewerFrame(win, username=self.username, role=self.role, on_close=win.destroy)
        viewer.pack(fill="both", expand=True)

    def _admin_user_management(self):
        if self.role != "admin":
            log_audit_event(action="PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, description="Staff user attempted unauthorized access to User Management")
            messagebox.showerror("Permission Denied", "Permission Denied: Administrator privileges required.")
            logging.warning(f"User '{self.username}' (role: {self.role}) attempted unauthorized access to User Management.")
            return
        if hasattr(self, "_user_mgmt_win") and self._user_mgmt_win is not None and self._user_mgmt_win.winfo_exists():
            self._user_mgmt_win.lift()
            self._user_mgmt_win.focus_force()
            return
        self._user_mgmt_win = UserManagementDialog(self, username=self.username, role=self.role)

    def _save(self):
        if self._editing_id is not None and self.role != "admin":
            log_audit_event(action="PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, entity_type="permit", entity_id=self._editing_id, description="Staff user attempted unauthorized permit modification")
            messagebox.showwarning("Permission Denied", "Only Administrators can modify existing permit records.")
            logging.warning(f"User '{self.username}' (role: {self.role}) attempted unauthorized edit save.")
            return

        d = {k: v.get().strip() for k, v in self._vars.items()}
        global LAST_SIGNATURE_PATH
        if d.get("signature_path"):
            LAST_SIGNATURE_PATH = d.get("signature_path")
        elif LAST_SIGNATURE_PATH:
            d["signature_path"] = LAST_SIGNATURE_PATH
        is_valid, err_msg = validate_permit_data(d)
        if not is_valid:
            log_audit_event(action="VALIDATION_FAILED", result="FAILED", username=self.username, role=self.role, description=f"Permit validation failed: {err_msg}")
            messagebox.showwarning("Validation Error", err_msg)
            return

        try:
            with get_db() as conn:
                cols = list(d.keys())
                vals = [d[c] for c in cols]
                if self._editing_id is None:
                    placeholders = ','.join(['?'] * len(cols))
                    col_names = ','.join(cols)
                    cur = conn.execute(f"INSERT INTO permits ({col_names}) VALUES ({placeholders})", vals)
                    pid = cur.lastrowid
                    log_audit_event("PERMIT_CREATED", result="SUCCESS", username=self.username, role=self.role, entity_type="permit", entity_id=pid, description=f"Permit '{d.get('serial_no')}' created successfully", conn=conn, is_critical=True)
                else:
                    set_clause = ','.join(f"{c}=?" for c in cols)
                    conn.execute(f"UPDATE permits SET {set_clause} WHERE id=?", vals + [self._editing_id])
                    log_audit_event("PERMIT_UPDATED", result="SUCCESS", username=self.username, role=self.role, entity_type="permit", entity_id=self._editing_id, description=f"Permit '{d.get('serial_no')}' updated successfully", conn=conn, is_critical=True)
            self._clear_form()
            self._load_table()
            messagebox.showinfo("Success", "Permit details saved successfully.")
        except sqlite3.IntegrityError as ie:
            logging.warning(f"Database integrity error during save: {ie}")
            err_str = str(ie).lower()
            if "idx_permits_serial_unique" in err_str or "serial_no" in err_str:
                messagebox.showerror("Duplicate Serial Number", f"Serial Number '{d.get('serial_no')}' already exists in the database.")
            elif "idx_permits_dispatch_unique" in err_str or "dispatch_slip" in err_str:
                messagebox.showerror("Duplicate Dispatch Slip", f"Dispatch Slip '{d.get('dispatch_slip')}' is already assigned to another permit.")
            else:
                messagebox.showerror("Duplicate Record Error", "This record conflicts with an existing entry in the database.")
        except sqlite3.DatabaseError as de:
            logging.error("Database access error during save", exc_info=True)
            log_audit_event("DATABASE_ERROR", result="FAILED", username=self.username, role=self.role, description=f"Database access error during save: {de}")
            messagebox.showerror("Database Error", "A database error occurred while processing your request.")
        except Exception as e:
            logging.error("Save operation error", exc_info=True)
            messagebox.showerror("Error", f"Failed to save permit details: {e}")

    def _load_table(self, reset_page=True):
        if reset_page:
            self.current_page = 1
        q = self.search_var.get().strip()
        if q:
            log_audit_event("PERMIT_SEARCHED", result="SUCCESS", username=self.username, role=self.role, description=f"Search performed with query: '{q[:50]}'")
        with get_db() as conn:
            if q:
                count_q = "SELECT COUNT(*) FROM permits WHERE serial_no LIKE ? OR vehicle_no LIKE ? OR dispatch_slip LIKE ?"
                data_q = "SELECT * FROM permits WHERE serial_no LIKE ? OR vehicle_no LIKE ? OR dispatch_slip LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?"
                params = (f"%{q}%", f"%{q}%", f"%{q}%")
                self.total_records = conn.execute(count_q, params).fetchone()[0]
                import math
                self.total_pages = max(1, math.ceil(self.total_records / self.page_size))
                if self.current_page > self.total_pages:
                    self.current_page = self.total_pages
                offset = (self.current_page - 1) * self.page_size
                r = conn.execute(data_q, params + (self.page_size, offset)).fetchall()
            else:
                count_q = "SELECT COUNT(*) FROM permits"
                data_q = "SELECT * FROM permits ORDER BY id DESC LIMIT ? OFFSET ?"
                self.total_records = conn.execute(count_q).fetchone()[0]
                import math
                self.total_pages = max(1, math.ceil(self.total_records / self.page_size))
                if self.current_page > self.total_pages:
                    self.current_page = self.total_pages
                offset = (self.current_page - 1) * self.page_size
                r = conn.execute(data_q, (self.page_size, offset)).fetchall()

        self.page_label.configure(text=f"Page {self.current_page} of {self.total_pages}  |  Total: {self.total_records:,} permits")
        self.btn_prev.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < self.total_pages else "disabled")

        self._table.clear()
        start_sl = (self.current_page - 1) * self.page_size + 1
        for i, row in enumerate(r):
            self._table.insert_row(
                row["id"],
                (start_sl + i, row["serial_no"], row["dispatch_slip"], row["destination"], row["vehicle_no"], row["driver_name"], row["driver_phone"], row["traveling_date"], row["quantity"]),
                ""
            )

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._load_table(reset_page=False)

    def _next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_table(reset_page=False)

    def _bulk_export_pdfs(self):
        q = self.search_var.get().strip()
        with get_db() as conn:
            if q:
                rows = conn.execute("SELECT * FROM permits WHERE serial_no LIKE ? OR vehicle_no LIKE ? OR dispatch_slip LIKE ? ORDER BY id DESC", (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
            else:
                rows = conn.execute("SELECT * FROM permits ORDER BY id DESC").fetchall()
        
        if not rows:
            messagebox.showinfo("No Permits", "No permit records found to export.")
            return

        total_records = len(rows)
        if not messagebox.askyesno("Confirm Batch Export", f"Do you want to generate {total_records:,} PDF files into a destination folder?"):
            return

        export_dir = filedialog.askdirectory(title=f"Select Destination Folder for {total_records:,} PDFs")
        if not export_dir:
            return

        progress_win = ctk.CTkToplevel(self)
        progress_win.title("Batch PDF Generation")
        progress_win.geometry("450x220")
        progress_win.grab_set()
        progress_win.focus_force()

        ctk.CTkLabel(progress_win, text=f"Generating {total_records:,} PDFs...", font=("Segoe UI", 14, "bold"), text_color=TEXT_PRIMARY).pack(pady=(20, 5))
        lbl_status = ctk.CTkLabel(progress_win, text="Initializing batch process...", font=("Segoe UI", 11), text_color=TEXT_SECONDARY)
        lbl_status.pack(pady=5)
        
        progress_bar = ctk.CTkProgressBar(progress_win, width=360)
        progress_bar.pack(pady=15)
        progress_bar.set(0)

        cancelled = [False]
        def on_cancel():
            cancelled[0] = True
            progress_win.destroy()

        ctk.CTkButton(progress_win, text="Cancel Export", command=on_cancel, fg_color="#EF4444", hover_color="#DC2626", width=120, height=32).pack(pady=5)

        import threading

        def run_batch():
            success_count = 0
            for idx, row in enumerate(rows):
                if cancelled[0]:
                    break
                pdf_path = os.path.join(export_dir, f"Permit_{row['serial_no']}.pdf")
                try:
                    generate_pdf(dict(row), pdf_path)
                    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                        success_count += 1
                except Exception as e:
                    print(f"Error generating PDF for {row['serial_no']}: {e}")
                
                pct = (idx + 1) / total_records
                s_no = row['serial_no']
                self.after(0, lambda p=pct, i=idx+1, t=total_records, s=s_no: (
                    progress_bar.set(p) if progress_win.winfo_exists() else None,
                    lbl_status.configure(text=f"Generated {i:,} / {t:,}: Permit_{s}.pdf") if progress_win.winfo_exists() else None
                ))

            if not cancelled[0]:
                log_audit_event(action="PDF_EXPORT_BATCH", result="SUCCESS", username=self.username, role=self.role, description=f"Batch exported {success_count:,}/{total_records:,} PDFs into {export_dir}")
                self.after(0, lambda: (
                    progress_win.destroy() if progress_win.winfo_exists() else None,
                    messagebox.showinfo("Batch Export Complete", f"Successfully generated {success_count:,} / {total_records:,} PDFs into:\n{export_dir}")
                ))

        threading.Thread(target=run_batch, daemon=True).start()

    def _clear_form(self):
        for v in self._vars.values(): v.set("")
        # Defaults from Sample Image
        self._vars["traveling_date"].set(datetime.now().strftime("%d-%m-%Y"))
        self._vars["traveling_time"].set(datetime.now().strftime("%I:%M %p"))
        self._vars["hsn_code"].set("6290009")
        self._vars["within_tn"].set("Yes")
        self._vars["lessee_id"].set("CHN241557")
        self._vars["minecode"].set("KKIN00225")
        self._vars["lessee_name"].set("Gautham P M")
        self._vars["lessee_address"].set("No. 19, 11th Avenue, Ashok nagar, Chennai - 600083")
        self._vars["district"].set("Kallakurichi")
        self._vars["taluk"].set("Ulundurpet")
        self._vars["village"].set("Kallamedu")
        self._vars["sf_no"].set("58/1 (P-1)., / 00002.85.00")
        self._vars["mineral"].set("Pebbles")
        self._vars["lease_period"].set("12-07-2024 to 07-11-2026")
        self._vars["auth_person"].set("Gautham P M")
        self._vars["classification"].set("Porampoke Land")
        self._vars["req_hours"].set("12")
        self._vars["dispatch_slip"].set(next_dispatch_slip())
        self._vars["serial_no"].set(next_serial_no())
        if LAST_SIGNATURE_PATH and "signature_path" in self._vars:
            self._vars["signature_path"].set(LAST_SIGNATURE_PATH)
        
        self._editing_id = None; self._form_title.configure(text="✚  Create New Permit")


    def _delete_selected(self):
        if self.role != "admin":
            log_audit_event(action="PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, entity_type="permit", description="Staff user attempted unauthorized permit deletion")
            messagebox.showwarning("Permission Denied", "Only Administrators can delete permit records.")
            logging.warning(f"User '{self.username}' (role: {self.role}) attempted unauthorized delete.")
            return

        sid = self._table.selected()
        if not sid:
            messagebox.showinfo("Selection Required", "Please select a permit from the list to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to permanently delete this permit record?"):
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM permits WHERE id=?", (sid,))
                    log_audit_event(action="PERMIT_DELETED", result="SUCCESS", username=self.username, role=self.role, entity_type="permit", entity_id=sid, description=f"Permit ID {sid} deleted successfully", conn=conn, is_critical=True)
                self._load_table()
                if self._editing_id == sid:
                    self._clear_form()
            except Exception as e:
                logging.error("Delete operation failed", exc_info=True)
                messagebox.showerror("Error", f"Could not delete permit: {e}")


    def _edit_selected(self):
        if self.role != "admin":
            log_audit_event(action="PERMISSION_DENIED", result="DENIED", username=self.username, role=self.role, entity_type="permit", description="Staff user attempted unauthorized permit edit")
            messagebox.showwarning("Permission Denied", "Only Administrators can edit existing permit records.")
            logging.warning(f"User '{self.username}' (role: {self.role}) attempted unauthorized edit.")
            return

        sid = self._table.selected()
        if sid:
            with get_db() as conn: row = conn.execute("SELECT * FROM permits WHERE id=?", (sid,)).fetchone()
            if row:
                for k in self._vars: self._vars[k].set(row[k] or "")
                self._editing_id = sid; self._form_title.configure(text=f"✏  Editing — {row['serial_no']}")
                log_audit_event(action="PERMIT_VIEWED", result="SUCCESS", username=self.username, role=self.role, entity_type="permit", entity_id=sid, description=f"Permit '{row['serial_no']}' loaded for editing")

    def _dup(self):
        sid = self._table.selected()
        if sid:
            with get_db() as conn: row = conn.execute("SELECT * FROM permits WHERE id=?", (sid,)).fetchone()
            if row:
                for k in self._vars: self._vars[k].set(row[k] or "")
                self._vars["dispatch_slip"].set(next_dispatch_slip())
                self._vars["serial_no"].set(next_serial_no())
                self._editing_id = None; self._form_title.configure(text="✚  New Permit (Duplicated)")

    def _print(self):
        sid = self._table.selected()
        if not sid: 
            messagebox.showwarning("No Selection", "Please select a permit to print.")
            return
        with get_db() as conn: row = conn.execute("SELECT * FROM permits WHERE id=?", (sid,)).fetchone()
        if row:
            d = dict(row)
            gui_sig = self._vars.get("signature_path", ctk.StringVar()).get().strip()
            if gui_sig:
                d["signature_path"] = gui_sig
            elif not d.get("signature_path") and LAST_SIGNATURE_PATH:
                d["signature_path"] = LAST_SIGNATURE_PATH
            path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Permit_{row['serial_no']}.pdf")
            if path:
                try:
                    path = os.path.normpath(os.path.abspath(path))
                    generate_pdf(d, path)
                    if os.path.exists(path) and os.path.getsize(path) > 0:
                        import time
                        time.sleep(0.3)
                        log_audit_event(action="PDF_GENERATED", result="SUCCESS", username=self.username, role=self.role, entity_type="permit", entity_id=sid, description=f"PDF generated: Permit_{row['serial_no']}.pdf")
                        messagebox.showinfo("Success", f"PDF saved successfully!\n{path}")
                        os.startfile(path)
                    else:
                        log_audit_event(action="PDF_GENERATED", result="FAILED", username=self.username, role=self.role, entity_type="permit", entity_id=sid, description="PDF file was not created or zero size")
                        messagebox.showerror("Error", "PDF file was not created. Check if Edge/Chrome is installed.")
                except PermissionError as pe:
                    log_audit_event(action="PDF_GENERATED", result="FAILED", username=self.username, role=self.role, entity_type="permit", entity_id=sid, description=f"PDF permission error: {pe}")
                    messagebox.showwarning("File Currently Open", str(pe))
                except Exception as e:
                    log_audit_event(action="PDF_GENERATED", result="FAILED", username=self.username, role=self.role, entity_type="permit", entity_id=sid, description=f"PDF generation error: {e}")
                    messagebox.showerror("PDF Error", f"Failed to generate PDF:\n{str(e)}")

# ══════════════════════════════════════════════════════════════════════════════
#  APP SHELL
# ══════════════════════════════════════════════════════════════════════════════

class PermitMaster(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Permit Master")
        self.geometry("1100x800")
        
        # Set window icon using get_resource_path
        icon_path = get_resource_path("permit_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                logging.warning(f"Could not set window icon: {e}")

        init_db()
        if not has_registered_users():
            self._show_first_run_setup()
        else:
            self._show_login()

    def _show_first_run_setup(self):
        if hasattr(self, "dashboard"): self.dashboard.destroy()
        if hasattr(self, "login"): self.login.destroy()
        self.first_run = FirstRunSetupFrame(self, self._on_first_run_complete)
        self.first_run.pack(fill="both", expand=True)

    def _on_first_run_complete(self):
        if hasattr(self, "first_run"): self.first_run.destroy()
        self._show_login()

    def _show_login(self):
        if hasattr(self, "dashboard") and hasattr(self.dashboard, "username"):
            log_audit_event(action="LOGOUT", result="SUCCESS", username=self.dashboard.username, role=self.dashboard.role, description="User logged out")
        if hasattr(self, "first_run"): self.first_run.destroy()
        if hasattr(self, "dashboard"): self.dashboard.destroy()
        self.login = LoginFrame(self, self._on_login)
        self.login.pack(fill="both", expand=True)

    def _on_login(self, user_data):
        try:
            self.login.destroy()
            self.dashboard = DashboardFrame(self, username=user_data["username"], role=user_data["role"], on_logout=self._show_login)
            self.dashboard.pack(fill="both", expand=True)
            self.update()
        except Exception as e:
            logging.error("Dashboard loading error", exc_info=True)
            messagebox.showerror("UI Error", f"Failed to load dashboard:\n{e}")

if __name__ == "__main__":
    try:
        logging.info("Starting PermitMaster application...")
        log_audit_event(action="APPLICATION_START", result="SUCCESS", description="PermitMaster process initialized")
        app = PermitMaster()
        app.mainloop()
        logging.info("PermitMaster application closed normally.")
        log_audit_event(action="APPLICATION_EXIT", result="SUCCESS", description="PermitMaster application shut down cleanly")
    except Exception as e:
        logging.error("Fatal application execution error", exc_info=True)
        log_audit_event(action="APPLICATION_EXIT", result="FAILED", description=f"Fatal application error: {e}")
        try:
            messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{e}\n\nCheck logs at:\n{LOG_FILE}")
        except:
            pass
        print(f"Fatal error: {e}")

