# train_agent1.py
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from pathlib import Path

# ============================
# 1. Load data
# ============================
data_path = Path(r'C:\Users\Nayanika\OneDrive\Documents\code\raw\Autonomous QUOTE AGENTS.csv')
df = pd.read_csv(data_path)

print("Data loaded. Shape:", df.shape)
print("First 5 rows:")
print(df.head())

# ============================
# 2. Convert Annual_Miles_Range to numeric
# ============================
def miles_range_to_midpoint(val):
    """Convert range strings like '> 55 K' to a numeric midpoint."""
    if pd.isna(val):
        return None
    val = str(val).strip()
    # Handle '<= 7.5 K' -> midpoint = (0 + 7500)/2 = 3750
    if val.startswith('<= '):
        num = float(val.replace('<= ', '').replace(' K', '')) * 1000
        return num / 2
    # Handle '> 7.5 K & <= 15 K' -> midpoint = (7500 + 15000)/2 = 11250
    elif '&' in val:
        parts = val.split('&')
        lower = float(parts[0].replace('> ', '').replace(' K', '')) * 1000
        upper = float(parts[1].replace('<= ', '').replace(' K', '')) * 1000
        return (lower + upper) / 2
    # Handle '> 55 K' -> choose a reasonable upper bound, e.g., 60,000
    elif val.startswith('> '):
        lower = float(val.replace('> ', '').replace(' K', '')) * 1000
        # Arbitrary: add 5,000 to the lower bound (adjust if needed)
        return lower + 5000
    else:
        # Fallback: return None
        return None

df['Annual_Miles_Numeric'] = df['Annual_Miles_Range'].apply(miles_range_to_midpoint)
print("Annual miles conversion sample:")
print(df[['Annual_Miles_Range', 'Annual_Miles_Numeric']].head(10))

# ============================
# 3. Create Risk_Tier using a simple rule
# ============================
# Note: Adjust weights based on business knowledge!
# For demonstration, we use: 
#   Risk_Score = Accidents*5 + Citations*3 - Driving_Exp*0.2 + Driver_Age*0.1 + (Annual_Miles_Numeric / 1000)
df['Risk_Score'] = (df['Prev_Accidents'] * 5) + \
                   (df['Prev_Citations'] * 3) - \
                   (df['Driving_Exp'] * 0.2) + \
                   (df['Driver_Age'] * 0.1) + \
                   (df['Annual_Miles_Numeric'] / 1000)

# Bin into 3 groups using quantiles (you can also use fixed thresholds)
df['Risk_Tier'] = pd.qcut(df['Risk_Score'], q=3, labels=['Low', 'Medium', 'High'])
print("\nRisk tier distribution:")
print(df['Risk_Tier'].value_counts())

# ============================
# 4. Prepare features (X) and target (y)
# ============================
feature_cols = ['Prev_Accidents', 'Prev_Citations', 'Driving_Exp', 
                'Driver_Age', 'Annual_Miles_Numeric', 'Veh_Usage']
target_col = 'Risk_Tier'

X = df[feature_cols].copy()
y = df[target_col]

# Rename for clarity (optional)
X.columns = ['Prev_Accidents', 'Prev_Citations', 'Driving_Exp', 
             'Driver_Age', 'Annual_Miles', 'Veh_Usage']

print("\nFeatures shape:", X.shape)
print("Target distribution:\n", y.value_counts())

# ============================
# 5. Handle missing values (just in case)
# ============================
numeric_cols = ['Prev_Accidents', 'Prev_Citations', 'Driving_Exp', 'Driver_Age', 'Annual_Miles']
for col in numeric_cols:
    X[col].fillna(X[col].median(), inplace=True)

X['Veh_Usage'].fillna(X['Veh_Usage'].mode()[0], inplace=True)

# ============================
# 6. Split into train/test
# ============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ============================
# 7. Preprocessing pipeline
# ============================
numeric_features = ['Prev_Accidents', 'Prev_Citations', 'Driving_Exp', 'Driver_Age', 'Annual_Miles']
categorical_features = ['Veh_Usage']

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric_features),
    ('cat', OneHotEncoder(drop='first'), categorical_features)
])

# ============================
# 8. Train Random Forest model
# ============================
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
])

print("\nTraining model...")
model.fit(X_train, y_train)
print("Training complete.")

# ============================
# 9. Evaluate
# ============================
y_pred = model.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ============================
# 10. Save model
# ============================
model_dir = Path.cwd() / 'models'
model_dir.mkdir(exist_ok=True)
model_path = model_dir / 'agent1_risk_profiler.pkl'
joblib.dump(model, model_path)
print(f"\nModel saved to {model_path}")