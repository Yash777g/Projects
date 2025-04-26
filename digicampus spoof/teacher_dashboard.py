import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class TeacherDashboard:
    def __init__(self, root, db, current_user, login_window):
        self.root = root
        self.db = db
        self.current_user = current_user
        self.login_window = login_window
        
        self.root.title(f"Teacher Dashboard - {current_user['name']}")
        self.root.geometry("1000x700")
        self.setup_ui()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_ui(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", pady=(10, 20), padx=20)
        
        ttk.Label(header_frame, text=f"Teacher Dashboard - Welcome {self.current_user['name']}", 
                 style="Header.TLabel").pack(side="left")
        ttk.Button(header_frame, text="Logout", command=self.logout).pack(side="right")
        
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill="both", expand=True)
        
        left_frame = ttk.LabelFrame(content_frame, text="Mark Attendance", padding=15)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.setup_attendance_marking(left_frame)
        
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        
        ttk.Button(right_frame, text="View All Records", command=self.view_all_attendance, width=25).pack(pady=10)
        ttk.Button(right_frame, text="View Today's Records", command=self.view_todays_attendance, width=25).pack(pady=10)
        ttk.Button(right_frame, text="Generate Report", command=self.generate_report, width=25).pack(pady=10)
    
    def setup_attendance_marking(self, parent):
        scroll_frame = ttk.Frame(parent)
        scroll_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(scroll_frame)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Label(scrollable_frame, text="Select Students", font=("Arial", 10, "bold")).pack(pady=(0, 10))
        
        students = self.db.fetch_all("SELECT id, name FROM users WHERE role = 'student'")
        self.student_vars = []
        self.status_vars = []
        
        for student in students:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill="x", pady=2)
            
            var = tk.IntVar()
            self.student_vars.append((student[0], var))
            
            ttk.Checkbutton(frame, text=student[1], variable=var).pack(side="left")
            
            status_var = tk.StringVar(value="present")
            self.status_vars.append(status_var)
            
            ttk.Radiobutton(frame, text="Present", variable=status_var, value="present").pack(side="left", padx=(10, 5))
            ttk.Radiobutton(frame, text="Absent", variable=status_var, value="absent").pack(side="left")
        
        ttk.Button(parent, text="Submit Attendance", command=self.submit_attendance_batch).pack(pady=10)
    
    def submit_attendance_batch(self):
        date = datetime.now().strftime("%Y-%m-%d")
        
        for student_id, var in self.student_vars:
            if var.get():
                status = self.status_vars[self.student_vars.index((student_id, var))].get()
                
                query = "SELECT * FROM attendance WHERE student_id = %s AND date = %s"
                if self.db.fetch_one(query, (student_id, date)):
                    continue
                
                query = "INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)"
                self.db.execute_query(query, (student_id, date, status))
        
        self.db.commit()
        messagebox.showinfo("Success", "Attendance marked successfully")
    
    def view_all_attendance(self):
        self.show_attendance_records("All Attendance Records", """
        SELECT u.name, a.date, a.status 
        FROM attendance a
        JOIN users u ON a.student_id = u.id
        ORDER BY a.date DESC, u.name
        """)
    
    def view_todays_attendance(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.show_attendance_records(f"Today's Attendance ({today})", """
        SELECT u.name, a.status 
        FROM attendance a
        JOIN users u ON a.student_id = u.id
        WHERE a.date = %s
        ORDER BY u.name
        """, (today,))
    
    def show_attendance_records(self, title, query, params=None):
        top = tk.Toplevel(self.root)
        top.title(title)
        top.geometry("800x500")
        
        ttk.Label(top, text=title, style="Header.TLabel").pack(pady=10)
        
        tree_frame = ttk.Frame(top)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("Student", "Date", "Status") if "date" in query.lower() else ("Student", "Status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200 if col == "Student" else 150, anchor="w" if col == "Student" else "center")
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        records = self.db.fetch_all(query, params or ())
        for record in records:
            tree.insert("", "end", values=record)
    
    def generate_report(self):
        top = tk.Toplevel(self.root)
        top.title("Generate Report")
        top.geometry("400x200")
        
        ttk.Label(top, text="Select Date Range", style="Header.TLabel").pack(pady=20)
        
        date_frame = ttk.Frame(top)
        date_frame.pack(pady=10)
        
        ttk.Label(date_frame, text="From:").grid(row=0, column=0, padx=5, pady=5)
        self.from_date = ttk.Entry(date_frame)
        self.from_date.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(date_frame, text="To:").grid(row=1, column=0, padx=5, pady=5)
        self.to_date = ttk.Entry(date_frame)
        self.to_date.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(top, text="Generate", command=self.display_report).pack(pady=20)
    
    def display_report(self):
        from_date = self.from_date.get()
        to_date = self.to_date.get()
        
        if not from_date or not to_date:
            messagebox.showerror("Error", "Please enter both dates")
            return
        
        query = """
        SELECT u.name, 
               COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present,
               COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as absent,
               COUNT(*) as total,
               ROUND(COUNT(CASE WHEN a.status = 'present' THEN 1 END) / COUNT(*) * 100, 2) as percentage
        FROM attendance a
        JOIN users u ON a.student_id = u.id
        WHERE a.date BETWEEN %s AND %s
        GROUP BY u.name
        ORDER BY percentage DESC
        """
        
        self.show_attendance_records(
            f"Attendance Report ({from_date} to {to_date})",
            query,
            (from_date, to_date)
        )
    
    def logout(self):
        self.root.destroy()
        self.login_window.deiconify()
    
    def on_close(self):
        self.logout()