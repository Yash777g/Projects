import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class StudentDashboard:
    def __init__(self, root, db, current_user, login_window):
        self.root = root
        self.db = db
        self.current_user = current_user
        self.login_window = login_window
        
        self.root.title(f"Student Dashboard - {current_user['name']}")
        self.root.geometry("800x600")
        self.setup_ui()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_ui(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", pady=(10, 20), padx=20)
        
        ttk.Label(header_frame, text=f"Student Dashboard - Welcome {self.current_user['name']}", 
                 style="Header.TLabel").pack(side="left")
        ttk.Button(header_frame, text="Logout", command=self.logout).pack(side="right")
        
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill="both", expand=True)
        
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        
        ttk.Button(left_frame, text="View My Attendance", command=self.view_attendance, width=20).pack(pady=10)
        ttk.Button(left_frame, text="View Today's Status", command=self.view_todays_status, width=20).pack(pady=10)
        
        right_frame = ttk.LabelFrame(content_frame, text="Statistics", padding=15)
        right_frame.pack(side="right", fill="both", expand=True)
        
        self.display_stats(right_frame)
    
    def display_stats(self, parent):
        student_id = self.current_user['id']
        
        total = self.db.fetch_one("SELECT COUNT(*) FROM attendance WHERE student_id = %s", (student_id,))[0]
        present = self.db.fetch_one(
            "SELECT COUNT(*) FROM attendance WHERE student_id = %s AND status = 'present'", 
            (student_id,))[0]
        
        percentage = (present / total * 100) if total > 0 else 0
        
        ttk.Label(parent, text=f"Total Classes Attended: {total}").pack(anchor="w", pady=5)
        ttk.Label(parent, text=f"Present: {present}").pack(anchor="w", pady=5)
        ttk.Label(parent, text=f"Absent: {total - present}").pack(anchor="w", pady=5)
        ttk.Label(parent, text=f"Attendance Percentage: {percentage:.1f}%", 
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=10)
    
    def view_attendance(self):
        top = tk.Toplevel(self.root)
        top.title("My Attendance Records")
        top.geometry("600x400")
        
        ttk.Label(top, text="My Attendance Records", style="Header.TLabel").pack(pady=10)
        
        tree_frame = ttk.Frame(top)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("Date", "Status"), show="headings")
        tree.heading("Date", text="Date")
        tree.heading("Status", text="Status")
        tree.column("Date", width=150, anchor="center")
        tree.column("Status", width=100, anchor="center")
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        records = self.db.fetch_all(
            "SELECT date, status FROM attendance WHERE student_id = %s ORDER BY date DESC",
            (self.current_user['id'],))
        
        for record in records:
            tree.insert("", "end", values=record)
    
    def view_todays_status(self):
        today = datetime.now().strftime("%Y-%m-%d")
        result = self.db.fetch_one(
            "SELECT status FROM attendance WHERE student_id = %s AND date = %s",
            (self.current_user['id'], today))
        
        status = result[0] if result else "Not marked yet"
        messagebox.showinfo("Today's Status", f"Your attendance status for today:\n{status}")
    
    def logout(self):
        self.root.destroy()
        self.login_window.deiconify()
    
    def on_close(self):
        self.logout()