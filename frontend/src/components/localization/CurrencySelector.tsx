import { DollarSign, IndianRupee } from 'lucide-react';

interface CurrencySelectorProps {
  value: 'INR' | 'USD' | 'DUAL';
  onChange: (currency: 'INR' | 'USD' | 'DUAL') => void;
  className?: string;
}

export default function CurrencySelector({ value, onChange, className = '' }: CurrencySelectorProps) {
  const options = [
    { value: 'INR', label: 'INR (₹)', icon: IndianRupee },
    { value: 'USD', label: 'USD ($)', icon: DollarSign },
    { value: 'DUAL', label: 'Both', icon: null },
  ] as const;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-xs text-text-secondary font-medium">Currency:</span>
      <div className="flex items-center gap-1 bg-surface-elevated rounded-lg p-1 border border-border">
        {options.map((option) => {
          const Icon = option.icon;
          const isActive = value === option.value;
          
          return (
            <button
              key={option.value}
              onClick={() => onChange(option.value as 'INR' | 'USD' | 'DUAL')}
              className={`
                flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200
                ${isActive
                  ? 'bg-primary text-white shadow-sm'
                  : 'text-text-secondary hover:text-text-primary hover:bg-white/[0.04]'
                }
              `}
            >
              {Icon && <Icon size={14} />}
              <span>{option.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
