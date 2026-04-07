# Talking BI - Developer Guide

**Version:** 1.0.0  
**Last Updated:** March 22, 2026

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Backend Development](#backend-development)
4. [Frontend Development](#frontend-development)
5. [Adding New Features](#adding-new-features)
6. [Testing](#testing)
7. [Code Style](#code-style)
8. [Contributing](#contributing)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │Components│  │  Hooks   │  │ Contexts │  │  Stores ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/REST
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ Routers  │  │ Services │  │  Agents  │  │ Database││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
                          │
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    External Services                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │   Groq   │  │  FAISS   │  │ChromaDB  │  │ SQLite  ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
```

### Multi-Agent System

```
┌──────────────┐
│ Orchestrator │ ◄─── User Query
└──────┬───────┘
       │
       ├──────► Cleaning Agent
       ├──────► Analyst Agent
       ├──────► Critic Agent
       ├──────► Chart Agent
       ├──────► Insight Agent
       ├──────► ML Agent
       ├──────► Strategist Agent
       ├──────► Root Cause Agent
       ├──────► Scrape Agent
       └──────► Report Agent
```

---

## Project Structure

### Backend Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── agents/               # AI agents
│   ├── orchestrator.py   # Master orchestrator
│   ├── cleaning_agent.py # Data cleaning
│   ├── analyst_agent.py  # Statistical analysis
│   ├── critic_agent.py   # Validation
│   ├── strategist_agent.py # Recommendations
│   ├── scrape_agent.py   # Web scraping
│   ├── chart_agent.py    # Chart selection
│   ├── insight_agent.py  # Insight generation
│   ├── ml_agent.py       # Machine learning
│   ├── root_cause_agent.py # Root cause analysis
│   └── report_agent.py   # Report generation
├── database/             # Database layer
│   ├── db.py            # Database setup
│   └── models.py        # ORM models
├── memory/              # Memory systems
│   ├── faiss_store.py   # FAISS vector store
│   ├── chroma_store.py  # ChromaDB store
│   └── preference_store.py # User preferences
├── routers/             # API endpoints
│   ├── upload.py        # File upload
│   ├── datasets.py      # Dataset CRUD
│   ├── dashboards.py    # Dashboard CRUD
│   ├── query.py         # Query processing
│   ├── ml.py            # ML endpoints
│   ├── drilldown.py     # Drill-down
│   ├── filters.py       # Filters
│   ├── memory.py        # Memory
│   └── export.py        # Export
├── services/            # Business logic
│   ├── ml_service.py    # ML operations
│   ├── what_if_service.py # Simulations
│   ├── knowledge_graph_service.py # Graphs
│   └── export_service.py # Export operations
└── utils/               # Utilities
    ├── llm.py          # LLM client
    ├── schema_detector.py # Type inference
    └── stats_utils.py  # Statistical helpers
```

### Frontend Structure

```
frontend/
├── src/
│   ├── main.tsx         # Entry point
│   ├── App.tsx          # Main app component
│   ├── components/      # React components
│   │   ├── dashboard/   # Dashboard components
│   │   ├── charts/      # Chart components
│   │   ├── ml/          # ML components
│   │   ├── insights/    # Insight components
│   │   ├── upload/      # Upload components
│   │   ├── shared/      # Shared components
│   │   └── conversation/ # Command components
│   ├── hooks/           # Custom hooks
│   │   ├── useDrillDown.ts
│   │   ├── useFilters.ts
│   │   ├── useMemory.ts
│   │   └── useOptimisticUpdate.ts
│   ├── contexts/        # React contexts
│   │   └── ThemeContext.tsx
│   ├── stores/          # State management
│   ├── api/             # API client
│   ├── types/           # TypeScript types
│   ├── utils/           # Utilities
│   └── styles/          # CSS files
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── vite.config.ts       # Vite config
└── tailwind.config.ts   # Tailwind config
```

---

## Backend Development

### Adding a New Agent

1. **Create Agent File**
   ```python
   # backend/agents/my_agent.py
   from utils.llm import call_llm
   import pandas as pd
   
   async def run_my_agent(df: pd.DataFrame, params: dict) -> dict:
       """
       My agent description.
       
       Args:
           df: Input DataFrame
           params: Agent parameters
           
       Returns:
           dict: Agent results
       """
       # Agent logic here
       result = await call_llm(
           messages=[{"role": "user", "content": "..."}],
           system="You are...",
           json_mode=True
       )
       
       return {
           "status": "success",
           "data": result
       }
   ```

2. **Register in Orchestrator**
   ```python
   # backend/agents/orchestrator.py
   from agents.my_agent import run_my_agent
   
   # Add to orchestrator logic
   if plan.get("use_my_agent"):
       my_result = await run_my_agent(df, params)
       results["my_agent"] = my_result
   ```

### Adding a New API Endpoint

1. **Create Router**
   ```python
   # backend/routers/my_router.py
   from fastapi import APIRouter, HTTPException, Depends
   from sqlalchemy.ext.asyncio import AsyncSession
   from database.db import get_db
   from pydantic import BaseModel
   
   router = APIRouter()
   
   class MyRequest(BaseModel):
       param1: str
       param2: int
   
   @router.post("/my-endpoint")
   async def my_endpoint(
       request: MyRequest,
       db: AsyncSession = Depends(get_db)
   ):
       """
       Endpoint description.
       """
       # Endpoint logic
       return {"result": "success"}
   ```

2. **Register Router**
   ```python
   # backend/main.py
   from routers import my_router
   
   app.include_router(
       my_router.router,
       prefix="/api/my-feature",
       tags=["My Feature"]
   )
   ```

### Adding a New Service

1. **Create Service**
   ```python
   # backend/services/my_service.py
   import pandas as pd
   
   class MyService:
       def __init__(self):
           pass
       
       async def process(self, data: pd.DataFrame) -> dict:
           """Process data."""
           # Service logic
           return {"processed": True}
   
   # Singleton instance
   my_service = MyService()
   ```

2. **Use in Router**
   ```python
   from services.my_service import my_service
   
   @router.post("/process")
   async def process_data(data: dict):
       result = await my_service.process(data)
       return result
   ```

### Database Models

1. **Add Model**
   ```python
   # backend/database/models.py
   from sqlalchemy import Column, String, Integer, DateTime
   from datetime import datetime
   import uuid
   
   class MyModel(Base):
       __tablename__ = "my_table"
       
       id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
       name = Column(String, nullable=False)
       value = Column(Integer)
       created_at = Column(DateTime, default=datetime.utcnow)
   ```

2. **Use Model**
   ```python
   from database.models import MyModel
   from sqlalchemy import select
   
   # Create
   item = MyModel(name="test", value=123)
   db.add(item)
   await db.commit()
   
   # Read
   result = await db.execute(select(MyModel).where(MyModel.id == item_id))
   item = result.scalar_one_or_none()
   
   # Update
   item.value = 456
   await db.commit()
   
   # Delete
   await db.delete(item)
   await db.commit()
   ```

---

## Frontend Development

### Adding a New Component

1. **Create Component**
   ```typescript
   // frontend/src/components/MyComponent.tsx
   import React, { useState } from 'react';
   
   interface MyComponentProps {
       title: string;
       onAction?: () => void;
   }
   
   export const MyComponent: React.FC<MyComponentProps> = ({
       title,
       onAction
   }) => {
       const [state, setState] = useState<string>('');
       
       return (
           <div className="p-4 bg-white rounded-lg">
               <h2 className="text-lg font-semibold">{title}</h2>
               {/* Component content */}
           </div>
       );
   };
   ```

2. **Export Component**
   ```typescript
   // frontend/src/components/index.ts
   export { MyComponent } from './MyComponent';
   ```

### Adding a New Hook

1. **Create Hook**
   ```typescript
   // frontend/src/hooks/useMyHook.ts
   import { useState, useCallback } from 'react';
   import axios from 'axios';
   
   export const useMyHook = (initialValue: string) => {
       const [value, setValue] = useState(initialValue);
       const [isLoading, setIsLoading] = useState(false);
       
       const fetchData = useCallback(async () => {
           setIsLoading(true);
           try {
               const response = await axios.get('/api/my-endpoint');
               setValue(response.data);
           } catch (error) {
               console.error('Error:', error);
           } finally {
               setIsLoading(false);
           }
       }, []);
       
       return { value, isLoading, fetchData };
   };
   ```

2. **Use Hook**
   ```typescript
   import { useMyHook } from './hooks/useMyHook';
   
   function MyComponent() {
       const { value, isLoading, fetchData } = useMyHook('initial');
       
       return (
           <div>
               {isLoading ? 'Loading...' : value}
               <button onClick={fetchData}>Fetch</button>
           </div>
       );
   }
   ```

### Adding a New Chart Type

1. **Create Chart Component**
   ```typescript
   // frontend/src/components/charts/MyChart.tsx
   import React from 'react';
   import { ResponsiveContainer, LineChart, Line } from 'recharts';
   
   interface MyChartProps {
       data: any[];
       xKey: string;
       yKey: string;
   }
   
   export const MyChart: React.FC<MyChartProps> = ({
       data,
       xKey,
       yKey
   }) => {
       return (
           <ResponsiveContainer width="100%" height={300}>
               <LineChart data={data}>
                   <Line dataKey={yKey} stroke="#3b82f6" />
               </LineChart>
           </ResponsiveContainer>
       );
   };
   ```

2. **Register Chart Type**
   ```typescript
   // In chart selection logic
   const CHART_TYPES = {
       'my-chart': MyChart,
       // ... other charts
   };
   ```

---

## Adding New Features

### Feature Development Workflow

1. **Plan Feature**
   - Define requirements
   - Design API endpoints
   - Design UI components
   - Identify dependencies

2. **Backend Implementation**
   - Create agent (if needed)
   - Create service (if needed)
   - Create router
   - Add database models
   - Write tests

3. **Frontend Implementation**
   - Create components
   - Create hooks
   - Add to integrated dashboard
   - Style with Tailwind
   - Write tests

4. **Integration**
   - Connect frontend to backend
   - Test end-to-end
   - Add error handling
   - Add loading states

5. **Documentation**
   - Update API docs
   - Update user guide
   - Add code comments
   - Update README

### Example: Adding a New Analysis Type

**Backend:**
```python
# 1. Create agent
# backend/agents/trend_agent.py
async def analyze_trends(df, columns):
    # Trend analysis logic
    return {"trends": [...]}

# 2. Create endpoint
# backend/routers/analysis.py
@router.post("/trends")
async def get_trends(dataset_id: str):
    # Load data, run agent, return results
    pass

# 3. Register router
# backend/main.py
app.include_router(analysis.router, prefix="/api/analysis")
```

**Frontend:**
```typescript
// 1. Create hook
// frontend/src/hooks/useTrends.ts
export const useTrends = (datasetId: string) => {
    // Hook logic
};

// 2. Create component
// frontend/src/components/analysis/TrendAnalysis.tsx
export const TrendAnalysis = ({ datasetId }) => {
    const { trends, isLoading } = useTrends(datasetId);
    // Component logic
};

// 3. Add to dashboard
// frontend/src/components/dashboard/IntegratedDashboard.tsx
<TrendAnalysis datasetId={datasetId} />
```

---

## Testing

### Backend Testing

**Unit Tests:**
```python
# tests/test_agents.py
import pytest
from agents.analyst_agent import run_analysis

@pytest.mark.asyncio
async def test_analyst_agent():
    df = pd.DataFrame({'revenue': [100, 200, 300]})
    result = await run_analysis(df, ['revenue'], None)
    
    assert 'kpis' in result
    assert 'revenue' in result['kpis']
    assert result['kpis']['revenue']['total'] == 600
```

**API Tests:**
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

### Frontend Testing

**Component Tests:**
```typescript
// tests/MyComponent.test.tsx
import { render, screen } from '@testing-library/react';
import { MyComponent } from './MyComponent';

test('renders component', () => {
    render(<MyComponent title="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
});
```

**Hook Tests:**
```typescript
// tests/useMyHook.test.ts
import { renderHook, act } from '@testing-library/react-hooks';
import { useMyHook } from './useMyHook';

test('hook works', async () => {
    const { result } = renderHook(() => useMyHook('initial'));
    
    expect(result.current.value).toBe('initial');
    
    await act(async () => {
        await result.current.fetchData();
    });
    
    expect(result.current.value).toBeDefined();
});
```

---

## Code Style

### Python Style (Backend)

**Follow PEP 8:**
```python
# Good
async def process_data(df: pd.DataFrame, columns: List[str]) -> dict:
    """
    Process data and return results.
    
    Args:
        df: Input DataFrame
        columns: Columns to process
        
    Returns:
        dict: Processing results
    """
    result = {}
    for col in columns:
        result[col] = df[col].sum()
    return result

# Bad
def processData(df,columns):
    result={}
    for col in columns:result[col]=df[col].sum()
    return result
```

**Type Hints:**
```python
from typing import List, Dict, Optional

async def my_function(
    param1: str,
    param2: int,
    param3: Optional[List[str]] = None
) -> Dict[str, any]:
    pass
```

### TypeScript Style (Frontend)

**Use TypeScript:**
```typescript
// Good
interface User {
    id: string;
    name: string;
    email: string;
}

const getUser = async (id: string): Promise<User> => {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
};

// Bad
const getUser = async (id) => {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
};
```

**Component Props:**
```typescript
interface MyComponentProps {
    title: string;
    count?: number;
    onAction: () => void;
}

export const MyComponent: React.FC<MyComponentProps> = ({
    title,
    count = 0,
    onAction
}) => {
    // Component logic
};
```

---

## Contributing

### Git Workflow

1. **Create Branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Changes**
   ```bash
   # Edit files
   git add .
   git commit -m "Add my feature"
   ```

3. **Push Branch**
   ```bash
   git push origin feature/my-feature
   ```

4. **Create Pull Request**
   - Go to GitHub
   - Create PR from your branch
   - Add description
   - Request review

### Commit Messages

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(ml): add forecasting endpoint

Add new endpoint for time-series forecasting with confidence intervals.

Closes #123
```

```
fix(dashboard): resolve chart rendering issue

Fix bug where charts wouldn't render after filter changes.
```

---

**Version:** 1.0.0  
**Last Updated:** March 22, 2026  
**Platform:** Talking BI - Agentic AI Business Intelligence

