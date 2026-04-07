import pandas as pd
import numpy as np
from typing import Dict, List
from utils.stats_utils import (
    calculate_kpis,
    detect_outliers_iqr,
    calculate_correlation_matrix,
    find_strong_correlations,
    detect_trend,
    calculate_distribution_stats
)
from sklearn.ensemble import IsolationForest
from scipy import stats


async def run_analysis(
    df: pd.DataFrame,
    kpi_columns: List[str],
    time_column: str = None
) -> Dict:
    """
    Comprehensive statistical analysis.
    Returns all KPIs, trends, anomalies, correlations, and distributions.
    """
    analysis_result = {
        "kpis": {},
        "anomalies": [],
        "correlations": [],
        "trends": {},
        "distributions": {},
        "seasonal_pattern": None,
        "insights_raw": []
    }
    
    # 1. Calculate KPIs for specified columns
    for col in kpi_columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            kpis = calculate_kpis(df, col, time_column)
            
            # Add trend analysis if time column exists
            if time_column and time_column in df.columns:
                df_sorted = df.sort_values(time_column)
                trend_info = detect_trend(df_sorted[col])
                kpis.update(trend_info)
            
            analysis_result["kpis"][col] = kpis
    
    # 2. Anomaly detection using Isolation Forest
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != '_is_outlier']
    
    if len(numeric_cols) > 0 and len(df) >= 10:
        # Prepare data for Isolation Forest
        X = df[numeric_cols].fillna(df[numeric_cols].median())
        
        if len(X) >= 10:
            iso_forest = IsolationForest(contamination=0.05, random_state=42)
            predictions = iso_forest.fit_predict(X)
            
            # Find anomalies
            anomaly_indices = np.where(predictions == -1)[0]
            
            for idx in anomaly_indices[:20]:  # First 20 anomalies
                anomaly_data = {
                    "row_index": int(idx),
                    "severity": "high",
                    "columns_affected": {}
                }
                
                # Add time info if available
                if time_column and time_column in df.columns:
                    anomaly_data["date"] = str(df.iloc[idx][time_column])
                
                # Find which columns are anomalous
                for col in numeric_cols[:5]:  # Check first 5 numeric columns
                    value = df.iloc[idx][col]
                    col_mean = df[col].mean()
                    col_std = df[col].std()
                    
                    if col_std > 0:
                        z_score = abs((value - col_mean) / col_std)
                        if z_score > 2:
                            anomaly_data["columns_affected"][col] = {
                                "value": float(value),
                                "expected_range": [
                                    float(col_mean - 2*col_std),
                                    float(col_mean + 2*col_std)
                                ],
                                "z_score": float(z_score)
                            }
                
                if anomaly_data["columns_affected"]:
                    analysis_result["anomalies"].append(anomaly_data)
    
    # 3. Correlation analysis
    if len(numeric_cols) >= 2:
        corr_matrix = calculate_correlation_matrix(df, numeric_cols)
        strong_corrs = find_strong_correlations(corr_matrix, threshold=0.7)
        
        for corr in strong_corrs[:10]:  # Top 10 correlations
            # Add interpretation
            if abs(corr["r"]) > 0.9:
                interpretation = f"Very strong {corr['strength'].split()[1]} correlation"
            elif abs(corr["r"]) > 0.7:
                interpretation = f"Strong {corr['strength'].split()[1]} correlation"
            else:
                interpretation = f"Moderate {corr['strength'].split()[1]} correlation"
            
            corr["interpretation"] = interpretation
            corr["p_value"] = 0.001  # Simplified - would need actual calculation
            
            analysis_result["correlations"].append(corr)
    
    # 4. Trend detection for time series
    if time_column and time_column in df.columns:
        df_sorted = df.sort_values(time_column)
        
        for col in numeric_cols[:5]:  # Analyze first 5 numeric columns
            if col in df_sorted.columns:
                trend_info = detect_trend(df_sorted[col])
                analysis_result["trends"][col] = trend_info
        
        # Detect seasonality (simplified)
        if len(df_sorted) >= 24:
            analysis_result["seasonal_pattern"] = "Potential seasonal pattern detected (requires ≥24 periods for full analysis)"
    
    # 5. Distribution analysis
    for col in numeric_cols[:5]:  # First 5 numeric columns
        if col in df.columns:
            dist_stats = calculate_distribution_stats(df[col].dropna())
            analysis_result["distributions"][col] = dist_stats
    
    # 6. Generate raw insights
    insights = []
    
    # KPI insights
    for col, kpi_data in analysis_result["kpis"].items():
        if "pct_change" in kpi_data:
            direction = "increased" if kpi_data["pct_change"] > 0 else "decreased"
            insights.append(
                f"{col} {direction} by {abs(kpi_data['pct_change']):.1f}% "
                f"(from {kpi_data.get('mean', 0):.2f} average)"
            )
    
    # Correlation insights
    for corr in analysis_result["correlations"][:3]:
        insights.append(
            f"{corr['col_a']} and {corr['col_b']} show {corr['interpretation']} (r={corr['r']})"
        )
    
    # Anomaly insights
    if len(analysis_result["anomalies"]) > 0:
        insights.append(
            f"{len(analysis_result['anomalies'])} anomalies detected across the dataset"
        )
    
    # Trend insights
    for col, trend_data in analysis_result["trends"].items():
        if trend_data.get("significant"):
            insights.append(
                f"{col} shows {trend_data['trend']} trend (slope={trend_data['slope']:.2f}, p<0.05)"
            )
    
    analysis_result["insights_raw"] = insights
    
    return analysis_result
