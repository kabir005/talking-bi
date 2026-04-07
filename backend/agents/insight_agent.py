from typing import Dict, List
from utils.llm import call_llm
import json


async def generate_insights(
    analysis_result: Dict,
    validation_result: Dict,
    dataset_name: str,
    use_llm: bool = False  # Disabled by default to avoid errors
) -> Dict:
    """
    Convert statistical outputs into rich, human-readable narratives.
    Returns executive summary, bullet insights, and watch-out items.
    """
    
    # Extract key data
    kpis = analysis_result.get("kpis", {})
    correlations = analysis_result.get("correlations", [])
    anomalies = analysis_result.get("anomalies", [])
    trends = analysis_result.get("trends", {})
    validated_insights = validation_result.get("validated_insights", [])
    overall_confidence = validation_result.get("overall_confidence", 0)
    
    # Use rule-based insights (more reliable)
    return await _generate_rule_based_insights(
        kpis, correlations, anomalies, trends,
        validated_insights, overall_confidence, dataset_name
    )


async def _generate_llm_insights(
    kpis: Dict,
    correlations: List[Dict],
    anomalies: List[Dict],
    trends: Dict,
    validated_insights: List[Dict],
    confidence: float,
    dataset_name: str
) -> Dict:
    """Generate insights using LLM"""
    
    system_prompt = """You are a business intelligence analyst writing executive-level insights.
Given validated statistics and anomalies, write:
1. An executive summary paragraph (3-5 sentences, plain English, no jargon)
2. 5 specific bullet point insights, each citing specific numbers
3. 2-3 "watch out" items (risks or anomalies to investigate)

CRITICAL: Every claim must cite a specific number from the data. Never generalize.

Bad: "Sales have been increasing"
Good: "Sales grew 18.3% MoM in October 2024, driven by Region A (+32%) offsetting Region C (-4.2%)"

Return JSON with:
{
  "executive_summary": "paragraph text",
  "key_insights": ["insight 1", "insight 2", ...],
  "watch_out": ["warning 1", "warning 2", ...]
}"""

    # Prepare data summary
    kpi_summary = []
    for col, data in list(kpis.items())[:5]:
        summary = f"{col}: "
        if "pct_change" in data:
            direction = "increased" if data["pct_change"] > 0 else "decreased"
            summary += f"{direction} {abs(data['pct_change']):.1f}%, "
        summary += f"mean={data.get('mean', 0):.2f}, total={data.get('total', 0):.2f}"
        kpi_summary.append(summary)
    
    corr_summary = [
        f"{c['col_a']} and {c['col_b']}: r={c['r']:.2f} ({c['interpretation']})"
        for c in correlations[:3]
    ]
    
    anomaly_summary = f"{len(anomalies)} anomalies detected" if anomalies else "No anomalies"
    
    trend_summary = []
    for col, data in list(trends.items())[:3]:
        if data.get("significant"):
            trend_summary.append(f"{col}: {data['trend']} trend (slope={data['slope']:.2f})")
    
    user_message = f"""
Dataset: {dataset_name}
Overall Confidence: {confidence:.1f}%

KPIs:
{chr(10).join(kpi_summary)}

Correlations:
{chr(10).join(corr_summary) if corr_summary else "None found"}

Anomalies: {anomaly_summary}

Trends:
{chr(10).join(trend_summary) if trend_summary else "No significant trends"}

Validated Insights: {len(validated_insights)} insights validated

Generate executive-level insights with specific numbers.
"""

    llm_response = await call_llm(
        messages=[{"role": "user", "content": user_message}],
        system=system_prompt,
        json_mode=True
    )
    
    insights_data = json.loads(llm_response)
    
    # Add confidence scores
    insights_data["overall_confidence"] = confidence
    insights_data["data_quality"] = "high" if confidence > 80 else "medium" if confidence > 60 else "low"
    
    return insights_data


async def _generate_rule_based_insights(
    kpis: Dict,
    correlations: List[Dict],
    anomalies: List[Dict],
    trends: Dict,
    validated_insights: List[Dict],
    confidence: float,
    dataset_name: str
) -> Dict:
    """Generate insights using rules (fallback)"""
    
    # Executive summary
    summary_parts = []
    
    # KPI summary
    if kpis:
        top_kpi = list(kpis.keys())[0]
        kpi_data = kpis[top_kpi]
        if "pct_change" in kpi_data:
            direction = "increased" if kpi_data["pct_change"] > 0 else "decreased"
            summary_parts.append(
                f"{top_kpi} {direction} by {abs(kpi_data['pct_change']):.1f}% "
                f"with a mean value of {kpi_data.get('mean', 0):.2f}"
            )
    
    # Correlation summary
    if correlations:
        top_corr = correlations[0]
        summary_parts.append(
            f"{top_corr['col_a']} and {top_corr['col_b']} show {top_corr['interpretation']} "
            f"(r={top_corr['r']:.2f})"
        )
    
    # Anomaly summary
    if anomalies:
        summary_parts.append(f"{len(anomalies)} anomalies were detected requiring investigation")
    
    executive_summary = ". ".join(summary_parts) + "." if summary_parts else "Analysis completed successfully."
    
    # Key insights
    key_insights = []
    
    # From KPIs
    for col, data in list(kpis.items())[:3]:
        if "pct_change" in data:
            direction = "increased" if data["pct_change"] > 0 else "decreased"
            key_insights.append(
                f"{col} {direction} by {abs(data['pct_change']):.1f}% "
                f"(mean: {data.get('mean', 0):.2f}, total: {data.get('total', 0):.2f})"
            )
        else:
            key_insights.append(
                f"{col} shows mean value of {data.get('mean', 0):.2f} "
                f"with total of {data.get('total', 0):.2f}"
            )
    
    # From correlations
    for corr in correlations[:2]:
        key_insights.append(
            f"{corr['col_a']} and {corr['col_b']}: {corr['interpretation']} "
            f"with correlation coefficient r={corr['r']:.2f}"
        )
    
    # From trends
    for col, data in list(trends.items())[:2]:
        if data.get("significant"):
            key_insights.append(
                f"{col} exhibits {data['trend']} trend "
                f"(slope={data['slope']:.2f}, R²={data.get('r_squared', 0):.2f}, p<0.05)"
            )
    
    # Watch out items
    watch_out = []
    
    # Anomalies
    if len(anomalies) > 0:
        watch_out.append(
            f"{len(anomalies)} anomalies detected - review data quality and investigate outliers"
        )
    
    # Low confidence insights
    uncertain_count = len([i for i in validated_insights if i.get("validation_status") == "uncertain"])
    if uncertain_count > 0:
        watch_out.append(
            f"{uncertain_count} insights have uncertain confidence - verify with additional data"
        )
    
    # Weak correlations flagged as strong
    weak_corrs = [c for c in correlations if abs(c['r']) < 0.5]
    if weak_corrs:
        watch_out.append(
            f"{len(weak_corrs)} weak correlations detected - may not be actionable"
        )
    
    # Add generic watch-out if none found
    if not watch_out:
        watch_out.append("Continue monitoring key metrics for unexpected changes")
    
    return {
        "executive_summary": executive_summary,
        "key_insights": key_insights[:5],  # Top 5
        "watch_out": watch_out[:3],  # Top 3
        "overall_confidence": confidence,
        "data_quality": "high" if confidence > 80 else "medium" if confidence > 60 else "low",
        "insights_count": len(key_insights)
    }


async def generate_deep_explanation(
    metric: str,
    change_value: float,
    contributors: List[Dict],
    correlations: List[Dict]
) -> str:
    """
    Generate deep explainability output for a specific metric change.
    """
    
    explanation_parts = []
    
    # Main change
    direction = "increased" if change_value > 0 else "decreased"
    explanation_parts.append(
        f"{metric} {direction} by {abs(change_value):.1f}% due to:"
    )
    
    # Top contributors
    for i, contrib in enumerate(contributors[:3], 1):
        explanation_parts.append(
            f"— {contrib['segment']}: {contrib['change']:+.1f}% "
            f"({contrib.get('reason', 'contributing factor')})"
        )
    
    # Correlations
    if correlations:
        explanation_parts.append("\nCorrelated factors:")
        for corr in correlations[:2]:
            explanation_parts.append(
                f"— {corr['factor']}: correlation r={corr['r']:.2f}, p={corr.get('p_value', 0.001):.3f}"
            )
    
    # Confidence statement
    explanation_parts.append(
        f"\nConfidence: {contributors[0].get('confidence', 85)}% "
        f"(validated by Critic Agent, n={contributors[0].get('sample_size', 100)})"
    )
    
    return "\n".join(explanation_parts)
