"""Query Executor — Deterministic, safe pandas execution.
Maps QueryIntent → DataFrame result. Zero code injection risk."""

import pandas as pd
import numpy as np
import logging
from typing import Tuple, Optional
from models.intent_models import QueryIntent, FilterClause

logger = logging.getLogger(__name__)

MAX_RESULT_ROWS = 500
MAX_PIVOT_COLS = 20


def execute(df: pd.DataFrame, intent: QueryIntent, schema: dict) -> Tuple[pd.DataFrame, str]:
    """Main dispatch. Never raises — returns empty df + error message on failure."""
    try:
        return _dispatch(df, intent, schema)
    except Exception as e:
        logger.error(f"Query executor error op={intent.op}: {e}", exc_info=True)
        return pd.DataFrame(), f"Could not execute query: {str(e)}"


def _dispatch(df: pd.DataFrame, intent: QueryIntent, schema: dict) -> Tuple[pd.DataFrame, str]:
    op = intent.op
    
    if op == "clarify":
        return pd.DataFrame(), intent.message or "Please clarify your query."
    
    if op == "no_date_column":
        available = ", ".join(schema.get("numerical_columns", []) + schema.get("categorical_columns", []))
        return pd.DataFrame(), f"No date column found. Available columns: {available}"
    
    if op == "unknown":
        return pd.DataFrame(), "Didn't understand that. Try: 'top 10 by revenue', 'group by region', 'filter where date is last year'."
    
    if op == "head":
        n = max(1, min(intent.n or 10, MAX_RESULT_ROWS))
        return df.head(n), f"First {min(n, len(df))} rows."
    
    if op == "tail":
        n = max(1, min(intent.n or 10, MAX_RESULT_ROWS))
        return df.tail(n), f"Last {min(n, len(df))} rows."
    
    if op == "select":
        valid_cols = [c for c in (intent.columns or []) if c in df.columns]
        missing = [c for c in (intent.columns or []) if c not in df.columns]
        if not valid_cols:
            return pd.DataFrame(), f"None of the requested columns found. Available: {list(df.columns)}"
        r = _cap(df[valid_cols])
        msg = f"Showing {len(valid_cols)} columns, {len(r)} rows."
        if missing:
            msg += f" (Not found: {missing})"
        return r, msg
    
    if op == "distinct":
        col = _require_col(intent.column, df)
        vals = df[col].dropna().unique()
        try: 
            vals = sorted(vals)
        except TypeError: 
            vals = list(vals)
        r = pd.DataFrame({col: vals, "count": [int((df[col] == v).sum()) for v in vals]})
        return r.sort_values("count", ascending=False), f"{len(r)} unique values in '{col}'."
    
    if op == "sample":
        n = max(1, min(intent.n or 20, len(df)))
        return df.sample(n=n, random_state=42), f"Random sample of {n} rows."
    
    if op == "filter":
        r = _single_filter(df, intent.column, intent.op_type, intent.value)
        if len(r) == 0:
            return r, _zero_rows_message(df, intent, schema)
        return _cap(r), f"{len(r):,} rows match your filter."
    
    if op == "filter_and":
        mask = pd.Series([True] * len(df), index=df.index)
        for f in (intent.filters or []):
            sub = _single_filter(df, f.column, f.op_type, f.value)
            mask &= df.index.isin(sub.index)
        r = df[mask]
        if len(r) == 0:
            return r, "No rows match all conditions. Try relaxing one filter."
        return _cap(r), f"{len(r):,} rows match all {len(intent.filters or [])} conditions."
    
    if op == "filter_or":
        mask = pd.Series([False] * len(df), index=df.index)
        for f in (intent.filters or []):
            sub = _single_filter(df, f.column, f.op_type, f.value)
            mask |= df.index.isin(sub.index)
        r = df[mask]
        if len(r) == 0:
            return r, "No rows match any condition."
        return _cap(r), f"{len(r):,} rows match at least one condition."
    
    if op == "time_filter":
        r = _time_filter(df, intent, schema)
        if len(r) == 0:
            return r, _zero_rows_message(df, intent, schema)
        return _cap(r), f"{len(r):,} rows for period '{intent.period}'."
    
    if op == "sort":
        cols = intent.columns or ([intent.column] if intent.column else [])
        if not cols:
            return pd.DataFrame(), "No column specified for sorting."
        valid = [c for c in cols if c in df.columns]
        asc = intent.ascending
        if isinstance(asc, bool):
            asc = [asc] * len(valid)
        r = df.sort_values(valid, ascending=asc)
        direction = "ascending" if (asc[0] if isinstance(asc, list) else asc) else "descending"
        return _cap(r), f"Sorted by {valid} ({direction})."
    
    if op == "topn":
        col = _require_col(intent.column, df)
        n = max(1, min(intent.n or 10, len(df)))
        asc = intent.ascending if intent.ascending is not None else False
        r = df.nsmallest(n, col) if asc else df.nlargest(n, col)
        return r, f"{'Bottom' if asc else 'Top'} {len(r)} by '{col}'."
    
    if op == "groupby":
        return _exec_groupby(df, intent)
    
    if op == "having":
        return _exec_having(df, intent)
    
    if op == "resample":
        return _exec_resample(df, intent, schema)
    
    if op == "describe":
        col = intent.column
        if col and col in df.columns:
            stats = df[col].describe()
            r = pd.DataFrame({"statistic": stats.index, "value": stats.values.round(4)})
        else:
            stats = df.describe(numeric_only=True)
            r = stats.reset_index().rename(columns={"index": "statistic"})
        return r, f"Stats for '{col or 'all numeric columns'}'."
    
    if op == "corr":
        cols = intent.columns
        valid = [c for c in cols if c in df.columns] if cols else list(df.select_dtypes(include="number").columns)
        if len(valid) < 2:
            return pd.DataFrame(), f"Need ≥2 numeric columns. Found: {valid}"
        r = df[valid].corr(numeric_only=True).round(3).reset_index().rename(columns={"index": "column"})
        return r, f"Pearson correlation for {len(valid)} columns."
    
    if op == "value_counts":
        col = _require_col(intent.column, df)
        r = df[col].value_counts().reset_index()
        r.columns = [col, "count"]
        r["percentage"] = (r["count"] / r["count"].sum() * 100).round(1)
        return r, f"{len(r)} unique values in '{col}'."
    
    if op == "null_report":
        null_counts = df.isnull().sum()
        r = pd.DataFrame({
            "column": null_counts.index,
            "null_count": null_counts.values,
            "null_pct": (null_counts.values / len(df) * 100).round(1),
            "dtype": [str(df[c].dtype) for c in null_counts.index]
        })
        r = r[r["null_count"] > 0].sort_values("null_count", ascending=False)
        if len(r) == 0:
            return r, "No missing values — dataset is complete."
        return r, f"{len(r)} columns have missing values."
    
    if op == "duplicates":
        r = df[df.duplicated(keep=False)]
        if len(r) == 0:
            return r, "No duplicate rows found."
        return _cap(r.sort_index()), f"{len(r):,} duplicate rows found."
    
    if op == "derive":
        return _exec_derive(df, intent)
    
    if op == "rank":
        col = _require_col(intent.column, df)
        asc = intent.ascending if intent.ascending is not None else False
        result = df.copy()
        rank_col = f"{col}_rank"
        result[rank_col] = result[col].rank(ascending=asc, method="dense").astype(int)
        return _cap(result.sort_values(rank_col)), f"Ranked {len(result):,} rows by '{col}'."
    
    if op == "rolling":
        return _exec_rolling(df, intent, schema)
    
    if op == "cumulative":
        return _exec_cumulative(df, intent, schema)
    
    if op == "pct_change":
        return _exec_pct_change(df, intent, schema)
    
    if op == "pivot":
        return _exec_pivot(df, intent)
    
    return pd.DataFrame(), f"Operation '{op}' not yet implemented."


# ── HELPERS ────────────────────────────────────────────────────────────────

def _require_col(col: Optional[str], df: pd.DataFrame) -> str:
    if not col:
        raise ValueError("No column specified.")
    if col not in df.columns:
        similar = [c for c in df.columns if col.lower() in c.lower() or c.lower() in col.lower()]
        msg = f"Column '{col}' not found."
        if similar:
            msg += f" Did you mean: {similar}?"
        else:
            msg += f" Available: {list(df.columns)}"
        raise ValueError(msg)
    return col


def _cap(df: pd.DataFrame) -> pd.DataFrame:
    return df.head(MAX_RESULT_ROWS)


def _ensure_datetime(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df[col]):
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _single_filter(df: pd.DataFrame, col: str, op_type: str, value) -> pd.DataFrame:
    col = _require_col(col, df)
    s = df[col]
    
    ops = {
        "eq": s == value,
        "ne": s != value,
        "gt": s > value,
        "lt": s < value,
        "gte": s >= value,
        "lte": s <= value,
        "in": s.isin(value if isinstance(value, list) else [value]),
        "between": s.between(value[0], value[1]) if isinstance(value, list) and len(value) == 2 else pd.Series([True]*len(df), index=df.index),
        "contains": s.astype(str).str.contains(str(value), case=False, na=False),
        "startswith": s.astype(str).str.startswith(str(value), na=False),
        "endswith": s.astype(str).str.endswith(str(value), na=False),
        "isnull": s.isnull(),
        "notnull": s.notna(),
    }
    
    mask = ops.get(op_type, pd.Series([True]*len(df), index=df.index))
    return df[mask]


def _time_filter(df: pd.DataFrame, intent: QueryIntent, schema: dict) -> pd.DataFrame:
    col = intent.date_col or schema.get("primary_time_column")
    if not col or col not in df.columns:
        raise ValueError(f"Date column '{col}' not found.")
    
    df = _ensure_datetime(df, col)
    now = pd.Timestamp.now()
    cur_year, cur_month, cur_quarter = now.year, now.month, (now.month - 1) // 3 + 1
    
    period_masks = {
        "prev_year": df[col].dt.year == cur_year - 1,
        "this_year": df[col].dt.year == cur_year,
        "this_month": (df[col].dt.year == cur_year) & (df[col].dt.month == cur_month),
        "last_month": (df[col].dt.year == (cur_year if cur_month > 1 else cur_year-1)) & (df[col].dt.month == (cur_month-1 if cur_month > 1 else 12)),
        "this_quarter": df[col].dt.quarter == cur_quarter,
        "last_quarter": df[col].dt.quarter == (cur_quarter-1 if cur_quarter > 1 else 4),
        "last_7_days": df[col] >= now - pd.Timedelta(days=7),
        "last_30_days": df[col] >= now - pd.Timedelta(days=30),
        "last_90_days": df[col] >= now - pd.Timedelta(days=90),
        "last_6_months": df[col] >= now - pd.Timedelta(days=180),
        "ytd": (df[col].dt.year == cur_year) & (df[col] <= now),
    }
    
    mask = period_masks.get(intent.period, pd.Series([True]*len(df), index=df.index))
    return df[mask]


def _zero_rows_message(df: pd.DataFrame, intent: QueryIntent, schema: dict) -> str:
    if intent.op == "time_filter":
        col = intent.date_col or schema.get("primary_time_column")
        if col and col in df.columns:
            try:
                df_temp = _ensure_datetime(df, col)
                dates = df_temp[col].dropna()
                if len(dates) > 0:
                    return f"No data for '{intent.period}'. Dataset spans {dates.min().date()} to {dates.max().date()}."
            except Exception:
                pass
    return "No rows match this filter. Try relaxing the conditions."


def _exec_groupby(df: pd.DataFrame, intent: QueryIntent) -> Tuple[pd.DataFrame, str]:
    g_col = intent.group_col
    a_col = intent.agg_col
    agg = intent.agg or "sum"
    
    if not g_col:
        return pd.DataFrame(), "No group column specified."
    
    valid_g = [g_col] if isinstance(g_col, str) and g_col in df.columns else (
        [c for c in g_col if c in df.columns] if isinstance(g_col, list) else []
    )
    if not valid_g:
        return pd.DataFrame(), f"Group column '{g_col}' not found."
    
    if agg == "count" or not a_col:
        r = df.groupby(valid_g).size().reset_index(name="count")
        return r, f"Row count grouped by {valid_g}. {len(r)} groups."
    
    if isinstance(a_col, list):
        valid_a = [c for c in a_col if c in df.columns]
        r = df.groupby(valid_g)[valid_a].agg(agg).reset_index()
    else:
        if a_col not in df.columns:
            return pd.DataFrame(), f"Aggregation column '{a_col}' not found."
        r = df.groupby(valid_g)[a_col].agg(agg).reset_index()
    
    return r, f"{agg.title()} of '{a_col}' grouped by {valid_g}. {len(r)} groups."


def _exec_having(df: pd.DataFrame, intent: QueryIntent) -> Tuple[pd.DataFrame, str]:
    grouped, msg = _exec_groupby(df, intent)
    if grouped.empty:
        return grouped, msg
    
    a_col = intent.agg_col if isinstance(intent.agg_col, str) else (intent.agg_col or [None])[0]
    if not a_col or a_col not in grouped.columns:
        return grouped, msg
    
    filtered = _single_filter(grouped, a_col, intent.op_type, intent.value)
    return filtered, f"{len(filtered)} groups where {intent.agg}({a_col}) {intent.op_type} {intent.value}."


def _exec_resample(df: pd.DataFrame, intent: QueryIntent, schema: dict) -> Tuple[pd.DataFrame, str]:
    d_col = intent.date_col or schema.get("primary_time_column")
    if not d_col or d_col not in df.columns:
        return pd.DataFrame(), f"Date column '{d_col}' not found."
    
    if not intent.agg_col or intent.agg_col not in df.columns:
        return pd.DataFrame(), f"Aggregation column '{intent.agg_col}' not found."
    
    df = _ensure_datetime(df, d_col)
    r = df.set_index(d_col)[intent.agg_col].resample(intent.freq or "ME").agg(intent.agg or "sum").reset_index()
    r.columns = [d_col, intent.agg_col]
    
    freq_labels = {"D": "daily", "W": "weekly", "ME": "monthly", "QE": "quarterly", "YE": "yearly"}
    return r, f"{freq_labels.get(intent.freq or 'ME', intent.freq).title()} {intent.agg} of '{intent.agg_col}'. {len(r)} periods."


def _exec_derive(df: pd.DataFrame, intent: QueryIntent) -> Tuple[pd.DataFrame, str]:
    result = df.copy()
    new_col = intent.new_col or "derived"
    
    if intent.extract and intent.source_col:
        src = _require_col(intent.source_col, df)
        result = _ensure_datetime(result, src)
        result[new_col] = getattr(result[src].dt, intent.extract)
        return _cap(result), f"Added '{new_col}' (extracted {intent.extract} from '{src}')."
    
    if intent.formula:
        f = intent.formula
        if f.numerator and f.denominator:
            num = _require_col(f.numerator, df)
            den = _require_col(f.denominator, df)
            result[new_col] = (result[num] / result[den].replace(0, np.nan)).round(4)
            return _cap(result), f"Added '{new_col}' = {num} / {den}."
        
        if f.operand_a and f.operand_b and f.operation:
            a = _require_col(f.operand_a, df)
            b = _require_col(f.operand_b, df)
            ops_map = {
                "add": result[a]+result[b], 
                "subtract": result[a]-result[b], 
                "multiply": result[a]*result[b], 
                "divide": result[a]/result[b].replace(0, np.nan)
            }
            result[new_col] = ops_map.get(f.operation, result[a])
            return _cap(result), f"Added '{new_col}' = {a} {f.operation} {b}."
    
    return _cap(result), f"Column '{new_col}' added."


def _exec_rolling(df: pd.DataFrame, intent: QueryIntent, schema: dict) -> Tuple[pd.DataFrame, str]:
    d_col = intent.date_col or schema.get("primary_time_column")
    col = _require_col(intent.column, df)
    window = intent.window or 7
    agg = intent.agg or "mean"
    
    if window > len(df):
        return pd.DataFrame(), f"Window ({window}) is larger than dataset ({len(df)} rows)."
    
    if d_col and d_col in df.columns:
        df = _ensure_datetime(df, d_col)
        temp = df.sort_values(d_col).copy()
        rolled = temp.set_index(d_col)[col].rolling(window).agg(agg).dropna().reset_index()
        rolled.columns = [d_col, f"{col}_{window}p_{agg}"]
        return rolled, f"{window}-period rolling {agg} of '{col}'. {len(rolled)} points."
    
    result = df.copy()
    result[f"{col}_{window}p_{agg}"] = result[col].rolling(window).agg(agg)
    return _cap(result.dropna(subset=[f"{col}_{window}p_{agg}"])), f"{window}-period rolling {agg} of '{col}'."


def _exec_cumulative(df: pd.DataFrame, intent: QueryIntent, schema: dict) -> Tuple[pd.DataFrame, str]:
    d_col = intent.date_col or schema.get("primary_time_column")
    col = _require_col(intent.column, df)
    
    if d_col and d_col in df.columns:
        df = _ensure_datetime(df, d_col)
        temp = df.sort_values(d_col).copy()
        temp[f"{col}_cumulative"] = temp[col].cumsum()
        return _cap(temp[[d_col, col, f"{col}_cumulative"]]), f"Cumulative {col} over time."
    
    result = df.copy()
    result[f"{col}_cumulative"] = result[col].cumsum()
    return _cap(result), f"Cumulative sum of '{col}'."


def _exec_pct_change(df: pd.DataFrame, intent: QueryIntent, schema: dict) -> Tuple[pd.DataFrame, str]:
    d_col = intent.date_col or schema.get("primary_time_column")
    col = _require_col(intent.column, df)
    
    if not d_col or d_col not in df.columns:
        return pd.DataFrame(), "Date column not found for period change."
    
    df = _ensure_datetime(df, d_col)
    freq = intent.freq or "ME"
    resampled = df.set_index(d_col)[col].resample(freq).sum()
    changes = resampled.pct_change().mul(100).round(2).dropna()
    r = changes.reset_index()
    r.columns = [d_col, "pct_change"]
    r["direction"] = r["pct_change"].apply(lambda x: "up" if x > 0 else "down" if x < 0 else "flat")
    
    freq_labels = {"D": "daily", "W": "weekly", "ME": "monthly", "QE": "quarterly", "YE": "yearly"}
    return r, f"{freq_labels.get(freq, freq).title()} % change for '{col}'. {len(r)} periods."


def _exec_pivot(df: pd.DataFrame, intent: QueryIntent) -> Tuple[pd.DataFrame, str]:
    idx = intent.index or intent.group_col
    cols_field = intent.column
    vals = intent.agg_col
    
    if not idx or idx not in df.columns:
        return pd.DataFrame(), f"Index column '{idx}' not found."
    
    if not cols_field or cols_field not in df.columns:
        return pd.DataFrame(), f"Column field '{cols_field}' not found."
    
    pivot = df.pivot_table(index=idx, columns=cols_field, values=vals, aggfunc=intent.agg or "sum", fill_value=0)
    
    if len(pivot.columns) > MAX_PIVOT_COLS:
        pivot = pivot[pivot.sum().nlargest(MAX_PIVOT_COLS).index]
    
    r = pivot.reset_index()
    r.columns = [str(c) for c in r.columns]
    return r, f"Pivot: {idx} × {cols_field} ({intent.agg} of '{vals}'). {len(r)} rows."
