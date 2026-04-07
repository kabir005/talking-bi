import React, { useState } from 'react';
import { Filter, X, Plus, Calendar, Hash, Type } from 'lucide-react';

export interface FilterConfig {
  id: string;
  column: string;
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than' | 'between' | 'in';
  value: string | number | [number, number] | string[];
  type: 'string' | 'number' | 'date';
}

interface FilterBarProps {
  columns: Array<{ name: string; type: string }>;
  filters: FilterConfig[];
  onFiltersChange: (filters: FilterConfig[]) => void;
}

const OPERATORS = {
  string: [
    { value: 'equals', label: 'Equals' },
    { value: 'contains', label: 'Contains' }
  ],
  number: [
    { value: 'equals', label: 'Equals' },
    { value: 'greater_than', label: 'Greater than' },
    { value: 'less_than', label: 'Less than' },
    { value: 'between', label: 'Between' }
  ],
  date: [
    { value: 'equals', label: 'On' },
    { value: 'greater_than', label: 'After' },
    { value: 'less_than', label: 'Before' },
    { value: 'between', label: 'Between' }
  ]
};

export const FilterBar: React.FC<FilterBarProps> = ({
  columns,
  filters,
  onFiltersChange
}) => {
  const [isExpanded, setIsExpanded] = useState(filters.length > 0);
  const [editingFilter, setEditingFilter] = useState<Partial<FilterConfig> | null>(null);

  const addFilter = () => {
    if (!columns.length) return;
    
    const firstColumn = columns[0];
    setEditingFilter({
      id: `filter_${Date.now()}`,
      column: firstColumn.name,
      type: firstColumn.type as 'string' | 'number' | 'date',
      operator: 'equals',
      value: ''
    });
  };

  const saveFilter = () => {
    if (!editingFilter || !editingFilter.column || !editingFilter.value) return;
    
    const newFilter: FilterConfig = {
      id: editingFilter.id || `filter_${Date.now()}`,
      column: editingFilter.column,
      type: editingFilter.type || 'string',
      operator: editingFilter.operator || 'equals',
      value: editingFilter.value
    };

    const existingIndex = filters.findIndex(f => f.id === newFilter.id);
    if (existingIndex >= 0) {
      const updated = [...filters];
      updated[existingIndex] = newFilter;
      onFiltersChange(updated);
    } else {
      onFiltersChange([...filters, newFilter]);
    }
    
    setEditingFilter(null);
  };

  const removeFilter = (id: string) => {
    onFiltersChange(filters.filter(f => f.id !== id));
  };

  const clearAllFilters = () => {
    onFiltersChange([]);
    setIsExpanded(false);
  };

  const getColumnType = (columnName: string): 'string' | 'number' | 'date' => {
    const column = columns.find(c => c.name === columnName);
    return (column?.type as 'string' | 'number' | 'date') || 'string';
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'number': return <Hash className="w-4 h-4" />;
      case 'date': return <Calendar className="w-4 h-4" />;
      default: return <Type className="w-4 h-4" />;
    }
  };

  return (
    <div className="border-b border-gray-200 bg-white">
      <div className="flex items-center justify-between px-4 py-3">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900"
        >
          <Filter className="w-4 h-4" />
          <span>Filters</span>
          {filters.length > 0 && (
            <span className="px-2 py-0.5 text-xs font-semibold text-blue-600 bg-blue-100 rounded-full">
              {filters.length}
            </span>
          )}
        </button>

        <div className="flex items-center gap-2">
          {filters.length > 0 && (
            <button
              onClick={clearAllFilters}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Clear all
            </button>
          )}
          <button
            onClick={addFilter}
            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Filter
          </button>
        </div>
      </div>

      {isExpanded && (filters.length > 0 || editingFilter) && (
        <div className="px-4 pb-3 space-y-2">
          {filters.map(filter => (
            <div
              key={filter.id}
              className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-md"
            >
              <div className="flex items-center gap-2 flex-1">
                {getTypeIcon(filter.type)}
                <span className="text-sm font-medium text-gray-700">{filter.column}</span>
                <span className="text-sm text-gray-500">{filter.operator.replace('_', ' ')}</span>
                <span className="text-sm font-medium text-gray-900">
                  {Array.isArray(filter.value) ? filter.value.join(' - ') : filter.value}
                </span>
              </div>
              <button
                onClick={() => removeFilter(filter.id)}
                className="p-1 text-gray-400 hover:text-red-600 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}

          {editingFilter && (
            <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 border border-blue-200 rounded-md">
              <select
                value={editingFilter.column}
                onChange={(e) => {
                  const type = getColumnType(e.target.value);
                  setEditingFilter({
                    ...editingFilter,
                    column: e.target.value,
                    type,
                    operator: 'equals'
                  });
                }}
                className="px-2 py-1 text-sm border border-gray-300 rounded"
              >
                {columns.map(col => (
                  <option key={col.name} value={col.name}>{col.name}</option>
                ))}
              </select>

              <select
                value={editingFilter.operator}
                onChange={(e) => setEditingFilter({
                  ...editingFilter,
                  operator: e.target.value as FilterConfig['operator']
                })}
                className="px-2 py-1 text-sm border border-gray-300 rounded"
              >
                {OPERATORS[editingFilter.type || 'string'].map(op => (
                  <option key={op.value} value={op.value}>{op.label}</option>
                ))}
              </select>

              <input
                type={editingFilter.type === 'number' ? 'number' : editingFilter.type === 'date' ? 'date' : 'text'}
                value={editingFilter.value as string}
                onChange={(e) => setEditingFilter({
                  ...editingFilter,
                  value: editingFilter.type === 'number' ? parseFloat(e.target.value) : e.target.value
                })}
                placeholder="Value..."
                className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded"
              />

              <button
                onClick={saveFilter}
                className="px-3 py-1 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded"
              >
                Apply
              </button>
              <button
                onClick={() => setEditingFilter(null)}
                className="p-1 text-gray-400 hover:text-gray-600 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
