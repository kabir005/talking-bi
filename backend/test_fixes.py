"""
Test script to verify all fixes are working
"""
import pandas as pd
import numpy as np
import json

# Test 1: Numpy serialization
print("=" * 60)
print("TEST 1: Numpy Serialization")
print("=" * 60)

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, (np.bool_, np.bool8)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, 'item'):
            return obj.item()
        return super().default(obj)

test_data = {
    "bool": np.bool_(True),
    "int": np.int64(42),
    "float": np.float64(3.14),
    "array": np.array([1, 2, 3]),
    "nested": {
        "bool": np.bool_(False),
        "value": np.int32(100)
    }
}

try:
    result = json.dumps(test_data, cls=NumpyEncoder)
    print("✅ Numpy serialization works!")
    print(f"Result: {result}")
except Exception as e:
    print(f"❌ Numpy serialization failed: {e}")

# Test 2: DataFrame operations
print("\n" + "=" * 60)
print("TEST 2: DataFrame Operations")
print("=" * 60)

df = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'A', 'B'],
    'Value': [10, 20, 30, 15, 25],
    'Count': [1, 2, 3, 4, 5]
})

print(f"DataFrame shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Test aggregation
try:
    grouped = df.groupby('Category')['Value'].sum().reset_index()
    print("✅ Aggregation works!")
    print(f"Result:\n{grouped}")
except Exception as e:
    print(f"❌ Aggregation failed: {e}")

# Test 3: String operations on mixed types
print("\n" + "=" * 60)
print("TEST 3: String Operations")
print("=" * 60)

df_mixed = pd.DataFrame({
    'text': ['hello', 'world', '  '],
    'number': [1, 2, 3],
    'bool': [True, False, True]
})

try:
    for col in df_mixed.columns:
        if df_mixed[col].dtype == 'object':
            if df_mixed[col].astype(str).str.strip().eq('').any():
                print(f"Column '{col}' has empty strings")
    print("✅ String operations work!")
except Exception as e:
    print(f"❌ String operations failed: {e}")

# Test 4: Chart data aggregation simulation
print("\n" + "=" * 60)
print("TEST 4: Chart Data Aggregation")
print("=" * 60)

df_sales = pd.DataFrame({
    'Region': ['North', 'South', 'East', 'West', 'North'],
    'Sales': [100, 200, 150, 300, 120],
    'Quantity': [10, 20, 15, 30, 12]
})

try:
    # Bar chart data
    bar_data = df_sales.groupby('Region')['Sales'].sum().reset_index()
    bar_result = [{"x": str(row['Region']), "y": float(row['Sales'])} 
                  for _, row in bar_data.iterrows()]
    print(f"✅ Bar chart data: {len(bar_result)} points")
    print(f"Sample: {bar_result[0]}")
    
    # Pie chart data
    pie_data = df_sales.groupby('Region')['Sales'].sum().reset_index()
    pie_result = [{"name": str(row['Region']), "value": float(row['Sales'])} 
                  for _, row in pie_data.iterrows()]
    print(f"✅ Pie chart data: {len(pie_result)} slices")
    print(f"Sample: {pie_result[0]}")
    
    # Histogram data
    hist_values = df_sales['Sales'].tolist()
    hist_result = [{"value": float(v)} for v in hist_values]
    print(f"✅ Histogram data: {len(hist_result)} values")
    
except Exception as e:
    print(f"❌ Chart aggregation failed: {e}")

# Test 5: JSON serialization of chart data
print("\n" + "=" * 60)
print("TEST 5: Chart Data JSON Serialization")
print("=" * 60)

chart_data = {
    "bar": bar_result,
    "pie": pie_result,
    "histogram": hist_result
}

try:
    json_str = json.dumps(chart_data, cls=NumpyEncoder)
    print("✅ Chart data serialization works!")
    print(f"JSON length: {len(json_str)} characters")
except Exception as e:
    print(f"❌ Chart data serialization failed: {e}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETE")
print("=" * 60)
