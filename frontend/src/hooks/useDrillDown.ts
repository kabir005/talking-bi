import { useState, useCallback } from 'react';
import axios from 'axios';

export interface DrillDownLevel {
  column: string;
  value: string;
  label: string;
}

export interface DrillDownState {
  levels: DrillDownLevel[];
  filters: Record<string, string>;
}

export interface DrillDownData {
  row_count: number;
  summary: Record<string, any>;
  sample_data: any[];
}

export const useDrillDown = (datasetId: string) => {
  const [state, setState] = useState<DrillDownState>({
    levels: [],
    filters: {}
  });
  const [data, setData] = useState<DrillDownData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const drillDown = useCallback(async (column: string, value: string, label?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const newFilters = { ...state.filters, [column]: value };
      
      const response = await axios.post('/api/drilldown/data', {
        dataset_id: datasetId,
        column,
        value,
        parent_filters: state.filters
      });

      setState(prev => ({
        levels: [...prev.levels, { column, value, label: label || value }],
        filters: newFilters
      }));

      setData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to drill down');
    } finally {
      setIsLoading(false);
    }
  }, [datasetId, state.filters]);

  const navigateToLevel = useCallback(async (index: number) => {
    setIsLoading(true);
    setError(null);

    try {
      const newLevels = state.levels.slice(0, index + 1);
      const newFilters: Record<string, string> = {};
      newLevels.forEach(level => {
        newFilters[level.column] = level.value;
      });

      const lastLevel = newLevels[newLevels.length - 1];
      const response = await axios.post('/api/drilldown/data', {
        dataset_id: datasetId,
        column: lastLevel.column,
        value: lastLevel.value,
        parent_filters: Object.fromEntries(
          Object.entries(newFilters).filter(([k]) => k !== lastLevel.column)
        )
      });

      setState({ levels: newLevels, filters: newFilters });
      setData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to navigate');
    } finally {
      setIsLoading(false);
    }
  }, [datasetId, state.levels]);

  const reset = useCallback(async () => {
    setState({ levels: [], filters: {} });
    setData(null);
    setError(null);
  }, []);

  const getSuggestions = useCallback(async () => {
    try {
      const response = await axios.post('/api/drilldown/suggest-next', {
        dataset_id: datasetId,
        column: state.levels[state.levels.length - 1]?.column,
        value: state.levels[state.levels.length - 1]?.value,
        parent_filters: state.filters
      });

      return response.data.suggestions;
    } catch (err) {
      console.error('Failed to get suggestions:', err);
      return [];
    }
  }, [datasetId, state.levels, state.filters]);

  return {
    levels: state.levels,
    filters: state.filters,
    data,
    isLoading,
    error,
    drillDown,
    navigateToLevel,
    reset,
    getSuggestions
  };
};
