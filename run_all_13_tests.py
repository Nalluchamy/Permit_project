import subprocess
import sys
import os

tests = [
    "test_phase3_security.py",
    "test_phase4_data_validation.py",
    "test_phase5_database_integrity.py",
    "test_phase6_backup_recovery.py",
    "test_phase7_audit.py",
    "test_phase8_reliability.py",
    "verify_phase9_operational.py",
    "verify_phase10_golive.py",
    "verify_phase10_1_formatting.py",
    "verify_phase10_2_bold_values.py",
    "verify_phase10_3_signature.py",
    "verify_phase10_4_quantity_formatting.py",
    "verify_phase10_5_staff_signature.py"
]

print("===========================================================================", flush=True)
print("  PERMITMASTER — FULL 13-SCRIPT REGRESSION SUITE EXECUTION", flush=True)
print("===========================================================================", flush=True)

all_pass = True
for t in tests:
    res = subprocess.run([sys.executable, t], capture_output=True, text=True)
    status = "PASS" if res.returncode == 0 else "FAIL"
    if res.returncode != 0:
        all_pass = False
    print(f"  {t:45s} : [{status}]", flush=True)
    if res.returncode != 0:
        print(f"    STDOUT:\n{res.stdout[:500]}", flush=True)
        print(f"    STDERR:\n{res.stderr[:500]}", flush=True)

print("===========================================================================")
if all_pass:
    print("  ALL 13 REGRESSION TEST SCRIPTS PASSED (100% GREEN)")
else:
    print("  SOME TESTS FAILED - REVIEW LOGS ABOVE")
print("===========================================================================")
sys.exit(0 if all_pass else 1)
