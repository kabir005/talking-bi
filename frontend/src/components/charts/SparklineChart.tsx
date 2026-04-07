import React from 'react';
import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface SparklineChartProps {
  data: any[];
  config: {
    x_column: string;
    y_column: string;
    title?: string;
    showValue?: boolean;
    showTrend?: boolean;
  };
}

export const SparklineChart: React.FC<SparklineChartProps> = ({ data, config }) => {
  const chartData = React.useMemo(() => {
    if (!data || data.length === 0) return [];
    
    return data.map(item => ({
      value: parseFloat(item[config.y_column]) || 0
    }));
  }, [data, config]);

  const stats = React.useMemo(() => {
    if (chartData.length === 0) return { current: 0, min: 0, max: 0, trend: 0, trendPercent: 0 };
    
    const values = chartData.map(d => d.value);
    const current = values[values.length - 1];
    const previous = values[0];
    const min = Math.min(...values);
    const max = Math.max(...values);
    const trend = current - previous;
    const trendPercent = previous !== 0 ? (trend / previous) * 100 : 0;
    
    return { current, min, max, trend, trendPercent };
  }, [chartData]);

  const getTrendColor = () => {
    if (stats.trend > 0) return '#22C55E'; // Green
    if (stats.trend < 0) return '#EF4444'; // Red
    return '#6B7280'; // Gray
  };

  const getTrendIcon = () => {
    if (stats.trend > 0) return <TrendingUp className="w-4 h-4" />;
    if (stats.trend < 0) return <TrendingDown className="w-4 h-4" />;
    return <Minus className="w-4 h-4" />;
  };

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-16 text-gray-400 text-sm">
        No data
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3 w-full">
      {/* Value and Trend */}
      {(config.showValue || config.showTrend) && (
        <div className="flex flex-col items-start min-w-[100px]">
          {config.showValue && (
            <div className="text-2xl font-bold text-gray-800">
              {stats.current.toFixed(0)}
            </div>
          )}
          {config.showTrend && (
            <div 
              className="flex items-center gap-1 text-sm font-medium"
              style={{ color: getTrendColor() }}
            >
              {getTrendIcon()}
              <span>
                {stats.trend > 0 ? '+' : ''}{stats.trendPercent.toFixed(1)}%
              </span>
            </div>
          )}
        </div>
      )}

      {/* Sparkline */}
      <div className="flex-1 h-16">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <YAxis domain={[stats.min * 0.95, stats.max * 1.05]} hide />
            <Line
              type="monotone"
              dataKey="value"
              stroke={getTrendColor()}
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Title */}
      {config.title && (
        <div className="text-sm text-gray-600 min-w-[80px] text-right">
          {config.title}
        </div>
      )}
    </div>
  );
};
