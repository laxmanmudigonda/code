import sys
import os
from datetime import datetime
import numpy as np

# Allow pipeline to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_1.risk_assessor import RiskAssessmentAgent
from agents.agent_2.conversion_agent import ConversionPredictorAgent
from agents.agent_3.premium_advisor import PremiumAdvisorAgent
from agents.agent_4.decision_agent import DecisionAgent


def clean_numpy(value):
    """Convert numpy types to Python native types."""
    if isinstance(value, np.generic):
        return value.item()
    return value


class QuotePipeline:

    def __init__(self):

        print("=" * 60)
        print("INITIALIZING QUOTE PIPELINE")
        print("=" * 60)

        try:
            self.agent1 = RiskAssessmentAgent()
            print("Agent 1 (Risk Profiler) Loaded")
        except Exception as e:
            print("Agent 1 failed:", e)
            self.agent1 = None

        try:
            self.agent2 = ConversionPredictorAgent()
            print("Agent 2 (Conversion Predictor) Loaded")
        except Exception as e:
            print("Agent 2 failed:", e)
            self.agent2 = None

        try:
            self.agent3 = PremiumAdvisorAgent()
            print("Agent 3 (Premium Advisor) Loaded")
        except Exception as e:
            print("Agent 3 failed:", e)
            self.agent3 = None

        try:
            self.agent4 = DecisionAgent()
            print("Agent 4 (Decision Agent) Loaded")
        except Exception as e:
            print("Agent 4 failed:", e)
            self.agent4 = None

        print("=" * 60)

    def run(self, quote):

        result = {
            "quote_id": quote.get("quote_id", "UNKNOWN"),
            "timestamp": datetime.now().isoformat(),
            "agent_outputs": {},
            "final_decision": None
        }

        print("\nINPUT QUOTE")
        print(quote)

        # Feature engineering
        if "Q_Valid_DT" in quote:
            quote["Quote_Valid_Days"] = quote["Q_Valid_DT"]

        quote["expires_soon"] = 1 if quote.get("Q_Valid_DT", 10) <= 7 else 0
        quote["multiple_drivers"] = 1 if quote.get("HH_Drivers", 1) > 1 else 0

        # =========================
        # Agent 1 — Risk
        # =========================

        if self.agent1:
            try:

                print("\nRunning Agent 1 (Risk Profiler)...")

                risk_result = self.agent1.assess_risk(quote)

                quote["Risk_Tier"] = risk_result["risk_tier"]

                result["agent_outputs"]["agent1"] = risk_result

                print("Risk Probability:", risk_result["risk_probability"])
                print("Risk Tier:", risk_result["risk_tier_name"])

            except Exception as e:
                print("Agent 1 error:", e)
                quote["Risk_Tier"] = 1

        # =========================
        # Agent 2 — Conversion
        # =========================

        if self.agent2:
            try:

                print("\nRunning Agent 2 (Conversion Predictor)...")

                agent2_result = self.agent2.process_quote(quote)

                agent2_output = agent2_result["agent_2_output"]

                if agent2_output["status"] != "success":
                    raise ValueError("Agent 2 prediction failed")

                conversion_prob = clean_numpy(
                    agent2_output["conversion_probability"]
                )

                quote["conversion_probability"] = conversion_prob

                result["agent_outputs"]["agent2"] = agent2_output

                print("Conversion Probability:", conversion_prob)
                print("Routing:", agent2_output["routing_decision"])

            except Exception as e:

                print("Agent 2 error:", e)

                quote["conversion_probability"] = 35

        # =========================
        # Agent 3 — Premium
        # =========================

        if self.agent3:
            try:

                print("\nRunning Agent 3 (Premium Advisor)...")

                agent3_result = self.agent3.process_quote(quote)

                agent3_output = agent3_result["agent_3_output"]

                recommended = clean_numpy(
                    agent3_output["recommended_premium"]
                )

                quote["Suggested_Premium"] = recommended
                quote["Quoted_Premium"] = recommended

                result["agent_outputs"]["agent3"] = agent3_output

                print("Original Premium:", agent3_output["original_premium"])
                print("Recommended Premium:", recommended)

            except Exception as e:

                print("Agent 3 error:", e)

        # =========================
        # Agent 4 — Decision
        # =========================

        if self.agent4:

            try:

                print("\nRunning Agent 4 (Decision Agent)...")

                decision = self.agent4.make_decision(quote)

                result["agent_outputs"]["agent4"] = decision
                result["final_decision"] = decision

                print("Final Decision:", decision)

            except Exception as e:
                print("Agent 4 error:", e)

        return result


if __name__ == "__main__":

    pipeline = QuotePipeline()

    sample_quote = {

        "quote_id": "Q1001",

        "HH_Vehicles": 2,
        "HH_Drivers": 2,
        "Driver_Age": 35,
        "Driving_Exp": 10,
        "Prev_Accidents": 0,
        "Prev_Citations": 1,

        "Annual_Miles_Mid": 12000,
        "Vehicle_Cost_Mid": 25000,
        "Salary_Mid": 85000,

        "Coverage": "Comprehensive",
        "Agent_Type": "EA",
        "Region": "West",
        "Sal_Range": "80-120k",

        "Re_Quote": 1,
        "Quoted_Premium": 700,

        "Q_Valid_DT": 5
    }

    output = pipeline.run(sample_quote)

    print("\nFINAL PIPELINE RESULT")
    print(output)