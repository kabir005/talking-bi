# KIRO AGENT PROMPT — AGENTIC AI BUSINESS INTELLIGENCE PLATFORM
## "Talking BI" — Complete Implementation Specification

---

> **Directive:** Build a full-stack, production-ready, agentic AI-powered Business Intelligence platform called **Talking BI**. This is a Power BI replacement that is 100% free to run, fully autonomous, multi-agent, and context-aware. Every single feature described below must be implemented. No stubs, no placeholders, no "TODO" comments in final code. Use only free APIs and free-tier services.

---

## 0. PROJECT OVERVIEW

**Name:** Talking BI  
**Tagline:** "Upload data. Ask anything. Understand everything."  
**What it is:** An autonomous agentic platform that ingests data from multiple sources (files, web scraping, APIs), cleans it automatically, generates intelligent dashboards, performs ML predictions, runs multi-agent reasoning with validation, and explains every insight in plain English.  
**Stack constraint:** 100% free. No PostgreSQL. No paid APIs.  

---

## 1. COMPLETE TECH STACK

### Backend
- **Runtime:** Python 3.11+
- **Framework:** FastAPI with async/await throughout
- **Data processing:** Pandas, NumPy
- **ML:** scikit-learn, PyCaret (free), SHAP (explainability)
- **Web scraping:** Playwright (headless), BeautifulSoup4, lxml
- **Vector memory:** FAISS (local), ChromaDB (local)
- **Knowledge graph:** NetworkX
- **Embeddings:** sentence-transformers (local, free — `all-MiniLM-L6-v2` model)
- **LLM:** Groq API (free tier) — model: `llama-3.1-70b-versatile` with fallback to `llama-3.1-8b-instant`
- **Storage:** SQLite (via SQLAlchemy), JSON flat files
- **Report generation:** ReportLab (PDF), python-pptx (PowerPoint)
- **Task queue:** asyncio + concurrent.futures for parallel agent execution
- **File parsing:** openpyxl (Excel), pandas (CSV), json stdlib (JSON)
- **HTTP client:** httpx (async)
- **Environment:** python-dotenv

### Frontend
- **Framework:** React 18 + TypeScript + Vite
- **Styling:** TailwindCSS + custom CSS variables
- **Charts:** Recharts (primary) + Chart.js (secondary for specific types)
- **Dashboard layout:** react-grid-layout (drag, drop, resize)
- **Maps:** Leaflet.js + react-leaflet
- **Knowledge graph viz:** react-force-graph
- **State management:** Zustand
- **HTTP:** Axios
- **File upload:** react-dropzone
- **PDF/PNG export:** html2canvas + jsPDF
- **Animations:** Framer Motion
- **Icons:** Lucide React
- **Fonts:** Load from Google Fonts — `DM Sans` (body) + `Bricolage Grotesque` (headings) + `JetBrains Mono` (code/data)
- **Notifications:** react-hot-toast

### Infrastructure (all free tier)
- **Backend deploy:** Render.com (free tier)
- **Frontend deploy:** Vercel (free tier)
- **File storage:** Local filesystem with SQLite metadata

---

## 2. PROJECT FILE STRUCTURE

```
Talking-bi/
├── backend/
│   ├── main.py                          # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── config.py                        # Settings, env vars
│   ├── database/
│   │   ├── db.py                        # SQLite + SQLAlchemy setup
│   │   ├── models.py                    # ORM models
│   │   └── migrations/
│   ├── agents/
│   │   ├── orchestrator.py              # Master orchestrator agent
│   │   ├── cleaning_agent.py            # Data cleaning agent
│   │   ├── analyst_agent.py             # Statistical analysis agent
│   │   ├── critic_agent.py              # Validation + confidence agent
│   │   ├── strategist_agent.py          # Recommendations + what-if agent
│   │   ├── scrape_agent.py              # Web scraping agent
│   │   ├── chart_agent.py               # Chart recommendation agent
│   │   ├── insight_agent.py             # NL insight generation agent
│   │   ├── ml_agent.py                  # Auto ML builder agent
│   │   ├── root_cause_agent.py          # Root cause analysis agent
│   │   └── report_agent.py              # Report generation agent
│   ├── memory/
│   │   ├── faiss_store.py               # FAISS vector store
│   │   ├── chroma_store.py              # ChromaDB store
│   │   └── preference_store.py          # User preference learning
│   ├── services/
│   │   ├── ingestion_service.py         # File + API ingestion
│   │   ├── cleaning_service.py          # Data cleaning pipeline
│   │   ├── ml_service.py                # scikit-learn + PyCaret
│   │   ├── chart_service.py             # Chart config generation
│   │   ├── export_service.py            # PDF + PPT export
│   │   ├── knowledge_graph_service.py   # NetworkX graph
│   │   └── what_if_service.py           # Simulation engine
│   ├── routers/
│   │   ├── upload.py                    # File upload endpoints
│   │   ├── datasets.py                  # Dataset CRUD
│   │   ├── dashboards.py                # Dashboard CRUD
│   │   ├── agents.py                    # Agent trigger endpoints
│   │   ├── query.py                     # Conversational query endpoint
│   │   ├── ml.py                        # ML endpoints
│   │   ├── reports.py                   # Report generation
│   │   ├── scrape.py                    # Scraping endpoints
│   │   └── export.py                    # Export endpoints
│   └── utils/
│       ├── llm.py                       # Groq API client + retry logic
│       ├── schema_detector.py           # Column type inference
│       ├── stats_utils.py               # Statistical helpers
│       └── serializers.py              # DataFrame → JSON serializers
│
└── frontend/
    ├── index.html
    ├── vite.config.ts
    ├── tailwind.config.ts
    ├── tsconfig.json
    ├── package.json
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css                    # Global styles + CSS variables
        ├── components/
        │   ├── layout/
        │   │   ├── Sidebar.tsx          # Navigation sidebar
        │   │   ├── Topbar.tsx           # Top bar with role selector
        │   │   └── Layout.tsx           # Main layout wrapper
        │   ├── upload/
        │   │   ├── DropZone.tsx         # File drop zone
        │   │   ├── UrlScraper.tsx       # URL input for scraping
        │   │   └── ApiConnector.tsx     # REST API connector form
        │   ├── cleaning/
        │   │   ├── CleaningReport.tsx   # Cleaning results card
        │   │   └── OutlierPanel.tsx     # Outlier review panel
        │   ├── dashboard/
        │   │   ├── DashboardCanvas.tsx  # react-grid-layout canvas
        │   │   ├── ChartTile.tsx        # Individual chart tile wrapper
        │   │   ├── KPICard.tsx          # KPI metric card
        │   │   ├── EditPanel.tsx        # Chart edit slide-over panel
        │   │   ├── PresetSelector.tsx   # 4 preset layout thumbnails
        │   │   ├── DrillDown.tsx        # Drill-down breadcrumb + logic
        │   │   └── FilterBar.tsx        # Global filter bar
        │   ├── charts/
        │   │   ├── LineChart.tsx
        │   │   ├── BarChart.tsx
        │   │   ├── AreaChart.tsx
        │   │   ├── PieChart.tsx
        │   │   ├── ScatterChart.tsx
        │   │   ├── HeatmapChart.tsx
        │   │   ├── HistogramChart.tsx
        │   │   ├── WaterfallChart.tsx
        │   │   ├── TreemapChart.tsx
        │   │   ├── MapChart.tsx         # Leaflet choropleth
        │   │   └── SparklineChart.tsx
        │   ├── ml/
        │   │   ├── MLPanel.tsx          # Auto ML results panel
        │   │   ├── FeatureImportance.tsx # SHAP bar chart
        │   │   ├── PredictionChart.tsx  # Actual vs predicted
        │   │   └── WhatIfSimulator.tsx  # What-if slider controls
        │   ├── insights/
        │   │   ├── InsightPanel.tsx     # AI insight sidebar
        │   │   ├── RootCauseTree.tsx    # Root cause chain visual
        │   │   ├── KnowledgeGraph.tsx   # react-force-graph viz
        │   │   └── AnomalyBadge.tsx     # Anomaly marker on charts
        │   ├── conversation/
        │   │   ├── ConversationBar.tsx  # Bottom NL command bar
        │   │   └── CommandSuggestions.tsx # Suggested commands
        │   ├── reports/
        │   │   ├── ReportPreview.tsx    # Full report preview modal
        │   │   └── ExportMenu.tsx       # PDF / PPT / JSON export
        │   └── shared/
        │       ├── AgentStatusBar.tsx   # Live agent progress indicator
        │       ├── ConfidenceBadge.tsx  # Confidence score badge
        │       ├── MemoryPanel.tsx      # Past queries / memory viewer
        │       └── ThemeToggle.tsx      # Light/dark toggle
        ├── stores/
        │   ├── datasetStore.ts          # Zustand: dataset state
        │   ├── dashboardStore.ts        # Zustand: dashboard state
        │   ├── agentStore.ts            # Zustand: agent run state
        │   └── preferenceStore.ts       # Zustand: user preferences
        ├── hooks/
        │   ├── useAgentRun.ts           # Hook for triggering agent pipeline
        │   ├── useDrillDown.ts          # Drill-down state hook
        │   └── useMemory.ts             # Memory retrieval hook
        ├── api/
        │   └── client.ts                # Axios API client
        ├── types/
        │   └── index.ts                 # All TypeScript interfaces
        └── utils/
            ├── chartHelpers.ts          # Chart config utilities
            └── formatters.ts            # Number / date formatters
```

---

## 3. BACKEND — DETAILED IMPLEMENTATION

### 3.1 FastAPI Main App (`backend/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.db import init_db
from routers import upload, datasets, dashboards, agents, query, ml, reports, scrape, export
from memory.faiss_store import init_faiss
from memory.chroma_store import init_chroma

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_faiss()
    await init_chroma()
    yield

app = FastAPI(title="Talking BI API", version="1.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(dashboards.router, prefix="/api/dashboards", tags=["Dashboards"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(ml.router, prefix="/api/ml", tags=["ML"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(scrape.router, prefix="/api/scrape", tags=["Scrape"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
```

### 3.2 LLM Client (`backend/utils/llm.py`)

Use Groq API exclusively (free tier, no billing required for moderate usage).

```python
import os
import json
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
PRIMARY_MODEL = "llama-3.1-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def call_llm(messages: list[dict], system: str = "", model: str = PRIMARY_MODEL, 
                   json_mode: bool = False) -> str:
    """
    Call Groq API with automatic retry and fallback.
    If PRIMARY_MODEL rate-limits, falls back to FALLBACK_MODEL.
    Returns string content of response.
    If json_mode=True, sets response_format to json_object.
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)
    
    payload = {
        "model": model,
        "messages": full_messages,
        "max_tokens": 4096,
        "temperature": 0.1,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(GROQ_BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and model == PRIMARY_MODEL:
                # Rate limited — fall back to smaller model
                return await call_llm(messages, system, FALLBACK_MODEL, json_mode)
            raise
```

### 3.3 Database Models (`backend/database/models.py`)

```python
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    source_type = Column(String)  # "file", "url", "api"
    source_path = Column(String)  # file path or URL
    row_count = Column(Integer)
    column_count = Column(Integer)
    schema_json = Column(JSON)    # {col_name: dtype, ...}
    sample_json = Column(JSON)    # first 5 rows
    cleaning_log = Column(JSON)   # list of cleaning actions taken
    created_at = Column(DateTime, default=datetime.utcnow)
    sqlite_table_name = Column(String)  # the table this data lives in

class Dashboard(Base):
    __tablename__ = "dashboards"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    dataset_id = Column(String)
    preset = Column(String)        # "executive", "operational", "trend", "comparison"
    layout_json = Column(JSON)     # react-grid-layout positions
    tiles_json = Column(JSON)      # list of tile configs
    filters_json = Column(JSON)    # active filters
    role = Column(String)          # "ceo", "analyst", "marketing"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class QueryMemory(Base):
    __tablename__ = "query_memory"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String)
    query_text = Column(Text)
    response_json = Column(JSON)
    embedding_id = Column(String)   # ID in FAISS index
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    action_type = Column(String)    # "chart_type_change", "axis_swap", "filter_add"
    from_value = Column(String)
    to_value = Column(String)
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class MLModel(Base):
    __tablename__ = "ml_models"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String)
    target_column = Column(String)
    algorithm = Column(String)
    r2_score = Column(Float)
    mae = Column(Float)
    rmse = Column(Float)
    feature_importance = Column(JSON)  # {feature: importance_score}
    model_path = Column(String)        # path to pickled model
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 4. AGENTS — FULL IMPLEMENTATION SPEC

### 4.1 Orchestrator Agent (`backend/agents/orchestrator.py`)

**Role:** The master brain. Receives everything, plans everything, routes everything.

**Input:**
- `dataset_schema`: dict of column names → inferred types
- `dataset_sample`: first 20 rows as JSON
- `user_prompt`: raw user query string
- `user_role`: "ceo" | "analyst" | "marketing" | "default"
- `memory_context`: top-3 semantically similar past queries from FAISS

**System prompt for LLM:**
```
You are the Orchestrator Agent for an agentic BI platform. 
Given a dataset schema, sample data, user prompt, and role, produce a JSON plan.

The plan MUST contain:
{
  "intent": "descriptive string of what user wants",
  "kpis": ["list of column names to compute KPIs for"],
  "chart_configs": [
    {
      "type": "line|bar|area|pie|scatter|heatmap|histogram|waterfall|treemap|map",
      "x_column": "column name",
      "y_column": "column name or null",
      "aggregation": "sum|mean|count|median|max|min",
      "title": "human readable title",
      "color_by": "column name or null",
      "filters": []
    }
  ],
  "preset": "executive|operational|trend|comparison",
  "role_filter": "which columns/charts to hide for this role",
  "questions_for_analyst": ["what trends to detect", "what anomalies to look for"],
  "questions_for_strategist": ["what recommendations to generate"],
  "ml_target": "column name if user asked for prediction, else null",
  "what_if_column": "column name for simulation, else null",
  "root_cause_target": "metric to explain drop/rise, else null",
  "knowledge_graph": true or false
}
```

**Implementation:**
- Call LLM with json_mode=True
- Parse response strictly
- Route results to all sub-agents in parallel via `asyncio.gather()`
- Aggregate all agent outputs into unified response
- Store query + response in FAISS memory

### 4.2 Data Cleaning Agent (`backend/agents/cleaning_agent.py`)

**Role:** Fully autonomous data cleaning with human-readable audit log.

**Must implement:**

**Missing value handling:**
- Numeric columns: fill with column median. Log: `"Revenue: 12.3% missing (847 rows) → filled with median (₹42,300)"`
- Categorical columns: fill with mode. Log: `"Region: 3.1% missing → filled with mode ('North')"`
- Datetime columns: forward-fill then backward-fill. Log: `"Date: 0.8% missing → forward-filled"`
- If missing > 40% of column: flag as "high missingness" and recommend dropping. Do NOT auto-drop.

**Duplicate detection:**
- Exact duplicates: `df.duplicated()` → drop and log count
- Near-duplicates on string columns: use fuzzy matching (fuzzywuzzy, threshold 95%) → flag but don't auto-remove, return to user for review

**Data type fixing:**
- Detect numeric strings like "1,234.56" or "$1,234" → strip symbols → cast to float64
- Detect date strings in formats: "DD-MM-YYYY", "MM/DD/YYYY", "YYYY-MM-DD", "01 Jan 2024", "Jan-24" → cast to datetime64
- Detect boolean strings "Yes/No", "True/False", "1/0", "Y/N" → cast to bool
- Detect ID columns (high cardinality strings, all unique) → flag as "identifier column, exclude from aggregations"

**Outlier detection (both methods, show both):**
- IQR method: Q1 - 1.5×IQR to Q3 + 1.5×IQR. Flag outside range.
- Z-score method: |z| > 3.0. Flag these rows.
- Report: `"Revenue: 7 outliers detected (IQR) — values: [1200000, 1350000, ...]"` 
- Do NOT remove outliers automatically. Return as flagged list for user to decide.
- Mark outlier rows with a boolean column `_is_outlier` in the DataFrame

**Output schema:**
```python
{
  "cleaning_log": [
    {"action": "fill_missing", "column": "Revenue", "method": "median", 
     "rows_affected": 847, "value_used": 42300, "pct_affected": 12.3},
    {"action": "remove_duplicates", "rows_removed": 23},
    {"action": "fix_dtype", "column": "Date", "from": "object", "to": "datetime64"},
    {"action": "outlier_flagged", "column": "Revenue", "count": 7, "method": "IQR"}
  ],
  "high_missingness_columns": ["Notes"],  # > 40% missing
  "near_duplicates": [...],               # for user review
  "outlier_rows": [list of row indices],
  "cleaned_df": DataFrame                 # in-memory, stored to SQLite
}
```

### 4.3 Analyst Agent (`backend/agents/analyst_agent.py`)

**Role:** Quantitative powerhouse. Runs all statistical analysis.

**Must implement:**

**KPI computation (for every numeric column identified by orchestrator):**
- Total, Mean, Median, Std Dev, Min, Max
- Period-over-period change: compare current period vs previous (auto-detect if time column present)
- % change with direction: `+18.3% MoM`, `-4.2% QoQ`
- Running average (7-day, 30-day if daily data)
- Growth rate (CAGR if multi-year data)

**Trend detection:**
- Linear regression slope per time-series column (positive/negative/flat)
- Mann-Kendall trend test for statistical significance
- Seasonal decomposition using statsmodels if ≥24 data points
- Moving average (7-period, 30-period)

**Anomaly detection:**
- Isolation Forest (scikit-learn) with contamination=0.05
- Statistical: values > 2 std deviations from rolling mean
- Contextual: compare value vs same period last year
- Return: list of anomaly points with timestamps and deviation magnitude

**Correlation analysis:**
- Pearson correlation matrix for all numeric columns
- Flag strong correlations (|r| > 0.7) with p-value
- Return top-5 significant correlations as insight bullets

**Distribution analysis:**
- Skewness and kurtosis per column
- Normality test (Shapiro-Wilk for n<5000, K-S test for larger)

**Output schema:**
```python
{
  "kpis": {
    "Revenue": {
      "total": 4230000, "mean": 42300, "median": 38900,
      "pct_change_mom": 18.3, "pct_change_qoq": -4.2,
      "trend": "upward", "trend_slope": 1234.5, "trend_significant": True
    }
  },
  "anomalies": [
    {"column": "Revenue", "row_index": 45, "date": "2024-10-15", 
     "value": 1200000, "expected_range": [20000, 80000], "severity": "high"}
  ],
  "correlations": [
    {"col_a": "ad_spend", "col_b": "revenue", "r": 0.81, "p_value": 0.003,
     "interpretation": "strong positive — ad spend strongly predicts revenue"}
  ],
  "seasonal_pattern": "quarterly peaks in Q4",
  "insights_raw": ["list of raw statistical findings"]
}
```

### 4.4 Critic Agent (`backend/agents/critic_agent.py`)

**Role:** Validates every insight from the Analyst Agent. Adds confidence scores. Prevents hallucinations.

**Must implement:**

For each insight from Analyst Agent:
1. Verify the statistical claim against raw data (re-compute independently)
2. Check sample size adequacy (n < 30 → low confidence flag)
3. Check for confounding variables (if correlation found, check if third variable explains it)
4. Assign confidence score (0-100%) based on: sample size, p-value, effect size, data quality
5. Add caveat if needed: `"Low confidence: only 12 data points in Q3"`

**LLM system prompt for critic:**
```
You are the Critic Agent. You receive raw statistical insights and must validate them.
For each insight, determine:
1. Is the statistical method appropriate for the data type?
2. Is the sample size sufficient (n >= 30 for parametric tests)?
3. Are there confounders that could explain this finding?
4. Assign a confidence percentage (0-100).
5. Rewrite the insight as a validated statement.

Return JSON: {"validated_insights": [...], "rejected_insights": [...], "caveats": [...]}
```

**Output:** Every insight gets `confidence_score` (int 0-100) and `validation_status` ("validated" | "uncertain" | "rejected").

### 4.5 Strategist Agent (`backend/agents/strategist_agent.py`)

**Role:** Translates validated insights into business recommendations and simulations.

**Must implement:**

**Recommendations:**
- Generate exactly 3 ranked business recommendations based on validated insights
- Each recommendation has: action, expected impact, timeline, risk level
- Format: `"Increase ad spend in Region A by 15% — expected +12% revenue in Q1 (high confidence)"`

**What-if simulation:**
- Receive: target column, change amount (e.g., marketing_budget +20%)
- Use trained ML model to predict outcome
- Generate: before/after comparison chart data
- Generate: sensitivity analysis (what % change needed to achieve 10% revenue increase)

**Root cause analysis (see also 4.9):**
- Identify causal chain for a metric change
- Use correlation data + time-lag analysis
- Output: step-by-step chain with confidence at each step

### 4.6 Scrape Agent (`backend/agents/scrape_agent.py`)

**Role:** Autonomous web scraping for external data enrichment.

**Must implement:**

```python
async def scrape_url(url: str, extract_tables: bool = True) -> dict:
    """
    1. Launch Playwright headless browser (chromium)
    2. Navigate to URL, wait for network idle
    3. Extract all <table> elements → convert to DataFrames
    4. Extract all structured lists (<ul>/<ol> with consistent structure)
    5. Extract JSON-LD structured data if present
    6. Try to extract main data content using readability heuristics
    7. Return list of DataFrames + metadata
    """
```

- Handle JavaScript-rendered pages (wait for page load, scroll to trigger lazy load)
- Handle pagination: detect "Next" button → scrape up to 10 pages max
- Handle rate limiting: random delay 1-3 seconds between requests
- Detect and handle CAPTCHAs: skip and report to user
- Clean scraped data: strip HTML tags from cell content, normalize whitespace
- Return column headers if detected in `<thead>`, otherwise auto-generate col names
- Store scraped data to SQLite exactly like uploaded files

**Multi-source merge:**
- After scraping + file upload both complete, call merge_datasets()
- Auto-detect join keys by column name similarity (e.g., "date" matches "Date", "DATE")
- Perform left join by default, report rows lost in join
- Allow user to override join type and key via UI

### 4.7 Chart Agent (`backend/agents/chart_agent.py`)

**Role:** Intelligently selects the best chart type for every column combination.

**Rules (implement ALL of these):**

```python
CHART_SELECTION_RULES = {
    "time_series_single": "line",           # datetime X + 1 numeric Y
    "time_series_multi": "area",             # datetime X + multiple numeric Y
    "category_single_metric": "bar",         # categorical X + 1 numeric Y
    "category_multi_metric": "grouped_bar",  # categorical X + multiple numeric Y
    "part_of_whole": "pie",                  # if total has clear parts summing to 100%
    "correlation": "scatter",                # 2 numeric columns
    "distribution": "histogram",             # 1 numeric column
    "heatmap": "heatmap",                    # correlation matrix or pivot table
    "geographic": "map",                     # if geo column detected (country/state/city)
    "hierarchical": "treemap",               # categorical hierarchy + size metric
    "cumulative": "waterfall",               # running total / bridge chart
    "sparkline": "sparkline",                # inline mini trend per table row
    "comparison_two_periods": "waterfall",   # current vs previous period
}
```

- Detect if column is geographic: check column name contains ("country", "state", "city", "region") OR values match known country/state names
- Detect if column is hierarchical: check if multiple categorical columns have parent-child relationship
- Allow user to override chart type via Edit Panel (all 11 chart types available)
- Generate complete Recharts/Chart.js config including: data mapping, axis labels, tooltips, colors, legend

### 4.8 Insight Agent (`backend/agents/insight_agent.py`)

**Role:** Converts statistical outputs into rich, specific, human-readable English narratives.

**Must implement:**

**Narrative generation via LLM:**
```
System: You are a business intelligence analyst writing executive-level insights.
Given validated statistics and anomalies, write:
1. An executive summary paragraph (3-5 sentences, plain English, no jargon)
2. 5 specific bullet point insights, each citing specific numbers
3. 2-3 "watch out" items (risks or anomalies to investigate)

CRITICAL: Every claim must cite a specific number from the data. Never generalize.
Bad: "Sales have been increasing"  
Good: "Sales grew 18.3% MoM in October 2024, driven by Region A (+32%) offsetting Region C (-4.2%)"
```

**Deep explainability output example:**
```
"Sales increased 18% in Q4 due to:
 — Region A: +32% (seasonal demand post-monsoon, correlation r=0.81 with rainfall index)
 — Product B: +27% (new campaign launched Oct 1, ad spend +40%)
 — Region C drag: -4.2% (competitor pricing -15%, identified via inverse correlation r=-0.73)
Confidence: 94% (validated by Critic Agent, n=847, p<0.001)"
```

### 4.9 Root Cause Analysis Agent (`backend/agents/root_cause_agent.py`)

**Role:** Automatically traces the causal chain behind metric movements.

**Must implement:**

```python
async def run_root_cause_analysis(
    metric: str,           # e.g., "Revenue"
    change_direction: str, # "drop" or "rise"
    dataset_id: str,
    time_period: str       # e.g., "Q3 2024"
) -> dict:
```

**Algorithm:**
1. Compute the metric's value in the specified period vs baseline (previous equivalent period)
2. Decompose by each categorical dimension (run `groupby` for each categorical column)
3. Identify which segment drove the most change (top contributor)
4. For the top contributor segment, check all correlated features (correlation matrix)
5. Check time-lag correlations (does variable X at t-1 predict metric at t?)
6. Build causality chain: `Revenue drop → Region X decline → competitor_price spike → market share loss`
7. Assign confidence to each link using: correlation strength + p-value + sample size
8. Build NetworkX graph for knowledge graph visualization

**LLM call for final explanation:**
```
Given this causal chain and data: [chain], write a 3-paragraph root cause analysis.
Paragraph 1: What happened and by how much.
Paragraph 2: Why it happened (causal chain with specific numbers).
Paragraph 3: What to do about it (2 specific actions).
```

**Output:**
```python
{
  "summary": "narrative text",
  "causal_chain": [
    {"cause": "competitor_price spike in Region X", "effect": "market share -8%", 
     "confidence": 87, "evidence": "r=-0.73, p=0.001, n=156"},
    {"cause": "market share -8%", "effect": "Revenue -23% in Region X", 
     "confidence": 94, "evidence": "r=0.91, p<0.001, n=156"}
  ],
  "knowledge_graph_nodes": [...],
  "knowledge_graph_edges": [...],
  "recommendations": ["action 1", "action 2"]
}
```

### 4.10 Auto ML Agent (`backend/agents/ml_agent.py`)

**Role:** Fully automated model selection, training, evaluation, and explanation.

**Must implement:**

```python
async def run_auto_ml(dataset_id: str, target_column: str, task_type: str = "auto") -> dict:
    """
    task_type: "auto" = detect from target column dtype
    If target is numeric → regression
    If target is categorical with <=20 unique → classification
    """
```

**Model selection (try all, return best):**

For regression:
- Linear Regression
- Ridge Regression  
- Random Forest Regressor
- Gradient Boosting Regressor
- XGBoost (if installable, else skip gracefully)

For classification:
- Logistic Regression
- Random Forest Classifier
- Gradient Boosting Classifier
- Decision Tree

**Pipeline:**
1. Auto feature engineering: encode categoricals (label encode for trees, one-hot for linear), scale numerics (StandardScaler for linear models), handle remaining nulls
2. Train/test split: 80/20, stratified for classification
3. Cross-validation: 5-fold CV, report mean ± std
4. Compare all models by: R² (regression) or Accuracy + F1 (classification)
5. Select best model
6. Compute SHAP values for feature importance (use `shap.TreeExplainer` for tree models, `shap.LinearExplainer` for linear)
7. Generate learning curve data
8. Save best model as pickle to filesystem, record path in DB

**Output:**
```python
{
  "best_model": "Random Forest Regressor",
  "metrics": {
    "r2": 0.847, "mae": 3241.5, "rmse": 5102.3,
    "cv_r2_mean": 0.831, "cv_r2_std": 0.042
  },
  "feature_importance": [
    {"feature": "ad_spend", "importance": 0.381, "shap_direction": "positive"},
    {"feature": "region", "importance": 0.274, "shap_direction": "positive"},
    {"feature": "season", "importance": 0.213, "shap_direction": "positive"}
  ],
  "predictions": [{"actual": 42000, "predicted": 39500, "date": "2024-01"}],
  "model_explanation": "Revenue is 38% explained by ad_spend, 27% by region, 21% by seasonal index",
  "model_id": "uuid"
}
```

**Prediction endpoint:** `POST /api/ml/{model_id}/predict` with new row data → returns predicted value + confidence interval.

### 4.11 Report Agent (`backend/agents/report_agent.py`)

**Role:** Generates a complete, professional business report in one click.

**Must implement two export formats:**

**PDF (via ReportLab):**
- Cover page: Report title, dataset name, date, generated by "Talking BI"
- Executive Summary section (from Insight Agent narrative)
- KPI Table (all KPIs with colored up/down arrows)
- Top 4 charts embedded as PNG (rendered from Matplotlib, not from browser)
- Insights section: 5 bullet points
- Recommendations section: 3 ranked recommendations with expected impact
- Root Cause Analysis section (if triggered)
- Appendix: Data cleaning log, model metrics (if ML was run)
- Page numbers, header/footer with logo placeholder

**PowerPoint (via python-pptx):**
- Slide 1: Title slide
- Slide 2: Executive summary text
- Slide 3: KPI dashboard (table with colored cells)
- Slides 4-7: One chart per slide with insight caption
- Slide 8: Root cause analysis (text + simple diagram)
- Slide 9: Recommendations (3 bullet points with action items)
- Use corporate blue/white theme

---

## 5. MEMORY SYSTEM

### 5.1 FAISS Vector Store (`backend/memory/faiss_store.py`)

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')  # runs locally, no API needed
index = faiss.IndexFlatL2(384)  # 384 = embedding dimension for MiniLM

async def store_query(query: str, response: dict, metadata: dict) -> str:
    """Encode query, add to FAISS index, return internal ID"""

async def retrieve_similar(query: str, top_k: int = 3) -> list[dict]:
    """Find top-k most similar past queries, return their responses as context"""
```

Memory is used to:
- Retrieve past queries when user says "compare with last month"
- Auto-suggest commands based on what similar users asked
- Build dataset memory: "last time you uploaded sales data, you focused on Regional KPIs"

### 5.2 User Preference Learning (`backend/memory/preference_store.py`)

**Track every user action:**
- Chart type change (bar → line): weight +1 to line chart preference
- Column selection for axis: record preferred X/Y patterns
- Filter additions: record common filter patterns
- Dashboard preset choice: record preferred layout

**Apply preferences:**
- Before generating dashboard, load top-10 preferences
- Bias chart selection: if user has changed to line chart 5 times, default to line
- Bias column selection: if user always puts "date" on X axis, default to that

---

## 6. DASHBOARD SYSTEM

### 6.1 Dashboard Presets

**Implement all 4 presets. Each is a JSON layout config for react-grid-layout.**

**Executive Preset:**
- Row 1: 4 KPI cards (full width)
- Row 2: Large line chart (60% width) + Donut chart (40% width)
- Row 3: Bar chart (full width)
- Show: Revenue, Growth %, Top KPIs only
- Hide: Raw data tables, complex charts

**Operational Preset:**
- Row 1: 4 KPI cards
- Row 2: Bar chart (50%) + Data table with sparklines (50%)
- Row 3: Scatter plot (50%) + Histogram (50%)
- Row 4: Heatmap (full width)
- Show: All columns, all chart types

**Trend Preset:**
- Row 1: Full-width area chart with zoom control
- Row 2: Moving average chart (50%) + Seasonal decomposition chart (50%)
- Row 3: Anomaly-highlighted line chart (full width)
- Row 4: Forecast line (extending 3 periods ahead using ML model)
- Show: Time-series focused, anomaly markers

**Comparison Preset:**
- Row 1: 2 KPI cards current period + 2 KPI cards previous period (with delta)
- Row 2: Side-by-side bar charts for current vs previous
- Row 3: Scatter plot with segment coloring (50%) + Waterfall chart (50%)
- Row 4: Heatmap segment comparison (full width)

### 6.2 Tile Edit Panel

Every chart tile has a gear icon that opens a slide-over panel with:
- Chart type selector (all 11 types as visual buttons)
- X-axis column selector (dropdown of all columns)
- Y-axis column selector (dropdown of numeric columns)
- Aggregation selector (sum, mean, count, median, max, min)
- Color picker / palette selector (5 preset palettes)
- Title editor (inline text input)
- Filter builder (add column = value conditions)
- Toggle: show data labels, show legend, show grid lines
- Delete tile button (with confirmation)
- Duplicate tile button

Every edit triggers:
1. Immediate chart re-render with new config
2. Config saved to dashboard JSON in SQLite
3. Preference event logged for self-learning

### 6.3 Drill-Down System

**Implement time drill-down:** Year → Quarter → Month → Week → Day

When user clicks a bar/point in a Year-level chart:
1. Push current state to drill-down stack
2. Re-query data with `WHERE year = clicked_year GROUP BY quarter`
3. Re-render chart with quarterly data
4. Show breadcrumb: `All Years > 2024 > Q3` with back buttons at each level

When user clicks a categorical bar:
1. Filter entire dashboard to show only that category
2. Show filter badge in FilterBar: `Region: North ×`

### 6.4 Dashboard Import/Export

**Export:** Serialize entire dashboard to JSON:
```json
{
  "Talking_bi_version": "1.0",
  "name": "Sales Dashboard Q4",
  "preset": "executive",
  "layout": [...],
  "tiles": [...],
  "filters": [...],
  "dataset_schema": {...}
}
```

**Import:** Accept this JSON → validate schema version → recreate all tiles → prompt user to link a dataset.

---

## 7. CONVERSATIONAL QUERY BAR

**Bottom-anchored command bar (always visible).**

**Must understand and execute these command types:**

| User types | System does |
|---|---|
| "show only last 6 months" | Applies date filter to all charts |
| "highlight best region" | Colors top-performing region amber, dims others |
| "remove outliers" | Filters out `_is_outlier = True` rows, re-renders |
| "switch to bar chart" | Changes currently focused tile to bar |
| "add Revenue to Y axis" | Updates focused tile's Y column |
| "compare with Q3" | Adds comparison period overlay to time charts |
| "predict next 3 months" | Triggers ML agent for forecasting |
| "why did sales drop in October?" | Triggers root cause analysis agent |
| "export as PDF" | Opens report generation |
| "show marketing view" | Switches role to marketing, filters dashboard |
| "what if marketing budget increases 20%?" | Triggers what-if simulation |

**Implementation:**
- Send query to `POST /api/query` endpoint
- Orchestrator parses intent → routes to appropriate action
- Action returns: dashboard_mutations (list of changes to apply) + narrative response
- Apply mutations to dashboard state immediately
- Show narrative response as a toast/notification above the bar

**Command suggestions:** Show 4 suggested commands based on FAISS retrieval of what similar queries were asked after similar actions.

---

## 8. FRONTEND — DETAILED DESIGN SPECIFICATION

### 8.1 Visual Design Language

**Aesthetic direction:** Industrial precision meets editorial clarity. Not corporate blue. Not purple gradients. Think high-end financial terminal crossed with editorial data journalism.

**Color system (implement as CSS variables):**
```css
:root {
  /* Core palette */
  --color-bg: #0A0B0E;           /* near-black background */
  --color-surface: #13151A;       /* card/panel surfaces */
  --color-surface-2: #1C1F27;     /* elevated surfaces */
  --color-border: rgba(255,255,255,0.07);
  --color-border-hover: rgba(255,255,255,0.15);
  
  /* Accent: sharp amber */
  --color-accent: #F5A623;
  --color-accent-dim: rgba(245,166,35,0.12);
  --color-accent-text: #FFC84A;
  
  /* Text hierarchy */
  --color-text-primary: #F0F1F3;
  --color-text-secondary: #8B8FA8;
  --color-text-tertiary: #4A4E63;
  
  /* Semantic */
  --color-success: #22C55E;
  --color-danger: #EF4444;
  --color-warning: #F59E0B;
  --color-info: #3B82F6;
  
  /* Chart palette (6 distinct, high contrast on dark bg) */
  --chart-1: #F5A623;  /* amber */
  --chart-2: #3B82F6;  /* blue */
  --chart-3: #22C55E;  /* green */
  --chart-4: #EC4899;  /* pink */
  --chart-5: #8B5CF6;  /* violet */
  --chart-6: #14B8A6;  /* teal */
  
  /* Layout */
  --sidebar-width: 240px;
  --topbar-height: 56px;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
}

/* Light mode override */
[data-theme="light"] {
  --color-bg: #F4F5F7;
  --color-surface: #FFFFFF;
  --color-surface-2: #F0F1F3;
  --color-border: rgba(0,0,0,0.08);
  --color-text-primary: #0A0B0E;
  --color-text-secondary: #5A5E73;
}
```

**Typography:**
```css
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,600&family=DM+Sans:opsz,wght@9..40,400;9..40,500&family=JetBrains+Mono:wght@400;500&display=swap');

body { font-family: 'DM Sans', sans-serif; }
h1, h2, h3, .heading { font-family: 'Bricolage Grotesque', sans-serif; }
code, .mono, .data-value { font-family: 'JetBrains Mono', monospace; }
```

### 8.2 Sidebar (`src/components/layout/Sidebar.tsx`)

```
┌─────────────────┐
│  ⬡ Talking BI     │  ← logo + wordmark
├─────────────────┤
│  Home           │
│  Datasets       │
│  Dashboards     │
│  ML Models      │
│  Reports        │
│  Memory         │
├─────────────────┤
│  RECENT         │
│  › Q4 Sales     │
│  › Churn Jan    │
│  › Marketing    │
├─────────────────┤
│  ○ Light/Dark   │
│  Role: Analyst  │  ← role selector dropdown
└─────────────────┘
```

- 240px wide, full height, dark surface (#13151A)
- Active item: amber left border + amber text
- Hover: subtle background highlight
- Collapsible to icon-only on mobile (64px)
- Framer Motion slide animation on collapse

### 8.3 Upload Page (`/upload`)

Full-screen upload experience:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│         ┌──────────────────────────────┐           │
│         │                              │           │
│         │   Drop files here            │           │
│         │   CSV · XLSX · JSON          │           │
│         │                              │           │
│         │   or click to browse         │           │
│         └──────────────────────────────┘           │
│                                                     │
│  ─────── OR ──────────────────────────────────     │
│                                                     │
│  Web URL  [https://...                ] [Scrape]    │
│                                                     │
│  API URL  [https://api...             ] [Connect]   │
│  Headers  [Key: Value                 ] [+ Add]     │
│                                                     │
│  Combine sources: [Dataset A] + [Dataset B]  [Join] │
│                                                     │
└─────────────────────────────────────────────────────┘
```

After upload → immediately show:
- File preview table (first 10 rows, scrollable)
- Auto-detected schema (column name, inferred type, sample values)
- "Looks right? Continue →" button

### 8.4 Cleaning Report UI (`src/components/cleaning/CleaningReport.tsx`)

Show cleaning results as a structured card report:

```
╔══════════════════════════════════════════════╗
║  Data Cleaning Report                         ║
║  847 changes made automatically               ║
╠══════════════════════════════════════════════╣
║  ✓  Revenue: 12.3% nulls → filled (median)  ║  ← green
║  ✓  Date: cast to datetime (01-Jan format)   ║  ← green
║  ✓  23 exact duplicates removed              ║  ← green
║  ⚠  Notes: 67% missing — consider dropping  ║  ← amber
║  ⚠  Revenue: 7 outliers flagged (IQR)        ║  ← amber
║     [View outliers] [Keep] [Remove all]      ║
╚══════════════════════════════════════════════╝
```

Outlier review: clicking "View outliers" opens a modal with the 7 outlier rows in a table, with a checkbox per row and "Remove selected" action.

### 8.5 Dashboard Canvas (`src/components/dashboard/DashboardCanvas.tsx`)

**Core component. Must implement:**

- react-grid-layout with: cols=12, rowHeight=80, draggable=true, resizable=true
- All tiles have: header bar (title + action icons), chart body, footer (data source label)
- Header action icons: edit (pencil), duplicate, fullscreen, delete
- Fullscreen: expand tile to modal overlay with full viewport chart
- Loading state: skeleton shimmer while chart data loads
- Error state: "Failed to load — retry" with error detail
- Empty state: "No data matches current filters" with filter reset link

**KPI Card design:**
```
┌─────────────────────────┐
│ Total Revenue            │
│                          │
│  ₹42.3M                  │  ← JetBrains Mono, 28px
│                          │
│  ▲ 18.3% vs last month   │  ← green arrow + text
│  ━━━━━━━━━━━━━░░░ 73%   │  ← mini sparkline
└─────────────────────────┘
```

### 8.6 Agent Status Bar (`src/components/shared/AgentStatusBar.tsx`)

Show real-time agent execution status during pipeline run:

```
Analyzing your data...
────────────────────────────────────────────────────
 ✓  Data Cleaning Agent      847 changes · 0.8s
 ✓  Orchestrator Agent       Plan generated · 1.2s
 ⟳  Analyst Agent            Running... (2.1s)
 ○  Critic Agent             Waiting
 ○  Strategist Agent         Waiting
 ○  Chart Agent              Waiting
────────────────────────────────────────────────────
```

- Animated spinning icon for "Running"
- Green checkmark for "Done" with timing
- Gray circle for "Waiting"
- All 11 agents shown in execution order
- Confidence score shown next to each agent's output when complete
- This component appears as a right-side drawer during processing, dismisses automatically on completion

### 8.7 Insight Panel (`src/components/insights/InsightPanel.tsx`)

Right sidebar (300px, collapsible):

```
╔══════════════════════════════════╗
║  AI Insights                     ║
╠══════════════════════════════════╣
║  Executive Summary               ║
║  Sales grew 18.3% MoM in Q4,    ║
║  driven by Region A (+32%)...    ║
╠══════════════════════════════════╣
║  Key Findings  (confidence 94%)  ║
║  • Revenue: +18.3% MoM (Oct)     ║
║  • Region A top performer +32%   ║
║  • Product B growing 27% YoY     ║
║  • Q3 dip: seasonal (-12%)       ║
║  • Churn: 4.2% — below baseline  ║
╠══════════════════════════════════╣
║  Watch Out                       ║
║  ⚠ Region C declining 4.2%      ║
║  ⚠ 7 outliers in October data   ║
╠══════════════════════════════════╣
║  Recommendations                 ║
║  1. Boost Region A spend 15%     ║
║     → +12% revenue projected     ║
║  2. Investigate Region C drop    ║
║  3. Replicate Product B campaign ║
╚══════════════════════════════════╝
```

### 8.8 ML Panel (`src/components/ml/MLPanel.tsx`)

Full-page modal when ML is triggered:

**Tab 1: Model Results**
- Model name + accuracy metrics in a summary card
- Actual vs Predicted scatter plot (Recharts)
- Learning curve chart

**Tab 2: Feature Importance**
- Horizontal bar chart (SHAP values, sorted descending)
- Color: positive SHAP = green bar, negative = red bar
- Explanation text below: "ad_spend is the strongest predictor of Revenue (+38%)"

**Tab 3: Predictions**
- Table of predicted values with confidence intervals
- Chart overlay: actual (solid line) + predicted (dashed) + forecast (lighter dashed)

**Tab 4: What-If Simulator**
```
Parameter to vary: [ad_spend ▼]
Current value: ₹500,000
Simulate change: [─────●──────────] +20%
New value: ₹600,000

Projected outcome:
Revenue: ₹42.3M → ₹47.8M  (+12.9%)
[Run simulation]

Sensitivity: A 10% revenue increase requires a 7.3% increase in ad_spend.
```

### 8.9 Knowledge Graph (`src/components/insights/KnowledgeGraph.tsx`)

**Use react-force-graph:**
- Nodes: Products, Regions, Customers, Time periods, KPIs
- Edges: colored by correlation strength (green = positive, red = negative)
- Edge thickness = correlation magnitude
- Node size = importance score from root cause analysis
- Click node → highlight connected edges → show correlation stats in side panel
- Zoom, pan, drag nodes

### 8.10 Conversational Bar (`src/components/conversation/ConversationBar.tsx`)

Fixed at bottom of dashboard view:

```
┌────────────────────────────────────────────────────────────────────┐
│ [⬡]  Ask anything or give a command...                    [Send ↑] │
└────────────────────────────────────────────────────────────────────┘
    Suggestions: "Show last 6 months" · "Why did sales drop?" · "Predict Q1"
```

- Full-width, 52px height
- Amber accent on focus ring
- JetBrains Mono font for typed input
- Suggestions update based on current dashboard state and FAISS memory
- Response appears as a toast notification AND narrows insight panel with result

---

## 9. API ENDPOINTS — COMPLETE LIST

### Upload & Datasets
- `POST /api/upload/file` — upload CSV/Excel/JSON file, return dataset_id
- `POST /api/upload/url` — trigger scrape agent for URL, return dataset_id  
- `POST /api/upload/api` — connect REST API, fetch data, return dataset_id
- `GET /api/datasets` — list all datasets
- `GET /api/datasets/{id}` — get dataset metadata + schema
- `GET /api/datasets/{id}/preview` — first 50 rows as JSON
- `DELETE /api/datasets/{id}` — delete dataset + associated data
- `POST /api/datasets/merge` — merge two datasets (body: {dataset_id_a, dataset_id_b, join_key, join_type})

### Cleaning
- `POST /api/datasets/{id}/clean` — run cleaning agent, return cleaning log
- `POST /api/datasets/{id}/remove-outliers` — remove flagged outlier rows
- `POST /api/datasets/{id}/drop-column` — drop a column

### Dashboard
- `POST /api/dashboards/generate` — generate dashboard from prompt + dataset_id
- `GET /api/dashboards` — list all dashboards
- `GET /api/dashboards/{id}` — get full dashboard config
- `PUT /api/dashboards/{id}` — update dashboard config (layout, tiles, filters)
- `DELETE /api/dashboards/{id}` — delete dashboard
- `POST /api/dashboards/import` — import dashboard JSON
- `GET /api/dashboards/{id}/export` — export dashboard as JSON

### Query / Agents
- `POST /api/query` — conversational query, runs orchestrator + routes agents
- `POST /api/agents/clean/{dataset_id}` — explicitly trigger cleaning agent
- `POST /api/agents/analyze/{dataset_id}` — trigger analyst agent
- `POST /api/agents/insights/{dataset_id}` — trigger insight narrative
- `POST /api/agents/root-cause` — trigger root cause analysis
- `GET /api/agents/status/{run_id}` — polling endpoint for agent run status

### ML
- `POST /api/ml/train` — body: {dataset_id, target_column} → trains AutoML
- `GET /api/ml/models` — list trained models
- `GET /api/ml/models/{id}` — model metadata + metrics + feature importance
- `POST /api/ml/models/{id}/predict` — predict on new data row
- `POST /api/ml/what-if` — run what-if simulation
- `POST /api/ml/forecast` — generate N-period forecast using best model

### Reports
- `POST /api/reports/generate` — generate full report, return report_id
- `GET /api/reports/{id}/pdf` — download PDF
- `GET /api/reports/{id}/pptx` — download PowerPoint

### Memory
- `GET /api/memory/queries` — list past queries for current session
- `GET /api/memory/similar?q={text}` — find similar past queries
- `GET /api/memory/preferences` — current user preference weights

---

## 10. ENVIRONMENT VARIABLES

```env
# backend/.env
GROQ_API_KEY=your_groq_api_key_here   # Get free at console.groq.com

# Storage paths
DATA_DIR=./data
MODELS_DIR=./models
FAISS_INDEX_PATH=./data/faiss.index
CHROMA_DB_PATH=./data/chroma
SQLITE_DB_PATH=./data/Talking.db
REPORTS_DIR=./data/reports

# App config
MAX_FILE_SIZE_MB=100
MAX_ROWS_ML=500000
CORS_ORIGINS=http://localhost:5173,https://your-vercel-app.vercel.app
```

---

## 11. REQUIREMENTS FILES

### `backend/requirements.txt`
```
fastapi==0.111.0
uvicorn==0.29.0
python-multipart==0.0.9
httpx==0.27.0
python-dotenv==1.0.1
tenacity==8.3.0
pandas==2.2.2
numpy==1.26.4
openpyxl==3.1.2
sqlalchemy==2.0.30
aiosqlite==0.20.0
playwright==1.44.0
beautifulsoup4==4.12.3
lxml==5.2.2
faiss-cpu==1.8.0
chromadb==0.5.0
sentence-transformers==3.0.1
scikit-learn==1.5.0
pycaret==3.3.0
shap==0.45.1
statsmodels==0.14.2
networkx==3.3
reportlab==4.2.0
python-pptx==0.6.23
matplotlib==3.9.0
scipy==1.13.1
fuzzywuzzy==0.18.0
python-Levenshtein==0.25.1
```

### `frontend/package.json` (dependencies section)
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "typescript": "^5.4.5",
    "axios": "^1.7.2",
    "zustand": "^4.5.2",
    "recharts": "^2.12.7",
    "chart.js": "^4.4.3",
    "react-chartjs-2": "^5.2.0",
    "react-grid-layout": "^1.4.4",
    "react-leaflet": "^4.2.1",
    "leaflet": "^1.9.4",
    "react-force-graph": "^1.44.4",
    "react-dropzone": "^14.2.3",
    "framer-motion": "^11.2.10",
    "lucide-react": "^0.394.0",
    "react-hot-toast": "^2.4.1",
    "html2canvas": "^1.4.1",
    "jspdf": "^2.5.1",
    "tailwindcss": "^3.4.4",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38"
  }
}
```

---

## 12. EDGE CASES — MUST HANDLE ALL

### Data Edge Cases
- Empty file uploaded → show friendly error "File appears to be empty. Please check and retry."
- File with only 1 row → skip statistical analysis, show raw data, flag: "Insufficient data for trend analysis (n=1)"
- File with 1000+ columns → auto-select top 20 by variance, show "showing top 20 columns — see all"
- All values in a column are identical → skip that column for correlation/trend analysis, flag it
- Mixed date formats in same column → attempt best-effort parse, flag ambiguous rows
- Negative values in "revenue" columns → flag as potentially erroneous, ask user to confirm
- Non-UTF-8 encoded files → attempt latin-1 decode, if fails show encoding selector
- Excel files with merged cells → flatten merges, note: "Merged cells detected and flattened"
- Excel files with multiple sheets → show sheet selector, allow multi-sheet import
- JSON nested objects → auto-flatten one level deep using pandas json_normalize
- Dataset with zero numeric columns → disable ML, what-if, KPI computation; show message
- Dataset with zero categorical columns → disable groupby charts; show message

### Agent Edge Cases
- Groq API rate limit hit → fall back to llama-3.1-8b-instant automatically, log fallback
- Groq API down entirely → fall back to rule-based insights (no LLM), flag "AI narrative unavailable"
- ML training fails (e.g., too few samples n<10) → return error card with explanation
- SHAP fails for certain model types → return feature importance from model.feature_importances_ instead
- FAISS index empty (first session) → skip memory retrieval, proceed without context
- Root cause analysis finds no strong correlations (all |r| < 0.3) → return "No clear causal driver found — data may require additional context"
- Web scraping blocked by CAPTCHA → return "Site requires verification — manual download needed"
- Web scraping returns no tables → attempt to extract structured lists and text → if nothing found, return "No structured data detected"
- Dataset merge: no common columns → show column mapping UI for manual join key selection
- What-if simulation: no ML model trained → auto-trigger ML training first, then run simulation

### Frontend Edge Cases
- Dashboard with 0 tiles → show empty state with "Ask a question to generate charts"
- Chart render fails → show error tile with "Chart unavailable — try editing chart settings"
- Drill-down returns empty data → show "No data for this selection" with back button
- Conversational query produces no action → show "I couldn't understand that command — try 'show last 6 months' or 'highlight top region'"
- File upload > 100MB → reject with size limit message before sending to server
- PDF export fails → show fallback: "Download as JSON instead"
- User switches role while dashboard is open → re-render with role filter applied, show banner "Dashboard filtered for CEO view"
- react-grid-layout on mobile → switch to single-column stacked layout below 768px breakpoint
- Knowledge graph with > 100 nodes → cluster nodes by type, show aggregate edges
- Long insight text → truncate to 3 lines with "Read more" expansion
- Theme toggle → persist to localStorage, apply immediately via data-theme attribute

---

## 13. SELF-LEARNING SYSTEM

### Preference Tracking Events (log ALL of these)

```python
PREFERENCE_EVENTS = {
    "chart_type_change": {"from_type": str, "to_type": str, "weight": 2},
    "axis_column_set": {"column": str, "axis": "x|y", "weight": 1},
    "preset_selected": {"preset": str, "weight": 3},
    "filter_added": {"column": str, "operator": str, "value": str, "weight": 1},
    "tile_deleted": {"chart_type": str, "weight": -1},  # negative = dispreference
    "drill_down_used": {"from_level": str, "to_level": str, "weight": 1},
    "insight_expanded": {"insight_type": str, "weight": 2},
    "ml_triggered": {"target_column": str, "weight": 2},
    "export_type": {"format": "pdf|pptx|json", "weight": 1},
    "role_selected": {"role": str, "weight": 3},
}
```

### Applying Preferences

Before generating next dashboard:
1. Load all preference events (last 30 sessions)
2. Compute weighted scores per preference dimension
3. Pass top-5 preferences to Orchestrator as context
4. Orchestrator biases chart_agent and layout_generator accordingly

Example: if user has changed 4 bar charts to line charts (weight 8 total) → next dashboard defaults to line charts for time-series data.

---

## 14. KNOWLEDGE GRAPH SPECIFICATION

**Nodes:**
- Product nodes (if "product" column exists)
- Region nodes (if "region/city/state/country" column exists)
- Customer segment nodes (if "segment/tier/type" column exists)
- Time period nodes (Year/Quarter)
- KPI nodes (Revenue, Churn, etc.)

**Edges (correlation-based):**
- Product → Region: edge weight = how strongly that product sells in that region
- Region → KPI: edge weight = Pearson r between region indicator and KPI
- Time → KPI: edge weight = regression slope

**Root cause edges (directional):**
- competitor_price → market_share → revenue (causal chain)
- Edge color: green = positive causation, red = negative causation

**Visualization in react-force-graph:**
- Node size = degree centrality (most connected = largest)
- Node color = node type (product=amber, region=blue, kpi=green, time=gray)
- Click interaction: click node → highlight 1-hop neighbors, show stats sidebar

---

## 15. DEPLOYMENT CONFIGURATION

### Backend (`render.yaml`)
```yaml
services:
  - type: web
    name: Talking-bi-backend
    env: python
    buildCommand: pip install -r requirements.txt && playwright install chromium
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false
    disk:
      name: data
      mountPath: /data
      sizeGB: 5
```

### Frontend (`vercel.json`)
```json
{
  "rewrites": [{"source": "/(.*)", "destination": "/index.html"}],
  "env": {"VITE_API_BASE_URL": "https://Talking-bi-backend.onrender.com"}
}
```

---

## 16. IMPLEMENTATION NOTES FOR KIRO

1. **Start with backend first:** Get FastAPI + SQLite + file upload working before touching frontend.

2. **Install Playwright browsers:** After `pip install playwright`, run `playwright install chromium`.

3. **FAISS note:** Install `faiss-cpu` not `faiss-gpu`. For Apple Silicon, use `pip install faiss-cpu --no-binary faiss-cpu`.

4. **PyCaret note:** PyCaret takes ~2 minutes to import on first run (it imports sklearn, xgboost, lightgbm). This is normal. Run `from pycaret.regression import *` in a startup warm-up to avoid cold start on first ML request.

5. **sentence-transformers note:** On first run, downloads the `all-MiniLM-L6-v2` model (~80MB). Cache it in `./models/` directory.

6. **React Grid Layout CSS:** Must import `react-grid-layout/css/styles.css` and `react-resizable/css/styles.css` in `index.css`.

7. **Recharts responsive:** Always wrap Recharts components in `<ResponsiveContainer width="100%" height={300}>`.

8. **Agent parallelism:** Use `asyncio.gather()` for Analyst + Critic + Chart agents running simultaneously. Strategist waits for Critic output. Total pipeline time target: < 15 seconds for datasets under 100k rows.

9. **Streaming for long operations:** Use FastAPI `StreamingResponse` for ML training and report generation to show progress to frontend.

10. **react-force-graph performance:** For knowledge graphs > 50 nodes, enable `nodeCanvasObject` for custom rendering and `cooldownTicks={100}` to prevent infinite simulation.

---

## 17. FEATURE CHECKLIST (verify all are implemented)

### Data Ingestion
- [ ] CSV upload
- [ ] Excel (.xlsx, .xls) upload  
- [ ] JSON upload
- [ ] Web scraping via URL
- [ ] REST API connector
- [ ] Multi-source merge with auto join-key detection
- [ ] Excel multi-sheet selector

### Data Cleaning Agent
- [ ] Missing value handling (median/mode/ffill per type)
- [ ] Duplicate removal (exact + near-duplicate detection)
- [ ] Data type fixing (dates, numbers, booleans)
- [ ] Outlier detection (IQR + z-score)
- [ ] Cleaning audit log with specific numbers
- [ ] High missingness column flagging
- [ ] User outlier review modal

### Multi-Agent System
- [ ] Orchestrator Agent
- [ ] Analyst Agent (KPIs + trends + anomalies + correlations)
- [ ] Critic Agent (validation + confidence scoring)
- [ ] Strategist Agent (recommendations + what-if)
- [ ] Scrape Agent (Playwright + BeautifulSoup)
- [ ] Chart Agent (smart chart type selection)
- [ ] Insight Agent (XAI narrative generation)
- [ ] ML Agent (AutoML + SHAP)
- [ ] Root Cause Analysis Agent
- [ ] Report Agent
- [ ] Agent status bar with live progress

### Dashboard System
- [ ] 4 preset layouts (Executive, Operational, Trend, Comparison)
- [ ] Drag-and-drop tiles (react-grid-layout)
- [ ] Resizable tiles
- [ ] Tile edit panel (all settings)
- [ ] Tile duplication
- [ ] Tile fullscreen
- [ ] Tile deletion
- [ ] All 11 chart types
- [ ] KPI cards with sparklines and trend arrows
- [ ] Drill-down (Year → Quarter → Month → Week → Day)
- [ ] Drill-down breadcrumb with back navigation
- [ ] Dashboard import (JSON)
- [ ] Dashboard export (JSON)
- [ ] Role-based dashboard adaptation (CEO/Analyst/Marketing)
- [ ] Global filter bar
- [ ] Date range filter

### ML Features
- [ ] AutoML model selection and training
- [ ] R², MAE, RMSE metrics display
- [ ] SHAP feature importance visualization
- [ ] Actual vs predicted chart
- [ ] Forecast (N-period ahead)
- [ ] What-if simulator with sliders
- [ ] Sensitivity analysis output

### Insights & Intelligence
- [ ] Executive summary narrative
- [ ] 5 specific bullet insights (each with numbers)
- [ ] Watch-out anomaly alerts
- [ ] Root cause analysis chain
- [ ] Knowledge graph visualization
- [ ] Confidence scores on all insights
- [ ] Cross-agent validated output

### Conversational Bar
- [ ] Natural language command parsing
- [ ] Date filter commands
- [ ] Chart type change commands
- [ ] Highlight commands
- [ ] Role switch commands
- [ ] ML trigger commands
- [ ] Root cause trigger commands
- [ ] Export commands
- [ ] Suggested commands (4 at all times)

### Memory System
- [ ] FAISS query memory
- [ ] ChromaDB storage
- [ ] Semantic retrieval for similar past queries
- [ ] User preference tracking (all 10 event types)
- [ ] Preference-biased dashboard generation
- [ ] Memory viewer panel

### Reports & Export
- [ ] AI-generated PDF report (all sections)
- [ ] PowerPoint report (all slides)
- [ ] Dashboard JSON export/import
- [ ] PNG export of individual charts (html2canvas)
- [ ] CSV export of filtered data

### Frontend Quality
- [ ] Dark mode (default) + Light mode toggle
- [ ] Bricolage Grotesque + DM Sans + JetBrains Mono fonts
- [ ] Framer Motion animations
- [ ] Responsive design (mobile single-column)
- [ ] Loading skeletons
- [ ] Error states for all components
- [ ] Empty states for all components
- [ ] react-hot-toast notifications
- [ ] Agent status drawer with live updates

---

*End of Kiro Prompt — Talking BI Full Implementation Specification v1.0*
*Every feature in this document must be implemented. No placeholders. No stubs. Production-ready code.*
and start to implement this project all the features in detailed and step by step manner 

nothing should be skipped

everyhting needs to implemented 

dont create much .md files 