"""
What-If Service - Scenario simulation and sensitivity analysis
Enables users to test different scenarios and understand parameter impacts
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import MLModel, Dataset
from agents.strategist_agent import run_what_if_simulation, run_sensitivity_analysis, compare_scenarios


async def simulate_scenario(
    db: AsyncSession,
    dataset_id: str,
    parameter_changes: Dict[str, float],
    target_metric: str
) -> Dict:
    """
    Simulate a what-if scenario with parameter changes.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        parameter_changes: Dict of {parameter: new_value}
        target_metric: Metric to analyze
    
    Returns:
        Simulation result with predicted impact
    """
    import pickle
    import os
    
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found")
    
    # Find a trained model for this dataset and target
    model_result = await db.execute(
        select(MLModel)
        .where(MLModel.dataset_id == dataset_id)
        .where(MLModel.target_column == target_metric)
        .order_by(MLModel.created_at.desc())
        .limit(1)
    )
    ml_model = model_result.scalar_one_or_none()
    
    if not ml_model:
        raise ValueError(f"No trained model found for dataset {dataset_id} with target {target_metric}")
    
    # Load the model and encoders
    model_path = ml_model.model_path
    if not os.path.exists(model_path):
        raise ValueError(f"Model file not found: {model_path}")
    
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    model = model_data['model']
    encoders = model_data['encoders']
    feature_names = model_data['feature_names']
    
    # Load data
    from sqlalchemy import text
    query_sql = f'SELECT * FROM "{dataset.sqlite_table_name}"'
    result = await db.execute(text(query_sql))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    
    if df.empty:
        raise ValueError("Dataset is empty")
    
    # Get baseline data (average of all rows)
    baseline_data = {}
    for col in df.columns:
        if col != target_metric:
            if df[col].dtype in ['int64', 'float64']:
                baseline_data[col] = float(df[col].mean())
            else:
                # For categorical, use mode
                mode_val = df[col].mode()
                baseline_data[col] = mode_val[0] if len(mode_val) > 0 else df[col].iloc[0]
    
    # Apply parameter changes to baseline
    for param, new_value in parameter_changes.items():
        if param in baseline_data:
            baseline_data[param] = new_value
    
    # Calculate baseline prediction (without changes)
    original_baseline = baseline_data.copy()
    for param in parameter_changes.keys():
        if param in original_baseline:
            # Restore original value for baseline
            if df[param].dtype in ['int64', 'float64']:
                original_baseline[param] = float(df[param].mean())
    
    # Run predictions
    from agents.ml_agent import predict_with_model
    
    # Baseline prediction
    baseline_df = pd.DataFrame([original_baseline])
    baseline_pred = await predict_with_model(model_path, baseline_df)
    baseline_value = baseline_pred['predictions'][0]
    
    # New prediction with changes
    new_df = pd.DataFrame([baseline_data])
    new_pred = await predict_with_model(model_path, new_df)
    predicted_value = new_pred['predictions'][0]
    
    # Calculate impact
    impact = predicted_value - baseline_value
    impact_pct = (impact / baseline_value * 100) if baseline_value != 0 else 0
    
    return {
        "baseline_value": baseline_value,
        "predicted_value": predicted_value,
        "impact": impact,
        "impact_pct": impact_pct,
        "parameter_changes": parameter_changes,
        "target_metric": target_metric
    }


async def analyze_sensitivity(
    db: AsyncSession,
    dataset_id: str,
    target_metric: str,
    parameters: Optional[List[str]] = None,
    variation_range: float = 0.2
) -> Dict:
    """
    Perform sensitivity analysis on parameters.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        target_metric: Metric to analyze
        parameters: List of parameters to vary (auto-detect if None)
        variation_range: Percentage variation (0.2 = ±20%)
    
    Returns:
        Sensitivity analysis results
    """
    # Get dataset
    dataset = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset.scalar_one_or_none()
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found")
    
    # Load data
    from sqlalchemy import text
    query_sql = f'SELECT * FROM "{dataset.sqlite_table_name}"'
    result = await db.execute(text(query_sql))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    
    if df.empty:
        raise ValueError("Dataset is empty")
    
    # Auto-detect parameters if not provided
    if parameters is None:
        # Use numeric columns as parameters
        parameters = df.select_dtypes(include=['number']).columns.tolist()
        # Remove target metric from parameters
        if target_metric in parameters:
            parameters.remove(target_metric)
        # Limit to top 5 most important
        parameters = parameters[:5]
    
    # Run sensitivity analysis using strategist agent
    sensitivity_result = await run_sensitivity_analysis(
        df=df,
        target_metric=target_metric,
        parameters=parameters,
        variation_range=variation_range
    )
    
    return sensitivity_result


async def compare_multiple_scenarios(
    db: AsyncSession,
    dataset_id: str,
    scenarios: List[Dict[str, Any]],
    target_metric: str
) -> Dict:
    """
    Compare multiple what-if scenarios side by side.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        scenarios: List of scenario dictionaries with parameter changes
        target_metric: Metric to compare
    
    Returns:
        Comparison results with rankings
    """
    # Get dataset
    dataset = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset.scalar_one_or_none()
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found")
    
    # Load data
    from sqlalchemy import text
    query_sql = f'SELECT * FROM "{dataset.sqlite_table_name}"'
    result = await db.execute(text(query_sql))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    
    if df.empty:
        raise ValueError("Dataset is empty")
    
    # Run comparison using strategist agent
    comparison_result = await compare_scenarios(
        df=df,
        scenarios=scenarios,
        target_metric=target_metric
    )
    
    return comparison_result


async def optimize_parameters(
    db: AsyncSession,
    dataset_id: str,
    target_metric: str,
    parameters: List[str],
    objective: str = "maximize",
    constraints: Optional[Dict[str, tuple]] = None
) -> Dict:
    """
    Find optimal parameter values to maximize/minimize target metric.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        target_metric: Metric to optimize
        parameters: Parameters to optimize
        objective: "maximize" or "minimize"
        constraints: Dict of {parameter: (min, max)}
    
    Returns:
        Optimization results with optimal values
    """
    # Get dataset
    dataset = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset.scalar_one_or_none()
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found")
    
    # Load data
    from sqlalchemy import text
    query_sql = f'SELECT * FROM "{dataset.sqlite_table_name}"'
    result = await db.execute(text(query_sql))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    
    if df.empty:
        raise ValueError("Dataset is empty")
    
    # Get current baseline
    baseline_value = df[target_metric].mean()
    
    # Simple grid search optimization
    best_value = baseline_value
    best_params = {}
    
    # Define search space
    if constraints is None:
        constraints = {}
        for param in parameters:
            if param in df.columns and df[param].dtype in ['int64', 'float64']:
                param_min = df[param].min()
                param_max = df[param].max()
                constraints[param] = (param_min, param_max)
    
    # Grid search (5 points per parameter)
    search_results = []
    
    for param in parameters:
        if param not in constraints:
            continue
        
        param_min, param_max = constraints[param]
        param_values = np.linspace(param_min, param_max, 5)
        
        for value in param_values:
            # Simulate this parameter change
            param_changes = {param: float(value)}
            
            try:
                sim_result = await run_what_if_simulation(
                    df=df,
                    parameter_changes=param_changes,
                    target_metric=target_metric
                )
                
                predicted_value = sim_result.get('predicted_value', baseline_value)
                
                search_results.append({
                    "parameters": param_changes,
                    "predicted_value": predicted_value,
                    "improvement": predicted_value - baseline_value
                })
                
                # Update best if better
                if objective == "maximize":
                    if predicted_value > best_value:
                        best_value = predicted_value
                        best_params = param_changes.copy()
                else:  # minimize
                    if predicted_value < best_value:
                        best_value = predicted_value
                        best_params = param_changes.copy()
            
            except Exception as e:
                print(f"Error in optimization iteration: {e}")
                continue
    
    return {
        "target_metric": target_metric,
        "objective": objective,
        "baseline_value": baseline_value,
        "optimal_value": best_value,
        "optimal_parameters": best_params,
        "improvement": best_value - baseline_value,
        "improvement_pct": ((best_value - baseline_value) / baseline_value * 100) if baseline_value != 0 else 0,
        "search_results": sorted(
            search_results,
            key=lambda x: x['predicted_value'],
            reverse=(objective == "maximize")
        )[:10],  # Top 10 results
        "parameters_tested": parameters,
        "iterations": len(search_results)
    }




