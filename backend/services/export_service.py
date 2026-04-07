"""
Export Service - Export dashboards, charts, and data in various formats
Supports JSON, PNG, CSV exports
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import json
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

from database.models import Dashboard, Dataset


async def export_dashboard_json(
    db: AsyncSession,
    dashboard_id: str,
    include_data: bool = False
) -> Dict:
    """
    Export dashboard configuration as JSON.
    
    Args:
        db: Database session
        dashboard_id: Dashboard ID
        include_data: Whether to include actual data
    
    Returns:
        Dashboard JSON export
    """
    # Get dashboard
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise ValueError(f"Dashboard {dashboard_id} not found")
    
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == dashboard.dataset_id))
    dataset = result.scalar_one_or_none()
    
    export_data = {
        "dashboard_id": dashboard.id,
        "name": dashboard.name,
        "dataset_id": dashboard.dataset_id,
        "dataset_name": dataset.name if dataset else None,
        "preset": dashboard.preset,
        "role": dashboard.role,
        "layout": dashboard.layout_json,
        "tiles": dashboard.tiles_json,
        "filters": dashboard.filters_json,
        "created_at": dashboard.created_at.isoformat() if dashboard.created_at else None,
        "updated_at": dashboard.updated_at.isoformat() if dashboard.updated_at else None,
        "exported_at": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    # Include actual data if requested
    if include_data and dataset:
        from sqlalchemy import text
        query_sql = f'SELECT * FROM "{dataset.sqlite_table_name}"'
        result = await db.execute(text(query_sql))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
        
        # Convert to JSON-serializable format
        export_data["data"] = {
            "rows": df.to_dict('records'),
            "columns": list(df.columns),
            "row_count": len(df),
            "column_count": len(df.columns)
        }
    
    return export_data


async def import_dashboard_json(
    db: AsyncSession,
    dashboard_json: Dict,
    dataset_id: Optional[str] = None
) -> Dict:
    """
    Import dashboard from JSON configuration.
    
    Args:
        db: Database session
        dashboard_json: Dashboard JSON data
        dataset_id: Optional dataset ID to use (overrides JSON)
    
    Returns:
        Imported dashboard information
    """
    from database.models import Dashboard
    import uuid
    
    # Use provided dataset_id or from JSON
    target_dataset_id = dataset_id or dashboard_json.get('dataset_id')
    
    if not target_dataset_id:
        raise ValueError("No dataset_id provided")
    
    # Verify dataset exists
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise ValueError(f"Dataset {target_dataset_id} not found")
    
    # Create new dashboard
    new_dashboard = Dashboard(
        id=str(uuid.uuid4()),
        name=dashboard_json.get('name', 'Imported Dashboard'),
        dataset_id=target_dataset_id,
        preset=dashboard_json.get('preset', 'executive'),
        role=dashboard_json.get('role', 'analyst'),
        layout_json=dashboard_json.get('layout', []),
        tiles_json=dashboard_json.get('tiles', []),
        filters_json=dashboard_json.get('filters', [])
    )
    
    db.add(new_dashboard)
    db.commit()
    db.refresh(new_dashboard)
    
    return {
        "dashboard_id": new_dashboard.id,
        "name": new_dashboard.name,
        "dataset_id": new_dashboard.dataset_id,
        "imported_at": datetime.now().isoformat(),
        "success": True
    }


async def export_chart_png(
    chart_data: Dict,
    chart_config: Dict,
    output_path: Optional[str] = None,
    width: int = 800,
    height: int = 600,
    dpi: int = 150
) -> str:
    """
    Export a single chart as PNG image.
    
    Args:
        chart_data: Chart data dictionary (can be empty if data is in config)
        chart_config: Chart configuration (contains data in 'data' field)
        output_path: Optional output file path
        width: Image width in pixels
        height: Image height in pixels
        dpi: Image DPI
    
    Returns:
        Path to saved PNG file or base64 encoded image
    """
    fig, ax = plt.subplots(figsize=(width/dpi, height/dpi), dpi=dpi)
    
    chart_type = chart_config.get('type', 'bar')
    title = chart_config.get('title', 'Chart')
    
    # Extract data from config (new format) or chart_data (old format)
    data_points = chart_config.get('data', [])
    
    # Extract labels and values based on data format
    labels = []
    values = []
    
    if data_points and isinstance(data_points, list) and len(data_points) > 0:
        first_point = data_points[0]
        
        if 'name' in first_point and 'value' in first_point:
            # Pie chart format: [{"name": ..., "value": ...}]
            labels = [str(p.get('name', '')) for p in data_points]
            values = [float(p.get('value', 0)) for p in data_points]
        elif 'x' in first_point and 'y' in first_point:
            # Check if this is a heatmap (has 'value' field and x/y are strings)
            if 'value' in first_point and chart_type == 'heatmap':
                # Heatmap format: [{"x": "col1", "y": "row1", "value": 0.95}]
                # Skip conversion - will be handled separately
                pass
            else:
                # Bar/line/area format: [{"x": ..., "y": ...}]
                try:
                    labels = [str(p.get('x', '')) for p in data_points]
                    values = [float(p.get('y', 0)) for p in data_points]
                except (ValueError, TypeError):
                    # If conversion fails, might be heatmap or other format
                    pass
    else:
        # Fallback to old format
        labels = chart_data.get('labels', [])
        values = chart_data.get('values', [])
    
    # Limit data points for readability
    if len(labels) > 30 and chart_type != 'pie':
        labels = labels[:30]
        values = values[:30]
    elif len(labels) > 15 and chart_type == 'pie':
        labels = labels[:15]
        values = values[:15]
    
    if not labels or not values:
        # Return empty chart
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    else:
        # Render chart based on type
        if chart_type == 'bar':
            ax.bar(labels, values, color='#3B82F6')
            ax.set_xlabel(chart_config.get('x_column', ''))
            ax.set_ylabel(chart_config.get('y_column', ''))
            plt.xticks(rotation=45, ha='right')
        
        elif chart_type == 'line':
            ax.plot(labels, values, marker='o', color='#3B82F6', linewidth=2)
            ax.set_xlabel(chart_config.get('x_column', ''))
            ax.set_ylabel(chart_config.get('y_column', ''))
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45, ha='right')
        
        elif chart_type == 'area':
            ax.fill_between(range(len(values)), values, alpha=0.5, color='#3B82F6')
            ax.plot(range(len(values)), values, color='#1e40af', linewidth=2)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha='right')
            ax.set_xlabel(chart_config.get('x_column', ''))
            ax.set_ylabel(chart_config.get('y_column', ''))
            ax.grid(True, alpha=0.3)
        
        elif chart_type == 'pie':
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
        
        elif chart_type == 'scatter':
            # For scatter, we need x,y pairs
            if data_points and 'x' in data_points[0] and 'y' in data_points[0]:
                x_values = [float(p.get('x', 0)) for p in data_points[:500]]
                y_values = [float(p.get('y', 0)) for p in data_points[:500]]
                ax.scatter(x_values, y_values, color='#3B82F6', s=50, alpha=0.6)
            else:
                x_values = chart_data.get('x_values', labels)
                y_values = chart_data.get('y_values', values)
                ax.scatter(x_values, y_values, color='#3B82F6', s=50, alpha=0.6)
            ax.set_xlabel(chart_config.get('x_column', ''))
            ax.set_ylabel(chart_config.get('y_column', ''))
            ax.grid(True, alpha=0.3)
        
        elif chart_type == 'heatmap':
            # Heatmap format: [{"x": "col1", "y": "row1", "value": 0.95}]
            if data_points and 'x' in data_points[0] and 'y' in data_points[0] and 'value' in data_points[0]:
                # Extract unique x and y labels
                x_labels = sorted(list(set(p.get('x', '') for p in data_points)))
                y_labels = sorted(list(set(p.get('y', '') for p in data_points)))
                
                # Create matrix
                import numpy as np
                matrix = np.zeros((len(y_labels), len(x_labels)))
                
                for point in data_points:
                    x_idx = x_labels.index(point.get('x', ''))
                    y_idx = y_labels.index(point.get('y', ''))
                    matrix[y_idx, x_idx] = float(point.get('value', 0))
                
                # Plot heatmap
                im = ax.imshow(matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
                
                # Set ticks
                ax.set_xticks(range(len(x_labels)))
                ax.set_yticks(range(len(y_labels)))
                ax.set_xticklabels(x_labels, rotation=45, ha='right')
                ax.set_yticklabels(y_labels)
                
                # Add colorbar
                plt.colorbar(im, ax=ax)
                
                # Add values as text
                for i in range(len(y_labels)):
                    for j in range(len(x_labels)):
                        text = ax.text(j, i, f'{matrix[i, j]:.2f}',
                                     ha="center", va="center", color="black", fontsize=8)
            else:
                ax.text(0.5, 0.5, 'Invalid heatmap data', ha='center', va='center')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
        
        elif chart_type == 'histogram':
            # Histogram format: [{"value": ...}]
            if data_points and 'value' in data_points[0]:
                hist_values = [float(p.get('value', 0)) for p in data_points]
                ax.hist(hist_values, bins=30, color='#3B82F6', alpha=0.7, edgecolor='black')
                ax.set_xlabel(chart_config.get('x_column', 'Value'))
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3, axis='y')
            else:
                ax.text(0.5, 0.5, 'Invalid histogram data', ha='center', va='center')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
        
        else:
            # Default to bar
            if labels and values:
                ax.bar(labels, values, color='#3B82F6')
            else:
                ax.text(0.5, 0.5, f'Unsupported chart type: {chart_type}', ha='center', va='center')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    
    # Save or return base64
    if output_path:
        plt.savefig(output_path, format='png', dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        return output_path
    else:
        # Return base64 encoded
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"


async def export_data_csv(
    db: AsyncSession,
    dataset_id: str,
    output_path: Optional[str] = None,
    filters: Optional[Dict] = None
) -> str:
    """
    Export dataset as CSV file.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        output_path: Optional output file path
        filters: Optional filters to apply
    
    Returns:
        Path to saved CSV file or CSV string
    """
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found")
    
    # Load data
    from sqlalchemy import text
    query_sql = f'SELECT * FROM "{dataset.sqlite_table_name}"'
    result = await db.execute(text(query_sql))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    
    # Apply filters if provided
    if filters:
        for column, filter_value in filters.items():
            if column in df.columns:
                if isinstance(filter_value, list):
                    df = df[df[column].isin(filter_value)]
                else:
                    df = df[df[column] == filter_value]
    
    # Export to CSV
    if output_path:
        df.to_csv(output_path, index=False)
        return output_path
    else:
        # Return CSV string
        return df.to_csv(index=False)


async def export_dashboard_bundle(
    db: AsyncSession,
    dashboard_id: str,
    output_dir: str = "data/exports"
) -> Dict:
    """
    Export complete dashboard bundle (JSON + all charts as PNG + data as CSV).
    
    Args:
        db: Database session
        dashboard_id: Dashboard ID
        output_dir: Output directory
    
    Returns:
        Export bundle information
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Get dashboard
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise ValueError(f"Dashboard {dashboard_id} not found")
    
    # Create export directory for this dashboard
    export_id = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dashboard_dir = os.path.join(output_dir, export_id)
    os.makedirs(dashboard_dir, exist_ok=True)
    
    # Export dashboard JSON
    dashboard_json = await export_dashboard_json(db, dashboard_id, include_data=False)
    json_path = os.path.join(dashboard_dir, "dashboard.json")
    with open(json_path, 'w') as f:
        json.dump(dashboard_json, f, indent=2)
    
    # Export all charts as PNG
    chart_paths = []
    tiles = dashboard.tiles_json or []
    chart_tiles = [t for t in tiles if t.get('type') in ['chart', 'bar', 'line', 'area', 'pie', 'scatter', 'histogram', 'heatmap']]
    
    print(f"Found {len(chart_tiles)} chart tiles to export")
    
    for i, chart_tile in enumerate(chart_tiles):
        chart_config = chart_tile.get('config', {})
        chart_title = chart_tile.get('title', f'Chart {i+1}')
        chart_type = chart_config.get('type', 'unknown')
        
        chart_filename = f"chart_{i+1}_{chart_type}.png"
        chart_path = os.path.join(dashboard_dir, chart_filename)
        
        try:
            # Pass empty dict for chart_data since data is in config
            await export_chart_png({}, chart_config, output_path=chart_path)
            chart_paths.append(chart_path)
            print(f"✓ Exported chart {i+1}: {chart_title}")
        except Exception as e:
            print(f"✗ Error exporting chart {i+1} ({chart_title}): {e}")
            import traceback
            traceback.print_exc()
    
    # Export data as CSV
    csv_path = os.path.join(dashboard_dir, "data.csv")
    await export_data_csv(db, dashboard.dataset_id, output_path=csv_path)
    
    # Create manifest file
    manifest = {
        "export_id": export_id,
        "dashboard_id": dashboard_id,
        "dashboard_name": dashboard.name,
        "exported_at": datetime.now().isoformat(),
        "files": {
            "dashboard_json": "dashboard.json",
            "data_csv": "data.csv",
            "charts": [os.path.basename(p) for p in chart_paths]
        },
        "chart_count": len(chart_paths)
    }
    
    manifest_path = os.path.join(dashboard_dir, "manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return {
        "export_id": export_id,
        "export_dir": dashboard_dir,
        "files": {
            "manifest": manifest_path,
            "dashboard_json": json_path,
            "data_csv": csv_path,
            "charts": chart_paths
        },
        "chart_count": len(chart_paths),
        "success": True
    }



