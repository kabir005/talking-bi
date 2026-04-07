import React, { useState, useEffect } from 'react';
import { apiClient } from '../../api/client';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { TrendingUp, Info } from 'lucide-react';

interface FeatureImportanceData {
  feature: string;
  importance: number;
  shap_direction?: string;
}

interface FeatureImportanceProps {
  modelId: string;
  maxFeatures?: number;
}

export const FeatureImportance: React.FC<FeatureImportanceProps> = ({ 
  modelId, 
  maxFeatures = 10 
}) => {
  const [data, setData] = useState<FeatureImportanceData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (modelId && modelId !== 'undefined') {
      loadFeatureImportance();
    } else {
      setLoading(false);
      setError('No model selected');
    }
  }, [modelId]);

  const loadFeatureImportance = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get(`/api/ml/models/${modelId}`);
      const featureImportance = response.data.feature_importance || {};
      
      // Convert to array and sort by importance
      const importanceArray: FeatureImportanceData[] = Object.entries(featureImportance)
        .map(([feature, importance]) => ({
          feature,
          importance: typeof importance === 'number' ? importance : (importance as any).importance || 0,
          shap_direction: typeof importance === 'object' ? (importance as any).shap_direction : undefined
        }))
        .sort((a, b) => b.importance - a.importance)
        .slice(0, maxFeatures);
      
      setData(importanceArray);
    } catch (err: any) {
      console.error('Error loading feature importance:', err);
      setError(err.response?.data?.detail || 'Failed to load feature importance');
    } finally {
      setLoading(false);
    }
  };

  const getBarColor = (direction?: string) => {
    if (direction === 'positive') return '#22C55E';
    if (direction === 'negative') return '#EF4444';
    return '#3B82F6';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading feature importance...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">{error}</div>
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">No feature importance data available</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-blue-600" />
          Feature Importance
        </h3>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Info className="w-4 h-4" />
          <span>Top {data.length} features</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis 
            type="number" 
            domain={[0, 'auto']}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
          />
          <YAxis 
            type="category" 
            dataKey="feature" 
            width={90}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            formatter={(value: number) => `${(value * 100).toFixed(2)}%`}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              padding: '8px'
            }}
          />
          <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={getBarColor(entry.shap_direction)} 
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span className="text-gray-600">Positive Impact</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded"></div>
          <span className="text-gray-600">Negative Impact</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500 rounded"></div>
          <span className="text-gray-600">Neutral</span>
        </div>
      </div>

      {/* Feature List */}
      <div className="mt-6 space-y-2">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Feature Rankings</h4>
        {data.map((item, index) => (
          <div 
            key={item.feature}
            className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <div className="flex items-center gap-3">
              <span className="text-sm font-semibold text-gray-500 w-6">
                #{index + 1}
              </span>
              <span className="text-sm text-gray-800">{item.feature}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-800">
                {(item.importance * 100).toFixed(2)}%
              </span>
              {item.shap_direction && (
                <span className={`text-xs px-2 py-1 rounded ${
                  item.shap_direction === 'positive' 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-red-100 text-red-700'
                }`}>
                  {item.shap_direction}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
