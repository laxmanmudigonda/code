# agents/agent1_risk_profiler/risk_model.py

import joblib
import pandas as pd
import numpy as np

class RiskProfilerModel:
    def __init__(self, model_path='models/risk_model.pkl',
                 scaler_path='models/scaler.pkl',
                 encoder_path='models/encoder.pkl'):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.encoder = joblib.load(encoder_path)

    def predict(self, X):
        """X is a DataFrame with raw features (already encoded if needed)."""
        # Scale numeric columns (same as training)
        num_cols = ['HH_Vehicles', 'HH_Drivers', 'Driver_Age', 'Driving_Exp',
                    'Prev_Accidents', 'Prev_Citations', 'Annual_Miles_Mid',
                    'Vehicle_Cost_Mid', 'Salary_Mid', 'Quote_Valid_Days']
        X_scaled = X.copy()
        X_scaled[num_cols] = self.scaler.transform(X[num_cols])
        proba = self.model.predict_proba(X_scaled)[:,1]
        return proba