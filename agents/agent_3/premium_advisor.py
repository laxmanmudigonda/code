# agents/agent_3/premium_advisor.py
"""
Agent 3: Premium Advisor Agent
Integrates with Agent 2 for conversion-based premium adjustments
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Tuple, Optional, Any

# Add parent directory to path so we can find agent_2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Agent 2
try:
    from agent_2.conversion_agent import ConversionPredictorAgent
except ImportError:
    # Alternative import path if module structure is different
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from agents.agent_2.conversion_agent import ConversionPredictorAgent


class PremiumAdvisorAgent:
    """
    Agent 3: Recommends premium adjustments based on conversion probability
    Receives enriched data from Agent 2 and provides premium recommendations
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize Premium Advisor Agent
        
        Args:
            model_path: Optional path to Agent 2 model (if None, uses default)
        """
        print("=" * 60)
        print("💰 [Agent 3] Initializing Premium Advisor Agent")
        print("=" * 60)
        
        # Initialize Agent 2 (optional - can also receive probability from pipeline)
        self.agent2 = None
        self._load_agent2(model_path)
        
        # Pricing configuration based on conversion probability
        self.pricing_tiers = {
            'VERY_LOW': {'threshold': 0.15, 'discount': 0.80, 'name': 'Very Low', 'action': 'AGGRESSIVE_DISCOUNT'},
            'LOW': {'threshold': 0.30, 'discount': 0.85, 'name': 'Low', 'action': 'MODERATE_DISCOUNT'},
            'MEDIUM': {'threshold': 0.50, 'discount': 0.92, 'name': 'Medium', 'action': 'SLIGHT_DISCOUNT'},
            'HIGH': {'threshold': 0.75, 'discount': 1.00, 'name': 'High', 'action': 'NO_CHANGE'},
            'VERY_HIGH': {'threshold': 1.00, 'discount': 1.05, 'name': 'Very High', 'action': 'SLIGHT_INCREASE'}
        }
        
        # Premium adjustment limits
        self.max_discount = 0.30  # Max 30% discount
        self.max_increase = 0.10   # Max 10% increase
        
        print("\n✅ Agent 3 ready to process quotes")
    
    def _load_agent2(self, model_path: Optional[str] = None):
        """Load Agent 2 model (optional)"""
        try:
            if model_path:
                self.agent2 = ConversionPredictorAgent(model_path=model_path)
            else:
                self.agent2 = ConversionPredictorAgent()
            print("   ✅ Agent 2 loaded successfully (optional)")
        except Exception as e:
            print(f"   ⚠️ Agent 2 not loaded: {e}")
            print("   Agent 3 will use probability from pipeline input")
    
    def process_quote(self, quote_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a quote through Agent 3 (Main entry point for pipeline)
        
        Args:
            quote_data: Dictionary containing:
                - Original quote data
                - conversion_probability (from Agent 2)
                - conversion_category (from Agent 2)
                - conversion_confidence (from Agent 2)
                - Quoted_Premium (original premium)
        
        Returns:
            Dictionary with premium recommendations
        """
        quote_id = quote_data.get('quote_id', 'UNKNOWN')
        
        print(f"\n📝 Agent 3 processing quote {quote_id}...")
        
        # Get conversion probability (either from input or calculate)
        conversion_prob = self._get_conversion_probability(quote_data)
        
        # Get original premium
        original_premium = float(quote_data.get('Quoted_Premium', 500))
        
        # Determine if premium is a blocker
        is_blocker, blocker_reason = self._is_premium_blocker(quote_data, conversion_prob)
        
        # Calculate recommended premium
        recommended_premium, adjustment_type, adjustment_pct = self._calculate_recommended_premium(
            original_premium, conversion_prob, quote_data
        )
        
        # Generate premium band recommendation
        premium_band = self._get_premium_band(recommended_premium, original_premium)
        
        # Prepare output for Agent 4
        agent3_output = {
            'quote_id': quote_id,
            'status': 'success',
            'processed_at': datetime.now().isoformat(),
            
            # Input data
            'original_premium': original_premium,
            'conversion_probability_used': conversion_prob,
            
            # Analysis results
            'is_premium_blocker': is_blocker,
            'blocker_reason': blocker_reason if is_blocker else None,
            'premium_sensitivity': self._assess_premium_sensitivity(quote_data, conversion_prob),
            
            # Recommendations
            'recommended_premium': recommended_premium,
            'premium_adjustment_type': adjustment_type,
            'premium_adjustment_percentage': adjustment_pct,
            'premium_band': premium_band,
            'alternative_coverage_tier': self._suggest_alternative_coverage(quote_data, conversion_prob),
            
            # Flags for Agent 4
            'needs_human_review': self._needs_human_review(conversion_prob, original_premium, recommended_premium),
            'escalation_reason': self._get_escalation_reason(conversion_prob, original_premium, recommended_premium),
            'confidence_in_recommendation': self._calculate_confidence(conversion_prob, quote_data),
            
            # Explanation
            'explanation': self._generate_explanation(
                original_premium, recommended_premium, conversion_prob, is_blocker
            ),
            
            # For dashboard
            'summary': f"Premium: ${original_premium:.2f} → ${recommended_premium:.2f} ({adjustment_type})"
        }
        
        print(f"   ✅ Agent 3: {agent3_output['summary']}")
        
        return {
            'quote_id': quote_id,
            'agent_3_output': agent3_output,
            'agent_3_status': 'success'
        }
    
    def _get_conversion_probability(self, quote_data: Dict[str, Any]) -> float:
        """
        Get conversion probability from either:
        1. Already computed by Agent 2 (in pipeline)
        2. Calculate using Agent 2 if available
        3. Fallback calculation
        
        Returns:
            Probability between 0 and 1
        """
        # Check if probability already exists (from Agent 2 in pipeline)
        if 'conversion_probability' in quote_data:
            prob = quote_data['conversion_probability'] / 100.0  # Convert from percentage
            print(f"   📊 Using Agent 2 probability: {prob:.2%}")
            return prob
        
        # Try to use Agent 2 to calculate
        if self.agent2:
            try:
                prob = self.agent2.predict_probability(quote_data)
                print(f"   🤖 Calculated probability via Agent 2: {prob:.2%}")
                return prob
            except Exception as e:
                print(f"   ⚠️ Agent 2 calculation failed: {e}")
        
        # Fallback: calculate based on risk tier and re-quote status
        print("   ⚠️ Using fallback probability calculation")
        risk_tier = quote_data.get('Risk_Tier', 1)
        re_quote = quote_data.get('Re_Quote', 0)
        
        # Convert string Re_Quote to numeric if needed
        if isinstance(re_quote, str):
            re_quote = 1 if re_quote.lower() in ['yes', 'y', '1', 'true'] else 0
        
        # Simple fallback logic
        base_prob = 0.20  # Base 20%
        
        # Risk tier adjustments
        if risk_tier == 0:  # Low risk
            base_prob += 0.15
        elif risk_tier == 2:  # High risk
            base_prob -= 0.08
        
        # Re-quote bonus
        if re_quote:
            base_prob += 0.10
        
        # Validity bonus
        valid_days = quote_data.get('Q_Valid_DT', 14)
        if isinstance(valid_days, str):
            # Could be date string, use default
            valid_days = 14
        base_prob += min(valid_days * 0.005, 0.10)  # Max 10% bonus
        
        return min(max(base_prob, 0.05), 0.95)  # Cap between 5% and 95%
    
    def _is_premium_blocker(self, quote_data: Dict[str, Any], probability: float) -> Tuple[bool, Optional[str]]:
        """
        Determine if quoted premium is blocking conversion
        """
        original_premium = float(quote_data.get('Quoted_Premium', 500))
        
        # Get salary range
        salary = quote_data.get('Sal_Range', '50-80k')
        
        # Estimate expected premium based on salary
        expected_premium = self._estimate_expected_premium(salary, quote_data)
        
        # Calculate premium ratio
        premium_ratio = original_premium / expected_premium if expected_premium > 0 else 1.0
        
        # Determine if premium is too high
        if premium_ratio > 1.3:  # 30% above expected
            return True, f"Premium ${original_premium:.2f} is {((premium_ratio-1)*100):.0f}% above expected for salary range {salary}"
        elif probability < 0.3 and premium_ratio > 1.1:
            return True, f"Low conversion probability ({probability:.1%}) combined with premium {((premium_ratio-1)*100):.0f}% above expected"
        elif probability < 0.2:
            return True, f"Very low conversion probability ({probability:.1%}) suggests premium may be too high"
        
        return False, None
    
    def _estimate_expected_premium(self, salary_range: str, quote_data: Dict[str, Any]) -> float:
        """
        Estimate expected premium based on salary and other factors
        """
        # Base premium by salary range
        salary_base = {
            '<30k': 400,
            '30-50k': 550,
            '50-80k': 700,
            '80-120k': 900,
            '>120k': 1100
        }
        
        base = salary_base.get(salary_range, 700)
        
        # Adjust for coverage
        coverage = quote_data.get('Coverage', 'Liability')
        coverage_multiplier = {
            'Liability': 0.8,
            'Collision': 1.0,
            'Comprehensive': 1.2
        }
        base *= coverage_multiplier.get(coverage, 1.0)
        
        # Adjust for risk tier
        risk_tier = quote_data.get('Risk_Tier', 1)
        risk_multiplier = {0: 0.9, 1: 1.0, 2: 1.2}
        base *= risk_multiplier.get(risk_tier, 1.0)
        
        return base
    
    def _calculate_recommended_premium(self, original: float, probability: float, 
                                      quote_data: Dict[str, Any]) -> Tuple[float, str, float]:
        """
        Calculate recommended premium based on probability
        Returns: (recommended_premium, adjustment_type, adjustment_percentage)
        """
        # Find appropriate tier
        selected_tier = None
        for tier, info in self.pricing_tiers.items():
            if probability < info['threshold']:
                selected_tier = info
                break
        
        if selected_tier is None:
            selected_tier = self.pricing_tiers['VERY_HIGH']
        
        # Calculate adjustment
        adjustment_multiplier = selected_tier['discount']
        adjustment_pct = (adjustment_multiplier - 1.0) * 100
        
        # Apply limits
        if adjustment_multiplier < (1 - self.max_discount):
            adjustment_multiplier = 1 - self.max_discount
            adjustment_pct = -self.max_discount * 100
        elif adjustment_multiplier > (1 + self.max_increase):
            adjustment_multiplier = 1 + self.max_increase
            adjustment_pct = self.max_increase * 100
        
        recommended = original * adjustment_multiplier
        
        # Determine adjustment type
        if adjustment_multiplier < 1:
            adj_type = 'DISCOUNT'
        elif adjustment_multiplier > 1:
            adj_type = 'INCREASE'
        else:
            adj_type = 'NO_CHANGE'
        
        return round(recommended, 2), adj_type, round(adjustment_pct, 1)
    
    def _get_premium_band(self, recommended: float, original: float) -> str:
        """
        Categorize premium into bands
        """
        ratio = recommended / original
        
        if ratio <= 0.8:
            return 'SIGNIFICANTLY_LOWER'
        elif ratio <= 0.95:
            return 'SLIGHTLY_LOWER'
        elif ratio <= 1.05:
            return 'SIMILAR'
        elif ratio <= 1.2:
            return 'SLIGHTLY_HIGHER'
        else:
            return 'SIGNIFICANTLY_HIGHER'
    
    def _assess_premium_sensitivity(self, quote_data: Dict[str, Any], probability: float) -> str:
        """
        Assess how sensitive this customer is to premium changes
        """
        # Factors that affect sensitivity
        sensitivity_score = 0
        
        # Re-quote indicates price sensitivity
        re_quote = quote_data.get('Re_Quote', 0)
        if isinstance(re_quote, str):
            re_quote = 1 if re_quote.lower() in ['yes', 'y', '1', 'true'] else 0
        
        if re_quote:
            sensitivity_score += 2
        
        # Lower salary ranges are more sensitive
        salary = quote_data.get('Sal_Range', '50-80k')
        if salary in ['<30k', '30-50k']:
            sensitivity_score += 2
        elif salary in ['50-80k']:
            sensitivity_score += 1
        
        # Low probability suggests sensitivity
        if probability < 0.3:
            sensitivity_score += 2
        elif probability < 0.5:
            sensitivity_score += 1
        
        # Categorize
        if sensitivity_score >= 4:
            return 'HIGH'
        elif sensitivity_score >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _suggest_alternative_coverage(self, quote_data: Dict[str, Any], probability: float) -> Optional[str]:
        """
        Suggest alternative coverage tier if premium is too high
        """
        if probability > 0.4:
            return None  # No need for alternative
        
        current_coverage = quote_data.get('Coverage', 'Liability')
        
        coverage_tiers = ['Liability', 'Collision', 'Comprehensive']
        
        if current_coverage == 'Comprehensive' and probability < 0.3:
            return 'Collision'
        elif current_coverage == 'Collision' and probability < 0.25:
            return 'Liability'
        
        return None
    
    def _needs_human_review(self, probability: float, original: float, recommended: float) -> bool:
        """
        Determine if this quote needs human review
        """
        # Large premium changes need review
        change_pct = abs(recommended - original) / original
        
        if change_pct > 0.25:  # More than 25% change
            return True
        
        # Very low probability quotes need review
        if probability < 0.15:
            return True
        
        # Very high probability with increase needs review
        if probability > 0.8 and recommended > original:
            return True
        
        return False
    
    def _get_escalation_reason(self, probability: float, original: float, recommended: float) -> Optional[str]:
        """
        Get reason for escalation if needed
        """
        reasons = []
        
        change_pct = abs(recommended - original) / original
        if change_pct > 0.25:
            reasons.append(f"Large premium adjustment ({change_pct:.1%})")
        
        if probability < 0.15:
            reasons.append(f"Very low probability ({probability:.1%})")
        
        if probability > 0.8 and recommended > original:
            reasons.append(f"Premium increase for high-probability quote")
        
        return "; ".join(reasons) if reasons else None
    
    def _calculate_confidence(self, probability: float, quote_data: Dict[str, Any]) -> str:
        """
        Calculate confidence in recommendation
        """
        # Base confidence on probability clarity
        if probability < 0.2 or probability > 0.8:
            confidence = 'HIGH'
        elif probability < 0.35 or probability > 0.65:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'  # Ambiguous range
        
        # Check if we have all data
        required_fields = ['Sal_Range', 'Coverage', 'Risk_Tier']
        missing = [f for f in required_fields if f not in quote_data]
        if missing:
            confidence = 'LOW'
        
        return confidence
    
    def _generate_explanation(self, original: float, recommended: float, 
                            probability: float, is_blocker: bool) -> str:
        """
        Generate human-readable explanation
        """
        if is_blocker:
            base = f"Premium is likely blocking conversion. "
        else:
            base = f"Premium appears reasonable. "
        
        change = recommended - original
        if abs(change) < 0.01:
            adj = "No adjustment needed"
        elif change < 0:
            adj = f"Recommend {abs(change):.2f} discount ({abs(change/original)*100:.0f}% reduction)"
        else:
            adj = f"Premium could be increased by {change:.2f} ({change/original*100:.0f}% increase)"
        
        prob_text = f"Based on {probability:.1%} conversion probability."
        
        return f"{base}{adj}. {prob_text}"
    
    def suggest_premium(self, quote_data: Dict) -> Tuple[float, float, str, Dict]:
        """
        Legacy method for backward compatibility
        Returns: (suggested_premium, probability, reason, full_details)
        """
        result = self.process_quote(quote_data)
        agent3_out = result['agent_3_output']
        
        return (
            agent3_out['recommended_premium'],
            agent3_out['conversion_probability_used'],
            agent3_out['explanation'],
            agent3_out
        )
    
    def suggest_premium_with_explanation(self, quote_data: Dict) -> Dict:
        """
        Legacy method for backward compatibility
        """
        result = self.process_quote(quote_data)
        agent3_out = result['agent_3_output']
        
        return {
            'quote_id': quote_data.get('quote_id', 'UNKNOWN'),
            'suggested_premium': agent3_out['recommended_premium'],
            'original_premium': agent3_out['original_premium'],
            'conversion_probability': agent3_out['conversion_probability_used'],
            'adjustment_reason': agent3_out['explanation'],
            'full_analysis': agent3_out,
            'timestamp': datetime.now().isoformat()
        }
    
    def batch_process(self, quotes: list) -> Dict:
        """
        Process multiple quotes in batch
        """
        print(f"\n📦 Processing batch of {len(quotes)} quotes...")
        
        results = []
        stats = {
            'total_discount': 0,
            'total_increase': 0,
            'blocker_count': 0,
            'review_needed': 0
        }
        
        for i, quote in enumerate(quotes, 1):
            print(f"\n--- Quote {i}/{len(quotes)} ---")
            result = self.process_quote(quote)
            
            agent3_out = result['agent_3_output']
            results.append(agent3_out)
            
            # Update statistics
            if agent3_out['premium_adjustment_type'] == 'DISCOUNT':
                stats['total_discount'] += (agent3_out['original_premium'] - agent3_out['recommended_premium'])
            elif agent3_out['premium_adjustment_type'] == 'INCREASE':
                stats['total_increase'] += (agent3_out['recommended_premium'] - agent3_out['original_premium'])
            
            if agent3_out['is_premium_blocker']:
                stats['blocker_count'] += 1
            
            if agent3_out['needs_human_review']:
                stats['review_needed'] += 1
        
        summary = {
            'total_processed': len(quotes),
            'results': results,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n✅ Batch processing complete!")
        return summary


# ============== TESTING ==============

def test_integration_with_agent2():
    """Test Agent 3 with simulated Agent 2 output"""
    
    advisor = PremiumAdvisorAgent()
    
    print("\n" + "="*70)
    print("🧪 TEST: Agent 3 with Agent 2 Integration")
    print("="*70)
    
    # Simulate quotes with Agent 2 output already included
    test_quotes = [
        {
            'quote_id': 'Q001',
            'Risk_Tier': 0,
            'Re_Quote': 1,
            'Q_Valid_DT': '2023/12/15',
            'HH_Drivers': 2,
            'Coverage': 'Comprehensive',
            'Agent_Type': 'EA',
            'Region': 'North',
            'Sal_Range': '80-120k',
            'Quoted_Premium': 850,
            # Simulated Agent 2 output
            'conversion_probability': 75.5,
            'conversion_category': 'HIGH',
            'conversion_confidence': 85.2
        },
        {
            'quote_id': 'Q002',
            'Risk_Tier': 2,
            'Re_Quote': 0,
            'Q_Valid_DT': '2023/12/10',
            'HH_Drivers': 1,
            'Coverage': 'Liability',
            'Agent_Type': 'IA',
            'Region': 'South',
            'Sal_Range': '<30k',
            'Quoted_Premium': 450,
            # Simulated Agent 2 output
            'conversion_probability': 15.3,
            'conversion_category': 'LOW',
            'conversion_confidence': 92.1
        }
    ]
    
    for quote in test_quotes:
        result = advisor.process_quote(quote)
        agent3 = result['agent_3_output']
        
        print(f"\n📊 Results for {quote['quote_id']}:")
        print(f"   Original Premium: ${agent3['original_premium']:.2f}")
        print(f"   Agent 2 Probability: {agent3['conversion_probability_used']:.1%}")
        print(f"   Is Premium Blocker: {agent3['is_premium_blocker']}")
        print(f"   Recommended Premium: ${agent3['recommended_premium']:.2f}")
        print(f"   Adjustment: {agent3['premium_adjustment_type']} ({agent3['premium_adjustment_percentage']}%)")
        print(f"   Needs Review: {agent3['needs_human_review']}")
        print(f"   Explanation: {agent3['explanation']}")


if __name__ == "__main__":
    print("\n" + "🚀"*35)
    print("🚀 AGENT 3: PREMIUM ADVISOR")
    print("🚀"*35)
    
    # Test with Agent 2 integration
    test_integration_with_agent2()
    
    print("\n" + "✅"*35)
    print("✅ TESTS COMPLETED")
    print("✅"*35)