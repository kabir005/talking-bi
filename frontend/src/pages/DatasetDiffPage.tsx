import { useState, useEffect } from 'react';
import { GitCompare, TrendingUp, TrendingDown, Minus, ArrowRight } from 'lucide-react';
import { getDatasets, compareDatasets, type DatasetDiffRequest } from '../api/client';
import toast from 'react-hot-toast';

export default function DatasetDiffPage() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [dataset1Id, setDataset1Id] = useState<string>('');
  const [dataset2Id, setDataset2Id] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [diffReport, setDiffReport] = useState<any>(null);

  useEffect(() => {
    loadDatasets();
  }, []);

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

  const runComparison = async () => {
    if (!dataset1Id || !dataset2Id) {
      toast.error('Please select both datasets');
      return;
    }

    if (dataset1Id === dataset2Id) {
      toast.error('Please select different datasets');
      return;
    }

    setLoading(true);
    try {
      const request: DatasetDiffRequest = {
        dataset1_id: dataset1Id,
        dataset2_id: dataset2Id,
        compare_distributions: true
      };

      const result = await compareDatasets(request);
      setDiffReport(result);
      toast.success('Comparison complete');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Comparison failed');
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (delta: number) => {
    if (delta > 0) return <TrendingUp size={16} className="text-green-500" />;
    if (delta < 0) return <TrendingDown size={16} className="text-red-500" />;
    return <Minus size={16} className="text-gray-500" />;
  };

  const getTrendColor = (delta: number) => {
    if (delta > 0) return 'text-green-500';
    if (delta < 0) return 'text-red-500';
    return 'text-gray-500';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-heading font-bold text-text-primary">Dataset Comparison</h1>
        <p className="text-sm text-text-secondary mt-1">
          Compare two datasets side-by-side
        </p>
      </div>

      {/* Selection */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Dataset 1
            </label>
            <select
              value={dataset1Id}
              onChange={(e) => setDataset1Id(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-surface-elevated border border-border
                text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            >
              <option value="">Select dataset...</option>
              {datasets.map((dataset) => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.name} ({dataset.row_count} rows)
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center justify-center">
            <ArrowRight size={24} className="text-text-secondary" />
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Dataset 2
            </label>
            <select
              value={dataset2Id}
              onChange={(e) => setDataset2Id(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-surface-elevated border border-border
                text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            >
              <option value="">Select dataset...</option>
              {datasets.map((dataset) => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.name} ({dataset.row_count} rows)
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={runComparison}
          disabled={loading || !dataset1Id || !dataset2Id}
          className="mt-4 w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg text-sm font-semibold
            bg-gradient-to-r from-primary to-[#5AC8FA] text-white
            hover:shadow-glow-sm transition-all duration-300 hover:scale-[1.02]
            disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          <GitCompare size={16} />
          {loading ? 'Comparing...' : 'Compare Datasets'}
        </button>
      </div>

      {/* Results */}
      {diffReport && (
        <div className="space-y-6">
          {/* AI Insights */}
          {diffReport.diff_report.insights && diffReport.diff_report.insights.length > 0 && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                <GitCompare size={20} className="text-primary" />
                Key Insights
              </h2>
              <div className="space-y-3">
                {diffReport.diff_report.insights.map((insight: any, idx: number) => {
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

          {/* Summary */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Summary</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-lg bg-surface-elevated border border-border">
                <p className="text-xs text-text-secondary mb-1">Row Change</p>
                <div className="flex items-center gap-2">
                  {getTrendIcon(diffReport.diff_report.summary.row_delta)}
                  <span className={`text-lg font-bold ${getTrendColor(diffReport.diff_report.summary.row_delta)}`}>
                    {diffReport.diff_report.summary.row_delta > 0 ? '+' : ''}
                    {diffReport.diff_report.summary.row_delta}
                  </span>
                </div>
                <p className="text-xs text-text-secondary mt-1">
                  {diffReport.diff_report.summary.row_percent_change?.toFixed(1)}%
                </p>
              </div>

              <div className="p-4 rounded-lg bg-surface-elevated border border-border">
                <p className="text-xs text-text-secondary mb-1">Columns Added</p>
                <p className="text-lg font-bold text-green-500">
                  +{diffReport.diff_report.summary.columns_added}
                </p>
              </div>

              <div className="p-4 rounded-lg bg-surface-elevated border border-border">
                <p className="text-xs text-text-secondary mb-1">Columns Removed</p>
                <p className="text-lg font-bold text-red-500">
                  -{diffReport.diff_report.summary.columns_removed}
                </p>
              </div>

              <div className="p-4 rounded-lg bg-surface-elevated border border-border">
                <p className="text-xs text-text-secondary mb-1">Schema Match</p>
                <p className={`text-lg font-bold ${diffReport.diff_report.summary.schema_match ? 'text-green-500' : 'text-yellow-500'}`}>
                  {diffReport.diff_report.summary.schema_match ? 'Yes' : 'No'}
                </p>
              </div>
            </div>
          </div>

          {/* Schema Diff */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Schema Changes</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {diffReport.diff_report.schema_diff.added_columns.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-green-500 mb-2">Added Columns</h3>
                  <div className="space-y-1">
                    {diffReport.diff_report.schema_diff.added_columns.map((col: string) => (
                      <div key={col} className="text-sm text-text-secondary px-3 py-1.5 rounded bg-green-500/10">
                        + {col}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {diffReport.diff_report.schema_diff.removed_columns.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-red-500 mb-2">Removed Columns</h3>
                  <div className="space-y-1">
                    {diffReport.diff_report.schema_diff.removed_columns.map((col: string) => (
                      <div key={col} className="text-sm text-text-secondary px-3 py-1.5 rounded bg-red-500/10">
                        - {col}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {diffReport.diff_report.schema_diff.common_columns.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-text-secondary mb-2">
                    Common Columns ({diffReport.diff_report.schema_diff.common_columns.length})
                  </h3>
                  <div className="max-h-40 overflow-y-auto space-y-1">
                    {diffReport.diff_report.schema_diff.common_columns.slice(0, 10).map((col: string) => (
                      <div key={col} className="text-sm text-text-secondary px-3 py-1.5 rounded bg-surface-elevated">
                        {col}
                      </div>
                    ))}
                    {diffReport.diff_report.schema_diff.common_columns.length > 10 && (
                      <p className="text-xs text-text-secondary px-3">
                        +{diffReport.diff_report.schema_diff.common_columns.length - 10} more...
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* KPI Comparison */}
          {diffReport.diff_report.kpi_diff.numeric_columns && Object.keys(diffReport.diff_report.kpi_diff.numeric_columns).length > 0 && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-text-primary mb-4">Numeric Column Comparison</h2>
              <div className="space-y-4">
                {Object.entries(diffReport.diff_report.kpi_diff.numeric_columns).slice(0, 5).map(([col, data]: [string, any]) => (
                  <div key={col} className="p-4 rounded-lg bg-surface-elevated border border-border">
                    <h3 className="text-sm font-medium text-text-primary mb-3">{col}</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-text-secondary mb-1">Mean</p>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-text-primary">
                            {data.mean.dataset1?.toFixed(2)} → {data.mean.dataset2?.toFixed(2)}
                          </span>
                          {data.mean.percent_change !== null && (
                            <span className={`text-xs ${getTrendColor(data.mean.percent_change)}`}>
                              ({data.mean.percent_change > 0 ? '+' : ''}{data.mean.percent_change?.toFixed(1)}%)
                            </span>
                          )}
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-text-secondary mb-1">Sum</p>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-text-primary">
                            {data.sum.dataset1?.toFixed(2)} → {data.sum.dataset2?.toFixed(2)}
                          </span>
                          {data.sum.percent_change !== null && (
                            <span className={`text-xs ${getTrendColor(data.sum.percent_change)}`}>
                              ({data.sum.percent_change > 0 ? '+' : ''}{data.sum.percent_change?.toFixed(1)}%)
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
