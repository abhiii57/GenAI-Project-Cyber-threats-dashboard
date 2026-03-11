import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

print("Loading dataset...")

# -----------------------------
# 1. Load Dataset
# -----------------------------

df = pd.read_csv("data/cleaned.csv")

print("Original dataset shape:", df.shape)

# -----------------------------
# 2. Clean Dataset
# -----------------------------

print("Cleaning dataset...")

df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

print("After cleaning:", df.shape)

# -----------------------------
# 3. Encode Labels
# -----------------------------

print("Encoding labels...")

df["Attack Type"] = df["Attack Type"].astype(str).str.lower()

df["Attack Type"] = df["Attack Type"].apply(
    lambda x: 0 if "normal" in x else 1
)

print("\nClass distribution:")
print(df["Attack Type"].value_counts())

# -----------------------------
# 4. Remove Non Numeric Columns
# -----------------------------

print("\nRemoving non numeric columns...")

for col in df.columns:
    if df[col].dtype == "object" and col != "Attack Type":
        df.drop(col, axis=1, inplace=True)

print("Remaining columns:", len(df.columns))

# -----------------------------
# 5. Split Features / Labels
# -----------------------------

X = df.drop("Attack Type", axis=1)
y = df["Attack Type"]

feature_names = X.columns.tolist()

print("\nTotal Features Used:", len(feature_names))

# -----------------------------
# 6. Feature Scaling
# -----------------------------

print("\nScaling features...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -----------------------------
# 7. Train / Validation / Test Split
# -----------------------------

print("\nSplitting dataset...")

X_train, X_temp, y_train, y_temp = train_test_split(
    X_scaled,
    y,
    test_size=0.30,
    stratify=y,
    random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    stratify=y_temp,
    random_state=42
)

print("Train size:", X_train.shape)
print("Validation size:", X_val.shape)
print("Test size:", X_test.shape)

# -----------------------------
# 8. Train Model
# -----------------------------

print("\nTraining Random Forest model...")

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    class_weight="balanced",
    n_jobs=-1,
    random_state=42
)

model.fit(X_train, y_train)

# -----------------------------
# 9. Validation Results
# -----------------------------

print("\nValidation Results")

val_pred = model.predict(X_val)

print("Validation Accuracy:", accuracy_score(y_val, val_pred))
print(classification_report(y_val, val_pred))

# -----------------------------
# 10. Test Results
# -----------------------------

print("\nTest Results")

test_pred = model.predict(X_test)

print("Test Accuracy:", accuracy_score(y_test, test_pred))
print(classification_report(y_test, test_pred))

# -----------------------------
# 11. Feature Importance
# -----------------------------

print("\nTop Important Features")

importance = model.feature_importances_
indices = np.argsort(importance)[::-1]

top_n = min(15, len(feature_names))

for i in range(top_n):
    print(f"{feature_names[indices[i]]}: {importance[indices[i]]:.4f}")

# -----------------------------
# 12. Save Model
# -----------------------------

print("\nSaving model...")

os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/intrusion_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")
joblib.dump(feature_names, "models/features.pkl")

print("\nModel saved successfully!")

print("""
Saved Files:

models/intrusion_model.pkl
models/scaler.pkl
models/features.pkl
""")

print("Expected feature count:", len(feature_names))