import React, { useState, useEffect } from 'react';
import { X, Save, Trash2, Copy } from 'lucide-react';
import axios from 'axios';

interface EditPanelProps {
  isOpen: boolean;
  onClose: () => void;
  tileId: string;
  tileConfig: any;
  datasetId: string;
  onSave: (config: any) => void;
  onDelete: () => void;
  onDuplicate: () => void;
}

const CHART_TYPES = [
  { value: 'bar', label: 'Bar Chart', icon: '📊' },
  { value: 'line', label: 'Line Chart', icon: '📈' },
  { value: 'pie', label: 'Pie Chart', icon: '🥧' },
  { value: 'scatter', label: 'Scatter Plot', icon: '⚫' },
  { value: 'area', label: 'Area Chart', icon: '📉' },
  { value: 'histogram', label: 'Histogram', icon: '📶' },
  { value: 'heatmap', label: 'Heatmap', icon: '🔥' },
  { value: 'waterfall', label: 'Waterfall', icon: '💧' },
  { value: 'treemap', label: 'Treemap', icon: '🌳' },
  { value: 'map', label: 'Map', icon: '🗺️' },
  { value: 'sparkline', label: 'Sparkline', icon: '⚡' },
];

const AGGREGATIONS = ['sum', 'mean', 'count', 'median', 'max', 'min'];

const COLOR_PALETTES = [
  { name: 'Default', colors: ['#3B82F6', '#22C55E', '#F59E0B', '#EF4444', '#8B5CF6'] },
  { name: 'Ocean', colors: ['#0EA5E9', '#06B6D4', '#14B8A6', '#10B981', '#22C55E'] },
  { name: 'Sunset', colors: ['#F59E0B', '#F97316', '#EF4444', '#EC4899', '#8B5CF6'] },
  { name: 'Forest', colors: ['#22C55E', '#16A34A', '#15803D', '#166534', '#14532D'] },
  { name: 'Monochrome', colors: ['#1F2937', '#374151', '#4B5563', '#6B7280', '#9CA3AF'] },
];

export const EditPanel: React.FC<EditPanelProps> = ({
  isOpen,
  onClose,
  tileId: _tileId,
  tileConfig,
  datasetId,
  onSave,
  onDelete,
  onDuplicate
}) => {
  const [config, setConfig] = useState(tileConfig);
  const [columns, setColumns] = useState<string[]>([]);
  const [numericColumns, setNumericColumns] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && datasetId) {
      loadColumns();
    }
  }, [isOpen, datasetId]);

  useEffect(() => {
    setConfig(tileConfig);
  }, [tileConfig]);

  const loadColumns = async () => {
    try {
      const response = await axios.get(`/api/datasets/${datasetId}`);
      const schema = response.data.schema_json || {};
      
      const allCols = Object.keys(schema);
      const numCols = Object.entries(schema)
        .filter(([_, type]) => ['numeric', 'currency', 'percentage'].includes(type as string))
        .map(([col, _]) => col);
      
      setColumns(allCols);
      setNumericColumns(numCols);
    } catch (error) {
      console.error('Error loading columns:', error);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await onSave(config);
      onClose();
    } catch (error) {
      console.error('Error saving config:', error);
      alert('Failed to save changes');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this tile?')) {
      onDelete();
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />

      {/* Slide-over Panel */}
      <div className="relative ml-auto w-full max-w-md bg-white shadow-2xl overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 z-10">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-800">Edit Chart</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Chart Type Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Chart Type
            </label>
            <div className="grid grid-cols-3 gap-2">
              {CHART_TYPES.map(type => (
                <button
                  key={type.value}
                  onClick={() => setConfig({ ...config, type: type.value })}
                  className={`p-3 border-2 rounded-lg text-center transition-all ${
                    config.type === type.value
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-1">{type.icon}</div>
                  <div className="text-xs font-medium text-gray-700">{type.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chart Title
            </label>
            <input
              type="text"
              value={config.title || ''}
              onChange={(e) => setConfig({ ...config, title: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter chart title"
            />
          </div>

          {/* X-Axis Column */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              X-Axis Column
            </label>
            <select
              value={config.x_column || ''}
              onChange={(e) => setConfig({ ...config, x_column: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select column...</option>
              {columns.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
          </div>

          {/* Y-Axis Column */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Y-Axis Column
            </label>
            <select
              value={config.y_column || ''}
              onChange={(e) => setConfig({ ...config, y_column: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select column...</option>
              {numericColumns.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
          </div>

          {/* Aggregation */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Aggregation
            </label>
            <select
              value={config.aggregation || 'sum'}
              onChange={(e) => setConfig({ ...config, aggregation: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {AGGREGATIONS.map(agg => (
                <option key={agg} value={agg}>{agg.toUpperCase()}</option>
              ))}
            </select>
          </div>

          {/* Color Palette */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Color Palette
            </label>
            <div className="space-y-2">
              {COLOR_PALETTES.map(palette => (
                <button
                  key={palette.name}
                  onClick={() => setConfig({ ...config, colors: palette.colors })}
                  className={`w-full p-3 border-2 rounded-lg flex items-center justify-between transition-all ${
                    JSON.stringify(config.colors) === JSON.stringify(palette.colors)
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <span className="text-sm font-medium text-gray-700">{palette.name}</span>
                  <div className="flex gap-1">
                    {palette.colors.map((color, idx) => (
                      <div
                        key={idx}
                        className="w-6 h-6 rounded"
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Display Options */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">
              Display Options
            </label>
            
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={config.options?.show_labels !== false}
                onChange={(e) => setConfig({
                  ...config,
                  options: { ...config.options, show_labels: e.target.checked }
                })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Show Data Labels</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={config.options?.show_legend !== false}
                onChange={(e) => setConfig({
                  ...config,
                  options: { ...config.options, show_legend: e.target.checked }
                })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Show Legend</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={config.options?.show_grid !== false}
                onChange={(e) => setConfig({
                  ...config,
                  options: { ...config.options, show_grid: e.target.checked }
                })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Show Grid Lines</span>
            </label>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="sticky bottom-0 bg-white border-t border-gray-200 p-6 space-y-3">
          <button
            onClick={handleSave}
            disabled={loading}
            className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors flex items-center justify-center gap-2 font-medium"
          >
            <Save className="w-5 h-5" />
            {loading ? 'Saving...' : 'Save Changes'}
          </button>

          <div className="flex gap-3">
            <button
              onClick={onDuplicate}
              className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
            >
              <Copy className="w-4 h-4" />
              Duplicate
            </button>

            <button
              onClick={handleDelete}
              className="flex-1 bg-red-100 text-red-700 px-4 py-2 rounded-lg hover:bg-red-200 transition-colors flex items-center justify-center gap-2"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
