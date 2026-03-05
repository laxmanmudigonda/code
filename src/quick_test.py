# quick_test.py
import pandas as pd
import joblib
from pathlib import Path

model = joblib.load('models/agent1_risk_profiler.pkl')

# Create test quotes using the actual categories from training
test_quotes = pd.DataFrame([
    {'Prev_Accidents': 0, 'Prev_Citations': 0, 'Driving_Exp': 10, 'Driver_Age': 40, 'Annual_Miles': 5000, 'Veh_Usage': 'Pleasure'},
    {'Prev_Accidents': 2, 'Prev_Citations': 1, 'Driving_Exp': 2, 'Driver_Age': 22, 'Annual_Miles': 25000, 'Veh_Usage': 'Commute'},
    {'Prev_Accidents': 5, 'Prev_Citations': 3, 'Driving_Exp': 1, 'Driver_Age': 19, 'Annual_Miles': 40000, 'Veh_Usage': 'Business'}
])

predictions = model.predict(test_quotes)
probs = model.predict_proba(test_quotes)

for i, (pred, prob) in enumerate(zip(predictions, probs)):
    print(f"Quote {i+1}: Predicted = {pred}, Probabilities = {dict(zip(model.classes_, prob))}")