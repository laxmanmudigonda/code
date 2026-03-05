# utils/constants.py

# Column names
TARGET = 'Policy_Bind'
AGENT_TYPE = 'Agent_Type'
REGION = 'Region'
RE_QUOTE = 'Re_Quote'
QUOTED_PREMIUM = 'Quoted_Premium'
PREV_ACCIDENTS = 'Prev_Accidents'
PREV_CITATIONS = 'Prev_Citations'
DRIVING_EXP = 'Driving_Exp'
DRIVER_AGE = 'Driver_Age'

# Derived risk proxy
HIGH_RISK = 'High_Risk'

# Thresholds for decision routing (base values)
AUTO_BIND_THRESHOLD = 0.8
ESCALATE_LOW_CONFIDENCE = 0.6
REJECT_CONV_LOW = 0.2
REJECT_RISK_HIGH = 0.7

# Premium adjustment bounds
MAX_ADJUSTMENT = 0.15

# Regional/agent type performance (example – will be updated dynamically)
EA_CONVERSION_BOOST = 0.05   # EA agents have 5% higher base conversion
REGION_ADJUSTMENT = {         # Lower conversion regions get more lenient thresholds
    'A': 1.0,
    'B': 1.0,
    'C': 0.95,
    'D': 0.95,
    'E': 1.0,
    'F': 0.9,
    'G': 1.0,
    'H': 0.98
}