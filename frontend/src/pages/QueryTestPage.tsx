import React, { useState } from 'react';
import { QuerySuggestions } from '../components/query/QuerySuggestions';
import { QueryResultCard } from '../components/query/QueryResultCard';
import { runNLQuery } from '../api/client';
import { NLQueryResult } from '../types';

export const QueryTestPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [datasetId, setDatasetId] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<NLQueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !datasetId.trim()) return;

    setLoading(true);
    setError(null);
    setShowSuggestions(false);

    try {
      const data = await runNLQuery(datasetId, query);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Query failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionSelect = (suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestions(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            NL2Pandas Query Engine
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Test natural language queries on your datasets
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Dataset ID
              </label>
              <input
                type="text"
                value={datasetId}
                onChange={(e) => setDatasetId(e.target.value)}
                placeholder="Enter dataset ID"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Query
              </label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., top 10 by revenue"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <button
              type="submit"
              disabled={loading || !query.trim() || !datasetId.trim()}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Processing...' : 'Run Query'}
            </button>
          </form>

          {showSuggestions && (
            <div className="mt-6">
              <QuerySuggestions
                visible={showSuggestions}
                onSelect={handleSuggestionSelect}
              />
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <div className="text-red-600 dark:text-red-400 text-xl">❌</div>
              <div>
                <div className="font-medium text-red-900 dark:text-red-100 mb-1">
                  Error
                </div>
                <div className="text-red-800 dark:text-red-200 text-sm">
                  {error}
                </div>
              </div>
            </div>
          </div>
        )}

        {result && (
          <div className="space-y-4">
            <QueryResultCard result={result} />
          </div>
        )}

        <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
            💡 Quick Start
          </h3>
          <ol className="text-sm text-blue-800 dark:text-blue-200 space-y-1 list-decimal list-inside">
            <li>Upload a dataset and generate a dashboard first</li>
            <li>Copy the dataset ID from the URL or dashboard</li>
            <li>Try example queries like "top 10 by revenue" or "last 30 days"</li>
            <li>Results will show as tables and auto-generated charts</li>
          </ol>
        </div>
      </div>
    </div>
  );
};
