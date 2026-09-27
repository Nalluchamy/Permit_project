import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import customtkinter as ctk
import permit_master_source
from PIL import ImageGrab
import time
import threading

def run_app():
    app = permit_master_source.PermitMaster()
    
    # We need to simulate login to get to dashboard
    # Since app._show_login is called in __init__, we can access app.login
    def delayed_actions():
        time.sleep(1) # wait for UI
        # Simulate typing admin and staff
        app.login.user_var.set("admin")
        app.login.pass_var.set("admin123")
        app.login._do_login()
        time.sleep(1) # Wait for dashboard...
        
        # Take screenshot of the app
        x = app.winfo_rootx()
        y = app.winfo_rooty()
        w = app.winfo_width()
        h = app.winfo_height()
        try:
            ImageGrab.grab(bbox=(x, y, x+w, y+100)).save(os.path.join(BASE_DIR, "header_test.png"))
            print("Screenshot saved to header_test.png")
            print("Screenshot saved to header_test.png")
        except Exception as e:
            print(f"Error capturing: {e}")
        
        app.quit()
        
    threading.Thread(target=delayed_actions, daemon=True).start()
    app.mainloop()

if __name__ == "__main__":
    run_app()
