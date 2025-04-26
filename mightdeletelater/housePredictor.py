import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests
from bs4 import BeautifulSoup

# sample data 
data = {
    'Size': [1200, 1500, 1800, 2000, 2400, 3000],
    'Locality': ['Urban', 'Suburban', 'Rural', 'Urban', 'Suburban', 'Urban'],
    'Region': ['Mumbai', 'Delhi', 'Bangalore', 'Mumbai', 'Hyderabad', 'Delhi'],
    'Seaview': [1, 0, 0, 1, 0, 0],
    'LandRate': [50000, 30000, 25000, 50000, 28000, 30000],
    'Price': [7500000, 4500000, 4500000, 10000000, 6720000, 9000000]
}

df = pd.DataFrame(data)

# Encode categorical variables
df = pd.get_dummies(df, columns=['Locality', 'Region'])

# training data
X = df.drop('Price', axis=1)
y = df['Price']

model = LinearRegression()
model.fit(X, y)

# replacing it with real data but might do it later due to legal reasons
def get_land_rate(region):
    """Mock function to simulate fetching land rates (replace with real scraping)"""
    rates = {
        'Mumbai': 50000,
        'Delhi': 30000,
        'Bangalore': 25000,
        'Hyderabad': 28000,
        'Chennai': 22000
    }
    return rates.get(region, 25000)  # Default if region not found

# gui
class HousePricePredictor:
    def __init__(self, root):
        self.root = root
        self.root.title("House Price Predictor")
        self.root.geometry("400x400")
        
        # Variables
        self.size = tk.DoubleVar()
        self.locality = tk.StringVar()
        self.region = tk.StringVar()
        self.seaview = tk.BooleanVar()
        self.land_rate = tk.DoubleVar()
        
        # Layout
        ttk.Label(root, text="House Features", font=('Arial', 14)).pack(pady=10)
        
        ttk.Label(root, text="Size (sq. ft.):").pack()
        ttk.Entry(root, textvariable=self.size).pack()
        
        ttk.Label(root, text="Locality:").pack()
        ttk.Combobox(root, textvariable=self.locality, 
                     values=["Urban", "Suburban", "Rural"]).pack()
        
        ttk.Label(root, text="Region:").pack()
        self.region_cb = ttk.Combobox(root, textvariable=self.region, 
                                    values=["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"])
        self.region_cb.pack()
        self.region_cb.bind("<<ComboboxSelected>>", self.update_land_rate)
        
        ttk.Label(root, text="Land Rate (₹/sq. ft.):").pack()
        ttk.Label(root, textvariable=self.land_rate).pack()
        
        ttk.Checkbutton(root, text="Seaview", variable=self.seaview).pack(pady=5)
        
        ttk.Button(root, text="Predict Price", command=self.predict).pack(pady=20)
        
        self.result_label = ttk.Label(root, text="", font=('Arial', 12))
        self.result_label.pack()
    
    def update_land_rate(self, event):
        """Update land rate when region changes"""
        region = self.region.get()
        rate = get_land_rate(region)
        self.land_rate.set(rate)
    
    def predict(self):
        """Predict house price based on inputs"""
        try:
            # Create input DataFrame
            input_data = {
                'Size': [self.size.get()],
                'Seaview': [1 if self.seaview.get() else 0],
                'LandRate': [self.land_rate.get()],
                'Locality_Urban': [1 if self.locality.get() == 'Urban' else 0],
                'Locality_Suburban': [1 if self.locality.get() == 'Suburban' else 0],
                'Locality_Rural': [1 if self.locality.get() == 'Rural' else 0],
                'Region_Bangalore': [1 if self.region.get() == 'Bangalore' else 0],
                'Region_Chennai': [1 if self.region.get() == 'Chennai' else 0],
                'Region_Delhi': [1 if self.region.get() == 'Delhi' else 0],
                'Region_Hyderabad': [1 if self.region.get() == 'Hyderabad' else 0],
                'Region_Mumbai': [1 if self.region.get() == 'Mumbai' else 0]
            }
            
            # Ensure all columns exist (some may be missing in input)
            input_df = pd.DataFrame(input_data)
            for col in X.columns:
                if col not in input_df.columns:
                    input_df[col] = 0
            
            # Reorder columns to match training data
            input_df = input_df[X.columns]
            
            # Predict
            price = model.predict(input_df)[0]
            self.result_label.config(text=f"Predicted Price: ₹{price:,.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = HousePricePredictor(root)
    root.mainloop()