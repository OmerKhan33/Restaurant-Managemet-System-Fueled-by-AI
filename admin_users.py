import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from connection import *
from werkzeug.security import generate_password_hash, check_password_hash



class AdminUsersScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Manage Users - Byte&Bite")
        self.geometry("800x500")
        self.configure(bg="#f5f5f5")

        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        # Treeview setup
        columns = ("id", "username", "email", "password_hash", "created_at")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="User ID")
        self.tree.heading("username", text="Username")
        self.tree.heading("email", text="Email")
        self.tree.heading("password_hash", text="Password")
        self.tree.heading("created_at", text="Created At")

        self.tree.column("id", width=60)
        self.tree.column("username", width=150)
        self.tree.column("email", width=200)
        self.tree.column("password_hash", width=200)
        self.tree.column("created_at", width=150)

        self.tree.pack(pady=20, fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack()

        tk.Button(btn_frame, text="Add User", bg="green", fg="white", width=15, command=self.add_user).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Delete User", bg="red", fg="white", width=15, command=self.delete_user).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Modify User", bg="blue", fg="white", width=15, command=self.modify_user).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Refresh", bg="gray", fg="white", width=15, command=self.load_users).pack(padx=10, side=tk.LEFT)

    def load_users(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, username, email, password_hash, created_at FROM users ORDER BY id DESC")
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_user(self):
        # Create popup window
        add_win = tk.Toplevel(self)
        add_win.title("Add New User")
        add_win.geometry("400x300")
        add_win.configure(bg="#eef")

        # Username
        tk.Label(add_win, text="Username:", bg="#eef").pack(pady=5)
        username_entry = tk.Entry(add_win, width=40)
        username_entry.pack(pady=5)

        # Email
        tk.Label(add_win, text="Email:", bg="#eef").pack(pady=5)
        email_entry = tk.Entry(add_win, width=40)
        email_entry.pack(pady=5)

        # Password Hash
        tk.Label(add_win, text="Password Hash:", bg="#eef").pack(pady=5)
        password_entry = tk.Entry(add_win, width=40)
        password_entry.pack(pady=5)

        # Save button for adding user
        def save_user():
            username = username_entry.get().strip()
            email = email_entry.get().strip()
            password_hash = password_entry.get().strip()
            password_hash = generate_password_hash(password_hash)

            if not username or not email or not password_hash:
                messagebox.showwarning("Validation Error", "All fields are required.")
                return

            try:
                conn = create_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO users (username, email, password_hash)
                    VALUES (%s, %s, %s)
                """, (username, email, password_hash))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "User added successfully.")
                self.load_users()
                add_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(add_win, text="Add User", bg="green", fg="white", command=save_user).pack(pady=20)

    def delete_user(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Required", "Please select at least one user to delete.")
            return

        user_ids = [self.tree.item(item)["values"][0] for item in selected_items]
        confirm = messagebox.askyesno("Delete Confirmation", f"Delete selected user(s) with ID(s): {', '.join(map(str, user_ids))}?")
        if confirm:
            try:
                conn = create_connection()
                cur = conn.cursor()
                for user_id in user_ids:
                    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deleted", "Selected user(s) deleted successfully.")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def modify_user(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a user to modify.")
            return

        selected_data = self.tree.item(selected)["values"]
        user_id, curr_username, curr_email, curr_password_hash = selected_data[0], selected_data[1], selected_data[2], selected_data[3]

        # Create popup window
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Modify User ID {user_id}")
        edit_win.geometry("400x300")
        edit_win.configure(bg="#eef")

        # Username
        tk.Label(edit_win, text="Username:", bg="#eef").pack(pady=5)
        username_entry = tk.Entry(edit_win, width=40)
        username_entry.insert(0, curr_username)
        username_entry.pack(pady=5)

        # Email
        tk.Label(edit_win, text="Email:", bg="#eef").pack(pady=5)
        email_entry = tk.Entry(edit_win, width=40)
        email_entry.insert(0, curr_email)
        email_entry.pack(pady=5)

        # Password (hash)
        tk.Label(edit_win, text="Password Hash:", bg="#eef").pack(pady=5)
        password_entry = tk.Entry(edit_win, width=40)
        password_entry.insert(0, curr_password_hash)
        password_entry.pack(pady=5)

        # Save button
        def save_changes():
            new_username = username_entry.get().strip()
            new_email = email_entry.get().strip()
            new_password_hash = password_entry.get().strip()

            if not new_username or not new_email or not new_password_hash:
                messagebox.showwarning("Validation Error", "All fields are required.")
                return

            try:
                conn = create_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE users
                    SET username = %s, email = %s, password_hash = %s
                    WHERE id = %s
                """, (new_username, new_email, new_password_hash, user_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"User ID {user_id} updated.")
                self.load_users()
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(edit_win, text="Save Changes", bg="green", fg="white", command=save_changes).pack(pady=20)


