"""QueryIntent — Pydantic model for validated NL query intents.
The LLM returns JSON matching this schema. Never raw Python code.
SAFE EXECUTION: No eval(), no exec(), deterministic pandas only."""

from pydantic import BaseModel, field_validator
from typing import Optional, List, Union, Literal, Dict, Any

ALLOWED_AGG = {"sum", "mean", "count", "min", "max", "std", "median", "nunique", "first", "last"}
ALLOWED_OP_TYPES = {"eq", "ne", "gt", "lt", "gte", "lte",
                    "in", "between", "contains", "startswith",
                    "endswith", "isnull", "notnull"}
ALLOWED_OPS = {"head", "tail", "select", "distinct", "sample",
               "filter", "filter_and", "filter_or",
               "sort", "topn",
               "groupby", "having",
               "describe", "corr", "value_counts", "null_report", "duplicates",
               "derive", "rank",
               "rolling", "cumulative", "pct_change",
               "pivot", "resample",
               "time_filter",
               "clarify", "no_date_column", "unknown"}
ALLOWED_PERIODS = {"prev_year", "this_year",
                   "this_month", "last_month",
                   "this_quarter", "last_quarter",
                   "last_7_days", "last_30_days", "last_90_days", "last_6_months",
                   "ytd"}
ALLOWED_FREQS = {"D", "W", "ME", "QE", "YE", "h"}
ALLOWED_EXTRACTS = {"year", "month", "quarter", "day", "dayofweek", "week", "hour"}


class FilterClause(BaseModel):
    column: str
    op_type: str
    value: Optional[Union[str, int, float, List[Union[str, int, float]]]] = None

    @field_validator("op_type")
    def valid_op_type(cls, v):
        if v not in ALLOWED_OP_TYPES:
            raise ValueError(f"op_type must be one of {ALLOWED_OP_TYPES}")
        return v


class DeriveFormula(BaseModel):
    numerator: Optional[str] = None
    denominator: Optional[str] = None
    operand_a: Optional[str] = None
    operand_b: Optional[str] = None
    operation: Optional[str] = None  # "add", "subtract", "multiply", "divide"


class QueryIntent(BaseModel):
    op: str
    column: Optional[str] = None
    columns: Optional[List[str]] = None
    label_col: Optional[str] = None
    n: Optional[int] = 10
    ascending: Optional[Union[bool, List[bool]]] = True
    group_col: Optional[Union[str, List[str]]] = None
    agg_col: Optional[Union[str, List[str]]] = None
    agg: Optional[str] = "sum"
    op_type: Optional[str] = None
    value: Optional[Union[str, int, float, List[Any]]] = None
    filters: Optional[List[FilterClause]] = None
    date_col: Optional[str] = None
    period: Optional[str] = None
    freq: Optional[str] = "ME"
    window: Optional[int] = 7
    new_col: Optional[str] = None
    source_col: Optional[str] = None
    extract: Optional[str] = None
    formula: Optional[DeriveFormula] = None
    index: Optional[str] = None
    message: Optional[str] = None

    @field_validator("op")
    def valid_op(cls, v):
        if v not in ALLOWED_OPS:
            return "unknown"
        return v

    @field_validator("agg")
    def valid_agg(cls, v):
        if v and v not in ALLOWED_AGG:
            raise ValueError(f"agg must be one of {ALLOWED_AGG}")
        return v

    @field_validator("period")
    def valid_period(cls, v):
        if v and v not in ALLOWED_PERIODS:
            raise ValueError(f"period must be one of {ALLOWED_PERIODS}")
        return v

    @field_validator("freq")
    def valid_freq(cls, v):
        if v and v not in ALLOWED_FREQS:
            return "ME"
        return v

    @field_validator("extract")
    def valid_extract(cls, v):
        if v and v not in ALLOWED_EXTRACTS:
            raise ValueError(f"extract must be one of {ALLOWED_EXTRACTS}")
        return v
