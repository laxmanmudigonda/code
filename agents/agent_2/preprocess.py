# agents/agent_2/preprocess.py
"""
Data preprocessing for Agent 2 - Conversion Predictor
"""

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from .config import FEATURES

class ConversionPreprocessor:
    """
    Preprocesses data specifically for conversion prediction
    """
    
    def __init__(self):
        self.numerical_features = FEATURES['numerical'].copy()
        self.categorical_features = FEATURES['categorical'].copy()
        self.label_encoders = {}
        
    def validate_input(self, df):
        """
        Validate input data has required columns
        """
        required_cols = self.numerical_features + self.categorical_features
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return False, f"Missing columns: {missing_cols}"
        
        return True, "Validation successful"
    
    def preprocess(self, df, fit_encoders=False):
        """
        Preprocess data for model input
        """
        df = df.copy()
        
        # Handle missing values and convert data types
        df = self._handle_missing_values(df)
        
        # Create derived features
        df = self._create_derived_features(df)
        
        # Encode categorical features to numeric
        df = self._encode_categorical(df, fit_encoders)
        
        # Ensure all numerical columns are numeric
        all_numerical = self.numerical_features.copy()
        
        # Add derived features to numerical list
        derived_features = ['risk_requote_interaction', 'expires_soon', 'multiple_drivers']
        for feat in derived_features:
            if feat in df.columns:
                all_numerical.append(feat)
        
        # Convert all numerical columns to float
        for col in all_numerical:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Select features
        all_features = all_numerical + self.categorical_features
        feature_cols = [f for f in all_features if f in df.columns]
        
        return df[feature_cols]
    
    def _handle_missing_values(self, df):
        """
        Handle missing values and convert data types
        """
        # Convert Yes/No to 1/0 for Re_Quote
        if 'Re_Quote' in df.columns:
            if df['Re_Quote'].dtype == 'object':
                df['Re_Quote'] = df['Re_Quote'].map({'Yes': 1, 'No': 0, 'yes': 1, 'no': 0, 'Y': 1, 'N': 0})
            df['Re_Quote'] = pd.to_numeric(df['Re_Quote'], errors='coerce').fillna(0)
        
        # Numerical defaults
        numerical_defaults = {
            'Risk_Tier': 1,      # Default to Medium
            'HH_Drivers': 1       # Default 1 driver
        }
        
        for col, default in numerical_defaults.items():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(default)
        
        # Handle Q_Valid_DT specially (it's a date)
        if 'Q_Valid_DT' in df.columns:
            # Convert date string to days until expiry
            df['Q_Valid_DT'] = self._convert_date_to_days(df['Q_Valid_DT'])
        
        # Categorical defaults
        categorical_defaults = {
            'Coverage': 'Liability',
            'Agent_Type': 'EA',
            'Region': 'North',
            'Sal_Range': '50-80k'
        }
        
        for col, default in categorical_defaults.items():
            if col in df.columns:
                df[col] = df[col].fillna(default)
        
        return df
    
    def _convert_date_to_days(self, date_series):
        """
        Convert date strings to number of days until expiry
        """
        def parse_date(date_val):
            try:
                if pd.isna(date_val):
                    return 14
                    
                if isinstance(date_val, (int, float)):
                    return min(max(int(date_val), 1), 30)
                    
                if isinstance(date_val, str):
                    # Handle different date formats
                    date_val = date_val.strip()
                    if '/' in date_val:
                        # Format: YYYY/MM/DD
                        date_obj = datetime.strptime(date_val, '%Y/%m/%d')
                    elif '-' in date_val:
                        # Format: YYYY-MM-DD
                        date_obj = datetime.strptime(date_val, '%Y-%m-%d')
                    else:
                        return 14
                    
                    # Calculate days from today
                    today = datetime.now()
                    days_until = (date_obj - today).days
                    
                    # Ensure positive and reasonable
                    if days_until < 1:
                        return 1
                    elif days_until > 30:
                        return 30
                    else:
                        return days_until
                else:
                    return 14
            except Exception as e:
                # If date parsing fails, return a default
                return 14
        
        return date_series.apply(parse_date)
    
    def _create_derived_features(self, df):
        """
        Create additional features for better prediction
        """
        # Risk and re-quote interaction
        if 'Risk_Tier' in df.columns and 'Re_Quote' in df.columns:
            # Ensure both are numeric
            risk_tier = pd.to_numeric(df['Risk_Tier'], errors='coerce').fillna(1)
            re_quote = pd.to_numeric(df['Re_Quote'], errors='coerce').fillna(0)
            df['risk_requote_interaction'] = risk_tier * re_quote
        
        # Days until expiry categorization
        if 'Q_Valid_DT' in df.columns:
            # Q_Valid_DT is now numeric
            df['expires_soon'] = (df['Q_Valid_DT'] <= 7).astype(int)
        
        # Multiple drivers flag
        if 'HH_Drivers' in df.columns:
            df['multiple_drivers'] = (df['HH_Drivers'] > 1).astype(int)
        
        return df
    
    def _encode_categorical(self, df, fit_encoders):
        """
        Encode categorical features to numeric
        """
        for col in self.categorical_features:
            if col in df.columns:
                # Convert to string first
                df[col] = df[col].astype(str)
                
                if fit_encoders:
                    # Fit new encoder
                    self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col])
                else:
                    # Use existing encoder
                    if col in self.label_encoders:
                        # Handle unseen categories
                        df[col] = df[col].map(
                            lambda x: self.label_encoders[col].transform([x])[0] 
                            if x in self.label_encoders[col].classes_ 
                            else -1
                        )
        
        return df
    
    def get_feature_names(self):
        """Get list of all features"""
        base_features = self.numerical_features + self.categorical_features
        derived = ['risk_requote_interaction', 'expires_soon', 'multiple_drivers']
        return base_features + derived