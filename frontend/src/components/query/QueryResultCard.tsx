import React from 'react';
import { DataTable } from './DataTable';
import { ChartCard } from '../charts/ChartCard';

interface NLQueryResult {
  success: boolean;
  query: string;
  intent: { op: string; [key: string]: any };
  result: Record<string, any>[];
  total_rows: number;
  displayed_rows: number;
  truncated: boolean;
  columns: string[];
  summary: string;
  chart_config?: any;
}

interface QueryResultCardProps {
  result: NLQueryResult;
}

const getIntentBadgeColor = (op: string): string => {
  const colors: Record<string, string> = {
    'head': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    'tail': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    'filter': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
    'filter_and': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
    'filter_or': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
    'time_filter': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
    'groupby': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'topn': 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300',
    'sort': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    'describe': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-300',
    'corr': 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300',
    'clarify': 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300',
    'no_date_column': 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300',
  };
  return colors[op] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
};

export const QueryResultCard: React.FC<QueryResultCardProps> = ({ result }) => {
  const { intent, result: rows, columns, summary, chart_config, truncated, total_rows } = result;

  // Handle clarify/error intents
  if (intent.op === 'clarify' || intent.op === 'no_date_column') {
    return (
      <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="text-amber-600 dark:text-amber-400 text-xl">⚠️</div>
          <div>
            <div className="font-medium text-amber-900 dark:text-amber-100 mb-1">
              Need clarification
            </div>
            <div className="text-amber-800 dark:text-amber-200 text-sm">
              {summary}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Handle empty results
  if (rows.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium mb-3 ${getIntentBadgeColor(intent.op)}`}>
          {intent.op.replace(/_/g, ' ')}
        </div>
        <div className="text-gray-600 dark:text-gray-400 mb-4">{summary}</div>
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          No results found
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 space-y-4">
      <div>
        <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium mb-2 ${getIntentBadgeColor(intent.op)}`}>
          {intent.op.replace(/_/g, ' ')}
        </div>
        <div className="text-gray-700 dark:text-gray-300 text-sm">
          {summary}
        </div>
      </div>

      {chart_config && chart_config.data && (
        <div className="mb-4">
          <ChartCard config={chart_config} />
        </div>
      )}

      <DataTable
        columns={columns}
        rows={rows}
        totalRows={total_rows}
        truncated={truncated}
      />
    </div>
  );
};
