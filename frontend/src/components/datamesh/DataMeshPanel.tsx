import { useState, useEffect } from 'react';
import { ArrowRight, Loader, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import { suggestJoins, analyzeCrossDataset, type JoinSuggestion, type CrossAnalysisResult } from '../../api/dataMesh';
import { getDatasets } from '../../api/client';
import toast from 'react-hot-toast';

type Step = 1 | 2 | 3 | 'results';

export default function DataMeshPanel() {
  const [step, setStep] = useState<Step>(1);
  const [datasets, setDatasets] = useState<any[]>([]);
  const [datasetIdA, setDatasetIdA] = useState('');
  const [datasetIdB, setDatasetIdB] = useState('');
  const [joinSuggestions, setJoinSuggestions] = useState<JoinSuggestion[]>([]);
  const [selectedJoin, setSelectedJoin] = useState<{
    join_key_a: string;
    join_key_b: string;
    join_type: string;
  } | null>(null);
  const [userQuestion, setUserQuestion] = useState('');
  const [analysisResult, setAnalysisResult] = useState<CrossAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      const data = await getDatasets();
      // Backend returns array directly
      setDatasets(Array.isArray(data) ? data : []);
    } catch (error) {
      toast.error('Failed to load datasets');
    }
  };

  const handleFindJoinKeys = async () => {
    if (!datasetIdA || !datasetIdB) {
      toast.error('Please select both datasets');
      return;
    }

    if (datasetIdA === datasetIdB) {
      toast.error('Please select different datasets');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await suggestJoins(datasetIdA, datasetIdB);
      setJoinSuggestions(result.suggestions);
      
      if (result.suggestions.length === 0) {
        setError('No obvious join keys found. Please select columns manually.');
      } else {
        setStep(2);
      }
    } catch (error: any) {
      toast.error('Failed to find join keys');
      setError(error.response?.data?.detail || 'Failed to analyze datasets');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectJoin = (suggestion: JoinSuggestion) => {
    setSelectedJoin({
      join_key_a: suggestion.col_a,
      join_key_b: suggestion.col_b,
      join_type: 'inner',
    });
    setStep(3);
  };

  const handleAnalyze = async () => {
    if (!selectedJoin) {
      toast.error('Please select a join configuration');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await analyzeCrossDataset({
        dataset_id_a: datasetIdA,
        dataset_id_b: datasetIdB,
        join_key_a: selectedJoin.join_key_a,
        join_key_b: selectedJoin.join_key_b,
        join_type: selectedJoin.join_type,
        user_question: userQuestion || undefined,
      });

      if (result.success) {
        setAnalysisResult(result);
        setStep('results');
      } else {
        setError(result.error || 'Analysis failed');
      }
    } catch (error: any) {
      toast.error('Analysis failed');
      setError(error.response?.data?.detail || 'Failed to analyze cross-dataset correlation');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setStep(1);
    setDatasetIdA('');
    setDatasetIdB('');
    setJoinSuggestions([]);
    setSelectedJoin(null);
    setUserQuestion('');
    setAnalysisResult(null);
    setError('');
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Multi-Dataset Cross-Correlation
          </h1>
          <p className="text-text-secondary">
            Join multiple datasets and discover correlations across them
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8 flex items-center justify-center gap-4">
          <div className={`flex items-center gap-2 ${typeof step === 'number' && step >= 1 ? 'text-accent' : 'text-text-secondary'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${typeof step === 'number' && step >= 1 ? 'bg-accent text-bg' : 'bg-surface-elevated'}`}>
              1
            </div>
            <span className="text-sm font-medium">Select Datasets</span>
          </div>
          <ArrowRight size={20} className="text-text-secondary" />
          <div className={`flex items-center gap-2 ${typeof step === 'number' && step >= 2 ? 'text-accent' : 'text-text-secondary'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${typeof step === 'number' && step >= 2 ? 'bg-accent text-bg' : 'bg-surface-elevated'}`}>
              2
            </div>
            <span className="text-sm font-medium">Select Join</span>
          </div>
          <ArrowRight size={20} className="text-text-secondary" />
          <div className={`flex items-center gap-2 ${typeof step === 'number' && step >= 3 ? 'text-accent' : 'text-text-secondary'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${typeof step === 'number' && step >= 3 ? 'bg-accent text-bg' : 'bg-surface-elevated'}`}>
              3
            </div>
            <span className="text-sm font-medium">Analyze</span>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start gap-3">
            <AlertCircle size={20} className="text-red-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-red-500">{error}</p>
            </div>
          </div>
        )}

        {/* Step 1: Select Datasets */}
        {step === 1 && (
          <div className="bg-surface border border-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-text-primary mb-4">
              Step 1: Select Datasets
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Dataset A
                </label>
                <select
                  value={datasetIdA}
                  onChange={(e) => setDatasetIdA(e.target.value)}
                  className="w-full px-4 py-2 bg-surface-elevated border border-border rounded-lg text-text-primary"
                >
                  <option value="">Select first dataset...</option>
                  {datasets.map((ds) => (
                    <option key={ds.id} value={ds.id}>
                      {ds.name} ({ds.row_count} rows, {ds.column_count} columns)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Dataset B
                </label>
                <select
                  value={datasetIdB}
                  onChange={(e) => setDatasetIdB(e.target.value)}
                  className="w-full px-4 py-2 bg-surface-elevated border border-border rounded-lg text-text-primary"
                  disabled={!datasetIdA}
                >
                  <option value="">Select second dataset...</option>
                  {datasets
                    .filter((ds) => ds.id !== datasetIdA)
                    .map((ds) => (
                      <option key={ds.id} value={ds.id}>
                        {ds.name} ({ds.row_count} rows, {ds.column_count} columns)
                      </option>
                    ))}
                </select>
              </div>

              <button
                onClick={handleFindJoinKeys}
                disabled={!datasetIdA || !datasetIdB || loading}
                className="w-full px-6 py-3 bg-accent text-bg rounded-lg font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader size={20} className="animate-spin" />
                    Finding Join Keys...
                  </>
                ) : (
                  'Find Join Keys'
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Select Join */}
        {step === 2 && (
          <div className="bg-surface border border-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-text-primary mb-4">
              Step 2: Select Join Configuration
            </h2>

            <div className="space-y-3 mb-6">
              {joinSuggestions.map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelectJoin(suggestion)}
                  className="w-full p-4 bg-surface-elevated border border-border rounded-lg hover:border-accent transition-colors text-left"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <span className="text-text-primary font-medium">
                        {suggestion.col_a}
                      </span>
                      <ArrowRight size={16} className="text-text-secondary" />
                      <span className="text-text-primary font-medium">
                        {suggestion.col_b}
                      </span>
                    </div>
                    <span className="px-3 py-1 bg-accent/20 text-accent text-sm rounded-full">
                      {Math.round(suggestion.confidence * 100)}% match
                    </span>
                  </div>
                  <p className="text-sm text-text-secondary">{suggestion.reason}</p>
                </button>
              ))}
            </div>

            <button
              onClick={() => setStep(1)}
              className="px-4 py-2 text-text-secondary hover:text-text-primary transition-colors"
            >
              ← Back to Dataset Selection
            </button>
          </div>
        )}

        {/* Step 3: Ask Question & Analyze */}
        {step === 3 && selectedJoin && (
          <div className="bg-surface border border-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-text-primary mb-4">
              Step 3: Configure Analysis
            </h2>

            <div className="space-y-4">
              <div className="p-4 bg-surface-elevated rounded-lg">
                <p className="text-sm text-text-secondary mb-2">Join Configuration:</p>
                <div className="flex items-center gap-3 text-text-primary">
                  <span className="font-medium">{selectedJoin.join_key_a}</span>
                  <ArrowRight size={16} />
                  <span className="font-medium">{selectedJoin.join_key_b}</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Join Type
                </label>
                <select
                  value={selectedJoin.join_type}
                  onChange={(e) =>
                    setSelectedJoin({ ...selectedJoin, join_type: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-surface-elevated border border-border rounded-lg text-text-primary"
                >
                  <option value="inner">Inner Join (matching rows only)</option>
                  <option value="left">Left Join (all from Dataset A)</option>
                  <option value="outer">Outer Join (all rows from both)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Business Question (Optional)
                </label>
                <input
                  type="text"
                  value={userQuestion}
                  onChange={(e) => setUserQuestion(e.target.value)}
                  placeholder="e.g., Is there a correlation between team turnover and sales drops?"
                  className="w-full px-4 py-2 bg-surface-elevated border border-border rounded-lg text-text-primary placeholder-text-secondary"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep(2)}
                  className="px-6 py-3 bg-surface-elevated text-text-primary rounded-lg font-medium hover:bg-white/[0.04] transition-colors"
                >
                  ← Back
                </button>
                <button
                  onClick={handleAnalyze}
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-accent text-bg rounded-lg font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader size={20} className="animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    'Analyze Cross-Correlation'
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {step === 'results' && analysisResult && (
          <div className="space-y-6">
            {/* Narrative */}
            <div className="bg-accent/10 border border-accent/20 rounded-lg p-6">
              <p className="text-lg italic text-accent">{analysisResult.narrative}</p>
            </div>

            {/* AI Insights */}
            {analysisResult.insights && analysisResult.insights.length > 0 && (
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-text-primary mb-4">Key Insights</h2>
                <div className="space-y-3">
                  {analysisResult.insights.map((insight: any, idx: number) => {
                    const severityColors = {
                      high: 'border-red-500/30 bg-red-500/5',
                      medium: 'border-yellow-500/30 bg-yellow-500/5',
                      low: 'border-blue-500/30 bg-blue-500/5'
                    };
                    const severityTextColors = {
                      high: 'text-red-500',
                      medium: 'text-yellow-500',
                      low: 'text-blue-500'
                    };
                    
                    return (
                      <div
                        key={idx}
                        className={`p-4 rounded-lg border ${severityColors[insight.severity as keyof typeof severityColors]}`}
                      >
                        <div className="flex items-start gap-3">
                          <div className={`mt-0.5 px-2 py-0.5 rounded text-xs font-semibold uppercase ${severityTextColors[insight.severity as keyof typeof severityTextColors]}`}>
                            {insight.severity}
                          </div>
                          <div className="flex-1">
                            <h3 className="text-sm font-semibold text-text-primary mb-1">{insight.title}</h3>
                            <p className="text-sm text-text-secondary mb-2">{insight.message}</p>
                            <div className="p-2 rounded bg-surface-elevated/50">
                              <p className="text-xs text-text-secondary">
                                <span className="font-medium">Recommendation:</span> {insight.recommendation}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-surface border border-border rounded-lg p-4">
                <p className="text-sm text-text-secondary mb-1">Merged Rows</p>
                <p className="text-2xl font-bold text-text-primary">
                  {analysisResult.merged_rows.toLocaleString()}
                </p>
              </div>
              <div className="bg-surface border border-border rounded-lg p-4">
                <p className="text-sm text-text-secondary mb-1">Dataset A</p>
                <p className="text-lg font-semibold text-text-primary">
                  {analysisResult.datasets.a.name}
                </p>
                <p className="text-sm text-text-secondary">
                  {analysisResult.datasets.a.rows.toLocaleString()} rows
                </p>
              </div>
              <div className="bg-surface border border-border rounded-lg p-4">
                <p className="text-sm text-text-secondary mb-1">Dataset B</p>
                <p className="text-lg font-semibold text-text-primary">
                  {analysisResult.datasets.b.name}
                </p>
                <p className="text-sm text-text-secondary">
                  {analysisResult.datasets.b.rows.toLocaleString()} rows
                </p>
              </div>
            </div>

            {/* Correlations Table */}
            {analysisResult.correlations.length > 0 && (
              <div className="bg-surface border border-border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Cross-Dataset Correlations
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-4 text-sm font-medium text-text-secondary">
                          Column A
                        </th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-text-secondary">
                          Column B
                        </th>
                        <th className="text-center py-3 px-4 text-sm font-medium text-text-secondary">
                          Correlation (r)
                        </th>
                        <th className="text-center py-3 px-4 text-sm font-medium text-text-secondary">
                          Strength
                        </th>
                        <th className="text-center py-3 px-4 text-sm font-medium text-text-secondary">
                          Direction
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysisResult.correlations.map((corr, idx) => (
                        <tr key={idx} className="border-b border-border/50">
                          <td className="py-3 px-4 text-sm text-text-primary">
                            {corr.col_a}
                          </td>
                          <td className="py-3 px-4 text-sm text-text-primary">
                            {corr.col_b}
                          </td>
                          <td className="py-3 px-4 text-center">
                            <span
                              className={`font-semibold ${
                                Math.abs(corr.r) > 0.7
                                  ? 'text-accent'
                                  : 'text-text-primary'
                              }`}
                            >
                              {corr.r.toFixed(3)}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-center">
                            <span
                              className={`px-2 py-1 rounded-full text-xs ${
                                corr.strength === 'strong'
                                  ? 'bg-accent/20 text-accent'
                                  : 'bg-surface-elevated text-text-secondary'
                              }`}
                            >
                              {corr.strength}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-center">
                            <div className="flex items-center justify-center gap-1">
                              {corr.direction === 'positive' ? (
                                <TrendingUp size={16} className="text-green-500" />
                              ) : (
                                <TrendingDown size={16} className="text-red-500" />
                              )}
                              <span className="text-sm text-text-secondary">
                                {corr.direction}
                              </span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Cross Chart */}
            {analysisResult.cross_chart && (
              <div className="bg-surface border border-border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  {analysisResult.cross_chart.title}
                </h3>
                <div className="h-64 flex items-center justify-center text-text-secondary">
                  <p>Scatter plot visualization (integrate with existing ChartCard)</p>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={handleReset}
                className="px-6 py-3 bg-surface-elevated text-text-primary rounded-lg font-medium hover:bg-white/[0.04] transition-colors"
              >
                Start New Analysis
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
