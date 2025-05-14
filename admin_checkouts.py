import tkinter as tk
from tkinter import ttk, messagebox
from connection import *

class AdminCheckoutsScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Manage Checkouts - Byte&Bite")
        self.geometry("800x500")
        self.configure(bg="#f5f5f5")

        self.create_widgets()
        self.load_checkouts()

    def create_widgets(self):
        # Treeview setup
        columns = ("id", "customer_name", "order_id", "total_amount")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="Checkout ID")
        self.tree.heading("customer_name", text="Customer Name")
        self.tree.heading("order_id", text="Order ID")
        self.tree.heading("total_amount", text="Total Amount (PKR)")

        self.tree.column("id", width=80)
        self.tree.column("customer_name", width=200)
        self.tree.column("order_id", width=100)
        self.tree.column("total_amount", width=120)

        self.tree.pack(pady=20, fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack()

        tk.Button(btn_frame, text="Delete Checkout", bg="red", fg="white", width=15, command=self.delete_checkout).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Modify Checkout", bg="blue", fg="white", width=15, command=self.modify_checkout).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Refresh", bg="gray", fg="white", width=15, command=self.load_checkouts).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Add Checkout", bg="green", fg="white", width=15, command=self.add_checkout).pack(padx=10, side=tk.LEFT)


    def load_checkouts(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, customer_name, order_id, total_amount FROM checkouts ORDER BY id DESC")
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_checkout(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Required", "Please select at least one checkout to delete.")
            return

        checkout_ids = [self.tree.item(item)["values"][0] for item in selected_items]
        confirm = messagebox.askyesno("Delete Confirmation", f"Delete selected checkout(s) with ID(s): {', '.join(map(str, checkout_ids))}?")
        if confirm:
            try:
                conn = create_connection()
                cur = conn.cursor()
                for checkout_id in checkout_ids:
                    cur.execute("DELETE FROM checkouts WHERE id = %s", (checkout_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deleted", "Selected checkout(s) deleted successfully.")
                self.load_checkouts()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    def add_checkout(self):
        # New window for input
        add_win = tk.Toplevel(self)
        add_win.title("Add New Checkout")
        add_win.geometry("400x300")
        add_win.configure(bg="#eef")

        # Customer Name
        tk.Label(add_win, text="Customer Name:", bg="#eef").pack(pady=5)
        name_entry = tk.Entry(add_win, width=40)
        name_entry.pack(pady=5)

        # Order ID
        tk.Label(add_win, text="Order ID:", bg="#eef").pack(pady=5)
        order_entry = tk.Entry(add_win, width=40)
        order_entry.pack(pady=5)

        # Total Amount
        tk.Label(add_win, text="Total Amount (PKR):", bg="#eef").pack(pady=5)
        amount_entry = tk.Entry(add_win, width=40)
        amount_entry.pack(pady=5)

        # Submit function
        def submit_checkout():
            name = name_entry.get().strip()
            order_id = order_entry.get().strip()
            total = amount_entry.get().strip()

            if not name or not order_id or not total:
                messagebox.showwarning("Validation Error", "All fields are required.")
                return

            try:
                conn = create_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO checkouts (customer_name, order_id, total_amount)
                    VALUES (%s, %s, %s)
                """, (name, int(order_id), float(total)))
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Checkout added successfully!")
                self.load_checkouts()
                add_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(add_win, text="Insert Checkout", bg="green", fg="white", command=submit_checkout).pack(pady=20)



    def modify_checkout(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a checkout to modify.")
            return

        selected_data = self.tree.item(selected)["values"]
        checkout_id, curr_name, curr_order_id, curr_amount = selected_data

        # Create popup window
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Modify Checkout ID {checkout_id}")
        edit_win.geometry("400x300")
        edit_win.configure(bg="#eef")

        # Customer Name
        tk.Label(edit_win, text="Customer Name:", bg="#eef").pack(pady=5)
        name_entry = tk.Entry(edit_win, width=40)
        name_entry.insert(0, curr_name)
        name_entry.pack(pady=5)

        # Order ID
        tk.Label(edit_win, text="Order ID:", bg="#eef").pack(pady=5)
        order_entry = tk.Entry(edit_win, width=40)
        order_entry.insert(0, curr_order_id)
        order_entry.pack(pady=5)

        # Total Amount
        tk.Label(edit_win, text="Total Amount (PKR):", bg="#eef").pack(pady=5)
        amount_entry = tk.Entry(edit_win, width=40)
        amount_entry.insert(0, str(curr_amount))
        amount_entry.pack(pady=5)


    

        # Save button
        def save_changes():
            new_name = name_entry.get().strip()
            new_order_id = order_entry.get().strip()
            new_amount = amount_entry.get().strip()

            if not new_name or not new_order_id or not new_amount:
                messagebox.showwarning("Validation Error", "All fields are required.")
                return

            try:
                conn = create_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE checkouts
                    SET customer_name = %s, order_id = %s, total_amount = %s
                    WHERE id = %s
                """, (new_name, int(new_order_id), float(new_amount), checkout_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Checkout ID {checkout_id} updated.")
                self.load_checkouts()
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(edit_win, text="Save Changes", bg="green", fg="white", command=save_changes).pack(pady=20)





