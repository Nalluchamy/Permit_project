import subprocess
import json
import os
import tempfile

def test_bridge():
    data = {
        "serial_no": "TEST-SERIAL-123",
        "lessee_name": "Test User",
        "district": "Test District",
        "date": "20-04-2026"
    }
    
    # Path to the generator script
    gen_script = os.path.abspath("pdf_generator/generate.js")
    output_pdf = os.path.abspath("bridge_test_output.pdf")
    
    print(f"Generator script: {gen_script}")
    print(f"Output PDF: {output_pdf}")
    
    # Create temp JSON
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w') as f:
        json.dump(data, f)
        temp_path = f.name
        
    print(f"Temp JSON: {temp_path}")
    
    try:
        # Run node
        result = subprocess.run(
            ["node", gen_script, temp_path, output_pdf],
            capture_output=True, text=True
        )
        
        print("\n--- STDOUT ---")
        print(result.stdout)
        print("\n--- STDERR ---")
        print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ Success! Bridge is working.")
        else:
            print(f"\n❌ Failed with return code {result.returncode}")
            
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == "__main__":
    test_bridge()
