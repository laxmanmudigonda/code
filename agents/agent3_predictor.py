# agents/agent3_predictor.py
import joblib
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Agent3PremiumAdvisor:
    """
    Agent 3 – Premium Advisor
    For high-propensity unconverted quotes, reasons whether Quoted_Premium
    is the conversion blocker. Recommends an adjusted premium band or
    alternative coverage tier.
    """
    def __init__(self, model_path='models/premium_model.pkl'):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path.absolute()}")
        self.model = joblib.load(self.model_path)
        logger.info(f"Agent 3 model loaded from {self.model_path}")

    def analyze(self, quote, risk_tier, conversion_output):
        """
        Analyze premium and recommend adjustments.

        Parameters
        ----------
        quote : dict
            Must contain 'Quoted_Premium', 'Coverage', 'Sal_Range', 'Vehicl_Cost_Range', 'Re_Quote'
        risk_tier : str
            Risk tier from Agent 1.
        conversion_output : dict
            Output from Agent 2 (containing at least conversion_probability).

        Returns
        -------
        dict
            Contains keys:
            - is_blocker (bool)         # whether premium is likely the blocker
            - recommended_premium (float) # suggested premium amount
            - recommended_coverage (str)   # suggested coverage tier
            - explanation (str)
            - status (str)
        """
        # Validate input
        required = ['Quoted_Premium', 'Coverage', 'Sal_Range', 'Vehicl_Cost_Range', 'Re_Quote']
        missing = [f for f in required if f not in quote]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        # Feature engineering (example – replace with actual)
        features = {
            'quoted_premium': quote['Quoted_Premium'],
            'risk_tier': risk_tier,
            'conversion_prob': conversion_output.get('conversion_probability', 0.5),
            're_quote': 1 if quote['Re_Quote'] == 'Yes' else 0,
            # ... more features
        }
        input_df = pd.DataFrame([features])

        # Predict using model (if model is a classifier or regressor)
        # For demo, we'll use a simple rule
        prob_blocker = 0.0  # replace with model.predict_proba(...)[0][1] if binary classifier

        # Dummy logic: if conversion prob is high but quote not bound, premium might be blocker
        conv_prob = conversion_output.get('conversion_probability', 0.5)
        if conv_prob > 0.6 and quote['Quoted_Premium'] > 800:
            is_blocker = True
            recommended_premium = quote['Quoted_Premium'] * 0.9  # 10% discount
            recommended_coverage = 'Liability'  # example downgrade
        elif conv_prob > 0.4 and quote['Quoted_Premium'] > 600:
            is_blocker = False
            recommended_premium = quote['Quoted_Premium']  # no change
            recommended_coverage = quote['Coverage']
        else:
            is_blocker = False
            recommended_premium = quote['Quoted_Premium']
            recommended_coverage = quote['Coverage']

        return {
            'is_blocker': is_blocker,
            'recommended_premium': recommended_premium,
            'recommended_coverage': recommended_coverage,
            'explanation': 'Premium analysis based on risk and conversion probability',
            'status': 'success'
        }

# Singleton
_instance = None

def get_agent():
    global _instance
    if _instance is None:
        _instance = Agent3PremiumAdvisor()
    return _instance

def analyze_premium(quote, risk_tier, conversion_output):
    return get_agent().analyze(quote, risk_tier, conversion_output)