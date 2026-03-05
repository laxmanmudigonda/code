# debug_model_predict.py
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agents.agent_2.conversion_agent import ConversionPredictorAgent
from agents.agent_2.conversion_model import ConversionModel

def debug_model_predict():
    print("=" * 60)
    print("DEBUGGING MODEL PREDICT METHOD")
    print("=" * 60)
    
    # Load the model directly
    model_path = os.path.join('agents', 'agent_2', 'conversion_model.pkl')
    print(f"\n📂 Loading model from: {model_path}")
    
    model = ConversionModel()
    model.load_model(model_path)
    
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
    
    print(f"\n📋 Test quote: {test_quote}")
    
    # Step 1: Preprocess the data
    print("\n🔧 Step 1: Preprocessing...")
    df = pd.DataFrame([test_quote])
    X = model.preprocessor.preprocess(df, fit_encoders=False)
    print(f"   Preprocessed data shape: {X.shape}")
    print(f"   Preprocessed columns: {X.columns.tolist()}")
    print(f"   Data types:\n{X.dtypes}")
    
    # Step 2: Try prediction
    print("\n🔧 Step 2: Making prediction...")
    try:
        proba = model.model.predict_proba(X)[:, 1]
        print(f"✅ Prediction successful! Probability: {proba[0]:.4f}")
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Check the model's predict method
    print("\n🔧 Step 3: Testing model.predict() method...")
    try:
        proba = model.predict(df)
        print(f"✅ model.predict() successful! Probability: {proba[0]:.4f}")
    except Exception as e:
        print(f"❌ model.predict() failed: {e}")
    
    # Step 4: Test the agent's process_quote method with our fixed preprocessor
    print("\n🔧 Step 4: Testing agent with our own preprocessing...")
    agent = ConversionPredictorAgent()
    
    # Manually set the preprocessor to ensure it's the updated version
    from agents.agent_2.preprocess import ConversionPreprocessor
    agent.model.preprocessor = ConversionPreprocessor()
    
    try:
        # Use the agent's process_quote but with our preprocessed data
        # First, let's see what the agent does internally
        print("   Calling agent.process_quote()...")
        result = agent.process_quote(test_quote)
        if result['agent_2_output']['status'] == 'success':
            print(f"✅ SUCCESS!")
            print(f"   Probability: {result['agent_2_output']['conversion_probability']}%")
        else:
            print(f"❌ Failed: {result['agent_2_output']}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_model_predict()