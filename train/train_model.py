import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
df = pd.read_csv("raw/Autonomous QUOTE AGENTS.csv")

print("Dataset loaded successfully")

# Convert Yes/No to numbers
df["Policy_Bind"] = df["Policy_Bind"].map({"Yes":1, "No":0})

# Select important features
features = [
"Quoted_Premium",
"Coverage",
"Vehicl_Cost_Range",
"Sal_Range",
"Veh_Usage",
"Annual_Miles_Range"
]

X = df[features]
y = df["Policy_Bind"]

# Convert text to numbers
X = pd.get_dummies(X)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier()

model.fit(X_train, y_train)

print("Model training completed")

# Test model
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("Model Accuracy:", accuracy)

# Save model
joblib.dump(model, "conversion_model.pkl")

print("Model saved successfully")
