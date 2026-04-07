import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple


def calculate_kpis(df: pd.DataFrame, column: str, time_column: str = None) -> Dict:
    """Calculate comprehensive KPIs for a numeric column"""
    kpis = {
        "total": float(df[column].sum()),
        "mean": float(df[column].mean()),
        "median": float(df[column].median()),
        "std": float(df[column].std()),
        "min": float(df[column].min()),
        "max": float(df[column].max()),
    }
    
    # Period-over-period if time column exists
    if time_column and time_column in df.columns:
        df_sorted = df.sort_values(time_column)
        
        # Try to detect period (monthly, quarterly, etc.)
        if len(df_sorted) >= 2:
            # Split into current and previous period (simple 50/50 split)
            mid_point = len(df_sorted) // 2
            previous = df_sorted.iloc[:mid_point][column].sum()
            current = df_sorted.iloc[mid_point:][column].sum()
            
            if previous != 0:
                pct_change = ((current - previous) / previous) * 100
                kpis["pct_change"] = round(pct_change, 2)
                kpis["trend_direction"] = "up" if pct_change > 0 else "down" if pct_change < 0 else "flat"
    
    return kpis


def detect_outliers_iqr(series: pd.Series) -> Tuple[List[int], Dict]:
    """Detect outliers using IQR method"""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outlier_mask = (series < lower_bound) | (series > upper_bound)
    outlier_indices = series[outlier_mask].index.tolist()
    outlier_values = series[outlier_mask].tolist()
    
    return outlier_indices, {
        "method": "IQR",
        "count": len(outlier_indices),
        "values": outlier_values[:10],  # First 10 only
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound)
    }


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> Tuple[List[int], Dict]:
    """Detect outliers using Z-score method"""
    z_scores = np.abs(stats.zscore(series.dropna()))
    outlier_mask = z_scores > threshold
    
    # Map back to original indices
    outlier_indices = series.dropna().iloc[outlier_mask].index.tolist()
    outlier_values = series.loc[outlier_indices].tolist()
    
    return outlier_indices, {
        "method": "Z-score",
        "count": len(outlier_indices),
        "values": outlier_values[:10],
        "threshold": threshold
    }


def calculate_correlation_matrix(df: pd.DataFrame, numeric_cols: List[str]) -> pd.DataFrame:
    """Calculate Pearson correlation matrix for numeric columns"""
    return df[numeric_cols].corr()


def find_strong_correlations(corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict]:
    """Find strong correlations (|r| > threshold)"""
    strong_corrs = []
    
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            col_a = corr_matrix.columns[i]
            col_b = corr_matrix.columns[j]
            r_value = corr_matrix.iloc[i, j]
            
            if abs(r_value) > threshold:
                strong_corrs.append({
                    "col_a": col_a,
                    "col_b": col_b,
                    "r": round(r_value, 3),
                    "strength": "strong positive" if r_value > 0 else "strong negative"
                })
    
    return sorted(strong_corrs, key=lambda x: abs(x["r"]), reverse=True)


def detect_trend(series: pd.Series) -> Dict:
    """Detect trend using linear regression"""
    if len(series) < 3:
        return {"trend": "insufficient_data", "slope": 0, "significant": False}
    
    x = np.arange(len(series))
    y = series.values
    
    # Remove NaN values
    mask = ~np.isnan(y)
    x = x[mask]
    y = y[mask]
    
    if len(x) < 3:
        return {"trend": "insufficient_data", "slope": 0, "significant": False}
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    trend = "upward" if slope > 0 else "downward" if slope < 0 else "flat"
    significant = p_value < 0.05
    
    return {
        "trend": trend,
        "slope": float(slope),
        "r_squared": float(r_value ** 2),
        "p_value": float(p_value),
        "significant": significant
    }


def calculate_distribution_stats(series: pd.Series) -> Dict:
    """Calculate distribution statistics"""
    return {
        "skewness": float(series.skew()),
        "kurtosis": float(series.kurtosis()),
        "is_normal": bool(stats.shapiro(series.dropna()[:5000])[1] > 0.05) if len(series.dropna()) >= 3 else None
    }
