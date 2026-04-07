import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';

interface WaterfallChartProps {
  data: any[];
  config: {
    x_column: string;
    y_column: string;
    title?: string;
    colors?: string[];
  };
}

export const WaterfallChart: React.FC<WaterfallChartProps> = ({ data, config }) => {
  // Transform data for waterfall chart
  const transformedData = React.useMemo(() => {
    if (!data || data.length === 0) return [];

    let cumulative = 0;
    const result = data.map((item, index) => {
      const value = parseFloat(item[config.y_column]) || 0;
      const start = cumulative;
      cumulative += value;
      
      return {
        name: item[config.x_column],
        value: value,
        start: start,
        end: cumulative,
        isPositive: value >= 0,
        isTotal: index === data.length - 1
      };
    });

    return result;
  }, [data, config]);

  const getColor = (item: any) => {
    if (item.isTotal) return '#6B7280'; // Gray for total
    return item.isPositive ? '#22C55E' : '#EF4444'; // Green for positive, red for negative
  };

  const CustomBar = (props: any) => {
    const { x, y, width, height, payload } = props;
    const barHeight = Math.abs(height);
    const barY = payload.isPositive ? y : y;

    return (
      <g>
        <rect
          x={x}
          y={barY}
          width={width}
          height={barHeight}
          fill={getColor(payload)}
          opacity={0.8}
        />
        {/* Connector line to next bar */}
        {props.index < transformedData.length - 1 && (
          <line
            x1={x + width}
            y1={barY + (payload.isPositive ? 0 : barHeight)}
            x2={x + width + 10}
            y2={barY + (payload.isPositive ? 0 : barHeight)}
            stroke="#9CA3AF"
            strokeWidth={1}
            strokeDasharray="3 3"
          />
        )}
      </g>
    );
  };

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No data available
      </div>
    );
  }

  return (
    <div className="w-full h-full">
      {config.title && (
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{config.title}</h3>
      )}
      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={transformedData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis 
            dataKey="name" 
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fontSize: 12 }}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value: number) => value.toFixed(2)}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              padding: '8px'
            }}
          />
          <Legend />
          <ReferenceLine y={0} stroke="#6B7280" strokeWidth={2} />
          <Bar 
            dataKey="value" 
            shape={<CustomBar />}
            name={config.y_column}
          >
            {transformedData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      
      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span className="text-gray-600">Increase</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded"></div>
          <span className="text-gray-600">Decrease</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-500 rounded"></div>
          <span className="text-gray-600">Total</span>
        </div>
      </div>
    </div>
  );
};
