import { useState, useEffect } from 'react';
import { X, RotateCcw, TrendingUp, TrendingDown } from 'lucide-react';
import { getScenarioParameters, simulateScenario, type ParameterConfig, type ScenarioResult, type SliderParam } from '../../api/scenario';
import toast from 'react-hot-toast';

interface WhatIfPanelProps {
  datasetId: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function WhatIfPanel({ datasetId, isOpen, onClose }: WhatIfPanelProps) {
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [parameters, setParameters] = useState<ParameterConfig[]>([]);
  const [sliderValues, setSliderValues] = useState<Record<string, number>>({});
  const [result, setResult] = useState<ScenarioResult | null>(null);

  useEffect(() => {
    if (isOpen && datasetId) {
      loadParameters();
    }
  }, [isOpen, datasetId]);

  const loadParameters = async () => {
    setLoading(true);
    try {
      const data = await getScenarioParameters(datasetId);
      setParameters(data.parameters);
      
      // Initialize slider values
      const initialValues: Record<string, number> = {};
      data.parameters.forEach(p => {
        initialValues[p.column] = p.default_pct;
      });
      setSliderValues(initialValues);
    } catch (error: any) {
      toast.error('Failed to load parameters');
    } finally {
      setLoading(false);
    }
  };

  const handleSliderChange = async (column: string, value: number) => {
    setSliderValues(prev => ({ ...prev, [column]: value }));
    
    // Debounced simulation
    if (simulateTimeout) clearTimeout(simulateTimeout);
    simulateTimeout = setTimeout(() => {
      runSimulation({ ...sliderValues, [column]: value });
    }, 300);
  };

  let simulateTimeout: number | null = null;

  const runSimulation = async (values: Record<string, number>) => {
    setSimulating(true);
    try {
      const params: SliderParam[] = parameters
        .filter(p => values[p.column] !== 0)
        .map(p => ({
          column: p.column,
          label: p.label,
          change_pct: values[p.column],
          change_type: p.change_type as any
        }));

      const result = await simulateScenario({
        dataset_id: datasetId,
        parameters: params
      });

      setResult(result);
    } catch (error: any) {
      toast.error('Simulation failed');
    } finally {
      setSimulating(false);
    }
  };

  const resetAll = () => {
    const resetValues: Record<string, number> = {};
    parameters.forEach(p => {
      resetValues[p.column] = 0;
    });
    setSliderValues(resetValues);
    setResult(null);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-[420px] bg-surface border-l border-border shadow-xl z-50 flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border flex items-center justify-between">
        <h2 className="text-lg font-semibold text-text-primary">What-If Scenario Modeling</h2>
        <button
          onClick={onClose}
          className="p-1 hover:bg-surface-elevated rounded transition-colors"
        >
          <X size={20} />
        </button>
      </div>

      {/* Instructions */}
      <div className="px-6 py-3 bg-surface-elevated border-b border-border">
        <p className="text-sm text-text-secondary">
          Drag sliders to simulate changes. KPIs update in real-time.
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
          </div>
        ) : (
          <div className="p-6 space-y-6">
            {/* Parameters Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-text-primary">Parameters</h3>
                <button
                  onClick={resetAll}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm bg-surface-elevated hover:bg-white/[0.04] rounded-lg transition-colors"
                >
                  <RotateCcw size={14} />
                  Reset All
                </button>
              </div>

              {parameters.map(param => (
                <div key={param.column} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-text-primary">
                      {param.label}
                    </label>
                    <span className={`text-sm font-semibold ${
                      sliderValues[param.column] > 0 ? 'text-green-500' :
                      sliderValues[param.column] < 0 ? 'text-red-500' :
                      'text-text-secondary'
                    }`}>
                      {sliderValues[param.column] > 0 ? '+' : ''}{sliderValues[param.column]}%
                    </span>
                  </div>
                  <input
                    type="range"
                    min={param.min_pct}
                    max={param.max_pct}
                    step={param.step}
                    value={sliderValues[param.column] || 0}
                    onChange={(e) => handleSliderChange(param.column, Number(e.target.value))}
                    className="w-full h-2 bg-surface-elevated rounded-lg appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-xs text-text-secondary">
                    <span>{param.min_pct}%</span>
                    <span>Current: {param.current_mean.toFixed(2)}</span>
                    <span>{param.max_pct}%</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Results Section */}
            {result && (
              <div className="space-y-4">
                {/* Narrative */}
                <div className="p-4 bg-accent/10 border border-accent/20 rounded-lg">
                  <p className="text-sm italic text-accent">{result.narrative}</p>
                </div>

                {/* KPI Deltas */}
                <div>
                  <h3 className="text-sm font-semibold text-text-primary mb-3">Impact on KPIs</h3>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(result.delta_kpis).map(([label, delta]) => (
                      <div
                        key={label}
                        className="p-3 bg-surface-elevated border border-border rounded-lg"
                      >
                        <div className="text-xs text-text-secondary mb-1">
                          {label.replace('_', ' ').toUpperCase()}
                        </div>
                        <div className={`flex items-center gap-2 text-lg font-bold ${
                          delta > 0 ? 'text-green-500' :
                          delta < 0 ? 'text-red-500' :
                          'text-text-secondary'
                        }`}>
                          {delta > 0 ? <TrendingUp size={18} /> : delta < 0 ? <TrendingDown size={18} /> : null}
                          {delta > 0 ? '+' : ''}{delta.toFixed(1)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Comparison Charts */}
                {result.chart_configs.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-text-primary mb-3">Comparison</h3>
                    <div className="space-y-3">
                      {result.chart_configs.map((chart, idx) => (
                        <div key={idx} className="p-4 bg-surface-elevated border border-border rounded-lg">
                          <div className="text-xs font-medium text-text-secondary mb-3">
                            {chart.title}
                          </div>
                          <div className="flex gap-4">
                            {chart.data.map((item: any, i: number) => (
                              <div key={i} className="flex-1">
                                <div className="text-xs text-text-secondary mb-1">{item.label}</div>
                                <div className="text-lg font-bold text-text-primary">
                                  {item.value.toLocaleString()}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {simulating && (
              <div className="flex items-center justify-center py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent"></div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
