"""
Text-to-SQL Translation Service
Uses LLM to convert natural language to SQL.
"""

import os
import logging
from groq import AsyncGroq

logger = logging.getLogger(__name__)


async def translate_to_sql(
    natural_query: str,
    schema: dict,
    db_type: str = "postgresql",
    retry_count: int = 0
) -> dict:
    """
    Translate natural language to SQL using LLM.
    
    Args:
        natural_query: User's natural language query
        schema: Database schema (tables, columns, types)
        db_type: Database type for dialect-specific SQL
        retry_count: Internal retry counter for validation failures
    
    Returns:
        dict with 'sql' and 'explanation' keys
    """
    try:
        client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Format schema for prompt
        schema_text = ""
        for table, columns in schema.items():
            schema_text += f"\nTable: {table}\n"
            for col in columns:
                schema_text += f"  - {col['name']} ({col['type']})\n"
        
        # Get list of available tables for validation
        available_tables = list(schema.keys())
        tables_list = ", ".join(available_tables) if available_tables else "No tables available"
        
        prompt = f"""You are a SQL expert. Convert this natural language query to {db_type} SQL.

AVAILABLE TABLES (YOU MUST USE ONLY THESE):
{tables_list}

FULL DATABASE SCHEMA:
{schema_text}

Natural Language Query:
{natural_query}

CRITICAL RULES - READ CAREFULLY:
1. You MUST use ONLY these tables: {tables_list}
2. DO NOT use tables named: customers, orders, products, sales, users, employees (unless they appear in the list above)
3. If the query cannot be answered with available tables, explain what tables are missing
4. Generate ONLY SELECT statements - no DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, or TRUNCATE
5. Return ONLY valid JSON: {{"sql": "SELECT ...", "explanation": "..."}}
6. Do not include markdown code blocks
7. If no relevant tables exist for the query, return: {{"sql": "SELECT name FROM sqlite_master WHERE type='table'", "explanation": "No relevant tables found. Showing available tables."}}

Example response format:
{{"sql": "SELECT * FROM actual_table_name WHERE column > 18 LIMIT 10", "explanation": "Description of what the query does"}}

Generate SQL using ONLY tables from this list: {tables_list}"""
        
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Updated to supported model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse as JSON
        import json
        sql = ""
        explanation = ""
        
        try:
            # Try direct JSON parse
            result = json.loads(content)
            sql = result.get("sql", "").strip()
            explanation = result.get("explanation", "")
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
                try:
                    result = json.loads(json_content)
                    sql = result.get("sql", "").strip()
                    explanation = result.get("explanation", "")
                except:
                    pass
            
            # If still no SQL, try to extract from SQL code blocks
            if not sql and "```sql" in content:
                sql_start = content.find("```sql") + 6
                sql_end = content.find("```", sql_start)
                sql = content[sql_start:sql_end].strip()
                explanation = "Query generated from natural language"
            
            # Last resort: use the whole content as SQL
            if not sql:
                sql = content.replace("```", "").strip()
                explanation = "Query generated from natural language"
        
        # Clean up SQL
        sql = sql.strip().rstrip(';')
        
        # Security: Only allow SELECT statements
        sql_upper = sql.upper().strip()
        if not sql_upper.startswith("SELECT"):
            raise ValueError(f"Only SELECT queries are allowed for security reasons. Generated query starts with: {sql[:50]}")
        
        # Remove dangerous keywords
        dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
        for keyword in dangerous:
            if keyword in sql_upper:
                raise ValueError(f"Query contains forbidden keyword: {keyword}")
        
        # Validate that SQL only uses tables from schema
        available_tables = set(schema.keys())
        if available_tables:
            # Extract table names from SQL (simple pattern matching)
            import re
            # Match FROM/JOIN table_name patterns
            table_pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            found_tables = set(re.findall(table_pattern, sql, re.IGNORECASE))
            
            # Check if any table is not in schema
            invalid_tables = found_tables - available_tables
            if invalid_tables:
                available_list = ", ".join(sorted(available_tables))
                
                # Retry once with more explicit prompt
                if retry_count == 0:
                    logger.warning(f"LLM used invalid tables: {invalid_tables}. Retrying with stricter prompt...")
                    corrected_query = f"Using ONLY these tables: {available_list}. {natural_query}"
                    return await translate_to_sql(corrected_query, schema, db_type, retry_count=1)
                
                # If retry also failed, return helpful error
                raise ValueError(
                    f"Cannot answer this query. The question references tables that don't exist ({', '.join(invalid_tables)}). "
                    f"Available tables are: {available_list}. "
                    f"Please rephrase your question using one of the available tables."
                )
        
        return {
            "sql": sql,
            "explanation": explanation
        }
        
    except Exception as e:
        logger.error(f"Text-to-SQL translation failed: {e}")
        raise ValueError(f"Failed to translate query: {str(e)}")
