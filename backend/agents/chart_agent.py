import pandas as pd
from typing import Dict, List
from utils.schema_detector import infer_column_types


CHART_SELECTION_RULES = {
    "time_series_single": "line",
    "time_series_multi": "area",
    "category_single_metric": "bar",
    "category_multi_metric": "grouped_bar",
    "part_of_whole": "pie",
    "correlation": "scatter",
    "distribution": "histogram",
    "heatmap": "heatmap",
    "geographic": "map",
    "hierarchical": "treemap",
    "cumulative": "waterfall",
    "sparkline": "sparkline",
    "comparison_two_periods": "waterfall",
}


async def recommend_charts(
    df: pd.DataFrame,
    schema: Dict[str, str],
    max_charts: int = 10
) -> List[Dict]:
    """
    Intelligently recommend chart configurations based on data types and relationships.
    Returns list of chart configs ready for frontend rendering.
    """
    chart_configs = []
    
    # Identify column types (exclude identifier columns)
    datetime_cols = [col for col, dtype in schema.items() if dtype in ["datetime", "year"]]
    numeric_cols = [col for col, dtype in schema.items() if dtype in ["numeric", "currency", "percentage"]]
    categorical_cols = [col for col, dtype in schema.items() if dtype == "categorical"]
    geographic_cols = [col for col, dtype in schema.items() if dtype == "geographic"]
    
    print(f"\n=== CHART RECOMMENDATION ===")
    print(f"Datetime columns: {datetime_cols}")
    print(f"Numeric columns: {numeric_cols}")
    print(f"Categorical columns: {categorical_cols}")
    print(f"Geographic columns: {geographic_cols}")
    print(f"===========================\n")
    
    # If no valid columns, return empty
    if not numeric_cols and not categorical_cols:
        print("WARNING: No numeric or categorical columns found for charts")
        # Try to create at least some basic charts with whatever we have
        all_cols = list(schema.keys())
        if len(all_cols) >= 2:
            # Create a simple scatter or bar chart with first two columns
            print(f"Attempting to create basic chart with columns: {all_cols[:2]}")
            chart_configs.append({
                "type": "bar",
                "x_column": all_cols[0],
                "y_column": None,
                "aggregation": "count",
                "title": f"Count by {all_cols[0]}",
                "color_by": None,
                "filters": []
            })
        return chart_configs
    
    # 1. Time series charts (if datetime column exists)
    if datetime_cols and numeric_cols:
        time_col = datetime_cols[0]
        
        # Create line chart for EACH numeric column
        for num_col in numeric_cols[:5]:
            chart_configs.append({
                "type": "line",
                "x_column": time_col,
                "y_column": num_col,
                "aggregation": "sum",
                "title": f"{num_col} Over Time",
                "color_by": None,
                "filters": []
            })
        
        # Multi-metric area chart
        if len(numeric_cols) >= 2:
            chart_configs.append({
                "type": "area",
                "x_column": time_col,
                "y_column": numeric_cols[0],
                "aggregation": "sum",
                "title": f"{numeric_cols[0]} Cumulative Trend",
                "color_by": categorical_cols[0] if categorical_cols else None,
                "filters": []
            })
    
    # 2. Categorical vs Numeric - Create MORE bar charts
    if categorical_cols and numeric_cols:
        # Create bar chart for EVERY combination
        for cat_col in categorical_cols[:3]:
            for num_col in numeric_cols[:3]:
                chart_configs.append({
                    "type": "bar",
                    "x_column": cat_col,
                    "y_column": num_col,
                    "aggregation": "sum",
                    "title": f"{num_col} by {cat_col}",
                    "color_by": None,
                    "filters": []
                })
        
        # Pie charts for EACH categorical column with EACH numeric
        for cat_col in categorical_cols[:3]:
            if df[cat_col].nunique() <= 10:
                for num_col in numeric_cols[:2]:
                    chart_configs.append({
                        "type": "pie",
                        "x_column": cat_col,
                        "y_column": num_col,
                        "aggregation": "sum",
                        "title": f"{num_col} Distribution by {cat_col}",
                        "color_by": None,
                        "filters": []
                    })
    
    # 3. Categorical only - Create count charts
    elif categorical_cols and not numeric_cols:
        # Create count bar charts for each categorical column
        for cat_col in categorical_cols[:5]:
            chart_configs.append({
                "type": "bar",
                "x_column": cat_col,
                "y_column": None,
                "aggregation": "count",
                "title": f"Count by {cat_col}",
                "color_by": None,
                "filters": []
            })
        
        # Create pie charts for distribution
        for cat_col in categorical_cols[:3]:
            if df[cat_col].nunique() <= 10:
                chart_configs.append({
                    "type": "pie",
                    "x_column": cat_col,
                    "y_column": None,
                    "aggregation": "count",
                    "title": f"{cat_col} Distribution",
                    "color_by": None,
                    "filters": []
                })
    
    # 4. Correlation scatter plots
    if len(numeric_cols) >= 2:
        # Create scatter for combinations
        for i in range(min(5, len(numeric_cols))):
            for j in range(i + 1, min(i + 3, len(numeric_cols))):
                if j < len(numeric_cols):
                    chart_configs.append({
                        "type": "scatter",
                        "x_column": numeric_cols[i],
                        "y_column": numeric_cols[j],
                        "aggregation": None,
                        "title": f"{numeric_cols[j]} vs {numeric_cols[i]}",
                        "color_by": categorical_cols[0] if categorical_cols else None,
                        "filters": []
                    })
    
    # 5. Distribution histograms for EACH numeric column
    for num_col in numeric_cols[:5]:
        chart_configs.append({
            "type": "histogram",
            "x_column": num_col,
            "y_column": None,
            "aggregation": "count",
            "title": f"{num_col} Distribution",
            "color_by": None,
            "filters": []
        })
    
    # 6. Geographic map
    if geographic_cols and numeric_cols:
        chart_configs.append({
            "type": "map",
            "x_column": geographic_cols[0],
            "y_column": numeric_cols[0],
            "aggregation": "sum",
            "title": f"{numeric_cols[0]} by {geographic_cols[0]}",
            "color_by": None,
            "filters": []
        })
    
    # 7. Heatmap for correlation matrix
    if len(numeric_cols) >= 3:
        chart_configs.append({
            "type": "heatmap",
            "x_column": None,
            "y_column": None,
            "aggregation": None,
            "title": "Correlation Matrix",
            "color_by": None,
            "filters": []
        })
    
    # 8. Comparison charts
    if len(numeric_cols) >= 2 and categorical_cols:
        chart_configs.append({
            "type": "bar",
            "x_column": categorical_cols[0],
            "y_column": numeric_cols[0],
            "aggregation": "mean",
            "title": f"Average {numeric_cols[0]} by {categorical_cols[0]}",
            "color_by": None,
            "filters": []
        })
    
    print(f"Total charts recommended: {len(chart_configs)}")
    
    # Return up to max_charts (but allow more if requested)
    return chart_configs[:max(max_charts, 20)]


async def generate_chart_config(
    chart_type: str,
    x_column: str,
    y_column: str = None,
    aggregation: str = "sum",
    title: str = None,
    color_by: str = None
) -> Dict:
    """
    Generate complete chart configuration for frontend rendering.
    """
    config = {
        "type": chart_type,
        "x_column": x_column,
        "y_column": y_column,
        "aggregation": aggregation,
        "title": title or f"{chart_type.title()} Chart",
        "color_by": color_by,
        "options": {
            "show_legend": True,
            "show_grid": True,
            "show_labels": True,
            "responsive": True
        },
        "colors": [
            "#F5A623", "#3B82F6", "#22C55E",
            "#EC4899", "#8B5CF6", "#14B8A6"
        ]
    }
    
    # Chart-specific options
    if chart_type == "line":
        config["options"]["curve"] = "monotone"
        config["options"]["dot_size"] = 4
    elif chart_type == "bar":
        config["options"]["bar_size"] = 40
    elif chart_type == "pie":
        config["options"]["inner_radius"] = 0
        config["options"]["show_labels"] = True
    elif chart_type == "scatter":
        config["options"]["dot_size"] = 6
    elif chart_type == "heatmap":
        config["options"]["color_scale"] = ["#3B82F6", "#F5A623", "#EF4444"]
    
    return config
