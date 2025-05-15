import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from connection import *

class AdminOrdersScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Manage Orders - Byte&Bite")
        self.geometry("800x500")
        self.configure(bg="#f5f5f5")

        self.create_widgets()
        self.load_orders()

    def create_widgets(self):
        # Treeview setup
        columns = ("id", "summary", "item_names", "quantities", "order_time")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="Order ID")
        self.tree.heading("summary", text="Summary")
        self.tree.heading("item_names", text="Items")
        self.tree.heading("quantities", text="Quantities")
        self.tree.heading("order_time", text="Order Time")

        self.tree.column("id", width=60)
        self.tree.column("summary", width=200)
        self.tree.column("item_names", width=150)
        self.tree.column("quantities", width=100)
        self.tree.column("order_time", width=150)

        self.tree.pack(pady=20, fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack()

        tk.Button(btn_frame, text="Add Order", bg="green", fg="white", width=15, command=self.add_order).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Delete Order", bg="red", fg="white", width=15, command=self.delete_order).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Modify Order", bg="blue", fg="white", width=15, command=self.modify_order).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Refresh", bg="gray", fg="white", width=15, command=self.load_orders).pack(padx=10, side=tk.LEFT)

    def load_orders(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, summary, item_names, quantities, order_time FROM orders ORDER BY id DESC")
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_order(self):
        selected_orders = self.tree.selection()
        if not selected_orders:
            messagebox.showwarning("Selection Required", "Please select at least one order to delete.")
            return

        order_ids = [self.tree.item(order)["values"][0] for order in selected_orders]
        confirm = messagebox.askyesno("Delete Confirmation", f"Delete selected order(s) with ID(s): {', '.join(map(str, order_ids))}?")
        if confirm:
            try:
                conn = create_connection()
                cur = conn.cursor()
                for order_id in order_ids:
                    cur.execute("DELETE FROM orders WHERE id = %s", (order_id,))
                    cur.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))

                conn.commit()
                conn.close()
                messagebox.showinfo("Deleted", "Selected order(s) deleted successfully.")
                self.load_orders()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def modify_order(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an order to modify.")
            return

        selected_data = self.tree.item(selected)["values"]
        order_id, current_summary, current_items, current_quantities = selected_data[0], selected_data[1], selected_data[2], selected_data[3]

        edit_win = tk.Toplevel(self)
        edit_win.title(f"Modify Order ID {order_id}")
        edit_win.geometry("400x300")
        edit_win.configure(bg="#eef")

        tk.Label(edit_win, text="Summary:", bg="#eef").pack(pady=5)
        summary_entry = tk.Entry(edit_win, width=40)
        summary_entry.insert(0, current_summary)
        summary_entry.pack(pady=5)

        tk.Label(edit_win, text="Item Names:", bg="#eef").pack(pady=5)
        item_entry = tk.Entry(edit_win, width=40)
        item_entry.insert(0, current_items)
        item_entry.pack(pady=5)

        tk.Label(edit_win, text="Quantities:", bg="#eef").pack(pady=5)
        quantity_entry = tk.Entry(edit_win, width=40)
        quantity_entry.insert(0, current_quantities)
        quantity_entry.pack(pady=5)

        def save_changes():
            new_summary = summary_entry.get().strip()
            new_items = item_entry.get().strip()
            new_quantities = quantity_entry.get().strip()

            if not new_summary or not new_items or not new_quantities:
                messagebox.showwarning("Validation Error", "All fields are required.")
                return

            try:
                conn = create_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE orders
                    SET summary = %s, item_names = %s, quantities = %s
                    WHERE id = %s
                """, (new_summary, new_items, new_quantities, order_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Order ID {order_id} updated.")
                self.load_orders()
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(edit_win, text="Save Changes", bg="green", fg="white", command=save_changes).pack(pady=20)

    def add_order(self):
        add_win = tk.Toplevel(self)
        add_win.title("Add New Order")
        add_win.geometry("400x300")
        add_win.configure(bg="#eef")

        tk.Label(add_win, text="Summary:", bg="#eef").pack(pady=5)
        summary_entry = tk.Entry(add_win, width=40)
        summary_entry.pack(pady=5)

        tk.Label(add_win, text="Item Names:", bg="#eef").pack(pady=5)
        item_entry = tk.Entry(add_win, width=40)
        item_entry.pack(pady=5)

        tk.Label(add_win, text="Quantities:", bg="#eef").pack(pady=5)
        quantity_entry = tk.Entry(add_win, width=40)
        quantity_entry.pack(pady=5)

        def insert_order():
            summary = summary_entry.get().strip()
            item_names = item_entry.get().strip()
            quantities = quantity_entry.get().strip()

            if not summary or not item_names or not quantities:
                messagebox.showwarning("Validation Error", "All fields are required.")
                return

            try:
                conn = create_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO orders (summary, item_names, quantities)
                    VALUES (%s, %s, %s)
                """, (summary, item_names, quantities))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Order added successfully.")
                add_win.destroy()
                self.load_orders()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(add_win, text="Add Order", bg="green", fg="white", command=insert_order).pack(pady=20)


