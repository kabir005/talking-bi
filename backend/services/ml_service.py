"""
ML Service - Model management, predictions, forecasting
Provides high-level ML operations for the API layer
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime
import os
import pickle
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text

from database.models import MLModel, Dataset
from agents.ml_agent import train_ml_model, predict_with_model


async def list_models(db: AsyncSession, dataset_id: Optional[str] = None) -> List[Dict]:
    """
    List all ML models, optionally filtered by dataset.
    
    Args:
        db: Database session
        dataset_id: Optional dataset ID to filter by
    
    Returns:
        List of model metadata dictionaries
    """
    query = select(MLModel)
    
    if dataset_id:
        query = query.where(MLModel.dataset_id == dataset_id)
    
    query = query.order_by(MLModel.created_at.desc())
    result = await db.execute(query)
    models = result.scalars().all()
    
    return [
        {
            "model_id": model.id,
            "dataset_id": model.dataset_id,
            "target_column": model.target_column,
            "algorithm": model.algorithm,
            "r2_score": model.r2_score,
            "mae": model.mae,
            "rmse": model.rmse,
            "feature_importance": model.feature_importance,
            "created_at": model.created_at.isoformat() if model.created_at else None,
            "model_path": model.model_path
        }
        for model in models
    ]


async def get_model(db: AsyncSession, model_id: str) -> Optional[Dict]:
    """
    Get detailed information about a specific model.
    
    Args:
        db: Database session
        model_id: Model ID
    
    Returns:
        Model metadata dictionary or None if not found
    """
    result = await db.execute(select(MLModel).where(MLModel.id == model_id))
    model = result.scalar_one_or_none()
    
    if not model:
        return None
    
    return {
        "model_id": model.id,
        "dataset_id": model.dataset_id,
        "target_column": model.target_column,
        "algorithm": model.algorithm,
        "r2_score": model.r2_score,
        "mae": model.mae,
        "rmse": model.rmse,
        "metrics": {
            "r2_score": model.r2_score,
            "mae": model.mae,
            "rmse": model.rmse
        },
        "feature_importance": model.feature_importance,
        "created_at": model.created_at.isoformat() if model.created_at else None,
        "model_path": model.model_path
    }


async def delete_model(db: AsyncSession, model_id: str) -> bool:
    """
    Delete a model from database and filesystem.
    
    Args:
        db: Database session
        model_id: Model ID
    
    Returns:
        True if deleted, False if not found
    """
    result = await db.execute(select(MLModel).where(MLModel.id == model_id))
    model = result.scalar_one_or_none()
    
    if not model:
        return False
    
    # Delete model file from filesystem
    if model.model_path and os.path.exists(model.model_path):
        try:
            os.remove(model.model_path)
        except Exception as e:
            print(f"Warning: Could not delete model file: {e}")
    
    # Delete from database
    await db.delete(model)
    await db.commit()
    
    return True


async def train_model(
    db: AsyncSession,
    dataset_id: str,
    target_column: str,
    feature_columns: Optional[List[str]] = None,
    task_type: str = "auto"
) -> Dict:
    """
    Train a new ML model.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        target_column: Target column name
        feature_columns: Optional list of feature columns (auto-detect if None)
        task_type: "auto", "regression", or "classification"
    
    Returns:
        Training result dictionary with model_id and metrics
    """
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found")
    
    # Load data from SQLite table
    from sqlalchemy import text
    query_sql = f'SELECT * FROM "{dataset.sqlite_table_name}"'
    result = await db.execute(text(query_sql))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    
    if df.empty:
        raise ValueError("Dataset is empty")
    
    # Train model using ML agent
    try:
        training_result = await train_ml_model(
            df=df,
            target_column=target_column,
            task_type=task_type
        )
    except Exception as e:
        print(f"Error in train_ml_model: {type(e).__name__}: {e}")
        raise
    
    # Save model to database
    try:
        # The ML agent already saved the model to disk and returned a model_id
        agent_model_id = training_result.get('model_id')
        agent_model_path = f"./models/{agent_model_id}.pkl"
        
        # Create a new UUID for our database record
        db_model_id = str(uuid.uuid4())
        
        # Extract metrics
        metrics = training_result.get('metrics', {})
        
        # Create MLModel record
        ml_model = MLModel(
            id=db_model_id,
            dataset_id=dataset_id,
            target_column=target_column,
            algorithm=training_result.get('best_model', 'Unknown'),
            r2_score=metrics.get('r2', metrics.get('r2_score', 0)),
            mae=metrics.get('mae', 0),
            rmse=metrics.get('rmse', 0),
            feature_importance=training_result.get('feature_importance', {}),
            model_path=agent_model_path,  # Use the path where agent saved the model
            created_at=datetime.utcnow()
        )
        
        db.add(ml_model)
        await db.commit()
        await db.refresh(ml_model)
        
        return {
            "model_id": db_model_id,
            "dataset_id": dataset_id,
            "target_column": target_column,
            "best_model": training_result.get('best_model', 'Unknown'),
            "metrics": metrics,
            "feature_importance": training_result.get('feature_importance', {}),
            "created_at": ml_model.created_at.isoformat()
        }
    except Exception as e:
        print(f"Error saving model to database: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise


async def make_predictions(
    db: AsyncSession,
    model_id: str,
    data: List[Dict[str, Any]]
) -> Dict:
    """
    Make predictions using a trained model.
    
    Args:
        db: Database session
        model_id: Model ID
        data: List of dictionaries with feature values
    
    Returns:
        Predictions dictionary with values and confidence
    """
    # Get model
    result = await db.execute(select(MLModel).where(MLModel.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise ValueError(f"Model {model_id} not found")
    
    # Convert data to DataFrame
    df = pd.DataFrame(data)
    
    # Make predictions using ML agent
    result = await predict_with_model(
        model_path=model.model_path,
        df=df
    )
    
    return result



async def forecast_future(
    db: AsyncSession,
    model_id: str,
    periods: int = 12,
    frequency: str = "M"
) -> Dict:
    """
    Generate future forecasts using a trained model.
    
    Args:
        db: Database session
        model_id: Model ID
        periods: Number of periods to forecast
        frequency: Time frequency ("D", "W", "M", "Q", "Y")
    
    Returns:
        Forecast dictionary with predictions and confidence intervals
    """
    # Get model
    result = await db.execute(select(MLModel).where(MLModel.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise ValueError(f"Model {model_id} not found")
    
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == model.dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise ValueError(f"Dataset {model.dataset_id} not found")
    
    # Load historical data
    from sqlalchemy import text
    query_sql = f'SELECT * FROM "{dataset.sqlite_table_name}"'
    result = await db.execute(text(query_sql))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    
    # Find date column
    date_col = None
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            date_col = col
            break
    
    if not date_col:
        raise ValueError("No date column found for forecasting")
    
    # Convert to datetime
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    df = df.sort_values(date_col)
    
    # Generate future dates
    last_date = df[date_col].max()
    future_dates = pd.date_range(
        start=last_date,
        periods=periods + 1,
        freq=frequency
    )[1:]  # Exclude the last historical date
    
    # Create feature DataFrame for future dates
    # Use mean values for numeric features, mode for categorical
    future_data = []
    
    feature_importance = model.feature_importance or {}
    important_features = [k for k, v in sorted(
        feature_importance.items(),
        key=lambda x: x[1],
        reverse=True
    )]
    
    for future_date in future_dates:
        row = {date_col: future_date}
        
        # Add features with their mean/mode values
        for col in df.columns:
            if col == date_col or col == model.target_column:
                continue
            
            if df[col].dtype in ['int64', 'float64']:
                row[col] = df[col].mean()
            else:
                row[col] = df[col].mode()[0] if len(df[col].mode()) > 0 else df[col].iloc[0]
        
        future_data.append(row)
    
    future_df = pd.DataFrame(future_data)
    
    # Make predictions
    predictions_result = await predict_with_model(
        model_id=model_id,
        model_path=model.model_path,
        data=future_df,
        db=db
    )
    
    # Calculate confidence intervals (simple approach: ±10% of prediction)
    predictions = predictions_result.get('predictions', [])
    confidence_intervals = []
    
    for pred in predictions:
        lower = pred * 0.9
        upper = pred * 1.1
        confidence_intervals.append({
            "prediction": pred,
            "lower_bound": lower,
            "upper_bound": upper,
            "confidence": 0.90
        })
    
    return {
        "model_id": model_id,
        "target_column": model.target_column,
        "periods": periods,
        "frequency": frequency,
        "forecast_dates": [d.isoformat() for d in future_dates],
        "predictions": predictions,
        "confidence_intervals": confidence_intervals,
        "algorithm": model.algorithm,
        "historical_performance": {
            "r2_score": model.r2_score,
            "mae": model.mae,
            "rmse": model.rmse
        }
    }


async def retrain_model(
    db: AsyncSession,
    model_id: str,
    new_data: Optional[pd.DataFrame] = None
) -> Dict:
    """
    Retrain an existing model with new data or updated parameters.
    
    Args:
        db: Database session
        model_id: Model ID to retrain
        new_data: Optional new training data (if None, uses original dataset)
    
    Returns:
        Retraining result dictionary
    """
    # Get existing model
    result = await db.execute(select(MLModel).where(MLModel.id == model_id))
    old_model = result.scalar_one_or_none()
    if not old_model:
        raise ValueError(f"Model {model_id} not found")
    
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == old_model.dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise ValueError(f"Dataset {old_model.dataset_id} not found")
    
    # Load data
    if new_data is None:
        from sqlalchemy import text
        query_sql = f'SELECT * FROM "{dataset.sqlite_table_name}"'
        result = await db.execute(text(query_sql))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
    else:
        df = new_data
    
    # Train new model with same parameters
    training_result = await train_ml_model(
        df=df,
        target_column=old_model.target_column,
        task_type="auto"
    )
    
    # Save new model to database
    agent_model_id = training_result.get('model_id')
    agent_model_path = f"./models/{agent_model_id}.pkl"
    new_db_model_id = str(uuid.uuid4())
    
    # Extract metrics
    new_metrics = training_result.get('metrics', {})
    
    # Create new MLModel record
    new_ml_model = MLModel(
        id=new_db_model_id,
        dataset_id=old_model.dataset_id,
        target_column=old_model.target_column,
        algorithm=training_result.get('best_model', 'Unknown'),
        r2_score=new_metrics.get('r2', new_metrics.get('r2_score', 0)),
        mae=new_metrics.get('mae', 0),
        rmse=new_metrics.get('rmse', 0),
        feature_importance=training_result.get('feature_importance', {}),
        model_path=agent_model_path,
        created_at=datetime.utcnow()
    )
    
    db.add(new_ml_model)
    
    # Delete old model
    await delete_model(db, model_id)
    
    await db.commit()
    
    return {
        "old_model_id": model_id,
        "new_model_id": new_db_model_id,
        "old_metrics": {
            "r2_score": old_model.r2_score,
            "mae": old_model.mae,
            "rmse": old_model.rmse
        },
        "new_metrics": new_metrics,
        "improvement": {
            "r2_delta": new_metrics.get('r2', new_metrics.get('r2_score', 0)) - (old_model.r2_score or 0),
            "mae_delta": (old_model.mae or 0) - new_metrics.get('mae', 0),
            "rmse_delta": (old_model.rmse or 0) - new_metrics.get('rmse', 0)
        },
        "retrained_at": datetime.now().isoformat()
    }


async def compare_models(
    db: AsyncSession,
    model_ids: List[str]
) -> Dict:
    """
    Compare multiple models side by side.
    
    Args:
        db: Database session
        model_ids: List of model IDs to compare
    
    Returns:
        Comparison dictionary with metrics for all models
    """
    models = []
    
    for model_id in model_ids:
        result = await db.execute(select(MLModel).where(MLModel.id == model_id))
        model = result.scalar_one_or_none()
        if model:
            models.append({
                "model_id": model.id,
                "algorithm": model.algorithm,
                "target_column": model.target_column,
                "r2_score": model.r2_score,
                "mae": model.mae,
                "rmse": model.rmse,
                "created_at": model.created_at.isoformat() if model.created_at else None
            })
    
    if not models:
        return {"models": [], "best_model": None}
    
    # Find best model by R² score
    best_model = max(models, key=lambda m: m.get('r2_score', 0) or 0)
    
    return {
        "models": models,
        "best_model": best_model['model_id'],
        "comparison_metric": "r2_score",
        "count": len(models)
    }
