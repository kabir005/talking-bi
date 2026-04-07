"""
Alert Engine - Threshold alerts, consecutive decline detection, anomaly alerts
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

AlertType = Literal["threshold", "consecutive_decline", "anomaly", "missing_data", "spike"]


class AlertEngine:
    """Generate alerts based on data conditions"""
    
    @staticmethod
    async def check_threshold_alerts(
        df: pd.DataFrame,
        column: str,
        threshold: float,
        condition: Literal["above", "below", "equal"] = "below",
        alert_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Check for threshold violations
        
        Args:
            df: DataFrame
            column: Column to check
            threshold: Threshold value
            condition: "above", "below", or "equal"
            alert_name: Custom alert name
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        if column not in df.columns:
            return alerts
        
        # Ensure column is numeric
        try:
            df[column] = pd.to_numeric(df[column], errors='coerce')
        except Exception:
            return alerts
        
        # Get latest value
        latest_value = df[column].dropna().iloc[-1] if len(df[column].dropna()) > 0 else None
        
        if latest_value is None or pd.isna(latest_value):
            return alerts
        
        # Check condition
        triggered = False
        if condition == "below" and latest_value < threshold:
            triggered = True
            message = f"{column} is below threshold: {latest_value:.2f} < {threshold:.2f}"
        elif condition == "above" and latest_value > threshold:
            triggered = True
            message = f"{column} exceeds threshold: {latest_value:.2f} > {threshold:.2f}"
        elif condition == "equal" and abs(latest_value - threshold) < 0.01:
            triggered = True
            message = f"{column} equals threshold: {latest_value:.2f} ≈ {threshold:.2f}"
        
        if triggered:
            alerts.append({
                "type": "threshold",
                "severity": "high" if condition == "below" else "medium",
                "column": column,
                "message": message,
                "current_value": float(latest_value),
                "threshold": float(threshold),
                "condition": condition,
                "timestamp": datetime.now().isoformat(),
                "alert_name": alert_name or f"{column}_threshold"
            })
        
        return alerts
    
    @staticmethod
    async def check_consecutive_decline(
        df: pd.DataFrame,
        column: str,
        periods: int = 3,
        min_decline_pct: float = 5.0
    ) -> List[Dict[str, Any]]:
        """
        Detect consecutive periods of decline
        
        Args:
            df: DataFrame
            column: Column to check
            periods: Number of consecutive periods
            min_decline_pct: Minimum decline percentage to trigger alert
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        if column not in df.columns or len(df) < periods + 1:
            return alerts
        
        # Ensure column is numeric
        try:
            df[column] = pd.to_numeric(df[column], errors='coerce')
        except Exception:
            return alerts
        
        # Get last N+1 values, drop NaN
        values = df[column].tail(periods + 1).dropna().values
        
        if len(values) < periods + 1:
            return alerts
        
        # Check if all consecutive changes are negative
        consecutive_declines = 0
        total_decline_pct = 0
        
        for i in range(1, len(values)):
            if values[i] < values[i-1] and values[i-1] != 0:
                consecutive_declines += 1
                decline_pct = ((values[i-1] - values[i]) / abs(values[i-1])) * 100
                total_decline_pct += decline_pct
            else:
                break
        
        if consecutive_declines >= periods and total_decline_pct >= min_decline_pct:
            alerts.append({
                "type": "consecutive_decline",
                "severity": "high",
                "column": column,
                "message": f"{column} has declined for {consecutive_declines} consecutive periods (total: {total_decline_pct:.1f}%)",
                "periods": consecutive_declines,
                "total_decline_pct": float(total_decline_pct),
                "current_value": float(values[-1]),
                "previous_value": float(values[0]),
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    @staticmethod
    async def check_anomaly_alerts(
        df: pd.DataFrame,
        column: str,
        method: Literal["zscore", "iqr", "isolation_forest"] = "zscore",
        threshold: float = 3.0
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in data
        
        Args:
            df: DataFrame
            column: Column to check
            method: Detection method
            threshold: Sensitivity threshold
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        if column not in df.columns or len(df) < 10:
            return alerts
        
        # Ensure column is numeric
        try:
            df[column] = pd.to_numeric(df[column], errors='coerce')
        except Exception:
            return alerts
        
        values = df[column].dropna()
        
        if len(values) < 10:
            return alerts
        
        # Detect anomalies based on method
        if method == "zscore":
            anomalies = AlertEngine._detect_zscore_anomalies(values, threshold)
        elif method == "iqr":
            anomalies = AlertEngine._detect_iqr_anomalies(values)
        else:
            anomalies = AlertEngine._detect_isolation_forest_anomalies(values)
        
        # Get latest value
        latest_idx = len(values) - 1
        if latest_idx in anomalies:
            latest_value = values.iloc[latest_idx]
            mean_value = values.mean()
            std_value = values.std()
            
            alerts.append({
                "type": "anomaly",
                "severity": "medium",
                "column": column,
                "message": f"Anomaly detected in {column}: {latest_value:.2f} (mean: {mean_value:.2f}, std: {std_value:.2f})",
                "current_value": float(latest_value),
                "mean": float(mean_value),
                "std": float(std_value),
                "method": method,
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    @staticmethod
    def _detect_zscore_anomalies(values: pd.Series, threshold: float = 3.0) -> List[int]:
        """Detect anomalies using Z-score method"""
        mean = values.mean()
        std = values.std()
        
        if std == 0:
            return []
        
        z_scores = np.abs((values - mean) / std)
        anomalies = np.where(z_scores > threshold)[0].tolist()
        
        return anomalies
    
    @staticmethod
    def _detect_iqr_anomalies(values: pd.Series) -> List[int]:
        """Detect anomalies using IQR method"""
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = np.where((values < lower_bound) | (values > upper_bound))[0].tolist()
        
        return anomalies
    
    @staticmethod
    def _detect_isolation_forest_anomalies(values: pd.Series) -> List[int]:
        """Detect anomalies using Isolation Forest"""
        try:
            from sklearn.ensemble import IsolationForest
            
            X = values.values.reshape(-1, 1)
            clf = IsolationForest(contamination=0.1, random_state=42)
            predictions = clf.fit_predict(X)
            
            anomalies = np.where(predictions == -1)[0].tolist()
            return anomalies
        except ImportError:
            # Fallback to Z-score if sklearn not available
            return AlertEngine._detect_zscore_anomalies(values)
    
    @staticmethod
    async def check_missing_data_alerts(
        df: pd.DataFrame,
        threshold_pct: float = 10.0
    ) -> List[Dict[str, Any]]:
        """
        Alert on columns with high missing data percentage
        
        Args:
            df: DataFrame
            threshold_pct: Percentage threshold for alert
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        for column in df.columns:
            missing_count = df[column].isna().sum()
            missing_pct = (missing_count / len(df)) * 100
            
            if missing_pct >= threshold_pct:
                alerts.append({
                    "type": "missing_data",
                    "severity": "low" if missing_pct < 30 else "medium",
                    "column": column,
                    "message": f"{column} has {missing_pct:.1f}% missing data ({missing_count}/{len(df)} rows)",
                    "missing_count": int(missing_count),
                    "missing_pct": float(missing_pct),
                    "total_rows": len(df),
                    "timestamp": datetime.now().isoformat()
                })
        
        return alerts
    
    @staticmethod
    async def check_spike_alerts(
        df: pd.DataFrame,
        column: str,
        spike_threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect sudden spikes (value > spike_threshold * moving average)
        
        Args:
            df: DataFrame
            column: Column to check
            spike_threshold: Multiplier for spike detection
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        if column not in df.columns or len(df) < 5:
            return alerts
        
        # Ensure column is numeric
        try:
            df[column] = pd.to_numeric(df[column], errors='coerce')
        except Exception:
            return alerts
        
        values = df[column].dropna()
        
        if len(values) < 5:
            return alerts
        
        # Calculate moving average (last 5 periods)
        ma = values.rolling(window=5).mean()
        
        # Check latest value
        latest_value = values.iloc[-1]
        latest_ma = ma.iloc[-1]
        
        if pd.notna(latest_ma) and latest_ma > 0 and latest_value > spike_threshold * latest_ma:
            spike_pct = ((latest_value - latest_ma) / latest_ma) * 100
            
            alerts.append({
                "type": "spike",
                "severity": "high",
                "column": column,
                "message": f"Spike detected in {column}: {latest_value:.2f} is {spike_pct:.1f}% above moving average ({latest_ma:.2f})",
                "current_value": float(latest_value),
                "moving_average": float(latest_ma),
                "spike_pct": float(spike_pct),
                "threshold": float(spike_threshold),
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    @staticmethod
    async def run_all_checks(
        df: pd.DataFrame,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run all configured alert checks
        
        Args:
            df: DataFrame
            config: Alert configuration
                {
                    "threshold_alerts": [{"column": "Revenue", "threshold": 50000, "condition": "below"}],
                    "consecutive_decline": [{"column": "Sales", "periods": 3}],
                    "anomaly_detection": [{"column": "Orders", "method": "zscore"}],
                    "missing_data_threshold": 10.0,
                    "spike_detection": [{"column": "Traffic", "threshold": 2.0}]
                }
        
        Returns:
            {
                "alerts": List[Dict],
                "summary": Dict,
                "timestamp": str
            }
        """
        all_alerts = []
        
        # Threshold alerts
        for alert_config in config.get("threshold_alerts", []):
            alerts = await AlertEngine.check_threshold_alerts(
                df,
                alert_config["column"],
                alert_config["threshold"],
                alert_config.get("condition", "below"),
                alert_config.get("alert_name")
            )
            all_alerts.extend(alerts)
        
        # Consecutive decline
        for alert_config in config.get("consecutive_decline", []):
            alerts = await AlertEngine.check_consecutive_decline(
                df,
                alert_config["column"],
                alert_config.get("periods", 3),
                alert_config.get("min_decline_pct", 5.0)
            )
            all_alerts.extend(alerts)
        
        # Anomaly detection
        for alert_config in config.get("anomaly_detection", []):
            alerts = await AlertEngine.check_anomaly_alerts(
                df,
                alert_config["column"],
                alert_config.get("method", "zscore"),
                alert_config.get("threshold", 3.0)
            )
            all_alerts.extend(alerts)
        
        # Missing data
        missing_threshold = config.get("missing_data_threshold", 10.0)
        missing_alerts = await AlertEngine.check_missing_data_alerts(df, missing_threshold)
        all_alerts.extend(missing_alerts)
        
        # Spike detection
        for alert_config in config.get("spike_detection", []):
            alerts = await AlertEngine.check_spike_alerts(
                df,
                alert_config["column"],
                alert_config.get("threshold", 2.0)
            )
            all_alerts.extend(alerts)
        
        # Summary
        summary = {
            "total_alerts": len(all_alerts),
            "by_severity": {
                "high": sum(1 for a in all_alerts if a.get("severity") == "high"),
                "medium": sum(1 for a in all_alerts if a.get("severity") == "medium"),
                "low": sum(1 for a in all_alerts if a.get("severity") == "low")
            },
            "by_type": {}
        }
        
        for alert in all_alerts:
            alert_type = alert.get("type", "unknown")
            summary["by_type"][alert_type] = summary["by_type"].get(alert_type, 0) + 1
        
        logger.info(f"Alert check complete: {len(all_alerts)} alerts generated")
        
        return {
            "alerts": all_alerts,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
