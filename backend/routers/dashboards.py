from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from database.db import get_db
from database.models import Dashboard, Dataset
from agents.chart_agent import recommend_charts
from agents.analyst_agent import run_analysis
from typing import List, Dict, Any
import uuid
import pandas as pd

router = APIRouter()


class DashboardCreate(BaseModel):
    name: str
    dataset_id: str
    preset: str = "executive"
    role: str = "default"


class DashboardUpdate(BaseModel):
    name: str = None
    layout_json: List[Dict] = None
    tiles_json: List[Dict] = None
    filters_json: Dict = None


@router.post("/generate")
async def generate_dashboard(
    request: DashboardCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate dashboard from dataset with automatic chart recommendations.
    Like Power BI - automatically creates intelligent visualizations.
    """
    print(f"\n=== GENERATE DASHBOARD ===")
    print(f"Dataset ID: {request.dataset_id}")
    print(f"Preset: {request.preset}")
    print(f"Name: {request.name}")
    
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == request.dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        print(f"✗ Dataset not found: {request.dataset_id}")
        # List all datasets for debugging
        all_datasets = await db.execute(select(Dataset))
        datasets = all_datasets.scalars().all()
        print(f"Available datasets: {[d.id for d in datasets]}")
        raise HTTPException(status_code=404, detail=f"Dataset not found: {request.dataset_id}")
    
    print(f"✓ Dataset found: {dataset.name}")
    
    # Load data from SQLite table
    table_name = dataset.sqlite_table_name
    
    if not table_name:
        print(f"✗ Dataset table not found")
        raise HTTPException(status_code=400, detail="Dataset table not found in database")
    
    try:
        query = f"SELECT * FROM {table_name}"
        result = await db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        
        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        print(f"Loaded {len(df)} rows from table {table_name}")
        print(f"Columns: {list(df.columns)}")
        
    except Exception as e:
        print(f"Error loading data from table {table_name}: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to load dataset: {str(e)}")
    
    if df.empty:
        raise HTTPException(status_code=400, detail="Dataset is empty")
    
    # Identify numeric columns for KPI analysis
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != '_is_outlier']
    
    # Identify time column if exists
    time_col = None
    for col in df.columns:
        if dataset.schema_json.get(col) in ['datetime', 'year']:
            time_col = col
            break
    
    # Run statistical analysis
    analysis_result = await run_analysis(df, numeric_cols[:5], time_col)
    
    # Get chart recommendations (request MORE charts - up to 20)
    chart_recommendations = await recommend_charts(df, dataset.schema_json, max_charts=20)
    
    # Generate tiles based on preset
    tiles = []
    layout = []
    
    # Use operational preset by default for more charts
    preset = request.preset if request.preset in ["executive", "operational", "trend", "comparison"] else "operational"
    
    if preset == "executive":
        # Executive preset: KPIs + key charts
        tiles, layout, analysis_result = generate_executive_preset(
            df, analysis_result, chart_recommendations
        )
    elif preset == "operational":
        # Operational preset: All charts + data tables
        tiles, layout, analysis_result = generate_operational_preset(
            df, analysis_result, chart_recommendations
        )
    elif preset == "trend":
        # Trend preset: Time-series focused
        tiles, layout, analysis_result = generate_trend_preset(
            df, analysis_result, chart_recommendations
        )
    elif preset == "comparison":
        # Comparison preset: Side-by-side comparisons
        tiles, layout, analysis_result = generate_comparison_preset(
            df, analysis_result, chart_recommendations
        )
    else:
        # Default: Auto-generate based on data
        tiles, layout, analysis_result = generate_auto_preset(
            df, analysis_result, chart_recommendations
        )
    
    # Generate insights and recommendations tiles
    from agents.insight_agent import generate_insights
    from agents.strategist_agent import generate_recommendations
    from agents.critic_agent import run_critic_validation
    
    # Run validation
    validation_result = await run_critic_validation(analysis_result, df, dataset.schema_json)
    
    # Generate insights
    insights_data = await generate_insights(
        analysis_result,
        validation_result,
        dataset.name,
        use_llm=False  # Use rule-based for reliability
    )
    
    # Generate recommendations
    recommendations_data = await generate_recommendations(
        validation_result.get("validated_insights", []),
        analysis_result.get("kpis", {}),
        analysis_result.get("correlations", []),
        analysis_result.get("trends", {})
    )
    
    # Add insights tile
    insights_tile_id = str(uuid.uuid4())
    tiles.append({
        "id": insights_tile_id,
        "type": "insights",
        "title": "Key Insights",
        "data": insights_data
    })
    
    # Add recommendations tile
    recommendations_tile_id = str(uuid.uuid4())
    tiles.append({
        "id": recommendations_tile_id,
        "type": "recommendations",
        "title": "Strategic Recommendations",
        "data": {"recommendations": recommendations_data}
    })
    
    print(f"\n=== DASHBOARD GENERATION ===")
    print(f"Preset: {preset}")
    print(f"Charts recommended: {len(chart_recommendations)}")
    print(f"Tiles generated: {len(tiles)}")
    print(f"Insights generated: {len(insights_data.get('key_insights', []))}")
    print(f"Recommendations generated: {len(recommendations_data)}")
    for i, tile in enumerate(tiles[:5]):  # Show first 5
        tile_type = tile.get('type')
        if tile_type == 'kpi':
            has_data = bool(tile.get('config', {}).get('value') is not None)
        else:
            has_data = bool(tile.get('config', {}).get('data') or tile.get('data'))
        print(f"Tile {i}: type={tile.get('type')}, title={tile.get('title')}, has_data={has_data}")
    print(f"===========================\n")
    
    # Create dashboard
    dashboard = Dashboard(
        id=str(uuid.uuid4()),
        name=request.name,
        dataset_id=request.dataset_id,
        preset=request.preset,
        role=request.role,
        layout_json=layout,
        tiles_json=tiles,
        filters_json={}
    )
    
    db.add(dashboard)
    await db.commit()
    await db.refresh(dashboard)
    
    return {
        "id": dashboard.id,
        "name": dashboard.name,
        "dataset_id": dashboard.dataset_id,
        "preset": dashboard.preset,
        "role": dashboard.role,
        "tiles": tiles,
        "layout": layout,
        "tile_count": len(tiles)
    }


def generate_executive_preset(df, analysis, charts):
    """
    Executive preset: Power BI style with KPI cards with sparklines + key charts
    Layout: 4 KPI cards at top, then mixed chart sizes below
    """
    tiles = []
    layout = []
    
    # ROW 1: KPI cards with sparklines (4 cards, equal width, taller for sparklines)
    kpis = analysis.get("kpis", {})
    current_y = 0
    
    # Generate sparkline data for each KPI
    time_col = None
    for col in df.columns:
        if df[col].dtype in ['datetime64[ns]', 'object']:
            try:
                pd.to_datetime(df[col])
                time_col = col
                break
            except:
                pass
    
    for i, (col, kpi_data) in enumerate(list(kpis.items())[:4]):
        tile_id = str(uuid.uuid4())
        
        # Get trend direction
        trend = "neutral"
        change = kpi_data.get("pct_change", 0)
        if change > 0:
            trend = "up"
        elif change < 0:
            trend = "down"
        
        # Generate sparkline data (last 10 data points)
        sparkline_data = []
        if time_col and col in df.columns:
            try:
                temp_df = df[[time_col, col]].copy()
                temp_df = temp_df.dropna()
                temp_df = temp_df.sort_values(time_col)
                temp_df = temp_df.tail(10)
                
                for _, row in temp_df.iterrows():
                    try:
                        sparkline_data.append({
                            "x": str(row[time_col]),
                            "y": float(row[col])
                        })
                    except:
                        pass
            except:
                pass
        
        # If no time-based sparkline, create simple trend from data
        if not sparkline_data and col in df.columns:
            values = df[col].dropna().tail(10).tolist()
            sparkline_data = [{"x": str(i), "y": float(v)} for i, v in enumerate(values)]
        
        tiles.append({
            "id": tile_id,
            "type": "kpi",
            "title": col.replace('_', ' ').title(),
            "config": {
                "column": col,
                "value": float(kpi_data.get("total", kpi_data.get("mean", 0))),
                "change": float(change),
                "trend": trend,
                "mean": float(kpi_data.get("mean", 0)),
                "median": float(kpi_data.get("median", 0)),
                "min": float(kpi_data.get("min", 0)),
                "max": float(kpi_data.get("max", 0)),
                "sparkline": sparkline_data,
                "prefix": "",
                "suffix": ""
            }
        })
        layout.append({
            "i": tile_id,
            "x": i * 3,
            "y": current_y,
            "w": 3,
            "h": 3  # Taller for sparkline
        })
    
    current_y = 3  # Move to next row
    
    # ROW 2: Two medium charts (half width each)
    for i in range(0, min(2, len(charts))):
        chart = charts[i]
        tile_id = str(uuid.uuid4())
        
        chart_data = aggregate_chart_data(df, chart)
        chart["data"] = chart_data
        
        tiles.append({
            "id": tile_id,
            "type": chart.get("type", "bar"),
            "title": chart.get("title", f"Chart {i+1}"),
            "config": chart
        })
        
        x = i * 6
        layout.append({"i": tile_id, "x": x, "y": current_y, "w": 6, "h": 5})
    
    current_y += 5
    
    # ROW 3: Three medium charts (third width each)
    for i in range(2, min(5, len(charts))):
        chart = charts[i]
        tile_id = str(uuid.uuid4())
        
        chart_data = aggregate_chart_data(df, chart)
        chart["data"] = chart_data
        
        tiles.append({
            "id": tile_id,
            "type": chart.get("type", "bar"),
            "title": chart.get("title", f"Chart {i+1}"),
            "config": chart
        })
        
        x = (i - 2) * 4
        layout.append({"i": tile_id, "x": x, "y": current_y, "w": 4, "h": 5})
    
    current_y += 5
    
    # ROW 4: One large chart (full width)
    if len(charts) > 5:
        chart = charts[5]
        tile_id = str(uuid.uuid4())
        
        chart_data = aggregate_chart_data(df, chart)
        chart["data"] = chart_data
        
        tiles.append({
            "id": tile_id,
            "type": chart.get("type", "bar"),
            "title": chart.get("title", "Detailed Analysis"),
            "config": chart
        })
        
        layout.append({"i": tile_id, "x": 0, "y": current_y, "w": 12, "h": 6})
    
    return tiles, layout, analysis


def generate_operational_preset(df, analysis, charts):
    """
    Operational preset: Power BI style with comprehensive view
    Layout: KPI cards at top + grid of charts below
    """
    tiles = []
    layout = []
    
    print(f"\n=== OPERATIONAL PRESET GENERATION ===")
    print(f"DataFrame shape: {df.shape}")
    print(f"Charts to process: {len(charts)}")
    
    # ROW 1: KPI cards with sparklines (4 cards)
    kpis = analysis.get("kpis", {})
    current_y = 0
    
    # Find time column for sparklines
    time_col = None
    for col in df.columns:
        if df[col].dtype in ['datetime64[ns]', 'object']:
            try:
                pd.to_datetime(df[col])
                time_col = col
                break
            except:
                pass
    
    if kpis:
        print(f"\nGenerating {len(kpis)} KPI cards with sparklines...")
        for i, (col, kpi_data) in enumerate(list(kpis.items())[:4]):
            tile_id = str(uuid.uuid4())
            
            trend = "neutral"
            change = kpi_data.get("pct_change", 0)
            if change > 0:
                trend = "up"
            elif change < 0:
                trend = "down"
            
            # Generate sparkline data
            sparkline_data = []
            if time_col and col in df.columns:
                try:
                    temp_df = df[[time_col, col]].copy()
                    temp_df = temp_df.dropna()
                    temp_df = temp_df.sort_values(time_col)
                    temp_df = temp_df.tail(15)
                    
                    for _, row in temp_df.iterrows():
                        try:
                            sparkline_data.append({
                                "x": str(row[time_col]),
                                "y": float(row[col])
                            })
                        except:
                            pass
                except:
                    pass
            
            if not sparkline_data and col in df.columns:
                values = df[col].dropna().tail(15).tolist()
                sparkline_data = [{"x": str(i), "y": float(v)} for i, v in enumerate(values)]
            
            tiles.append({
                "id": tile_id,
                "type": "kpi",
                "title": col.replace('_', ' ').title(),
                "config": {
                    "type": "kpi",
                    "column": col,
                    "value": float(kpi_data.get("total", kpi_data.get("mean", 0))),
                    "change": float(change),
                    "trend": trend,
                    "mean": float(kpi_data.get("mean", 0)),
                    "median": float(kpi_data.get("median", 0)),
                    "min": float(kpi_data.get("min", 0)),
                    "max": float(kpi_data.get("max", 0)),
                    "sparkline": sparkline_data
                }
            })
            
            layout.append({
                "i": tile_id,
                "x": i * 3,
                "y": current_y,
                "w": 3,
                "h": 3
            })
        
        current_y = 3
    
    # Grid layout for charts: 2x2 grid pattern
    chart_index = 0
    row = 0
    
    while chart_index < len(charts):
        # Row pattern: 2 medium charts (6 units each)
        for col_pos in range(2):
            if chart_index >= len(charts):
                break
            
            chart = charts[chart_index]
            tile_id = str(uuid.uuid4())
            
            print(f"\nProcessing chart {chart_index+1}/{len(charts)}: {chart.get('title')}")
            
            chart_data = aggregate_chart_data(df, chart)
            chart["data"] = chart_data
            
            tiles.append({
                "id": tile_id,
                "type": chart.get("type", "bar"),
                "title": chart.get("title", f"Chart {chart_index+1}"),
                "config": chart
            })
            
            x = col_pos * 6
            y = current_y + (row * 5)
            layout.append({"i": tile_id, "x": x, "y": y, "w": 6, "h": 5})
            
            chart_index += 1
        
        row += 1
    
    print(f"\n=== OPERATIONAL PRESET COMPLETE ===")
    print(f"Total tiles: {len(tiles)}")
    print(f"KPI cards: {len([t for t in tiles if t.get('type') == 'kpi'])}")
    print(f"Chart tiles: {len([t for t in tiles if t.get('type') != 'kpi'])}")
    print(f"=====================================\n")
    
    return tiles, layout, analysis


def generate_trend_preset(df, analysis, charts):
    """Trend preset: Time-series and trend analysis charts"""
    tiles = []
    layout = []
    
    # ROW 1: KPI cards at the top
    kpis = analysis.get("kpis", {})
    current_y = 0
    
    if kpis:
        for i, (col, kpi_data) in enumerate(list(kpis.items())[:4]):
            tile_id = str(uuid.uuid4())
            
            trend = "neutral"
            change = kpi_data.get("pct_change", 0)
            if change > 0:
                trend = "up"
            elif change < 0:
                trend = "down"
            
            tiles.append({
                "id": tile_id,
                "type": "kpi",
                "title": col.replace('_', ' ').title(),
                "config": {
                    "type": "kpi",
                    "column": col,
                    "value": float(kpi_data.get("total", kpi_data.get("mean", 0))),
                    "change": float(change),
                    "trend": trend,
                    "mean": float(kpi_data.get("mean", 0)),
                    "median": float(kpi_data.get("median", 0)),
                    "min": float(kpi_data.get("min", 0)),
                    "max": float(kpi_data.get("max", 0))
                }
            })
            layout.append({
                "i": tile_id,
                "x": i * 3,
                "y": 0,
                "w": 3,
                "h": 2
            })
        
        current_y = 2
    
    # Prefer line/area charts, but include scatter if no line charts
    time_charts = [c for c in charts if c.get("type") in ["line", "area"]]
    
    if not time_charts:
        # If no line/area charts, use scatter and other charts
        time_charts = [c for c in charts if c.get("type") in ["scatter", "bar", "histogram"]]
    
    # Full-width stacked charts for trend analysis
    for i, chart in enumerate(time_charts):
        tile_id = str(uuid.uuid4())
        
        # Aggregate data for chart
        chart_data = aggregate_chart_data(df, chart)
        chart["data"] = chart_data
        
        tiles.append({
            "id": tile_id,
            "type": chart.get("type", "chart"),
            "title": chart.get("title", f"Trend {i+1}"),
            "config": chart
        })
        
        # Full width, 4 units tall, stacked vertically
        layout.append({"i": tile_id, "x": 0, "y": current_y, "w": 12, "h": 4})
        current_y += 4
    
    return tiles, layout, analysis


def generate_comparison_preset(df, analysis, charts):
    """Comparison preset: Side-by-side comparison charts in 2-column grid"""
    tiles = []
    layout = []
    
    # ROW 1: KPI cards at the top
    kpis = analysis.get("kpis", {})
    current_y = 0
    
    if kpis:
        for i, (col, kpi_data) in enumerate(list(kpis.items())[:4]):
            tile_id = str(uuid.uuid4())
            
            trend = "neutral"
            change = kpi_data.get("pct_change", 0)
            if change > 0:
                trend = "up"
            elif change < 0:
                trend = "down"
            
            tiles.append({
                "id": tile_id,
                "type": "kpi",
                "title": col.replace('_', ' ').title(),
                "config": {
                    "type": "kpi",
                    "column": col,
                    "value": float(kpi_data.get("total", kpi_data.get("mean", 0))),
                    "change": float(change),
                    "trend": trend,
                    "mean": float(kpi_data.get("mean", 0)),
                    "median": float(kpi_data.get("median", 0)),
                    "min": float(kpi_data.get("min", 0)),
                    "max": float(kpi_data.get("max", 0))
                }
            })
            layout.append({
                "i": tile_id,
                "x": i * 3,
                "y": 0,
                "w": 3,
                "h": 2
            })
        
        current_y = 2
    
    # Prefer bar charts, but include scatter for comparison
    comparison_charts = [c for c in charts if c.get("type") in ["bar", "grouped_bar"]]
    
    if not comparison_charts:
        # If no bar charts, use scatter charts (good for comparing relationships)
        comparison_charts = [c for c in charts if c.get("type") in ["scatter", "histogram"]]
    
    # 2-column grid layout for side-by-side comparison
    for i, chart in enumerate(comparison_charts):
        tile_id = str(uuid.uuid4())
        
        # Aggregate data for chart
        chart_data = aggregate_chart_data(df, chart)
        chart["data"] = chart_data
        
        tiles.append({
            "id": tile_id,
            "type": chart.get("type", "chart"),
            "title": chart.get("title", f"Comparison {i+1}"),
            "config": chart
        })
        
        # 2-column grid: left (x=0) or right (x=6), each 6 units wide, 4 units tall
        x = (i % 2) * 6
        y = current_y + (i // 2) * 4
        layout.append({"i": tile_id, "x": x, "y": y, "w": 6, "h": 4})
    
    return tiles, layout, analysis


def generate_auto_preset(df, analysis, charts):
    """Auto preset: Smart layout based on data"""
    return generate_operational_preset(df, analysis, charts)


def aggregate_chart_data(df: pd.DataFrame, chart_config: Dict) -> List[Dict]:
    """
    Aggregate data for chart based on configuration.
    Returns list of data points ready for frontend rendering.
    """
    chart_type = chart_config.get("type")
    x_col = chart_config.get("x_column")
    y_col = chart_config.get("y_column")
    agg = chart_config.get("aggregation", "sum")
    color_by = chart_config.get("color_by")
    
    print(f"\n--- Aggregating {chart_type} chart ---")
    print(f"x_col: {x_col}, y_col: {y_col}")
    print(f"Available columns: {df.columns.tolist()}")
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame dtypes:\n{df.dtypes}")
    
    # Verify columns exist
    if x_col and x_col not in df.columns:
        print(f"ERROR: x_column '{x_col}' not found in DataFrame!")
        print(f"Available columns: {df.columns.tolist()}")
        return []
    
    if y_col and y_col not in df.columns:
        print(f"ERROR: y_column '{y_col}' not found in DataFrame!")
        print(f"Available columns: {df.columns.tolist()}")
        return []
    
    try:
        # Handle different chart types
        if chart_type == "histogram":
            # For histogram, return raw values
            if x_col and x_col in df.columns:
                values = df[x_col].dropna()
                # Convert to numeric if possible
                try:
                    values = pd.to_numeric(values, errors='coerce').dropna()
                except:
                    pass
                values_list = values.tolist()
                print(f"Histogram: {len(values_list)} values")
                return [{"value": float(v)} for v in values_list[:1000]]  # Limit to 1000 points
            else:
                print(f"ERROR: Column {x_col} not found for histogram")
                return []
        
        elif chart_type == "scatter":
            # For scatter, return x,y pairs
            if x_col and y_col and x_col in df.columns and y_col in df.columns:
                data = df[[x_col, y_col]].copy()
                
                # Convert to numeric
                try:
                    data[x_col] = pd.to_numeric(data[x_col], errors='coerce')
                    data[y_col] = pd.to_numeric(data[y_col], errors='coerce')
                except:
                    pass
                
                data = data.dropna()
                result = []
                for _, row in data.head(500).iterrows():  # Limit to 500 points
                    try:
                        point = {
                            "x": float(row[x_col]),
                            "y": float(row[y_col])
                        }
                        if color_by and color_by in df.columns:
                            point["category"] = str(row.get(color_by, ""))
                        result.append(point)
                    except (ValueError, TypeError) as e:
                        continue
                print(f"Scatter: {len(result)} points")
                return result
            else:
                print(f"ERROR: Columns {x_col}, {y_col} not found for scatter")
                return []
        
        elif chart_type == "pie":
            # For pie, aggregate by category
            if x_col and x_col in df.columns:
                try:
                    if y_col and y_col in df.columns:
                        # Try to convert y_col to numeric
                        y_series = pd.to_numeric(df[y_col], errors='coerce')
                        
                        if y_series.notna().sum() > 0:
                            # Aggregate numeric y column
                            temp_df = df[[x_col]].copy()
                            temp_df['y_numeric'] = y_series
                            grouped = temp_df.groupby(x_col)['y_numeric'].agg(agg).reset_index()
                            grouped = grouped.sort_values('y_numeric', ascending=False).head(10)  # Top 10
                            result = [
                                {
                                    "name": str(row[x_col]),
                                    "value": float(row['y_numeric'])
                                }
                                for _, row in grouped.iterrows()
                            ]
                        else:
                            # Count by x_col
                            grouped = df.groupby(x_col).size().reset_index(name='count')
                            grouped = grouped.sort_values('count', ascending=False).head(10)  # Top 10
                            result = [
                                {
                                    "name": str(row[x_col]),
                                    "value": int(row['count'])
                                }
                                for _, row in grouped.iterrows()
                            ]
                    else:
                        # Count by x_col
                        grouped = df.groupby(x_col).size().reset_index(name='count')
                        grouped = grouped.sort_values('count', ascending=False).head(10)  # Top 10
                        result = [
                            {
                                "name": str(row[x_col]),
                                "value": int(row['count'])
                            }
                            for _, row in grouped.iterrows()
                        ]
                    print(f"Pie: {len(result)} slices")
                    return result
                except Exception as e:
                    print(f"ERROR in pie aggregation: {e}")
                    import traceback
                    traceback.print_exc()
                    return []
            else:
                print(f"ERROR: Column {x_col} not found for pie")
                return []
        
        elif chart_type in ["line", "area", "bar"]:
            # For line/area/bar, aggregate by x column
            if x_col and x_col in df.columns:
                if y_col and y_col in df.columns:
                    try:
                        # Try to convert y_col to numeric
                        y_series = pd.to_numeric(df[y_col], errors='coerce')
                        
                        if y_series.notna().sum() > 0:
                            # Group by x column and aggregate y column
                            temp_df = df[[x_col]].copy()
                            temp_df['y_numeric'] = y_series
                            temp_df = temp_df.dropna()
                            
                            grouped = temp_df.groupby(x_col)['y_numeric'].agg(agg).reset_index()
                            grouped = grouped.sort_values(x_col)
                            
                            result = []
                            for _, row in grouped.iterrows():
                                try:
                                    point = {
                                        "x": str(row[x_col]),
                                        "y": float(row['y_numeric'])
                                    }
                                    result.append(point)
                                except (ValueError, TypeError):
                                    continue
                            
                            print(f"{chart_type}: {len(result)} points")
                            return result
                        else:
                            # If y_col is not numeric, do count aggregation
                            print(f"y_col {y_col} is not numeric, using count aggregation")
                            grouped = df.groupby(x_col).size().reset_index(name='count')
                            grouped = grouped.sort_values(x_col)
                            
                            result = []
                            for _, row in grouped.iterrows():
                                try:
                                    point = {
                                        "x": str(row[x_col]),
                                        "y": int(row['count'])
                                    }
                                    result.append(point)
                                except (ValueError, TypeError):
                                    continue
                            
                            print(f"{chart_type}: {len(result)} points (count)")
                            return result
                    except Exception as e:
                        print(f"ERROR in {chart_type} aggregation: {e}")
                        import traceback
                        traceback.print_exc()
                        return []
                else:
                    # No y_col specified, do count by x_col
                    try:
                        grouped = df.groupby(x_col).size().reset_index(name='count')
                        grouped = grouped.sort_values(x_col)
                        
                        result = []
                        for _, row in grouped.iterrows():
                            try:
                                point = {
                                    "x": str(row[x_col]),
                                    "y": int(row['count'])
                                }
                                result.append(point)
                            except (ValueError, TypeError):
                                continue
                        
                        print(f"{chart_type}: {len(result)} points (count)")
                        return result
                    except Exception as e:
                        print(f"ERROR in {chart_type} count aggregation: {e}")
                        import traceback
                        traceback.print_exc()
                        return []
            else:
                print(f"ERROR: Column {x_col} not found for {chart_type}")
                return []
        
        elif chart_type == "heatmap":
            # For heatmap, return correlation matrix
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            numeric_cols = [c for c in numeric_cols if c != '_is_outlier'][:10]  # Max 10 cols
            
            print(f"Numeric columns for heatmap: {numeric_cols}")
            
            if len(numeric_cols) >= 2:
                corr_matrix = df[numeric_cols].corr()
                result = []
                for i, row_name in enumerate(corr_matrix.index):
                    for j, col_name in enumerate(corr_matrix.columns):
                        result.append({
                            "x": str(col_name),
                            "y": str(row_name),
                            "value": float(corr_matrix.iloc[i, j])
                        })
                print(f"Heatmap: {len(result)} cells")
                return result
            else:
                print(f"ERROR: Not enough numeric columns for heatmap")
                return []
        
        # Default: return empty
        print(f"WARNING: Unknown chart type {chart_type}")
        return []
    
    except Exception as e:
        print(f"ERROR aggregating chart data: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.get("")
async def list_dashboards(db: AsyncSession = Depends(get_db)):
    """List all dashboards"""
    result = await db.execute(select(Dashboard).order_by(Dashboard.created_at.desc()))
    dashboards = result.scalars().all()
    
    return [
        {
            "id": d.id,
            "name": d.name,
            "dataset_id": d.dataset_id,
            "preset": d.preset,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "tile_count": len(d.tiles_json) if d.tiles_json else 0
        }
        for d in dashboards
    ]


@router.get("/{dashboard_id}")
async def get_dashboard(dashboard_id: str, db: AsyncSession = Depends(get_db)):
    """Get dashboard configuration with chart data"""
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Get dataset to fetch actual data
    result = await db.execute(select(Dataset).where(Dataset.id == dashboard.dataset_id))
    dataset = result.scalar_one_or_none()
    
    chart_data = {}
    if dataset and dataset.sqlite_table_name:
        # Load data from SQLite
        table_name = dataset.sqlite_table_name
        query = f"SELECT * FROM {table_name}"
        result = await db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
        
        # Prepare data for each tile
        if dashboard.tiles_json:
            for tile in dashboard.tiles_json:
                if tile.get("type") == "chart" and tile.get("config"):
                    # Data is already in the config from generation
                    # But we can refresh it here if needed
                    pass
    
    return {
        "id": dashboard.id,
        "name": dashboard.name,
        "dataset_id": dashboard.dataset_id,
        "preset": dashboard.preset,
        "layout": dashboard.layout_json,
        "tiles": dashboard.tiles_json,
        "filters": dashboard.filters_json,
        "role": dashboard.role
    }


@router.put("/{dashboard_id}")
async def update_dashboard(
    dashboard_id: str,
    request: DashboardUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update dashboard configuration"""
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    if request.name:
        dashboard.name = request.name
    if request.layout_json is not None:
        dashboard.layout_json = request.layout_json
    if request.tiles_json is not None:
        dashboard.tiles_json = request.tiles_json
    if request.filters_json is not None:
        dashboard.filters_json = request.filters_json
    
    await db.commit()
    await db.refresh(dashboard)
    
    return {"message": "Dashboard updated successfully"}


@router.delete("/{dashboard_id}")
async def delete_dashboard(dashboard_id: str, db: AsyncSession = Depends(get_db)):
    """Delete dashboard"""
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    await db.delete(dashboard)
    await db.commit()
    
    return {"message": "Dashboard deleted successfully"}
