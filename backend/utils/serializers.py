import pandas as pd
import numpy as np
import json
from datetime import datetime, date


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif pd.isna(obj):
            return None
        return super().default(obj)


def dataframe_to_dict(df: pd.DataFrame, max_rows: int = None) -> dict:
    """Convert DataFrame to JSON-serializable dict"""
    # Make a copy to avoid modifying the original
    df_copy = df.copy()
    
    if max_rows:
        df_copy = df_copy.head(max_rows)
    
    # Convert datetime columns to string
    for col in df_copy.select_dtypes(include=['datetime64']).columns:
        df_copy[col] = df_copy[col].astype(str)
    
    # Replace NaN with None
    df_copy = df_copy.replace({np.nan: None})
    
    return {
        "columns": df_copy.columns.tolist(),
        "data": df_copy.to_dict(orient='records')
    }


def series_to_list(series: pd.Series) -> list:
    """Convert pandas Series to JSON-serializable list"""
    return [None if pd.isna(x) else x for x in series.tolist()]
