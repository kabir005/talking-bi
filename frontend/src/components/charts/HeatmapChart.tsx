import { useMemo } from 'react';

interface HeatmapChartProps {
  data: any[];
  title?: string;
}

export default function HeatmapChart({ data, title: _title }: HeatmapChartProps) {
  
  const { matrix, xLabels, yLabels, minValue, maxValue } = useMemo(() => {
    if (!data || data.length === 0) {
      return { matrix: [], xLabels: [], yLabels: [], minValue: 0, maxValue: 1 };
    }

    // Extract unique x and y labels
    const xSet = new Set(data.map(d => d.x));
    const ySet = new Set(data.map(d => d.y));
    const xLabels = Array.from(xSet);
    const yLabels = Array.from(ySet);

    // Create matrix
    const matrix: number[][] = [];
    const values: number[] = [];
    
    yLabels.forEach(yLabel => {
      const row: number[] = [];
      xLabels.forEach(xLabel => {
        const point = data.find(d => d.x === xLabel && d.y === yLabel);
        const value = point?.value ?? 0;
        row.push(value);
        values.push(value);
      });
      matrix.push(row);
    });

    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);

    return { matrix, xLabels, yLabels, minValue, maxValue };
  }, [data]);

  const getColor = (value: number) => {
    if (maxValue === minValue) return 'rgb(245, 166, 35)';
    
    const normalized = (value - minValue) / (maxValue - minValue);
    
    // Color scale from blue (low) to orange (high)
    if (normalized < 0.5) {
      const t = normalized * 2;
      return `rgb(${Math.round(59 + (245 - 59) * t)}, ${Math.round(130 + (166 - 130) * t)}, ${Math.round(246 + (35 - 246) * t)})`;
    } else {
      const t = (normalized - 0.5) * 2;
      return `rgb(${Math.round(245)}, ${Math.round(166 - 66 * t)}, ${Math.round(35)})`;
    }
  };

  if (matrix.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-text-tertiary">
        No data available
      </div>
    );
  }

  const cellSize = Math.min(
    (400 - 100) / xLabels.length,
    (300 - 80) / yLabels.length,
    40
  );

  return (
    <div className="flex items-center justify-center h-full overflow-auto p-4">
      <div className="inline-block">
        <svg 
          width={xLabels.length * cellSize + 100} 
          height={yLabels.length * cellSize + 80}
          className="font-mono text-xs"
        >
          {/* Y-axis labels */}
          {yLabels.map((label, i) => (
            <text
              key={`y-${i}`}
              x={90}
              y={i * cellSize + cellSize / 2 + 40}
              textAnchor="end"
              dominantBaseline="middle"
              fill="#888"
              fontSize="10"
            >
              {String(label).length > 12 ? String(label).substring(0, 12) + '...' : label}
            </text>
          ))}

          {/* X-axis labels */}
          {xLabels.map((label, i) => (
            <text
              key={`x-${i}`}
              x={i * cellSize + cellSize / 2 + 100}
              y={30}
              textAnchor="middle"
              fill="#888"
              fontSize="10"
              transform={`rotate(-45, ${i * cellSize + cellSize / 2 + 100}, 30)`}
            >
              {String(label).length > 12 ? String(label).substring(0, 12) + '...' : label}
            </text>
          ))}

          {/* Heatmap cells */}
          {matrix.map((row, i) =>
            row.map((value, j) => (
              <g key={`cell-${i}-${j}`}>
                <rect
                  x={j * cellSize + 100}
                  y={i * cellSize + 40}
                  width={cellSize - 2}
                  height={cellSize - 2}
                  fill={getColor(value)}
                  rx={2}
                />
                <text
                  x={j * cellSize + cellSize / 2 + 100}
                  y={i * cellSize + cellSize / 2 + 40}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill={value > (maxValue - minValue) * 0.6 + minValue ? '#000' : '#fff'}
                  fontSize="9"
                  fontWeight="500"
                >
                  {value.toFixed(2)}
                </text>
              </g>
            ))
          )}
        </svg>
      </div>
    </div>
  );
}
