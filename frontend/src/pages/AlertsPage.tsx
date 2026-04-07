import { useState, useEffect } from 'react';
import { Bell, AlertTriangle, TrendingDown, Activity, Database, Zap, Plus, Play, Trash2 } from 'lucide-react';
import { getDatasets, checkAlerts, getAlertTemplates, apiClient, type AlertCheckRequest } from '../api/client';
import toast from 'react-hot-toast';

interface Alert {
  type: string;
  severity: 'high' | 'medium' | 'low';
  message: string;
  column?: string;
  value?: number;
  threshold?: number;
}

interface AlertConfig {
  id: string;
  name: string;
  dataset_id: string;
  dataset_name: string;
  config: AlertCheckRequest;
}

export default function AlertsPage() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const [columns, setColumns] = useState<string[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertSummary, setAlertSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<any[]>([]);
  const [savedConfigs, setSavedConfigs] = useState<AlertConfig[]>([]);
  
  // Alert configuration
  const [thresholdColumn, setThresholdColumn] = useState('');
  const [thresholdValue, setThresholdValue] = useState('');
  const [thresholdCondition, setThresholdCondition] = useState<'above' | 'below' | 'equal'>('below');
  
  const [anomalyColumn, setAnomalyColumn] = useState('');
  const [anomalyMethod, setAnomalyMethod] = useState<'zscore' | 'iqr' | 'isolation_forest'>('zscore');
  
  const [declineColumn, setDeclineColumn] = useState('');
  const [declinePeriods, setDeclinePeriods] = useState('3');

  useEffect(() => {
    loadDatasets();
    loadTemplates();
    loadSavedConfigs();
  }, []);

  useEffect(() => {
    if (selectedDataset) {
      loadColumns();
    } else {
      setColumns([]);
    }
  }, [selectedDataset]);

  const loadDatasets = async () => {
    try {
      const data = await getDatasets();
      console.log('Datasets loaded:', data);
      // Backend returns array directly, not wrapped in {datasets: [...]}
      setDatasets(Array.isArray(data) ? data : (data.datasets || []));
    } catch (error) {
      console.error('Failed to load datasets:', error);
      toast.error('Failed to load datasets');
    }
  };

  const loadColumns = async () => {
    try {
      const response = await apiClient.get(`/api/datasets/${selectedDataset}`);
      const schema = response.data.schema || {};
      setColumns(Object.keys(schema));
    } catch (error) {
      console.error('Failed to load columns:', error);
      toast.error('Failed to load columns');
    }
  };

  const loadTemplates = async () => {
    try {
      const data = await getAlertTemplates();
      setTemplates(data.templates || []);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const loadSavedConfigs = () => {
    const saved = localStorage.getItem('alert_configs');
    if (saved) {
      setSavedConfigs(JSON.parse(saved));
    }
  };

  const saveConfig = () => {
    if (!selectedDataset) {
      toast.error('Please select a dataset');
      return;
    }

    const dataset = datasets.find(d => d.id === selectedDataset);
    const config: AlertConfig = {
      id: Date.now().toString(),
      name: `Alert Config - ${dataset?.name}`,
      dataset_id: selectedDataset,
      dataset_name: dataset?.name || '',
      config: buildAlertRequest()
    };

    const updated = [...savedConfigs, config];
    setSavedConfigs(updated);
    localStorage.setItem('alert_configs', JSON.stringify(updated));
    toast.success('Alert configuration saved');
  };

  const deleteConfig = (id: string) => {
    const updated = savedConfigs.filter(c => c.id !== id);
    setSavedConfigs(updated);
    localStorage.setItem('alert_configs', JSON.stringify(updated));
    toast.success('Configuration deleted');
  };

  const buildAlertRequest = (): AlertCheckRequest => {
    const request: AlertCheckRequest = {
      dataset_id: selectedDataset,
      threshold_alerts: [],
      consecutive_decline: [],
      anomaly_detection: [],
      spike_detection: [],
      missing_data_threshold: 10.0
    };

    if (thresholdColumn && thresholdValue) {
      request.threshold_alerts!.push({
        column: thresholdColumn,
        threshold: parseFloat(thresholdValue),
        condition: thresholdCondition
      });
    }

    if (anomalyColumn) {
      request.anomaly_detection!.push({
        column: anomalyColumn,
        method: anomalyMethod,
        threshold: 3.0
      });
    }

    if (declineColumn) {
      request.consecutive_decline!.push({
        column: declineColumn,
        periods: parseInt(declinePeriods),
        min_decline_pct: 5.0
      });
    }

    return request;
  };

  const runAlertCheck = async () => {
    if (!selectedDataset) {
      toast.error('Please select a dataset');
      return;
    }

    setLoading(true);
    try {
      const request = buildAlertRequest();
      const result = await checkAlerts(request);
      
      setAlerts(result.alerts || []);
      setAlertSummary(result.summary || null);
      
      if (result.alerts && result.alerts.length > 0) {
        toast.success(`Found ${result.alerts.length} alert(s)`);
      } else {
        toast.success('No alerts triggered');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to check alerts');
    } finally {
      setLoading(false);
    }
  };

  const runSavedConfig = async (config: AlertConfig) => {
    setLoading(true);
    try {
      const result = await checkAlerts(config.config);
      setAlerts(result.alerts || []);
      setAlertSummary(result.summary || null);
      setSelectedDataset(config.dataset_id);
      
      if (result.alerts && result.alerts.length > 0) {
        toast.success(`Found ${result.alerts.length} alert(s)`);
      } else {
        toast.success('No alerts triggered');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to check alerts');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-500 bg-red-500/10 border-red-500/20';
      case 'medium': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
      case 'low': return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
      default: return 'text-text-secondary bg-surface-elevated border-border';
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'threshold': return AlertTriangle;
      case 'consecutive_decline': return TrendingDown;
      case 'anomaly': return Activity;
      case 'missing_data': return Database;
      case 'spike': return Zap;
      default: return Bell;
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-heading font-bold text-text-primary">Alert Engine</h1>
          <p className="text-sm text-text-secondary mt-1">
            Configure and monitor alerts for your datasets
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={saveConfig}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
              bg-surface-elevated text-text-primary border border-border
              hover:bg-white/[0.04] transition-colors"
          >
            <Plus size={16} />
            Save Config
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Dataset Selection */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Dataset Selection</h2>
            <select
              value={selectedDataset}
              onChange={(e) => setSelectedDataset(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-surface-elevated border border-border
                text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            >
              <option value="">Select a dataset...</option>
              {datasets.map((dataset) => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.name} ({dataset.row_count} rows)
                </option>
              ))}
            </select>
          </div>

          {/* Threshold Alerts */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
              <AlertTriangle size={20} className="text-yellow-500" />
              Threshold Alerts
            </h2>
            <div className="grid grid-cols-3 gap-4">
              <select
                value={thresholdColumn}
                onChange={(e) => setThresholdColumn(e.target.value)}
                disabled={!selectedDataset}
                className="px-4 py-2.5 rounded-lg bg-surface-elevated border border-border
                  text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-primary/50
                  disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">Select column...</option>
                {columns.map((col) => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
              <input
                type="number"
                placeholder="Threshold value"
                value={thresholdValue}
                onChange={(e) => setThresholdValue(e.target.value)}
                className="px-4 py-2.5 rounded-lg bg-surface-elevated border border-border
                  text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
              <select
                value={thresholdCondition}
                onChange={(e) => setThresholdCondition(e.target.value as any)}
                className="px-4 py-2.5 rounded-lg bg-surface-elevated border border-border
                  text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                <option value="below">Below</option>
                <option value="above">Above</option>
                <option value="equal">Equal</option>
              </select>
            </div>
          </div>

          {/* Anomaly Detection */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
              <Activity size={20} className="text-purple-500" />
              Anomaly Detection
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <select
                value={anomalyColumn}
                onChange={(e) => setAnomalyColumn(e.target.value)}
                disabled={!selectedDataset}
                className="px-4 py-2.5 rounded-lg bg-surface-elevated border border-border
                  text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-primary/50
                  disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">Select column...</option>
                {columns.map((col) => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
              <select
                value={anomalyMethod}
                onChange={(e) => setAnomalyMethod(e.target.value as any)}
                className="px-4 py-2.5 rounded-lg bg-surface-elevated border border-border
                  text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                <option value="zscore">Z-Score</option>
                <option value="iqr">IQR</option>
                <option value="isolation_forest">Isolation Forest</option>
              </select>
            </div>
          </div>

          {/* Consecutive Decline */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
              <TrendingDown size={20} className="text-red-500" />
              Consecutive Decline
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <select
                value={declineColumn}
                onChange={(e) => setDeclineColumn(e.target.value)}
                disabled={!selectedDataset}
                className="px-4 py-2.5 rounded-lg bg-surface-elevated border border-border
                  text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-primary/50
                  disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">Select column...</option>
                {columns.map((col) => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
              <input
                type="number"
                placeholder="Periods (default: 3)"
                value={declinePeriods}
                onChange={(e) => setDeclinePeriods(e.target.value)}
                className="px-4 py-2.5 rounded-lg bg-surface-elevated border border-border
                  text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
          </div>

          {/* Run Button */}
          <button
            onClick={runAlertCheck}
            disabled={loading || !selectedDataset}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg text-sm font-semibold
              bg-gradient-to-r from-primary to-[#5AC8FA] text-white
              hover:shadow-glow-sm transition-all duration-300 hover:scale-[1.02]
              disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            <Play size={16} />
            {loading ? 'Checking Alerts...' : 'Run Alert Check'}
          </button>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Summary */}
          {alertSummary && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-text-primary mb-4">Summary</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-secondary">Total Alerts</span>
                  <span className="text-lg font-bold text-text-primary">{alertSummary.total_alerts}</span>
                </div>
                {alertSummary.by_severity && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-red-500">High</span>
                      <span className="text-sm font-semibold text-red-500">{alertSummary.by_severity.high || 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-yellow-500">Medium</span>
                      <span className="text-sm font-semibold text-yellow-500">{alertSummary.by_severity.medium || 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-blue-500">Low</span>
                      <span className="text-sm font-semibold text-blue-500">{alertSummary.by_severity.low || 0}</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Saved Configurations */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Saved Configs</h2>
            <div className="space-y-2">
              {savedConfigs.length === 0 ? (
                <p className="text-sm text-text-secondary">No saved configurations</p>
              ) : (
                savedConfigs.map((config) => (
                  <div
                    key={config.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-surface-elevated border border-border"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-text-primary truncate">{config.dataset_name}</p>
                      <p className="text-xs text-text-secondary truncate">{config.name}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => runSavedConfig(config)}
                        className="p-1.5 rounded hover:bg-white/[0.04] text-primary transition-colors"
                      >
                        <Play size={14} />
                      </button>
                      <button
                        onClick={() => deleteConfig(config.id)}
                        className="p-1.5 rounded hover:bg-white/[0.04] text-red-500 transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Templates */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Templates</h2>
            <div className="space-y-2">
              {templates.map((template, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-surface-elevated border border-border hover:border-primary/50 transition-colors cursor-pointer"
                >
                  <p className="text-sm font-medium text-text-primary">{template.name}</p>
                  <p className="text-xs text-text-secondary mt-1">{template.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      {alerts.length > 0 && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-text-primary mb-4">Triggered Alerts</h2>
          <div className="space-y-3">
            {alerts.map((alert, idx) => {
              const Icon = getAlertIcon(alert.type);
              return (
                <div
                  key={idx}
                  className={`flex items-start gap-4 p-4 rounded-lg border ${getSeverityColor(alert.severity)}`}
                >
                  <Icon size={20} className="mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-semibold uppercase">{alert.type.replace('_', ' ')}</span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-current/10">{alert.severity}</span>
                    </div>
                    <p className="text-sm">{alert.message}</p>
                    {alert.column && (
                      <p className="text-xs mt-1 opacity-75">Column: {alert.column}</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
