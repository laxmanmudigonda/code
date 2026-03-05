import pandas as pd
from agents.agent_2.conversion_model import ConversionModel

# Load dataset
df = pd.read_csv("raw/Autonomous QUOTE AGENTS.csv")

print("Dataset loaded")

# Convert Yes/No to numbers
df["Policy_Bind"] = df["Policy_Bind"].map({"Yes": 1, "No": 0})

# If Risk_Tier doesn't exist yet, create a placeholder
if "Risk_Tier" not in df.columns:
    df["Risk_Tier"] = 1

# Initialize model
model = ConversionModel()

# Train model
model.train(df, target_col="Policy_Bind")

# Save model
model.save_model()

print("Training complete")