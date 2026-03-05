import joblib
from pathlib import Path

# Load the model (adjust path if needed)
model_path = Path('models/agent1_risk_profiler.pkl')
model = joblib.load(model_path)

# Print the type of the loaded object
print("Model type:", type(model))

# Print the pipeline steps summary
print("\nPipeline steps:")
print(model)
