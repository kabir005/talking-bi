import React, { useState, useEffect } from 'react';
import { apiClient } from '../../api/client';
import { 
  ScatterChart, 
  Scatter, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Line,
  ComposedChart,
  ReferenceLine
} from 'recharts';
import { Target, AlertCircle } from 'lucide-react';

interface PredictionData {
  actual: number;
  predicted: number;
  date?: string;
  index: number;
}

interface PredictionChartProps {
  modelId: string;
  datasetId: string;
  maxPoints?: number;
}

export const PredictionChart: React.FC<PredictionChartProps> = ({ 
  modelId, 
  datasetId,
  maxPoints = 100 
}) => {
  const [data, setData] = useState<PredictionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<{
    r2: number;
    mae: number;
    rmse: number;
  } | null>(null);

  useEffect(() => {
    if (modelId && modelId !== 'undefined' && datasetId && datasetId !== 'undefined') {
      loadPredictions();
    } else {
      setLoading(false);
      setError('No model or dataset selected');
    }
  }, [modelId, datasetId]);

  const loadPredictions = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get model details
      const modelResponse = await apiClient.get(`/api/ml/models/${modelId}`);
      const model = modelResponse.data;
      
      setMetrics({
        r2: model.r2_score || model.metrics?.r2_score || 0,
        mae: model.mae || model.metrics?.mae || 0,
        rmse: model.rmse || model.metrics?.rmse || 0
      });

      // Get dataset (not used but needed for API call)
      await apiClient.get(`/api/datasets/${datasetId}`);

      // Load data from dataset
      const dataResponse = await apiClient.get(`/api/datasets/${datasetId}/data?limit=${maxPoints}`);
      const rows = dataResponse.data.rows || [];

      // Make predictions
      const predictResponse = await apiClient.post(`/api/ml/models/${modelId}/predict`, {
        data: rows
      });

      const predictions = predictResponse.data.predictions || [];
      const targetColumn = model.target_column;

      // Combine actual and predicted
      const combinedData: PredictionData[] = rows.map((row: any, index: number) => ({
        actual: parseFloat(row[targetColumn]) || 0,
        predicted: predictions[index] || 0,
        date: row.date || row.Date || row.DATE,
        index: index + 1
      }));

      setData(combinedData);
    } catch (err: any) {
      console.error('Error loading predictions:', err);
      setError(err.response?.data?.detail || 'Failed to load predictions');
    } finally {
      setLoading(false);
    }
  };

  const calculateResiduals = () => {
    return data.map(d => ({
      index: d.index,
      residual: d.actual - d.predicted
    }));
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-gray-500">Loading predictions...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-red-500 flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            {error}
          </div>
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-gray-500">No prediction data available</div>
        </div>
      </div>
    );
  }

  const residuals = calculateResiduals();
  const minValue = Math.min(...data.map(d => Math.min(d.actual, d.predicted)));
  const maxValue = Math.max(...data.map(d => Math.max(d.actual, d.predicted)));

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          <Target className="w-6 h-6 text-blue-600" />
          Prediction Analysis
        </h3>
        {metrics && (
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1">
              <span className="text-gray-600">R²:</span>
              <span className="font-semibold text-gray-800">{metrics.r2.toFixed(3)}</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-gray-600">MAE:</span>
              <span className="font-semibold text-gray-800">{metrics.mae.toFixed(2)}</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-gray-600">RMSE:</span>
              <span className="font-semibold text-gray-800">{metrics.rmse.toFixed(2)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Actual vs Predicted Scatter Plot */}
      <div className="mb-8">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Actual vs Predicted</h4>
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              type="number" 
              dataKey="actual" 
              name="Actual"
              domain={[minValue * 0.95, maxValue * 1.05]}
              label={{ value: 'Actual Values', position: 'insideBottom', offset: -10 }}
            />
            <YAxis 
              type="number" 
              dataKey="predicted" 
              name="Predicted"
              domain={[minValue * 0.95, maxValue * 1.05]}
              label={{ value: 'Predicted Values', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              formatter={(value: number) => value.toFixed(2)}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                padding: '8px'
              }}
            />
            <Legend />
            <Scatter 
              name="Predictions" 
              data={data} 
              fill="#3B82F6"
              opacity={0.6}
            />
            <ReferenceLine 
              segment={[
                { x: minValue, y: minValue },
                { x: maxValue, y: maxValue }
              ]}
              stroke="#EF4444"
              strokeWidth={2}
              strokeDasharray="5 5"
              label={{ value: 'Perfect Prediction', position: 'top' }}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Time Series View */}
      <div className="mb-8">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Predictions Over Time</h4>
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={data} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="index"
              label={{ value: 'Sample Index', position: 'insideBottom', offset: -10 }}
            />
            <YAxis 
              label={{ value: 'Value', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              formatter={(value: number) => value.toFixed(2)}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                padding: '8px'
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="actual" 
              stroke="#22C55E" 
              strokeWidth={2}
              dot={false}
              name="Actual"
            />
            <Line 
              type="monotone" 
              dataKey="predicted" 
              stroke="#3B82F6" 
              strokeWidth={2}
              dot={false}
              name="Predicted"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Residuals Plot */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Residuals (Actual - Predicted)</h4>
        <ResponsiveContainer width="100%" height={250}>
          <ComposedChart data={residuals} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="index"
              label={{ value: 'Sample Index', position: 'insideBottom', offset: -10 }}
            />
            <YAxis 
              label={{ value: 'Residual', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              formatter={(value: number) => value.toFixed(2)}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                padding: '8px'
              }}
            />
            <ReferenceLine y={0} stroke="#6B7280" strokeWidth={2} />
            <Scatter 
              name="Residuals" 
              data={residuals} 
              fill="#8B5CF6"
              opacity={0.6}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Summary Statistics */}
      <div className="mt-6 grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="text-sm text-gray-600">Total Samples</div>
          <div className="text-2xl font-bold text-gray-800">{data.length}</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-600">Avg Residual</div>
          <div className="text-2xl font-bold text-gray-800">
            {(residuals.reduce((sum, r) => sum + r.residual, 0) / residuals.length).toFixed(2)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-600">Model Accuracy</div>
          <div className="text-2xl font-bold text-green-600">
            {metrics ? `${(metrics.r2 * 100).toFixed(1)}%` : 'N/A'}
          </div>
        </div>
      </div>
    </div>
  );
};
