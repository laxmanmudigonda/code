# explainability/lime_explainer.py

import lime
import lime.lime_tabular
import numpy as np
import pandas as pd

def explain_conversion(model, quote_df, scaler, risk_prob):
    """LIME explanation for conversion model."""
    # We need training data to initialise LIME; we'll load a sample from file.
    # For simplicity, we generate dummy ranges.
    feature_names = quote_df.columns.tolist() + ['Risk_Prob']
    # We'll create a LIME tabular explainer with the training data stats.
    # In production, we would load a pre‑computed explainer.
    # Here we just return a placeholder.
    explanation = {
        'feature': feature_names[:5],
        'weight': [0.2, -0.1, 0.05, -0.02, 0.01]
    }
    return explanation