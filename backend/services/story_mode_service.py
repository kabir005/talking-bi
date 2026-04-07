"""
Story Mode Service - Generate executive narrative summaries
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from services.llm_service import call_llm

logger = logging.getLogger(__name__)


class StoryModeService:
    """Generate executive narratives from data insights"""
    
    @staticmethod
    async def generate_executive_summary(
        dataset_name: str,
        kpis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        trends: Optional[List[Dict[str, Any]]] = None,
        recommendations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a 3-paragraph executive narrative
        
        Args:
            dataset_name: Name of the dataset
            kpis: Key performance indicators
            insights: List of insights
            trends: Optional trend analysis
            recommendations: Optional recommendations
            
        Returns:
            Executive summary with narrative
        """
        try:
            # Build context
            context = f"Dataset: {dataset_name}\n\n"
            
            # Add KPIs
            if kpis:
                context += "Key Metrics:\n"
                for key, value in list(kpis.items())[:5]:
                    context += f"- {key}: {value}\n"
                context += "\n"
            
            # Add top insights
            if insights:
                context += "Key Insights:\n"
                for insight in insights[:5]:
                    context += f"- {insight.get('text', insight.get('insight', ''))}\n"
                context += "\n"
            
            # Add trends
            if trends:
                context += "Trends:\n"
                for trend in trends[:3]:
                    context += f"- {trend.get('description', '')}\n"
                context += "\n"
            
            # Add recommendations
            if recommendations:
                context += "Recommendations:\n"
                for rec in recommendations[:3]:
                    context += f"- {rec}\n"
            
            # Generate narrative
            prompt = f"""You are an executive business analyst. Generate a concise 3-paragraph executive summary based on the following data analysis.

{context}

Write a professional executive summary with exactly 3 paragraphs:
1. Overview paragraph: What the data shows at a high level
2. Key findings paragraph: The most important insights and trends
3. Action items paragraph: What should be done based on these findings

Keep it concise, professional, and actionable. Each paragraph should be 3-4 sentences."""

            response = await call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse into paragraphs
            paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
            
            # Ensure we have 3 paragraphs
            while len(paragraphs) < 3:
                paragraphs.append("Additional analysis pending.")
            
            return {
                "narrative": response,
                "paragraphs": {
                    "overview": paragraphs[0] if len(paragraphs) > 0 else "",
                    "key_findings": paragraphs[1] if len(paragraphs) > 1 else "",
                    "action_items": paragraphs[2] if len(paragraphs) > 2 else ""
                },
                "word_count": len(response.split()),
                "generated": True
            }
            
        except Exception as e:
            logger.error(f"Story generation failed: {str(e)}")
            # Fallback to template-based summary
            return StoryModeService._generate_template_summary(
                dataset_name, kpis, insights, trends, recommendations
            )
    
    @staticmethod
    def _generate_template_summary(
        dataset_name: str,
        kpis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        trends: Optional[List[Dict[str, Any]]],
        recommendations: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Generate template-based summary when LLM fails"""
        
        # Overview paragraph
        overview = f"Analysis of {dataset_name} reveals "
        if kpis:
            kpi_count = len(kpis)
            overview += f"{kpi_count} key performance indicators. "
        if insights:
            overview += f"The dataset contains {len(insights)} significant insights "
            overview += "that provide actionable intelligence for decision-making."
        
        # Key findings paragraph
        key_findings = "Key findings include: "
        if insights:
            top_insights = [i.get('text', i.get('insight', '')) for i in insights[:3]]
            key_findings += "; ".join(top_insights[:2]) + "."
        else:
            key_findings += "Data patterns indicate stable performance with opportunities for optimization."
        
        # Action items paragraph
        action_items = "Recommended actions: "
        if recommendations:
            action_items += "; ".join(recommendations[:3]) + "."
        else:
            action_items += "Continue monitoring key metrics and investigate anomalies for deeper insights."
        
        narrative = f"{overview}\n\n{key_findings}\n\n{action_items}"
        
        return {
            "narrative": narrative,
            "paragraphs": {
                "overview": overview,
                "key_findings": key_findings,
                "action_items": action_items
            },
            "word_count": len(narrative.split()),
            "generated": False,
            "fallback": True
        }
    
    @staticmethod
    async def generate_insight_story(insight: Dict[str, Any], context: str = "") -> str:
        """
        Generate a narrative explanation for a single insight
        
        Args:
            insight: Insight dictionary
            context: Additional context
            
        Returns:
            Narrative explanation
        """
        try:
            insight_text = insight.get('text', insight.get('insight', ''))
            category = insight.get('category', 'general')
            
            prompt = f"""Explain this data insight in a clear, narrative style for business executives:

Insight: {insight_text}
Category: {category}
{f"Context: {context}" if context else ""}

Write 2-3 sentences that explain:
1. What this insight means
2. Why it matters
3. What action might be taken

Keep it concise and actionable."""

            response = await call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=150
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Insight story generation failed: {str(e)}")
            return insight.get('text', insight.get('insight', 'No insight available'))
    
    @staticmethod
    async def generate_trend_narrative(
        column: str,
        trend_type: str,
        values: List[float],
        dates: Optional[List[str]] = None
    ) -> str:
        """
        Generate narrative for a trend
        
        Args:
            column: Column name
            trend_type: Type of trend (increasing, decreasing, stable, volatile)
            values: Trend values
            dates: Optional date labels
            
        Returns:
            Trend narrative
        """
        try:
            # Calculate statistics
            start_val = values[0] if values else 0
            end_val = values[-1] if values else 0
            change = end_val - start_val
            pct_change = (change / start_val * 100) if start_val != 0 else 0
            
            # Build context
            context = f"Column: {column}\n"
            context += f"Trend: {trend_type}\n"
            context += f"Start value: {start_val:.2f}\n"
            context += f"End value: {end_val:.2f}\n"
            context += f"Change: {change:.2f} ({pct_change:.1f}%)\n"
            if dates:
                context += f"Period: {dates[0]} to {dates[-1]}\n"
            
            prompt = f"""Generate a brief narrative (2-3 sentences) describing this trend:

{context}

Explain what the trend shows and what it might indicate for the business."""

            response = await call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=100
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Trend narrative generation failed: {str(e)}")
            # Fallback
            direction = "increased" if change > 0 else "decreased" if change < 0 else "remained stable"
            return f"{column} has {direction} by {abs(pct_change):.1f}% over the period, showing a {trend_type} trend."
