import pandas as pd

class RiskAssessmentAgent:

    def __init__(self):
        print("Rule-Based Risk Model Loaded")

    def assess_risk(self, quote):

        accidents = quote.get("Prev_Accidents", 0)
        citations = quote.get("Prev_Citations", 0)
        age = quote.get("Driver_Age", 30)
        exp = quote.get("Driving_Exp", 5)

        risk_score = 0

        # accidents
        risk_score += accidents * 0.3

        # citations
        risk_score += citations * 0.2

        # young drivers
        if age < 25:
            risk_score += 0.2

        # low experience
        if exp < 3:
            risk_score += 0.2

        # normalize
        risk_prob = min(risk_score, 1.0)

        if risk_prob < 0.3:
            tier = 0
            tier_name = "Low"

        elif risk_prob < 0.6:
            tier = 1
            tier_name = "Medium"

        else:
            tier = 2
            tier_name = "High"

        return {
            "risk_probability": risk_prob,
            "risk_tier": tier,
            "risk_tier_name": tier_name,
            "explanation": f"Risk score calculated from accidents, citations, age and experience"
        }