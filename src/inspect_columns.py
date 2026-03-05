import pandas as pd
from pathlib import Path

data_path = Path(r'C:\Users\admin\OneDrive\Desktop\autonomous-quote-agents\raw\Autonomous QUOTE AGENTS.csv')
df = pd.read_csv(data_path)

print("All column names:")
print(df.columns.tolist())
