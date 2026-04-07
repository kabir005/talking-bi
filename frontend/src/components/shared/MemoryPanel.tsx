import React, { useState, useEffect } from 'react';
import { Brain, Clock, Search, X } from 'lucide-react';
import axios from 'axios';

interface QueryMemory {
  id: string;
  query_text: string;
  created_at: string;
  response_summary?: string;
}

interface MemoryPanelProps {
  datasetId?: string;
  onSelectQuery?: (query: string) => void;
  maxItems?: number;
}

export const MemoryPanel: React.FC<MemoryPanelProps> = ({
  datasetId,
  onSelectQuery,
  maxItems = 10
}) => {
  const [memories, setMemories] = useState<QueryMemory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (isExpanded) {
      loadMemories();
    }
  }, [isExpanded, datasetId]);

  const loadMemories = async () => {
    setIsLoading(true);
    try {
      const params: any = { limit: maxItems };
      if (datasetId) {
        params.dataset_id = datasetId;
      }

      const response = await axios.get('/api/memory/queries', { params });
      setMemories(response.data.queries || []);
    } catch (error) {
      console.error('Failed to load query memory:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const searchSimilar = async () => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    try {
      const response = await axios.get('/api/memory/similar', {
        params: {
          q: searchQuery,
          limit: maxItems,
          dataset_id: datasetId
        }
      });
      setMemories(response.data.similar_queries || []);
    } catch (error) {
      console.error('Failed to search similar queries:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      searchSimilar();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="border border-gray-200 rounded-lg bg-white shadow-sm">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-600" />
          <span className="font-semibold text-gray-900">Query Memory</span>
          {memories.length > 0 && (
            <span className="px-2 py-0.5 text-xs font-semibold text-purple-600 bg-purple-100 rounded-full">
              {memories.length}
            </span>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="border-t border-gray-200">
          <div className="p-4 space-y-3">
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Search similar queries..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                />
              </div>
              {searchQuery && (
                <button
                  onClick={() => {
                    setSearchQuery('');
                    loadMemories();
                  }}
                  className="p-2 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600" />
              </div>
            ) : memories.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Brain className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No query history yet</p>
                <p className="text-xs mt-1">Your past queries will appear here</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {memories.map((memory) => (
                  <button
                    key={memory.id}
                    onClick={() => onSelectQuery?.(memory.query_text)}
                    className="w-full text-left p-3 bg-gray-50 hover:bg-purple-50 rounded-lg transition-colors group"
                  >
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <p className="text-sm font-medium text-gray-900 group-hover:text-purple-900 line-clamp-2">
                        {memory.query_text}
                      </p>
                      <Clock className="w-3 h-3 text-gray-400 flex-shrink-0 mt-0.5" />
                    </div>
                    <div className="flex items-center justify-between">
                      <p className="text-xs text-gray-500">
                        {formatTimestamp(memory.created_at)}
                      </p>
                      {memory.response_summary && (
                        <p className="text-xs text-gray-400 truncate max-w-xs">
                          {memory.response_summary}
                        </p>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
