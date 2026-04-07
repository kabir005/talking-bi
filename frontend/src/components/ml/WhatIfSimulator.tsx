import React, { useState, useEffect } from 'react';
import { apiClient } from '../../api/client';
import { Sliders, Play, RotateCcw, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface Parameter {
  name: string;
  currentValue: number;
  minValue: number;
  maxValue: number;
  newValue: number;
}

interface SimulationResult {
  baseline_value: number;
  predicted_value: number;
  impact: number;
  impact_pct: number;
}

interface WhatIfSimulatorProps {
  datasetId: string;
  targetMetric: string;
  onSimulationComplete?: (result: SimulationResult) => void;
}

export const WhatIfSimulator: React.FC<WhatIfSimulatorProps> = ({ 
  datasetId, 
  targetMetric,
  onSimulationComplete 
}) => {
  const [parameters, setParameters] = useState<Parameter[]>([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadParameters();
  }, [datasetId]);

  const loadParameters = async () => {
    try {
      setLoading(true);
      setError(null);

      // Validate datasetId
      if (!datasetId) {
        setError('No dataset selected');
        setLoading(false);
        return;
      }

      // Get dataset schema
      const response = await apiClient.get(`/api/datasets/${datasetId}`);
      const schema = response.data.schema || {};
      
      // Get sample data to determine ranges
      const dataResponse = await apiClient.get(`/api/datasets/${datasetId}/data?limit=100`);
      const rows = dataResponse.data.rows || [];

      // Extract numeric parameters
      const numericParams: Parameter[] = [];
      
      for (const [colName, colType] of Object.entries(schema)) {
        if (colType === 'numeric' || colType === 'currency' || colType === 'percentage') {
          if (colName !== targetMetric) {
            const values = rows.map((r: any) => parseFloat(r[colName])).filter((v: number) => !isNaN(v));
            
            if (values.length > 0) {
              const min = Math.min(...values);
              const max = Math.max(...values);
              const avg = values.reduce((a: number, b: number) => a + b, 0) / values.length;
              
              numericParams.push({
                name: colName,
                currentValue: avg,
                minValue: min,
                maxValue: max,
                newValue: avg
              });
            }
          }
        }
      }

      setParameters(numericParams.slice(0, 10)); // Limit to top 10
    } catch (err: any) {
      console.error('Error loading parameters:', err);
      setError(err.response?.data?.detail || 'Failed to load parameters');
    } finally {
      setLoading(false);
    }
  };

  const handleParameterChange = (paramName: string, newValue: number) => {
    setParameters(prev => 
      prev.map(p => 
        p.name === paramName ? { ...p, newValue } : p
      )
    );
  };

  const resetParameter = (paramName: string) => {
    setParameters(prev => 
      prev.map(p => 
        p.name === paramName ? { ...p, newValue: p.currentValue } : p
      )
    );
  };

  const resetAll = () => {
    setParameters(prev => 
      prev.map(p => ({ ...p, newValue: p.currentValue }))
    );
    setResult(null);
  };

  const runSimulation = async () => {
    try {
      setSimulating(true);
      setError(null);

      // Build parameter changes object
      const parameterChanges: Record<string, number> = {};
      parameters.forEach(p => {
        if (p.newValue !== p.currentValue) {
          parameterChanges[p.name] = p.newValue;
        }
      });

      if (Object.keys(parameterChanges).length === 0) {
        setError('No parameters changed. Adjust at least one parameter to run simulation.');
        return;
      }

      const response = await apiClient.post('/api/ml/what-if/simulate', {
        dataset_id: datasetId,
        parameter_changes: parameterChanges,
        target_metric: targetMetric
      });

      setResult(response.data);
      
      if (onSimulationComplete) {
        onSimulationComplete(response.data);
      }
    } catch (err: any) {
      console.error('Error running simulation:', err);
      setError(err.response?.data?.detail || 'Simulation failed');
    } finally {
      setSimulating(false);
    }
  };

  const getChangePercentage = (param: Parameter) => {
    if (param.currentValue === 0) return 0;
    return ((param.newValue - param.currentValue) / param.currentValue) * 100;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-gray-500">Loading parameters...</div>
        </div>
      </div>
    );
  }

  if (parameters.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-gray-500">No numeric parameters available for simulation</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          <Sliders className="w-6 h-6 text-blue-600" />
          What-If Simulator
        </h3>
        <button
          onClick={resetAll}
          className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          Reset All
        </button>
      </div>

      <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="text-sm text-blue-800">
          <strong>Target Metric:</strong> {targetMetric}
        </div>
        <div className="text-xs text-blue-600 mt-1">
          Adjust parameters below to see predicted impact on {targetMetric}
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 rounded-lg border border-red-200">
          <div className="text-sm text-red-800">{error}</div>
        </div>
      )}

      {/* Parameters */}
      <div className="space-y-6 mb-6">
        {parameters.map(param => {
          const changePercent = getChangePercentage(param);
          const hasChanged = Math.abs(changePercent) > 0.1;

          return (
            <div key={param.name} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium text-gray-700">
                    {param.name}
                  </label>
                  {hasChanged && (
                    <span className={`text-xs px-2 py-1 rounded ${
                      changePercent > 0 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {changePercent > 0 ? '+' : ''}{changePercent.toFixed(1)}%
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-gray-800">
                    {param.newValue.toFixed(2)}
                  </span>
                  <button
                    onClick={() => resetParameter(param.name)}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                    title="Reset to baseline"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                <span className="text-xs text-gray-500 w-16">
                  {param.minValue.toFixed(0)}
                </span>
                <input
                  type="range"
                  min={param.minValue}
                  max={param.maxValue}
                  step={(param.maxValue - param.minValue) / 100}
                  value={param.newValue}
                  onChange={(e) => handleParameterChange(param.name, parseFloat(e.target.value))}
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
                <span className="text-xs text-gray-500 w-16 text-right">
                  {param.maxValue.toFixed(0)}
                </span>
              </div>
              
              <div className="text-xs text-gray-500">
                Baseline: {param.currentValue.toFixed(2)}
              </div>
            </div>
          );
        })}
      </div>

      {/* Run Simulation Button */}
      <button
        onClick={runSimulation}
        disabled={simulating}
        className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 font-medium mb-6"
      >
        {simulating ? (
          <>
            <RotateCcw className="w-5 h-5 animate-spin" />
            Simulating...
          </>
        ) : (
          <>
            <Play className="w-5 h-5" />
            Run Simulation
          </>
        )}
      </button>

      {/* Results */}
      {result && (
        <div className="p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border border-blue-200">
          <h4 className="text-lg font-semibold text-gray-800 mb-4">Simulation Results</h4>
          
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="p-4 bg-white rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Baseline Value</div>
              <div className="text-2xl font-bold text-gray-800">
                {result.baseline_value.toFixed(2)}
              </div>
            </div>
            
            <div className="p-4 bg-white rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Predicted Value</div>
              <div className="text-2xl font-bold text-blue-600">
                {result.predicted_value.toFixed(2)}
              </div>
            </div>
          </div>

          <div className="p-4 bg-white rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-gray-600">Impact</div>
              <div className="flex items-center gap-2">
                {result.impact_pct > 0 ? (
                  <TrendingUp className="w-5 h-5 text-green-600" />
                ) : result.impact_pct < 0 ? (
                  <TrendingDown className="w-5 h-5 text-red-600" />
                ) : (
                  <Minus className="w-5 h-5 text-gray-600" />
                )}
                <span className={`text-2xl font-bold ${
                  result.impact_pct > 0 
                    ? 'text-green-600' 
                    : result.impact_pct < 0 
                    ? 'text-red-600' 
                    : 'text-gray-600'
                }`}>
                  {result.impact_pct > 0 ? '+' : ''}{result.impact_pct.toFixed(2)}%
                </span>
              </div>
            </div>
            <div className="text-sm text-gray-600">
              Absolute change: {result.impact > 0 ? '+' : ''}{result.impact.toFixed(2)}
            </div>
          </div>

          <div className="mt-4 p-3 bg-blue-100 rounded-lg">
            <div className="text-sm text-blue-800">
              {result.impact_pct > 0 ? (
                <>
                  <strong>Positive Impact:</strong> The parameter changes would increase {targetMetric} by {Math.abs(result.impact_pct).toFixed(2)}%.
                </>
              ) : result.impact_pct < 0 ? (
                <>
                  <strong>Negative Impact:</strong> The parameter changes would decrease {targetMetric} by {Math.abs(result.impact_pct).toFixed(2)}%.
                </>
              ) : (
                <>
                  <strong>No Impact:</strong> The parameter changes would have minimal effect on {targetMetric}.
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
