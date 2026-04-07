import { ScatterChart as RechartsScatter, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ScatterChartProps {
  data: any[];
  xKey: string;
  yKey: string;
  title?: string;
  color?: string;
}

export default function ScatterChart({ data, xKey, yKey, title, color = '#F5A623' }: ScatterChartProps) {
  return (
    <div className="w-full h-full">
      {title && <h3 className="text-lg font-heading font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height="100%">
        <RechartsScatter>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis 
            type="number"
            dataKey={xKey} 
            name={xKey}
            stroke="var(--color-text-secondary)"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            type="number"
            dataKey={yKey} 
            name={yKey}
            stroke="var(--color-text-secondary)"
            style={{ fontSize: '12px' }}
          />
          <Tooltip 
            cursor={{ strokeDasharray: '3 3' }}
            contentStyle={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: '8px',
              color: 'var(--color-text-primary)'
            }}
          />
          <Legend />
          <Scatter name={yKey} data={data} fill={color} />
        </RechartsScatter>
      </ResponsiveContainer>
    </div>
  );
}
