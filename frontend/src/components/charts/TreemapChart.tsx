import React from 'react';
import { Treemap, ResponsiveContainer, Tooltip } from 'recharts';

interface TreemapChartProps {
  data: any[];
  config: {
    x_column: string;
    y_column: string;
    title?: string;
    colors?: string[];
  };
}

export const TreemapChart: React.FC<TreemapChartProps> = ({ data, config }) => {
  // Transform data for treemap
  const transformedData = React.useMemo(() => {
    if (!data || data.length === 0) return [];

    const children = data.map((item, index) => ({
      name: item[config.x_column],
      size: Math.abs(parseFloat(item[config.y_column]) || 0),
      value: parseFloat(item[config.y_column]) || 0,
      index: index
    }));

    return [{
      name: 'root',
      children: children
    }];
  }, [data, config]);

  const COLORS = config.colors || [
    '#3B82F6', '#22C55E', '#F59E0B', '#EF4444', 
    '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'
  ];

  const CustomContent = (props: any) => {
    const { x, y, width, height, index, name, value } = props;
    
    if (width < 40 || height < 40) return null;

    const color = COLORS[index % COLORS.length];
    const textColor = '#FFFFFF';
    const fontSize = Math.min(width / 8, height / 4, 14);

    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          style={{
            fill: color,
            stroke: '#fff',
            strokeWidth: 2,
            opacity: 0.9
          }}
        />
        {width > 60 && height > 40 && (
          <>
            <text
              x={x + width / 2}
              y={y + height / 2 - fontSize / 2}
              textAnchor="middle"
              fill={textColor}
              fontSize={fontSize}
              fontWeight="bold"
            >
              {name}
            </text>
            <text
              x={x + width / 2}
              y={y + height / 2 + fontSize}
              textAnchor="middle"
              fill={textColor}
              fontSize={fontSize * 0.8}
            >
              {value.toFixed(0)}
            </text>
          </>
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
        <Treemap
          data={transformedData}
          dataKey="size"
          aspectRatio={4 / 3}
          stroke="#fff"
          fill="#8884d8"
          content={<CustomContent />}
        >
          <Tooltip
            formatter={(value: number) => value.toFixed(2)}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              padding: '8px'
            }}
          />
        </Treemap>
      </ResponsiveContainer>
    </div>
  );
};
