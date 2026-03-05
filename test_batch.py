# test_batch.py
"""
Test batch processing with Agent 2 and Agent 3
"""

import pandas as pd
import numpy as np
from pipeline.quote_pipeline import QuotePipeline

def create_sample_batch(n_samples=10):
    """Create sample quotes for testing"""
    
    np.random.seed(42)
    
    quotes = []
    for i in range(n_samples):
        quote = {
            'quote_id': f'BATCH_{i:03d}',
            'Risk_Tier': np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2]),
            'Re_Quote': np.random.choice([0, 1], p=[0.7, 0.3]),
            'Q_Valid_DT': f'2023/12/{np.random.randint(1, 30):02d}',
            'HH_Drivers': np.random.randint(1, 5),
            'Coverage': np.random.choice(['Liability', 'Comprehensive', 'Collision']),
            'Agent_Type': np.random.choice(['EA', 'IA']),
            'Region': np.random.choice(['North', 'South', 'East', 'West']),
            'Sal_Range': np.random.choice(['<30k', '30-50k', '50-80k', '80-120k', '>120k']),
            'Quoted_Premium': np.random.randint(500, 2000)
        }
        quotes.append(quote)
    
    return pd.DataFrame(quotes)

def main():
    print("=" * 60)
    print("BATCH PROCESSING TEST")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = QuotePipeline()
    
    # Create sample batch
    batch_df = create_sample_batch(20)
    print(f"\n📊 Created batch with {len(batch_df)} quotes")
    
    # Process batch
    results = pipeline.process_batch(batch_df)
    
    # Display summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)
    
    summary = results['batch_summary']
    print(f"Total quotes processed: {summary['total_processed']}")
    print(f"Agent 2 success rate: {summary['agent2_success_rate']}")
    print(f"Agent 3 execution rate: {summary['agent3_execution_rate']}")
    
    print("\n📊 Routing Decisions:")
    for decision, count in summary['routing_decisions'].items():
        print(f"  {decision}: {count}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()