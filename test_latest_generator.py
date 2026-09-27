import os
import sys
import json
from permit_master_source import generate_pdf

def test_latest():
    data = {
        "serial_no": "FINAL-REBUILD-TEST",
        "lessee_name": "Gautham P M",
        "district": "Kallakurichi",
        "taluk": "Ulundurpet",
        "village": "Kallamedu",
        "mineral": "Pebbles",
        "quantity": "9",
        "vehicle_no": "TN58J7212",
        "traveling_date": "20-04-2026",
        "traveling_time": "12:00 PM",
        "dispatch_slip": "DISP000007354833"
    }
    
    output_path = os.path.abspath("final_rebuild_verification.pdf")
    print(f"Testing latest generator. Output: {output_path}")
    
    try:
        generate_pdf(data, output_path)
        if os.path.exists(output_path):
            print("--- SUCCESS ---")
            print(f"PDF successfully generated at: {output_path}")
        else:
            print("--- FAILURE ---")
            print("PDF file was not created.")
    except Exception as e:
        print(f"--- ERROR ---")
        print(str(e))

if __name__ == "__main__":
    test_latest()
