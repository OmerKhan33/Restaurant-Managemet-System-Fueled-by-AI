import tkinter as tk
from tkinter import ttk, messagebox
from connection import *

class OrderSummaryScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Order Summary View - Byte&Bite")
        self.geometry("800x500")
        self.configure(bg="#1e1e1e")

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        columns = ("order_id", "customer_name", "order_time", "total_price")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=150)

        self.tree.pack(pady=20, fill="both", expand=True)

        btn_frame = tk.Frame(self, bg="#1e1e1e")
        btn_frame.pack(pady=10)

        # 🆕 Button: Get Total Orders
        tk.Button(
            btn_frame,
            text="Get Total Orders",
            bg="#4caf50",
            fg="white",
            width=18,
            command=self.get_total_orders
        ).pack(side=tk.LEFT, padx=10)

        # Exit Button
        tk.Button(
            btn_frame,
            text="Exit",
            bg="red",
            fg="white",
            width=12,
            command=self.destroy
        ).pack(side=tk.LEFT, padx=10)

    def load_data(self):
        try:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT order_id, customer_name, order_time, total_price FROM view_order_summary ORDER BY order_id DESC")
            rows = cur.fetchall()
            for row in self.tree.get_children():
                self.tree.delete(row)
            for row in rows:
                self.tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # 🆕 Function to get total orders using the stored function
    def get_total_orders(self):
        try:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT get_total_orders();")
            result = cur.fetchone()[0]
            conn.close()
            messagebox.showinfo("Total Orders", f"Total number of orders placed: {result}")
        except Exception as e:
            messagebox.showerror("Error", str(e))



