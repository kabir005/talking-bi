import React, { useState, useEffect } from 'react';
import { Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { DrillDown } from './DrillDown';
import { FilterBar } from './FilterBar';
import { PresetSelector } from './PresetSelector';
import { CommandProcessor } from '../conversation/CommandProcessor';
import { MemoryPanel } from '../shared/MemoryPanel';
import { useDrillDown } from '../../hooks/useDrillDown';
import { useFilters } from '../../hooks/useFilters';
import axios from 'axios';

interface IntegratedDashboardProps {
  dashboardId: string;
  datasetId: string;
  onRefresh?: () => void;
}

interface DashboardData {
  id: string;
  name: string;
  preset: string;
  tiles: any[];
  layout: any[];
  filters: any;
}

export const IntegratedDashboard: React.FC<IntegratedDashboardProps> = ({
  dashboardId,
  datasetId,
  onRefresh
}) => {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [columns, setColumns] = useState<Array<{ name: string; type: string }>>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Use custom hooks
  const drillDown = useDrillDown(datasetId);
  const filters = useFilters(datasetId);

  // Load dashboard data
  const loadDashboard = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.get(`/api/dashboards/${dashboardId}`);
      setDashboard(response.data);

      // Load dataset schema for columns
      const datasetResponse = await axios.get(`/api/datasets/${datasetId}`);
      const schema = datasetResponse.data.schema_json || {};
      const cols = Object.entries(schema).map(([name, type]) => ({
        name,
        type: type as string
      }));
      setColumns(cols);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, [dashboardId, datasetId]);

  // Handle preset change
  const handlePresetChange = async (presetId: string) => {
    setIsRefreshing(true);
    try {
      await axios.put(`/api/dashboards/${dashboardId}`, {
        preset: presetId
      });
      await loadDashboard();
      onRefresh?.();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to change preset');
    } finally {
      setIsRefreshing(false);
    }
  };

  // Handle filter changes
  const handleFiltersChange = async (newFilters: any[]) => {
    filters.clearFilters();
    newFilters.forEach(f => filters.addFilter(f));

    try {
      const result = await filters.applyFilters(false);
      
      // Update dashboard with filter results
      await axios.put(`/api/dashboards/${dashboardId}`, {
        filters_json: {
          ...dashboard?.filters,
          active_filters: newFilters,
          result_summary: result
        }
      });

      await loadDashboard();
    } catch (err) {
      console.error('Failed to apply filters:', err);
    }
  };

  // Handle command execution
  const handleCommandExecuted = async (result: any) => {
    if (result.success) {
      // Refresh dashboard after command
      await loadDashboard();
      onRefresh?.();
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Dashboard</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadDashboard}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* Header with preset selector */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{dashboard.name}</h1>
            <p className="text-sm text-gray-500">
              {dashboard.tiles.length} visualizations • {dashboard.preset} preset
            </p>
          </div>
          <button
            onClick={loadDashboard}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        <PresetSelector
          selectedPreset={dashboard.preset}
          onSelectPreset={handlePresetChange}
        />
      </div>

      {/* Drill-down breadcrumb */}
      {drillDown.levels.length > 0 && (
        <DrillDown
          levels={drillDown.levels}
          onNavigate={drillDown.navigateToLevel}
          onReset={drillDown.reset}
        />
      )}

      {/* Filter bar */}
      <FilterBar
        columns={columns}
        filters={filters.filters}
        onFiltersChange={handleFiltersChange}
      />

      {/* Command processor */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <CommandProcessor
          dashboardId={dashboardId}
          onCommandExecuted={handleCommandExecuted}
        />
      </div>

      {/* Dashboard content */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        {dashboard.tiles.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No visualizations yet</p>
          </div>
        ) : (
          <div className="grid grid-cols-12 gap-4">
            {dashboard.tiles.map((tile, index) => (
              <div
                key={tile.id || index}
                className="col-span-12 md:col-span-6 lg:col-span-4 bg-gray-50 border border-gray-200 rounded-lg p-4"
                onClick={() => {
                  // Handle tile click for drill-down
                  if (tile.config?.x_column) {
                    // This would be enhanced with actual chart interaction
                    console.log('Tile clicked:', tile);
                  }
                }}
              >
                <h3 className="text-sm font-semibold text-gray-900 mb-2">
                  {tile.title}
                </h3>
                <div className="text-xs text-gray-500">
                  Type: {tile.type}
                </div>
                {tile.config?.data && (
                  <div className="text-xs text-gray-500 mt-1">
                    Data points: {tile.config.data.length}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Memory panel */}
      <MemoryPanel
        datasetId={datasetId}
        onSelectQuery={(query) => {
          console.log('Selected query:', query);
          // Could trigger command processor with this query
        }}
      />

      {/* Drill-down data display */}
      {drillDown.data && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Drill-Down Results
          </h3>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Total Rows</div>
              <div className="text-2xl font-bold text-blue-600">
                {drillDown.data.row_count.toLocaleString()}
              </div>
            </div>
            {Object.entries(drillDown.data.summary).slice(0, 2).map(([key, value]: [string, any]) => (
              <div key={key} className="bg-green-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">{key}</div>
                <div className="text-2xl font-bold text-green-600">
                  {value.sum?.toLocaleString() || value.mean?.toLocaleString() || 'N/A'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filter results display */}
      {filters.result && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Filter Results
          </h3>
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Original Count</div>
              <div className="text-xl font-bold text-gray-900">
                {filters.result.original_count.toLocaleString()}
              </div>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Filtered Count</div>
              <div className="text-xl font-bold text-blue-600">
                {filters.result.filtered_count.toLocaleString()}
              </div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Rows Removed</div>
              <div className="text-xl font-bold text-red-600">
                {filters.result.rows_removed.toLocaleString()}
              </div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Remaining</div>
              <div className="text-xl font-bold text-green-600">
                {filters.result.percentage_remaining.toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
