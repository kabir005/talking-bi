import React from 'react';
import { LayoutGrid, TrendingUp, BarChart3, GitCompare } from 'lucide-react';

interface PresetOption {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

interface PresetSelectorProps {
  selectedPreset?: string;
  onSelectPreset: (presetId: string) => void;
}

const PRESETS: PresetOption[] = [
  {
    id: 'executive',
    name: 'Executive',
    description: 'High-level KPIs and key metrics',
    icon: <LayoutGrid className="w-6 h-6" />,
    color: 'from-blue-500 to-blue-600'
  },
  {
    id: 'operational',
    name: 'Operational',
    description: 'Detailed operational metrics',
    icon: <BarChart3 className="w-6 h-6" />,
    color: 'from-green-500 to-green-600'
  },
  {
    id: 'trend',
    name: 'Trend Analysis',
    description: 'Time-series and trend visualization',
    icon: <TrendingUp className="w-6 h-6" />,
    color: 'from-purple-500 to-purple-600'
  },
  {
    id: 'comparison',
    name: 'Comparison',
    description: 'Period-over-period comparison',
    icon: <GitCompare className="w-6 h-6" />,
    color: 'from-amber-500 to-amber-600'
  }
];

export const PresetSelector: React.FC<PresetSelectorProps> = ({
  selectedPreset,
  onSelectPreset
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4">
      {PRESETS.map((preset) => (
        <button
          key={preset.id}
          onClick={() => onSelectPreset(preset.id)}
          className={`
            relative overflow-hidden rounded-lg border-2 transition-all duration-200
            ${selectedPreset === preset.id
              ? 'border-blue-500 shadow-lg scale-105'
              : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
            }
          `}
        >
          <div className={`
            bg-gradient-to-br ${preset.color} p-6 text-white
            ${selectedPreset === preset.id ? 'opacity-100' : 'opacity-90'}
          `}>
            <div className="flex items-center justify-center mb-3">
              {preset.icon}
            </div>
            <h3 className="font-semibold text-lg mb-1">{preset.name}</h3>
            <p className="text-sm opacity-90">{preset.description}</p>
          </div>
          
          {selectedPreset === preset.id && (
            <div className="absolute top-2 right-2 bg-white rounded-full p-1">
              <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
          )}
        </button>
      ))}
    </div>
  );
};
