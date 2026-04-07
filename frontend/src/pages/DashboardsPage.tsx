import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { LayoutDashboard, Plus, Trash2, Eye } from 'lucide-react';
import { getDashboards, deleteDashboard as deleteDashboardAPI } from '../api/client';
import toast from 'react-hot-toast';

interface Dashboard {
  id: string;
  name: string;
  dataset_id: string;
  preset: string;
  created_at: string;
  tile_count?: number;
}

export default function DashboardsPage() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboards();
  }, []);

  const loadDashboards = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getDashboards();
      setDashboards(data);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load dashboards';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDashboard = async (id: string) => {
    if (!confirm('Are you sure you want to delete this dashboard?')) return;
    
    try {
      await deleteDashboardAPI(id);
      setDashboards(dashboards.filter(d => d.id !== id));
      toast.success('Dashboard deleted successfully');
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to delete dashboard';
      toast.error(errorMsg);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading dashboards...</p>
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
            onClick={loadDashboards}
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
          <h1 className="text-3xl font-heading font-bold mb-2">Dashboards</h1>
          <p className="text-text-secondary">
            View and manage your interactive dashboards
          </p>
        </div>
        <Link
          to="/datasets"
          className="flex items-center gap-2 px-4 py-2 bg-accent text-bg rounded-lg hover:bg-accent-hover transition-colors"
        >
          <Plus size={20} />
          Create Dashboard
        </Link>
      </div>

      {dashboards.length === 0 ? (
        <div className="text-center py-16">
          <LayoutDashboard size={64} className="mx-auto mb-4 text-text-tertiary" />
          <h3 className="text-xl font-semibold mb-2">No dashboards yet</h3>
          <p className="text-text-secondary mb-6">
            Upload a dataset and generate your first dashboard
          </p>
          <Link
            to="/upload"
            className="inline-flex items-center gap-2 px-6 py-3 bg-accent text-bg rounded-lg hover:bg-accent-hover transition-colors"
          >
            <Plus size={20} />
            Upload Data
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dashboards.map((dashboard) => (
            <div
              key={dashboard.id}
              className="bg-surface border border-border rounded-xl p-6 hover:border-accent transition-colors"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-accent-dim rounded-lg flex items-center justify-center">
                    <LayoutDashboard size={20} className="text-accent" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{dashboard.name}</h3>
                    <p className="text-sm text-text-tertiary capitalize">
                      {dashboard.preset} preset
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">Created</span>
                  <span className="text-text-primary">
                    {new Date(dashboard.created_at).toLocaleDateString()}
                  </span>
                </div>
                {dashboard.tile_count && (
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Tiles</span>
                    <span className="text-text-primary">{dashboard.tile_count}</span>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <Link
                  to={`/dashboard/${dashboard.id}`}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-accent text-bg rounded-lg hover:bg-accent-hover transition-colors"
                >
                  <Eye size={16} />
                  View
                </Link>
                <button
                  onClick={() => handleDeleteDashboard(dashboard.id)}
                  className="px-4 py-2 bg-surface-2 text-text-secondary rounded-lg hover:bg-red-500 hover:text-white transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
