from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from database.db import get_db
from database.models import Dashboard, Dataset
from agents.report_agent import generate_pdf_report, generate_pptx_report
import os

router = APIRouter()


class ReportRequest(BaseModel):
    dashboard_id: str
    format: str = "both"  # "pdf", "pptx", or "both"


@router.post("/generate")
async def generate_report(request: ReportRequest, db: AsyncSession = Depends(get_db)):
    """
    Generate comprehensive business report from dashboard.
    
    Args:
        request: ReportRequest with dashboard_id and format
        db: Database session
    
    Returns:
        Dict with report_id, file paths, and metadata
    """
    
    # Validate dashboard exists
    result = await db.execute(select(Dashboard).where(Dashboard.id == request.dashboard_id))
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail=f"Dashboard {request.dashboard_id} not found")
    
    # Validate dataset exists
    result = await db.execute(select(Dataset).where(Dataset.id == dashboard.dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dashboard.dataset_id} not found")
    
    results = {
        "dashboard_id": request.dashboard_id,
        "dataset_name": dataset.name,
        "formats_generated": []
    }
    
    try:
        # Generate PDF
        if request.format in ["pdf", "both"]:
            pdf_result = await generate_pdf_report(request.dashboard_id, db)
            results["pdf"] = pdf_result
            results["formats_generated"].append("pdf")
        
        # Generate PowerPoint
        if request.format in ["pptx", "both"]:
            pptx_result = await generate_pptx_report(request.dashboard_id, db)
            results["pptx"] = pptx_result
            results["formats_generated"].append("pptx")
        
        return results
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )


@router.get("/{report_id}/pdf")
async def download_pdf(report_id: str):
    """
    Download PDF report by report_id.
    
    Args:
        report_id: Report identifier (e.g., report_20240322_143025)
    
    Returns:
        FileResponse with PDF file
    """
    
    reports_dir = "data/reports"
    pdf_path = os.path.join(reports_dir, f"{report_id}.pdf")
    
    if not os.path.exists(pdf_path):
        # Try to find any PDF with this report_id prefix
        import glob
        matching_files = glob.glob(os.path.join(reports_dir, f"{report_id}*.pdf"))
        if matching_files:
            pdf_path = matching_files[0]
        else:
            raise HTTPException(status_code=404, detail=f"PDF report {report_id} not found")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"talking_bi_{report_id}.pdf"
    )


@router.get("/{report_id}/pptx")
async def download_pptx(report_id: str):
    """
    Download PowerPoint report by report_id.
    
    Args:
        report_id: Report identifier (e.g., report_20240322_143025)
    
    Returns:
        FileResponse with PowerPoint file
    """
    
    reports_dir = "data/reports"
    pptx_path = os.path.join(reports_dir, f"{report_id}.pptx")
    
    if not os.path.exists(pptx_path):
        # Try to find any PPTX with this report_id prefix
        import glob
        matching_files = glob.glob(os.path.join(reports_dir, f"{report_id}*.pptx"))
        if matching_files:
            pptx_path = matching_files[0]
        else:
            raise HTTPException(status_code=404, detail=f"PowerPoint report {report_id} not found")
    
    return FileResponse(
        pptx_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"talking_bi_{report_id}.pptx"
    )


@router.get("/list")
async def list_reports():
    """
    List all available reports.
    
    Returns:
        List of report metadata
    """
    
    reports_dir = "data/reports"
    
    if not os.path.exists(reports_dir):
        return {"reports": []}
    
    import glob
    from datetime import datetime
    
    reports = []
    
    # Find all PDF and PPTX files
    pdf_files = glob.glob(os.path.join(reports_dir, "report_*.pdf"))
    pptx_files = glob.glob(os.path.join(reports_dir, "report_*.pptx"))
    
    # Group by report_id
    report_ids = set()
    for f in pdf_files + pptx_files:
        basename = os.path.basename(f)
        report_id = basename.split('.')[0]
        report_ids.add(report_id)
    
    for report_id in sorted(report_ids, reverse=True):
        pdf_path = os.path.join(reports_dir, f"{report_id}.pdf")
        pptx_path = os.path.join(reports_dir, f"{report_id}.pptx")
        
        report_info = {
            "report_id": report_id,
            "has_pdf": os.path.exists(pdf_path),
            "has_pptx": os.path.exists(pptx_path)
        }
        
        # Get creation time from whichever file exists
        if os.path.exists(pdf_path):
            report_info["created_at"] = datetime.fromtimestamp(
                os.path.getctime(pdf_path)
            ).isoformat()
            report_info["size_pdf"] = os.path.getsize(pdf_path)
        elif os.path.exists(pptx_path):
            report_info["created_at"] = datetime.fromtimestamp(
                os.path.getctime(pptx_path)
            ).isoformat()
        
        if os.path.exists(pptx_path):
            report_info["size_pptx"] = os.path.getsize(pptx_path)
        
        reports.append(report_info)
    
    return {"reports": reports}

