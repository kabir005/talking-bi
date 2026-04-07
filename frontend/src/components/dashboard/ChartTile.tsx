import { Settings, Maximize2, Trash2, GripVertical } from 'lucide-react';
import { ChartTile as ChartTileType } from '../../types';
import LineChart from '../charts/LineChart';
import BarChart from '../charts/BarChart';
import AreaChart from '../charts/AreaChart';
import PieChart from '../charts/PieChart';
import ScatterChart from '../charts/ScatterChart';
import HistogramChart from '../charts/HistogramChart';
import HeatmapChart from '../charts/HeatmapChart';
import KPICard from './KPICard';

interface ChartTileProps {
  tile: ChartTileType;
  data: any[];
  onEdit?: () => void;
  onDuplicate?: () => void;
  onDelete?: () => void;
  onFullscreen?: () => void;
}

export default function ChartTile({ 
  tile, 
  data, 
  onEdit, 
  onDuplicate: _onDuplicate, 
  onDelete, 
  onFullscreen 
}: ChartTileProps) {
  
  // Extract config from tile
  const config = tile.config || tile;
  const chartType = config.type || tile.type;
  const title = config.title || tile.title;
  
  // If it's a KPI card, render it directly without the wrapper
  if (chartType === 'kpi') {
    return (
      <div className="h-full">
        <KPICard
          label={title}
          value={config.value || 0}
          change={config.change}
          trend={config.trend || 'neutral'}
          sparkline={config.sparkline}
          prefix={config.prefix}
          suffix={config.suffix}
        />
      </div>
    );
  }
  
  const renderChart = () => {
    // Backend aggregate_chart_data returns data with keys "x" and "y"
    const chartProps = {
      data,
      xKey: 'x',
      yKey: 'y',
      title: title,
      color: config.options?.colors?.[0] || config.colors?.[0] || '#F5A623'
    };
    
    if (!data || data.length === 0) {
      console.warn(`Chart ${tile.id} has no data:`, { title, type: chartType });
    }

    switch (chartType) {
      case 'line':
        return <LineChart {...chartProps} />;
      case 'bar':
        return <BarChart {...chartProps} />;
      case 'area':
        return <AreaChart {...chartProps} />;
      case 'pie':
        return <PieChart 
          data={data} 
          nameKey="name" 
          valueKey="value" 
          title={title} 
        />;
      case 'scatter':
        return <ScatterChart {...chartProps} />;
      case 'histogram':
        return <HistogramChart data={data} title={title} color={chartProps.color} />;
      case 'heatmap':
        return <HeatmapChart data={data} title={title} />;
      default:
        return (
          <div className="flex items-center justify-center h-full text-slate-400">
            Chart type "{chartType}" not yet implemented
          </div>
        );
    }
  };

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg border border-slate-700 h-full flex flex-col overflow-hidden hover:border-accent transition-all duration-200 shadow-lg">
      {/* Header with drag handle */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700 bg-slate-800/50">
        <div className="flex items-center gap-2">
          <GripVertical size={16} className="text-slate-500 drag-handle cursor-move" />
          <h3 className="font-semibold text-white text-sm truncate">{title}</h3>
        </div>
        
        <div className="flex items-center gap-1">
          {onFullscreen && (
            <button
              onClick={onFullscreen}
              className="p-1.5 hover:bg-slate-700 rounded transition-colors text-slate-400 hover:text-white"
              title="Fullscreen"
            >
              <Maximize2 size={14} />
            </button>
          )}
          {onEdit && (
            <button
              onClick={onEdit}
              className="p-1.5 hover:bg-slate-700 rounded transition-colors text-slate-400 hover:text-white"
              title="Edit"
            >
              <Settings size={14} />
            </button>
          )}
          {onDelete && (
            <button
              onClick={onDelete}
              className="p-1.5 hover:bg-red-500/10 text-red-400 hover:text-red-300 rounded transition-colors"
              title="Delete"
            >
              <Trash2 size={14} />
            </button>
          )}
        </div>
      </div>
      
      {/* Chart Body */}
      <div className="flex-1 p-4 min-h-0">
        {data && data.length > 0 ? (
          renderChart()
        ) : (
          <div className="flex items-center justify-center h-full text-slate-500">
            No data available
          </div>
        )}
      </div>
    </div>
  );
}
