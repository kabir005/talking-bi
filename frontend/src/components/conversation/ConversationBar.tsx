import { useState } from 'react';
import { Send, Sparkles } from 'lucide-react';

interface ConversationBarProps {
  onSubmit: (query: string) => void;
  loading?: boolean;
  suggestions?: string[];
}

export default function ConversationBar({ onSubmit, loading, suggestions }: ConversationBarProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSubmit(query.trim());
      setQuery('');
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
  };

  const defaultSuggestions = [
    "Show last 6 months",
    "Why did sales drop?",
    "Predict next 3 months",
    "What if marketing budget increases 20%?"
  ];

  const displaySuggestions = suggestions || defaultSuggestions;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-surface border-t border-border">
      <div className="max-w-7xl mx-auto p-4">
        {/* Suggestions */}
        {displaySuggestions.length > 0 && (
          <div className="flex gap-2 mb-3 overflow-x-auto pb-2">
            {displaySuggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => handleSuggestionClick(suggestion)}
                className="px-3 py-1.5 bg-surface-2 hover:bg-accent-dim hover:text-accent rounded-lg text-sm whitespace-nowrap transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex items-center gap-3">
          <div className="flex-1 relative">
            <Sparkles className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-accent" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything or give a command..."
              disabled={loading}
              className="w-full pl-12 pr-4 py-3 bg-surface-2 border border-border rounded-lg focus:outline-none focus:border-accent transition-colors font-mono text-sm disabled:opacity-50"
            />
          </div>
          <button
            type="submit"
            disabled={!query.trim() || loading}
            className="px-6 py-3 bg-accent text-bg rounded-lg font-semibold hover:bg-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-bg border-t-transparent rounded-full animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Send size={18} />
                Send
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
