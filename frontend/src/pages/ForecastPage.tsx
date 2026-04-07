import { useState, useEffect } from 'react';
import { getDatasets, generateForecast, autoDetectTimeColumn } from '../api/client';
import { Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface Dataset {
  id: string;
  name: string;
  row_count: number;
  column_count: number;
}

export default function ForecastPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const [targetColumn, setTargetColumn] = useState<string>('');
  const [timeColumn, setTimeColumn] = useState<string>('');
  const [periods, setPeriods] = useState<number>(12);
  const [method, setMethod] = useState<'auto' | 'linear' | 'ma'>('auto');
  const [loading, setLoading] = useState(false);
  const [forecastResult, setForecastResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      const data = await getDatasets();
      setDatasets(data);
    } catch (err) {
      console.error('Failed to load datasets:', err);
    }
  };

  const handleAutoDetectTime = async () => {
    if (!selectedDataset) return;
    
    try {
      const result = await autoDetectTimeColumn(selectedDataset);
      if (result.time_column) {
        setTimeColumn(result.time_column);
      }
    } catch (err) {
      console.error('Failed to auto-detect time column:', err);
    }
  };

  const handleGenerateForecast = async () => {
    if (!selectedDataset || !targetColumn) {
      setError('Please select dataset and target column');
      return;
    }

    setLoading(true);
    setError('');
    setForecastResult(null);

    try {
      const result = await generateForecast({
        dataset_id: selectedDataset,
        target_column: targetColumn,
        time_column: timeColumn || undefined,
        periods,
        method
      });

      setForecastResult(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate forecast');
    } finally {
      setLoading(false);
    }
  };

  const prepareChartData = () => {
    if (!forecastResult) return [];

    const historical = forecastResult.historical || [];
    const forecast = forecastResult.forecast || [];
    const confidenceLower = forecastResult.confidence_lower || [];
    const confidenceUpper = forecastResult.confidence_upper || [];

    const data: Array<{
      period: number;
      actual: number | null;
      forecast: number | null;
      lower: number | null;
      upper: number | null;
    }> = [];

    // Historical data
    historical.forEach((value: number, index: number) => {
      data.push({
        period: index + 1,
        actual: value,
        forecast: null,
        lower: null,
        upper: null
      });
    });

    // Forecast data
    forecast.forEach((value: number, index: number) => {
      data.push({
        period: historical.length + index + 1,
        actual: null,
        forecast: value,
        lower: confidenceLower[index],
        upper: confidenceUpper[index]
      });
    });

    return data;
  };

  return (
    <div className="min-h-screen bg-bg p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="font-heading text-4xl font-bold mb-8">Time-Series Forecasting</h1>

        {/* Configuration Panel */}
        <div className="bg-surface rounded-xl p-6 mb-8 shadow-lg border border-border">
          <h2 className="font-heading text-xl font-semibold mb-4">Forecast Configuration</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Dataset Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">Dataset</label>
              <select
                value={selectedDataset}
                onChange={(e) => setSelectedDataset(e.target.value)}
                className="w-full px-4 py-2 bg-bg border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">Select dataset...</option>
                {datasets.map((ds) => (
                  <option key={ds.id} value={ds.id}>
                    {ds.name} ({ds.row_count} rows)
                  </option>
                ))}
              </select>
            </div>

            {/* Target Column */}
            <div>
              <label className="block text-sm font-medium mb-2">Target Column</label>
              <input
                type="text"
                value={targetColumn}
                onChange={(e) => setTargetColumn(e.target.value)}
                placeholder="e.g., Revenue, Sales, Close"
                className="w-full px-4 py-2 bg-bg border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            {/* Time Column */}
            <div>
              <label className="block text-sm font-medium mb-2">Time Column (Optional)</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={timeColumn}
                  onChange={(e) => setTimeColumn(e.target.value)}
                  placeholder="e.g., Date, Month, Year"
                  className="flex-1 px-4 py-2 bg-bg border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <button
                  onClick={handleAutoDetectTime}
                  disabled={!selectedDataset}
                  className="px-4 py-2 bg-surface-2 hover:bg-surface-3 rounded-lg transition-colors disabled:opacity-50"
                >
                  Auto-detect
                </button>
              </div>
            </div>

            {/* Periods */}
            <div>
              <label className="block text-sm font-medium mb-2">Forecast Periods</label>
              <input
                type="number"
                value={periods}
                onChange={(e) => setPeriods(parseInt(e.target.value))}
                min="1"
                max="100"
                className="w-full px-4 py-2 bg-bg border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            {/* Method */}
            <div>
              <label className="block text-sm font-medium mb-2">Method</label>
              <select
                value={method}
                onChange={(e) => setMethod(e.target.value as any)}
                className="w-full px-4 py-2 bg-bg border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="auto">Auto (Recommended)</option>
                <option value="linear">Linear Regression</option>
                <option value="ma">Moving Average</option>
              </select>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerateForecast}
            disabled={loading || !selectedDataset || !targetColumn}
            className="mt-6 w-full px-6 py-3 bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating Forecast...' : 'Generate Forecast'}
          </button>

          {error && (
            <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        {forecastResult && (
          <div className="space-y-8">
            {/* Metrics */}
            <div className="bg-surface rounded-xl p-6 shadow-lg border border-border">
              <h2 className="font-heading text-xl font-semibold mb-4">Forecast Metrics</h2>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-bg rounded-lg p-4">
                  <div className="text-sm text-text-secondary mb-1">Method</div>
                  <div className="text-lg font-semibold">{forecastResult.method_used}</div>
                </div>
                
                {forecastResult.metrics?.mae && (
                  <div className="bg-bg rounded-lg p-4">
                    <div className="text-sm text-text-secondary mb-1">MAE</div>
                    <div className="text-lg font-semibold">{forecastResult.metrics.mae.toFixed(2)}</div>
                  </div>
                )}
                
                {forecastResult.metrics?.rmse && (
                  <div className="bg-bg rounded-lg p-4">
                    <div className="text-sm text-text-secondary mb-1">RMSE</div>
                    <div className="text-lg font-semibold">{forecastResult.metrics.rmse.toFixed(2)}</div>
                  </div>
                )}
                
                {forecastResult.metrics?.r2_score !== undefined && (
                  <div className="bg-bg rounded-lg p-4">
                    <div className="text-sm text-text-secondary mb-1">R² Score</div>
                    <div className="text-lg font-semibold">{forecastResult.metrics.r2_score.toFixed(3)}</div>
                  </div>
                )}
              </div>

              {forecastResult.metrics?.trend && (
                <div className="mt-4 p-4 bg-bg rounded-lg">
                  <div className="text-sm text-text-secondary mb-1">Trend</div>
                  <div className="text-lg font-semibold capitalize">{forecastResult.metrics.trend}</div>
                </div>
              )}
            </div>

            {/* Chart */}
            <div className="bg-surface rounded-xl p-6 shadow-lg border border-border">
              <h2 className="font-heading text-xl font-semibold mb-4">Forecast Visualization</h2>
              
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={prepareChartData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    dataKey="period" 
                    stroke="#9CA3AF"
                    label={{ value: 'Period', position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  
                  {/* Confidence Interval */}
                  <Area
                    type="monotone"
                    dataKey="upper"
                    stroke="none"
                    fill="#3B82F6"
                    fillOpacity={0.1}
                    name="Upper Confidence"
                  />
                  <Area
                    type="monotone"
                    dataKey="lower"
                    stroke="none"
                    fill="#3B82F6"
                    fillOpacity={0.1}
                    name="Lower Confidence"
                  />
                  
                  {/* Actual Values */}
                  <Line
                    type="monotone"
                    dataKey="actual"
                    stroke="#10B981"
                    strokeWidth={2}
                    dot={{ fill: '#10B981', r: 4 }}
                    name="Historical"
                  />
                  
                  {/* Forecast */}
                  <Line
                    type="monotone"
                    dataKey="forecast"
                    stroke="#3B82F6"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={{ fill: '#3B82F6', r: 4 }}
                    name="Forecast"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Forecast Values Table */}
            <div className="bg-surface rounded-xl p-6 shadow-lg border border-border">
              <h2 className="font-heading text-xl font-semibold mb-4">Forecast Values</h2>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 px-4">Period</th>
                      <th className="text-right py-2 px-4">Forecast</th>
                      <th className="text-right py-2 px-4">Lower Bound</th>
                      <th className="text-right py-2 px-4">Upper Bound</th>
                    </tr>
                  </thead>
                  <tbody>
                    {forecastResult.forecast.map((value: number, index: number) => (
                      <tr key={index} className="border-b border-border/50">
                        <td className="py-2 px-4">{forecastResult.historical.length + index + 1}</td>
                        <td className="text-right py-2 px-4">{value.toFixed(2)}</td>
                        <td className="text-right py-2 px-4">{forecastResult.confidence_lower[index].toFixed(2)}</td>
                        <td className="text-right py-2 px-4">{forecastResult.confidence_upper[index].toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
