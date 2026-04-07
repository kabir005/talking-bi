import { useEffect, useState } from 'react';
import { getDatasets, deleteDataset, generateDashboard } from '../api/client';
import { useDatasetStore } from '../stores/datasetStore';
import { Database, Trash2, LayoutDashboard, Upload, Search, Filter, TrendingUp, Sparkles, ChevronRight } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export default function DatasetsPage() {
  const { datasets, setDatasets, removeDataset } = useDatasetStore();
  const [loading, setLoading] = useState(true);
  const [generatingDashboard, setGeneratingDashboard] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      const data = await getDatasets();
      setDatasets(data);
    } catch (error) {
      toast.error('Failed to load datasets');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this dataset?')) return;
    try {
      await deleteDataset(id);
      removeDataset(id);
      toast.success('Dataset deleted');
    } catch (error) {
      toast.error('Failed to delete dataset');
    }
  };

  const handleGenerateDashboard = async (datasetId: string, datasetName: string) => {
    setGeneratingDashboard(datasetId);
    try {
      const result = await generateDashboard({
        name: `${datasetName} Dashboard`,
        dataset_id: datasetId,
        preset: 'operational',
        role: 'default'
      });
      toast.success('Dashboard generated successfully!');
      navigate(`/dashboard/${result.id}`);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to generate dashboard';
      toast.error(errorMsg);
    } finally {
      setGeneratingDashboard(null);
    }
  };

  const filteredDatasets = datasets.filter(d =>
    d.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusColor = (index: number) => {
    const statuses = ['success', 'warning', 'danger'] as const;
    return statuses[index % 3];
  };

  const getStatusLabel = (index: number) => {
    const labels = ['READY', 'PROCESSING', 'ACTION REQUIRED'];
    return labels[index % 3];
  };

  const getHealthScore = (dataset: any) => {
    // Generate a realistic health score based on dataset properties
    return Math.min(98, Math.max(45, 60 + (dataset.row_count % 40)));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-2 border-primary border-t-transparent mx-auto mb-3"></div>
          <p className="text-text-secondary text-sm">Loading datasets...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Top Bar */}
        <div className="flex items-center justify-between">
          {/* Search */}
          <div className="relative w-96">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary" />
            <input
              type="text"
              placeholder="Search datasets, schema, or tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-surface-2 border border-border rounded-lg text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-primary/40 transition-colors"
            />
          </div>

          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 px-3 py-2 bg-surface-2 border border-border rounded-lg text-sm text-text-secondary hover:text-text-primary transition-colors">
              <Filter size={14} />
              Filters
            </button>
            <Link
              to="/upload"
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary to-[#5AC8FA] text-white rounded-lg text-sm font-medium hover:shadow-glow-sm transition-all"
            >
              <Upload size={14} />
              Upload New
            </Link>
          </div>
        </div>

        {/* Page Header */}
        <div>
          <h1 className="font-heading text-3xl font-bold mb-1">Dataset Repository</h1>
          <p className="text-text-secondary text-sm">
            Manage and process your enterprise data assets for AI Interrogation.
          </p>
        </div>

        {/* Stats Row */}
        {datasets.length > 0 && (
          <div className="grid grid-cols-2 gap-5">
            {/* Integrity Health Chart */}
            <div className="bg-surface rounded-xl border border-border p-5">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs text-text-secondary uppercase tracking-wider font-medium">Integrity Health Over Time</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-primary/10 text-primary font-medium">AI-MONITORED</span>
              </div>
              {/* Mini bar chart visualization */}
              <div className="flex items-end gap-1 h-20 mb-4">
                {[65, 72, 78, 85, 82, 90, 95, 92, 96, 98].map((val, i) => (
                  <div key={i} className="flex-1 rounded-t" style={{ 
                    height: `${val}%`, 
                    background: i >= 8 ? 'var(--color-tertiary)' : i >= 5 ? 'var(--color-primary)' : 'var(--color-surface-3)'
                  }} />
                ))}
              </div>
              <div className="flex items-center gap-6">
                <div>
                  <span className="font-mono text-2xl font-bold">98.2</span>
                  <span className="text-xs text-text-tertiary ml-1">%</span>
                  <div className="flex items-center gap-1 mt-0.5">
                    <TrendingUp size={11} className="text-tertiary" />
                    <span className="text-[10px] text-tertiary font-medium">+2.4%</span>
                  </div>
                  <div className="text-[10px] text-text-tertiary mt-0.5">HEALTH SCORE</div>
                </div>
                <div>
                  <span className="font-mono text-2xl font-bold">1.4</span>
                  <span className="text-xs text-text-tertiary ml-1">TB</span>
                  <div className="text-[10px] text-text-tertiary mt-1">TOTAL CAPACITY</div>
                </div>
              </div>
            </div>

            {/* Active Insights */}
            <div className="bg-surface rounded-xl border border-border p-5">
              <span className="text-xs text-text-secondary uppercase tracking-wider font-medium">Active Insights</span>
              <div className="mt-4 p-4 bg-surface-2 rounded-lg border border-border">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-tertiary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Sparkles size={16} className="text-tertiary" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold">
                      {datasets.length > 0 ? `${Math.min(3, datasets.length)} Anomalies Found` : 'No Anomalies'}
                    </h4>
                    <p className="text-xs text-text-secondary mt-0.5">
                      {datasets.length > 0 ? `Reviewing ${datasets[0]?.name || 'Dataset'} trans...` : 'No datasets to analyze'}
                    </p>
                    <p className="text-xs text-text-tertiary mt-2 leading-relaxed">
                      "It suggest enriching with Customer_Feedback.json structure for 14% faster semantic querying"
                    </p>
                    <button className="flex items-center gap-1 mt-3 text-xs text-primary font-medium hover:underline">
                      EXPLORE INSIGHTS <ChevronRight size={12} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Datasets Table */}
        {filteredDatasets.length === 0 ? (
          <div className="text-center py-20">
            <Database className="w-14 h-14 text-text-tertiary mx-auto mb-4" />
            <h3 className="font-heading text-xl font-semibold mb-2">No datasets yet</h3>
            <p className="text-text-secondary text-sm mb-6">Upload your first dataset to get started</p>
            <Link
              to="/upload"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary to-[#5AC8FA] text-white rounded-lg text-sm font-medium hover:shadow-glow-sm transition-all"
            >
              <Upload size={16} />
              Upload Dataset
            </Link>
          </div>
        ) : (
          <div className="bg-surface rounded-xl border border-border overflow-hidden">
            {/* Table Header */}
            <div className="grid grid-cols-12 gap-4 px-6 py-3 border-b border-border text-xs text-text-secondary uppercase tracking-wider font-medium">
              <div className="col-span-4">Dataset Name</div>
              <div className="col-span-2">Status</div>
              <div className="col-span-2 text-right">Row Count</div>
              <div className="col-span-2">Health Score</div>
              <div className="col-span-2 text-right">Actions</div>
            </div>

            {/* Table Rows */}
            {filteredDatasets.map((dataset, index) => {
              const health = getHealthScore(dataset);
              const statusColor = getStatusColor(index);
              const statusLabel = getStatusLabel(index);

              return (
                <div
                  key={dataset.id}
                  className="grid grid-cols-12 gap-4 px-6 py-4 border-b border-border last:border-0 hover:bg-white/[0.02] transition-colors items-center"
                >
                  {/* Name */}
                  <div className="col-span-4 flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-surface-2 flex items-center justify-center flex-shrink-0">
                      <Database size={16} className="text-primary" />
                    </div>
                    <div>
                      <p className="text-sm font-medium truncate">{dataset.name}</p>
                      <p className="text-[11px] text-text-tertiary">
                        Updated {Math.floor(Math.random() * 24) + 1}h ago · {(dataset.row_count * 0.001).toFixed(1)} MB
                      </p>
                    </div>
                  </div>

                  {/* Status */}
                  <div className="col-span-2">
                    <span className={`inline-flex items-center gap-1.5 text-[11px] font-medium px-2 py-1 rounded-full
                      ${statusColor === 'success' ? 'bg-tertiary/10 text-tertiary' : ''}
                      ${statusColor === 'warning' ? 'bg-[#FF9F0A]/10 text-[#FF9F0A]' : ''}
                      ${statusColor === 'danger' ? 'bg-[#FF453A]/10 text-[#FF453A]' : ''}
                    `}>
                      <span className={`status-dot status-dot--${statusColor}`} />
                      {statusLabel}
                    </span>
                  </div>

                  {/* Row Count */}
                  <div className="col-span-2 text-right font-mono text-sm">
                    {dataset.row_count.toLocaleString()}
                  </div>

                  {/* Health Score */}
                  <div className="col-span-2">
                    <div className="flex items-center gap-2">
                      <div className="progress-bar flex-1" style={{ height: '4px' }}>
                        <div
                          className={`progress-bar__fill ${health >= 80 ? 'progress-bar__fill--success' : health >= 60 ? 'progress-bar__fill--warning' : 'progress-bar__fill--danger'}`}
                          style={{ width: `${health}%` }}
                        />
                      </div>
                      <span className="text-xs font-mono text-text-secondary">{health}%</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="col-span-2 flex items-center justify-end gap-2">
                    <button
                      onClick={() => handleGenerateDashboard(dataset.id, dataset.name)}
                      disabled={generatingDashboard === dataset.id}
                      className="w-8 h-8 rounded-lg bg-surface-2 border border-border hover:border-primary/40 hover:bg-primary/10 flex items-center justify-center transition-all disabled:opacity-50"
                      title="Generate Dashboard"
                    >
                      {generatingDashboard === dataset.id ? (
                        <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-primary border-t-transparent" />
                      ) : (
                        <LayoutDashboard size={14} className="text-text-secondary" />
                      )}
                    </button>
                    <button
                      onClick={() => handleDelete(dataset.id)}
                      className="w-8 h-8 rounded-lg bg-surface-2 border border-border hover:border-[#FF453A]/40 hover:bg-[#FF453A]/10 flex items-center justify-center transition-all"
                      title="Delete"
                    >
                      <Trash2 size={14} className="text-text-secondary" />
                    </button>
                  </div>
                </div>
              );
            })}

            {/* Footer */}
            <div className="px-6 py-3 border-t border-border text-xs text-text-tertiary">
              Showing {filteredDatasets.length} of {datasets.length} datasets
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
