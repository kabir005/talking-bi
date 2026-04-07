"""Intent Classifier
Converts NL query → validated QueryIntent JSON.
Uses Groq (already configured in llm.py) with JSON mode.
Falls back to clarify intent on 2 failed attempts.
IMPORTANT: Uses existing llm.py client, not a new one."""

import json
import re
import logging
from utils.llm import call_llm  # USE EXISTING LLM CLIENT
from models.intent_models import QueryIntent

logger = logging.getLogger(__name__)


def _build_system_prompt(schema: dict) -> str:
    cols = schema.get("columns", {})
    col_lines = []
    for name, info in cols.items():
        typ = info.get("type", "unknown")
        extra = ""
        if typ == "categorical":
            top = list(info.get("top_values", {}).keys())[:5]
            if top:
                extra = f" (values: {', '.join(str(t) for t in top)})"
        elif typ == "numerical":
            mn, mx = info.get("min"), info.get("max")
            if mn is not None and mx is not None:
                extra = f" (range: {mn} to {mx})"
        col_lines.append(f"  - {name}: {typ}{extra}")
    
    col_summary = "\n".join(col_lines)
    time_col = schema.get("primary_time_column") or "none detected"
    kpi_cols = ", ".join(schema.get("kpi_columns", [])) or "none detected"
    
    return f"""You are a data query intent classifier for a Business Intelligence system.

DATASET SCHEMA:
{col_summary}

Primary date/time column: {time_col}
Detected KPI columns: {kpi_cols}

YOUR TASK:
Convert the user's natural language query into a single JSON intent object.

STRICT RULES:
1. Return ONLY valid JSON. No explanation. No markdown. No code blocks.
2. Only reference column names that exist exactly in the schema above.
3. Never generate Python or SQL code — only structured JSON.
4. Column names are case-sensitive.
5. If a column doesn't exist, set op="clarify" with a helpful message.
6. If query is ambiguous, set op="clarify".
7. If user asks time query but no date column exists, set op="no_date_column".

SUPPORTED OPS:
head: {{"op":"head","n":10}}
tail: {{"op":"tail","n":5}}
select: {{"op":"select","columns":["col1","col2"]}}
distinct: {{"op":"distinct","column":"region"}}
sample: {{"op":"sample","n":20}}
filter: {{"op":"filter","column":"revenue","op_type":"gt","value":5000}}
filter_and: {{"op":"filter_and","filters":[{{"column":"c1","op_type":"eq","value":"v1"}},{{"column":"c2","op_type":"gt","value":100}}]}}
filter_or: {{"op":"filter_or","filters":[...]}}
time_filter: {{"op":"time_filter","date_col":"{time_col}","period":"prev_year"}}

TIME PERIODS: prev_year|this_year|this_month|last_month|this_quarter|last_quarter|last_7_days|last_30_days|last_90_days|last_6_months|ytd

sort: {{"op":"sort","column":"revenue","ascending":false}}
topn: {{"op":"topn","column":"revenue","n":10,"ascending":false,"label_col":"product"}}
groupby: {{"op":"groupby","group_col":"region","agg_col":"revenue","agg":"sum"}}
groupby count: {{"op":"groupby","group_col":"region","agg":"count"}}
having: {{"op":"having","group_col":"region","agg_col":"revenue","agg":"sum","op_type":"gt","value":100000}}
resample: {{"op":"resample","date_col":"{time_col}","freq":"ME","agg_col":"revenue","agg":"sum"}}

RESAMPLE FREQ: D=daily|W=weekly|ME=monthly|QE=quarterly|YE=yearly

describe: {{"op":"describe","column":"revenue"}} or {{"op":"describe"}} for all
corr: {{"op":"corr","columns":["revenue","profit"]}}
value_counts: {{"op":"value_counts","column":"region"}}
null_report: {{"op":"null_report"}}
duplicates: {{"op":"duplicates"}}
derive ratio: {{"op":"derive","new_col":"margin","formula":{{"numerator":"profit","denominator":"revenue"}}}}
derive date: {{"op":"derive","new_col":"year","source_col":"{time_col}","extract":"year"}}

EXTRACT: year|month|quarter|day|dayofweek|week

rank: {{"op":"rank","column":"revenue","ascending":false}}
rolling: {{"op":"rolling","column":"revenue","window":7,"agg":"mean","date_col":"{time_col}"}}
cumulative: {{"op":"cumulative","column":"revenue","date_col":"{time_col}"}}
pct_change: {{"op":"pct_change","column":"revenue","date_col":"{time_col}","freq":"ME"}}
pivot: {{"op":"pivot","index":"region","column":"product","agg_col":"revenue","agg":"sum"}}
clarify: {{"op":"clarify","message":"Which column for growth?"}}

EXAMPLES:
"top 5 products by revenue" → {{"op":"topn","column":"revenue","n":5,"ascending":false,"label_col":"product"}}
"previous year data" → {{"op":"time_filter","date_col":"{time_col}","period":"prev_year"}}
"total sales by region" → {{"op":"groupby","group_col":"region","agg_col":"sales","agg":"sum"}}
"monthly revenue trend" → {{"op":"resample","date_col":"{time_col}","freq":"ME","agg_col":"revenue","agg":"sum"}}
"7-day rolling average of revenue" → {{"op":"rolling","column":"revenue","window":7,"agg":"mean","date_col":"{time_col}"}}
"month over month growth" → {{"op":"pct_change","column":"revenue","date_col":"{time_col}","freq":"ME"}}
"""


async def classify_intent(query: str, schema: dict) -> QueryIntent:
    """Convert NL query to QueryIntent. Max 2 LLM attempts. Falls back to clarify.
    Uses existing call_llm() from utils/llm.py."""
    
    system_prompt = _build_system_prompt(schema)
    last_error = None
    
    for attempt in range(2):
        user_msg = query if attempt == 0 else (
            f"Attempt 1 failed: {last_error}. Fix and return ONLY valid JSON. Query: {query}"
        )
        
        try:
            content = await call_llm(
                messages=[{"role": "user", "content": user_msg}],
                system=system_prompt,
                json_mode=True
            )
            
            # Clean markdown code blocks if present
            content = re.sub(r'^```json\s*', '', content, flags=re.MULTILINE)
            content = re.sub(r'```\s*$', '', content, flags=re.MULTILINE)
            
            # Extract JSON object
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if not match:
                raise ValueError("No JSON found in LLM response")
            
            intent_dict = json.loads(match.group())
            return QueryIntent(**intent_dict)
            
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Intent classification attempt {attempt + 1} failed: {e}")
            
            # If it's an API error, don't retry
            if "HTTPStatusError" in str(e) or "RetryError" in str(e):
                logger.error(f"API Error - stopping retries: {e}")
                break
    
    logger.error(f"Classification failed: {last_error}")
    
    # Provide helpful clarify message
    if "HTTPStatusError" in str(last_error) or "RetryError" in str(last_error):
        return QueryIntent(
            op="clarify",
            message="I couldn't understand that. Try: 'top 10 by revenue', 'group by region', 'last 30 days'. (AI service temporarily unavailable)"
        )
    
    return QueryIntent(
        op="clarify",
        message="I couldn't understand that. Try: 'top 10 by revenue', 'group by region', 'last 30 days', 'filter where profit > 0'."
    )
