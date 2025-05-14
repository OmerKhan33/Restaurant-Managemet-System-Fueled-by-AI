import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from connection import *

class AdminOrderItemsScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Manage Order Items - Byte&Bite")
        self.geometry("800x500")
        self.configure(bg="#f5f5f5")

        self.create_widgets()
        self.load_order_items()

    def create_widgets(self):
        # Treeview setup
        columns = ("id", "order_id", "item_name", "quantity")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="Item ID")
        self.tree.heading("order_id", text="Order ID")
        self.tree.heading("item_name", text="Item Name")
        self.tree.heading("quantity", text="Quantity")

        self.tree.column("id", width=60)
        self.tree.column("order_id", width=100)
        self.tree.column("item_name", width=300)
        self.tree.column("quantity", width=100)

        self.tree.pack(pady=20, fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack()

        tk.Button(btn_frame, text="Add Item", bg="green", fg="white", width=15, command=self.add_order_item).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Delete Item", bg="red", fg="white", width=15, command=self.delete_order_item).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Modify Item", bg="blue", fg="white", width=15, command=self.modify_order_item).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Refresh", bg="gray", fg="white", width=15, command=self.load_order_items).pack(padx=10, side=tk.LEFT)

    def load_order_items(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, order_id, item_name, quantity FROM order_items ORDER BY id DESC")
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_order_item(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Required", "Please select at least one order item to delete.")
            return

        order_item_ids = [self.tree.item(item)["values"][0] for item in selected_items]
        confirm = messagebox.askyesno("Delete Confirmation", f"Delete selected order item(s) with ID(s): {', '.join(map(str, order_item_ids))}?")
        if confirm:
            try:
                conn = create_connection()
                cur = conn.cursor()
                for order_item_id in order_item_ids:
                    cur.execute("DELETE FROM order_items WHERE id = %s", (order_item_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deleted", "Selected order item(s) deleted successfully.")
                self.load_order_items()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def modify_order_item(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an item to modify.")
            return

        selected_data = self.tree.item(selected)["values"]
        item_id, curr_order_id, curr_item_name, curr_quantity = selected_data

        edit_win = tk.Toplevel(self)
        edit_win.title(f"Modify Order Item ID {item_id}")
        edit_win.geometry("400x300")
        edit_win.configure(bg="#eef")

        # Order ID
        tk.Label(edit_win, text="Order ID:", bg="#eef").pack(pady=5)
        order_id_entry = tk.Entry(edit_win, width=40)
        order_id_entry.insert(0, curr_order_id)
        order_id_entry.pack(pady=5)

        # Item Name
        tk.Label(edit_win, text="Item Name:", bg="#eef").pack(pady=5)
        item_name_entry = tk.Entry(edit_win, width=40)
        item_name_entry.insert(0, curr_item_name)
        item_name_entry.pack(pady=5)

        # Quantity
        tk.Label(edit_win, text="Quantity:", bg="#eef").pack(pady=5)
        quantity_entry = tk.Entry(edit_win, width=40)
        quantity_entry.insert(0, curr_quantity)
        quantity_entry.pack(pady=5)

        def save_changes():
            new_order_id = order_id_entry.get().strip()
            new_item_name = item_name_entry.get().strip()
            new_quantity = quantity_entry.get().strip()

            if not new_order_id or not new_item_name or not new_quantity:
                messagebox.showwarning("Validation Error", "All fields are required.")
                return

            try:
                conn = create_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE order_items
                    SET order_id = %s, item_name = %s, quantity = %s
                    WHERE id = %s
                """, (new_order_id, new_item_name, new_quantity, item_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Order Item ID {item_id} updated.")
                self.load_order_items()
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(edit_win, text="Save Changes", bg="green", fg="white", command=save_changes).pack(pady=20)

    def add_order_item(self):
        add_win = tk.Toplevel(self)
        add_win.title("Add Order Item")
        add_win.geometry("400x300")
        add_win.configure(bg="#eef")

        # Order ID
        tk.Label(add_win, text="Order ID:", bg="#eef").pack(pady=5)
        order_id_entry = tk.Entry(add_win, width=40)
        order_id_entry.pack(pady=5)

        # Item Name
        tk.Label(add_win, text="Item Name:", bg="#eef").pack(pady=5)
        item_name_entry = tk.Entry(add_win, width=40)
        item_name_entry.pack(pady=5)

        # Quantity
        tk.Label(add_win, text="Quantity:", bg="#eef").pack(pady=5)
        quantity_entry = tk.Entry(add_win, width=40)
        quantity_entry.pack(pady=5)

        def submit_item():
            order_id = order_id_entry.get().strip()
            item_name = item_name_entry.get().strip()
            quantity = quantity_entry.get().strip()

            if not order_id or not item_name or not quantity:
                messagebox.showwarning("Validation Error", "All fields are required.")
                return

            try:
                conn = create_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO order_items (order_id, item_name, quantity)
                    VALUES (%s, %s, %s)
                """, (int(order_id), item_name, int(quantity)))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Order item added successfully!")
                self.load_order_items()
                add_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(add_win, text="Insert Item", bg="green", fg="white", command=submit_item).pack(pady=20)

