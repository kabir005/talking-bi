import React, { useState } from 'react';
import { Send, Loader2, Sparkles } from 'lucide-react';
import axios from 'axios';

interface CommandProcessorProps {
  dashboardId: string;
  onCommandExecuted?: (result: any) => void;
}

interface CommandSuggestion {
  command: string;
  category: string;
  description: string;
}

export const CommandProcessor: React.FC<CommandProcessorProps> = ({
  dashboardId,
  onCommandExecuted
}) => {
  const [command, setCommand] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [suggestions, setSuggestions] = useState<CommandSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const loadSuggestions = async () => {
    try {
      const response = await axios.get('/api/query/suggestions', {
        params: { dashboard_id: dashboardId }
      });
      setSuggestions(response.data.suggestions || []);
      setShowSuggestions(true);
    } catch (err) {
      console.error('Failed to load suggestions:', err);
    }
  };

  const processCommand = async () => {
    if (!command.trim()) return;

    setIsProcessing(true);
    setResult(null);

    try {
      const response = await axios.post('/api/query/command', {
        dashboard_id: dashboardId,
        command: command.trim()
      });

      setResult(response.data);
      
      if (response.data.success && onCommandExecuted) {
        onCommandExecuted(response.data);
      }
    } catch (err: any) {
      setResult({
        success: false,
        message: err.response?.data?.detail || 'Failed to process command'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      processCommand();
    }
  };

  const selectSuggestion = (suggestion: CommandSuggestion) => {
    setCommand(suggestion.command);
    setShowSuggestions(false);
  };

  return (
    <div className="space-y-3">
      <div className="relative">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyPress={handleKeyPress}
              onFocus={loadSuggestions}
              placeholder="Type a command... (e.g., 'show last 6 months' or 'switch to bar chart')"
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isProcessing}
            />
            <button
              onClick={() => setShowSuggestions(!showSuggestions)}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-blue-600"
              title="Show suggestions"
            >
              <Sparkles className="w-5 h-5" />
            </button>
          </div>

          <button
            onClick={processCommand}
            disabled={isProcessing || !command.trim()}
            className={`
              flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors
              ${isProcessing || !command.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
              }
            `}
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span>Execute</span>
              </>
            )}
          </button>
        </div>

        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
            <div className="p-2">
              <div className="text-xs font-semibold text-gray-500 uppercase px-3 py-2">
                Suggested Commands
              </div>
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => selectSuggestion(suggestion)}
                  className="w-full text-left px-3 py-2 hover:bg-blue-50 rounded-md transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900">
                        {suggestion.command}
                      </div>
                      <div className="text-xs text-gray-500 mt-0.5">
                        {suggestion.description}
                      </div>
                    </div>
                    <span className="px-2 py-0.5 text-xs font-semibold text-blue-600 bg-blue-100 rounded">
                      {suggestion.category}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {result && (
        <div className={`
          p-4 rounded-lg border-2
          ${result.success
            ? 'bg-green-50 border-green-200'
            : 'bg-red-50 border-red-200'
          }
        `}>
          <div className="flex items-start gap-2">
            <div className="flex-1">
              <p className={`text-sm font-medium ${
                result.success ? 'text-green-900' : 'text-red-900'
              }`}>
                {result.message}
              </p>
              
              {result.note && (
                <p className="text-xs text-gray-600 mt-1">{result.note}</p>
              )}

              {result.action && (
                <div className="mt-2 text-xs text-gray-700">
                  <span className="font-semibold">Action:</span> {result.action}
                </div>
              )}

              {result.suggestions && result.suggestions.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-semibold text-gray-700 mb-1">Try these instead:</p>
                  <div className="space-y-1">
                    {result.suggestions.map((sug: string, idx: number) => (
                      <button
                        key={idx}
                        onClick={() => setCommand(sug)}
                        className="block text-xs text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        {sug}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
