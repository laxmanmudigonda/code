# debug_agent2_detailed.py
import sys
import os
import pandas as pd
import traceback

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agents.agent_2.conversion_agent import ConversionPredictorAgent

def debug_step_by_step():
    print("=" * 60)
    print("DETAILED STEP-BY-STEP DEBUGGING")
    print("=" * 60)
    
    # Initialize agent
    print("\n🔧 Initializing Agent...")
    agent = ConversionPredictorAgent()
    
    # Test quote
    test_quote = {
        'quote_id': 'TEST001',
        'Risk_Tier': 0,
        'Re_Quote': 1,
        'Q_Valid_DT': '2023/12/15',
        'HH_Drivers': 2,
        'Coverage': 'Comprehensive',
        'Agent_Type': 'EA',
        'Region': 'North',
        'Sal_Range': '80-120k'
    }
    
    print(f"\n📋 Original quote: {test_quote}")
    
    # Step through the process_quote method manually
    print("\n🔍 Step 1: Converting to DataFrame...")
    df = pd.DataFrame([test_quote])
    print(f"   DataFrame created with columns: {df.columns.tolist()}")
    print(f"   Q_Valid_DT type: {type(df['Q_Valid_DT'].iloc[0])}")
    print(f"   Q_Valid_DT value: {df['Q_Valid_DT'].iloc[0]}")
    
    print("\n🔍 Step 2: Accessing model's preprocessor...")
    print(f"   Model preprocessor exists: {agent.model.preprocessor is not None}")
    
    try:
        print("\n🔍 Step 3: Running preprocessor.preprocess()...")
        X = agent.model.preprocessor.preprocess(df, fit_encoders=False)
        print(f"✅ Preprocessing successful!")
        print(f"   Preprocessed data shape: {X.shape}")
        print(f"   Preprocessed columns: {X.columns.tolist()}")
        print(f"   Data types after preprocessing:")
        for col in X.columns:
            print(f"      {col}: {X[col].dtype}")
        print(f"   Q_Valid_DT value after preprocessing: {X['Q_Valid_DT'].iloc[0]}")
    except Exception as e:
        print(f"❌ Preprocessing failed at Step 3: {e}")
        traceback.print_exc()
        return
    
    try:
        print("\n🔍 Step 4: Running model.predict_proba()...")
        proba = agent.model.model.predict_proba(X)[:, 1]
        print(f"✅ Prediction successful! Probability: {proba[0]:.4f}")
    except Exception as e:
        print(f"❌ Prediction failed at Step 4: {e}")
        traceback.print_exc()
        return
    
    try:
        print("\n🔍 Step 5: Calculating confidence...")
        prob = proba[0]
        confidence = abs(prob - 0.5) * 2
        print(f"   Probability: {prob:.4f}")
        print(f"   Confidence: {confidence:.4f}")
        
        print("\n🔍 Step 6: Categorizing...")
        if prob >= 0.75:
            category = 'VERY_HIGH'
        elif prob >= 0.50:
            category = 'HIGH'
        elif prob >= 0.25:
            category = 'MEDIUM'
        elif prob >= 0.10:
            category = 'LOW'
        else:
            category = 'VERY_LOW'
        print(f"   Category: {category}")
        
        print("\n🔍 Step 7: Determining routing...")
        from agents.agent_2.config import ESCALATION_CONFIG, ROUTING_DECISIONS
        
        if prob >= ESCALATION_CONFIG['auto_approve']:
            routing = ROUTING_DECISIONS['auto_approve']
        elif prob >= ESCALATION_CONFIG['human_review_lower']:
            routing = ROUTING_DECISIONS['agent_follow_up']
        else:
            routing = ROUTING_DECISIONS['escalate']
        print(f"   Routing: {routing}")
        
        print("\n✅ All steps completed successfully!")
        
    except Exception as e:
        print(f"❌ Failed at later step: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_step_by_step()