class DecisionAgent:

    def make_decision(self, quote):

        prob = quote.get("conversion_probability", 50)

        premium = quote.get("Quoted_Premium", 0)

        if prob >= 70:
            action = "AUTO_APPROVE"

        elif prob >= 40:
            action = "OFFER_OPTIMIZED_PREMIUM"

        elif prob >= 20:
            action = "AGENT_FOLLOW_UP"

        else:
            action = "ESCALATE_TO_UNDERWRITER"

        return {
            "action": action,
            "final_premium": premium
        }