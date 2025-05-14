import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import psycopg2
from io import BytesIO
from connection import *

class AdminFeedbackScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Manage Feedbacks - Byte&Bite")
        self.geometry("950x550")
        self.configure(bg="#f5f5f5")

        self.create_widgets()
        self.load_feedbacks()

    def create_widgets(self):
        columns = ("id", "user_name", "order_id", "order_name", "description")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("user_name", text="User Name")
        self.tree.heading("order_id", text="Order ID")
        self.tree.heading("order_name", text="Order Name")
        self.tree.heading("description", text="Description")

        self.tree.column("id", width=50)
        self.tree.column("user_name", width=120)
        self.tree.column("order_id", width=80)
        self.tree.column("order_name", width=150)
        self.tree.column("description", width=250)

        self.tree.pack(pady=20, fill="both", expand=True)

        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack()

        tk.Button(btn_frame, text="Delete Feedback", bg="red", fg="white", width=15, command=self.delete_feedback).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Modify Feedback", bg="blue", fg="white", width=15, command=self.modify_feedback).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="View Image", bg="purple", fg="white", width=15, command=self.view_image).pack(padx=10, side=tk.LEFT)
        tk.Button(btn_frame, text="Refresh", bg="gray", fg="white", width=15, command=self.load_feedbacks).pack(padx=10, side=tk.LEFT)

    def load_feedbacks(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, user_name, order_id, order_name, description FROM feedbacks ORDER BY id DESC")
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_feedback(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Required", "Please select at least one feedback to delete.")
            return

        feedback_ids = [self.tree.item(item)["values"][0] for item in selected_items]
        confirm = messagebox.askyesno("Delete Confirmation", f"Delete selected feedback(s) with ID(s): {', '.join(map(str, feedback_ids))}?")
        if confirm:
            try:
                conn = create_connection()
                cur = conn.cursor()
                for fid in feedback_ids:
                    cur.execute("DELETE FROM feedbacks WHERE id = %s", (fid,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deleted", "Selected feedback(s) deleted successfully.")
                self.load_feedbacks()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def view_image(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a feedback to view its image.")
            return

        feedback_id = self.tree.item(selected)["values"][0]

        try:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT bad_order_image FROM feedbacks WHERE id = %s", (feedback_id,))
            result = cur.fetchone()
            conn.close()

            if result and result[0]:
                img_data = BytesIO(result[0])
                img = Image.open(img_data).resize((300, 300))
                img_tk = ImageTk.PhotoImage(img)

                img_win = tk.Toplevel(self)
                img_win.title(f"Bad Order Image - Feedback ID {feedback_id}")

                # Save reference to prevent garbage collection
                img_win.img_tk = img_tk

                img_label = tk.Label(img_win, image=img_tk)
                img_label.pack()
            else:
                messagebox.showinfo("No Image", "This feedback has no image attached.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def modify_feedback(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a feedback to modify.")
            return

        selected_data = self.tree.item(selected)["values"]
        feedback_id, curr_user_name, curr_order_id, curr_order_name, curr_description = selected_data

        edit_win = tk.Toplevel(self)
        edit_win.title(f"Modify Feedback ID {feedback_id}")
        edit_win.geometry("400x500")
        edit_win.configure(bg="#eef")

        def create_labeled_entry(label, default_value):
            tk.Label(edit_win, text=label, bg="#eef").pack(pady=5)
            entry = tk.Entry(edit_win, width=40)
            entry.insert(0, default_value)
            entry.pack(pady=5)
            return entry

        user_name_entry = create_labeled_entry("User Name:", curr_user_name)
        order_id_entry = create_labeled_entry("Order ID:", str(curr_order_id))
        order_name_entry = create_labeled_entry("Order Name:", curr_order_name)
        desc_entry = create_labeled_entry("Description:", curr_description)

        new_image_data = None

        def upload_image():
            nonlocal new_image_data
            filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
            if filepath:
                with open(filepath, "rb") as f:
                    new_image_data = f.read()
                messagebox.showinfo("Image Loaded", "Image loaded successfully!")

        tk.Button(edit_win, text="Upload New Image", command=upload_image).pack(pady=10)

        def save_changes():
            try:
                new_user_name = user_name_entry.get().strip()
                new_order_id = int(order_id_entry.get().strip())
                new_order_name = order_name_entry.get().strip()
                new_description = desc_entry.get().strip()

                if not all([new_user_name, new_order_name]):
                    messagebox.showwarning("Validation Error", "All fields must be filled properly.")
                    return

                conn = create_connection()
                cur = conn.cursor()

                if new_image_data:
                    cur.execute("""
                        UPDATE feedbacks
                        SET user_name=%s, order_id=%s, order_name=%s, description=%s, bad_order_image=%s
                        WHERE id=%s
                    """, (new_user_name, new_order_id, new_order_name, new_description, new_image_data, feedback_id))
                else:
                    cur.execute("""
                        UPDATE feedbacks
                        SET user_name=%s, order_id=%s, order_name=%s, description=%s
                        WHERE id=%s
                    """, (new_user_name, new_order_id, new_order_name, new_description, feedback_id))

                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Feedback ID {feedback_id} updated.")
                self.load_feedbacks()
                edit_win.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(edit_win, text="Save Changes", bg="green", fg="white", command=save_changes).pack(pady=20)



