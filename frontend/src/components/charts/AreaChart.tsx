import { AreaChart as RechartsArea, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface AreaChartProps {
  data: any[];
  xKey: string;
  yKey: string;
  title?: string;
  color?: string;
}

export default function AreaChart({ data, xKey, yKey, title, color = '#F5A623' }: AreaChartProps) {
  return (
    <div className="w-full h-full">
      {title && <h3 className="text-lg font-heading font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height="100%">
        <RechartsArea data={data}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={color} stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis 
            dataKey={xKey} 
            stroke="var(--color-text-secondary)"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="var(--color-text-secondary)"
            style={{ fontSize: '12px' }}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: '8px',
              color: 'var(--color-text-primary)'
            }}
          />
          <Legend />
          <Area 
            type="monotone" 
            dataKey={yKey} 
            stroke={color} 
            fillOpacity={1} 
            fill="url(#colorValue)" 
          />
        </RechartsArea>
      </ResponsiveContainer>
    </div>
  );
}
