"""
Export Router - API endpoints for exporting dashboards, charts, and data
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, Dict
from database.db import get_db
from services import export_service
import os

router = APIRouter()


class ExportDashboardRequest(BaseModel):
    dashboard_id: str
    include_data: bool = False


class ImportDashboardRequest(BaseModel):
    dashboard_json: dict
    dataset_id: Optional[str] = None


class ExportChartRequest(BaseModel):
    chart_data: dict
    chart_config: dict
    width: int = 800
    height: int = 600
    dpi: int = 150


class ExportDataRequest(BaseModel):
    dataset_id: str
    filters: Optional[Dict] = None


class ExportBundleRequest(BaseModel):
    dashboard_id: str


@router.post("/dashboard/json")
async def export_dashboard_json(request: ExportDashboardRequest, db: AsyncSession = Depends(get_db)):
    """
    Export dashboard configuration as JSON.
    
    Request body:
    - dashboard_id: Dashboard ID
    - include_data: Whether to include actual data
    
    Returns:
    - Dashboard JSON export
    """
    try:
        result = await export_service.export_dashboard_json(
            db=db,
            dashboard_id=request.dashboard_id,
            include_data=request.include_data
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/dashboard/import")
async def import_dashboard_json(request: ImportDashboardRequest, db: AsyncSession = Depends(get_db)):
    """
    Import dashboard from JSON configuration.
    
    Request body:
    - dashboard_json: Dashboard JSON data
    - dataset_id: Optional dataset ID to use
    
    Returns:
    - Imported dashboard information
    """
    try:
        result = await export_service.import_dashboard_json(
            db=db,
            dashboard_json=request.dashboard_json,
            dataset_id=request.dataset_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/chart/png")
async def export_chart_png(request: ExportChartRequest):
    """
    Export a single chart as PNG image.
    
    Request body:
    - chart_data: Chart data dictionary
    - chart_config: Chart configuration
    - width: Image width in pixels
    - height: Image height in pixels
    - dpi: Image DPI
    
    Returns:
    - Base64 encoded PNG image
    """
    try:
        result = await export_service.export_chart_png(
            chart_data=request.chart_data,
            chart_config=request.chart_config,
            output_path=None,  # Return base64
            width=request.width,
            height=request.height,
            dpi=request.dpi
        )
        return {"image": result, "format": "base64"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart export failed: {str(e)}")


@router.post("/data/csv")
async def export_data_csv(request: ExportDataRequest, db: AsyncSession = Depends(get_db)):
    """
    Export dataset as CSV file.
    
    Request body:
    - dataset_id: Dataset ID
    - filters: Optional filters to apply
    
    Returns:
    - CSV file download
    """
    try:
        csv_string = await export_service.export_data_csv(
            db=db,
            dataset_id=request.dataset_id,
            output_path=None,  # Return string
            filters=request.filters
        )
        
        return Response(
            content=csv_string,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=data_{request.dataset_id}.csv"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV export failed: {str(e)}")


@router.post("/dashboard/bundle")
async def export_dashboard_bundle(request: ExportBundleRequest, db: AsyncSession = Depends(get_db)):
    """
    Export complete dashboard bundle (JSON + charts + data).
    
    Request body:
    - dashboard_id: Dashboard ID
    
    Returns:
    - Export bundle information with file paths
    """
    try:
        result = await export_service.export_dashboard_bundle(
            db=db,
            dashboard_id=request.dashboard_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        print(f"Bundle export error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Bundle export failed: {str(e)}")


@router.get("/dashboard/bundle/{export_id}/download")
async def download_bundle(export_id: str):
    """
    Download a previously exported dashboard bundle.
    
    Path params:
    - export_id: Export ID from bundle export
    
    Returns:
    - ZIP file download (future enhancement)
    """
    # For now, return the directory path
    # In production, this would create a ZIP file
    bundle_dir = f"data/exports/{export_id}"
    
    if not os.path.exists(bundle_dir):
        raise HTTPException(status_code=404, detail="Export bundle not found")
    
    return {
        "export_id": export_id,
        "bundle_dir": bundle_dir,
        "message": "Bundle available at specified directory",
        "note": "ZIP download will be implemented in future version"
    }

