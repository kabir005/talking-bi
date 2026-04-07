import pandas as pd
import numpy as np
from datetime import datetime
import warnings

# Suppress pandas warnings
warnings.filterwarnings('ignore', message='.*Could not infer format.*')


def infer_column_types(df: pd.DataFrame) -> dict:
    """
    Infer semantic types for each column beyond pandas dtypes.
    Returns dict of {column_name: semantic_type}
    """
    schema = {}
    
    print(f"\n=== SCHEMA DETECTION ===")
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame dtypes:\n{df.dtypes}")
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        unique_count = df[col].nunique()
        total_count = len(df[col])
        sample_values = df[col].dropna().head(10).tolist()
        
        print(f"\nColumn: {col}")
        print(f"  dtype: {dtype}")
        print(f"  unique: {unique_count}/{total_count}")
        print(f"  sample: {sample_values[:3]}")
        
        # Check if it's an ID column (high cardinality, all unique)
        if unique_count == total_count and total_count > 10:
            schema[col] = "identifier"
            print(f"  → identifier")
            continue
        
        # Check for datetime
        if "datetime" in dtype or "date" in dtype.lower():
            schema[col] = "datetime"
            print(f"  → datetime")
            continue
        
        # Try to parse as datetime if object type
        if dtype == "object":
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    pd.to_datetime(df[col].dropna().head(100), errors='raise', format='mixed')
                    schema[col] = "datetime"
                    print(f"  → datetime (parsed)")
                    continue
            except:
                pass
        
        # Check for boolean
        if dtype == "bool" or (dtype == "object" and unique_count <= 2):
            unique_vals = set(str(v).lower() for v in df[col].dropna().unique())
            bool_patterns = [
                {"yes", "no"}, {"y", "n"}, {"true", "false"},
                {"1", "0"}, {"t", "f"}
            ]
            if any(unique_vals.issubset(pattern) for pattern in bool_patterns):
                schema[col] = "boolean"
                print(f"  → boolean")
                continue
        
        # Check for geographic columns
        col_lower = col.lower()
        if any(geo in col_lower for geo in ["country", "state", "city", "region", "location"]):
            schema[col] = "geographic"
            print(f"  → geographic")
            continue
        
        # Numeric types
        if "int" in dtype or "float" in dtype:
            # Check if it's a year column
            if "year" in col_lower and df[col].min() > 1900 and df[col].max() < 2100:
                schema[col] = "year"
                print(f"  → year")
            # Check if it's currency
            elif any(money in col_lower for money in ["revenue", "sales", "price", "cost", "amount", "salary", "profit"]):
                schema[col] = "currency"
                print(f"  → currency")
            # Check if it's a percentage
            elif "percent" in col_lower or "pct" in col_lower or "rate" in col_lower or "discount" in col_lower:
                schema[col] = "percentage"
                print(f"  → percentage")
            else:
                schema[col] = "numeric"
                print(f"  → numeric")
            continue
        
        # Try to convert object to numeric - CRITICAL FIX
        if dtype == "object":
            try:
                # Try to convert to numeric
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                non_null_count = numeric_series.notna().sum()
                
                # If more than 50% can be converted to numeric, treat as numeric (lowered threshold)
                if non_null_count > total_count * 0.5:
                    # Check column name for type hints
                    if any(money in col_lower for money in ["revenue", "sales", "price", "cost", "amount", "salary", "profit"]):
                        schema[col] = "currency"
                        print(f"  → currency (converted from object)")
                    elif "percent" in col_lower or "pct" in col_lower or "rate" in col_lower or "discount" in col_lower:
                        schema[col] = "percentage"
                        print(f"  → percentage (converted from object)")
                    elif "quantity" in col_lower or "count" in col_lower or "number" in col_lower or "qty" in col_lower:
                        schema[col] = "numeric"
                        print(f"  → numeric (converted from object)")
                    else:
                        schema[col] = "numeric"
                        print(f"  → numeric (converted from object)")
                    continue
            except:
                pass
        
        # Categorical
        if dtype == "object" or dtype == "category":
            # Low cardinality = categorical
            if unique_count < total_count * 0.5 and unique_count < 50:
                schema[col] = "categorical"
                print(f"  → categorical")
            else:
                schema[col] = "text"
                print(f"  → text")
            continue
        
        # Default
        schema[col] = "unknown"
        print(f"  → unknown")
    
    print(f"\n=== SCHEMA SUMMARY ===")
    for dtype_name in ["numeric", "currency", "percentage", "categorical", "datetime", "geographic"]:
        cols = [col for col, dtype in schema.items() if dtype == dtype_name]
        if cols:
            print(f"{dtype_name}: {cols}")
    print(f"======================\n")
    
    return schema


def detect_hierarchical_columns(df: pd.DataFrame, schema: dict) -> list:
    """
    Detect if there are hierarchical relationships between categorical columns.
    Returns list of tuples: [(parent_col, child_col), ...]
    """
    hierarchies = []
    categorical_cols = [col for col, dtype in schema.items() if dtype == "categorical"]
    
    for i, parent in enumerate(categorical_cols):
        for child in categorical_cols[i+1:]:
            # Check if each parent value maps to multiple child values
            # but each child value maps to only one parent value
            grouped = df.groupby(parent)[child].nunique()
            reverse_grouped = df.groupby(child)[parent].nunique()
            
            if grouped.mean() > 1 and reverse_grouped.max() == 1:
                hierarchies.append((parent, child))
    
    return hierarchies
