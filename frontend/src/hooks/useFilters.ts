import { useState, useCallback } from 'react';
import axios from 'axios';

export interface FilterConfig {
  id: string;
  column: string;
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than' | 'between' | 'in';
  value: string | number | [number, number] | string[];
  type: 'string' | 'number' | 'date';
}

export interface FilterResult {
  original_count: number;
  filtered_count: number;
  rows_removed: number;
  percentage_remaining: number;
  summary: Record<string, any>;
  data?: any[];
}

export const useFilters = (datasetId: string) => {
  const [filters, setFilters] = useState<FilterConfig[]>([]);
  const [result, setResult] = useState<FilterResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addFilter = useCallback((filter: Omit<FilterConfig, 'id'>) => {
    const newFilter: FilterConfig = {
      ...filter,
      id: `filter_${Date.now()}_${Math.random()}`
    };
    setFilters(prev => [...prev, newFilter]);
  }, []);

  const removeFilter = useCallback((id: string) => {
    setFilters(prev => prev.filter(f => f.id !== id));
  }, []);

  const updateFilter = useCallback((id: string, updates: Partial<FilterConfig>) => {
    setFilters(prev => prev.map(f => f.id === id ? { ...f, ...updates } : f));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters([]);
    setResult(null);
  }, []);

  const applyFilters = useCallback(async (returnData: boolean = false) => {
    if (filters.length === 0) {
      setError('No filters to apply');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/filters/apply', {
        dataset_id: datasetId,
        filters,
        return_data: returnData,
        limit: 1000
      });

      setResult(response.data);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to apply filters');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [datasetId, filters]);

  const validateFilter = useCallback(async (filter: Omit<FilterConfig, 'id'>) => {
    try {
      const response = await axios.post('/api/filters/validate', filter, {
        params: { dataset_id: datasetId }
      });
      return response.data;
    } catch (err: any) {
      return {
        valid: false,
        error: err.response?.data?.detail || 'Validation failed'
      };
    }
  }, [datasetId]);

  const getSuggestions = useCallback(async (column: string, limit: number = 10) => {
    try {
      const response = await axios.get(`/api/filters/suggestions/${datasetId}/${column}`, {
        params: { limit }
      });
      return response.data;
    } catch (err) {
      console.error('Failed to get suggestions:', err);
      return { suggested_values: [], value_counts: {} };
    }
  }, [datasetId]);

  const getRange = useCallback(async (column: string) => {
    try {
      const response = await axios.post('/api/filters/range', null, {
        params: { dataset_id: datasetId, column }
      });
      return response.data;
    } catch (err) {
      console.error('Failed to get range:', err);
      return null;
    }
  }, [datasetId]);

  return {
    filters,
    result,
    isLoading,
    error,
    addFilter,
    removeFilter,
    updateFilter,
    clearFilters,
    applyFilters,
    validateFilter,
    getSuggestions,
    getRange
  };
};
