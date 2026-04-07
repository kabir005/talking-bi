import React from 'react';
import { ChevronRight, Home } from 'lucide-react';

export interface DrillDownLevel {
  label: string;
  value: string;
  column: string;
}

interface DrillDownProps {
  levels: DrillDownLevel[];
  onNavigate: (index: number) => void;
  onReset: () => void;
}

export const DrillDown: React.FC<DrillDownProps> = ({
  levels,
  onNavigate,
  onReset
}) => {
  if (levels.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-2 px-4 py-3 bg-gray-50 border-b border-gray-200">
      <button
        onClick={onReset}
        className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-white rounded-md transition-colors"
        title="Reset to top level"
      >
        <Home className="w-4 h-4" />
        <span>All Data</span>
      </button>

      {levels.map((level, index) => (
        <React.Fragment key={index}>
          <ChevronRight className="w-4 h-4 text-gray-400" />
          <button
            onClick={() => onNavigate(index)}
            className={`
              px-3 py-1.5 text-sm font-medium rounded-md transition-colors
              ${index === levels.length - 1
                ? 'text-blue-600 bg-blue-50'
                : 'text-gray-700 hover:text-blue-600 hover:bg-white'
              }
            `}
            title={`${level.column}: ${level.value}`}
          >
            <span className="text-gray-500 mr-1">{level.column}:</span>
            {level.label}
          </button>
        </React.Fragment>
      ))}
    </div>
  );
};

export interface DrillDownState {
  levels: DrillDownLevel[];
  filters: Record<string, string>;
}

export const useDrillDown = () => {
  const [state, setState] = React.useState<DrillDownState>({
    levels: [],
    filters: {}
  });

  const drillDown = React.useCallback((column: string, value: string, label?: string) => {
    setState(prev => ({
      levels: [...prev.levels, { column, value, label: label || value }],
      filters: { ...prev.filters, [column]: value }
    }));
  }, []);

  const navigateToLevel = React.useCallback((index: number) => {
    setState(prev => {
      const newLevels = prev.levels.slice(0, index + 1);
      const newFilters: Record<string, string> = {};
      newLevels.forEach(level => {
        newFilters[level.column] = level.value;
      });
      return { levels: newLevels, filters: newFilters };
    });
  }, []);

  const reset = React.useCallback(() => {
    setState({ levels: [], filters: {} });
  }, []);

  return {
    levels: state.levels,
    filters: state.filters,
    drillDown,
    navigateToLevel,
    reset
  };
};
