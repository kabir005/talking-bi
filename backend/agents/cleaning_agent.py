import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from typing import Dict, List, Tuple
from utils.stats_utils import detect_outliers_iqr, detect_outliers_zscore
import warnings

# Suppress pandas warnings (SettingWithCopyWarning removed in pandas 2.2+)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*Could not infer format.*')
warnings.filterwarnings('ignore', message='.*match groups.*')


async def run_cleaning(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Fully autonomous data cleaning with human-readable audit log.
    Returns: (cleaned_df, cleaning_report)
    """
    # Make a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    cleaning_log = []
    high_missingness_columns = []
    near_duplicates = []
    all_outlier_rows = set()
    
    original_shape = df.shape
    
    # 1. Handle missing values
    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count == 0:
            continue
        
        missing_pct = (missing_count / len(df)) * 100
        
        # Flag high missingness
        if missing_pct > 40:
            high_missingness_columns.append(col)
            cleaning_log.append({
                "action": "flag_high_missingness",
                "column": col,
                "pct_missing": round(missing_pct, 2),
                "recommendation": "Consider dropping this column"
            })
            continue
        
        # Fill based on dtype
        if pd.api.types.is_numeric_dtype(df[col]):
            fill_value = df[col].median()
            df[col] = df[col].fillna(fill_value)
            cleaning_log.append({
                "action": "fill_missing",
                "column": col,
                "method": "median",
                "rows_affected": int(missing_count),
                "value_used": float(fill_value) if not pd.isna(fill_value) else None,
                "pct_affected": round(missing_pct, 2)
            })
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].ffill().bfill()
            cleaning_log.append({
                "action": "fill_missing",
                "column": col,
                "method": "forward_fill",
                "rows_affected": int(missing_count),
                "pct_affected": round(missing_pct, 2)
            })
        else:
            # Categorical - fill with mode
            mode_value = df[col].mode()
            if len(mode_value) > 0:
                df[col] = df[col].fillna(mode_value[0])
                cleaning_log.append({
                    "action": "fill_missing",
                    "column": col,
                    "method": "mode",
                    "rows_affected": int(missing_count),
                    "value_used": str(mode_value[0]),
                    "pct_affected": round(missing_pct, 2)
                })
    
    # 2. Remove exact duplicates
    duplicates_before = len(df)
    df = df.drop_duplicates()
    duplicates_removed = duplicates_before - len(df)
    if duplicates_removed > 0:
        cleaning_log.append({
            "action": "remove_duplicates",
            "rows_removed": int(duplicates_removed)
        })
    
    # 3. Detect near-duplicates (on string columns only, for review)
    string_cols = df.select_dtypes(include=['object']).columns
    if len(string_cols) > 0 and len(df) < 10000:  # Only for smaller datasets
        # Check first string column for near-duplicates
        col = string_cols[0]
        unique_vals = df[col].dropna().unique()
        if len(unique_vals) < 1000:
            for i, val1 in enumerate(unique_vals):
                for val2 in unique_vals[i+1:]:
                    ratio = fuzz.ratio(str(val1), str(val2))
                    if ratio > 95 and ratio < 100:
                        near_duplicates.append({
                            "column": col,
                            "value1": str(val1),
                            "value2": str(val2),
                            "similarity": ratio
                        })
                        if len(near_duplicates) >= 10:
                            break
                if len(near_duplicates) >= 10:
                    break
    
    # 4. Fix data types
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to detect and fix numeric strings
            sample = df[col].dropna().head(100)
            if len(sample) > 0:
                # Check for currency symbols
                try:
                    if sample.astype(str).str.contains(r'[$₹€£¥]', regex=True).any():
                        cleaned = df[col].astype(str).str.replace(r'[$₹€£¥,]', '', regex=True)
                        df[col] = pd.to_numeric(cleaned, errors='coerce')
                        cleaning_log.append({
                            "action": "fix_dtype",
                            "column": col,
                            "from": "object",
                            "to": "float64",
                            "note": "Removed currency symbols"
                        })
                        continue
                except:
                    pass
                
                # Check for comma-separated numbers (non-capturing groups)
                try:
                    if sample.astype(str).str.contains(r'^\d{1,3}(?:,\d{3})*(?:\.\d+)?$', regex=True).any():
                        cleaned = df[col].astype(str).str.replace(',', '')
                        df[col] = pd.to_numeric(cleaned, errors='coerce')
                        cleaning_log.append({
                            "action": "fix_dtype",
                            "column": col,
                            "from": "object",
                            "to": "float64",
                            "note": "Removed thousand separators"
                        })
                        continue
                except:
                    pass
                
                # Try to parse as datetime
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        parsed = pd.to_datetime(df[col], errors='coerce', format='mixed')
                        if parsed.notna().sum() > len(df) * 0.8:  # If >80% successfully parsed
                            df[col] = parsed
                            cleaning_log.append({
                                "action": "fix_dtype",
                                "column": col,
                                "from": "object",
                                "to": "datetime64"
                            })
                            continue
                except:
                    pass
                
                # Try to convert to numeric (even without special characters)
                try:
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    non_null_count = numeric_series.notna().sum()
                    
                    # If more than 80% can be converted, treat as numeric
                    if non_null_count > len(df) * 0.8:
                        df[col] = numeric_series
                        cleaning_log.append({
                            "action": "fix_dtype",
                            "column": col,
                            "from": "object",
                            "to": "float64",
                            "note": "Converted string numbers to numeric"
                        })
                        continue
                except:
                    pass
                
                # Check for boolean strings
                try:
                    unique_lower = set(df[col].dropna().astype(str).str.lower().unique())
                    bool_patterns = [
                        {"yes", "no"}, {"y", "n"}, {"true", "false"},
                        {"1", "0"}, {"t", "f"}
                    ]
                    for pattern in bool_patterns:
                        if unique_lower.issubset(pattern):
                            pattern_list = list(pattern)
                            df[col] = df[col].astype(str).str.lower().map({
                                pattern_list[0]: True,
                                pattern_list[1]: False
                            })
                            cleaning_log.append({
                                "action": "fix_dtype",
                                "column": col,
                                "from": "object",
                                "to": "boolean"
                            })
                            break
                except:
                    pass
    
    # 5. Detect outliers (flag only, don't remove)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if len(df[col].dropna()) < 10:
            continue
        
        try:
            # IQR method
            outlier_indices_iqr, outlier_info_iqr = detect_outliers_iqr(df[col])
            
            # Z-score method
            outlier_indices_z, outlier_info_z = detect_outliers_zscore(df[col])
            
            # Combine both methods
            combined_outliers = set(outlier_indices_iqr + outlier_indices_z)
            
            if len(combined_outliers) > 0:
                all_outlier_rows.update(combined_outliers)
                outlier_sample = df.loc[list(combined_outliers)[:5], col].tolist()
                cleaning_log.append({
                    "action": "outlier_flagged",
                    "column": col,
                    "count": len(combined_outliers),
                    "method": "IQR + Z-score",
                    "sample_values": [float(v) if not pd.isna(v) else None for v in outlier_sample]
                })
        except:
            pass
    
    # Add outlier flag column
    df['_is_outlier'] = False
    if len(all_outlier_rows) > 0:
        df.loc[list(all_outlier_rows), '_is_outlier'] = True
    
    # 6. Detect ID columns (high cardinality, all unique)
    for col in df.columns:
        if col != '_is_outlier' and df[col].nunique() == len(df) and len(df) > 10:
            cleaning_log.append({
                "action": "flag_id_column",
                "column": col,
                "note": "All values unique - likely an identifier column"
            })
    
    cleaning_report = {
        "cleaning_log": cleaning_log,
        "high_missingness_columns": high_missingness_columns,
        "near_duplicates": near_duplicates[:10],  # First 10 only
        "outlier_rows": list(all_outlier_rows)[:100],  # First 100 only
        "original_shape": original_shape,
        "final_shape": df.shape,
        "total_changes": len(cleaning_log)
    }
    
    return df, cleaning_report
