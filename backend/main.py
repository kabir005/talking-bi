import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*urllib3.*")
warnings.filterwarnings("ignore", message=".*chardet.*")

import asyncio
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.db import init_db
from config import CORS_ORIGINS, GROQ_API_KEY

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    print("\n" + "="*80)
    print("🚀 TALKING BI - Starting up...")
    print("="*80)

    # ── Startup Validation ────────────────────────────────────────────────────
    if not GROQ_API_KEY or len(GROQ_API_KEY) < 10:
        logger.critical("⚠ GROQ_API_KEY is missing or too short — LLM agents will fall back to rule-based mode")
    else:
        print("✓ Groq API key configured")

    # Pipeline concurrency guard (prevents overlapping heavy pipelines)
    app.state.PIPELINE_LOCK = asyncio.Semaphore(3)   # max 3 concurrent pipelines
    print("✓ Pipeline semaphore initialized (max 3 concurrent)")

    await init_db()
    print("✓ Database initialized")

    # Initialize memory systems (optional - will work without if dependencies missing)
    try:
        from memory.faiss_store import init_faiss
        await init_faiss()
        print("✓ FAISS memory initialized")
    except Exception as e:
        print(f"⚠ FAISS memory not available (optional): {str(e)[:50]}")

    try:
        from memory.chroma_store import init_chroma
        await init_chroma()
        print("✓ ChromaDB memory initialized")
    except Exception as e:
        print(f"⚠ ChromaDB memory not available (optional): {str(e)[:50]}")
    
    # Initialize RAG service
    try:
        from services.rag_service import init_rag
        await init_rag()
        print("✓ RAG service initialized")
    except Exception as e:
        print(f"⚠ RAG service not available (optional): {str(e)[:50]}")
    
    # Initialize scheduler for briefings
    try:
        from services.scheduler import init_scheduler
        await init_scheduler()
        print("✓ Briefing scheduler initialized")
    except Exception as e:
        print(f"⚠ Briefing scheduler not available: {str(e)[:50]}")

    # Check Celery/Redis availability
    try:
        from tasks.celery_app import celery_app
        inspect = celery_app.control.inspect(timeout=1.0)
        active = inspect.active()
        if active is not None:
            print(f"✓ Celery workers online: {list(active.keys())}")
        else:
            print("⚠ Celery workers offline — pipeline will run synchronously (no background tasks)")
    except Exception as e:
        print(f"⚠ Celery/Redis not available — running in sync mode: {str(e)[:60]}")

    print("\n" + "="*80)
    print("✅ TALKING BI API - Ready!")
    print("📊 Dashboard generation: ENABLED")
    print("🤖 Query system: ENABLED")
    print("🧠 LLM Insights: ENABLED (Groq llama-3.3-70b)")
    print("📈 Chart types: 10-12 charts per dashboard")
    print("🔴 Background tasks: Redis+Celery (if available)")
    print("="*80)
    print("🌐 API running at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("💡 Health check: http://localhost:8000/health")
    print("="*80 + "\n")

    yield

    # Shutdown scheduler
    try:
        from services.scheduler import shutdown_scheduler
        await shutdown_scheduler()
    except:
        pass

    print("\n" + "="*80)
    print("👋 TALKING BI - Shutting down...")
    print("="*80 + "\n")


app = FastAPI(
    title="Talking BI API",
    version="2.0.0",
    description="Agentic AI-powered Business Intelligence Platform",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from routers import upload, datasets, dashboards, agents, query, ml, reports, scrape
from routers import export_router, knowledge_graph, export as export_new
from routers import drilldown, filters, memory, insights_regenerate, nl_query
from routers import pipeline_status_router
from routers import conversation, forecast, localization, alerts, doc2chart, dataset_diff
from routers import story_mode, llm_provider, auth, voice_insight, scenario, data_mesh, db_agent, briefing, system_status

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(dashboards.router, prefix="/api/dashboards", tags=["Dashboards"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(nl_query.router, prefix="/api/nl-query", tags=["NL Query"])
app.include_router(ml.router, prefix="/api/ml", tags=["ML"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(scrape.router, prefix="/api/scrape", tags=["Scrape"])
app.include_router(export_router.router, prefix="/api/export", tags=["Export"])
app.include_router(knowledge_graph.router, prefix="/api/knowledge-graph", tags=["Knowledge Graph"])
app.include_router(export_new.router, prefix="/api/export-v2", tags=["Export V2"])
app.include_router(drilldown.router, prefix="/api/drilldown", tags=["Drill-Down"])
app.include_router(filters.router, prefix="/api/filters", tags=["Filters"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
app.include_router(insights_regenerate.router, prefix="/api", tags=["Insights"])
app.include_router(pipeline_status_router.router, prefix="/api", tags=["Pipeline Status"])
app.include_router(conversation.router, prefix="/api/conversation", tags=["Conversation"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])
app.include_router(localization.router, prefix="/api/localization", tags=["Localization"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(doc2chart.router, prefix="/api/doc2chart", tags=["Doc2Chart"])
app.include_router(dataset_diff.router, prefix="/api/dataset-diff", tags=["Dataset Diff"])
app.include_router(story_mode.router, prefix="/api/story", tags=["Story Mode"])
app.include_router(llm_provider.router, prefix="/api/llm", tags=["LLM Provider"])
app.include_router(voice_insight.router, prefix="/api/voice-insight", tags=["Voice Insight"])
app.include_router(scenario.router, prefix="/api/scenario", tags=["Scenario"])
app.include_router(data_mesh.router, prefix="/api/data-mesh", tags=["Data Mesh"])
app.include_router(db_agent.router, prefix="/api/db-agent", tags=["Database Agent"])
app.include_router(briefing.router, prefix="/api/briefing", tags=["Briefing"])
app.include_router(system_status.router, prefix="/api/system", tags=["System Status"])


@app.get("/")
async def root():
    return {
        "message": "Talking BI API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    checks = {"api": "ok", "database": "ok"}
    try:
        from database.db import engine
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception as e:
        checks["database"] = f"error: {str(e)[:50]}"

    overall = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"
    return {"status": overall, "checks": checks}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*80)
    print("🚀 Starting Talking BI API Server...")
    print("="*80)
    print("\n💡 TIP: For production with Celery workers, use:")
    print("   python start_server.py")
    print("\n" + "="*80 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

