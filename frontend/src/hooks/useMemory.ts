import { useState, useCallback } from 'react';
import axios from 'axios';

export interface QueryMemory {
  id: string;
  dataset_id: string;
  query_text: string;
  response_summary?: string;
  created_at: string;
}

export interface UserPreference {
  id: string;
  action_type: string;
  from_value: string;
  to_value: string;
  weight: number;
  created_at: string;
}

export const useMemory = (datasetId?: string) => {
  const [queries, setQueries] = useState<QueryMemory[]>([]);
  const [preferences, setPreferences] = useState<UserPreference[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadQueries = useCallback(async (limit: number = 10) => {
    setIsLoading(true);
    setError(null);

    try {
      const params: any = { limit };
      if (datasetId) {
        params.dataset_id = datasetId;
      }

      const response = await axios.get('/api/memory/queries', { params });
      setQueries(response.data.queries || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load queries');
    } finally {
      setIsLoading(false);
    }
  }, [datasetId]);

  const searchSimilar = useCallback(async (query: string, limit: number = 5) => {
    setIsLoading(true);
    setError(null);

    try {
      const params: any = { q: query, limit };
      if (datasetId) {
        params.dataset_id = datasetId;
      }

      const response = await axios.get('/api/memory/similar', { params });
      setQueries(response.data.similar_queries || []);
      return response.data.similar_queries;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to search queries');
      return [];
    } finally {
      setIsLoading(false);
    }
  }, [datasetId]);

  const saveQuery = useCallback(async (
    queryText: string,
    responseJson: Record<string, any>
  ) => {
    try {
      await axios.post('/api/memory/queries', {
        dataset_id: datasetId,
        query_text: queryText,
        response_json: responseJson
      });
      
      // Reload queries
      await loadQueries();
    } catch (err: any) {
      console.error('Failed to save query:', err);
    }
  }, [datasetId, loadQueries]);

  const deleteQuery = useCallback(async (queryId: string) => {
    try {
      await axios.delete(`/api/memory/queries/${queryId}`);
      setQueries(prev => prev.filter(q => q.id !== queryId));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete query');
    }
  }, []);

  const loadPreferences = useCallback(async (actionType?: string, limit: number = 50) => {
    setIsLoading(true);
    setError(null);

    try {
      const params: any = { limit };
      if (actionType) {
        params.action_type = actionType;
      }

      const response = await axios.get('/api/memory/preferences', { params });
      setPreferences(response.data.preferences || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load preferences');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const savePreference = useCallback(async (
    actionType: string,
    fromValue: string,
    toValue: string,
    weight: number = 1.0
  ) => {
    try {
      await axios.post('/api/memory/preferences', {
        action_type: actionType,
        from_value: fromValue,
        to_value: toValue,
        weight
      });
      
      // Reload preferences
      await loadPreferences();
    } catch (err: any) {
      console.error('Failed to save preference:', err);
    }
  }, [loadPreferences]);

  const getSuggestion = useCallback(async (
    actionType: string,
    fromValue: string
  ) => {
    try {
      const response = await axios.get('/api/memory/preferences/suggest', {
        params: { action_type: actionType, from_value: fromValue }
      });
      return response.data;
    } catch (err) {
      console.error('Failed to get suggestion:', err);
      return { suggestion: null, confidence: 0 };
    }
  }, []);

  const resetPreferences = useCallback(async (actionType?: string) => {
    try {
      const params: any = {};
      if (actionType) {
        params.action_type = actionType;
      }

      await axios.post('/api/memory/preferences/reset', null, { params });
      setPreferences([]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset preferences');
    }
  }, []);

  return {
    queries,
    preferences,
    isLoading,
    error,
    loadQueries,
    searchSimilar,
    saveQuery,
    deleteQuery,
    loadPreferences,
    savePreference,
    getSuggestion,
    resetPreferences
  };
};
