import tkinter as tk
from tkinter import ttk, messagebox
from connection import *

conn = create_connection()
cursor = conn.cursor()


# === Restore Function ===
def restore_selected(tree, table):
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showinfo("No Selection", "Please select at least one record to restore.")
        return

    original_table = table.replace("del_", "")

    for item in selected_items:
        item_values = tree.item(item, 'values')

        # Get column names
        cursor.execute(f"SELECT * FROM {table} LIMIT 0")
        colnames = [desc[0] for desc in cursor.description]

        insert_cols = ", ".join(colnames)
        placeholders = ", ".join(["%s"] * len(item_values))
        insert_values = item_values

        try:
            # Insert into original table
            cursor.execute(
                f"INSERT INTO {original_table} ({insert_cols}) VALUES ({placeholders})",
                insert_values
            )

            # Delete from deleted table
            item_id = item_values[0]
            cursor.execute(f"DELETE FROM {table} WHERE id = %s", (item_id,))
        except Exception as e:
            messagebox.showerror("Restore Error", str(e))
    
    conn.commit()
    messagebox.showinfo("Restored", "Selected record(s) restored successfully.")
    refresh_tree(tree, table)


# === Delete Permanently Function ===
def delete_permanently(tree, table, create_sql):
    confirm = messagebox.askyesno("Delete Forever", f"This will delete all records in {table}.\nContinue?")
    if confirm:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        cursor.execute(create_sql)
        conn.commit()
        messagebox.showinfo("Deleted", f"{table} has been wiped clean.")
        refresh_tree(tree, table)


# === Refresh Treeview ===
def refresh_tree(tree, table):
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute(f"SELECT * FROM {table}")
    for row in cursor.fetchall():
        tree.insert('', tk.END, values=row)


# === Create Tree Tab ===
def create_tab(notebook, table, create_sql):
    frame = ttk.Frame(notebook, style="My.TFrame")
    notebook.add(frame, text=table.replace("del_", "").capitalize())

    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

    yscroll = ttk.Scrollbar(tree_frame, orient='vertical')
    yscroll.pack(side='right', fill='y')

    tree = ttk.Treeview(tree_frame, columns=[], show='headings', yscrollcommand=yscroll.set)
    tree.pack(fill='both', expand=True)
    yscroll.config(command=tree.yview)

    cursor.execute(f"SELECT * FROM {table} LIMIT 0")
    colnames = [desc[0] for desc in cursor.description]
    tree['columns'] = colnames
    for col in colnames:
        tree.heading(col, text=col)
        tree.column(col, anchor='center', stretch=True, width=100)

    refresh_tree(tree, table)

    btn_frame = ttk.Frame(frame)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="✅ Restore Selected", command=lambda: restore_selected(tree, table)).pack(side='left', padx=15)
    ttk.Button(btn_frame, text="❌ Delete Permanently", command=lambda: delete_permanently(tree, table, create_sql)).pack(side='left', padx=15)


# === Main Deleted Data Window ===
def open_deleted_data_window():
    root = tk.Tk()
    root.title("🗑️ View Deleted Data")
    root.geometry("1000x650")
    root.configure(bg="#d0e8f2")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#f0f8ff", foreground="#000000", rowheight=30,
                    fieldbackground="#f0f8ff", font=('Segoe UI', 10))
    style.map('Treeview', background=[('selected', '#66c2ff')])
    style.configure("TButton", font=('Segoe UI', 10, 'bold'), padding=6)

    tk.Label(root, text="🧾 View Deleted Data", font=("Segoe UI", 16, "bold"), bg="#d0e8f2", fg="#005f73").pack(pady=10)

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=15, pady=10)

    # Tabs for deleted tables
    create_tab(notebook, "del_users", """
    CREATE TABLE del_users (
        id int PRIMARY KEY,
        username VARCHAR(100),
        email VARCHAR(100),
        password_hash TEXT
    );
    """)

    create_tab(notebook, "del_orders", """
    CREATE TABLE del_orders (
        id int PRIMARY KEY,
        summary TEXT,
        item_names TEXT,
        quantities TEXT,
        order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    create_tab(notebook, "del_order_items", """
    CREATE TABLE del_order_items (
        id int PRIMARY KEY,
        order_id INTEGER,
        item_name TEXT,
        quantity INTEGER
    );
    """)

    create_tab(notebook, "del_checkouts", """
    CREATE TABLE del_checkouts (
        id int PRIMARY KEY,
        customer_name VARCHAR(100),
        order_id INTEGER NOT NULL,
        total_amount NUMERIC(10, 2)
    );
    """)

    create_tab(notebook, "del_menu_items", """
    CREATE TABLE del_menu_items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price NUMERIC(6, 2) NOT NULL,
        image TEXT,
        category TEXT,
        deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    create_tab(notebook, "del_feedbacks", """
    CREATE TABLE del_feedbacks (
        id SERIAL PRIMARY KEY,
        user_name VARCHAR(100) NOT NULL,
        order_id INTEGER,
        order_name TEXT NOT NULL,
        description TEXT,
        bad_order_image BYTEA,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    root.mainloop()

