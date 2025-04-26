import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector

class LoginSignupWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("DigiCampus - Login/Signup")
        self.root.geometry("400x400")
        self.setup_login()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_login(self):
        self.clear_frame()

        ttk.Label(self.root, text="Login to DigiCampus", font=("Arial", 16)).pack(pady=20)
        self.email_entry = ttk.Entry(self.root)
        self.email_entry.pack(pady=10)
        self.email_entry.insert(0, "Enter Email")

        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_entry.pack(pady=10)
        self.password_entry.insert(0, "Password")

        ttk.Button(self.root, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self.root, text="New user? Sign Up", command=self.setup_signup).pack()

    def setup_signup(self):
        self.clear_frame()

        ttk.Label(self.root, text="Signup to DigiCampus", font=("Arial", 16)).pack(pady=20)
        self.name_entry = ttk.Entry(self.root)
        self.name_entry.pack(pady=10)
        self.name_entry.insert(0, "Full Name")

        self.email_entry = ttk.Entry(self.root)
        self.email_entry.pack(pady=10)
        self.email_entry.insert(0, "Gmail Address")

        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_entry.pack(pady=10)
        self.password_entry.insert(0, "Password")

        self.confirm_password_entry = ttk.Entry(self.root, show="*")
        self.confirm_password_entry.pack(pady=10)
        self.confirm_password_entry.insert(0, "Confirm Password")

        ttk.Button(self.root, text="Sign Up", command=self.signup).pack(pady=10)
        ttk.Button(self.root, text="Already have account? Login", command=self.setup_login).pack()

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        user = db.fetch_one("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        if user:
            self.root.withdraw()
            user_data = {'id': user[0], 'name': user[1], 'email': user[2], 'role': user[4]}
            if user_data['role'] == "student":
                StudentDashboard(tk.Toplevel(), user_data, self.root)
            else:
                TeacherDashboard(tk.Toplevel(), user_data, self.root)
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")

    def signup(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        try:
            db.execute_query("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'student')",
                             (name, email, password))
            db.commit()
            messagebox.showinfo("Success", "Account created! You can now log in.")
            self.setup_login()
        except mysql.connector.errors.IntegrityError:
            messagebox.showerror("Error", "Email already exists!")
