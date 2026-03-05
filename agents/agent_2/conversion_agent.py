# agents/agent_2/conversion_agent.py
"""
Agent 2: Conversion Predictor Agent
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

from .config import CONVERSION_THRESHOLDS, ESCALATION_CONFIG, ROUTING_DECISIONS
from .conversion_model import ConversionModel
from .preprocess import ConversionPreprocessor

class ConversionPredictorAgent:
    """
    Agent 2: Predicts quote conversion probability
    """
    
    def __init__(self, model_path=None):
        self.model = ConversionModel()
        self.preprocessor = ConversionPreprocessor()
        self.agent_name = "Conversion Predictor"
        self.agent_version = "2.0"
        
        # If no model path provided, look in the current directory
        if model_path is None:
            # Get the directory where this file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, 'conversion_model.pkl')
        
        # Try to load pre-trained model
        try:
            if os.path.exists(model_path):
                self.model.load_model(model_path)
                print(f"✅ Agent 2: Model loaded successfully from {model_path}")
            else:
                print(f"⚠️ Agent 2: Model file not found at {model_path}")
                print("   Train first using: python agents/agent_2/train_agent2.py")
        except Exception as e:
            print(f"⚠️ Agent 2: Failed to load model: {e}")
            print("   Train first using: python agents/agent_2/train_agent2.py")
    
    def process_quote(self, quote_data):
        """
        Process a single quote and return conversion prediction
        
        Args:
            quote_data: Dictionary containing quote information
        
        Returns:
            Dictionary with conversion prediction results
        """
        # Validate input
        required_fields = ['Risk_Tier', 'Re_Quote', 'Q_Valid_DT', 'HH_Drivers', 
                          'Coverage', 'Agent_Type', 'Region', 'Sal_Range']
        
        missing_fields = [f for f in required_fields if f not in quote_data]
        if missing_fields:
            return {
                'quote_id': quote_data.get('quote_id', 'UNKNOWN'),
                'agent_2_output': {
                    'error': f"Missing required fields: {missing_fields}",
                    'status': 'failed',
                    'processed_at': datetime.now().isoformat()
                }
            }
        
        # Check if model is loaded
        if self.model.model is None:
            return {
                'quote_id': quote_data.get('quote_id', 'UNKNOWN'),
                'agent_2_output': {
                    'error': 'Model not trained. Call train() first.',
                    'status': 'failed',
                    'processed_at': datetime.now().isoformat()
                }
            }
        
        # Convert to DataFrame
        df = pd.DataFrame([quote_data])
        
        try:
            # IMPORTANT FIX: Use the model's preprocessor, not the agent's preprocessor
            # This ensures we use the same preprocessing as during training
            X = self.model.preprocessor.preprocess(df, fit_encoders=False)
            
            # Make prediction
            probabilities = self.model.model.predict_proba(X)[:, 1]
            prob = probabilities[0]
            
            # Calculate confidence (distance from 0.5)
            confidence = np.abs(prob - 0.5) * 2
            
            # Categorize
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
            
            # Determine routing
            routing_decision = self._determine_routing(prob)
            
            # Check if escalation needed
            needs_escalation = confidence < ESCALATION_CONFIG['confidence_threshold']
            
            # Prepare result
            result = {
                'quote_id': quote_data.get('quote_id', 'UNKNOWN'),
                'agent_2_output': {
                    'conversion_probability': round(prob * 100, 2),
                    'probability_category': category,
                    'confidence_score': round(confidence * 100, 2),
                    'risk_tier_input': quote_data['Risk_Tier'],
                    'routing_decision': routing_decision,
                    'needs_escalation': needs_escalation,
                    'processed_at': datetime.now().isoformat(),
                    'status': 'success'
                }
            }
            
            # Add explanation
            result['agent_2_output']['explanation'] = self._generate_explanation(quote_data, prob)
            
            # Add escalation reason if needed
            if needs_escalation:
                result['agent_2_output']['escalation_reason'] = self._get_escalation_reason(prob, confidence)
            
            return result
            
        except Exception as e:
            return {
                'quote_id': quote_data.get('quote_id', 'UNKNOWN'),
                'agent_2_output': {
                    'error': str(e),
                    'status': 'failed',
                    'processed_at': datetime.now().isoformat()
                }
            }
    
    def _determine_routing(self, probability):
        """Determine routing decision based on probability"""
        if probability >= ESCALATION_CONFIG['auto_approve']:
            return ROUTING_DECISIONS['auto_approve']
        elif probability >= ESCALATION_CONFIG['human_review_lower']:
            return ROUTING_DECISIONS['agent_follow_up']
        else:
            return ROUTING_DECISIONS['escalate']
    
    def _get_escalation_reason(self, probability, confidence):
        """Get reason for escalation"""
        reasons = []
        
        if confidence < ESCALATION_CONFIG['confidence_threshold']:
            reasons.append(f"Low confidence ({confidence:.1%})")
        
        if ESCALATION_CONFIG['human_review_lower'] <= probability <= ESCALATION_CONFIG['human_review_upper']:
            reasons.append(f"Probability in review range ({probability:.1%})")
        
        return "; ".join(reasons) if reasons else "Routed for human review"
    
    def _generate_explanation(self, quote_data, probability):
        """Generate human-readable explanation"""
        explanations = []
        
        # Risk tier impact
        risk_map = {0: 'Low', 1: 'Medium', 2: 'High'}
        risk_text = risk_map.get(quote_data.get('Risk_Tier'), 'Unknown')
        
        if quote_data.get('Risk_Tier') == 0:
            explanations.append(f"Low risk profile increases conversion likelihood")
        elif quote_data.get('Risk_Tier') == 2:
            explanations.append(f"High risk profile decreases conversion likelihood")
        
        # Re-quote impact
        if quote_data.get('Re_Quote') == 1:
            explanations.append(f"Customer is re-quoting, showing higher intent")
        
        # Expiry impact
        if quote_data.get('Q_Valid_DT', 0) <= 7:
            explanations.append(f"Quote expires soon, creating urgency")
        
        # Salary impact
        if quote_data.get('Sal_Range') in ['80-120k', '>120k']:
            explanations.append(f"Higher salary range indicates ability to purchase")
        
        if explanations:
            return "Based on: " + "; ".join(explanations[:3])
        else:
            return "Standard prediction based on historical patterns"
    
    def predict_probability(self, quote_data):
        """Simple method to just get probability (for Agent 3)"""
        if self.model.model is None:
            # Fallback calculation
            risk_tier = quote_data.get('Risk_Tier', 1)
            re_quote = quote_data.get('Re_Quote', 0)
            
            if isinstance(re_quote, str):
                re_quote = 1 if re_quote.lower() in ['yes', 'y', '1', 'true'] else 0
            
            base_prob = 0.20
            if risk_tier == 0:
                base_prob += 0.15
            elif risk_tier == 2:
                base_prob -= 0.08
            
            if re_quote:
                base_prob += 0.10
            
            return min(max(base_prob, 0.05), 0.95)
        
        df = pd.DataFrame([quote_data])
        X = self.model.preprocessor.preprocess(df, fit_encoders=False)
        prob = self.model.model.predict_proba(X)[:, 1][0]
        return prob
    
    def process_batch(self, quotes_df):
        """Process multiple quotes in batch"""
        results = []
        
        for idx, row in quotes_df.iterrows():
            quote_dict = row.to_dict()
            result = self.process_quote(quote_dict)
            results.append(result)
        
        # Generate summary
        summary = self._generate_batch_summary(results)
        
        return {
            'batch_results': results,
            'batch_summary': summary,
            'total_processed': len(results),
            'agent': self.agent_name,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_batch_summary(self, results):
        """Generate summary statistics for batch"""
        successful = [r for r in results if r['agent_2_output'].get('status') == 'success']
        
        if not successful:
            return {'error': 'No successful predictions'}
        
        decisions = [r['agent_2_output']['routing_decision'] for r in successful]
        categories = [r['agent_2_output']['probability_category'] for r in successful]
        escalations = [r['agent_2_output'].get('needs_escalation', False) for r in successful]
        
        summary = {
            'total_processed': len(results),
            'successful': len(successful),
            'failed': len(results) - len(successful),
            'routing_breakdown': {
                'AUTO_APPROVE': decisions.count('AUTO_APPROVE'),
                'AGENT_FOLLOW_UP': decisions.count('AGENT_FOLLOW_UP'),
                'ESCALATE_TO_UNDERWRITER': decisions.count('ESCALATE_TO_UNDERWRITER')
            },
            'escalations_needed': sum(escalations),
            'avg_probability': np.mean([r['agent_2_output']['conversion_probability'] for r in successful])
        }
        
        return summary