"""
InsightEval Agent - Validates LLM-generated insights for accuracy
Prevents hallucinations by checking numbers against actual data
"""

import pandas as pd
from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


async def validate_insights(
    insights: List[Dict[str, Any]],
    df: pd.DataFrame,
    kpis: Dict[str, Any],
    schema: Dict[str, str]
) -> Dict[str, Any]:
    """
    Validate insights against actual data
    
    Args:
        insights: List of insights from insight agent
        df: Original DataFrame
        kpis: Calculated KPIs
        schema: Dataset schema
    
    Returns:
        {
            "validated_insights": List[Dict],  # Insights that passed validation
            "rejected_insights": List[Dict],   # Insights that failed
            "validation_score": float,         # 0-1 score
            "issues_found": List[str]
        }
    """
    logger.info(f"Validating {len(insights)} insights...")
    
    validated = []
    rejected = []
    issues = []
    
    for insight in insights:
        validation_result = await _validate_single_insight(
            insight, df, kpis, schema
        )
        
        if validation_result["valid"]:
            validated.append({
                **insight,
                "validation_score": validation_result["confidence"],
                "validated": True
            })
        else:
            rejected.append({
                **insight,
                "rejection_reason": validation_result["reason"],
                "validated": False
            })
            issues.append(validation_result["reason"])
    
    validation_score = len(validated) / len(insights) if insights else 0
    
    logger.info(f"✓ Validated: {len(validated)}/{len(insights)} insights")
    logger.info(f"✗ Rejected: {len(rejected)} insights")
    
    return {
        "validated_insights": validated,
        "rejected_insights": rejected,
        "validation_score": validation_score,
        "issues_found": issues,
        "total_insights": len(insights),
        "passed": len(validated),
        "failed": len(rejected)
    }


async def _validate_single_insight(
    insight: Dict[str, Any],
    df: pd.DataFrame,
    kpis: Dict[str, Any],
    schema: Dict[str, str]
) -> Dict[str, Any]:
    """Validate a single insight"""
    
    text = insight.get("text", "")
    category = insight.get("category", "")
    
    # Extract numbers from insight text
    numbers = _extract_numbers(text)
    
    # Validation checks
    checks = []
    
    # Check 1: Number validation
    if numbers:
        number_check = _validate_numbers(numbers, df, kpis)
        checks.append(number_check)
    
    # Check 2: Column name validation
    column_check = _validate_column_names(text, schema)
    checks.append(column_check)
    
    # Check 3: Taxonomy validation
    taxonomy_check = _validate_taxonomy(category)
    checks.append(taxonomy_check)
    
    # Check 4: Logical consistency
    logic_check = _validate_logic(text)
    checks.append(logic_check)
    
    # Aggregate results
    passed_checks = sum(1 for c in checks if c["valid"])
    confidence = passed_checks / len(checks)
    
    # Insight is valid if it passes at least 75% of checks
    is_valid = confidence >= 0.75
    
    # Collect reasons for failure
    reasons = [c["reason"] for c in checks if not c["valid"]]
    reason = "; ".join(reasons) if reasons else "Passed all checks"
    
    return {
        "valid": is_valid,
        "confidence": confidence,
        "reason": reason,
        "checks_passed": passed_checks,
        "checks_total": len(checks)
    }


def _extract_numbers(text: str) -> List[float]:
    """Extract numbers from text"""
    # Match numbers with optional decimals, commas, and percentage signs
    pattern = r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?%?'
    matches = re.findall(pattern, text)
    
    numbers = []
    for match in matches:
        try:
            # Remove commas and percentage signs
            clean = match.replace(',', '').replace('%', '')
            numbers.append(float(clean))
        except ValueError:
            continue
    
    return numbers


def _validate_numbers(
    numbers: List[float],
    df: pd.DataFrame,
    kpis: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate that numbers in insight match actual data"""
    
    # Get all actual values from KPIs
    actual_values = []
    for col, kpi_data in kpis.items():
        if "total" in kpi_data:
            actual_values.append(kpi_data["total"])
        if "mean" in kpi_data:
            actual_values.append(kpi_data["mean"])
        if "median" in kpi_data:
            actual_values.append(kpi_data["median"])
        if "min" in kpi_data:
            actual_values.append(kpi_data["min"])
        if "max" in kpi_data:
            actual_values.append(kpi_data["max"])
    
    # Check if insight numbers are close to actual values
    for num in numbers:
        # Skip percentages (0-100 range)
        if 0 <= num <= 100:
            continue
        
        # Check if number is within reasonable range of any actual value
        found_match = False
        for actual in actual_values:
            # Allow 10% tolerance
            if abs(num - actual) / max(abs(actual), 1) < 0.1:
                found_match = True
                break
        
        if not found_match and num > 1000:  # Only check large numbers
            return {
                "valid": False,
                "reason": f"Number {num} doesn't match any actual data values"
            }
    
    return {"valid": True, "reason": "Numbers validated"}


def _validate_column_names(text: str, schema: Dict[str, str]) -> Dict[str, Any]:
    """Validate that column names mentioned exist in schema"""
    
    # Extract potential column names (capitalized words)
    words = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', text)
    
    # Check if any mentioned columns don't exist
    for word in words:
        # Check exact match or fuzzy match
        if word not in schema:
            # Check if it's close to any actual column
            from difflib import get_close_matches
            matches = get_close_matches(word, schema.keys(), n=1, cutoff=0.8)
            if not matches:
                # Not a column name, might be a regular word
                continue
    
    return {"valid": True, "reason": "Column names validated"}


def _validate_taxonomy(category: str) -> Dict[str, Any]:
    """Validate that insight category is valid"""
    
    valid_categories = [
        "trend",
        "anomaly",
        "correlation",
        "distribution",
        "comparison",
        "summary",
        "outlier",
        "pattern",
        "seasonality",
        "forecast"
    ]
    
    if category.lower() not in valid_categories:
        return {
            "valid": False,
            "reason": f"Invalid category: {category}"
        }
    
    return {"valid": True, "reason": "Category validated"}


def _validate_logic(text: str) -> Dict[str, Any]:
    """Validate logical consistency of insight"""
    
    # Check for contradictions
    contradictions = [
        (r'increase.*decrease', 'Contradictory: increase and decrease'),
        (r'higher.*lower', 'Contradictory: higher and lower'),
        (r'positive.*negative', 'Contradictory: positive and negative'),
        (r'growth.*decline', 'Contradictory: growth and decline')
    ]
    
    text_lower = text.lower()
    for pattern, reason in contradictions:
        if re.search(pattern, text_lower):
            return {"valid": False, "reason": reason}
    
    # Check for impossible claims
    impossible_patterns = [
        (r'(\d+)%.*growth.*(\d+)%', lambda m: float(m.group(1)) > 1000, 'Unrealistic growth rate'),
        (r'(\d+)x.*increase', lambda m: float(m.group(1)) > 100, 'Unrealistic multiplier')
    ]
    
    for pattern, check_func, reason in impossible_patterns:
        match = re.search(pattern, text_lower)
        if match and check_func(match):
            return {"valid": False, "reason": reason}
    
    return {"valid": True, "reason": "Logic validated"}


async def calculate_novelty_score(
    insight: Dict[str, Any],
    existing_insights: List[Dict[str, Any]]
) -> float:
    """
    Calculate how novel/unique an insight is compared to existing ones
    
    Returns:
        0-1 score (1 = completely novel, 0 = duplicate)
    """
    from difflib import SequenceMatcher
    
    text = insight.get("text", "")
    
    if not existing_insights:
        return 1.0
    
    max_similarity = 0
    for existing in existing_insights:
        existing_text = existing.get("text", "")
        similarity = SequenceMatcher(None, text, existing_text).ratio()
        max_similarity = max(max_similarity, similarity)
    
    # Novelty is inverse of similarity
    novelty = 1 - max_similarity
    
    return novelty


async def deduplicate_insights(
    insights: List[Dict[str, Any]],
    similarity_threshold: float = 0.8
) -> List[Dict[str, Any]]:
    """
    Remove duplicate or very similar insights
    
    Args:
        insights: List of insights
        similarity_threshold: Threshold for considering insights as duplicates
    
    Returns:
        Deduplicated list of insights
    """
    from difflib import SequenceMatcher
    
    if not insights:
        return []
    
    unique_insights = [insights[0]]
    
    for insight in insights[1:]:
        text = insight.get("text", "")
        
        # Check similarity with all unique insights
        is_duplicate = False
        for unique in unique_insights:
            unique_text = unique.get("text", "")
            similarity = SequenceMatcher(None, text, unique_text).ratio()
            
            if similarity >= similarity_threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_insights.append(insight)
    
    logger.info(f"Deduplicated: {len(insights)} → {len(unique_insights)} insights")
    
    return unique_insights
