import React from 'react';
import LineChart from './LineChart';
import BarChart from './BarChart';
import PieChart from './PieChart';
import ScatterChart from './ScatterChart';

interface ChartCardProps {
  config: {
    type: string;
    title: string;
    data: any;
    options?: Record<string, any>;
  };
}

export const ChartCard: React.FC<ChartCardProps> = ({ config }) => {
  const { type, title, data } = config;

  // Extract data for charts based on structure
  const getChartData = () => {
    // If data has labels and datasets (Chart.js format)
    if (data.labels && data.datasets) {
      const labels = data.labels;
      const values = data.datasets[0]?.data || [];
      
      // Convert to array of objects for Recharts
      return labels.map((label: string, index: number) => ({
        name: label,
        value: values[index]
      }));
    }
    
    // If data is already array of objects
    if (Array.isArray(data)) {
      return data;
    }
    
    // If data has datasets with x/y format (scatter)
    if (data.datasets && Array.isArray(data.datasets[0]?.data)) {
      return data.datasets[0].data;
    }
    
    return [];
  };

  const chartData = getChartData();
  
  // Determine keys for x and y axes
  const xKey = chartData.length > 0 ? Object.keys(chartData[0])[0] : 'name';
  const yKey = chartData.length > 0 ? Object.keys(chartData[0])[1] || 'value' : 'value';

  const renderChart = () => {
    if (!chartData || chartData.length === 0) {
      return (
        <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
          No data available for chart
        </div>
      );
    }

    switch (type) {
      case 'line':
        return <LineChart data={chartData} xKey={xKey} yKey={yKey} title={title} />;
      case 'bar':
        return <BarChart data={chartData} xKey={xKey} yKey={yKey} title={title} />;
      case 'pie':
        return <PieChart data={chartData} nameKey={xKey} valueKey={yKey} title={title} />;
      case 'scatter':
        return <ScatterChart data={chartData} xKey={xKey} yKey={yKey} title={title} />;
      default:
        return <BarChart data={chartData} xKey={xKey} yKey={yKey} title={title} />;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
      <div style={{ height: '300px' }}>
        {renderChart()}
      </div>
    </div>
  );
};
