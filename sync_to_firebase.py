import tkinter as tk
from tkinter import messagebox
import requests
import threading
from connection import *  # ✅ Using your custom DB connection

# ==================== Firebase Configuration =======================
FIREBASE_BASE_URL = "https://cs232-proj-default-rtdb.firebaseio.com"

# ==================== Upload Function ===============================
def upload_table_to_firebase(table_name):
    try:
        conn = create_connection()  # ✅ Using your own function
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]

        data_dict = {}
        for i, row in enumerate(rows):
            row_data = {col: str(val) for col, val in zip(colnames, row)}
            data_dict[f"{table_name}_{i+1}"] = row_data

        url = f"{FIREBASE_BASE_URL}/{table_name}.json"
        response = requests.put(url, json=data_dict)

        if response.status_code == 200:
            messagebox.showinfo("✅ Upload Successful", f"'{table_name}' data uploaded to Firebase.")
        else:
            messagebox.showerror("❌ Upload Failed", f"Firebase returned error code: {response.status_code}")

        cursor.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("❌ Database Error", str(e))

# ==================== Thread Wrapper ================================
def threaded_upload(table_name):
    threading.Thread(target=upload_table_to_firebase, args=(table_name,)).start()

# ==================== GUI Setup =====================================
def launch_realtime_db_app():
    realtime_db_app = tk.Tk()
    realtime_db_app.title("Sync PostgreSQL to Firebase")
    realtime_db_app.geometry("420x350")
    realtime_db_app.configure(bg="#f0f0f0")

    tk.Label(realtime_db_app, text="📤 Sync PostgreSQL Tables to Firebase", 
             font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=20)

    tk.Button(realtime_db_app, text="📦 Upload Orders", width=30, font=("Arial", 12),
              command=lambda: threaded_upload("orders")).pack(pady=6)

    tk.Button(realtime_db_app, text="🧾 Upload Order Items", width=30, font=("Arial", 12),
              command=lambda: threaded_upload("order_items")).pack(pady=6)

    tk.Button(realtime_db_app, text="👤 Upload Users", width=30, font=("Arial", 12),
              command=lambda: threaded_upload("users")).pack(pady=6)

    tk.Button(realtime_db_app, text="💰 Upload Checkouts", width=30, font=("Arial", 12),
              command=lambda: threaded_upload("checkouts")).pack(pady=6)
    
    tk.Button(realtime_db_app, text="🦾 Upload Menu Items", width=30, font=("Arial", 12),
              command=lambda: threaded_upload("menu_items")).pack(pady=6)
    
    tk.Button(realtime_db_app, text="🪟 Upload Feedbacks", width=30, font=("Arial", 12),
              command=lambda: threaded_upload("feedbacks")).pack(pady=6)
    

    

    tk.Button(realtime_db_app, text="❌ End Screen", width=30, font=("Arial", 12),
              bg="red", fg="white", command=realtime_db_app.destroy).pack(pady=25)

    realtime_db_app.mainloop()


