import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer } from 'recharts';
import { useState, useEffect } from 'react';
import { formatCurrency, formatDualCurrency } from '../../api/client';

interface KPICardProps {
  label: string;
  value: number | string;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  format?: 'number' | 'currency' | 'percent';
  sparkline?: Array<{ x: string; y: number }>;
  prefix?: string;
  suffix?: string;
  currency?: 'INR' | 'USD' | 'DUAL';
  exchangeRate?: number;
}

export default function KPICard({ 
  label, 
  value, 
  change, 
  trend = 'neutral',
  format = 'number',
  sparkline,
  prefix = '',
  suffix = '',
  currency = 'INR',
  exchangeRate = 83.0
}: KPICardProps) {
  const [formattedCurrency, setFormattedCurrency] = useState<string>('');
  
  useEffect(() => {
    if (format === 'currency' && typeof value === 'number') {
      formatCurrencyValue(value);
    }
  }, [value, format, currency, exchangeRate]);

  const formatCurrencyValue = async (val: number) => {
    try {
      if (currency === 'DUAL') {
        const result = await formatDualCurrency({
          amount: val,
          primary_currency: 'INR',
          secondary_currency: 'USD',
          exchange_rate: exchangeRate,
          decimals: 2
        });
        setFormattedCurrency(result.formatted);
      } else {
        const result = await formatCurrency({
          amount: val,
          currency: currency,
          use_indian_format: currency === 'INR',
          decimals: 2
        });
        setFormattedCurrency(result.formatted);
      }
    } catch (error) {
      // Fallback to local formatting
      setFormattedCurrency(val.toLocaleString(undefined, { maximumFractionDigits: 0 }));
    }
  };
  
  const formatValue = (val: number | string) => {
    if (typeof val === 'string') return val;
    
    let formatted = '';
    switch (format) {
      case 'currency':
        // Use the formatted currency from API if available
        return formattedCurrency || `${val.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
      case 'percent':
        formatted = `${val.toFixed(1)}%`;
        break;
      default:
        formatted = val.toLocaleString(undefined, { maximumFractionDigits: 2 });
    }
    
    return `${prefix}${formatted}${suffix}`;
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4" />;
      case 'down':
        return <TrendingDown className="w-4 h-4" />;
      default:
        return <Minus className="w-4 h-4" />;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-emerald-400';
      case 'down':
        return 'text-rose-400';
      default:
        return 'text-slate-400';
    }
  };

  const getSparklineColor = () => {
    switch (trend) {
      case 'up':
        return '#10b981'; // emerald-500
      case 'down':
        return '#f43f5e'; // rose-500
      default:
        return '#3b82f6'; // blue-500
    }
  };

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg border border-slate-700 p-5 hover:border-accent transition-all duration-200 shadow-lg hover:shadow-xl">
      {/* Label */}
      <div className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-3">
        {label}
      </div>
      
      {/* Value */}
      <div className="font-bold text-3xl text-white mb-2 tracking-tight">
        {formatValue(value)}
      </div>
      
      {/* Change indicator */}
      {change !== undefined && (
        <div className={`flex items-center gap-1.5 text-sm font-medium ${getTrendColor()} mb-3`}>
          {getTrendIcon()}
          <span>
            {change > 0 ? '+' : ''}{change.toFixed(1)}%
          </span>
          <span className="text-slate-500 text-xs ml-1">vs prev</span>
        </div>
      )}
      
      {/* Sparkline */}
      {sparkline && sparkline.length > 0 && (
        <div className="h-12 -mx-2 mt-auto">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={sparkline}>
              <Line 
                type="monotone" 
                dataKey="y" 
                stroke={getSparklineColor()}
                strokeWidth={2}
                dot={false}
                animationDuration={300}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
