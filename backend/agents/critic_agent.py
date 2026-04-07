"""
Critic Agent - Validates insights, adds confidence scores, prevents hallucinations
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from scipy import stats
from utils.llm import call_llm
import json


async def run_critic_validation(
    insights: Dict[str, Any],
    df: pd.DataFrame,
    dataset_schema: Dict[str, str]
) -> Dict[str, Any]:
    """
    Validates every insight from Analyst Agent.
    Re-computes statistics independently and assigns confidence scores.
    
    Returns:
        {
            "validated_insights": [...],
            "rejected_insights": [...],
            "caveats": [...],
            "overall_confidence": 0-100
        }
    """
    validated_insights = []
    rejected_insights = []
    caveats = []
    
    print(f"\n{'='*80}")
    print(f"CRITIC AGENT - VALIDATION")
    print(f"{'='*80}")
    
    # Validate KPIs
    if "kpis" in insights:
        for col, kpi_data in insights["kpis"].items():
            validation = await validate_kpi(col, kpi_data, df)
            
            if validation["is_valid"]:
                validated_insights.append({
                    "type": "kpi",
                    "column": col,
                    "data": kpi_data,
                    "confidence": validation["confidence"],
                    "validation_status": "validated",
                    "evidence": validation["evidence"]
                })
                print(f"✓ KPI '{col}' validated (confidence: {validation['confidence']}%)")
            else:
                rejected_insights.append({
                    "type": "kpi",
                    "column": col,
                    "reason": validation["reason"]
                })
                print(f"✗ KPI '{col}' rejected: {validation['reason']}")
            
            if validation.get("caveat"):
                caveats.append(validation["caveat"])
    
    # Validate correlations
    if "correlations" in insights:
        for corr in insights["correlations"]:
            validation = await validate_correlation(corr, df)
            
            if validation["is_valid"]:
                validated_insights.append({
                    "type": "correlation",
                    "data": corr,
                    "confidence": validation["confidence"],
                    "validation_status": "validated",
                    "evidence": validation["evidence"]
                })
                print(f"✓ Correlation {corr['col_a']} ↔ {corr['col_b']} validated")
            else:
                rejected_insights.append({
                    "type": "correlation",
                    "data": corr,
                    "reason": validation["reason"]
                })
                print(f"✗ Correlation rejected: {validation['reason']}")
            
            if validation.get("caveat"):
                caveats.append(validation["caveat"])
    
    # Validate anomalies
    if "anomalies" in insights:
        for anomaly in insights["anomalies"]:
            validation = await validate_anomaly(anomaly, df)
            
            if validation["is_valid"]:
                validated_insights.append({
                    "type": "anomaly",
                    "data": anomaly,
                    "confidence": validation["confidence"],
                    "validation_status": "validated"
                })
                print(f"✓ Anomaly in {anomaly['column']} validated")
            else:
                rejected_insights.append({
                    "type": "anomaly",
                    "data": anomaly,
                    "reason": validation["reason"]
                })
            
            if validation.get("caveat"):
                caveats.append(validation["caveat"])
    
    # Use LLM to generate final validation summary
    llm_validation = await generate_llm_validation(
        validated_insights, rejected_insights, caveats, df
    )
    
    # Calculate overall confidence
    if validated_insights:
        overall_confidence = int(np.mean([i["confidence"] for i in validated_insights]))
    else:
        overall_confidence = 0
    
    print(f"\n{'='*80}")
    print(f"VALIDATION COMPLETE")
    print(f"Validated: {len(validated_insights)}")
    print(f"Rejected: {len(rejected_insights)}")
    print(f"Overall Confidence: {overall_confidence}%")
    print(f"{'='*80}\n")
    
    return {
        "validated_insights": validated_insights,
        "rejected_insights": rejected_insights,
        "caveats": caveats,
        "overall_confidence": overall_confidence,
        "llm_summary": llm_validation
    }


async def validate_kpi(col: str, kpi_data: Dict, df: pd.DataFrame) -> Dict:
    """Validate a single KPI by re-computing independently"""
    try:
        if col not in df.columns:
            return {
                "is_valid": False,
                "reason": f"Column '{col}' not found in dataset",
                "confidence": 0
            }
        
        # Re-compute statistics
        series = pd.to_numeric(df[col], errors='coerce').dropna()
        
        if len(series) == 0:
            return {
                "is_valid": False,
                "reason": "No valid numeric values",
                "confidence": 0
            }
        
        actual_total = float(series.sum())
        actual_mean = float(series.mean())
        actual_median = float(series.median())
        
        claimed_total = kpi_data.get("total", 0)
        claimed_mean = kpi_data.get("mean", 0)
        
        # Check if claimed values match actual (within 1% tolerance)
        total_match = abs(actual_total - claimed_total) / max(abs(actual_total), 1) < 0.01
        mean_match = abs(actual_mean - claimed_mean) / max(abs(actual_mean), 1) < 0.01
        
        if not (total_match and mean_match):
            return {
                "is_valid": False,
                "reason": f"Statistics mismatch: claimed total={claimed_total}, actual={actual_total}",
                "confidence": 0
            }
        
        # Check sample size
        n = len(series)
        if n < 30:
            caveat = f"Low sample size (n={n}) — confidence reduced"
            confidence = max(50, int(70 * (n / 30)))  # Scale confidence by sample size
        else:
            caveat = None
            confidence = 95
        
        # Check for high variance
        cv = series.std() / series.mean() if series.mean() != 0 else 0
        if cv > 1.0:
            if caveat:
                caveat += f"; High variability (CV={cv:.2f})"
            else:
                caveat = f"High variability (CV={cv:.2f}) — interpret with caution"
            confidence = max(confidence - 10, 60)
        
        return {
            "is_valid": True,
            "confidence": confidence,
            "evidence": f"n={n}, mean={actual_mean:.2f}, median={actual_median:.2f}",
            "caveat": caveat
        }
    
    except Exception as e:
        return {
            "is_valid": False,
            "reason": f"Validation error: {str(e)}",
            "confidence": 0
        }


async def validate_correlation(corr: Dict, df: pd.DataFrame) -> Dict:
    """Validate a correlation claim"""
    try:
        col_a = corr["col_a"]
        col_b = corr["col_b"]
        claimed_r = corr["r"]
        claimed_p = corr.get("p_value", 1.0)
        
        if col_a not in df.columns or col_b not in df.columns:
            return {
                "is_valid": False,
                "reason": "One or both columns not found",
                "confidence": 0
            }
        
        # Re-compute correlation
        series_a = pd.to_numeric(df[col_a], errors='coerce')
        series_b = pd.to_numeric(df[col_b], errors='coerce')
        
        # Remove NaN pairs
        valid_mask = series_a.notna() & series_b.notna()
        series_a = series_a[valid_mask]
        series_b = series_b[valid_mask]
        
        if len(series_a) < 10:
            return {
                "is_valid": False,
                "reason": f"Insufficient data points (n={len(series_a)})",
                "confidence": 0,
                "caveat": "Need at least 10 data points for correlation"
            }
        
        # Compute Pearson correlation
        actual_r, actual_p = stats.pearsonr(series_a, series_b)
        
        # Check if claimed r matches actual (within 0.05 tolerance)
        r_match = abs(actual_r - claimed_r) < 0.05
        
        if not r_match:
            return {
                "is_valid": False,
                "reason": f"Correlation mismatch: claimed r={claimed_r:.3f}, actual r={actual_r:.3f}",
                "confidence": 0
            }
        
        # Assign confidence based on p-value and sample size
        n = len(series_a)
        
        if actual_p < 0.001:
            confidence = 95
        elif actual_p < 0.01:
            confidence = 90
        elif actual_p < 0.05:
            confidence = 80
        else:
            confidence = 60
            caveat = f"Weak statistical significance (p={actual_p:.3f})"
        
        # Reduce confidence for small samples
        if n < 30:
            confidence = max(confidence - 15, 50)
            caveat = f"Small sample (n={n}), p={actual_p:.3f}"
        else:
            caveat = None
        
        # Check for confounders (simplified - check if correlation is spurious)
        # If both variables have strong trend, correlation might be spurious
        if abs(actual_r) > 0.7:
            # Check if both have strong autocorrelation (time trend)
            try:
                from statsmodels.tsa.stattools import acf
                acf_a = acf(series_a, nlags=min(10, len(series_a)//4))
                acf_b = acf(series_b, nlags=min(10, len(series_b)//4))
                
                if acf_a[1] > 0.7 and acf_b[1] > 0.7:
                    caveat = "Both variables show strong trends — correlation may be spurious"
                    confidence = max(confidence - 10, 60)
            except:
                pass
        
        return {
            "is_valid": True,
            "confidence": confidence,
            "evidence": f"r={actual_r:.3f}, p={actual_p:.4f}, n={n}",
            "caveat": caveat
        }
    
    except Exception as e:
        return {
            "is_valid": False,
            "reason": f"Validation error: {str(e)}",
            "confidence": 0
        }


async def validate_anomaly(anomaly: Dict, df: pd.DataFrame) -> Dict:
    """Validate an anomaly detection"""
    try:
        col = anomaly["column"]
        row_index = anomaly["row_index"]
        claimed_value = anomaly["value"]
        expected_range = anomaly.get("expected_range", [])
        
        if col not in df.columns:
            return {
                "is_valid": False,
                "reason": "Column not found",
                "confidence": 0
            }
        
        if row_index >= len(df):
            return {
                "is_valid": False,
                "reason": "Row index out of bounds",
                "confidence": 0
            }
        
        # Get actual value
        actual_value = df.iloc[row_index][col]
        
        # Check if claimed value matches
        if abs(float(actual_value) - float(claimed_value)) / max(abs(float(claimed_value)), 1) > 0.01:
            return {
                "is_valid": False,
                "reason": f"Value mismatch: claimed={claimed_value}, actual={actual_value}",
                "confidence": 0
            }
        
        # Re-compute expected range using IQR
        series = pd.to_numeric(df[col], errors='coerce').dropna()
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Check if value is actually an outlier
        is_outlier = (actual_value < lower_bound) or (actual_value > upper_bound)
        
        if not is_outlier:
            return {
                "is_valid": False,
                "reason": "Value is not an outlier by IQR method",
                "confidence": 0
            }
        
        # Calculate severity
        if actual_value < lower_bound:
            deviation = (lower_bound - actual_value) / IQR
        else:
            deviation = (actual_value - upper_bound) / IQR
        
        # Confidence based on deviation magnitude
        if deviation > 3:
            confidence = 95
            severity = "extreme"
        elif deviation > 2:
            confidence = 90
            severity = "high"
        elif deviation > 1:
            confidence = 80
            severity = "moderate"
        else:
            confidence = 70
            severity = "mild"
        
        return {
            "is_valid": True,
            "confidence": confidence,
            "evidence": f"IQR deviation: {deviation:.2f}σ, severity: {severity}",
            "caveat": None
        }
    
    except Exception as e:
        return {
            "is_valid": False,
            "reason": f"Validation error: {str(e)}",
            "confidence": 0
        }


async def generate_llm_validation(
    validated: List[Dict],
    rejected: List[Dict],
    caveats: List[str],
    df: pd.DataFrame
) -> str:
    """Use LLM to generate human-readable validation summary"""
    try:
        system_prompt = """You are the Critic Agent for a BI platform. 
You receive validated and rejected insights and must write a concise validation summary.

Write 2-3 sentences explaining:
1. What insights were validated and why they're trustworthy
2. What caveats or limitations exist
3. Overall confidence level

Be specific and cite numbers. Be honest about limitations."""
        
        context = {
            "validated_count": len(validated),
            "rejected_count": len(rejected),
            "caveats": caveats,
            "sample_size": len(df),
            "validated_sample": validated[:3] if validated else []
        }
        
        messages = [{
            "role": "user",
            "content": f"Validation results:\n{json.dumps(context, indent=2)}\n\nWrite validation summary:"
        }]
        
        summary = await call_llm(messages, system_prompt)
        return summary
    
    except Exception as e:
        return f"Validation complete: {len(validated)} insights validated, {len(rejected)} rejected."
