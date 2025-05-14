import tkinter as tk
from tkinter import ttk, messagebox
from connection import *

class AdminMenuItemsScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Manage Menu Items - Byte&Bite")
        self.geometry("900x550")
        self.configure(bg="#f5f5f5")

        self.create_widgets()
        self.load_menu_items()

    def create_widgets(self):
        columns = ("id", "name", "description", "price", "image", "category")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("description", text="Description")
        self.tree.heading("price", text="Price")
        self.tree.heading("image", text="Image")
        self.tree.heading("category", text="Category")

        self.tree.column("id", width=50)
        self.tree.column("name", width=150)
        self.tree.column("description", width=200)
        self.tree.column("price", width=80)
        self.tree.column("image", width=150)
        self.tree.column("category", width=120)

        self.tree.pack(pady=20, fill="both", expand=True)

        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack()

        tk.Button(btn_frame, text="Add Item", bg="green", fg="white", width=15, command=self.add_item).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Delete Item", bg="red", fg="white", width=15, command=self.delete_item).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Modify Item", bg="blue", fg="white", width=15, command=self.modify_item).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Refresh", bg="gray", fg="white", width=15, command=self.load_menu_items).pack(padx=10, side=tk.LEFT)

    def load_menu_items(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name, description, price, image, category FROM menu_items ORDER BY id DESC")
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_item(self):
        add_win = tk.Toplevel(self)
        add_win.title("Add Menu Item")
        add_win.geometry("400x500")
        add_win.configure(bg="#eef")

        def create_labeled_entry(label):
            tk.Label(add_win, text=label, bg="#eef").pack(pady=5)
            entry = tk.Entry(add_win, width=40)
            entry.pack(pady=5)
            return entry

        name_entry = create_labeled_entry("Name:")
        desc_entry = create_labeled_entry("Description:")
        price_entry = create_labeled_entry("Price:")
        image_entry = create_labeled_entry("Image URL:")
        category_entry = create_labeled_entry("Category:")

        def save_item():
            name = name_entry.get().strip()
            desc = desc_entry.get().strip()
            price_text = price_entry.get().strip()
            image = image_entry.get().strip()
            category = category_entry.get().strip()

            if not name or not desc or not price_text or not image or not category:
                messagebox.showwarning("Validation Error", "All fields are required.")
                return

            try:
                price = float(price_text)
            except ValueError:
                messagebox.showwarning("Invalid Input", "Price must be a valid number.")
                return

            try:
                conn = create_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO menu_items (name, description, price, image, category)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, desc, price, image, category))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Menu item added successfully.")
                self.load_menu_items()
                add_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(add_win, text="Add Item", bg="green", fg="white", command=save_item).pack(pady=20)

    def delete_item(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Required", "Please select at least one item to delete.")
            return

        item_ids = [self.tree.item(item)["values"][0] for item in selected_items]
        confirm = messagebox.askyesno("Delete Confirmation", f"Delete selected item(s) with ID(s): {', '.join(map(str, item_ids))}?")
        if confirm:
            try:
                conn = create_connection()
                cur = conn.cursor()
                for item_id in item_ids:
                    cur.execute("DELETE FROM menu_items WHERE id = %s", (item_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deleted", "Selected item(s) deleted successfully.")
                self.load_menu_items()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def modify_item(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an item to modify.")
            return

        selected_data = self.tree.item(selected)["values"]
        item_id, curr_name, curr_desc, curr_price, curr_image, curr_category = selected_data

        edit_win = tk.Toplevel(self)
        edit_win.title(f"Modify Menu Item ID {item_id}")
        edit_win.geometry("400x500")
        edit_win.configure(bg="#eef")

        def create_labeled_entry(label, default_value):
            tk.Label(edit_win, text=label, bg="#eef").pack(pady=5)
            entry = tk.Entry(edit_win, width=40)
            entry.insert(0, default_value)
            entry.pack(pady=5)
            return entry

        name_entry = create_labeled_entry("Name:", curr_name)
        desc_entry = create_labeled_entry("Description:", curr_desc)
        price_entry = create_labeled_entry("Price:", str(curr_price))
        image_entry = create_labeled_entry("Image URL:", curr_image)
        category_entry = create_labeled_entry("Category:", curr_category)

        def save_changes():
            new_name = name_entry.get().strip()
            new_desc = desc_entry.get().strip()
            try:
                new_price = float(price_entry.get().strip())
            except ValueError:
                messagebox.showwarning("Invalid Input", "Price must be a valid number.")
                return
            new_image = image_entry.get().strip()
            new_category = category_entry.get().strip()

            if not new_name or not new_desc or not new_image or not new_category:
                messagebox.showwarning("Validation Error", "All fields are required.")
                return

            try:
                conn = create_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE menu_items
                    SET name = %s, description = %s, price = %s, image = %s, category = %s
                    WHERE id = %s
                """, (new_name, new_desc, new_price, new_image, new_category, item_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Menu item ID {item_id} updated.")
                self.load_menu_items()
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(edit_win, text="Save Changes", bg="green", fg="white", command=save_changes).pack(pady=20)
