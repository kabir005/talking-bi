"""
Briefing Generator Service
Generates briefing content from dataset analysis.
"""

import logging
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from sqlalchemy import select
from database.models import Dataset
from database.db import get_db
from services.email_service import generate_html_email

logger = logging.getLogger(__name__)


async def generate_briefing_content(dataset_id: str, config: dict) -> dict:
    """Generate briefing content including HTML and PDF."""
    try:
        # Load dataset
        async for db in get_db():
            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            
            if not dataset:
                raise ValueError(f"Dataset {dataset_id} not found")
            
            # Load data
            df = pd.read_csv(dataset.source_path)
            
            # Generate analysis
            analysis = analyze_dataset(df, config)
            
            # Generate HTML
            html = generate_html_email(
                briefing_name=config.get("name", "Daily Briefing"),
                dataset_name=dataset.name,
                summary=analysis["summary"],
                kpis=analysis["kpis"],
                trends=analysis["trends"],
                anomalies=analysis["anomalies"]
            )
            
            # Generate PDF
            pdf = generate_pdf_report(
                briefing_name=config.get("name", "Daily Briefing"),
                dataset_name=dataset.name,
                analysis=analysis
            )
            
            return {
                "subject": f"{config.get('name', 'Daily Briefing')} - {datetime.now().strftime('%B %d, %Y')}",
                "html": html,
                "pdf": pdf,
                "pdf_filename": f"briefing_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
            
    except Exception as e:
        logger.error(f"Failed to generate briefing content: {e}")
        raise


def analyze_dataset(df: pd.DataFrame, config: dict) -> dict:
    """Analyze dataset and extract insights."""
    analysis = {
        "summary": "",
        "kpis": [],
        "trends": [],
        "anomalies": []
    }
    
    try:
        # Generate summary
        row_count = len(df)
        col_count = len(df.columns)
        analysis["summary"] = f"Dataset contains {row_count:,} rows and {col_count} columns. "
        
        # Calculate KPIs
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) > 0:
            for col in numeric_cols[:5]:  # Top 5 numeric columns
                mean_val = df[col].mean()
                analysis["kpis"].append({
                    "label": f"Avg {col}",
                    "value": f"{mean_val:,.2f}"
                })
        
        # Detect trends
        if config.get("include_trends", True):
            for col in numeric_cols[:3]:
                if len(df) > 1:
                    first_val = df[col].iloc[0]
                    last_val = df[col].iloc[-1]
                    change = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
                    direction = "increased" if change > 0 else "decreased"
                    analysis["trends"].append(
                        f"{col} {direction} by {abs(change):.1f}% from start to end"
                    )
        
        # Detect anomalies
        if config.get("include_anomalies", True):
            for col in numeric_cols[:3]:
                mean = df[col].mean()
                std = df[col].std()
                outliers = df[(df[col] > mean + 3*std) | (df[col] < mean - 3*std)]
                if len(outliers) > 0:
                    analysis["anomalies"].append(
                        f"Found {len(outliers)} outliers in {col} (beyond 3 standard deviations)"
                    )
        
        # Enhance summary
        if analysis["trends"]:
            analysis["summary"] += f"Detected {len(analysis['trends'])} significant trends. "
        if analysis["anomalies"]:
            analysis["summary"] += f"Identified {len(analysis['anomalies'])} anomalies requiring attention."
        else:
            analysis["summary"] += "No anomalies detected."
            
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        analysis["summary"] = "Analysis completed with limited insights due to data structure."
    
    return analysis


def generate_pdf_report(briefing_name: str, dataset_name: str, analysis: dict) -> bytes:
    """Generate PDF report."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30
    )
    story.append(Paragraph(briefing_name, title_style))
    story.append(Paragraph(datetime.now().strftime("%B %d, %Y"), styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Paragraph(analysis["summary"], styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # KPIs
    if analysis["kpis"]:
        story.append(Paragraph("Key Metrics", styles['Heading2']))
        kpi_data = [[kpi["label"], kpi["value"]] for kpi in analysis["kpis"]]
        kpi_table = Table(kpi_data, colWidths=[3*inch, 2*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.white)
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Trends
    if analysis["trends"]:
        story.append(Paragraph("Trends", styles['Heading2']))
        for trend in analysis["trends"]:
            story.append(Paragraph(f"• {trend}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Anomalies
    if analysis["anomalies"]:
        story.append(Paragraph("Anomalies", styles['Heading2']))
        for anomaly in analysis["anomalies"]:
            story.append(Paragraph(f"• {anomaly}", styles['Normal']))
    else:
        story.append(Paragraph("Anomalies", styles['Heading2']))
        story.append(Paragraph("No anomalies detected.", styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Dataset: {dataset_name}", styles['Normal']))
    story.append(Paragraph("Generated by Talking BI", styles['Normal']))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
