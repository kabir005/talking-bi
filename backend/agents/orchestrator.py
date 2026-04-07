import asyncio
import json
from typing import Dict, List
from utils.llm import call_llm
from agents.cleaning_agent import run_cleaning
from agents.analyst_agent import run_analysis
from agents.critic_agent import run_critic_validation
from agents.chart_agent import recommend_charts
from agents.insight_agent import generate_insights
from agents.strategist_agent import generate_recommendations
from agents.root_cause_agent import run_root_cause_analysis
from agents.insight_eval_agent import validate_insights, deduplicate_insights
from services.rag_service import index_dataset
import pandas as pd
import logging

logger = logging.getLogger(__name__)


async def run_orchestrator(
    df: pd.DataFrame,
    dataset_schema: Dict[str, str],
    dataset_sample: List[Dict],
    user_prompt: str,
    user_role: str = "default",
    memory_context: List[Dict] = None
) -> Dict:
    """
    Master orchestrator agent that plans and coordinates all other agents.
    Returns comprehensive analysis plan and results.
    """
    
    # Build context for LLM
    schema_str = "\n".join([f"- {col}: {dtype}" for col, dtype in dataset_schema.items()])
    sample_str = json.dumps(dataset_sample[:5], indent=2)
    memory_str = ""
    
    if memory_context:
        memory_str = "\n\nPast similar queries:\n"
        for mem in memory_context[:3]:
            memory_str += f"- {mem.get('query', '')}\n"
    
    system_prompt = """You are the Orchestrator Agent for an agentic BI platform. 
Given a dataset schema, sample data, user prompt, and role, produce a JSON plan.

The plan MUST contain:
{
  "intent": "descriptive string of what user wants",
  "kpis": ["list of column names to compute KPIs for"],
  "chart_configs": [
    {
      "type": "line|bar|area|pie|scatter|heatmap|histogram|waterfall|treemap|map",
      "x_column": "column name",
      "y_column": "column name or null",
      "aggregation": "sum|mean|count|median|max|min",
      "title": "human readable title",
      "color_by": "column name or null",
      "filters": []
    }
  ],
  "preset": "executive|operational|trend|comparison",
  "role_filter": "which columns/charts to hide for this role",
  "questions_for_analyst": ["what trends to detect", "what anomalies to look for"],
  "questions_for_strategist": ["what recommendations to generate"],
  "ml_target": "column name if user asked for prediction, else null",
  "what_if_column": "column name for simulation, else null",
  "root_cause_target": "metric to explain drop/rise, else null",
  "knowledge_graph": true or false
}

Be specific and actionable. Choose appropriate chart types based on data types."""

    user_message = f"""
Dataset Schema:
{schema_str}

Sample Data (first 5 rows):
{sample_str}

User Role: {user_role}
User Prompt: {user_prompt}
{memory_str}

Generate a comprehensive analysis plan.
"""

    try:
        # Call LLM to generate plan
        llm_response = await call_llm(
            messages=[{"role": "user", "content": user_message}],
            system=system_prompt,
            json_mode=True
        )
        
        plan = json.loads(llm_response)
    
    except Exception as e:
        # Fallback to rule-based plan if LLM fails
        numeric_cols = [col for col, dtype in dataset_schema.items() 
                       if dtype in ["numeric", "currency", "percentage"]]
        datetime_cols = [col for col, dtype in dataset_schema.items() 
                        if dtype in ["datetime", "year"]]
        
        plan = {
            "intent": user_prompt or "Analyze dataset and generate insights",
            "kpis": numeric_cols[:5],
            "chart_configs": [],
            "preset": "executive" if user_role == "ceo" else "operational",
            "role_filter": "",
            "questions_for_analyst": [
                "Identify key trends in the data",
                "Detect any anomalies or outliers",
                "Find strong correlations between variables"
            ],
            "questions_for_strategist": [
                "Generate actionable recommendations",
                "Identify opportunities for improvement"
            ],
            "ml_target": None,
            "what_if_column": None,
            "root_cause_target": None,
            "knowledge_graph": False
        }
    
    # Determine time column for analysis
    time_column = None
    for col, dtype in dataset_schema.items():
        if dtype in ["datetime", "year"]:
            time_column = col
            break
    
    # Execute agents in parallel where possible
    results = {
        "plan": plan,
        "agent_outputs": {},
        "execution_time": {}
    }
    
    # Run analyst agent
    analyst_result = None
    if plan.get("kpis"):
        analyst_result = await run_analysis(
            df=df,
            kpi_columns=plan["kpis"],
            time_column=time_column
        )
        results["agent_outputs"]["analyst"] = analyst_result
        
        # Run critic agent to validate analyst output
        critic_result = await run_critic_validation(
            analyst_result,
            df,
            dataset_schema
        )
        results["agent_outputs"]["critic"] = critic_result
        
        # Run insight agent (use rule-based for reliability)
        insight_result = await generate_insights(
            analysis_result=analyst_result,
            validation_result=critic_result,
            dataset_name="Dataset",
            use_llm=True   # LLM-powered insights enabled
        )
        
        # Validate insights with InsightEval agent
        try:
            key_insights = insight_result.get("key_insights", [])
            if key_insights:
                validation_result = await validate_insights(
                    key_insights,
                    df,
                    analyst_result.get("kpis", {}),
                    dataset_schema
                )
                
                # Use validated insights
                insight_result["key_insights"] = validation_result["validated_insights"]
                insight_result["rejected_insights"] = validation_result["rejected_insights"]
                insight_result["validation_score"] = validation_result["validation_score"]
                
                # Deduplicate insights
                insight_result["key_insights"] = await deduplicate_insights(
                    insight_result["key_insights"],
                    similarity_threshold=0.8
                )
                
                logger.info(f"✓ InsightEval: {validation_result['passed']}/{validation_result['total_insights']} insights validated")
        except Exception as e:
            logger.warning(f"⚠ InsightEval failed (non-critical): {e}")
        
        results["agent_outputs"]["insights"] = insight_result
        
        # Run strategist agent
        recommendations = await generate_recommendations(
            validated_insights=critic_result["validated_insights"],
            kpis=analyst_result["kpis"],
            correlations=analyst_result["correlations"],
            trends=analyst_result["trends"]
        )
        results["agent_outputs"]["recommendations"] = recommendations
    
    # Run chart agent (request more charts for better analysis)
    chart_recommendations = await recommend_charts(
        df=df,
        schema=dataset_schema,
        max_charts=10
    )
    results["agent_outputs"]["chart"] = chart_recommendations
    
    # Merge LLM chart configs with recommended charts
    if plan.get("chart_configs"):
        results["agent_outputs"]["chart"] = plan["chart_configs"] + chart_recommendations
    
    # Run root cause analysis if requested
    if plan.get("root_cause_target") and plan["root_cause_target"] in df.columns:
        try:
            root_cause_result = await run_root_cause_analysis(
                df=df,
                metric=plan["root_cause_target"],
                change_direction="drop",  # Could be inferred from data
                time_period=None,
                baseline_period=None
            )
            results["agent_outputs"]["root_cause"] = root_cause_result
        except Exception as e:
            print(f"Root cause analysis failed: {e}")
    
    # Add execution summary
    results["summary"] = {
        "intent": plan.get("intent", ""),
        "kpis_analyzed": len(plan.get("kpis", [])),
        "charts_generated": len(results["agent_outputs"].get("chart", [])),
        "insights_found": len(results["agent_outputs"].get("insights", {}).get("key_insights", [])),
        "overall_confidence": results["agent_outputs"].get("critic", {}).get("overall_confidence", 0),
        "preset": plan.get("preset", "executive"),
        "recommendations_count": len(results["agent_outputs"].get("recommendations", []))
    }
    
    # Index dataset context in RAG (async, non-blocking)
    try:
        dataset_id = str(hash(str(dataset_schema)))  # Generate ID from schema
        await index_dataset(
            dataset_id=dataset_id,
            df=df,
            schema=dataset_schema,
            insights=results["agent_outputs"].get("insights", {}).get("key_insights", []),
            kpis=results["agent_outputs"].get("analyst", {}).get("kpis", {})
        )
        logger.info(f"✓ Dataset context indexed in RAG")
    except Exception as e:
        logger.warning(f"⚠ RAG indexing failed (non-critical): {e}")
    
    return results
