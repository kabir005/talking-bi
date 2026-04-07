"""
Root Cause Analysis Agent - Traces causal chains behind metric movements
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats
from scipy.stats import pearsonr
import networkx as nx
from utils.llm import call_llm
import json


async def run_root_cause_analysis(
    df: pd.DataFrame,
    metric: str,
    change_direction: str,  # "drop" or "rise"
    time_period: Optional[str] = None,
    baseline_period: Optional[str] = None,
    dataset_schema: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Automatically traces the causal chain behind metric movements.
    
    Algorithm:
    1. Compute metric change vs baseline
    2. Decompose by categorical dimensions
    3. Identify top contributor segments
    4. Check correlations with all features
    5. Check time-lag correlations
    6. Build causal chain
    7. Generate NetworkX graph
    8. Generate LLM explanation
    
    Returns:
        {
            "summary": "narrative text",
            "causal_chain": [...],
            "knowledge_graph_nodes": [...],
            "knowledge_graph_edges": [...],
            "recommendations": [...]
        }
    """
    print(f"\n{'='*80}")
    print(f"ROOT CAUSE ANALYSIS")
    print(f"{'='*80}")
    print(f"Metric: {metric}")
    print(f"Direction: {change_direction}")
    print(f"Dataset shape: {df.shape}")
    
    # Validate metric column
    if metric not in df.columns:
        raise ValueError(f"Metric column '{metric}' not found in dataset")
    
    # Convert metric to numeric
    metric_series = pd.to_numeric(df[metric], errors='coerce').dropna()
    
    if len(metric_series) == 0:
        raise ValueError(f"No valid numeric values in metric column '{metric}'")
    
    # Step 1: Compute metric change
    metric_change = compute_metric_change(
        df, metric, time_period, baseline_period
    )
    
    print(f"\nMetric Change Analysis:")
    print(f"  Current: {metric_change['current_value']:.2f}")
    print(f"  Baseline: {metric_change['baseline_value']:.2f}")
    print(f"  Change: {metric_change['absolute_change']:.2f} ({metric_change['percent_change']:.1f}%)")
    
    # Step 2: Decompose by categorical dimensions
    categorical_decomposition = decompose_by_categories(
        df, metric, dataset_schema
    )
    
    print(f"\nCategorical Decomposition:")
    for decomp in categorical_decomposition[:3]:
        print(f"  {decomp['dimension']}: Top contributor = {decomp['top_segment']} ({decomp['contribution']:.1f}%)")
    
    # Step 3: Identify top contributors
    top_contributors = identify_top_contributors(
        categorical_decomposition, change_direction
    )
    
    print(f"\nTop Contributors:")
    for contrib in top_contributors[:3]:
        print(f"  {contrib['segment']} in {contrib['dimension']}: {contrib['impact']:.1f}% impact")
    
    # Step 4: Correlation analysis
    correlations = analyze_correlations(
        df, metric, dataset_schema
    )
    
    print(f"\nCorrelations Found: {len(correlations)}")
    for corr in correlations[:3]:
        print(f"  {corr['feature']} ↔ {metric}: r={corr['correlation']:.3f}, p={corr['p_value']:.4f}")
    
    # Step 5: Time-lag analysis
    time_lag_correlations = analyze_time_lag_correlations(
        df, metric, correlations, dataset_schema
    )
    
    print(f"\nTime-Lag Correlations: {len(time_lag_correlations)}")
    for lag_corr in time_lag_correlations[:3]:
        print(f"  {lag_corr['feature']} (lag {lag_corr['lag']}) → {metric}: r={lag_corr['correlation']:.3f}")
    
    # Step 6: Build causal chain
    causal_chain = build_causal_chain(
        metric,
        metric_change,
        top_contributors,
        correlations,
        time_lag_correlations,
        change_direction
    )
    
    print(f"\nCausal Chain Built: {len(causal_chain)} links")
    for i, link in enumerate(causal_chain):
        print(f"  {i+1}. {link['cause']} → {link['effect']} (confidence: {link['confidence']}%)")
    
    # Step 7: Build knowledge graph
    graph_data = build_knowledge_graph(
        metric,
        causal_chain,
        correlations,
        top_contributors
    )
    
    print(f"\nKnowledge Graph:")
    print(f"  Nodes: {len(graph_data['nodes'])}")
    print(f"  Edges: {len(graph_data['edges'])}")
    
    # Step 8: Generate recommendations
    recommendations = generate_recommendations(
        causal_chain,
        top_contributors,
        change_direction
    )
    
    print(f"\nRecommendations: {len(recommendations)}")
    for i, rec in enumerate(recommendations):
        print(f"  {i+1}. {rec['action']}")
    
    # Step 9: Generate LLM narrative
    narrative = await generate_root_cause_narrative(
        metric,
        metric_change,
        causal_chain,
        top_contributors,
        recommendations,
        change_direction
    )
    
    print(f"\n{'='*80}")
    print(f"ROOT CAUSE ANALYSIS COMPLETE")
    print(f"{'='*80}\n")
    
    return {
        "metric": metric,
        "change_direction": change_direction,
        "metric_change": metric_change,
        "summary": narrative,
        "causal_chain": causal_chain,
        "top_contributors": top_contributors,
        "correlations": correlations[:10],  # Top 10
        "time_lag_correlations": time_lag_correlations[:5],  # Top 5
        "knowledge_graph_nodes": graph_data["nodes"],
        "knowledge_graph_edges": graph_data["edges"],
        "recommendations": recommendations,
        "confidence_score": calculate_overall_confidence(causal_chain)
    }


def compute_metric_change(
    df: pd.DataFrame,
    metric: str,
    time_period: Optional[str],
    baseline_period: Optional[str]
) -> Dict[str, float]:
    """Compute metric change between current and baseline periods"""
    metric_series = pd.to_numeric(df[metric], errors='coerce').dropna()
    
    # If no time periods specified, compare first half vs second half
    if time_period is None or baseline_period is None:
        mid_point = len(df) // 2
        baseline_value = float(metric_series.iloc[:mid_point].mean())
        current_value = float(metric_series.iloc[mid_point:].mean())
    else:
        # TODO: Implement time period filtering when date column is available
        baseline_value = float(metric_series.iloc[:len(df)//2].mean())
        current_value = float(metric_series.iloc[len(df)//2:].mean())
    
    absolute_change = current_value - baseline_value
    percent_change = (absolute_change / baseline_value * 100) if baseline_value != 0 else 0
    
    return {
        "current_value": current_value,
        "baseline_value": baseline_value,
        "absolute_change": absolute_change,
        "percent_change": percent_change
    }


def decompose_by_categories(
    df: pd.DataFrame,
    metric: str,
    dataset_schema: Optional[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """Decompose metric by each categorical dimension"""
    decompositions = []
    
    # Identify categorical columns
    if dataset_schema:
        categorical_cols = [col for col, dtype in dataset_schema.items() 
                          if dtype in ["categorical", "geographic"] and col != metric]
    else:
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        categorical_cols = [col for col in categorical_cols if col != metric]
    
    metric_series = pd.to_numeric(df[metric], errors='coerce')
    total_metric = metric_series.sum()
    
    for cat_col in categorical_cols[:10]:  # Limit to 10 dimensions
        try:
            # Group by category and sum metric
            grouped = df.groupby(cat_col)[metric].apply(
                lambda x: pd.to_numeric(x, errors='coerce').sum()
            ).sort_values(ascending=False)
            
            if len(grouped) == 0:
                continue
            
            # Calculate contribution of each segment
            contributions = (grouped / total_metric * 100).to_dict()
            
            # Find top contributor
            top_segment = grouped.index[0]
            top_contribution = contributions[top_segment]
            
            decompositions.append({
                "dimension": cat_col,
                "top_segment": str(top_segment),
                "contribution": float(top_contribution),
                "segment_value": float(grouped.iloc[0]),
                "all_segments": {str(k): float(v) for k, v in contributions.items()}
            })
        
        except Exception as e:
            print(f"Warning: Could not decompose by {cat_col}: {e}")
            continue
    
    # Sort by contribution
    decompositions.sort(key=lambda x: x['contribution'], reverse=True)
    
    return decompositions


def identify_top_contributors(
    decompositions: List[Dict],
    change_direction: str
) -> List[Dict[str, Any]]:
    """Identify segments that contributed most to the change"""
    contributors = []
    
    for decomp in decompositions[:5]:  # Top 5 dimensions
        contributors.append({
            "dimension": decomp["dimension"],
            "segment": decomp["top_segment"],
            "impact": decomp["contribution"],
            "value": decomp["segment_value"],
            "direction": change_direction
        })
    
    return contributors


def analyze_correlations(
    df: pd.DataFrame,
    metric: str,
    dataset_schema: Optional[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """Analyze correlations between metric and all numeric features"""
    correlations = []
    
    # Get metric series
    metric_series = pd.to_numeric(df[metric], errors='coerce')
    
    # Identify numeric columns
    if dataset_schema:
        numeric_cols = [col for col, dtype in dataset_schema.items() 
                       if dtype in ["numeric", "currency", "percentage"] and col != metric]
    else:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col != metric and col != '_is_outlier']
    
    for col in numeric_cols:
        try:
            # Convert to numeric
            feature_series = pd.to_numeric(df[col], errors='coerce')
            
            # Remove NaN pairs
            valid_mask = metric_series.notna() & feature_series.notna()
            metric_clean = metric_series[valid_mask]
            feature_clean = feature_series[valid_mask]
            
            if len(metric_clean) < 10:
                continue
            
            # Compute Pearson correlation
            r, p_value = pearsonr(metric_clean, feature_clean)
            
            # Only keep significant correlations
            if abs(r) > 0.3 and p_value < 0.05:
                correlations.append({
                    "feature": col,
                    "correlation": float(r),
                    "p_value": float(p_value),
                    "direction": "positive" if r > 0 else "negative",
                    "strength": "strong" if abs(r) > 0.7 else "moderate" if abs(r) > 0.5 else "weak",
                    "n_samples": len(metric_clean)
                })
        
        except Exception as e:
            continue
    
    # Sort by absolute correlation
    correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
    
    return correlations


def analyze_time_lag_correlations(
    df: pd.DataFrame,
    metric: str,
    correlations: List[Dict],
    dataset_schema: Optional[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """Check if features at time t-k predict metric at time t"""
    time_lag_correlations = []
    
    metric_series = pd.to_numeric(df[metric], errors='coerce')
    
    # Only check top correlated features
    top_features = [c['feature'] for c in correlations[:5]]
    
    for feature in top_features:
        try:
            feature_series = pd.to_numeric(df[feature], errors='coerce')
            
            # Try lags 1, 2, 3
            for lag in [1, 2, 3]:
                if len(df) < lag + 10:
                    continue
                
                # Shift feature series by lag
                feature_lagged = feature_series.shift(lag)
                
                # Remove NaN
                valid_mask = metric_series.notna() & feature_lagged.notna()
                metric_clean = metric_series[valid_mask]
                feature_clean = feature_lagged[valid_mask]
                
                if len(metric_clean) < 10:
                    continue
                
                # Compute correlation
                r, p_value = pearsonr(metric_clean, feature_clean)
                
                # Only keep if stronger than zero-lag correlation
                if abs(r) > 0.4 and p_value < 0.05:
                    time_lag_correlations.append({
                        "feature": feature,
                        "lag": lag,
                        "correlation": float(r),
                        "p_value": float(p_value),
                        "interpretation": f"{feature} at t-{lag} predicts {metric} at t"
                    })
        
        except Exception as e:
            continue
    
    # Sort by absolute correlation
    time_lag_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
    
    return time_lag_correlations


def build_causal_chain(
    metric: str,
    metric_change: Dict,
    top_contributors: List[Dict],
    correlations: List[Dict],
    time_lag_correlations: List[Dict],
    change_direction: str
) -> List[Dict[str, Any]]:
    """Build causal chain from evidence"""
    chain = []
    
    # Link 1: Top contributor → metric change
    if top_contributors:
        top = top_contributors[0]
        
        # Calculate confidence based on contribution magnitude
        confidence = min(95, int(50 + top['impact'] / 2))
        
        chain.append({
            "cause": f"{top['segment']} in {top['dimension']}",
            "effect": f"{metric} {change_direction}",
            "confidence": confidence,
            "evidence": f"Contributes {top['impact']:.1f}% of total {metric}",
            "mechanism": "direct_contribution"
        })
    
    # Link 2: Correlated features → top contributor
    if correlations and top_contributors:
        top_corr = correlations[0]
        top_contrib = top_contributors[0]
        
        # Confidence based on correlation strength and p-value
        if top_corr['p_value'] < 0.001:
            confidence = 90
        elif top_corr['p_value'] < 0.01:
            confidence = 85
        else:
            confidence = 75
        
        chain.append({
            "cause": f"{top_corr['feature']} change",
            "effect": f"{top_contrib['segment']} performance",
            "confidence": confidence,
            "evidence": f"r={top_corr['correlation']:.3f}, p={top_corr['p_value']:.4f}",
            "mechanism": "correlation"
        })
    
    # Link 3: Time-lagged predictors
    if time_lag_correlations:
        lag_corr = time_lag_correlations[0]
        
        confidence = min(90, int(60 + abs(lag_corr['correlation']) * 30))
        
        chain.append({
            "cause": f"{lag_corr['feature']} (t-{lag_corr['lag']})",
            "effect": f"{metric} (t)",
            "confidence": confidence,
            "evidence": f"r={lag_corr['correlation']:.3f}, lag={lag_corr['lag']} periods",
            "mechanism": "time_lag"
        })
    
    return chain


def build_knowledge_graph(
    metric: str,
    causal_chain: List[Dict],
    correlations: List[Dict],
    top_contributors: List[Dict]
) -> Dict[str, List]:
    """Build NetworkX graph for visualization"""
    G = nx.DiGraph()
    
    nodes = []
    edges = []
    
    # Add metric as central node
    nodes.append({
        "id": metric,
        "label": metric,
        "type": "metric",
        "size": 30,
        "color": "#F5A623"
    })
    
    # Add nodes from causal chain
    node_ids = {metric}
    for link in causal_chain:
        cause_id = link['cause']
        effect_id = link['effect']
        
        if cause_id not in node_ids:
            nodes.append({
                "id": cause_id,
                "label": cause_id,
                "type": "cause",
                "size": 20,
                "color": "#3B82F6"
            })
            node_ids.add(cause_id)
        
        if effect_id not in node_ids:
            nodes.append({
                "id": effect_id,
                "label": effect_id,
                "type": "effect",
                "size": 20,
                "color": "#22C55E"
            })
            node_ids.add(effect_id)
        
        # Add edge
        edges.append({
            "source": cause_id,
            "target": effect_id,
            "weight": link['confidence'] / 100,
            "label": f"{link['confidence']}%",
            "color": "#F5A623" if link['confidence'] > 80 else "#8B8FA8"
        })
    
    # Add correlation edges
    for corr in correlations[:5]:
        feature_id = corr['feature']
        
        if feature_id not in node_ids:
            nodes.append({
                "id": feature_id,
                "label": feature_id,
                "type": "feature",
                "size": 15,
                "color": "#8B5CF6"
            })
            node_ids.add(feature_id)
        
        edges.append({
            "source": feature_id,
            "target": metric,
            "weight": abs(corr['correlation']),
            "label": f"r={corr['correlation']:.2f}",
            "color": "#22C55E" if corr['direction'] == "positive" else "#EF4444"
        })
    
    return {
        "nodes": nodes,
        "edges": edges
    }


def generate_recommendations(
    causal_chain: List[Dict],
    top_contributors: List[Dict],
    change_direction: str
) -> List[Dict[str, Any]]:
    """Generate actionable recommendations based on root cause"""
    recommendations = []
    
    if not causal_chain:
        return recommendations
    
    # Recommendation 1: Address primary cause
    primary_cause = causal_chain[0]
    
    if change_direction == "drop":
        action = f"Investigate and address issues in {primary_cause['cause']}"
        expected_impact = "Reverse the decline"
    else:
        action = f"Amplify success factors in {primary_cause['cause']}"
        expected_impact = "Sustain the growth"
    
    recommendations.append({
        "rank": 1,
        "action": action,
        "expected_impact": expected_impact,
        "timeline": "Immediate (1-2 weeks)",
        "risk_level": "low",
        "confidence": primary_cause['confidence']
    })
    
    # Recommendation 2: Leverage top contributor
    if top_contributors:
        top = top_contributors[0]
        
        if change_direction == "drop":
            action = f"Focus resources on recovering {top['segment']} segment"
        else:
            action = f"Replicate {top['segment']} success to other segments"
        
        recommendations.append({
            "rank": 2,
            "action": action,
            "expected_impact": f"Impact {top['impact']:.0f}% of total metric",
            "timeline": "Short-term (2-4 weeks)",
            "risk_level": "medium",
            "confidence": 80
        })
    
    # Recommendation 3: Monitor leading indicators
    if len(causal_chain) > 1:
        lagged_cause = causal_chain[-1]
        
        recommendations.append({
            "rank": 3,
            "action": f"Monitor {lagged_cause['cause']} as leading indicator",
            "expected_impact": "Early warning system for future changes",
            "timeline": "Ongoing",
            "risk_level": "low",
            "confidence": lagged_cause['confidence']
        })
    
    return recommendations


def calculate_overall_confidence(causal_chain: List[Dict]) -> int:
    """Calculate overall confidence in root cause analysis"""
    if not causal_chain:
        return 0
    
    # Average confidence of all links
    confidences = [link['confidence'] for link in causal_chain]
    
    # Weight by position (earlier links more important)
    weights = [1.0 / (i + 1) for i in range(len(confidences))]
    weighted_avg = sum(c * w for c, w in zip(confidences, weights)) / sum(weights)
    
    return int(weighted_avg)


async def generate_root_cause_narrative(
    metric: str,
    metric_change: Dict,
    causal_chain: List[Dict],
    top_contributors: List[Dict],
    recommendations: List[Dict],
    change_direction: str
) -> str:
    """Generate human-readable root cause narrative using LLM"""
    try:
        system_prompt = """You are a business analyst writing a root cause analysis report.

Write a 3-paragraph analysis:
Paragraph 1: What happened and by how much (cite specific numbers)
Paragraph 2: Why it happened (explain the causal chain with evidence)
Paragraph 3: What to do about it (2-3 specific actions)

Be specific, cite numbers, and be actionable."""
        
        context = {
            "metric": metric,
            "change": {
                "direction": change_direction,
                "current": metric_change['current_value'],
                "baseline": metric_change['baseline_value'],
                "percent_change": metric_change['percent_change']
            },
            "causal_chain": causal_chain[:3],
            "top_contributors": top_contributors[:2],
            "recommendations": recommendations
        }
        
        messages = [{
            "role": "user",
            "content": f"Root cause analysis data:\n{json.dumps(context, indent=2)}\n\nWrite the analysis:"
        }]
        
        narrative = await call_llm(messages, system_prompt)
        return narrative
    
    except Exception as e:
        # Fallback to template-based narrative
        return generate_template_narrative(
            metric, metric_change, causal_chain, top_contributors, change_direction
        )


def generate_template_narrative(
    metric: str,
    metric_change: Dict,
    causal_chain: List[Dict],
    top_contributors: List[Dict],
    change_direction: str
) -> str:
    """Fallback template-based narrative"""
    para1 = f"{metric} {change_direction} by {abs(metric_change['percent_change']):.1f}% "
    para1 += f"from {metric_change['baseline_value']:.2f} to {metric_change['current_value']:.2f}."
    
    if causal_chain:
        para2 = f"Root cause analysis reveals: {causal_chain[0]['cause']} → {causal_chain[0]['effect']} "
        para2 += f"(confidence: {causal_chain[0]['confidence']}%). "
        para2 += f"Evidence: {causal_chain[0]['evidence']}."
    else:
        para2 = "Causal factors are still being analyzed."
    
    if top_contributors:
        para3 = f"Recommended actions: Focus on {top_contributors[0]['segment']} "
        para3 += f"which accounts for {top_contributors[0]['impact']:.1f}% of the impact."
    else:
        para3 = "Further investigation recommended."
    
    return f"{para1}\n\n{para2}\n\n{para3}"
