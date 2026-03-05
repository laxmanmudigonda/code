# agents/agent2_conversion_predictor/conversion_model.py
"""
ML Model for conversion prediction with imbalance handling
"""

import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                           f1_score, roc_auc_score, confusion_matrix)
from sklearn.utils import class_weight
import warnings
warnings.filterwarnings('ignore')

from .config import MODEL_CONFIG, MODEL_PATH
from .preprocess import ConversionPreprocessor

class ConversionModel:
    """
    XGBoost model for predicting quote conversion probability
    """
    
    def __init__(self):
        self.model = None
        self.preprocessor = ConversionPreprocessor()
        self.feature_columns = None
        self.imbalance_ratio = None
        
    def train(self, df, target_col='Converted'):
        """
        Train the conversion prediction model
        """
        print("=" * 60)
        print("TRAINING CONVERSION PREDICTION MODEL")
        print("=" * 60)
        
        # Validate data
        is_valid, message = self.preprocessor.validate_input(df)
        if not is_valid:
            print(f"Warning: {message}")
        
        # Preprocess data
        X = self.preprocessor.preprocess(df, fit_encoders=True)
        y = df[target_col].values
        
        self.feature_columns = X.columns.tolist()
        
        # Calculate imbalance ratio
        n_neg = (y == 0).sum()
        n_pos = (y == 1).sum()
        self.imbalance_ratio = n_neg / n_pos
        
        print(f"\nDataset Statistics:")
        print(f"Total samples: {len(df)}")
        print(f"Converted (positive): {n_pos} ({n_pos/len(df):.2%})")
        print(f"Not converted (negative): {n_neg} ({n_neg/len(df):.2%})")
        print(f"Imbalance ratio: {self.imbalance_ratio:.2f}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=MODEL_CONFIG['test_size'], 
            random_state=MODEL_CONFIG['random_state'],
            stratify=y
        )
        
        print(f"\nTraining set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Calculate class weights
        class_weights = class_weight.compute_class_weight(
            class_weight='balanced',
            classes=np.unique(y_train),
            y=y_train
        )
        scale_pos_weight = class_weights[1] / class_weights[0]
        
        # Initialize XGBoost with imbalance handling
        self.model = xgb.XGBClassifier(
            n_estimators=MODEL_CONFIG['n_estimators'],
            max_depth=MODEL_CONFIG['max_depth'],
            learning_rate=MODEL_CONFIG['learning_rate'],
            scale_pos_weight=scale_pos_weight * 0.9,  # Slightly conservative
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=1,
            random_state=MODEL_CONFIG['random_state'],
            eval_metric=['logloss', 'auc'],
            use_label_encoder=False
        )
        
        # Cross-validation with error handling
        print("\nPerforming cross-validation...")
        try:
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            cv_scores = cross_val_score(self.model, X_train, y_train, cv=cv, scoring='roc_auc')
            print(f"Cross-validation ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
        except Exception as e:
            print(f"⚠️ Cross-validation failed: {e}")
            print("Continuing with training only...")
        
        # Train model
        print("\nTraining final model...")
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluate
        self._evaluate(X_test, y_test)
        
        return self.model
    
    def _evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        """
        # Predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        print("\n" + "=" * 40)
        print("MODEL PERFORMANCE METRICS")
        print("=" * 40)
        for metric, value in metrics.items():
            print(f"{metric.upper():10s}: {value:.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print("\nCONFUSION MATRIX:")
        print(f"TN: {cm[0,0]:5d}  FP: {cm[0,1]:5d}")
        print(f"FN: {cm[1,0]:5d}  TP: {cm[1,1]:5d}")
        
        # Feature importance
        self._show_feature_importance()
        
        return metrics
    
    def _show_feature_importance(self):
        """
        Display feature importance
        """
        importance = self.model.feature_importances_
        feature_imp = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        print("\nTOP 5 FEATURE IMPORTANCES:")
        for idx, row in feature_imp.head(5).iterrows():
            print(f"  {row['feature']:25s}: {row['importance']:.4f}")
    
    def predict(self, df):
        """
        Make predictions on new data
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Preprocess data
        X = self.preprocessor.preprocess(df, fit_encoders=False)
        
        # Predict probabilities
        probabilities = self.model.predict_proba(X)[:, 1]
        
        return probabilities
    
    def predict_with_details(self, df):
        """
        Predict with additional details
        """
        probabilities = self.predict(df)
        
        # Calculate confidence (distance from 0.5)
        confidence = np.abs(probabilities - 0.5) * 2
        
        # Categorize
        categories = []
        for prob in probabilities:
            if prob >= 0.75:
                categories.append('VERY_HIGH')
            elif prob >= 0.50:
                categories.append('HIGH')
            elif prob >= 0.25:
                categories.append('MEDIUM')
            elif prob >= 0.10:
                categories.append('LOW')
            else:
                categories.append('VERY_LOW')
        
        return {
            'probabilities': probabilities,
            'confidence': confidence,
            'categories': categories
        }
    
    def save_model(self, path=MODEL_PATH):
        """
        Save model and preprocessors
        """
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        model_artifacts = {
            'model': self.model,
            'label_encoders': self.preprocessor.label_encoders,
            'feature_columns': self.feature_columns,
            'numerical_features': self.preprocessor.numerical_features,
            'categorical_features': self.preprocessor.categorical_features,
            'imbalance_ratio': self.imbalance_ratio
        }
        
        joblib.dump(model_artifacts, path)
        print(f"\n✅ Model saved to {path}")
    
    def load_model(self, path=MODEL_PATH):
        """
        Load model and preprocessors
        """
        model_artifacts = joblib.load(path)
        self.model = model_artifacts['model']
        self.preprocessor.label_encoders = model_artifacts['label_encoders']
        self.feature_columns = model_artifacts['feature_columns']
        self.preprocessor.numerical_features = model_artifacts['numerical_features']
        self.preprocessor.categorical_features = model_artifacts['categorical_features']
        self.imbalance_ratio = model_artifacts.get('imbalance_ratio', None)
        
        print(f"\n✅ Model loaded from {path}")
        return self