import React, { useState } from 'react';
import { Link2, Plus, X, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

interface Header {
  key: string;
  value: string;
}

interface ApiConnectorProps {
  onConnectionComplete?: (datasetId: string) => void;
}

interface ConnectionResult {
  dataset_id: string;
  rows_imported: number;
  message: string;
}

export const ApiConnector: React.FC<ApiConnectorProps> = ({ onConnectionComplete }) => {
  const [url, setUrl] = useState('');
  const [method, setMethod] = useState<'GET' | 'POST'>('GET');
  const [headers, setHeaders] = useState<Header[]>([{ key: '', value: '' }]);
  const [body, setBody] = useState('');
  const [dataPath, setDataPath] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ConnectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const addHeader = () => {
    setHeaders([...headers, { key: '', value: '' }]);
  };

  const removeHeader = (index: number) => {
    setHeaders(headers.filter((_, i) => i !== index));
  };

  const updateHeader = (index: number, field: 'key' | 'value', value: string) => {
    const updated = [...headers];
    updated[index][field] = value;
    setHeaders(updated);
  };

  const handleConnect = async () => {
    if (!url.trim()) {
      setError('Please enter a valid API URL');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const headersObj: Record<string, string> = {};
      headers.forEach(h => {
        if (h.key.trim() && h.value.trim()) {
          headersObj[h.key.trim()] = h.value.trim();
        }
      });

      const payload: any = {
        url: url.trim(),
        method,
        headers: headersObj
      };

      if (method === 'POST' && body.trim()) {
        try {
          payload.body = JSON.parse(body);
        } catch {
          setError('Invalid JSON in request body');
          setIsLoading(false);
          return;
        }
      }

      if (dataPath.trim()) {
        payload.data_path = dataPath.trim();
      }

      const response = await axios.post('/api/scrape/api', payload);

      setResult(response.data);
      
      if (response.data.dataset_id && onConnectionComplete) {
        onConnectionComplete(response.data.dataset_id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to connect to API. Please check your configuration.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Link2 className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">Connect to REST API</h3>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-4 gap-2">
          <div className="col-span-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Method</label>
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value as 'GET' | 'POST')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
            </select>
          </div>

          <div className="col-span-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">API Endpoint URL</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://api.example.com/data"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">Headers (Optional)</label>
            <button
              onClick={addHeader}
              className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
              disabled={isLoading}
            >
              <Plus className="w-4 h-4" />
              Add Header
            </button>
          </div>
          <div className="space-y-2">
            {headers.map((header, index) => (
              <div key={index} className="flex items-center gap-2">
                <input
                  type="text"
                  value={header.key}
                  onChange={(e) => updateHeader(index, 'key', e.target.value)}
                  placeholder="Header name (e.g., Authorization)"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  disabled={isLoading}
                />
                <input
                  type="text"
                  value={header.value}
                  onChange={(e) => updateHeader(index, 'value', e.target.value)}
                  placeholder="Header value (e.g., Bearer token)"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  disabled={isLoading}
                />
                {headers.length > 1 && (
                  <button
                    onClick={() => removeHeader(index)}
                    className="p-2 text-gray-400 hover:text-red-600"
                    disabled={isLoading}
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {method === 'POST' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Request Body (JSON)
            </label>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder='{"key": "value"}'
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Data Path (Optional)
          </label>
          <input
            type="text"
            value={dataPath}
            onChange={(e) => setDataPath(e.target.value)}
            placeholder="data.results (leave empty if data is at root)"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <p className="mt-1 text-xs text-gray-500">
            Dot-notation path to the array of data in the JSON response
          </p>
        </div>

        <button
          onClick={handleConnect}
          disabled={isLoading || !url.trim()}
          className={`
            w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium
            transition-colors
            ${isLoading || !url.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
            }
          `}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Connecting...</span>
            </>
          ) : (
            <>
              <Link2 className="w-5 h-5" />
              <span>Connect & Import</span>
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="flex items-start gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-red-900">Error</h4>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {result && (
        <div className="flex items-start gap-2 p-4 bg-green-50 border border-green-200 rounded-lg">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-green-900">Success!</h4>
            <p className="text-sm text-green-700 mt-1">{result.message}</p>
            <div className="mt-2 space-y-1 text-xs text-green-600">
              <div>Rows imported: {result.rows_imported}</div>
              <div className="font-mono text-xs text-green-700 mt-2">
                Dataset ID: {result.dataset_id}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">Example configurations:</h4>
        <div className="text-xs text-blue-800 space-y-2">
          <div>
            <div className="font-semibold">Public API:</div>
            <code className="block mt-1 p-2 bg-white rounded">
              GET https://api.example.com/users
            </code>
          </div>
          <div>
            <div className="font-semibold">With Authentication:</div>
            <code className="block mt-1 p-2 bg-white rounded">
              Header: Authorization = Bearer your_token_here
            </code>
          </div>
        </div>
      </div>
    </div>
  );
};
