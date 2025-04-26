import tkinter as tk
from tkinter import ttk
from database import Database
from login_page import LoginPage

def configure_styles():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#f0f0f0")
    style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
    style.configure("TButton", font=("Arial", 10), padding=5)
    style.configure("Header.TLabel", font=("Arial", 16, "bold"))
    style.configure("Title.TLabel", font=("Arial", 20, "bold"))
    style.configure("TCombobox", padding=5)
    style.configure("Treeview", font=("Arial", 10))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    configure_styles()
    
    db = Database()
    login_page = LoginPage(root, db)
    
    root.mainloop()