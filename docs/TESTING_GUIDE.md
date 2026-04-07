# Talking BI - Testing Guide

**Version:** 1.0.0  
**Last Updated:** March 22, 2026

---

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [Integration Testing](#integration-testing)
5. [E2E Testing](#e2e-testing)
6. [Performance Testing](#performance-testing)
7. [Security Testing](#security-testing)
8. [CI/CD Integration](#cicd-integration)

---

## Testing Strategy

### Testing Pyramid

```
        /\
       /  \      E2E Tests (10%)
      /____\     
     /      \    Integration Tests (30%)
    /________\   
   /          \  Unit Tests (60%)
  /__________  \
```

### Coverage Goals

- **Unit Tests**: 80% code coverage
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user flows
- **Performance Tests**: Key operations
- **Security Tests**: All endpoints

---

## Backend Testing

### Setup

Install testing dependencies:
```bash
cd backend
pip install pytest pytest-asyncio pytest-cov httpx
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agents.py

# Run specific test
pytest tests/test_agents.py::test_orchestrator_agent

# Run with verbose output
pytest -v

# Run with print statements
pytest -s
```

### Test Structure

```
backend/tests/
├── conftest.py              # Fixtures
├── test_agents/
│   ├── test_orchestrator.py
│   ├── test_cleaning_agent.py
│   ├── test_analyst_agent.py
│   ├── test_critic_agent.py
│   ├── test_strategist_agent.py
│   ├── test_scrape_agent.py
│   ├── test_chart_agent.py
│   ├── test_insight_agent.py
│   ├── test_ml_agent.py
│   ├── test_root_cause_agent.py
│   └── test_report_agent.py
├── test_routers/
│   ├── test_upload.py
│   ├── test_datasets.py
│   ├── test_dashboards.py
│   ├── test_query.py
│   ├── test_ml.py
│   ├── test_drilldown.py
│   ├── test_filters.py
│   ├── test_memory.py
│   └── test_export.py
├── test_services/
│   ├── test_ml_service.py
│   ├── test_what_if_service.py
│   ├── test_knowledge_graph_service.py
│   └── test_export_service.py
└── test_utils/
    ├── test_llm.py
    ├── test_schema_detector.py
    └── test_stats_utils.py
```

### Example Unit Test

```python
# tests/test_agents/test_cleaning_agent.py
import pytest
import pandas as pd
from agents.cleaning_agent import CleaningAgent

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'revenue': [100, 200, None, 400, 500],
        'region': ['North', 'South', None, 'East', 'West'],
        'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
    })

@pytest.mark.asyncio
async def test_fill_missing_values(sample_data):
    agent = CleaningAgent()
    result = await agent.clean(sample_data)
    
    # Check no missing values remain
    assert result['cleaned_df'].isnull().sum().sum() == 0
    
    # Check cleaning log
    assert len(result['cleaning_log']) > 0
    assert any(log['action'] == 'fill_missing' for log in result['cleaning_log'])

@pytest.mark.asyncio
async def test_outlier_detection(sample_data):
    # Add outlier
    sample_data.loc[5] = [10000, 'North', '2024-01-06']
    
    agent = CleaningAgent()
    result = await agent.clean(sample_data)
    
    # Check outliers detected
    assert len(result['outlier_rows']) > 0
    assert 5 in result['outlier_rows']
```

### Example API Test

```python
# tests/test_routers/test_upload.py
import pytest
from fastapi.testclient import TestClient
from main import app
from io import BytesIO

client = TestClient(app)

def test_upload_csv():
    # Create test CSV
    csv_content = b"name,value\ntest1,100\ntest2,200"
    files = {"file": ("test.csv", BytesIO(csv_content), "text/csv")}
    
    response = client.post("/api/upload/file", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "dataset_id" in data
    assert data["row_count"] == 2
    assert data["column_count"] == 2

def test_upload_invalid_file():
    files = {"file": ("test.txt", BytesIO(b"invalid"), "text/plain")}
    
    response = client.post("/api/upload/file", files=files)
    
    assert response.status_code == 400
```

### Mocking LLM Calls

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_llm():
    with patch('utils.llm.call_llm') as mock:
        mock.return_value = '{"intent": "test", "kpis": []}'
        yield mock

# Usage in test
@pytest.mark.asyncio
async def test_orchestrator_with_mock(mock_llm):
    from agents.orchestrator import Orchestrator
    
    orchestrator = Orchestrator()
    result = await orchestrator.plan({}, [], "test query", "analyst")
    
    assert mock_llm.called
    assert "intent" in result
```

---

## Frontend Testing

### Setup

Install testing dependencies:
```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest jsdom
```

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm test -- MLPanel.test.tsx
```

### Test Structure

```
frontend/src/
├── components/
│   ├── __tests__/
│   │   ├── MLPanel.test.tsx
│   │   ├── FeatureImportance.test.tsx
│   │   ├── WhatIfSimulator.test.tsx
│   │   └── ...
├── hooks/
│   ├── __tests__/
│   │   ├── useDrillDown.test.ts
│   │   ├── useFilters.test.ts
│   │   └── useMemory.test.ts
├── stores/
│   ├── __tests__/
│   │   ├── datasetStore.test.ts
│   │   ├── dashboardStore.test.ts
│   │   └── agentStore.test.ts
└── utils/
    ├── __tests__/
    │   ├── chartHelpers.test.ts
    │   └── formatters.test.ts
```

### Example Component Test

```typescript
// src/components/__tests__/MLPanel.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MLPanel } from '../ml/MLPanel';
import { vi } from 'vitest';

describe('MLPanel', () => {
  it('renders ML panel with model info', () => {
    const mockModel = {
      id: 'model1',
      algorithm: 'RandomForest',
      r2_score: 0.85,
      feature_importance: { price: 0.5, quantity: 0.3 }
    };
    
    render(<MLPanel model={mockModel} />);
    
    expect(screen.getByText('RandomForest')).toBeInTheDocument();
    expect(screen.getByText('0.85')).toBeInTheDocument();
  });
  
  it('handles train button click', async () => {
    const onTrain = vi.fn();
    render(<MLPanel onTrain={onTrain} />);
    
    const trainButton = screen.getByRole('button', { name: /train/i });
    await userEvent.click(trainButton);
    
    expect(onTrain).toHaveBeenCalled();
  });
});
```

### Example Hook Test

```typescript
// src/hooks/__tests__/useDrillDown.test.ts
import { renderHook, act } from '@testing-library/react';
import { useDrillDown } from '../useDrillDown';

describe('useDrillDown', () => {
  it('initializes with empty path', () => {
    const { result } = renderHook(() => useDrillDown('dataset1'));
    
    expect(result.current.path).toEqual([]);
    expect(result.current.currentLevel).toBeNull();
  });
  
  it('drills down correctly', async () => {
    const { result } = renderHook(() => useDrillDown('dataset1'));
    
    await act(async () => {
      await result.current.drillDown('region', 'North');
    });
    
    expect(result.current.path).toHaveLength(1);
    expect(result.current.path[0]).toEqual({ column: 'region', value: 'North' });
  });
  
  it('drills up correctly', () => {
    const { result } = renderHook(() => useDrillDown('dataset1'));
    
    act(() => {
      result.current.drillDown('region', 'North');
      result.current.drillDown('city', 'Boston');
      result.current.drillUp();
    });
    
    expect(result.current.path).toHaveLength(1);
  });
});
```

### Mocking API Calls

```typescript
// src/api/__mocks__/client.ts
import { vi } from 'vitest';

export const api = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn()
};

// Usage in test
import { api } from '../api/client';

vi.mock('../api/client');

test('fetches data', async () => {
  api.get.mockResolvedValue({ data: { datasets: [] } });
  
  // Test component that uses api.get
  // ...
  
  expect(api.get).toHaveBeenCalledWith('/datasets');
});
```

---

## Integration Testing

### Backend Integration Tests

Test complete API flows:

```python
# tests/integration/test_dashboard_flow.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_complete_dashboard_flow():
    # 1. Upload dataset
    csv_content = b"date,revenue\n2024-01-01,1000\n2024-01-02,2000"
    files = {"file": ("test.csv", BytesIO(csv_content), "text/csv")}
    upload_response = client.post("/api/upload/file", files=files)
    assert upload_response.status_code == 200
    dataset_id = upload_response.json()["dataset_id"]
    
    # 2. Generate dashboard
    dashboard_response = client.post("/api/dashboards/generate", json={
        "name": "Test Dashboard",
        "dataset_id": dataset_id,
        "preset": "executive"
    })
    assert dashboard_response.status_code == 200
    dashboard_id = dashboard_response.json()["id"]
    
    # 3. Get dashboard
    get_response = client.get(f"/api/dashboards/{dashboard_id}")
    assert get_response.status_code == 200
    dashboard = get_response.json()
    assert len(dashboard["tiles"]) > 0
    
    # 4. Apply filter
    filter_response = client.post("/api/filters/apply", json={
        "dataset_id": dataset_id,
        "filters": [{
            "column": "revenue",
            "operator": "greater_than",
            "value": 1500
        }]
    })
    assert filter_response.status_code == 200
    assert filter_response.json()["filtered_count"] == 1
```

### Frontend Integration Tests

Test component interactions:

```typescript
// src/__tests__/integration/DashboardFlow.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '../App';

describe('Dashboard Flow', () => {
  it('completes full dashboard creation flow', async () => {
    render(<App />);
    
    // 1. Upload file
    const fileInput = screen.getByLabelText(/upload/i);
    const file = new File(['date,revenue\n2024-01-01,1000'], 'test.csv', { type: 'text/csv' });
    await userEvent.upload(fileInput, file);
    
    // 2. Wait for upload
    await waitFor(() => {
      expect(screen.getByText(/upload successful/i)).toBeInTheDocument();
    });
    
    // 3. Generate dashboard
    const generateButton = screen.getByRole('button', { name: /generate dashboard/i });
    await userEvent.click(generateButton);
    
    // 4. Select preset
    const executiveButton = screen.getByRole('button', { name: /executive/i });
    await userEvent.click(executiveButton);
    
    // 5. Verify dashboard created
    await waitFor(() => {
      expect(screen.getByText(/dashboard created/i)).toBeInTheDocument();
    });
  });
});
```

---

## E2E Testing

### Setup Playwright

```bash
cd frontend
npm install --save-dev @playwright/test
npx playwright install
```

### E2E Test Structure

```
frontend/e2e/
├── upload.spec.ts
├── dashboard.spec.ts
├── query.spec.ts
├── ml.spec.ts
└── export.spec.ts
```

### Example E2E Test

```typescript
// e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Dashboard Creation', () => {
  test('creates dashboard from CSV upload', async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:5173');
    
    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test-data/sample.csv');
    
    // Wait for upload
    await expect(page.locator('text=Upload successful')).toBeVisible();
    
    // Generate dashboard
    await page.click('button:has-text("Generate Dashboard")');
    
    // Select preset
    await page.click('button:has-text("Executive")');
    
    // Verify dashboard
    await expect(page.locator('.dashboard-canvas')).toBeVisible();
    await expect(page.locator('.chart-tile')).toHaveCount(8);
    
    // Verify KPI cards
    await expect(page.locator('.kpi-card')).toHaveCount(4);
  });
  
  test('applies filters to dashboard', async ({ page }) => {
    await page.goto('http://localhost:5173/dashboard/test-id');
    
    // Open filter bar
    await page.click('button:has-text("Add Filter")');
    
    // Select column
    await page.selectOption('select[name="column"]', 'revenue');
    
    // Select operator
    await page.selectOption('select[name="operator"]', 'greater_than');
    
    // Enter value
    await page.fill('input[name="value"]', '1000');
    
    // Apply filter
    await page.click('button:has-text("Apply")');
    
    // Verify filter applied
    await expect(page.locator('.filter-badge')).toContainText('revenue > 1000');
  });
});
```

### Running E2E Tests

```bash
# Run all E2E tests
npx playwright test

# Run specific test
npx playwright test dashboard.spec.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Run in debug mode
npx playwright test --debug

# Generate report
npx playwright show-report
```

---

## Performance Testing

### Backend Performance Tests

```python
# tests/performance/test_performance.py
import pytest
import time
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_dashboard_generation_performance():
    # Upload large dataset
    csv_content = generate_large_csv(10000)  # 10k rows
    files = {"file": ("large.csv", BytesIO(csv_content), "text/csv")}
    
    start = time.time()
    upload_response = client.post("/api/upload/file", files=files)
    upload_time = time.time() - start
    
    assert upload_time < 10.0  # Should complete in < 10 seconds
    
    dataset_id = upload_response.json()["dataset_id"]
    
    # Generate dashboard
    start = time.time()
    dashboard_response = client.post("/api/dashboards/generate", json={
        "name": "Performance Test",
        "dataset_id": dataset_id,
        "preset": "operational"
    })
    generation_time = time.time() - start
    
    assert generation_time < 5.0  # Should complete in < 5 seconds
    assert dashboard_response.status_code == 200

def test_query_response_time():
    start = time.time()
    response = client.post("/api/query", json={
        "dataset_id": "test-id",
        "query": "Show revenue trends"
    })
    query_time = time.time() - start
    
    assert query_time < 3.0  # Should respond in < 3 seconds
```

### Frontend Performance Tests

```typescript
// src/__tests__/performance/ChartRendering.test.tsx
import { render } from '@testing-library/react';
import { performance } from 'perf_hooks';
import { DashboardCanvas } from '../components/dashboard/DashboardCanvas';

describe('Chart Rendering Performance', () => {
  it('renders 20 charts in under 2 seconds', () => {
    const tiles = Array.from({ length: 20 }, (_, i) => ({
      id: `tile-${i}`,
      type: 'bar',
      config: { /* ... */ }
    }));
    
    const start = performance.now();
    render(<DashboardCanvas tiles={tiles} />);
    const end = performance.now();
    
    const renderTime = end - start;
    expect(renderTime).toBeLessThan(2000);
  });
});
```

---

## Security Testing

### Authentication Tests

```python
# tests/security/test_auth.py
def test_unauthorized_access():
    response = client.get("/api/datasets")
    # Should require auth in production
    assert response.status_code in [200, 401]

def test_sql_injection():
    response = client.post("/api/query", json={
        "dataset_id": "test'; DROP TABLE datasets; --",
        "query": "test"
    })
    # Should not execute SQL injection
    assert response.status_code in [400, 404]
```

### XSS Tests

```typescript
// src/__tests__/security/XSS.test.tsx
test('prevents XSS in user input', () => {
  const maliciousInput = '<script>alert("XSS")</script>';
  render(<ConversationBar />);
  
  const input = screen.getByRole('textbox');
  userEvent.type(input, maliciousInput);
  
  // Should escape HTML
  expect(screen.queryByText(/<script>/)).not.toBeInTheDocument();
});
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/coverage-final.json
  
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install Playwright
        run: |
          cd frontend
          npm install
          npx playwright install --with-deps
      - name: Run E2E tests
        run: |
          cd frontend
          npx playwright test
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

---

## Best Practices

### General

1. **Write tests first** (TDD when possible)
2. **Keep tests isolated** (no dependencies between tests)
3. **Use descriptive names** (test_should_return_error_when_invalid_input)
4. **Test edge cases** (empty data, null values, large datasets)
5. **Mock external dependencies** (LLM calls, file system, network)

### Backend

1. **Use fixtures** for common test data
2. **Test async functions** with pytest-asyncio
3. **Mock database** for unit tests
4. **Test error handling** explicitly
5. **Verify logging** output

### Frontend

1. **Test user interactions** not implementation
2. **Use semantic queries** (getByRole, getByLabelText)
3. **Wait for async updates** (waitFor, findBy)
4. **Test accessibility** (screen reader compatibility)
5. **Snapshot tests** for UI components

---

## Troubleshooting

### Common Issues

**Tests fail with "Module not found"**
- Check imports and paths
- Ensure dependencies installed
- Verify test configuration

**Async tests timeout**
- Increase timeout in pytest.ini or vitest.config.ts
- Check for unresolved promises
- Mock slow operations

**E2E tests flaky**
- Add explicit waits
- Use stable selectors
- Increase timeouts
- Check for race conditions

**Coverage not accurate**
- Ensure all files included
- Check coverage configuration
- Verify test execution

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Library](https://testing-library.com/)
- [Playwright Documentation](https://playwright.dev/)
- [Vitest Documentation](https://vitest.dev/)

---

**Version:** 1.0.0  
**Last Updated:** March 22, 2026  
**Platform:** Talking BI - Agentic AI Business Intelligence
