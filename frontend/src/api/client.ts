import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Upload file
export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/api/upload/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

// Datasets
export const getDatasets = async () => {
  const response = await apiClient.get('/api/datasets');
  return response.data;
};

export const getDataset = async (id: string) => {
  const response = await apiClient.get(`/api/datasets/${id}`);
  return response.data;
};

export const getDatasetPreview = async (id: string, limit = 50) => {
  const response = await apiClient.get(`/api/datasets/${id}/preview?limit=${limit}`);
  return response.data;
};

export const deleteDataset = async (id: string) => {
  const response = await apiClient.delete(`/api/datasets/${id}`);
  return response.data;
};

// Dashboards
export const generateDashboard = async (data: any) => {
  const response = await apiClient.post('/api/dashboards/generate', data);
  return response.data;
};

export const getDashboards = async () => {
  const response = await apiClient.get('/api/dashboards');
  return response.data;
};

export const getDashboard = async (id: string) => {
  const response = await apiClient.get(`/api/dashboards/${id}`);
  return response.data;
};

export const updateDashboard = async (id: string, data: any) => {
  const response = await apiClient.put(`/api/dashboards/${id}`, data);
  return response.data;
};

export const deleteDashboard = async (id: string) => {
  const response = await apiClient.delete(`/api/dashboards/${id}`);
  return response.data;
};

// Query
export const submitQuery = async (data: { dataset_id: string; query: string; role?: string }) => {
  const response = await apiClient.post('/api/query', data);
  return response.data;
};

export const getQueryHistory = async (dataset_id?: string) => {
  const url = dataset_id ? `/api/query/history?dataset_id=${dataset_id}` : '/api/query/history';
  const response = await apiClient.get(url);
  return response.data;
};

// ML Models
export const trainModel = async (data: { dataset_id: string; target_column: string; task_type?: string }) => {
  const response = await apiClient.post('/api/ml/train', data);
  return response.data;
};

export const getMLModels = async (dataset_id?: string) => {
  const url = dataset_id ? `/api/ml/models?dataset_id=${dataset_id}` : '/api/ml/models';
  const response = await apiClient.get(url);
  return response.data;
};

export const getMLModel = async (id: string) => {
  const response = await apiClient.get(`/api/ml/models/${id}`);
  return response.data;
};

export const predictWithModel = async (model_id: string, input_data: any) => {
  const response = await apiClient.post(`/api/ml/models/${model_id}/predict`, { input_data });
  return response.data;
};

export const runWhatIfSimulation = async (data: { model_id: string; dataset_id: string; variable: string; change_percent: number }) => {
  const response = await apiClient.post('/api/ml/what-if', data);
  return response.data;
};

// NL Query
export const runNLQuery = async (dataset_id: string, query: string) => {
  const response = await apiClient.post('/api/nl-query/', { dataset_id, query });
  return response.data;
};

// ── NEW: Conversation (multi-turn) ─────────────────────────────────────────

export interface ConversationPayload {
  dataset_id: string;
  query: string;
  history: Array<{ role: string; content: string }>;
  schema?: Record<string, any>;
  kpis?: Record<string, any> | null;
}

export const conversationChat = async (payload: ConversationPayload) => {
  const response = await apiClient.post('/api/conversation/chat', payload);
  return response.data;
};

// ── NEW: Pipeline Status (one-shot, non-SSE) ───────────────────────────────

export const getPipelineStatusOnce = async (datasetId: string) => {
  const response = await apiClient.get(`/api/pipeline/status/${datasetId}/once`);
  return response.data as { status: string; progress: number; error: string | null };
};

// ── NEW: Forecast API ──────────────────────────────────────────────────────

export interface ForecastRequest {
  dataset_id: string;
  target_column: string;
  time_column?: string;
  periods?: number;
  method?: 'auto' | 'linear' | 'ma';
}

export interface MultiForecastRequest {
  dataset_id: string;
  target_columns: string[];
  time_column?: string;
  periods?: number;
}

export const generateForecast = async (request: ForecastRequest) => {
  const response = await apiClient.post('/api/forecast/generate', request);
  return response.data;
};

export const generateMultipleForecasts = async (request: MultiForecastRequest) => {
  const response = await apiClient.post('/api/forecast/generate-multiple', request);
  return response.data;
};

export const autoDetectTimeColumn = async (datasetId: string) => {
  const response = await apiClient.get(`/api/forecast/auto-detect-time/${datasetId}`);
  return response.data;
};

// ── NEW: Localization API ──────────────────────────────────────────────────

export interface FormatCurrencyRequest {
  amount: number;
  currency?: 'INR' | 'USD' | 'EUR' | 'GBP' | 'AUTO';
  use_indian_format?: boolean;
  decimals?: number;
}

export interface FormatDualCurrencyRequest {
  amount: number;
  primary_currency?: 'INR' | 'USD' | 'EUR' | 'GBP';
  secondary_currency?: 'INR' | 'USD' | 'EUR' | 'GBP';
  exchange_rate?: number;
  decimals?: number;
}

export const formatCurrency = async (request: FormatCurrencyRequest) => {
  const response = await apiClient.post('/api/localization/format-currency', request);
  return response.data;
};

export const formatDualCurrency = async (request: FormatDualCurrencyRequest) => {
  const response = await apiClient.post('/api/localization/format-dual-currency', request);
  return response.data;
};

export const getIndianFiscalYear = async (date: string) => {
  const response = await apiClient.post('/api/localization/indian-fiscal-year', { date });
  return response.data;
};

export const getCurrencySymbols = async () => {
  const response = await apiClient.get('/api/localization/currency-symbols');
  return response.data;
};

export const getExchangeRates = async () => {
  const response = await apiClient.get('/api/localization/exchange-rates');
  return response.data;
};

// ── NEW: Alerts API ────────────────────────────────────────────────────────

export interface ThresholdAlertConfig {
  column: string;
  threshold: number;
  condition?: 'above' | 'below' | 'equal';
  alert_name?: string;
}

export interface ConsecutiveDeclineConfig {
  column: string;
  periods?: number;
  min_decline_pct?: number;
}

export interface AnomalyDetectionConfig {
  column: string;
  method?: 'zscore' | 'iqr' | 'isolation_forest';
  threshold?: number;
}

export interface SpikeDetectionConfig {
  column: string;
  threshold?: number;
}

export interface AlertCheckRequest {
  dataset_id: string;
  threshold_alerts?: ThresholdAlertConfig[];
  consecutive_decline?: ConsecutiveDeclineConfig[];
  anomaly_detection?: AnomalyDetectionConfig[];
  missing_data_threshold?: number;
  spike_detection?: SpikeDetectionConfig[];
}

export const checkAlerts = async (request: AlertCheckRequest) => {
  const response = await apiClient.post('/api/alerts/check', request);
  return response.data;
};

export const checkThresholdAlert = async (
  datasetId: string,
  column: string,
  threshold: number,
  condition: 'above' | 'below' | 'equal' = 'below'
) => {
  const response = await apiClient.post('/api/alerts/check-threshold', null, {
    params: { dataset_id: datasetId, column, threshold, condition }
  });
  return response.data;
};

export const checkAnomalies = async (
  datasetId: string,
  column: string,
  method: 'zscore' | 'iqr' | 'isolation_forest' = 'zscore',
  threshold: number = 3.0
) => {
  const response = await apiClient.post('/api/alerts/check-anomalies', null, {
    params: { dataset_id: datasetId, column, method, threshold }
  });
  return response.data;
};

export const getAlertTemplates = async () => {
  const response = await apiClient.get('/api/alerts/templates');
  return response.data;
};

// ── NEW: Doc2Chart API ─────────────────────────────────────────────────────

export const uploadDocument = async (file: File, mergeStrategy: 'concat' | 'join' = 'concat') => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post(`/api/doc2chart/upload-document?merge_strategy=${mergeStrategy}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const extractTablesOnly = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/api/doc2chart/extract-tables', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getSupportedFormats = async () => {
  const response = await apiClient.get('/api/doc2chart/supported-formats');
  return response.data;
};

// ── NEW: Dataset Diff API ──────────────────────────────────────────────────

export interface DatasetDiffRequest {
  dataset1_id: string;
  dataset2_id: string;
  compare_distributions?: boolean;
}

export const compareDatasets = async (request: DatasetDiffRequest) => {
  const response = await apiClient.post('/api/dataset-diff/compare', request);
  return response.data;
};

export const compareColumnDistribution = async (
  dataset1Id: string,
  dataset2Id: string,
  column: string
) => {
  const response = await apiClient.post('/api/dataset-diff/compare-column', {
    dataset1_id: dataset1Id,
    dataset2_id: dataset2Id,
    column
  });
  return response.data;
};

export const compareRows = async (
  dataset1Id: string,
  dataset2Id: string,
  keyColumns?: string[]
) => {
  const response = await apiClient.post('/api/dataset-diff/compare-rows', {
    dataset1_id: dataset1Id,
    dataset2_id: dataset2Id,
    key_columns: keyColumns
  });
  return response.data;
};

export const getSchemaDiff = async (dataset1Id: string, dataset2Id: string) => {
  const response = await apiClient.get(`/api/dataset-diff/schema-diff/${dataset1Id}/${dataset2Id}`);
  return response.data;
};

// ── NEW: Story Mode API ────────────────────────────────────────────────────

export interface ExecutiveSummaryRequest {
  dataset_name: string;
  kpis: Record<string, any>;
  insights: Array<Record<string, any>>;
  trends?: Array<Record<string, any>>;
  recommendations?: string[];
}

export const generateExecutiveSummary = async (request: ExecutiveSummaryRequest) => {
  const response = await apiClient.post('/api/story/executive-summary', request);
  return response.data;
};

export const getDashboardStory = async (dashboardId: string) => {
  const response = await apiClient.get(`/api/story/dashboard-story/${dashboardId}`);
  return response.data;
};

export const generateInsightStory = async (insight: Record<string, any>, context?: string) => {
  const response = await apiClient.post('/api/story/insight-story', { insight, context });
  return response.data;
};

// ── NEW: LLM Provider API ──────────────────────────────────────────────────

export const getLLMStatus = async () => {
  const response = await apiClient.get('/api/llm/status');
  return response.data;
};

export const listOllamaModels = async () => {
  const response = await apiClient.get('/api/llm/ollama/models');
  return response.data;
};

export const testLLM = async (prompt: string, provider?: string) => {
  const response = await apiClient.post('/api/llm/test', { prompt, provider });
  return response.data;
};

export const getPrivacyMode = async () => {
  const response = await apiClient.get('/api/llm/privacy-mode');
  return response.data;
};

