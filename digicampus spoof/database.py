import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector

# Database Connection
class Database:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_password_here",  # <-- replace with your MySQL password
            database="attendance_system"
        )
        self.cursor = self.db.cursor()

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor

    def commit(self):
        self.db.commit()

    def fetch_one(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchone()

    def fetch_all(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

db = Database()

# Ensure assignments and projects tables exist
db.execute_query('''
CREATE TABLE IF NOT EXISTS assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    due_date DATE,
    created_by INT
)
''')
db.execute_query('''
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    due_date DATE,
    created_by INT
)
''')
db.commit()
