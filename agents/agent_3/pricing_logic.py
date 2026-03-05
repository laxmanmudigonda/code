"""
Agent 3: Pricing Logic
Determines premium adjustment based on conversion probability
"""

def calculate_price(current_premium, probability):
    """
    Adjust premium based on predicted conversion probability

    Args:
        current_premium (float): original quoted premium
        probability (float): predicted conversion probability (0–1)

    Returns:
        suggested_premium (float)
        reason (str)
    """

    # Low probability → give strong discount
    if probability < 0.40:
        suggested = current_premium * 0.90
        reason = "Low probability → 10% discount applied"

    # Medium probability → small discount
    elif probability < 0.60:
        suggested = current_premium * 0.95
        reason = "Medium probability → 5% discount applied"

    # High probability → keep premium
    else:
        suggested = current_premium
        reason = "High probability → premium unchanged"

    return round(suggested, 2), reason


def explain_pricing(probability):
    """
    Optional helper to explain pricing decision
    """

    if probability < 0.40:
        return "Customer unlikely to convert, discount given to increase purchase chance."

    elif probability < 0.60:
        return "Customer moderately likely to convert, small discount applied."

    else:
        return "Customer likely to convert, no discount needed."