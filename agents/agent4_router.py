# agents/agent4_router.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Agent4DecisionRouter:
    """
    Agent 4 – Decision Router
    Combines outputs from Agents 1,2,3 into a final decision:
    - Auto-Approve
    - Agent Follow-Up
    - Escalate to Underwriter
    """
    def __init__(self, rule_based=True):
        # If rule_based, we use business rules; otherwise could load a model.
        self.rule_based = rule_based
        logger.info("Agent 4 initialized (rule-based)")

    def route(self, risk_tier, conversion_output, premium_output, agent_type, region):
        """
        Determine the final action.

        Parameters
        ----------
        risk_tier : str
            'Low', 'Medium', or 'High'
        conversion_output : dict
            Output from Agent 2, containing at least 'conversion_probability' and 'routing_decision'
        premium_output : dict
            Output from Agent 3, containing at least 'is_blocker', 'recommended_premium', etc.
        agent_type : str
            e.g., 'EA', 'IA', 'Online'
        region : str
            e.g., 'North', 'South', 'East', 'West'

        Returns
        -------
        dict
            Contains final decision and explanation.
        """
        conv_prob = conversion_output.get('conversion_probability', 0.5)
        is_blocker = premium_output.get('is_blocker', False)

        # Example rule-based logic – adjust according to your business rules
        if risk_tier == 'High' and conv_prob < 0.3:
            decision = 'Escalate to Underwriter'
            explanation = 'High risk and low conversion probability'
        elif risk_tier == 'Low' and conv_prob > 0.7 and not is_blocker:
            decision = 'Auto-Approve'
            explanation = 'Low risk, high conversion, premium not a blocker'
        elif is_blocker:
            decision = 'Agent Follow-Up (premium adjustment suggested)'
            explanation = 'Premium likely a blocker, agent can offer discount'
        elif conv_prob > 0.6:
            decision = 'Auto-Approve'
            explanation = 'Sufficient conversion probability'
        else:
            decision = 'Agent Follow-Up'
            explanation = 'Standard review needed'

        return {
            'decision': decision,
            'explanation': explanation,
            'processed_at': datetime.now().isoformat()
        }

# Singleton
_instance = None

def get_router():
    global _instance
    if _instance is None:
        _instance = Agent4DecisionRouter()
    return _instance

def route_decision(risk_tier, conversion_output, premium_output, agent_type, region):
    return get_router().route(risk_tier, conversion_output, premium_output, agent_type, region)