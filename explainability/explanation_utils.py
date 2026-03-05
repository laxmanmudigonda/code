# explainability/explanation_utils.py

def format_explanation(exp_dict):
    """Convert explanation dict to human‑readable string."""
    # Simple implementation
    lines = ["Key factors:"]
    for feat, weight in zip(exp_dict.get('feature', []), exp_dict.get('weight', [])):
        direction = "increases" if weight > 0 else "decreases"
        lines.append(f"  {feat} {direction} probability by {abs(weight):.2f}")
    return "\n".join(lines)