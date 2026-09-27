import urllib.parse
import urllib.request
from datetime import datetime

d = {
    "serial_no": "TN03996631",
    "dispatch_slip": "DISP000007354833",
    "minecode": "KKIN0025",
    "traveling_date": "01-04-2026",
    "traveling_time": "06:45 PM",
    "distance": "689",
    "req_hours": "12",
    "mineral": "Pebbles",
    "quantity": "9",
    "vehicle_no": "TN56J7212",
    "destination": "ARANTHANGI"
}

base_url = "https://cheery-sherbet-91f7c4.netlify.app/"

try:
    t24 = datetime.strptime(d.get('traveling_time',''), "%I:%M %p").strftime("%H:%M")
except Exception as e:
    t24 = d.get('traveling_time','')

traveling_date_val = d.get('traveling_date', '')
date_param = f"{traveling_date_val} {t24}".strip()

mineral_val = d.get('mineral', '')
qty_val = d.get('quantity', '')
if qty_val and not mineral_val.endswith(f"({qty_val}MT)"):
    mineral_param = f"{mineral_val}({qty_val}MT)"
else:
    mineral_param = mineral_val

params = {
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

query_str = urllib.parse.urlencode(params)
full_url = f"{base_url}?{query_str}"

print("Constructed Full URL:")
print(full_url)

print("\nPayload Length:", len(full_url), "chars")
