# tests/test_agent3.py
"""
Comprehensive test for Agent 3 - Premium Advisor
"""

import sys
import os
import random
from datetime import datetime

# Add the project root directory to Python path
# This fixes the "No module named 'agents'" error
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import from agents
from agents.agent_3.premium_advisor import PremiumAdvisorAgent

def print_separator(title=None):
    """Print a nice separator"""
    if title:
        print("\n" + "=" * 70)
        print(f" {title}")
        print("=" * 70)
    else:
        print("\n" + "-" * 70)

def test_agent3_standalone():
    """Test 1: Agent 3 standalone with simulated Agent 2 data"""
    print_separator("TEST 1: AGENT 3 STANDALONE (with simulated Agent 2 data)")
    
    # Initialize Agent 3
    advisor = PremiumAdvisorAgent()
    
    # Test quotes with simulated Agent 2 output
    test_quotes = [
        {
            'quote_id': 'Q001',
            'Risk_Tier': 0,
            'Re_Quote': 1,
            'Q_Valid_DT': '2023/12/15',
            'HH_Drivers': 2,
            'Coverage': 'Comprehensive',
            'Agent_Type': 'EA',
            'Region': 'North',
            'Sal_Range': '80-120k',
            'Quoted_Premium': 850,
            # Simulated Agent 2 output
            'conversion_probability': 75.5,
            'conversion_category': 'HIGH',
            'conversion_confidence': 85.2
        },
        {
            'quote_id': 'Q002',
            'Risk_Tier': 1,
            'Re_Quote': 0,
            'Q_Valid_DT': '2023/12/10',
            'HH_Drivers': 3,
            'Coverage': 'Collision',
            'Agent_Type': 'IA',
            'Region': 'South',
            'Sal_Range': '50-80k',
            'Quoted_Premium': 1200,
            # Simulated Agent 2 output
            'conversion_probability': 45.2,
            'conversion_category': 'MEDIUM',
            'conversion_confidence': 78.3
        },
        {
            'quote_id': 'Q003',
            'Risk_Tier': 2,
            'Re_Quote': 1,
            'Q_Valid_DT': '2023/12/05',
            'HH_Drivers': 1,
            'Coverage': 'Liability',
            'Agent_Type': 'EA',
            'Region': 'East',
            'Sal_Range': '<30k',
            'Quoted_Premium': 950,
            # Simulated Agent 2 output
            'conversion_probability': 15.3,
            'conversion_category': 'LOW',
            'conversion_confidence': 92.1
        }
    ]
    
    for quote in test_quotes:
        print(f"\n📋 Processing Quote: {quote['quote_id']}")
        print(f"   Original Premium: ${quote['Quoted_Premium']}")
        print(f"   Agent 2 Probability: {quote['conversion_probability']}%")
        
        # Process through Agent 3
        result = advisor.process_quote(quote)
        agent3 = result['agent_3_output']
        
        print(f"\n   📊 RESULTS:")
        print(f"      Premium Blocker: {agent3['is_premium_blocker']}")
        print(f"      Recommended: ${agent3['recommended_premium']:.2f}")
        print(f"      Adjustment: {agent3['premium_adjustment_type']} ({agent3['premium_adjustment_percentage']}%)")
        print(f"      Needs Review: {agent3['needs_human_review']}")
        print(f"      📝 {agent3['explanation']}")

def test_agent3_fallback_mode():
    """Test 2: Agent 3 with fallback (no Agent 2 data provided)"""
    print_separator("TEST 2: AGENT 3 FALLBACK MODE")
    
    advisor = PremiumAdvisorAgent()
    
    fallback_quotes = [
        {
            'quote_id': 'F001',
            'Risk_Tier': 0,
            'Re_Quote': 1,
            'Q_Valid_DT': '2023/12/15',
            'HH_Drivers': 2,
            'Coverage': 'Comprehensive',
            'Agent_Type': 'EA',
            'Region': 'North',
            'Sal_Range': '80-120k',
            'Quoted_Premium': 850
            # No conversion_probability provided
        }
    ]
    
    for quote in fallback_quotes:
        print(f"\n📋 Processing Quote: {quote['quote_id']} (no Agent 2 data)")
        result = advisor.process_quote(quote)
        agent3 = result['agent_3_output']
        
        print(f"   Calculated Probability: {agent3['conversion_probability_used']:.1%}")
        print(f"   Recommended: ${agent3['recommended_premium']:.2f}")

def test_batch_processing():
    """Test 3: Batch processing"""
    print_separator("TEST 3: BATCH PROCESSING")
    
    advisor = PremiumAdvisorAgent()
    
    # Generate random batch
    batch = []
    for i in range(5):
        quote = {
            'quote_id': f'BATCH_{i:03d}',
            'Risk_Tier': random.randint(0, 2),
            'Re_Quote': random.choice([0, 1]),
            'Q_Valid_DT': f'2023/12/{random.randint(1, 28):02d}',
            'HH_Drivers': random.randint(1, 4),
            'Coverage': random.choice(['Liability', 'Collision', 'Comprehensive']),
            'Agent_Type': random.choice(['EA', 'IA']),
            'Region': random.choice(['North', 'South', 'East', 'West']),
            'Sal_Range': random.choice(['<30k', '30-50k', '50-80k', '80-120k', '>120k']),
            'Quoted_Premium': random.randint(400, 1500),
            'conversion_probability': random.uniform(5, 95)
        }
        batch.append(quote)
    
    print(f"📦 Processing batch of {len(batch)} quotes...")
    results = advisor.batch_process(batch)
    
    stats = results['statistics']
    print(f"\n📊 BATCH SUMMARY:")
    print(f"   Total Processed: {results['total_processed']}")
    print(f"   Total Discounts: ${stats['total_discount']:.2f}")
    print(f"   Total Increases: ${stats['total_increase']:.2f}")
    print(f"   Premium Blockers: {stats['blocker_count']}")

def main():
    """Run all tests"""
    print("\n" + "🚀" * 35)
    print("🚀 AGENT 3 - COMPREHENSIVE TEST SUITE")
    print("🚀" * 35)
    
    # Verify paths
    print(f"Project root: {os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))}")
    print(f"Agents folder exists: {os.path.exists('../agents')}")
    
    # Run tests
    test_agent3_standalone()
    test_agent3_fallback_mode()
    test_batch_processing()
    
    print_separator("TEST SUMMARY")
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    main()