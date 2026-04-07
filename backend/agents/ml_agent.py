"""
ML Agent - Fully automated model selection, training, evaluation, and explanation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, accuracy_score, f1_score, classification_report
import pickle
import os
from datetime import datetime
import json


async def run_auto_ml(
    df: pd.DataFrame,
    target_column: str,
    task_type: str = "auto",
    test_size: float = 0.2,
    cv_folds: int = 5
) -> Dict[str, Any]:
    """
    Fully automated ML pipeline:
    1. Auto-detect task type (regression/classification)
    2. Feature engineering
    3. Train multiple models
    4. Select best model
    5. Compute feature importance
    6. Generate predictions
    
    Returns complete ML results with model ID
    """
    print(f"\n{'='*80}")
    print(f"AUTO ML AGENT - TRAINING")
    print(f"{'='*80}")
    print(f"Target column: {target_column}")
    print(f"Dataset shape: {df.shape}")
    
    # Validate target column
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset")
    
    # Auto-detect task type
    if task_type == "auto":
        task_type = detect_task_type(df[target_column])
        print(f"Auto-detected task type: {task_type}")
    
    # Prepare features and target
    X, y, feature_names, encoders = prepare_features(df, target_column, task_type)
    
    print(f"Features prepared: {X.shape[1]} features, {X.shape[0]} samples")
    print(f"Feature names: {feature_names[:10]}...")  # Show first 10
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42,
        stratify=y if task_type == "classification" and len(np.unique(y)) > 1 else None
    )
    
    print(f"Train set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Train multiple models
    if task_type == "regression":
        models = train_regression_models(X_train, y_train, cv_folds)
    else:
        models = train_classification_models(X_train, y_train, cv_folds)
    
    # Select best model
    best_model_name, best_model, best_metrics = select_best_model(
        models, X_test, y_test, task_type
    )
    
    print(f"\n✓ Best model: {best_model_name}")
    print(f"  Metrics: {best_metrics}")
    
    # Compute feature importance
    feature_importance = compute_feature_importance(
        best_model, feature_names, X_train, y_train
    )
    
    # Generate predictions
    predictions = generate_predictions(
        best_model, X_test, y_test, df, target_column
    )
    
    # Save model
    model_id = save_model(best_model, encoders, feature_names, target_column, task_type)
    
    # Generate explanation
    explanation = generate_model_explanation(
        best_model_name, feature_importance, best_metrics, task_type
    )
    
    print(f"\n{'='*80}")
    print(f"AUTO ML COMPLETE")
    print(f"Model ID: {model_id}")
    print(f"{'='*80}\n")
    
    return {
        "model_id": model_id,
        "best_model": best_model_name,
        "task_type": task_type,
        "metrics": best_metrics,
        "feature_importance": feature_importance,
        "predictions": predictions,
        "model_explanation": explanation,
        "feature_names": feature_names,
        "n_features": len(feature_names),
        "n_samples": len(df)
    }


def detect_task_type(target_series: pd.Series) -> str:
    """Auto-detect if regression or classification"""
    # Remove NaN
    target_series = target_series.dropna()
    
    # Check if numeric
    try:
        numeric_series = pd.to_numeric(target_series, errors='coerce')
        if numeric_series.notna().sum() > len(target_series) * 0.9:
            # Numeric - check unique values
            n_unique = target_series.nunique()
            if n_unique <= 20:
                return "classification"
            else:
                return "regression"
    except:
        pass
    
    # Categorical
    n_unique = target_series.nunique()
    if n_unique <= 20:
        return "classification"
    else:
        # Too many categories - treat as regression if possible
        return "regression"


def prepare_features(
    df: pd.DataFrame,
    target_column: str,
    task_type: str
) -> tuple:
    """
    Feature engineering pipeline:
    1. Separate features from target
    2. Handle missing values
    3. Encode categorical variables
    4. Scale numeric features
    """
    # Separate features and target
    X = df.drop(columns=[target_column, '_is_outlier'], errors='ignore').copy()
    y = df[target_column].copy()
    
    # Remove rows with missing target
    valid_mask = y.notna()
    X = X[valid_mask]
    y = y[valid_mask]
    
    # Encode target for classification
    target_encoder = None
    if task_type == "classification":
        target_encoder = LabelEncoder()
        y = target_encoder.fit_transform(y.astype(str))
    else:
        y = pd.to_numeric(y, errors='coerce')
        valid_mask = y.notna()
        X = X[valid_mask]
        y = y[valid_mask]
    
    # Identify column types
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Handle missing values in numeric columns
    for col in numeric_cols:
        X[col] = X[col].fillna(X[col].median())
    
    # Handle missing values in categorical columns
    for col in categorical_cols:
        X[col] = X[col].fillna(X[col].mode()[0] if len(X[col].mode()) > 0 else 'missing')
    
    # Encode categorical variables
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
    
    # Scale numeric features (for linear models)
    scaler = StandardScaler()
    if numeric_cols:
        X[numeric_cols] = scaler.fit_transform(X[numeric_cols])
    encoders['scaler'] = scaler
    encoders['numeric_cols'] = numeric_cols  # Save which columns were numeric
    encoders['categorical_cols'] = categorical_cols  # Save which columns were categorical
    encoders['target_encoder'] = target_encoder
    
    feature_names = X.columns.tolist()
    
    return X.values, y, feature_names, encoders


def train_regression_models(X_train, y_train, cv_folds):
    """Train multiple regression models"""
    models = {}
    
    print(f"\nTraining regression models...")
    
    # Linear Regression
    try:
        lr = LinearRegression()
        lr.fit(X_train, y_train)
        cv_scores = cross_val_score(lr, X_train, y_train, cv=cv_folds, scoring='r2')
        models['Linear Regression'] = {
            'model': lr,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std()
        }
        print(f"  ✓ Linear Regression: R² = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    except Exception as e:
        print(f"  ✗ Linear Regression failed: {e}")
    
    # Ridge Regression
    try:
        ridge = Ridge(alpha=1.0)
        ridge.fit(X_train, y_train)
        cv_scores = cross_val_score(ridge, X_train, y_train, cv=cv_folds, scoring='r2')
        models['Ridge Regression'] = {
            'model': ridge,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std()
        }
        print(f"  ✓ Ridge Regression: R² = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    except Exception as e:
        print(f"  ✗ Ridge Regression failed: {e}")
    
    # Random Forest
    try:
        rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        cv_scores = cross_val_score(rf, X_train, y_train, cv=min(cv_folds, 3), scoring='r2')  # Reduce CV for speed
        models['Random Forest'] = {
            'model': rf,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std()
        }
        print(f"  ✓ Random Forest: R² = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    except Exception as e:
        print(f"  ✗ Random Forest failed: {e}")
    
    # Gradient Boosting
    try:
        gb = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        gb.fit(X_train, y_train)
        cv_scores = cross_val_score(gb, X_train, y_train, cv=min(cv_folds, 3), scoring='r2')
        models['Gradient Boosting'] = {
            'model': gb,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std()
        }
        print(f"  ✓ Gradient Boosting: R² = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    except Exception as e:
        print(f"  ✗ Gradient Boosting failed: {e}")
    
    return models


def train_classification_models(X_train, y_train, cv_folds):
    """Train multiple classification models"""
    models = {}
    
    print(f"\nTraining classification models...")
    
    # Logistic Regression
    try:
        lr = LogisticRegression(max_iter=1000, random_state=42)
        lr.fit(X_train, y_train)
        cv_scores = cross_val_score(lr, X_train, y_train, cv=cv_folds, scoring='accuracy')
        models['Logistic Regression'] = {
            'model': lr,
            'cv_accuracy_mean': cv_scores.mean(),
            'cv_accuracy_std': cv_scores.std()
        }
        print(f"  ✓ Logistic Regression: Accuracy = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    except Exception as e:
        print(f"  ✗ Logistic Regression failed: {e}")
    
    # Random Forest
    try:
        rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        cv_scores = cross_val_score(rf, X_train, y_train, cv=min(cv_folds, 3), scoring='accuracy')
        models['Random Forest'] = {
            'model': rf,
            'cv_accuracy_mean': cv_scores.mean(),
            'cv_accuracy_std': cv_scores.std()
        }
        print(f"  ✓ Random Forest: Accuracy = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    except Exception as e:
        print(f"  ✗ Random Forest failed: {e}")
    
    # Gradient Boosting
    try:
        gb = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        gb.fit(X_train, y_train)
        cv_scores = cross_val_score(gb, X_train, y_train, cv=min(cv_folds, 3), scoring='accuracy')
        models['Gradient Boosting'] = {
            'model': gb,
            'cv_accuracy_mean': cv_scores.mean(),
            'cv_accuracy_std': cv_scores.std()
        }
        print(f"  ✓ Gradient Boosting: Accuracy = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    except Exception as e:
        print(f"  ✗ Gradient Boosting failed: {e}")
    
    # Decision Tree
    try:
        dt = DecisionTreeClassifier(max_depth=10, random_state=42)
        dt.fit(X_train, y_train)
        cv_scores = cross_val_score(dt, X_train, y_train, cv=cv_folds, scoring='accuracy')
        models['Decision Tree'] = {
            'model': dt,
            'cv_accuracy_mean': cv_scores.mean(),
            'cv_accuracy_std': cv_scores.std()
        }
        print(f"  ✓ Decision Tree: Accuracy = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    except Exception as e:
        print(f"  ✗ Decision Tree failed: {e}")
    
    return models


def select_best_model(models, X_test, y_test, task_type):
    """Select best model based on test set performance"""
    best_score = -np.inf
    best_model_name = None
    best_model = None
    best_metrics = {}
    
    for name, model_data in models.items():
        model = model_data['model']
        y_pred = model.predict(X_test)
        
        if task_type == "regression":
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            score = r2  # Use R² as selection criterion
            
            if score > best_score:
                best_score = score
                best_model_name = name
                best_model = model
                best_metrics = {
                    "r2": float(r2),
                    "mae": float(mae),
                    "rmse": float(rmse),
                    "cv_r2_mean": float(model_data['cv_r2_mean']),
                    "cv_r2_std": float(model_data['cv_r2_std'])
                }
        else:
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            score = f1  # Use F1 as selection criterion
            
            if score > best_score:
                best_score = score
                best_model_name = name
                best_model = model
                best_metrics = {
                    "accuracy": float(accuracy),
                    "f1_score": float(f1),
                    "cv_accuracy_mean": float(model_data['cv_accuracy_mean']),
                    "cv_accuracy_std": float(model_data['cv_accuracy_std'])
                }
    
    return best_model_name, best_model, best_metrics


def compute_feature_importance(model, feature_names, X_train, y_train):
    """Compute feature importance (simplified - no SHAP for now)"""
    importance_list = []
    
    try:
        # Tree-based models have feature_importances_
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            for i, importance in enumerate(importances):
                if i < len(feature_names):
                    importance_list.append({
                        "feature": feature_names[i],
                        "importance": float(importance),
                        "shap_direction": "positive" if importance > 0 else "neutral"
                    })
        
        # Linear models have coef_
        elif hasattr(model, 'coef_'):
            coefs = model.coef_ if len(model.coef_.shape) == 1 else model.coef_[0]
            for i, coef in enumerate(coefs):
                if i < len(feature_names):
                    importance_list.append({
                        "feature": feature_names[i],
                        "importance": float(abs(coef)),
                        "shap_direction": "positive" if coef > 0 else "negative"
                    })
        
        # Sort by importance
        importance_list.sort(key=lambda x: x['importance'], reverse=True)
        
        # Return top 10
        return importance_list[:10]
    
    except Exception as e:
        print(f"Warning: Could not compute feature importance: {e}")
        return []


def generate_predictions(model, X_test, y_test, df, target_column):
    """Generate predictions with actual vs predicted comparison"""
    y_pred = model.predict(X_test)
    
    # Convert y_test to numpy array to avoid index issues
    y_test_array = y_test.values if hasattr(y_test, 'values') else y_test
    
    predictions = []
    for i in range(min(len(y_test_array), 100)):  # Limit to 100 predictions
        predictions.append({
            "actual": float(y_test_array[i]) if hasattr(y_test_array[i], 'item') else float(y_test_array[i]),
            "predicted": float(y_pred[i]) if hasattr(y_pred[i], 'item') else float(y_pred[i]),
            "index": int(i)
        })
    
    return predictions


def save_model(model, encoders, feature_names, target_column, task_type):
    """Save model and metadata to disk"""
    model_id = f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, f"{model_id}.pkl")
    
    model_data = {
        "model": model,
        "encoders": encoders,
        "feature_names": feature_names,
        "target_column": target_column,
        "task_type": task_type
    }
    
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"Model saved to: {model_path}")
    
    return model_id


def generate_model_explanation(model_name, feature_importance, metrics, task_type):
    """Generate human-readable model explanation"""
    if not feature_importance:
        return f"{model_name} trained successfully."
    
    top_features = feature_importance[:3]
    feature_text = ", ".join([f"{f['feature']} ({f['importance']:.1%})" for f in top_features])
    
    if task_type == "regression":
        metric_text = f"R² = {metrics.get('r2', 0):.3f}"
    else:
        metric_text = f"Accuracy = {metrics.get('accuracy', 0):.3f}"
    
    explanation = f"{model_name} explains the target using: {feature_text}. Performance: {metric_text}."
    
    return explanation


# Wrapper functions for backward compatibility
async def train_ml_model(
    df: pd.DataFrame,
    target_column: str,
    task_type: str = "auto",
    test_size: float = 0.2,
    cv_folds: int = 5
) -> Dict[str, Any]:
    """Wrapper for run_auto_ml for backward compatibility"""
    return await run_auto_ml(df, target_column, task_type, test_size, cv_folds)


async def predict_with_model(
    model_path: str,
    df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Load a saved model and make predictions on new data
    
    Args:
        model_path: Path to the saved model file
        df: DataFrame with features to predict on
    
    Returns:
        Dictionary with predictions and metadata
    """
    try:
        # Load model
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        model = model_data["model"]
        encoders = model_data["encoders"]
        feature_names = model_data["feature_names"]
        target_column = model_data["target_column"]
        task_type = model_data["task_type"]
        
        # Prepare features using the saved encoders
        # Remove target column if it exists
        X = df.drop(columns=[target_column, '_is_outlier'], errors='ignore').copy()
        
        # Get the original numeric and categorical columns from encoders
        original_numeric_cols = encoders.get('numeric_cols', [])
        original_categorical_cols = encoders.get('categorical_cols', [])
        
        # If not saved (old model), try to detect from current data
        if not original_numeric_cols and not original_categorical_cols:
            original_numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
            original_categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Handle missing values in numeric columns
        for col in original_numeric_cols:
            if col in X.columns:
                X[col] = X[col].fillna(X[col].median() if len(X[col]) > 0 else 0)
        
        # Handle missing values in categorical columns
        for col in original_categorical_cols:
            if col in X.columns:
                mode_val = X[col].mode()[0] if len(X[col].mode()) > 0 else 'missing'
                X[col] = X[col].fillna(mode_val)
        
        # Encode categorical variables using saved encoders
        for col in original_categorical_cols:
            if col in X.columns:
                if col in encoders and encoders[col] is not None:
                    le = encoders[col]
                    # Handle unseen categories
                    X[col] = X[col].astype(str).apply(
                        lambda x: le.transform([x])[0] if x in le.classes_ else -1
                    )
                else:
                    # If no encoder exists, try to convert to numeric
                    X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)
        
        # Ensure all columns are numeric now
        for col in X.columns:
            if X[col].dtype == 'object':
                X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)
        
        # Add missing columns with 0
        for col in feature_names:
            if col not in X.columns:
                X[col] = 0
        
        # Select only the features used in training, in the correct order
        X = X[feature_names]
        
        # Scale ONLY the original numeric features using saved scaler
        # Only scale if we have the saved numeric_cols (new models)
        if 'scaler' in encoders and encoders.get('numeric_cols'):
            scaler = encoders['scaler']
            original_numeric_cols = encoders['numeric_cols']
            # Only scale the columns that were numeric before encoding
            # IMPORTANT: Must be in the same order as during training
            numeric_cols_in_X = [col for col in original_numeric_cols if col in X.columns]
            if numeric_cols_in_X:
                # Extract numeric columns as numpy array to avoid feature name checking
                X_numeric_values = X[numeric_cols_in_X].values
                # Transform using scaler (works on numpy arrays without feature name checking)
                X_numeric_scaled = scaler.transform(X_numeric_values)
                # Put the scaled values back
                for i, col in enumerate(numeric_cols_in_X):
                    X[col] = X_numeric_scaled[:, i]
        
        # Make predictions
        predictions = model.predict(X.values)
        
        # Format results
        results = {
            "predictions": [float(p) for p in predictions],
            "model_id": os.path.basename(model_path).replace('.pkl', ''),
            "task_type": task_type,
            "num_predictions": len(predictions)
        }
        
        # Add probabilities for classification
        if task_type == "classification" and hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X.values)
            results["probabilities"] = probabilities.tolist()
        
        return results
        
    except Exception as e:
        print(f"Prediction error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Failed to make predictions: {str(e)}")
