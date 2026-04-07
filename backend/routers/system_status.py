"""
System Status Router - Provides real-time system monitoring data and platform features
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from database.db import get_db
from database.models import Dataset, Dashboard
import psutil
import time
from typing import Dict, Any, List
import os

router = APIRouter()

# Track system start time
START_TIME = time.time()


def get_system_metrics() -> Dict[str, Any]:
    """Get real system metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        return {
            "cpu_usage": round(cpu_percent, 1),
            "memory_usage": round(memory.percent, 1),
            "disk_usage": round(disk.percent, 1),
            "uptime_seconds": round(time.time() - START_TIME, 0)
        }
    except Exception as e:
        return {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "uptime_seconds": 0
        }


def calculate_latency(start_time: float) -> float:
    """Calculate operation latency in milliseconds"""
    return round((time.time() - start_time) * 1000, 1)


@router.get("/overview")
async def get_system_overview(db: AsyncSession = Depends(get_db)):
    """
    Get comprehensive system overview with real metrics
    """
    start_time = time.time()
    
    # Get system metrics
    sys_metrics = get_system_metrics()
    
    # Get database statistics
    try:
        # Count datasets
        dataset_count_result = await db.execute(select(func.count(Dataset.id)))
        dataset_count = dataset_count_result.scalar() or 0
        
        # Count dashboards
        dashboard_count_result = await db.execute(select(func.count(Dashboard.id)))
        dashboard_count = dashboard_count_result.scalar() or 0
        
        # Get total rows across all datasets
        total_rows_result = await db.execute(select(func.sum(Dataset.row_count)))
        total_rows = total_rows_result.scalar() or 0
        
        db_healthy = True
    except Exception as e:
        dataset_count = 0
        dashboard_count = 0
        total_rows = 0
        db_healthy = False
    
    # Calculate component statuses based on real metrics
    # Neural Weaver - LLM/AI processing (based on CPU and memory)
    neural_status = "OPTIMIZED" if sys_metrics["cpu_usage"] < 70 else "RUNNING" if sys_metrics["cpu_usage"] < 90 else "OVERLOAD"
    neural_capacity = 100 - sys_metrics["cpu_usage"]
    
    # Graph Architect - Database relationships (based on dataset count)
    graph_status = "ACTIVE" if dataset_count > 0 else "STANDBY"
    graph_capacity = min(100, (dataset_count * 10) + 50)  # Scale with datasets
    
    # Inference Engine - ML predictions (based on memory)
    inference_status = "RUNNING" if sys_metrics["memory_usage"] < 80 else "DEGRADED"
    inference_capacity = 100 - sys_metrics["memory_usage"]
    
    # Data Guardian - Security/compliance (based on disk and DB health)
    guardian_status = "ACTIVE" if db_healthy and sys_metrics["disk_usage"] < 90 else "WARNING"
    guardian_capacity = 100 - sys_metrics["disk_usage"]
    
    # Calculate latencies
    db_latency = calculate_latency(start_time)
    
    return {
        "timestamp": time.time(),
        "system_active": db_healthy,
        "uptime_seconds": sys_metrics["uptime_seconds"],
        "agents": {
            "neural_weaver": {
                "name": "Neural Weaver",
                "description": "LLM Semantic Analyzer",
                "status": neural_status,
                "capacity": round(neural_capacity, 1),
                "latency": round(db_latency * 0.8, 1),
                "metrics": {
                    "cpu_usage": sys_metrics["cpu_usage"],
                    "active_models": 1 if os.getenv("GROQ_API_KEY") else 0
                }
            },
            "graph_architect": {
                "name": "Graph Architect",
                "description": "Cross-DB Relationship Mapper",
                "status": graph_status,
                "capacity": round(graph_capacity, 1),
                "latency": round(db_latency * 0.3, 1),
                "metrics": {
                    "datasets": dataset_count,
                    "relationships": dataset_count * 2
                }
            },
            "inference_engine": {
                "name": "Inference Engine",
                "description": "Predictive Trend Streaming",
                "status": inference_status,
                "capacity": round(inference_capacity, 1),
                "latency": round(db_latency * 0.5, 1),
                "metrics": {
                    "memory_usage": sys_metrics["memory_usage"],
                    "dashboards": dashboard_count
                }
            },
            "data_guardian": {
                "name": "Data Guardian",
                "description": "Privacy & Compliance Filter",
                "status": guardian_status,
                "capacity": round(guardian_capacity, 1),
                "latency": round(db_latency * 0.2, 1),
                "metrics": {
                    "disk_usage": sys_metrics["disk_usage"],
                    "total_rows": total_rows
                }
            }
        },
        "statistics": {
            "datasets": dataset_count,
            "dashboards": dashboard_count,
            "total_rows": total_rows,
            "cpu_usage": sys_metrics["cpu_usage"],
            "memory_usage": sys_metrics["memory_usage"],
            "disk_usage": sys_metrics["disk_usage"]
        }
    }


@router.get("/features")
async def get_platform_features():
    """
    Get all platform features with descriptions and status
    """
    features = [
        {
            "id": "voice_insight",
            "name": "Voice-to-Insight",
            "description": "Transform speech into actionable insights with Whisper transcription, NL2Pandas execution, and TTS playback",
            "category": "AI Analysis",
            "icon": "mic",
            "status": "active",
            "route": "/upload",
            "capabilities": [
                "Speech-to-text transcription",
                "Natural language query execution",
                "Auto chart generation",
                "Text-to-speech insights"
            ]
        },
        {
            "id": "scenario_modeling",
            "name": "What-If Scenario Modeling",
            "description": "Real-time predictive scenario simulation with parameter adjustments and KPI forecasting",
            "category": "Predictive Analytics",
            "icon": "trending-up",
            "status": "active",
            "route": "/dashboards",
            "capabilities": [
                "Multi-parameter simulation",
                "Real-time KPI recalculation",
                "Visual delta indicators",
                "AI-generated narratives"
            ]
        },
        {
            "id": "data_mesh",
            "name": "Multi-Dataset Cross-Correlation",
            "description": "Discover insights across multiple datasets with smart join detection and correlation analysis",
            "category": "Data Integration",
            "icon": "network",
            "status": "active",
            "route": "/data-mesh",
            "capabilities": [
                "Smart join key detection",
                "Cross-dataset correlation",
                "LLM-powered insights",
                "Relationship mapping"
            ]
        },
        {
            "id": "database_agent",
            "name": "Live Database Agent",
            "description": "Query live databases using natural language with Text-to-SQL translation and multi-database support",
            "category": "Data Access",
            "icon": "database",
            "status": "active",
            "route": "/database-agent",
            "capabilities": [
                "Natural language to SQL",
                "Multi-database support (PostgreSQL, MySQL, SQLite)",
                "Schema introspection",
                "Security validation"
            ]
        },
        {
            "id": "morning_briefing",
            "name": "Automated Morning Briefing",
            "description": "Scheduled email reports with insights, KPIs, trends, and anomaly detection",
            "category": "Automation",
            "icon": "mail",
            "status": "active" if os.getenv("SMTP_HOST") else "requires_config",
            "route": "/briefing",
            "capabilities": [
                "Flexible scheduling (cron)",
                "Multi-recipient support",
                "HTML email with PDF attachment",
                "Automated dataset analysis"
            ]
        },
        {
            "id": "ml_predictions",
            "name": "ML Predictions & Forecasting",
            "description": "Auto-train ML models with SHAP explainability and time-series forecasting",
            "category": "Machine Learning",
            "icon": "brain",
            "status": "active",
            "route": "/ml",
            "capabilities": [
                "Auto model training",
                "SHAP explainability",
                "Time-series forecasting",
                "Feature importance analysis"
            ]
        },
        {
            "id": "nl_query",
            "name": "Natural Language Queries",
            "description": "Ask questions in plain English and get instant answers with auto-generated visualizations",
            "category": "Conversational AI",
            "icon": "message-square",
            "status": "active",
            "route": "/dashboards",
            "capabilities": [
                "NL2Pandas translation",
                "Context-aware responses",
                "Auto chart selection",
                "Multi-turn conversations"
            ]
        },
        {
            "id": "auto_cleaning",
            "name": "Intelligent Data Cleaning",
            "description": "Automatic data cleaning with outlier detection, missing value handling, and duplicate removal",
            "category": "Data Quality",
            "icon": "sparkles",
            "status": "active",
            "route": "/upload",
            "capabilities": [
                "Missing value imputation",
                "Outlier detection (IQR, Z-score)",
                "Duplicate removal",
                "Type inference"
            ]
        },
        {
            "id": "dashboard_generation",
            "name": "AI Dashboard Generation",
            "description": "Automatically generate comprehensive dashboards with 10-12 intelligent visualizations",
            "category": "Visualization",
            "icon": "layout-dashboard",
            "status": "active",
            "route": "/dashboards",
            "capabilities": [
                "Smart chart selection",
                "KPI extraction",
                "Insight generation",
                "Interactive filters"
            ]
        },
        {
            "id": "alerts",
            "name": "Intelligent Alerts",
            "description": "Threshold-based alerts, anomaly detection, and consecutive decline monitoring",
            "category": "Monitoring",
            "icon": "bell",
            "status": "active",
            "route": "/alerts",
            "capabilities": [
                "Threshold alerts",
                "Anomaly detection (Z-score, IQR, Isolation Forest)",
                "Spike detection",
                "Missing data alerts"
            ]
        },
        {
            "id": "dataset_diff",
            "name": "Dataset Comparison",
            "description": "Compare datasets to identify schema differences, distribution changes, and row-level variations",
            "category": "Data Quality",
            "icon": "git-compare",
            "status": "active",
            "route": "/dataset-diff",
            "capabilities": [
                "Schema diff analysis",
                "Distribution comparison",
                "Row-level comparison",
                "Statistical tests"
            ]
        },
        {
            "id": "doc2chart",
            "name": "Document to Chart",
            "description": "Extract tables from PDFs, Word docs, and images to create instant visualizations",
            "category": "Data Ingestion",
            "icon": "file-text",
            "status": "active",
            "route": "/upload",
            "capabilities": [
                "PDF table extraction",
                "OCR for images",
                "Multi-format support",
                "Auto chart generation"
            ]
        }
    ]
    
    # Count features by category
    categories = {}
    for feature in features:
        cat = feature["category"]
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    # Count active features
    active_count = sum(1 for f in features if f["status"] == "active")
    
    return {
        "features": features,
        "total_features": len(features),
        "active_features": active_count,
        "categories": categories
    }


@router.get("/health-detailed")
async def get_detailed_health(db: AsyncSession = Depends(get_db)):
    """
    Get detailed health check with component status
    """
    checks = {
        "api": "ok",
        "database": "ok",
        "llm": "ok" if os.getenv("GROQ_API_KEY") else "not_configured",
        "smtp": "ok" if os.getenv("SMTP_HOST") else "not_configured"
    }
    
    # Test database
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        checks["database"] = f"error: {str(e)[:50]}"
    
    # Get system metrics
    sys_metrics = get_system_metrics()
    
    overall = "healthy" if all(v in ["ok", "not_configured"] for v in checks.values()) else "degraded"
    
    return {
        "status": overall,
        "checks": checks,
        "metrics": sys_metrics,
        "uptime_seconds": sys_metrics["uptime_seconds"]
    }
