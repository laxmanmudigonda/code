from agents import agent1, agent2, agent3, agent4

def run_pipeline(quote):
    q = quote.copy()
    risk_tier, probs = agent1.predict_risk_tier(q)
    conversion = agent2.predict_conversion(q, risk_tier)
    premium = agent3.analyze_premium(q, risk_tier, conversion)
    decision = agent4.route_decision(risk_tier, conversion, premium, q['Agent_Type'], q['Region'])
    return {
        'risk_tier': risk_tier,
        'conversion': conversion,
        'premium': premium,
        'decision': decision
    }
