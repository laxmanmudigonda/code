# tests/test_agent2.py

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.agent_2.conversion_agent import ConversionPredictorAgent


def test_agent2():

    print("=" * 60)
    print("TESTING AGENT 2 - CONVERSION PREDICTOR")
    print("=" * 60)

    agent = ConversionPredictorAgent()

    test_quote = {
        'quote_id': 'TEST001',
        'Risk_Tier': 0,
        'Re_Quote': 1,
        'Q_Valid_DT': 5,   # fixed
        'HH_Drivers': 2,
        'Coverage': 'Comprehensive',
        'Agent_Type': 'EA',
        'Region': 'North',
        'Sal_Range': '80-120k'
    }

    print(f"\nTesting quote: {test_quote['quote_id']}")

    result = agent.process_quote(test_quote)

    if result['agent_2_output']['status'] == 'success':

        print("\nSUCCESS")

        print("Conversion Probability:",
              result['agent_2_output']['conversion_probability'])

        print("Category:",
              result['agent_2_output']['probability_category'])

        print("Confidence:",
              result['agent_2_output']['confidence_score'])

        print("Routing:",
              result['agent_2_output']['routing_decision'])

        print("Explanation:",
              result['agent_2_output']['explanation'])

    else:
        print("\nFAILED")
        print(result['agent_2_output'])


if __name__ == "__main__":
    test_agent2()