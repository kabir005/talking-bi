import React, { useState, useEffect } from 'react';
import { Play, TrendingUp, Target, Zap, RefreshCw } from 'lucide-react';
import { apiClient, getDatasets } from '../../api/client';
import toast from 'react-hot-toast';

interface MLModel {
  model_id: string;
  dataset_id: string;
  target_column: string;
  algorithm: string;
  r2_score: number;
  mae: number;
  rmse: number;
  created_at: string;
}

interface Dataset {
  id: string;
  name: string;
  row_count: number;
  column_count: number;
}

interface MLPanelProps {
  datasetId?: string;
  onModelTrained?: (modelId: string) => void;
}

export const MLPanel: React.FC<MLPanelProps> = ({ datasetId: initialDatasetId, onModelTrained }) => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState(initialDatasetId || '');
  const [models, setModels] = useState<MLModel[]>([]);
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const [targetColumn, setTargetColumn] = useState('');
  const [taskType, setTaskType] = useState('auto');
  const [columns, setColumns] = useState<string[]>([]);
  const [loadingColumns, setLoadingColumns] = useState(false);

  useEffect(() => {
    loadDatasets();
  }, []);

  useEffect(() => {
    if (selectedDatasetId) {
      loadModels();
      loadColumns();
    }
  }, [selectedDatasetId]);

  const loadDatasets = async () => {
    try {
      const data = await getDatasets();
      setDatasets(data || []);
      if (data && data.length > 0 && !selectedDatasetId) {
        setSelectedDatasetId(data[0].id);
      }
    } catch (error) {
      console.error('Error loading datasets:', error);
      toast.error('Failed to load datasets');
    }
  };

  const loadModels = async () => {
    if (!selectedDatasetId) return;
    
    try {
      setLoading(true);
      const response = await apiClient.get(`/api/ml/models?dataset_id=${selectedDatasetId}`);
      setModels(response.data.models || []);
    } catch (error) {
      console.error('Error loading models:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadColumns = async () => {
    if (!selectedDatasetId) return;
    
    try {
      setLoadingColumns(true);
      console.log('Loading columns for dataset:', selectedDatasetId);
      
      // Try to get dataset details first
      const response = await apiClient.get(`/api/datasets/${selectedDatasetId}`);
      console.log('Dataset response:', response.data);
      
      let columnNames: string[] = [];
      
      // Try schema first (backend returns 'schema', not 'schema_json')
      if (response.data.schema && Object.keys(response.data.schema).length > 0) {
        columnNames = Object.keys(response.data.schema);
        console.log('Columns from schema:', columnNames);
      } 
      // Fallback: try to get from preview/data endpoint
      else {
        console.log('schema empty, trying preview endpoint...');
        try {
          const previewResponse = await apiClient.get(`/api/datasets/${selectedDatasetId}/preview?limit=1`);
          if (previewResponse.data.columns && previewResponse.data.columns.length > 0) {
            columnNames = previewResponse.data.columns;
            console.log('Columns from preview:', columnNames);
          }
        } catch (previewError) {
          console.error('Preview endpoint also failed:', previewError);
        }
      }
      
      setColumns(columnNames);
      
      if (columnNames.length === 0) {
        toast.error('No columns found in dataset. Please re-upload the dataset.');
      } else {
        toast.success(`Loaded ${columnNames.length} columns`);
      }
    } catch (error: any) {
      console.error('Error loading columns:', error);
      console.error('Error response:', error.response?.data);
      toast.error(`Failed to load dataset columns: ${error.response?.data?.detail || error.message}`);
      setColumns([]);
    } finally {
      setLoadingColumns(false);
    }
  };

  const trainModel = async () => {
    if (!selectedDatasetId) {
      toast.error('Please select a dataset');
      return;
    }

    if (!targetColumn) {
      toast.error('Please select a target column');
      return;
    }

    try {
      setTraining(true);
      const response = await apiClient.post('/api/ml/train', {
        dataset_id: selectedDatasetId,
        target_column: targetColumn,
        task_type: taskType
      });

      toast.success(`Model trained successfully! Algorithm: ${response.data.best_model}`);
      await loadModels();
      
      if (onModelTrained) {
        onModelTrained(response.data.model_id);
      }
    } catch (error: any) {
      console.error('Error training model:', error);
      toast.error(`Training failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setTraining(false);
    }
  };

  const deleteModel = async (modelId: string) => {
    if (!confirm('Are you sure you want to delete this model?')) {
      return;
    }

    try {
      await apiClient.delete(`/api/ml/models/${modelId}`);
      toast.success('Model deleted successfully');
      await loadModels();
    } catch (error) {
      console.error('Error deleting model:', error);
      toast.error('Failed to delete model');
    }
  };

  const retrainModel = async (modelId: string) => {
    try {
      setTraining(true);
      const response = await apiClient.post(`/api/ml/models/${modelId}/retrain`);
      toast.success(`Model retrained! Improvement: ${response.data.improvement.r2_delta.toFixed(3)}`);
      await loadModels();
    } catch (error) {
      console.error('Error retraining model:', error);
      toast.error('Retraining failed');
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="bg-surface rounded-xl border border-border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Zap className="w-6 h-6 text-accent" />
          Machine Learning
        </h2>
        <button
          onClick={loadModels}
          className="p-2 hover:bg-surface-2 rounded-lg transition-colors"
          title="Refresh"
          disabled={!selectedDatasetId}
        >
          <RefreshCw className="w-5 h-5 text-text-secondary" />
        </button>
      </div>

      {/* Train New Model */}
      <div className="mb-8 p-6 bg-surface-2 rounded-lg border border-border">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Target className="w-5 h-5 text-accent" />
          Train New Model
        </h3>
        
        <div className="space-y-4">
          {/* Dataset Selector */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Select Dataset
            </label>
            <select
              value={selectedDatasetId}
              onChange={(e) => {
                setSelectedDatasetId(e.target.value);
                setTargetColumn('');
              }}
              className="w-full px-4 py-2 bg-surface border border-border rounded-lg focus:ring-2 focus:ring-accent focus:border-transparent text-text-primary"
              disabled={training}
            >
              <option value="">Select a dataset...</option>
              {datasets.map(ds => (
                <option key={ds.id} value={ds.id}>
                  {ds.name} ({ds.row_count} rows, {ds.column_count} columns)
                </option>
              ))}
            </select>
          </div>

          {/* Target Column */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Target Column {loadingColumns && <span className="text-accent">(Loading...)</span>}
            </label>
            <select
              value={targetColumn}
              onChange={(e) => setTargetColumn(e.target.value)}
              className="w-full px-4 py-2 bg-surface border border-border rounded-lg focus:ring-2 focus:ring-accent focus:border-transparent text-text-primary"
              disabled={training || !selectedDatasetId || loadingColumns}
            >
              <option value="">
                {loadingColumns ? 'Loading columns...' : columns.length === 0 ? 'No columns available' : 'Select target column...'}
              </option>
              {columns.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
            {selectedDatasetId && !loadingColumns && columns.length === 0 && (
              <p className="text-xs text-red-400 mt-1">Failed to load columns. Please try refreshing.</p>
            )}
            {selectedDatasetId && !loadingColumns && columns.length > 0 && (
              <p className="text-xs text-text-tertiary mt-1">{columns.length} columns available</p>
            )}
          </div>

          {/* Task Type */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Task Type
            </label>
            <select
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
              className="w-full px-4 py-2 bg-surface border border-border rounded-lg focus:ring-2 focus:ring-accent focus:border-transparent text-text-primary"
              disabled={training}
            >
              <option value="auto">Auto-detect (Recommended)</option>
              <option value="regression">Regression - Predict continuous values (prices, quantities, scores)</option>
              <option value="classification">Classification - Predict categories (yes/no, high/medium/low)</option>
              <option value="time_series">Time Series - Forecast future values based on historical data</option>
              <option value="clustering">Clustering - Group similar data points together</option>
              <option value="anomaly_detection">Anomaly Detection - Identify unusual patterns</option>
            </select>
            <p className="text-xs text-text-tertiary mt-1">
              {taskType === 'auto' && 'System will automatically determine the best task type'}
              {taskType === 'regression' && 'Best for: Sales forecasting, price prediction, demand estimation'}
              {taskType === 'classification' && 'Best for: Customer churn, fraud detection, sentiment analysis'}
              {taskType === 'time_series' && 'Best for: Stock prices, weather forecasting, demand planning'}
              {taskType === 'clustering' && 'Best for: Customer segmentation, pattern discovery'}
              {taskType === 'anomaly_detection' && 'Best for: Fraud detection, quality control, system monitoring'}
            </p>
          </div>

          <button
            onClick={trainModel}
            disabled={training || !selectedDatasetId || !targetColumn}
            className="w-full bg-accent text-bg px-6 py-3 rounded-lg hover:bg-accent-hover disabled:bg-border disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 font-medium"
          >
            {training ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Training...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Train Model
              </>
            )}
          </button>
        </div>
      </div>

      {/* Trained Models */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-secondary" />
          Trained Models ({models.length})
        </h3>

        {!selectedDatasetId ? (
          <div className="text-center py-8 text-text-secondary">
            Please select a dataset to view models
          </div>
        ) : loading ? (
          <div className="text-center py-8 text-text-secondary">
            Loading models...
          </div>
        ) : models.length === 0 ? (
          <div className="text-center py-8 text-text-secondary">
            No models trained yet. Train your first model above!
          </div>
        ) : (
          <div className="space-y-4">
            {models.map(model => (
              <div
                key={model.model_id}
                className="p-4 border border-border rounded-lg hover:border-accent transition-colors bg-surface"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold">{model.algorithm}</h4>
                    <p className="text-sm text-text-secondary">Target: {model.target_column}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => retrainModel(model.model_id)}
                      className="p-2 text-accent hover:bg-surface-2 rounded-lg transition-colors"
                      title="Retrain"
                    >
                      <RefreshCw className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => deleteModel(model.model_id)}
                      className="p-2 text-red-500 hover:bg-surface-2 rounded-lg transition-colors"
                      title="Delete"
                    >
                      ×
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-text-secondary">R² Score:</span>
                    <span className="ml-2 font-semibold">
                      {model.r2_score?.toFixed(3) || 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-text-secondary">MAE:</span>
                    <span className="ml-2 font-semibold">
                      {model.mae?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-text-secondary">RMSE:</span>
                    <span className="ml-2 font-semibold">
                      {model.rmse?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                </div>

                <div className="mt-3 text-xs text-text-tertiary">
                  Created: {new Date(model.created_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
