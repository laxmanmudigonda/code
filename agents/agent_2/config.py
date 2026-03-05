# agents/agent2_conversion_predictor/config.py
"""
Agent 2 specific configuration
"""

# Model parameters
MODEL_CONFIG = {
    'random_state': 42,
    'test_size': 0.2,
    'n_estimators': 300,
    'max_depth': 6,
    'learning_rate': 0.05,
}

# Feature definitions
FEATURES = {
    'numerical': [
        'Risk_Tier',        # From Agent 1 (0=Low, 1=Medium, 2=High)
        'Re_Quote',          # 0 or 1 (after conversion)
        'Q_Valid_DT',        # Days until quote expires (converted from date)
        'HH_Drivers'         # Number of drivers in household
    ],
    'categorical': [
        'Coverage',          # Liability, Comprehensive, Collision
        'Agent_Type',        # EA or IA
        'Region',            # North, South, East, West
        'Sal_Range'          # <30k, 30-50k, 50-80k, 80-120k, >120k
    ]
}

# Conversion probability thresholds
CONVERSION_THRESHOLDS = {
    'very_high': 0.75,   # >75%
    'high': 0.50,        # 50-75%
    'medium': 0.25,      # 25-50%
    'low': 0.10,         # 10-25%
    'very_low': 0.0      # <10%
}

# Routing decisions
ROUTING_DECISIONS = {
    'auto_approve': 'AUTO_APPROVE',
    'agent_follow_up': 'AGENT_FOLLOW_UP',
    'escalate': 'ESCALATE_TO_UNDERWRITER'
}

# Escalation thresholds
ESCALATION_CONFIG = {
    'confidence_threshold': 0.85,           # Escalate if confidence < 85%
    'human_review_lower': 0.15,             # 15-30% need human review
    'human_review_upper': 0.30,
    'auto_approve': 0.75,                    # >75% auto-approve
    'auto_reject': 0.15                       # <15% auto-reject
}

# Paths
MODEL_PATH = 'models/conversion_model.pkl'