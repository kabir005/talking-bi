from typing import Dict, List
from utils.llm import call_llm
import json
import numpy as np
import pandas as pd


async def generate_recommendations(
    validated_insights: List[Dict],
    kpis: Dict,
    correlations: List[Dict],
    trends: Dict
) -> List[Dict]:
    """
    Generate ranked business recommendations based on validated insights.
    Returns 3 actionable recommendations with expected impact.
    """
    
    # Use rule-based recommendations (more reliable)
    return await _generate_rule_based_recommendations(
        validated_insights, kpis, correlations, trends
    )


async def _generate_llm_recommendations(
    validated_insights: List[Dict],
    kpis: Dict,
    correlations: List[Dict],
    trends: Dict
) -> List[Dict]:
    """Generate recommendations using LLM"""
    
    system_prompt = """You are a business strategist generating actionable recommendations.
Based on validated insights, generate exactly 3 ranked recommendations.

Each recommendation must include:
- action: Specific action to take
- expected_impact: Quantified expected outcome (e.g., "+12% revenue")
- timeline: When to expect results (e.g., "Q1 2024", "3 months")
- risk_level: "low", "medium", or "high"
- confidence: 0-100 percentage
- rationale: Why this recommendation makes sense (cite specific data)

Return JSON array of 3 recommendations, ranked by expected impact."""

    # Prepare insight summary
    insight_summary = []
    
    for col, data in list(kpis.items())[:3]:
        if "pct_change" in data:
            insight_summary.append(
                f"{col}: {data['pct_change']:+.1f}% change, mean={data.get('mean', 0):.2f}"
            )
    
    for corr in correlations[:2]:
        insight_summary.append(
            f"Strong correlation: {corr['col_a']} ↔ {corr['col_b']} (r={corr['r']:.2f})"
        )
    
    for col, trend_data in list(trends.items())[:2]:
        if trend_data.get("significant"):
            insight_summary.append(
                f"{col}: {trend_data['trend']} trend (slope={trend_data['slope']:.2f})"
            )
    
    user_message = f"""
Key Insights:
{chr(10).join(insight_summary)}

Validated Insights: {len(validated_insights)} insights with high confidence

Generate 3 specific, actionable business recommendations with quantified expected impact.
"""

    llm_response = await call_llm(
        messages=[{"role": "user", "content": user_message}],
        system=system_prompt,
        json_mode=True
    )
    
    data = json.loads(llm_response)
    
    # Ensure it's a list
    if isinstance(data, dict) and "recommendations" in data:
        recommendations = data["recommendations"]
    elif isinstance(data, list):
        recommendations = data
    else:
        raise ValueError("Invalid LLM response format")
    
    # Add rank
    for i, rec in enumerate(recommendations[:3], 1):
        rec["rank"] = i
    
    return recommendations[:3]


async def _generate_rule_based_recommendations(
    validated_insights: List[Dict],
    kpis: Dict,
    correlations: List[Dict],
    trends: Dict
) -> List[Dict]:
    """Generate recommendations using rules (fallback)"""
    
    recommendations = []
    
    # Recommendation 1: Based on strongest positive trend
    upward_trends = [
        (col, data) for col, data in trends.items()
        if data.get("trend") == "upward" and data.get("significant")
    ]
    
    if upward_trends:
        col, trend_data = upward_trends[0]
        recommendations.append({
            "rank": 1,
            "action": f"Increase investment in {col} by 15%",
            "expected_impact": f"+{abs(trend_data['slope'] * 1.15):.1f}% improvement",
            "timeline": "Q1 (3 months)",
            "risk_level": "medium",
            "confidence": 85,
            "rationale": f"{col} shows strong upward trend (slope={trend_data['slope']:.2f}, p<0.05). Increasing investment should amplify positive momentum."
        })
    
    # Recommendation 2: Based on strongest correlation
    if correlations:
        top_corr = correlations[0]
        if top_corr['r'] > 0:
            recommendations.append({
                "rank": 2,
                "action": f"Optimize {top_corr['col_a']} to improve {top_corr['col_b']}",
                "expected_impact": f"+{abs(top_corr['r'] * 10):.1f}% in {top_corr['col_b']}",
                "timeline": "Q2 (6 months)",
                "risk_level": "low",
                "confidence": 78,
                "rationale": f"Strong positive correlation (r={top_corr['r']:.2f}) indicates {top_corr['col_a']} drives {top_corr['col_b']}. Focus on improving the driver metric."
            })
    
    # Recommendation 3: Based on largest KPI change
    largest_change = None
    largest_change_val = 0
    
    for col, data in kpis.items():
        if "pct_change" in data and abs(data["pct_change"]) > largest_change_val:
            largest_change_val = abs(data["pct_change"])
            largest_change = (col, data)
    
    if largest_change:
        col, data = largest_change
        if data["pct_change"] < 0:
            recommendations.append({
                "rank": 3,
                "action": f"Investigate and address {col} decline",
                "expected_impact": f"Recover {abs(data['pct_change']):.1f}% loss",
                "timeline": "Immediate (1 month)",
                "risk_level": "high",
                "confidence": 72,
                "rationale": f"{col} declined by {data['pct_change']:.1f}%. Immediate action needed to prevent further deterioration."
            })
        else:
            recommendations.append({
                "rank": 3,
                "action": f"Replicate {col} success in other areas",
                "expected_impact": f"+{data['pct_change'] * 0.5:.1f}% overall improvement",
                "timeline": "Q2 (6 months)",
                "risk_level": "low",
                "confidence": 80,
                "rationale": f"{col} grew by {data['pct_change']:.1f}%. Identify and replicate success factors across organization."
            })
    
    # Fill with generic recommendations if needed
    while len(recommendations) < 3:
        recommendations.append({
            "rank": len(recommendations) + 1,
            "action": "Continue monitoring key metrics",
            "expected_impact": "Maintain current performance",
            "timeline": "Ongoing",
            "risk_level": "low",
            "confidence": 60,
            "rationale": "Insufficient data for specific recommendation. Focus on data collection and monitoring."
        })
    
    return recommendations[:3]


async def run_sensitivity_analysis(
    model_prediction_func,
    baseline_input: Dict,
    variable: str,
    target_change: float
) -> Dict:
    """
    Calculate what % change in variable is needed to achieve target change in output.
    """
    
    # Get baseline prediction
    baseline_pred = await model_prediction_func(baseline_input)
    baseline_value = baseline_pred["prediction"]
    
    # Target value
    target_value = baseline_value * (1 + target_change / 100)
    
    # Binary search for required change
    low, high = -50, 200  # Search between -50% and +200%
    best_change = 0
    best_diff = float('inf')
    
    for _ in range(20):  # 20 iterations
        mid = (low + high) / 2
        
        # Test this change
        test_input = baseline_input.copy()
        test_input[variable] = baseline_input[variable] * (1 + mid / 100)
        
        test_pred = await model_prediction_func(test_input)
        test_value = test_pred["prediction"]
        
        diff = abs(test_value - target_value)
        
        if diff < best_diff:
            best_diff = diff
            best_change = mid
        
        if test_value < target_value:
            low = mid
        else:
            high = mid
    
    return {
        "variable": variable,
        "required_change_percent": round(best_change, 2),
        "target_output_change": target_change,
        "baseline_value": baseline_input[variable],
        "required_value": baseline_input[variable] * (1 + best_change / 100),
        "sensitivity": round(target_change / best_change, 3) if best_change != 0 else 0
    }



async def run_what_if_simulation(
    model,
    encoders: Dict,
    feature_names: List[str],
    baseline_data: Dict[str, any],
    parameter: str,
    change_percent: float,
    target_column: str
) -> Dict[str, any]:
    """
    Run what-if simulation: predict outcome if parameter changes by X%.
    
    Args:
        model: Trained ML model
        encoders: Feature encoders from training
        feature_names: List of feature names
        baseline_data: Current values for all features
        parameter: Feature to vary
        change_percent: % change to apply (e.g., 20 for +20%)
        target_column: Name of target variable
    
    Returns:
        {
            "baseline_prediction": float,
            "new_prediction": float,
            "absolute_change": float,
            "percent_change": float,
            "parameter": str,
            "parameter_baseline": float,
            "parameter_new": float,
            "sensitivity_analysis": {...}
        }
    """
    import pandas as pd
    import numpy as np
    
    print(f"\n{'='*80}")
    print(f"WHAT-IF SIMULATION")
    print(f"{'='*80}")
    print(f"Parameter: {parameter}")
    print(f"Change: {change_percent:+.1f}%")
    
    # Validate parameter
    if parameter not in feature_names:
        raise ValueError(f"Parameter '{parameter}' not in model features")
    
    # Prepare baseline input
    baseline_input = prepare_simulation_input(
        baseline_data, feature_names, encoders
    )
    
    # Get baseline prediction
    baseline_pred = model.predict([baseline_input])[0]
    
    print(f"Baseline {target_column}: {baseline_pred:.2f}")
    
    # Modify parameter
    param_index = feature_names.index(parameter)
    modified_input = baseline_input.copy()
    
    # Get original value
    original_value = baseline_data.get(parameter, baseline_input[param_index])
    
    # Apply change
    if isinstance(original_value, (int, float)):
        new_value = original_value * (1 + change_percent / 100)
        # Scale the new value using the same scaler
        if 'scaler' in encoders:
            # Create a dummy array with the new value
            dummy = np.zeros((1, len(feature_names)))
            dummy[0, param_index] = new_value
            scaled = encoders['scaler'].transform(dummy)
            modified_input[param_index] = scaled[0, param_index]
        else:
            modified_input[param_index] = new_value
    else:
        print(f"Warning: Parameter '{parameter}' is not numeric, using baseline")
        new_value = original_value
    
    # Get new prediction
    new_pred = model.predict([modified_input])[0]
    
    print(f"New {target_column}: {new_pred:.2f}")
    
    # Calculate changes
    absolute_change = new_pred - baseline_pred
    percent_change = (absolute_change / baseline_pred * 100) if baseline_pred != 0 else 0
    
    print(f"Change: {absolute_change:+.2f} ({percent_change:+.1f}%)")
    
    # Run sensitivity analysis
    sensitivity = await run_sensitivity_analysis_detailed(
        model, encoders, feature_names, baseline_data, parameter, target_column
    )
    
    print(f"\n{'='*80}")
    print(f"SIMULATION COMPLETE")
    print(f"{'='*80}\n")
    
    return {
        "baseline_prediction": float(baseline_pred),
        "new_prediction": float(new_pred),
        "absolute_change": float(absolute_change),
        "percent_change": float(percent_change),
        "parameter": parameter,
        "parameter_baseline": float(original_value) if isinstance(original_value, (int, float)) else original_value,
        "parameter_new": float(new_value) if isinstance(new_value, (int, float)) else new_value,
        "parameter_change_percent": float(change_percent),
        "target_column": target_column,
        "sensitivity_analysis": sensitivity
    }


def prepare_simulation_input(
    baseline_data: Dict,
    feature_names: List[str],
    encoders: Dict
) -> np.ndarray:
    """Prepare input array for model prediction"""
    import pandas as pd
    import numpy as np
    
    # Create input array
    input_array = np.zeros(len(feature_names))
    
    for i, feature in enumerate(feature_names):
        if feature in baseline_data:
            value = baseline_data[feature]
            
            # Handle categorical encoding
            if feature in encoders and feature != 'scaler' and feature != 'target_encoder':
                try:
                    encoder = encoders[feature]
                    if hasattr(encoder, 'transform'):
                        value = encoder.transform([str(value)])[0]
                except:
                    value = 0
            
            input_array[i] = value
        else:
            # Use median/mode from training data
            input_array[i] = 0
    
    # Apply scaling if scaler exists
    if 'scaler' in encoders:
        input_array = encoders['scaler'].transform([input_array])[0]
    
    return input_array


async def run_sensitivity_analysis_detailed(
    model,
    encoders: Dict,
    feature_names: List[str],
    baseline_data: Dict,
    parameter: str,
    target_column: str
) -> Dict[str, any]:
    """
    Detailed sensitivity analysis: test multiple parameter values
    """
    import numpy as np
    
    # Test parameter changes from -50% to +50% in 10% increments
    test_changes = list(range(-50, 51, 10))
    results = []
    
    baseline_input = prepare_simulation_input(baseline_data, feature_names, encoders)
    baseline_pred = model.predict([baseline_input])[0]
    
    param_index = feature_names.index(parameter)
    original_value = baseline_data.get(parameter, baseline_input[param_index])
    
    for change_pct in test_changes:
        modified_input = baseline_input.copy()
        
        if isinstance(original_value, (int, float)):
            new_value = original_value * (1 + change_pct / 100)
            
            if 'scaler' in encoders:
                dummy = np.zeros((1, len(feature_names)))
                dummy[0, param_index] = new_value
                scaled = encoders['scaler'].transform(dummy)
                modified_input[param_index] = scaled[0, param_index]
            else:
                modified_input[param_index] = new_value
        
        pred = model.predict([modified_input])[0]
        
        results.append({
            "parameter_change_percent": float(change_pct),
            "parameter_value": float(new_value) if isinstance(original_value, (int, float)) else original_value,
            "predicted_value": float(pred),
            "predicted_change_percent": float((pred - baseline_pred) / baseline_pred * 100) if baseline_pred != 0 else 0
        })
    
    # Calculate elasticity (% change in output / % change in input)
    elasticities = []
    for r in results:
        if r['parameter_change_percent'] != 0:
            elasticity = r['predicted_change_percent'] / r['parameter_change_percent']
            elasticities.append(elasticity)
    
    avg_elasticity = np.mean(elasticities) if elasticities else 0
    
    # Find required change for 10% output increase
    target_output_change = 10.0
    required_input_change = target_output_change / avg_elasticity if avg_elasticity != 0 else 0
    
    return {
        "sensitivity_curve": results,
        "average_elasticity": float(avg_elasticity),
        "interpretation": f"A 1% change in {parameter} leads to {avg_elasticity:.2f}% change in {target_column}",
        "required_change_for_10pct_increase": {
            "parameter": parameter,
            "required_change_percent": float(required_input_change),
            "target_output_change_percent": 10.0
        }
    }


async def generate_scenario_comparison(
    model,
    encoders: Dict,
    feature_names: List[str],
    baseline_data: Dict,
    scenarios: List[Dict[str, float]],
    target_column: str
) -> Dict[str, any]:
    """
    Compare multiple scenarios side-by-side
    
    Args:
        scenarios: List of dicts, each with parameter: change_percent pairs
                  e.g., [{"marketing_budget": 20, "price": -5}, {"marketing_budget": 10}]
    
    Returns:
        Comparison of all scenarios with predictions
    """
    import numpy as np
    
    print(f"\n{'='*80}")
    print(f"SCENARIO COMPARISON")
    print(f"{'='*80}")
    print(f"Comparing {len(scenarios)} scenarios")
    
    # Get baseline
    baseline_input = prepare_simulation_input(baseline_data, feature_names, encoders)
    baseline_pred = model.predict([baseline_input])[0]
    
    scenario_results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}: {scenario}")
        
        # Apply all changes in this scenario
        modified_input = baseline_input.copy()
        
        for param, change_pct in scenario.items():
            if param not in feature_names:
                print(f"  Warning: {param} not in features, skipping")
                continue
            
            param_index = feature_names.index(param)
            original_value = baseline_data.get(param, baseline_input[param_index])
            
            if isinstance(original_value, (int, float)):
                new_value = original_value * (1 + change_pct / 100)
                
                if 'scaler' in encoders:
                    dummy = np.zeros((1, len(feature_names)))
                    dummy[0, param_index] = new_value
                    scaled = encoders['scaler'].transform(dummy)
                    modified_input[param_index] = scaled[0, param_index]
                else:
                    modified_input[param_index] = new_value
        
        # Predict
        pred = model.predict([modified_input])[0]
        change = pred - baseline_pred
        change_pct = (change / baseline_pred * 100) if baseline_pred != 0 else 0
        
        print(f"  Prediction: {pred:.2f} ({change_pct:+.1f}%)")
        
        scenario_results.append({
            "scenario_id": i,
            "changes": scenario,
            "prediction": float(pred),
            "absolute_change": float(change),
            "percent_change": float(change_pct)
        })
    
    # Rank scenarios by predicted outcome
    scenario_results.sort(key=lambda x: x['prediction'], reverse=True)
    
    for i, result in enumerate(scenario_results, 1):
        result['rank'] = i
    
    print(f"\n{'='*80}")
    print(f"COMPARISON COMPLETE")
    print(f"Best scenario: Scenario {scenario_results[0]['scenario_id']}")
    print(f"{'='*80}\n")
    
    return {
        "baseline_prediction": float(baseline_pred),
        "scenarios": scenario_results,
        "best_scenario": scenario_results[0],
        "worst_scenario": scenario_results[-1],
        "target_column": target_column
    }


# Alias for backward compatibility
compare_scenarios = generate_scenario_comparison
