# explainability/shap_explainer.py

import shap
import pandas as pd
import numpy as np
import joblib

def explain_risk(model, quote_df, scaler):
    """Return SHAP force plot explanation as JSON."""
    # Scale the quote
    num_cols = ['HH_Vehicles', 'HH_Drivers', 'Driver_Age', 'Driving_Exp',
                'Prev_Accidents', 'Prev_Citations', 'Annual_Miles_Mid',
                'Vehicle_Cost_Mid', 'Salary_Mid', 'Quote_Valid_Days']
    X_scaled = quote_df.copy()
    X_scaled[num_cols] = scaler.transform(quote_df[num_cols])

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_scaled)
    # Return as dict for dashboard
    return {
        'base_value': explainer.expected_value,
        'values': shap_values[0].tolist(),
        'feature_names': X_scaled.columns.tolist(),
        'data': X_scaled.iloc[0].tolist()
    }

def explain_decision(model, X_enc):
    """SHAP for router (multi‑class)."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_enc)
    return {
        'base_values': explainer.expected_value.tolist(),
        'values': [sv[0].tolist() for sv in shap_values],
        'feature_names': X_enc.columns.tolist(),
        'data': X_enc.iloc[0].tolist()
    }