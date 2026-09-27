import sqlite3

conn = sqlite3.connect('C:/Users/nallu/AppData/Local/PermitMaster/permits.db')
conn.row_factory = sqlite3.Row

rows = conn.execute("""
    SELECT id, serial_no, dispatch_slip, vehicle_no, lessee_name, driver_name, created_at 
    FROM permits 
    WHERE serial_no IN (
        SELECT serial_no FROM permits 
        WHERE serial_no IS NOT NULL AND TRIM(serial_no) != '' 
        GROUP BY serial_no HAVING COUNT(*) > 1
    ) OR dispatch_slip IN (
        SELECT dispatch_slip FROM permits 
        WHERE dispatch_slip IS NOT NULL AND TRIM(dispatch_slip) != '' 
        GROUP BY dispatch_slip HAVING COUNT(*) > 1
    ) 
    ORDER BY serial_no, dispatch_slip, id
""").fetchall()

print("| ID | Serial No | Dispatch Slip | Vehicle No | Lessee / Driver Name | Created At |")
print("|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['id']} | {r['serial_no']} | {r['dispatch_slip']} | {r['vehicle_no']} | {r['lessee_name']} / {r['driver_name']} | {r['created_at']} |")
