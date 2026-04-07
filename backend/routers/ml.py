from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from database.db import get_db
from services import ml_service, what_if_service

router = APIRouter()


class TrainRequest(BaseModel):
    dataset_id: str
    target_column: str
    feature_columns: Optional[List[str]] = None
    task_type: str = "auto"


class PredictRequest(BaseModel):
    data: List[Dict[str, Any]]


class ForecastRequest(BaseModel):
    periods: int = 12
    frequency: str = "M"  # D, W, M, Q, Y


class WhatIfRequest(BaseModel):
    dataset_id: str
    parameter_changes: Dict[str, float]
    target_metric: str


class SensitivityRequest(BaseModel):
    dataset_id: str
    target_metric: str
    parameters: Optional[List[str]] = None
    variation_range: float = 0.2


class ScenarioComparisonRequest(BaseModel):
    dataset_id: str
    scenarios: List[Dict[str, Any]]
    target_metric: str


class OptimizeRequest(BaseModel):
    dataset_id: str
    target_metric: str
    parameters: List[str]
    objective: str = "maximize"  # or "minimize"
    constraints: Optional[Dict[str, tuple]] = None



@router.post("/train")
async def train_model(request: TrainRequest, db: AsyncSession = Depends(get_db)):
    """
    Train a new ML model on dataset.
    
    Request body:
    - dataset_id: Dataset ID
    - target_column: Target column name
    - feature_columns: Optional list of feature columns
    - task_type: "auto", "regression", or "classification"
    
    Returns:
    - model_id: ID of trained model
    - metrics: Performance metrics
    - feature_importance: Feature importance scores
    """
    try:
        result = await ml_service.train_model(
            db=db,
            dataset_id=request.dataset_id,
            target_column=request.target_column,
            feature_columns=request.feature_columns,
            task_type=request.task_type
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.get("/models")
async def list_models(dataset_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """
    List all trained ML models.
    
    Query params:
    - dataset_id: Optional filter by dataset
    
    Returns:
    - List of model metadata
    """
    try:
        models = await ml_service.list_models(db=db, dataset_id=dataset_id)
        return {"models": models, "count": len(models)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_id}")
async def get_model(model_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get detailed information about a specific model.
    
    Path params:
    - model_id: Model ID
    
    Returns:
    - Model metadata and metrics
    """
    try:
        model = await ml_service.get_model(db=db, model_id=model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/models/{model_id}")
async def delete_model(model_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a trained model.
    
    Path params:
    - model_id: Model ID
    
    Returns:
    - Success status
    """
    try:
        success = await ml_service.delete_model(db=db, model_id=model_id)
        if not success:
            raise HTTPException(status_code=404, detail="Model not found")
        return {"success": True, "message": "Model deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/predict")
async def predict(
    model_id: str,
    request: PredictRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Make predictions using a trained model.
    
    Path params:
    - model_id: Model ID
    
    Request body:
    - data: List of dictionaries with feature values
    
    Returns:
    - predictions: List of predicted values
    - confidence: Confidence scores
    """
    try:
        result = await ml_service.make_predictions(
            db=db,
            model_id=model_id,
            data=request.data
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/models/{model_id}/forecast")
async def forecast(
    model_id: str,
    request: ForecastRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate future forecasts using a trained model.
    
    Path params:
    - model_id: Model ID
    
    Request body:
    - periods: Number of periods to forecast
    - frequency: Time frequency (D, W, M, Q, Y)
    
    Returns:
    - forecast_dates: List of future dates
    - predictions: Predicted values
    - confidence_intervals: Upper and lower bounds
    """
    try:
        result = await ml_service.forecast_future(
            db=db,
            model_id=model_id,
            periods=request.periods,
            frequency=request.frequency
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting failed: {str(e)}")


@router.post("/models/{model_id}/retrain")
async def retrain_model(model_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retrain an existing model with updated data.
    
    Path params:
    - model_id: Model ID
    
    Returns:
    - new_model_id: ID of retrained model
    - improvement: Performance improvement metrics
    """
    try:
        result = await ml_service.retrain_model(db=db, model_id=model_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")


@router.post("/models/compare")
async def compare_models(model_ids: List[str], db: AsyncSession = Depends(get_db)):
    """
    Compare multiple models side by side.
    
    Request body:
    - model_ids: List of model IDs to compare
    
    Returns:
    - models: List of model metrics
    - best_model: ID of best performing model
    """
    try:
        result = await ml_service.compare_models(db=db, model_ids=model_ids)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# What-If Simulation Endpoints

@router.post("/what-if/simulate")
async def simulate_scenario(request: WhatIfRequest, db: AsyncSession = Depends(get_db)):
    """
    Simulate a what-if scenario with parameter changes.
    
    Request body:
    - dataset_id: Dataset ID
    - parameter_changes: Dict of {parameter: new_value}
    - target_metric: Metric to analyze
    
    Returns:
    - predicted_value: Predicted metric value
    - baseline_value: Current metric value
    - impact: Change in metric
    """
    try:
        result = await what_if_service.simulate_scenario(
            db=db,
            dataset_id=request.dataset_id,
            parameter_changes=request.parameter_changes,
            target_metric=request.target_metric
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/what-if/sensitivity")
async def analyze_sensitivity(request: SensitivityRequest, db: AsyncSession = Depends(get_db)):
    """
    Perform sensitivity analysis on parameters.
    
    Request body:
    - dataset_id: Dataset ID
    - target_metric: Metric to analyze
    - parameters: List of parameters to vary
    - variation_range: Percentage variation (0.2 = ±20%)
    
    Returns:
    - sensitivity_scores: Parameter sensitivity rankings
    - impact_analysis: Detailed impact for each parameter
    """
    try:
        result = await what_if_service.analyze_sensitivity(
            db=db,
            dataset_id=request.dataset_id,
            target_metric=request.target_metric,
            parameters=request.parameters,
            variation_range=request.variation_range
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sensitivity analysis failed: {str(e)}")


@router.post("/what-if/compare")
async def compare_scenarios(request: ScenarioComparisonRequest, db: AsyncSession = Depends(get_db)):
    """
    Compare multiple what-if scenarios side by side.
    
    Request body:
    - dataset_id: Dataset ID
    - scenarios: List of scenario dictionaries
    - target_metric: Metric to compare
    
    Returns:
    - scenarios: List of scenario results
    - best_scenario: Best performing scenario
    - rankings: Scenario rankings
    """
    try:
        result = await what_if_service.compare_multiple_scenarios(
            db=db,
            dataset_id=request.dataset_id,
            scenarios=request.scenarios,
            target_metric=request.target_metric
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario comparison failed: {str(e)}")


@router.post("/what-if/optimize")
async def optimize_parameters(request: OptimizeRequest, db: AsyncSession = Depends(get_db)):
    """
    Find optimal parameter values to maximize/minimize target metric.
    
    Request body:
    - dataset_id: Dataset ID
    - target_metric: Metric to optimize
    - parameters: Parameters to optimize
    - objective: "maximize" or "minimize"
    - constraints: Optional parameter constraints
    
    Returns:
    - optimal_value: Optimal metric value
    - optimal_parameters: Optimal parameter values
    - improvement: Improvement over baseline
    """
    try:
        result = await what_if_service.optimize_parameters(
            db=db,
            dataset_id=request.dataset_id,
            target_metric=request.target_metric,
            parameters=request.parameters,
            objective=request.objective,
            constraints=request.constraints
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

