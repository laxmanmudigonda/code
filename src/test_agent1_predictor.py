# test_agent1_predictor.py
from agent1_predictor import predict_risk_tier

# Example quote from raw data (you might have this in your system)
quote_example = {
    'Prev_Accidents': 0,
    'Prev_Citations': 0,
    'Driving_Exp': 10,
    'Driver_Age': 40,
    'Annual_Miles': 5000,
    'Veh_Usage': 'Pleasure'
}

tier, probs = predict_risk_tier(quote_example)
print(f"Risk Tier: {tier}")
print(f"Probabilities: {probs}")