import { PieChart as RechartsPie, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface PieChartProps {
  data: any[];
  nameKey: string;
  valueKey: string;
  title?: string;
}

const COLORS = ['#F5A623', '#3B82F6', '#22C55E', '#EC4899', '#8B5CF6', '#14B8A6'];

export default function PieChart({ data, nameKey, valueKey, title }: PieChartProps) {
  return (
    <div className="w-full h-full">
      {title && <h3 className="text-lg font-heading font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height="100%">
        <RechartsPie>
          <Pie
            data={data}
            dataKey={valueKey}
            nameKey={nameKey}
            cx="50%"
            cy="50%"
            outerRadius={80}
            label
          >
            {data.map((_entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: '8px',
              color: 'var(--color-text-primary)'
            }}
          />
          <Legend />
        </RechartsPie>
      </ResponsiveContainer>
    </div>
  );
}
