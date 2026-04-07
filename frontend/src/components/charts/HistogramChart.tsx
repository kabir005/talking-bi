import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface HistogramChartProps {
  data: any[];
  xKey?: string;
  yKey?: string;
  title?: string;
  color?: string;
}

export default function HistogramChart({ 
  data, 
  xKey = 'value', 
  yKey = 'count',
  title: _title,
  color = '#F5A623' 
}: HistogramChartProps) {
  
  // Process data into bins if raw values provided
  const processedData = data.length > 0 && data[0].value !== undefined && data[0].count === undefined
    ? createHistogramBins(data.map(d => d.value))
    : data;

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={processedData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2A2A2A" />
        <XAxis 
          dataKey={xKey} 
          stroke="#888"
          tick={{ fill: '#888', fontSize: 12 }}
        />
        <YAxis 
          stroke="#888"
          tick={{ fill: '#888', fontSize: 12 }}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#1A1A1A', 
            border: '1px solid #2A2A2A',
            borderRadius: '8px'
          }}
        />
        <Bar dataKey={yKey || 'count'} fill={color} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function createHistogramBins(values: number[], binCount: number = 10) {
  if (values.length === 0) return [];
  
  const min = Math.min(...values);
  const max = Math.max(...values);
  const binSize = (max - min) / binCount;
  
  const bins = Array(binCount).fill(0).map((_, i) => ({
    bin: `${(min + i * binSize).toFixed(1)}-${(min + (i + 1) * binSize).toFixed(1)}`,
    count: 0,
    x: min + i * binSize
  }));
  
  values.forEach(value => {
    const binIndex = Math.min(Math.floor((value - min) / binSize), binCount - 1);
    bins[binIndex].count++;
  });
  
  return bins.map(b => ({ value: b.bin, count: b.count }));
}
