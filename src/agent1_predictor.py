# agent1_predictor.py
import pandas as pd
import joblib
from pathlib import Path

class Agent1RiskProfiler:
    def __init__(self, model_path='models/agent1_risk_profiler.pkl'):
        self.model = joblib.load(model_path)
        self.required_features = ['Prev_Accidents', 'Prev_Citations', 'Driving_Exp',
                                   'Driver_Age', 'Annual_Miles', 'Veh_Usage']
        # Known Veh_Usage categories (from training)
        self.valid_veh_usage = ['Commute', 'Pleasure', 'Business']

    def predict(self, quote_dict):
        """
        quote_dict: dictionary with keys matching required_features.
        Returns: predicted risk tier (string) and probabilities (dict).
        """
        # Validate input
        for feature in self.required_features:
            if feature not in quote_dict:
                raise ValueError(f"Missing feature: {feature}")

        # Ensure Veh_Usage is one of the known categories
        if quote_dict['Veh_Usage'] not in self.valid_veh_usage:
            # Option: map unknown to most common, or raise error
            # Here we'll raise a clear error
            raise ValueError(f"Unknown Veh_Usage '{quote_dict['Veh_Usage']}'. Must be one of {self.valid_veh_usage}")

        # Create DataFrame (model expects DataFrame)
        input_df = pd.DataFrame([quote_dict])

        # Predict
        pred = self.model.predict(input_df)[0]
        probs = self.model.predict_proba(input_df)[0]
        prob_dict = dict(zip(self.model.classes_, probs))
        return pred, prob_dict

# Optional: create a singleton instance for easy import
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = Agent1RiskProfiler()
    return _agent

def predict_risk_tier(quote_dict):
    return get_agent().predict(quote_dict)