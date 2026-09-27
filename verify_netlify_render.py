import urllib.parse

params = {
    'serial': 'TN03996631',
    'slip': 'DISP000007354833',
    'minecode': 'KKIN0025',
    'date': '01-04-2026 18:45',
    'vehicle': 'TN56J7212',
    'mineral': 'Pebbles(9MT)',
    'distance': '689',
    'reqtime': '12',
    'dest': 'ARANTHANGI'
}

def get(key):
    return params.get(key, '')

serial = get('serial')
slip = get('slip')
minecode = get('minecode')
date = get('date')
vehicle = get('vehicle')
mineral = get('mineral')
distance = get('distance')
reqtime = get('reqtime')
dest = get('dest')

m1 = minecode[:3]
m2 = minecode[3:]

v_clean = vehicle.replace(' ', '')
v1 = v_clean[:4]
v2 = v_clean[4:]

lines = [
    f"{serial},{slip},{m1}",
    f"{m2},{date}",
    f"{distance}kms,{reqtime}hrs,{mineral},{v1}",
    f"{v2},{dest}"
]

print("Simulated Netlify Renders:")
for line in lines:
    print(line)
