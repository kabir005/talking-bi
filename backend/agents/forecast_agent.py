"""
Forecast Agent - Time-series prediction with LinearRegression + Moving Average fallback
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import logging

logger = logging.getLogger(__name__)


async def generate_forecast(
    df: pd.DataFrame,
    target_column: str,
    time_column: Optional[str] = None,
    periods: int = 12,
    method: str = "auto"
) -> Dict[str, Any]:
    """
    Generate time-series forecast
    
    Args:
        df: DataFrame with historical data
        target_column: Column to forecast
        time_column: Time/date column (auto-detected if None)
        periods: Number of periods to forecast
        method: "auto", "linear", "ma" (moving average)
    
    Returns:
        {
            "forecast": List[float],
            "confidence_lower": List[float],
            "confidence_upper": List[float],
            "method_used": str,
            "metrics": Dict,
            "historical": List[float]
        }
    """
    try:
        # Auto-detect time column if not provided
        if time_column is None:
            time_column = _detect_time_column(df)
        
        # Validate target column
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found")
        
        # Ensure target is numeric
        if not pd.api.types.is_numeric_dtype(df[target_column]):
            raise ValueError(f"Target column '{target_column}' must be numeric")
        
        # Sort by time if time column exists
        if time_column and time_column in df.columns:
            df = df.sort_values(time_column).reset_index(drop=True)
        
        # Get historical values
        historical = df[target_column].dropna().values
        
        if len(historical) < 3:
            raise ValueError("Need at least 3 historical data points for forecasting")
        
        # Choose method
        if method == "auto":
            # Use linear regression if we have enough data, otherwise MA
            method = "linear" if len(historical) >= 10 else "ma"
        
        # Generate forecast
        if method == "linear":
            result = _linear_regression_forecast(historical, periods)
        elif method == "ma":
            result = _moving_average_forecast(historical, periods)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Add historical data
        result["historical"] = historical.tolist()
        result["target_column"] = target_column
        result["time_column"] = time_column
        
        return result
        
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        return {
            "error": str(e),
            "forecast": [],
            "method_used": "none"
        }


def _linear_regression_forecast(
    historical: np.ndarray,
    periods: int
) -> Dict[str, Any]:
    """Linear regression forecast"""
    n = len(historical)
    
    # Prepare training data
    X = np.arange(n).reshape(-1, 1)
    y = historical
    
    # Train model
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate predictions
    future_X = np.arange(n, n + periods).reshape(-1, 1)
    forecast = model.predict(future_X)
    
    # Calculate confidence intervals (simple approach using residuals)
    train_pred = model.predict(X)
    residuals = y - train_pred
    std_error = np.std(residuals)
    
    # 95% confidence interval (±1.96 * std_error)
    confidence_lower = forecast - 1.96 * std_error
    confidence_upper = forecast + 1.96 * std_error
    
    # Calculate metrics on training data
    mae = mean_absolute_error(y, train_pred)
    rmse = np.sqrt(mean_squared_error(y, train_pred))
    
    # Calculate trend
    trend = "increasing" if model.coef_[0] > 0 else "decreasing"
    trend_strength = abs(model.coef_[0])
    
    return {
        "forecast": forecast.tolist(),
        "confidence_lower": confidence_lower.tolist(),
        "confidence_upper": confidence_upper.tolist(),
        "method_used": "linear_regression",
        "metrics": {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2_score": float(model.score(X, y)),
            "trend": trend,
            "trend_strength": float(trend_strength)
        },
        "model_params": {
            "slope": float(model.coef_[0]),
            "intercept": float(model.intercept_)
        }
    }


def _moving_average_forecast(
    historical: np.ndarray,
    periods: int,
    window: int = 3
) -> Dict[str, Any]:
    """Moving average forecast"""
    n = len(historical)
    
    # Use last 'window' values for MA
    window = min(window, n)
    ma = np.mean(historical[-window:])
    
    # Simple forecast: repeat MA value
    forecast = np.full(periods, ma)
    
    # Calculate confidence intervals based on historical volatility
    std = np.std(historical[-window:])
    confidence_lower = forecast - 1.96 * std
    confidence_upper = forecast + 1.96 * std
    
    # Calculate metrics
    # Use MA as prediction for last 'window' points
    train_pred = np.full(window, ma)
    train_actual = historical[-window:]
    mae = mean_absolute_error(train_actual, train_pred)
    rmse = np.sqrt(mean_squared_error(train_actual, train_pred))
    
    return {
        "forecast": forecast.tolist(),
        "confidence_lower": confidence_lower.tolist(),
        "confidence_upper": confidence_upper.tolist(),
        "method_used": "moving_average",
        "metrics": {
            "mae": float(mae),
            "rmse": float(rmse),
            "window_size": window,
            "volatility": float(std)
        },
        "model_params": {
            "moving_average": float(ma),
            "std_dev": float(std)
        }
    }


def _detect_time_column(df: pd.DataFrame) -> Optional[str]:
    """Auto-detect time/date column"""
    for col in df.columns:
        # Check if column name suggests time
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['date', 'time', 'year', 'month', 'day', 'period']):
            return col
        
        # Check if column dtype is datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    
    return None


async def forecast_multiple_columns(
    df: pd.DataFrame,
    target_columns: List[str],
    time_column: Optional[str] = None,
    periods: int = 12
) -> Dict[str, Any]:
    """
    Generate forecasts for multiple columns
    
    Returns:
        {
            "forecasts": {
                "column1": {...forecast result...},
                "column2": {...forecast result...}
            },
            "summary": {...}
        }
    """
    forecasts = {}
    
    for col in target_columns:
        try:
            forecast = await generate_forecast(
                df, col, time_column, periods, method="auto"
            )
            forecasts[col] = forecast
        except Exception as e:
            logger.error(f"Error forecasting {col}: {e}")
            forecasts[col] = {"error": str(e)}
    
    # Generate summary
    successful = sum(1 for f in forecasts.values() if "error" not in f)
    
    return {
        "forecasts": forecasts,
        "summary": {
            "total_columns": len(target_columns),
            "successful": successful,
            "failed": len(target_columns) - successful,
            "periods": periods
        }
    }
