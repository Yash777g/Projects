# importing libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (classification_report, 
                            confusion_matrix, 
                            roc_auc_score,
                            precision_recall_curve,
                            average_precision_score)
from imblearn.over_sampling import SMOTE

# loading datasets
try:
    df = pd.read_csv("mightdeletelater\WA_Fn-UseC_-Telco-Customer-Churn.csv")
    print("Data loaded successfully!\nFirst 5 rows:")
    print(df.head())
    
    # Basic EDA
    print("\nMissing values per column:")
    print(df.isnull().sum())
    
    print("\nChurn distribution:")
    print(df['Churn'].value_counts())
    
    # Visualize churn distribution
    plt.figure(figsize=(8, 5))
    sns.countplot(x='Churn', data=df)
    plt.title("Customer Churn Distribution")
    plt.show()
    
except FileNotFoundError:
    print("ERROR: File not found. Please download the dataset from Kaggle:")
    print("https://www.kaggle.com/datasets/blastchar/telco-customer-churn")
    exit()

# Handle TotalCharges (contains empty strings)
# data cleaning 
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'].fillna(df['TotalCharges'].median(), inplace=True)

# Encode categorical variables
cat_cols = ['gender', 'Partner', 'Dependents', 'PhoneService', 'MultipleLines',
            'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
            'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract', 
            'PaperlessBilling', 'PaymentMethod']

le = LabelEncoder()
df[cat_cols] = df[cat_cols].apply(le.fit_transform)

# Drop customerID (not useful for modeling)
df.drop('customerID', axis=1, inplace=True)

# Convert target to binary
df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})

# training data
X = df.drop('Churn', axis=1)
y = df['Churn']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# Scale numerical features
num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
scaler = StandardScaler()
X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
X_test[num_cols] = scaler.transform(X_test[num_cols])

smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

print("\nClass distribution after SMOTE:")
print(pd.Series(y_train_res).value_counts())


# model training
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(random_state=42),
    "XGBoost": XGBClassifier(random_state=42, eval_metric='logloss')
}

results = {}
for name, model in models.items():
    # Train model
    model.fit(X_train_res, y_train_res)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # Store results
    results[name] = {
        'Classification Report': classification_report(y_test, y_pred),
        'Confusion Matrix': confusion_matrix(y_test, y_pred),
        'ROC AUC': roc_auc_score(y_test, y_prob),
        'AP Score': average_precision_score(y_test, y_prob)
    }
    
    # Print results
    print(f"\n{'-'*40}")
    print(f"Model: {name}")
    print(f"ROC AUC: {results[name]['ROC AUC']:.3f}")
    print(f"Average Precision: {results[name]['AP Score']:.3f}")
    print("\nClassification Report:")
    print(results[name]['Classification Report'])
    print("Confusion Matrix:")
    print(results[name]['Confusion Matrix'])

# feature selection
rf_model = models["Random Forest"]
importances = rf_model.feature_importances_
features = X.columns

# Create DataFrame and sort
feature_importance = pd.DataFrame({
    'Feature': features,
    'Importance': importances
}).sort_values('Importance', ascending=False)

# Plot top 10 features
plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=feature_importance.head(10))
plt.title("Top 10 Important Features (Random Forest)")
plt.tight_layout()
plt.show()

import joblib

# Save XGBoost model (best performer typically)
joblib.dump(models["XGBoost"], "best_churn_model.pkl")
print("\nModel saved as 'best_churn_model.pkl'")

def predict_churn(customer_data):
    """Predict churn for new customer data"""
    # Load model
    model = joblib.load("best_churn_model.pkl")
    
    # Preprocess input
    customer_df = pd.DataFrame([customer_data])
    customer_df[cat_cols] = customer_df[cat_cols].apply(le.fit_transform)
    customer_df[num_cols] = scaler.transform(customer_df[num_cols])
    
    # Predict
    prediction = model.predict(customer_df)
    probability = model.predict_proba(customer_df)[0][1]
    
    return {
        'Will Churn': 'Yes' if prediction[0] == 1 else 'No',
        'Probability': f"{probability:.2%}"
    }

# Example usage:
example_customer = {
    'gender': 'Female',
    'SeniorCitizen': 0,
    'Partner': 'Yes',
    'Dependents': 'No',
    'tenure': 12,
    'PhoneService': 'Yes',
    'MultipleLines': 'No',
    'InternetService': 'DSL',
    'OnlineSecurity': 'No',
    'OnlineBackup': 'Yes',
    'DeviceProtection': 'No',
    'TechSupport': 'No',
    'StreamingTV': 'Yes',
    'StreamingMovies': 'Yes',
    'Contract': 'Month-to-month',
    'PaperlessBilling': 'Yes',
    'PaymentMethod': 'Electronic check',
    'MonthlyCharges': 70.35,
    'TotalCharges': 850.75
}

print("\nExample Prediction:")
print(predict_churn(example_customer))