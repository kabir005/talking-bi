# Talking BI - API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000/api`  
**Last Updated:** March 22, 2026

---

## Table of Contents

1. [Authentication](#authentication)
2. [Upload Endpoints](#upload-endpoints)
3. [Dataset Endpoints](#dataset-endpoints)
4. [Dashboard Endpoints](#dashboard-endpoints)
5. [Query Endpoints](#query-endpoints)
6. [ML Endpoints](#ml-endpoints)
7. [Drill-Down Endpoints](#drill-down-endpoints)
8. [Filter Endpoints](#filter-endpoints)
9. [Memory Endpoints](#memory-endpoints)
10. [Export Endpoints](#export-endpoints)
11. [Error Handling](#error-handling)

---

## Authentication

Currently, the API does not require authentication. For production deployment, implement JWT or API key authentication.

---

## Upload Endpoints

### Upload File

Upload a data file (CSV, Excel, JSON).

**Endpoint:** `POST /upload/file`

**Request:**
```http
POST /api/upload/file
Content-Type: multipart/form-data

file: <binary>
```

**Response:**
```json
{
  "dataset_id": "abc123",
  "name": "sales_data.csv",
  "row_count": 1000,
  "column_count": 10,
  "schema": {
    "date": "datetime",
    "revenue": "float64",
    "region": "object"
  },
  "cleaning_log": [
    {
      "action": "fill_missing",
      "column": "revenue",
      "rows_affected": 50
    }
  ]
}
```

---

## Dataset Endpoints

### List Datasets

Get all datasets.

**Endpoint:** `GET /datasets`

**Response:**
```json
{
  "datasets": [
    {
      "id": "abc123",
      "name": "sales_data.csv",
      "row_count": 1000,
      "column_count": 10,
      "created_at": "2024-03-22T10:00:00Z"
    }
  ]
}
```

### Get Dataset

Get dataset details.

**Endpoint:** `GET /datasets/{dataset_id}`

**Response:**
```json
{
  "id": "abc123",
  "name": "sales_data.csv",
  "row_count": 1000,
  "column_count": 10,
  "schema_json": {...},
  "sample_json": [...],
  "cleaning_log": [...]
}
```

### Delete Dataset

Delete a dataset.

**Endpoint:** `DELETE /datasets/{dataset_id}`

**Response:**
```json
{
  "message": "Dataset deleted successfully"
}
```

---

## Dashboard Endpoints

### Generate Dashboard

Create a dashboard from a dataset.

**Endpoint:** `POST /dashboards/generate`

**Request:**
```json
{
  "name": "Sales Dashboard",
  "dataset_id": "abc123",
  "preset": "executive",
  "role": "ceo"
}
```

**Response:**
```json
{
  "id": "dash123",
  "name": "Sales Dashboard",
  "preset": "executive",
  "tiles": [...],
  "layout": [...],
  "tile_count": 8
}
```

### List Dashboards

Get all dashboards.

**Endpoint:** `GET /dashboards`

**Response:**
```json
[
  {
    "id": "dash123",
    "name": "Sales Dashboard",
    "dataset_id": "abc123",
    "preset": "executive",
    "created_at": "2024-03-22T10:00:00Z",
    "tile_count": 8
  }
]
```

### Get Dashboard

Get dashboard with data.

**Endpoint:** `GET /dashboards/{dashboard_id}`

**Response:**
```json
{
  "id": "dash123",
  "name": "Sales Dashboard",
  "preset": "executive",
  "tiles": [
    {
      "id": "tile1",
      "type": "kpi",
      "title": "Total Revenue",
      "config": {
        "value": 1000000,
        "change": 15.3,
        "trend": "up"
      }
    }
  ],
  "layout": [...],
  "filters": {}
}
```

### Update Dashboard

Update dashboard configuration.

**Endpoint:** `PUT /dashboards/{dashboard_id}`

**Request:**
```json
{
  "name": "Updated Dashboard",
  "layout_json": [...],
  "tiles_json": [...],
  "filters_json": {...}
}
```

**Response:**
```json
{
  "message": "Dashboard updated successfully"
}
```

### Delete Dashboard

Delete a dashboard.

**Endpoint:** `DELETE /dashboards/{dashboard_id}`

**Response:**
```json
{
  "message": "Dashboard deleted successfully"
}
```

---

## Query Endpoints

### Conversational Query

Process natural language query.

**Endpoint:** `POST /query`

**Request:**
```json
{
  "dataset_id": "abc123",
  "query": "Show me revenue trends by region",
  "role": "analyst"
}
```

**Response:**
```json
{
  "query_id": "query123",
  "query": "Show me revenue trends by region",
  "result": {
    "intent": "trend_analysis",
    "kpis": {...},
    "chart_configs": [...],
    "insights": [...]
  }
}
```

### Process Command

Execute dashboard command.

**Endpoint:** `POST /query/command`

**Request:**
```json
{
  "dashboard_id": "dash123",
  "command": "show only last 6 months"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Filtered to last 6 months",
  "filters_applied": {
    "date_range": {
      "start": "2023-09-22",
      "end": "2024-03-22"
    }
  }
}
```

### Get Command Suggestions

Get suggested commands.

**Endpoint:** `GET /query/suggestions?dashboard_id={dashboard_id}`

**Response:**
```json
{
  "suggestions": [
    {
      "command": "show only last 6 months",
      "category": "filter",
      "description": "Filter data to recent time period"
    }
  ]
}
```

---

## ML Endpoints

### Train Model

Train a machine learning model.

**Endpoint:** `POST /ml/train`

**Request:**
```json
{
  "dataset_id": "abc123",
  "target_column": "revenue",
  "task_type": "auto",
  "test_size": 0.2
}
```

**Response:**
```json
{
  "model_id": "model123",
  "algorithm": "RandomForest",
  "metrics": {
    "r2_score": 0.85,
    "mae": 1234.56,
    "rmse": 2345.67
  },
  "feature_importance": {
    "price": 0.45,
    "quantity": 0.30,
    "region": 0.25
  }
}
```

### List Models

Get all trained models.

**Endpoint:** `GET /ml/models?dataset_id={dataset_id}`

**Response:**
```json
{
  "models": [
    {
      "id": "model123",
      "dataset_id": "abc123",
      "target_column": "revenue",
      "algorithm": "RandomForest",
      "r2_score": 0.85,
      "created_at": "2024-03-22T10:00:00Z"
    }
  ]
}
```

### Make Prediction

Make predictions with a model.

**Endpoint:** `POST /ml/models/{model_id}/predict`

**Request:**
```json
{
  "data": [
    {
      "price": 100,
      "quantity": 50,
      "region": "North"
    }
  ]
}
```

**Response:**
```json
{
  "predictions": [5000.0],
  "model_id": "model123"
}
```

### Forecast

Generate time-series forecast.

**Endpoint:** `POST /ml/models/{model_id}/forecast`

**Request:**
```json
{
  "periods": 12,
  "frequency": "M"
}
```

**Response:**
```json
{
  "forecast": [
    {
      "period": "2024-04",
      "value": 105000,
      "lower_bound": 95000,
      "upper_bound": 115000
    }
  ]
}
```

### What-If Simulation

Run scenario simulation.

**Endpoint:** `POST /ml/what-if/simulate`

**Request:**
```json
{
  "dataset_id": "abc123",
  "parameter_changes": {
    "price": 120,
    "marketing_budget": 50000
  },
  "target_metric": "revenue"
}
```

**Response:**
```json
{
  "baseline": {
    "revenue": 100000
  },
  "scenario": {
    "revenue": 115000
  },
  "impact": {
    "absolute": 15000,
    "percentage": 15.0
  }
}
```

---

## Drill-Down Endpoints

### Get Drill-Down Levels

Get available drill-down values.

**Endpoint:** `POST /drilldown/levels`

**Request:**
```json
{
  "dataset_id": "abc123",
  "column": "region",
  "parent_filters": {}
}
```

**Response:**
```json
{
  "column": "region",
  "values": [
    {
      "value": "North",
      "count": 250,
      "percentage": 25.0
    }
  ],
  "total_count": 1000,
  "unique_count": 4
}
```

### Get Drill-Down Data

Get filtered data for drill-down level.

**Endpoint:** `POST /drilldown/data`

**Request:**
```json
{
  "dataset_id": "abc123",
  "column": "region",
  "value": "North",
  "parent_filters": {}
}
```

**Response:**
```json
{
  "row_count": 250,
  "summary": {
    "revenue": {
      "sum": 250000,
      "mean": 1000,
      "median": 950
    }
  },
  "sample_data": [...]
}
```

### Suggest Next Drill-Down

Get suggestions for next drill-down column.

**Endpoint:** `POST /drilldown/suggest-next`

**Request:**
```json
{
  "dataset_id": "abc123",
  "column": "region",
  "value": "North",
  "parent_filters": {}
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "column": "product_category",
      "unique_count": 5,
      "score": 85.5
    }
  ]
}
```

---

## Filter Endpoints

### Apply Filters

Apply filters to dataset.

**Endpoint:** `POST /filters/apply`

**Request:**
```json
{
  "dataset_id": "abc123",
  "filters": [
    {
      "column": "revenue",
      "operator": "greater_than",
      "value": 1000,
      "type": "number"
    }
  ],
  "return_data": false
}
```

**Response:**
```json
{
  "original_count": 1000,
  "filtered_count": 750,
  "rows_removed": 250,
  "percentage_remaining": 75.0,
  "summary": {...}
}
```

### Validate Filter

Validate filter configuration.

**Endpoint:** `POST /filters/validate?dataset_id={dataset_id}`

**Request:**
```json
{
  "column": "revenue",
  "operator": "greater_than",
  "value": 1000,
  "type": "number"
}
```

**Response:**
```json
{
  "valid": true,
  "total_rows": 1000,
  "valid_values": 950,
  "estimated_result_count": 750
}
```

### Get Filter Suggestions

Get suggested filter values.

**Endpoint:** `GET /filters/suggestions/{dataset_id}/{column}?limit=10`

**Response:**
```json
{
  "column": "region",
  "suggested_values": ["North", "South", "East", "West"],
  "value_counts": {
    "North": 250,
    "South": 300,
    "East": 200,
    "West": 250
  },
  "total_unique": 4
}
```

---

## Memory Endpoints

### Get Query History

Get past queries.

**Endpoint:** `GET /memory/queries?dataset_id={dataset_id}&limit=10`

**Response:**
```json
{
  "queries": [
    {
      "id": "query123",
      "query_text": "Show revenue trends",
      "response_summary": "Revenue increased 15%",
      "created_at": "2024-03-22T10:00:00Z"
    }
  ]
}
```

### Search Similar Queries

Find similar past queries.

**Endpoint:** `GET /memory/similar?q={query}&limit=5`

**Response:**
```json
{
  "similar_queries": [
    {
      "id": "query123",
      "query_text": "Show revenue trends by region",
      "response_summary": "...",
      "created_at": "2024-03-22T10:00:00Z"
    }
  ]
}
```

### Save Query

Save query to memory.

**Endpoint:** `POST /memory/queries`

**Request:**
```json
{
  "dataset_id": "abc123",
  "query_text": "Show revenue trends",
  "response_json": {...}
}
```

**Response:**
```json
{
  "id": "query123",
  "embedding_id": "emb123",
  "message": "Query saved to memory"
}
```

### Get User Preferences

Get learned preferences.

**Endpoint:** `GET /memory/preferences?action_type={type}&limit=50`

**Response:**
```json
{
  "preferences": [
    {
      "id": "pref123",
      "action_type": "chart_type_change",
      "from_value": "line",
      "to_value": "bar",
      "weight": 5.0,
      "created_at": "2024-03-22T10:00:00Z"
    }
  ]
}
```

### Save Preference

Save user preference.

**Endpoint:** `POST /memory/preferences`

**Request:**
```json
{
  "action_type": "chart_type_change",
  "from_value": "line",
  "to_value": "bar",
  "weight": 1.0
}
```

**Response:**
```json
{
  "id": "pref123",
  "weight": 1.0,
  "message": "Preference saved"
}
```

---

## Export Endpoints

### Export Dashboard JSON

Export dashboard configuration.

**Endpoint:** `POST /export-v2/dashboard/json`

**Request:**
```json
{
  "dashboard_id": "dash123",
  "include_data": false
}
```

**Response:**
```json
{
  "dashboard": {...},
  "export_id": "export123",
  "timestamp": "2024-03-22T10:00:00Z"
}
```

### Export Chart PNG

Export chart as image.

**Endpoint:** `POST /export-v2/chart/png`

**Request:**
```json
{
  "chart_config": {...},
  "width": 800,
  "height": 600,
  "dpi": 300
}
```

**Response:**
```json
{
  "image_base64": "data:image/png;base64,...",
  "width": 800,
  "height": 600
}
```

### Export Data CSV

Export filtered data.

**Endpoint:** `POST /export-v2/data/csv`

**Request:**
```json
{
  "dataset_id": "abc123",
  "filters": [...]
}
```

**Response:**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="data.csv"

date,revenue,region
2024-01-01,1000,North
...
```

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (invalid input)
- `404` - Not Found (resource doesn't exist)
- `422` - Validation Error (invalid data format)
- `500` - Internal Server Error

### Common Errors

**Dataset Not Found**
```json
{
  "detail": "Dataset not found"
}
```

**Invalid Filter**
```json
{
  "detail": "Column 'invalid_column' not found"
}
```

**ML Training Failed**
```json
{
  "detail": "Insufficient data for training. Need at least 50 rows."
}
```

---

## Rate Limiting

Currently no rate limiting. For production:
- Implement rate limiting per IP
- Suggested: 100 requests per minute
- Return `429 Too Many Requests` when exceeded

---

## Pagination

For endpoints returning lists, use:
- `limit` - Number of items (default: 10, max: 100)
- `offset` - Skip items (default: 0)

Example:
```
GET /datasets?limit=20&offset=40
```

---

## Webhooks

Not currently implemented. Future feature for:
- Dashboard updates
- ML training completion
- Data upload completion

---

## API Versioning

Current version: `v1`

Future versions will use URL versioning:
- `/api/v1/...`
- `/api/v2/...`

---

## SDK Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Upload file
with open("data.csv", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/upload/file",
        files={"file": f}
    )
    dataset = response.json()

# Generate dashboard
response = requests.post(
    f"{BASE_URL}/dashboards/generate",
    json={
        "name": "My Dashboard",
        "dataset_id": dataset["dataset_id"],
        "preset": "executive"
    }
)
dashboard = response.json()
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000/api";

// Upload file
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const response = await fetch(`${BASE_URL}/upload/file`, {
  method: "POST",
  body: formData
});
const dataset = await response.json();

// Generate dashboard
const dashResponse = await fetch(`${BASE_URL}/dashboards/generate`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "My Dashboard",
    dataset_id: dataset.dataset_id,
    preset: "executive"
  })
});
const dashboard = await dashResponse.json();
```

---

## Testing

Use the interactive API documentation:
- Navigate to `http://localhost:8000/docs`
- Try out endpoints directly
- See request/response examples
- Download OpenAPI spec

---

**Version:** 1.0.0  
**Last Updated:** March 22, 2026  
**Platform:** Talking BI - Agentic AI Business Intelligence

