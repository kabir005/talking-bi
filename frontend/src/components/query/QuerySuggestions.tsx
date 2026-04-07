import React from 'react';

interface QuerySuggestionsProps {
  visible: boolean;
  onSelect: (query: string) => void;
}

const SUGGESTIONS = [
  'show head',
  'top 10 by revenue',
  'filter where revenue > 50000',
  'last 30 days',
  'total sales by region',
  'monthly revenue trend',
  'describe revenue',
  'value counts for region',
  '7-day rolling average',
  'month over month growth',
  'correlation between revenue and profit',
  'show duplicates',
];

export const QuerySuggestions: React.FC<QuerySuggestionsProps> = ({ visible, onSelect }) => {
  if (!visible) return null;

  return (
    <div className="mb-4">
      <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
        Try these example queries:
      </div>
      <div className="flex flex-wrap gap-2">
        {SUGGESTIONS.map((suggestion, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(suggestion)}
            className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 hover:border-blue-400 dark:hover:border-blue-500 transition-colors"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
};
