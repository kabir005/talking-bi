"""
Dataset Diff Service - Compare two datasets side-by-side
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DatasetDiffService:
    """Compare two datasets and generate diff report"""
    
    @staticmethod
    async def compare_schemas(df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, Any]:
        """
        Compare schemas of two datasets
        
        Returns:
            Schema comparison with added/removed/changed columns
        """
        cols1 = set(df1.columns)
        cols2 = set(df2.columns)
        
        added = list(cols2 - cols1)
        removed = list(cols1 - cols2)
        common = list(cols1 & cols2)
        
        # Check dtype changes in common columns
        dtype_changes = []
        for col in common:
            if df1[col].dtype != df2[col].dtype:
                dtype_changes.append({
                    "column": col,
                    "old_dtype": str(df1[col].dtype),
                    "new_dtype": str(df2[col].dtype)
                })
        
        return {
            "dataset1_columns": len(df1.columns),
            "dataset2_columns": len(df2.columns),
            "added_columns": added,
            "removed_columns": removed,
            "common_columns": common,
            "dtype_changes": dtype_changes,
            "schema_match": len(added) == 0 and len(removed) == 0 and len(dtype_changes) == 0
        }
    
    @staticmethod
    async def compare_kpis(df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, Any]:
        """
        Compare KPIs between two datasets
        
        Returns:
            KPI deltas with percentage changes
        """
        kpis = {}
        
        # Row count
        kpis["row_count"] = {
            "dataset1": len(df1),
            "dataset2": len(df2),
            "delta": len(df2) - len(df1),
            "percent_change": ((len(df2) - len(df1)) / len(df1) * 100) if len(df1) > 0 else 0
        }
        
        # Column count
        kpis["column_count"] = {
            "dataset1": len(df1.columns),
            "dataset2": len(df2.columns),
            "delta": len(df2.columns) - len(df1.columns)
        }
        
        # Compare numeric columns
        numeric_cols = set(df1.select_dtypes(include=[np.number]).columns) & \
                      set(df2.select_dtypes(include=[np.number]).columns)
        
        numeric_kpis = {}
        for col in numeric_cols:
            try:
                mean1 = df1[col].mean()
                mean2 = df2[col].mean()
                sum1 = df1[col].sum()
                sum2 = df2[col].sum()
                
                numeric_kpis[col] = {
                    "mean": {
                        "dataset1": float(mean1) if not pd.isna(mean1) else None,
                        "dataset2": float(mean2) if not pd.isna(mean2) else None,
                        "delta": float(mean2 - mean1) if not pd.isna(mean1) and not pd.isna(mean2) else None,
                        "percent_change": float((mean2 - mean1) / mean1 * 100) if mean1 != 0 and not pd.isna(mean1) else None
                    },
                    "sum": {
                        "dataset1": float(sum1) if not pd.isna(sum1) else None,
                        "dataset2": float(sum2) if not pd.isna(sum2) else None,
                        "delta": float(sum2 - sum1) if not pd.isna(sum1) and not pd.isna(sum2) else None,
                        "percent_change": float((sum2 - sum1) / sum1 * 100) if sum1 != 0 and not pd.isna(sum1) else None
                    }
                }
            except Exception as e:
                logger.warning(f"Could not compare column {col}: {str(e)}")
        
        kpis["numeric_columns"] = numeric_kpis
        
        return kpis
    
    @staticmethod
    async def compare_distributions(df1: pd.DataFrame, df2: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Compare distribution of a specific column
        
        Returns:
            Distribution comparison with statistics
        """
        if column not in df1.columns or column not in df2.columns:
            raise ValueError(f"Column {column} not found in both datasets")
        
        result = {
            "column": column,
            "dtype": str(df1[column].dtype)
        }
        
        # Numeric column
        if pd.api.types.is_numeric_dtype(df1[column]):
            result["type"] = "numeric"
            result["statistics"] = {
                "dataset1": {
                    "mean": float(df1[column].mean()) if not pd.isna(df1[column].mean()) else None,
                    "median": float(df1[column].median()) if not pd.isna(df1[column].median()) else None,
                    "std": float(df1[column].std()) if not pd.isna(df1[column].std()) else None,
                    "min": float(df1[column].min()) if not pd.isna(df1[column].min()) else None,
                    "max": float(df1[column].max()) if not pd.isna(df1[column].max()) else None
                },
                "dataset2": {
                    "mean": float(df2[column].mean()) if not pd.isna(df2[column].mean()) else None,
                    "median": float(df2[column].median()) if not pd.isna(df2[column].median()) else None,
                    "std": float(df2[column].std()) if not pd.isna(df2[column].std()) else None,
                    "min": float(df2[column].min()) if not pd.isna(df2[column].min()) else None,
                    "max": float(df2[column].max()) if not pd.isna(df2[column].max()) else None
                }
            }
        
        # Categorical column
        else:
            result["type"] = "categorical"
            
            # Value counts
            vc1 = df1[column].value_counts().head(10).to_dict()
            vc2 = df2[column].value_counts().head(10).to_dict()
            
            result["value_counts"] = {
                "dataset1": {str(k): int(v) for k, v in vc1.items()},
                "dataset2": {str(k): int(v) for k, v in vc2.items()}
            }
            
            # Unique values
            result["unique_values"] = {
                "dataset1": int(df1[column].nunique()),
                "dataset2": int(df2[column].nunique())
            }
        
        return result
    
    @staticmethod
    async def generate_diff_report(
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        dataset1_name: str = "Dataset 1",
        dataset2_name: str = "Dataset 2"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive diff report
        
        Returns:
            Complete comparison report
        """
        logger.info(f"Generating diff report: {dataset1_name} vs {dataset2_name}")
        
        # Schema comparison
        schema_diff = await DatasetDiffService.compare_schemas(df1, df2)
        
        # KPI comparison
        kpi_diff = await DatasetDiffService.compare_kpis(df1, df2)
        
        # Distribution comparison for common numeric columns
        common_numeric = set(df1.select_dtypes(include=[np.number]).columns) & \
                        set(df2.select_dtypes(include=[np.number]).columns)
        
        distributions = []
        for col in list(common_numeric)[:5]:  # Limit to 5 columns
            try:
                dist = await DatasetDiffService.compare_distributions(df1, df2, col)
                distributions.append(dist)
            except Exception as e:
                logger.warning(f"Could not compare distribution for {col}: {str(e)}")
        
        # Missing data comparison
        missing1 = df1.isnull().sum().to_dict()
        missing2 = df2.isnull().sum().to_dict()
        
        missing_diff = {}
        for col in set(list(missing1.keys()) + list(missing2.keys())):
            m1 = missing1.get(col, 0)
            m2 = missing2.get(col, 0)
            if m1 > 0 or m2 > 0:
                missing_diff[col] = {
                    "dataset1": int(m1),
                    "dataset2": int(m2),
                    "delta": int(m2 - m1)
                }
        
        # Generate AI insights
        insights = await DatasetDiffService._generate_insights(
            schema_diff, kpi_diff, distributions, missing_diff, dataset1_name, dataset2_name
        )
        
        return {
            "dataset1_name": dataset1_name,
            "dataset2_name": dataset2_name,
            "schema_diff": schema_diff,
            "kpi_diff": kpi_diff,
            "distributions": distributions,
            "missing_data_diff": missing_diff,
            "insights": insights,
            "summary": {
                "schema_match": schema_diff["schema_match"],
                "row_delta": kpi_diff["row_count"]["delta"],
                "row_percent_change": kpi_diff["row_count"]["percent_change"],
                "columns_added": len(schema_diff["added_columns"]),
                "columns_removed": len(schema_diff["removed_columns"])
            }
        }
    
    @staticmethod
    async def _generate_insights(
        schema_diff: Dict,
        kpi_diff: Dict,
        distributions: List[Dict],
        missing_diff: Dict,
        dataset1_name: str,
        dataset2_name: str
    ) -> List[Dict[str, str]]:
        """Generate actionable insights from comparison"""
        insights = []
        
        # Row count insights
        row_change = kpi_diff["row_count"]["percent_change"]
        if abs(row_change) > 10:
            severity = "high" if abs(row_change) > 50 else "medium"
            direction = "increased" if row_change > 0 else "decreased"
            insights.append({
                "type": "data_volume",
                "severity": severity,
                "title": f"Significant Data Volume Change",
                "message": f"Row count {direction} by {abs(row_change):.1f}% ({kpi_diff['row_count']['delta']:+d} rows). This could indicate data growth, filtering, or data quality issues.",
                "recommendation": "Verify if this change is expected. Check for data pipeline issues if unexpected."
            })
        
        # Schema changes insights
        if schema_diff["added_columns"]:
            insights.append({
                "type": "schema_change",
                "severity": "medium",
                "title": "New Columns Detected",
                "message": f"{len(schema_diff['added_columns'])} new columns added: {', '.join(schema_diff['added_columns'][:3])}{'...' if len(schema_diff['added_columns']) > 3 else ''}",
                "recommendation": "Review new columns for data quality and ensure downstream processes can handle them."
            })
        
        if schema_diff["removed_columns"]:
            insights.append({
                "type": "schema_change",
                "severity": "high",
                "title": "Columns Removed",
                "message": f"{len(schema_diff['removed_columns'])} columns removed: {', '.join(schema_diff['removed_columns'][:3])}{'...' if len(schema_diff['removed_columns']) > 3 else ''}",
                "recommendation": "Critical: Verify if dependent reports or dashboards use these columns. Update queries and visualizations."
            })
        
        # Numeric column insights
        for col, data in kpi_diff.get("numeric_columns", {}).items():
            mean_change = data["mean"].get("percent_change")
            if mean_change and abs(mean_change) > 20:
                severity = "high" if abs(mean_change) > 50 else "medium"
                direction = "increased" if mean_change > 0 else "decreased"
                insights.append({
                    "type": "metric_change",
                    "severity": severity,
                    "title": f"{col} Changed Significantly",
                    "message": f"Average {col} {direction} by {abs(mean_change):.1f}% ({data['mean']['dataset1']:.2f} → {data['mean']['dataset2']:.2f})",
                    "recommendation": f"Investigate what caused this change in {col}. Could indicate business trends or data quality issues."
                })
        
        # Missing data insights
        for col, data in missing_diff.items():
            delta = data["delta"]
            if abs(delta) > 10:
                severity = "medium" if abs(delta) < 50 else "high"
                direction = "increased" if delta > 0 else "decreased"
                insights.append({
                    "type": "data_quality",
                    "severity": severity,
                    "title": f"Missing Data Change in {col}",
                    "message": f"Missing values {direction} by {abs(delta)} ({data['dataset1']} → {data['dataset2']})",
                    "recommendation": "Check data collection process. Increased missing data may indicate upstream issues."
                })
        
        # Data type changes
        if schema_diff.get("dtype_changes"):
            for change in schema_diff["dtype_changes"]:
                insights.append({
                    "type": "schema_change",
                    "severity": "high",
                    "title": f"Data Type Changed: {change['column']}",
                    "message": f"Column {change['column']} type changed from {change['old_dtype']} to {change['new_dtype']}",
                    "recommendation": "Critical: This may break existing queries and calculations. Update data processing logic."
                })
        
        # Overall assessment
        if not insights:
            insights.append({
                "type": "summary",
                "severity": "low",
                "title": "Datasets Are Similar",
                "message": f"No significant differences detected between {dataset1_name} and {dataset2_name}",
                "recommendation": "Datasets appear consistent. Continue monitoring for changes."
            })
        else:
            # Add summary insight
            high_severity = sum(1 for i in insights if i["severity"] == "high")
            if high_severity > 0:
                insights.insert(0, {
                    "type": "summary",
                    "severity": "high",
                    "title": "Action Required",
                    "message": f"Found {len(insights)} differences including {high_severity} critical issues",
                    "recommendation": "Review all high-severity changes immediately to prevent downstream issues."
                })
        
        return insights
    
    @staticmethod
    async def find_common_rows(
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        key_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Find common and unique rows between datasets
        
        Args:
            df1: First dataset
            df2: Second dataset
            key_columns: Columns to use as keys (if None, uses all common columns)
            
        Returns:
            Row comparison with common/unique counts
        """
        if key_columns is None:
            key_columns = list(set(df1.columns) & set(df2.columns))
        
        if not key_columns:
            return {
                "error": "No common columns to compare",
                "common_rows": 0,
                "unique_to_dataset1": len(df1),
                "unique_to_dataset2": len(df2)
            }
        
        try:
            # Create composite keys
            df1_keys = df1[key_columns].apply(lambda x: tuple(x), axis=1)
            df2_keys = df2[key_columns].apply(lambda x: tuple(x), axis=1)
            
            # Find common and unique
            common = set(df1_keys) & set(df2_keys)
            unique1 = set(df1_keys) - set(df2_keys)
            unique2 = set(df2_keys) - set(df1_keys)
            
            return {
                "key_columns": key_columns,
                "common_rows": len(common),
                "unique_to_dataset1": len(unique1),
                "unique_to_dataset2": len(unique2),
                "total_dataset1": len(df1),
                "total_dataset2": len(df2),
                "match_percentage": (len(common) / max(len(df1), len(df2)) * 100) if max(len(df1), len(df2)) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Row comparison failed: {str(e)}")
            raise
