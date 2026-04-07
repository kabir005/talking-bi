"""
Test script to verify data flow from upload → schema detection → chart generation → data aggregation
"""
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.schema_detector import infer_column_types
from agents.chart_agent import recommend_charts
from routers.dashboards import aggregate_chart_data

# Create sample data similar to user's dataset
data = {
    'Ship': ['First Class', 'Second Class', 'First Class', 'Standard Class'] * 25,
    'Mode': ['Air', 'Ground', 'Air', 'Ground'] * 25,
    'Segment': ['Consumer', 'Corporate', 'Consumer', 'Home Office'] * 25,
    'Country': ['USA', 'Canada', 'USA', 'Mexico'] * 25,
    'City': ['New York', 'Toronto', 'Los Angeles', 'Mexico City'] * 25,
    'State': ['NY', 'ON', 'CA', 'MX'] * 25,
    'Region': ['East', 'North', 'West', 'South'] * 25,
    'Category': ['Technology', 'Furniture', 'Office Supplies', 'Technology'] * 25,
    'Sub-Category': ['Phones', 'Chairs', 'Paper', 'Computers'] * 25,
    'Sales': [1000.50, 2500.75, 500.25, 3000.00] * 25,
    'Quantity': [5, 10, 2, 8] * 25,
    'Discount': [0.1, 0.2, 0.0, 0.15] * 25,
    'Profit': [200.10, 500.15, 100.05, 600.00] * 25
}

df = pd.DataFrame(data)

print("=" * 80)
print("TEST 1: DataFrame Creation")
print("=" * 80)
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"Dtypes:\n{df.dtypes}")
print(f"\nSample data:\n{df.head(3)}")

print("\n" + "=" * 80)
print("TEST 2: Schema Detection")
print("=" * 80)

schema = infer_column_types(df)
print(f"\nDetected schema:")
for col, dtype in schema.items():
    print(f"  {col}: {dtype}")

# Count by type
numeric_cols = [col for col, dtype in schema.items() if dtype in ["numeric", "currency", "percentage"]]
categorical_cols = [col for col, dtype in schema.items() if dtype == "categorical"]
print(f"\nNumeric columns: {numeric_cols}")
print(f"Categorical columns: {categorical_cols}")

print("\n" + "=" * 80)
print("TEST 3: Chart Recommendations")
print("=" * 80)

import asyncio

async def test_charts():
    charts = await recommend_charts(df, schema, max_charts=10)
    print(f"\nTotal charts recommended: {len(charts)}")
    
    for i, chart in enumerate(charts[:5]):
        print(f"\nChart {i+1}:")
        print(f"  Type: {chart['type']}")
        print(f"  Title: {chart['title']}")
        print(f"  X: {chart['x_column']}")
        print(f"  Y: {chart['y_column']}")
        print(f"  Aggregation: {chart['aggregation']}")
    
    return charts

charts = asyncio.run(test_charts())

print("\n" + "=" * 80)
print("TEST 4: Data Aggregation")
print("=" * 80)

for i, chart in enumerate(charts[:3]):
    print(f"\nAggregating chart {i+1}: {chart['title']}")
    data_points = aggregate_chart_data(df, chart)
    print(f"  Data points generated: {len(data_points)}")
    if len(data_points) > 0:
        print(f"  Sample data: {data_points[0]}")
        print(f"  ✓ SUCCESS")
    else:
        print(f"  ✗ FAILED - No data generated!")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
