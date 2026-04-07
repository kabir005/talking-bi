import { useEffect, useState } from 'react';
import { Brain, Plus, TrendingUp, Target, Zap, Sliders } from 'lucide-react';
import { getMLModels } from '../api/client';
import { MLPanel } from '../components/ml/MLPanel';
import { FeatureImportance } from '../components/ml/FeatureImportance';
import { PredictionChart } from '../components/ml/PredictionChart';
import { WhatIfSimulator } from '../components/ml/WhatIfSimulator';
import toast from 'react-hot-toast';

interface MLModel {
  model_id: string;
  name?: string;
  dataset_id: string;
  target_column: string;
  task_type?: string;
  algorithm: string;
  r2_score?: number;
  mae?: number;
  rmse?: number;
  metrics?: any;
  created_at: string;
}

export default function MLModelsPage() {
  const [models, setModels] = useState<MLModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<MLModel | null>(null);
  const [activeTab, setActiveTab] = useState<'train' | 'models' | 'predict' | 'whatif'>('models');

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getMLModels();
      // Backend returns {models: [...], count: ...}
      setModels(data.models || data || []);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load models';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading ML models...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button
            onClick={loadModels}
            className="px-4 py-2 bg-accent text-bg rounded-lg hover:bg-accent-hover"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-heading font-bold mb-2">ML Models</h1>
          <p className="text-text-secondary">
            Train and manage machine learning models
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border mb-6">
        <button
          onClick={() => setActiveTab('train')}
          className={`
            px-6 py-3 font-semibold transition-colors
            ${activeTab === 'train'
              ? 'text-accent border-b-2 border-accent'
              : 'text-text-secondary hover:text-text'
            }
          `}
        >
          Train Model
        </button>
        <button
          onClick={() => setActiveTab('models')}
          className={`
            px-6 py-3 font-semibold transition-colors
            ${activeTab === 'models'
              ? 'text-accent border-b-2 border-accent'
              : 'text-text-secondary hover:text-text'
            }
          `}
        >
          Models ({models.length})
        </button>
        <button
          onClick={() => setActiveTab('predict')}
          className={`
            px-6 py-3 font-semibold transition-colors
            ${activeTab === 'predict'
              ? 'text-accent border-b-2 border-accent'
              : 'text-text-secondary hover:text-text'
            }
          `}
          disabled={!selectedModel}
        >
          Predictions
        </button>
        <button
          onClick={() => setActiveTab('whatif')}
          className={`
            px-6 py-3 font-semibold transition-colors
            ${activeTab === 'whatif'
              ? 'text-accent border-b-2 border-accent'
              : 'text-text-secondary hover:text-text'
            }
          `}
        >
          What-If Analysis
        </button>
      </div>

      {/* Train Tab */}
      {activeTab === 'train' && (
        <div className="space-y-6">
          <MLPanel
            datasetId=""
            onModelTrained={(_modelId) => {
              toast.success('Model trained successfully!');
              loadModels();
              setActiveTab('models');
            }}
          />
        </div>
      )}

      {/* Models Tab */}
      {activeTab === 'models' && (
        <>
          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-surface border border-border rounded-xl p-6">
              <div className="w-12 h-12 bg-accent-dim rounded-lg flex items-center justify-center mb-4">
                <Zap size={24} className="text-accent" />
              </div>
              <h3 className="font-semibold mb-2">AutoML</h3>
              <p className="text-sm text-text-secondary">
                Automatically selects the best algorithm for your data
              </p>
            </div>

            <div className="bg-surface border border-border rounded-xl p-6">
              <div className="w-12 h-12 bg-accent-dim rounded-lg flex items-center justify-center mb-4">
                <Target size={24} className="text-accent" />
              </div>
              <h3 className="font-semibold mb-2">Feature Importance</h3>
              <p className="text-sm text-text-secondary">
                Understand which features drive your predictions
              </p>
            </div>

            <div className="bg-surface border border-border rounded-xl p-6">
              <div className="w-12 h-12 bg-accent-dim rounded-lg flex items-center justify-center mb-4">
                <TrendingUp size={24} className="text-accent" />
              </div>
              <h3 className="font-semibold mb-2">Predictions</h3>
              <p className="text-sm text-text-secondary">
                Make predictions and run what-if scenarios
              </p>
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-16">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
                <p className="text-text-secondary">Loading ML models...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center py-16">
              <div className="text-center">
                <p className="text-red-500 mb-4">{error}</p>
                <button
                  onClick={loadModels}
                  className="px-4 py-2 bg-accent text-bg rounded-lg hover:bg-accent-hover"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : models.length === 0 ? (
            <div className="text-center py-16">
              <Brain size={64} className="mx-auto mb-4 text-text-tertiary" />
              <h3 className="text-xl font-semibold mb-2">No models trained yet</h3>
              <p className="text-text-secondary mb-6">
                Upload a dataset and train your first ML model
              </p>
              <button
                onClick={() => setActiveTab('train')}
                className="inline-flex items-center gap-2 px-6 py-3 bg-accent text-bg rounded-lg hover:bg-accent-hover transition-colors"
              >
                <Plus size={20} />
                Train Model
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {models.map((model) => (
                <div
                  key={model.model_id}
                  className={`
                    bg-surface border rounded-xl p-6 hover:border-accent transition-colors cursor-pointer
                    ${selectedModel?.model_id === model.model_id ? 'border-accent' : 'border-border'}
                  `}
                  onClick={() => setSelectedModel(model)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-accent-dim rounded-lg flex items-center justify-center">
                        <Brain size={20} className="text-accent" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{model.name || model.algorithm}</h3>
                        <p className="text-sm text-text-tertiary capitalize">
                          {model.task_type || 'regression'} - {model.algorithm}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-text-secondary">Target</span>
                      <span className="text-text-primary">{model.target_column}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-text-secondary">Created</span>
                      <span className="text-text-primary">
                        {new Date(model.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {(model.r2_score || model.metrics) && (
                      <div className="mt-4 p-3 bg-surface-2 rounded-lg">
                        <p className="text-xs text-text-tertiary mb-2">Performance Metrics</p>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div>
                            <span className="text-text-secondary">R² Score: </span>
                            <span className="text-text-primary font-mono">
                              {(model.r2_score || model.metrics?.r2_score || 0).toFixed(3)}
                            </span>
                          </div>
                          <div>
                            <span className="text-text-secondary">MAE: </span>
                            <span className="text-text-primary font-mono">
                              {(model.mae || model.metrics?.mae || 0).toFixed(2)}
                            </span>
                          </div>
                          <div>
                            <span className="text-text-secondary">RMSE: </span>
                            <span className="text-text-primary font-mono">
                              {(model.rmse || model.metrics?.rmse || 0).toFixed(2)}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <button
                      className="flex-1 px-4 py-2 bg-accent text-bg rounded-lg hover:bg-accent-hover transition-colors"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedModel(model);
                        setActiveTab('predict');
                      }}
                    >
                      View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Predictions Tab */}
      {activeTab === 'predict' && selectedModel && (
        <div className="space-y-6">
          <div className="bg-surface border border-border rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-4">Model: {selectedModel.name || selectedModel.algorithm}</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <FeatureImportance modelId={selectedModel.model_id} maxFeatures={10} />
              <PredictionChart 
                modelId={selectedModel.model_id} 
                datasetId={selectedModel.dataset_id}
                maxPoints={100}
              />
            </div>
          </div>
        </div>
      )}

      {/* What-If Tab */}
      {activeTab === 'whatif' && (
        <div className="space-y-6">
          {selectedModel ? (
            <WhatIfSimulator
              datasetId={selectedModel.dataset_id}
              targetMetric={selectedModel.target_column}
              onSimulationComplete={(result) => {
                console.log('Simulation complete:', result);
              }}
            />
          ) : (
            <div className="bg-surface border border-border rounded-xl p-6">
              <div className="text-center py-16">
                <Sliders size={64} className="mx-auto mb-4 text-text-tertiary" />
                <h3 className="text-xl font-semibold mb-2">No Model Selected</h3>
                <p className="text-text-secondary mb-6">
                  Select a model from the Models tab to run what-if scenarios
                </p>
                <button
                  onClick={() => setActiveTab('models')}
                  className="px-6 py-3 bg-accent text-bg rounded-lg hover:bg-accent-hover transition-colors"
                >
                  View Models
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* API Reference */}
      <div className="mt-12 p-6 bg-surface border border-border rounded-xl">
        <h3 className="font-semibold mb-4">API Endpoints</h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <code className="px-2 py-1 bg-surface-2 rounded text-accent">POST /api/ml/train</code>
            <span className="text-text-secondary">- Train a new model</span>
          </div>
          <div className="flex items-center gap-2">
            <code className="px-2 py-1 bg-surface-2 rounded text-accent">GET /api/ml/models</code>
            <span className="text-text-secondary">- List all models</span>
          </div>
          <div className="flex items-center gap-2">
            <code className="px-2 py-1 bg-surface-2 rounded text-accent">POST /api/ml/models/:id/predict</code>
            <span className="text-text-secondary">- Make predictions</span>
          </div>
          <div className="flex items-center gap-2">
            <code className="px-2 py-1 bg-surface-2 rounded text-accent">POST /api/ml/what-if</code>
            <span className="text-text-secondary">- Run what-if scenarios</span>
          </div>
        </div>
        <a
          href="http://127.0.0.1:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block mt-4 text-accent hover:underline"
        >
          View Full API Documentation →
        </a>
      </div>
    </div>
  );
}
